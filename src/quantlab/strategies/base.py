from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.models import Order, PortfolioState


class Strategy:
    name = "base"

    def __init__(self) -> None:
        self.risk_events: list[dict[str, Any]] = []

    def generate_orders(
        self,
        date: datetime,
        portfolio_state: PortfolioState,
        price_history: pd.DataFrame,
        config: dict[str, Any],
    ) -> list[Order]:
        raise NotImplementedError

    def consume_risk_events(self) -> list[dict[str, Any]]:
        events = list(self.risk_events)
        self.risk_events.clear()
        return events


def get_strategy(strategy_type: str) -> Strategy:
    if strategy_type == "buy_and_hold":
        from quantlab.strategies.buy_and_hold import BuyAndHoldStrategy

        return BuyAndHoldStrategy()
    if strategy_type == "periodic_rebalance":
        from quantlab.strategies.periodic_rebalance import PeriodicRebalanceStrategy

        return PeriodicRebalanceStrategy()
    if strategy_type == "trend_filter":
        from quantlab.strategies.trend_filter import TrendFilterStrategy

        return TrendFilterStrategy()
    if strategy_type == "drawdown_buy":
        from quantlab.strategies.drawdown_rules import DrawdownBuyStrategy

        return DrawdownBuyStrategy()
    raise ValueError(f"Unsupported strategy type: {strategy_type}")
