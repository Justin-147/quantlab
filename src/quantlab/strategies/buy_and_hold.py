from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.models import Order, PortfolioState
from quantlab.portfolio.rebalancing import target_weight_orders
from quantlab.strategies.base import Strategy


class BuyAndHoldStrategy(Strategy):
    name = "buy_and_hold"

    def describe(self, config: dict[str, Any]) -> dict[str, str]:
        return {
            "objective": "Hold the configured target allocation through the full test period.",
            "entry_rule": "Buy target weights at the first available simulated execution.",
            "exit_or_rebalance_rule": "No scheduled exits or rebalances.",
            "risk_control": "No leverage; purchases are constrained by available cash.",
            "known_limitations": "Does not adapt to drawdown, trend, or valuation changes.",
        }

    def generate_orders(
        self,
        date: datetime,
        portfolio_state: PortfolioState,
        price_history: pd.DataFrame,
        config: dict[str, Any],
    ) -> list[Order]:
        if portfolio_state.positions:
            return []
        prices = price_history.loc[date].to_dict()
        target_weights = config.get("target_weights", {})
        return target_weight_orders(
            portfolio_state,
            target_weights,
            prices,
            threshold=0.0,
            reason="initial buy and hold allocation",
        )
