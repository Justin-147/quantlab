from __future__ import annotations

from datetime import datetime

from quantlab.config import load_portfolio_config
from quantlab.portfolio.portfolio import initialize_portfolio_from_target


def test_portfolio_weights_sum_to_approximately_one():
    config = load_portfolio_config("growth_balanced")
    prices = {"SPY": 100.0, "QQQ": 100.0, "BND": 100.0, "GLD": 100.0}
    state = initialize_portfolio_from_target(config, prices, datetime(2024, 1, 1))
    assert abs(sum(state.weights.values()) - 1.0) < 1e-6
