from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.models import Order, PortfolioState
from quantlab.portfolio.rebalancing import target_weight_orders
from quantlab.strategies.base import Strategy


class BuyAndHoldStrategy(Strategy):
    name = "buy_and_hold"

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
