from __future__ import annotations

import pandas as pd

from quantlab.config import load_strategy_config
from quantlab.models import PortfolioState
from quantlab.strategies.trend_filter import TrendFilterStrategy


def test_trend_filter_ignores_future_price_jump():
    dates = pd.bdate_range("2024-01-01", periods=230)
    base = [100.0] * 210 + [300.0] * 20
    history = pd.DataFrame(
        {"SPY": base, "BND": [80.0] * 230, "QQQ": [100.0] * 230, "GLD": [120.0] * 230}, index=dates
    )
    decision_date = dates[205]
    state = PortfolioState(
        date=decision_date.to_pydatetime(),
        cash=1000,
        positions={},
        total_value=1000,
        weights={"cash": 1.0},
    )
    config = load_strategy_config("trend_filter")
    full_orders = TrendFilterStrategy().generate_orders(
        decision_date.to_pydatetime(), state, history, config
    )
    truncated_orders = TrendFilterStrategy().generate_orders(
        decision_date.to_pydatetime(), state, history.loc[:decision_date], config
    )
    assert [(order.symbol, order.side) for order in full_orders] == [
        (order.symbol, order.side) for order in truncated_orders
    ]
