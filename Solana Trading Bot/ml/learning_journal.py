"""
Learning / journaling system for the trading bot.

Stores trade notes, insights, and patterns learned over time.
Persistent knowledge is saved to disk and used to improve decision making.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from config.settings import Config


@dataclass
class TradeNote:
    """A single trade note / journal entry."""

    timestamp: str
    symbol: str
    action: str
    pnl: float
    note: str
    tags: List[str]


@dataclass
class LearnedPattern:
    """A pattern learned from trade history."""

    id: str
    created_at: str
    description: str
    win_count: int
    loss_count: int
    confidence: float
    tags: List[str]


class LearningJournal:
    """
    Persistent learning journal for the trading bot.

    Saves trade notes and extracts patterns from wins/losses.
    """

    def __init__(self, journal_dir: Optional[Path] = None):
        self.journal_dir = journal_dir or Config.DATA_DIR / "journal"
        self.journal_dir.mkdir(parents=True, exist_ok=True)

        self.notes_file = self.journal_dir / "trade_notes.json"
        self.patterns_file = self.journal_dir / "patterns.json"
        self.insights_file = self.journal_dir / "insights.json"

        self.notes: List[TradeNote] = []
        self.patterns: List[LearnedPattern] = []
        self.insights: str = ""

        self._load()

    def _load(self):
        """Load journal data from disk."""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, "r") as f:
                    data = json.load(f)
                self.notes = [TradeNote(**item) for item in data]
            except Exception:
                self.notes = []

        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, "r") as f:
                    data = json.load(f)
                self.patterns = [LearnedPattern(**item) for item in data]
            except Exception:
                self.patterns = []

        if self.insights_file.exists():
            try:
                with open(self.insights_file, "r") as f:
                    self.insights = f.read()
            except Exception:
                self.insights = ""

    def _save(self):
        """Save journal data to disk."""
        with open(self.notes_file, "w") as f:
            json.dump([asdict(n) for n in self.notes], f, indent=2)

        with open(self.patterns_file, "w") as f:
            json.dump([asdict(p) for p in self.patterns], f, indent=2)

        with open(self.insights_file, "w") as f:
            f.write(self.insights)

    def add_trade_note(
        self,
        symbol: str,
        action: str,
        pnl: float,
        note: str,
        tags: Optional[List[str]] = None,
    ) -> TradeNote:
        """Add a note about a trade."""
        note_obj = TradeNote(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            action=action,
            pnl=pnl,
            note=note,
            tags=tags or [],
        )
        self.notes.insert(0, note_obj)
        self.notes = self.notes[:1000]  # Keep last 1000
        self._save()
        return note_obj

    def generate_trade_note(self, symbol: str, action: str, pnl: float, reasons: List[str]) -> str:
        """Generate an AI-style note for a trade."""
        if pnl > 0:
            outcome = "profitable"
        elif pnl < 0:
            outcome = "losing"
        else:
            outcome = "breakeven"

        reason_text = "; ".join(reasons) if reasons else "no specific signal"
        note = f"{action.upper()} {symbol} was {outcome} (${pnl:+.2f}). Key factors: {reason_text}."

        if pnl < 0:
            note += " Reviewing entry timing and volume confirmation for next trade."
        elif pnl > 0:
            note += " Pattern validated; consider repeating under similar conditions."

        return note

    def analyze_patterns(self) -> str:
        """Analyze trade history and generate insights."""
        if len(self.notes) < 5:
            return "Need more trades to identify meaningful patterns."

        wins = [n for n in self.notes if n.pnl > 0]
        losses = [n for n in self.notes if n.pnl < 0]

        win_rate = len(wins) / len(self.notes) * 100 if self.notes else 0
        avg_win = sum(n.pnl for n in wins) / len(wins) if wins else 0
        avg_loss = sum(n.pnl for n in losses) / len(losses) if losses else 0

        # Collect common tags
        tag_counts: Dict[str, int] = {}
        for note in wins:
            for tag in note.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_tags_text = ", ".join([f"{tag} ({count}x)" for tag, count in top_tags]) or "none yet"

        insights = f"""Trade Analysis ({len(self.notes)} trades)
• Win Rate: {win_rate:.1f}%
• Avg Win: ${avg_win:,.2f}
• Avg Loss: ${avg_loss:,.2f}
• Most common winning tags: {top_tags_text}

Key learnings:
"""

        if win_rate < 40:
            insights += "• Win rate is below target. Consider tightening entry filters and waiting for higher confidence signals.\n"
        elif win_rate > 60:
            insights += "• Strong win rate. Current strategy is working well; consider gradual position size increases.\n"

        if avg_loss < -avg_win * 0.5:
            insights += "• Losses are smaller than wins — good risk/reward profile.\n"
        else:
            insights += "• Losses are too large relative to wins. Tighten stop losses.\n"

        insights += "• Continue journaling every trade to refine the model.\n"

        self.insights = insights
        self._save()
        return insights

    def get_recent_notes(self, n: int = 20) -> List[TradeNote]:
        """Get recent trade notes."""
        return self.notes[:n]

    def get_insights(self) -> str:
        """Get current insights."""
        if not self.insights:
            return self.analyze_patterns()
        return self.insights

    def add_pattern(
        self,
        description: str,
        tags: Optional[List[str]] = None,
        initial_wins: int = 0,
        initial_losses: int = 0,
    ) -> LearnedPattern:
        """Add a learned pattern."""
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        total = initial_wins + initial_losses
        confidence = initial_wins / total if total > 0 else 0.5

        pattern = LearnedPattern(
            id=pattern_id,
            created_at=datetime.now().isoformat(),
            description=description,
            win_count=initial_wins,
            loss_count=initial_losses,
            confidence=confidence,
            tags=tags or [],
        )
        self.patterns.append(pattern)
        self._save()
        return pattern

    def update_pattern(self, pattern_id: str, won: bool):
        """Update a pattern with a new outcome."""
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                if won:
                    pattern.win_count += 1
                else:
                    pattern.loss_count += 1
                total = pattern.win_count + pattern.loss_count
                pattern.confidence = pattern.win_count / total if total > 0 else 0.5
                self._save()
                return

    def get_top_patterns(self, n: int = 5) -> List[LearnedPattern]:
        """Get top patterns by confidence."""
        return sorted(self.patterns, key=lambda p: p.confidence, reverse=True)[:n]


# Global journal instance
_journal: Optional[LearningJournal] = None


def get_journal() -> LearningJournal:
    """Get or create the global learning journal."""
    global _journal
    if _journal is None:
        _journal = LearningJournal()
    return _journal
