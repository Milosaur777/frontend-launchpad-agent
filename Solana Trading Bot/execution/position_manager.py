"""
Position manager for tracking open trades and P&L.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class Position:
    """An open trading position."""

    token_address: str
    symbol: str
    entry_price_usd: float
    token_amount: float
    sol_invested: float
    entry_time: datetime
    stop_loss_price: float
    take_profit_price: float
    highest_price: float
    trailing_stop_pct: float = 0.0
    trailing_stop_activation_pct: float = 0.0
    trailing_stop_active: bool = False
    _open_cycle: int = 0  # Set by bot_core to track minimum hold


@dataclass
class ClosedTrade:
    """A completed trade."""

    token_address: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    token_amount: float
    pnl_usd: float
    pnl_pct: float
    entry_time: datetime
    exit_time: datetime
    reason: str


class PositionManager:
    """Manages open positions and trade history."""

    def __init__(self, state_file: Optional[Path] = None):
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[ClosedTrade] = []
        self.state_file = state_file

        if state_file:
            self.load_state()

    def open_position(
        self,
        token_address: str,
        symbol: str,
        entry_price: float,
        token_amount: float,
        sol_invested: float,
        stop_loss_pct: float,
        take_profit_pct: float,
        trailing_stop_pct: float = 0.0,
        trailing_stop_activation_pct: float = 0.0,
    ) -> Position:
        """Open a new position."""
        position = Position(
            token_address=token_address,
            symbol=symbol,
            entry_price_usd=entry_price,
            token_amount=token_amount,
            sol_invested=sol_invested,
            entry_time=datetime.now(),
            stop_loss_price=entry_price * (1 - stop_loss_pct),
            take_profit_price=entry_price * (1 + take_profit_pct),
            highest_price=entry_price,
            trailing_stop_pct=trailing_stop_pct,
            trailing_stop_activation_pct=trailing_stop_activation_pct,
            trailing_stop_active=False,
        )
        self.positions[token_address] = position
        self.save_state()
        return position

    def close_position(
        self,
        token_address: str,
        exit_price: float,
        reason: str = "manual",
    ) -> Optional[ClosedTrade]:
        """Close an open position."""
        position = self.positions.pop(token_address, None)
        if not position:
            return None

        pnl_usd = (exit_price - position.entry_price_usd) * position.token_amount
        pnl_pct = (exit_price / position.entry_price_usd - 1) * 100

        trade = ClosedTrade(
            token_address=token_address,
            symbol=position.symbol,
            side="sell",
            entry_price=position.entry_price_usd,
            exit_price=exit_price,
            token_amount=position.token_amount,
            pnl_usd=pnl_usd,
            pnl_pct=pnl_pct,
            entry_time=position.entry_time,
            exit_time=datetime.now(),
            reason=reason,
        )
        self.trade_history.append(trade)
        self.save_state()
        return trade

    def update_position_price(self, token_address: str, current_price: float):
        """Update current price and check stop-loss / take-profit / trailing-stop."""
        position = self.positions.get(token_address)
        if not position:
            return None

        if current_price > position.highest_price:
            position.highest_price = current_price

        # Check take profit first
        if current_price >= position.take_profit_price:
            return self.close_position(token_address, current_price, reason="take_profit")

        # Activate trailing stop once price has reached activation threshold
        if (
            position.trailing_stop_pct > 0
            and position.trailing_stop_activation_pct > 0
            and not position.trailing_stop_active
        ):
            peak_gain_pct = (position.highest_price / position.entry_price_usd) - 1
            if peak_gain_pct >= position.trailing_stop_activation_pct:
                position.trailing_stop_active = True

        # Check trailing stop against highest price seen
        if position.trailing_stop_active:
            trailing_stop_price = position.highest_price * (1 - position.trailing_stop_pct)
            if current_price <= trailing_stop_price:
                return self.close_position(
                    token_address,
                    current_price,
                    reason="trailing_stop",
                )

        # Check fixed stop loss
        if current_price <= position.stop_loss_price:
            return self.close_position(token_address, current_price, reason="stop_loss")

        return None

    def get_position(self, token_address: str) -> Optional[Position]:
        """Get a specific open position."""
        return self.positions.get(token_address)

    def get_all_positions(self) -> Dict[str, Position]:
        """Get all open positions."""
        return self.positions.copy()

    def get_unrealized_pnl(self, token_address: str, current_price: float) -> float:
        """Get unrealized P&L for a position."""
        position = self.positions.get(token_address)
        if not position:
            return 0.0
        return (current_price - position.entry_price_usd) * position.token_amount

    def get_total_unrealized_pnl(self, prices: Dict[str, float]) -> float:
        """Get total unrealized P&L across all positions."""
        total = 0.0
        for token_address, position in self.positions.items():
            price = prices.get(token_address, position.entry_price_usd)
            total += self.get_unrealized_pnl(token_address, price)
        return total

    def get_realized_pnl(self) -> float:
        """Get total realized P&L from closed trades."""
        return sum(t.pnl_usd for t in self.trade_history)

    def get_trade_stats(self) -> Dict:
        """Get trade statistics."""
        if not self.trade_history:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "avg_pnl": 0.0,
            }

        wins = sum(1 for t in self.trade_history if t.pnl_usd > 0)
        losses = len(self.trade_history) - wins

        return {
            "total_trades": len(self.trade_history),
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": wins / len(self.trade_history),
            "total_pnl": self.get_realized_pnl(),
            "avg_pnl": self.get_realized_pnl() / len(self.trade_history),
        }

    def save_state(self):
        """Save positions and trade history to disk."""
        if not self.state_file:
            return

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "positions": {
                addr:                 {
                    "token_address": p.token_address,
                    "symbol": p.symbol,
                    "entry_price_usd": p.entry_price_usd,
                    "token_amount": p.token_amount,
                    "sol_invested": p.sol_invested,
                    "entry_time": p.entry_time.isoformat(),
                    "stop_loss_price": p.stop_loss_price,
                    "take_profit_price": p.take_profit_price,
                    "highest_price": p.highest_price,
                    "trailing_stop_pct": p.trailing_stop_pct,
                    "trailing_stop_activation_pct": p.trailing_stop_activation_pct,
                    "trailing_stop_active": p.trailing_stop_active,
                    "_open_cycle": getattr(p, '_open_cycle', 0),
                }
                for addr, p in self.positions.items()
            },
            "trade_history": [
                {
                    "token_address": t.token_address,
                    "symbol": t.symbol,
                    "side": t.side,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "token_amount": t.token_amount,
                    "pnl_usd": t.pnl_usd,
                    "pnl_pct": t.pnl_pct,
                    "entry_time": t.entry_time.isoformat(),
                    "exit_time": t.exit_time.isoformat(),
                    "reason": t.reason,
                }
                for t in self.trade_history
            ],
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load positions and trade history from disk."""
        if not self.state_file or not self.state_file.exists():
            return

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)

            self.positions = {}
            for addr, p in state.get("positions", {}).items():
                self.positions[addr] = Position(
                    token_address=p["token_address"],
                    symbol=p["symbol"],
                    entry_price_usd=p["entry_price_usd"],
                    token_amount=p["token_amount"],
                    sol_invested=p["sol_invested"],
                    entry_time=datetime.fromisoformat(p["entry_time"]),
                    stop_loss_price=p["stop_loss_price"],
                    take_profit_price=p["take_profit_price"],
                    highest_price=p["highest_price"],
                    trailing_stop_pct=p.get("trailing_stop_pct", 0.0),
                    trailing_stop_activation_pct=p.get("trailing_stop_activation_pct", 0.0),
                    trailing_stop_active=p.get("trailing_stop_active", False),
                    _open_cycle=p.get("_open_cycle", 0),
                )

            self.trade_history = [
                ClosedTrade(
                    token_address=t["token_address"],
                    symbol=t["symbol"],
                    side=t["side"],
                    entry_price=t["entry_price"],
                    exit_price=t["exit_price"],
                    token_amount=t["token_amount"],
                    pnl_usd=t["pnl_usd"],
                    pnl_pct=t["pnl_pct"],
                    entry_time=datetime.fromisoformat(t["entry_time"]),
                    exit_time=datetime.fromisoformat(t["exit_time"]),
                    reason=t["reason"],
                )
                for t in state.get("trade_history", [])
            ]
        except Exception:
            pass
