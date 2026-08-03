"""
Risk management for memecoin trading bot.
Handles position sizing, stop losses, drawdown control, and circuit breakers.
"""

from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

from config.settings import Config


@dataclass
class RiskCheck:
    """Result of a risk check."""

    allowed: bool
    reason: Optional[str] = None
    suggested_size: Optional[float] = None


class RiskManager:
    """
    Risk management system.

    Rules:
    - Max risk per trade (% of capital)
    - Max daily loss (% of capital)
    - Max drawdown (% of capital) -> halt
    - Circuit breaker: N consecutive losses -> cooldown
    - Position sizing based on confidence
    """

    def __init__(
        self,
        initial_capital: Optional[float] = None,
        max_risk_per_trade: Optional[float] = None,
        max_daily_loss: Optional[float] = None,
        max_drawdown: Optional[float] = None,
    ):
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital

        self.max_risk_per_trade = max_risk_per_trade or Config.MAX_RISK_PER_TRADE
        self.max_daily_loss = max_daily_loss or Config.MAX_DAILY_LOSS
        self.max_drawdown = max_drawdown or Config.MAX_DRAWDOWN

        self.daily_pnl = 0.0
        self.last_reset = datetime.now().date()
        self.consecutive_losses = 0
        self.circuit_breaker_until: Optional[datetime] = None
        self.halted = False

    def update_capital(self, current_capital: float):
        """Update current capital and peak."""
        self.current_capital = current_capital
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital

    def get_drawdown(self) -> float:
        """Get current drawdown as fraction of peak capital."""
        if self.peak_capital <= 0:
            return 0.0
        return (self.peak_capital - self.current_capital) / self.peak_capital

    def _reset_daily_stats_if_needed(self):
        """Reset daily stats if it's a new day."""
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_pnl = 0.0
            self.last_reset = today
            self.consecutive_losses = 0

    def record_trade_result(self, pnl_usd: float):
        """Record result of a closed trade."""
        self._reset_daily_stats_if_needed()
        self.daily_pnl += pnl_usd
        self.current_capital += pnl_usd
        self.update_capital(self.current_capital)

        if pnl_usd < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is active."""
        if self.circuit_breaker_until and datetime.now() < self.circuit_breaker_until:
            return True

        if self.consecutive_losses >= Config.CB_MAX_CONSECUTIVE_LOSSES:
            self.circuit_breaker_until = datetime.now() + timedelta(
                minutes=Config.CB_COOLDOWN_MINUTES
            )
            return True

        return False

    def can_trade(self) -> RiskCheck:
        """Check if trading is allowed."""
        self._reset_daily_stats_if_needed()

        if self.halted:
            return RiskCheck(False, "Trading halted due to max drawdown")

        drawdown = self.get_drawdown()
        if drawdown >= self.max_drawdown:
            self.halted = True
            return RiskCheck(False, f"Max drawdown reached: {drawdown:.2%}")

        if self.daily_pnl <= -self.initial_capital * self.max_daily_loss:
            return RiskCheck(False, f"Daily loss limit reached: ${self.daily_pnl:.2f}")

        if self.check_circuit_breaker():
            return RiskCheck(False, "Circuit breaker active")

        return RiskCheck(True)

    def calculate_position_size(
        self,
        confidence: float,
        token_price: float,
        sol_price: float,
        n_open_positions: int = 0,
    ) -> RiskCheck:
        """
        Calculate safe position size based on confidence and risk limits.

        Args:
            confidence: Model confidence (0-1).
            token_price: Token price in USD.
            sol_price: SOL price in USD.
            n_open_positions: Number of currently open positions.

        Returns:
            RiskCheck with suggested SOL amount to invest.
        """
        base_check = self.can_trade()
        if not base_check.allowed:
            return base_check

        # Reduce size as number of open positions grows
        position_dilution = max(0.2, 1.0 - n_open_positions * 0.15)

        # Scale by confidence (higher confidence = larger size)
        confidence_factor = max(0.2, confidence)

        # Kelly-like sizing: risk a fraction of capital
        max_risk_amount = self.current_capital * self.max_risk_per_trade
        position_amount_usd = max_risk_amount * confidence_factor * position_dilution

        # Convert USD to SOL
        position_amount_sol = position_amount_usd / max(sol_price, 1.0)

        # Minimum trade size: 0.001 SOL
        if position_amount_sol < 0.001:
            return RiskCheck(False, "Position size below minimum 0.001 SOL")

        return RiskCheck(True, suggested_size=position_amount_sol)

    def get_status(self) -> Dict:
        """Get current risk status."""
        return {
            "current_capital": self.current_capital,
            "peak_capital": self.peak_capital,
            "drawdown": self.get_drawdown(),
            "daily_pnl": self.daily_pnl,
            "consecutive_losses": self.consecutive_losses,
            "circuit_breaker_active": self.check_circuit_breaker(),
            "halted": self.halted,
        }
