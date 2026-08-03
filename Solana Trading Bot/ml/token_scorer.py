"""
Token risk scoring for memecoin trading.
Uses on-chain and market data heuristics to detect high-risk tokens.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from data.price_feed import PriceSnapshot
from config.settings import Config


@dataclass
class RiskScore:
    """Risk assessment result for a token."""

    token_address: str
    symbol: str
    total_score: float  # 0-100, higher = riskier
    is_safe: bool
    reasons: list


class TokenScorer:
    """
    Score token risk using market heuristics.

    Note: This is not a full smart-contract audit. It flags obvious red flags
    like extremely low liquidity, suspicious volume patterns, and new tokens
    with extreme FDV/market cap ratios.
    """

    def __init__(self):
        self.min_liquidity = Config.MIN_LIQUIDITY_USD
        self.min_volume_24h = Config.MIN_VOLUME_24H_USD
        self.min_age_hours = Config.MIN_TOKEN_AGE_HOURS
        self.max_age_hours = Config.MAX_TOKEN_AGE_HOURS

    def score(self, snapshot: PriceSnapshot) -> RiskScore:
        """
        Calculate risk score for a token.

        Returns:
            RiskScore with total score (0-100) and safety flag.
        """
        score = 0.0
        reasons = []

        # ── Hard gates: these instantly mark a token unsafe ──
        # Relaxed thresholds for established watchlist tokens
        min_liq = min(self.min_liquidity, 5_000)
        min_vol = min(self.min_volume_24h, 10_000)

        if snapshot.liquidity_usd < min_liq:
            reasons.append(f"Insufficient liquidity: ${snapshot.liquidity_usd:,.2f} < ${min_liq:,.2f}")
            return RiskScore(
                token_address=snapshot.token_address,
                symbol=snapshot.symbol,
                total_score=100.0,
                is_safe=False,
                reasons=reasons,
            )

        if snapshot.volume_24h_usd < min_vol:
            reasons.append(f"Insufficient volume: ${snapshot.volume_24h_usd:,.2f} < ${min_vol:,.2f}")
            return RiskScore(
                token_address=snapshot.token_address,
                symbol=snapshot.symbol,
                total_score=100.0,
                is_safe=False,
                reasons=reasons,
            )

        if snapshot.pair_created_at:
            now = datetime.now(timezone.utc) if snapshot.pair_created_at.tzinfo else datetime.now()
            age_hours = (now - snapshot.pair_created_at).total_seconds() / 3600
            if age_hours < 1:  # Only reject tokens younger than 1 hour
                reasons.append(f"Too new: {age_hours:.1f}h < 1h minimum")
                return RiskScore(
                    token_address=snapshot.token_address,
                    symbol=snapshot.symbol,
                    total_score=100.0,
                    is_safe=False,
                    reasons=reasons,
                )

        # 1. Liquidity depth (0-20 points)
        if snapshot.liquidity_usd < self.min_liquidity * 2:
            score += 15
            reasons.append(f"Moderate liquidity: ${snapshot.liquidity_usd:,.2f}")
        elif snapshot.liquidity_usd < self.min_liquidity * 5:
            score += 5
            reasons.append(f"Acceptable liquidity: ${snapshot.liquidity_usd:,.2f}")

        # 2. Volume vs liquidity ratio (0-20 points)
        if snapshot.liquidity_usd > 0:
            vol_liq_ratio = snapshot.volume_24h_usd / snapshot.liquidity_usd
            if vol_liq_ratio > 50:
                score += 20
                reasons.append(f"Suspicious volume/liquidity ratio: {vol_liq_ratio:.1f}x")
            elif vol_liq_ratio > 30:
                score += 12
                reasons.append(f"High volume/liquidity ratio: {vol_liq_ratio:.1f}x")

        # 3. Buy/sell imbalance (0-15 points)
        total_txns = snapshot.txns_24h_buy + snapshot.txns_24h_sell
        if total_txns > 10:
            buy_ratio = snapshot.txns_24h_buy / total_txns
            if buy_ratio > 0.80:
                score += 15
                reasons.append(f"Extreme buy imbalance: {buy_ratio:.1%} buys")
            elif buy_ratio < 0.20:
                score += 15
                reasons.append(f"Extreme sell imbalance: {buy_ratio:.1%} buys")

        # 4. FDV vs Market Cap ratio (0-15 points)
        if snapshot.market_cap > 0:
            fdv_mc_ratio = snapshot.fdv / snapshot.market_cap
            if fdv_mc_ratio > 10:
                score += 15
                reasons.append(f"Extreme FDV/MC ratio: {fdv_mc_ratio:.1f}x")
            elif fdv_mc_ratio > 3:
                score += 8
                reasons.append(f"High FDV/MC ratio: {fdv_mc_ratio:.1f}x")

        # 5. Price stability (0-10 points)
        if abs(snapshot.price_change_1h_pct) > 100:
            score += 10
            reasons.append(f"Extreme 1h price move: {snapshot.price_change_1h_pct:+.1f}%")
        elif abs(snapshot.price_change_1h_pct) > 50:
            score += 5
            reasons.append(f"Large 1h price move: {snapshot.price_change_1h_pct:+.1f}%")

        # Cap at 100
        score = min(score, 100)

        # Safety threshold (stricter for established-token strategy)
        is_safe = score < 35

        return RiskScore(
            token_address=snapshot.token_address,
            symbol=snapshot.symbol,
            total_score=score,
            is_safe=is_safe,
            reasons=reasons,
        )

    def is_tradable(self, snapshot: PriceSnapshot) -> bool:
        """Quick check if token passes basic safety filters."""
        risk = self.score(snapshot)
        return risk.is_safe
