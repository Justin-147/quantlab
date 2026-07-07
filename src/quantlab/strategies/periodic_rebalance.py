from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.models import Order, PortfolioState
from quantlab.portfolio.rebalancing import target_weight_orders
from quantlab.strategies.base import Strategy


class PeriodicRebalanceStrategy(Strategy):
    name = "periodic_rebalance"

    def __init__(self) -> None:
        super().__init__()
        self.last_rebalance_period: tuple[int, int] | None = None

    def generate_orders(
        self,
        date: datetime,
        portfolio_state: PortfolioState,
        price_history: pd.DataFrame,
        config: dict[str, Any],
    ) -> list[Order]:
        prices = price_history.loc[date].to_dict()
        target_weights = config.get("target_weights", {})
        threshold = float(config.get("rebalance_threshold", 0.05))
        frequency = config.get("rebalance_frequency", "monthly")
        period = _period_key(pd.Timestamp(date), frequency)

        should_rebalance = not portfolio_state.positions
        if self.last_rebalance_period != period:
            should_rebalance = True

        orders = target_weight_orders(
            portfolio_state,
            target_weights,
            prices,
            threshold=0.0 if should_rebalance else threshold,
            reason=f"{frequency} rebalance",
        )

        if orders:
            if should_rebalance:
                self.last_rebalance_period = period
            return orders
        return []


def _period_key(date: pd.Timestamp, frequency: str) -> tuple[int, int]:
    if frequency == "quarterly":
        return (date.year, (date.month - 1) // 3)
    return (date.year, date.month)
