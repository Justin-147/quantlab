from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.models import Order, PortfolioState
from quantlab.portfolio.rebalancing import target_weight_orders
from quantlab.strategies.base import Strategy


class TrendFilterStrategy(Strategy):
    name = "trend_filter"

    def __init__(self) -> None:
        super().__init__()
        self.last_signal: str | None = None
        self.last_switch_date: pd.Timestamp | None = None

    def generate_orders(
        self,
        date: datetime,
        portfolio_state: PortfolioState,
        price_history: pd.DataFrame,
        config: dict[str, Any],
    ) -> list[Order]:
        current_date = pd.Timestamp(date)
        signal_asset = config.get("signal_asset", "SPY")
        window = int(config.get("moving_average_window", 200))
        cooldown_days = int(config.get("cooldown_days", 20))
        history = price_history.loc[:current_date]

        if signal_asset not in history.columns or len(history[signal_asset].dropna()) < window:
            target_weights = config.get("target_weights", config.get("risk_on_weights", {}))
            signal = "risk_on"
        else:
            series = history[signal_asset].dropna()
            moving_average = float(series.rolling(window).mean().iloc[-1])
            last_price = float(series.iloc[-1])
            signal = "risk_on" if last_price >= moving_average else "risk_off"
            target_weights = config.get("risk_on_weights" if signal == "risk_on" else "risk_off_weights", {})

        can_switch = True
        if self.last_switch_date is not None and self.last_signal != signal:
            can_switch = (current_date - self.last_switch_date).days >= cooldown_days

        if self.last_signal is None:
            self.last_signal = signal
            self.last_switch_date = current_date
        elif self.last_signal != signal and can_switch:
            self.last_signal = signal
            self.last_switch_date = current_date
        elif self.last_signal != signal and not can_switch:
            target_weights = config.get("risk_on_weights" if self.last_signal == "risk_on" else "risk_off_weights", target_weights)

        prices = history.loc[current_date].to_dict()
        return target_weight_orders(
            portfolio_state,
            target_weights,
            prices,
            threshold=0.0 if not portfolio_state.positions else 0.05,
            reason=f"trend filter {self.last_signal}",
        )
