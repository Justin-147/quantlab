from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.backtest.orders import create_order
from quantlab.models import Order, PortfolioState
from quantlab.strategies.base import Strategy


class DrawdownBuyStrategy(Strategy):
    name = "drawdown_buy"

    def __init__(self) -> None:
        super().__init__()
        self.fired_thresholds: set[float] = set()

    def describe(self, config: dict[str, Any]) -> dict[str, str]:
        reference_asset = config.get("reference_asset", "SPY")
        return {
            "objective": (
                "Simulate disciplined incremental buying during reference-asset drawdowns."
            ),
            "entry_rule": f"Track {reference_asset} peak-to-current drawdown thresholds.",
            "exit_or_rebalance_rule": (
                "Each configured trigger fires once unless reset rules are added later."
            ),
            "risk_control": (
                "Uses cash-constrained simulated orders and records large drawdown reviews."
            ),
            "known_limitations": "No valuation model and no repeated trigger reset logic in V0.2.",
        }

    def generate_orders(
        self,
        date: datetime,
        portfolio_state: PortfolioState,
        price_history: pd.DataFrame,
        config: dict[str, Any],
    ) -> list[Order]:
        reference_asset = config.get("reference_asset", "SPY")
        if reference_asset not in price_history.columns:
            return []
        series = price_history.loc[: pd.Timestamp(date), reference_asset].dropna()
        if series.empty:
            return []

        peak = float(series.cummax().iloc[-1])
        current = float(series.iloc[-1])
        drawdown = 0.0 if peak == 0 else 1 - current / peak
        orders: list[Order] = []

        for trigger in sorted(
            config.get("drawdown_triggers", []), key=lambda item: item["drawdown"]
        ):
            threshold = float(trigger["drawdown"])
            if drawdown < threshold or threshold in self.fired_thresholds:
                continue
            self.fired_thresholds.add(threshold)
            action = trigger.get("action", "")
            if action == "risk_review":
                self.risk_events.append(
                    {
                        "date": pd.Timestamp(date).strftime("%Y-%m-%d"),
                        "type": "risk_review",
                        "message": f"{reference_asset} drawdown reached {drawdown:.2%}",
                        "drawdown": drawdown,
                    }
                )
                continue
            amount_pct = float(trigger.get("amount_pct_of_cash", 0.0))
            notional = max(0.0, portfolio_state.cash * amount_pct)
            price = float(series.iloc[-1])
            if notional > 50 and price > 0:
                orders.append(
                    create_order(
                        pd.Timestamp(date).to_pydatetime(),
                        reference_asset,
                        "buy",
                        notional / price,
                        f"drawdown trigger {threshold:.0%}",
                    )
                )
        return orders
