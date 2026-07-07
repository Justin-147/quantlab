from __future__ import annotations

from datetime import datetime

import pandas as pd

from quantlab.config import load_portfolio_config, load_strategy_config
from quantlab.models import PortfolioState
from quantlab.portfolio.portfolio import create_initial_state
from quantlab.strategies.buy_and_hold import BuyAndHoldStrategy
from quantlab.strategies.drawdown_rules import DrawdownBuyStrategy
from quantlab.strategies.trend_filter import TrendFilterStrategy


def test_buy_and_hold_generates_initial_orders():
    portfolio = load_portfolio_config("balanced_6040")
    state = create_initial_state(portfolio, datetime(2024, 1, 2))
    history = pd.DataFrame({"SPY": [100.0], "BND": [80.0]}, index=[pd.Timestamp("2024-01-02")])
    config = {"target_weights": portfolio.target_weights}
    orders = BuyAndHoldStrategy().generate_orders(datetime(2024, 1, 2), state, history, config)
    assert len(orders) == 2


def test_trend_filter_uses_available_history_only():
    dates = pd.bdate_range("2024-01-01", periods=220)
    history = pd.DataFrame(
        {"SPY": range(100, 320), "BND": [80.0] * 220, "QQQ": [100.0] * 220, "GLD": [120.0] * 220},
        index=dates,
    )
    state = PortfolioState(
        date=dates[-1].to_pydatetime(),
        cash=100000,
        positions={},
        total_value=100000,
        weights={"cash": 1.0},
    )
    config = load_strategy_config("trend_filter") | {"target_weights": {"SPY": 0.5, "BND": 0.5}}
    orders = TrendFilterStrategy().generate_orders(
        dates[-1].to_pydatetime(), state, history, config
    )
    assert orders


def test_drawdown_rule_triggers_at_threshold():
    dates = pd.bdate_range("2024-01-01", periods=4)
    history = pd.DataFrame({"SPY": [100.0, 105.0, 90.0, 84.0]}, index=dates)
    state = PortfolioState(
        date=dates[-1].to_pydatetime(),
        cash=100000,
        positions={},
        total_value=100000,
        weights={"cash": 1.0},
    )
    config = load_strategy_config("drawdown_buy")
    orders = DrawdownBuyStrategy().generate_orders(
        dates[-1].to_pydatetime(), state, history, config
    )
    assert orders
