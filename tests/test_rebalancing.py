from __future__ import annotations

from datetime import datetime

from quantlab.config import load_portfolio_config
from quantlab.portfolio.portfolio import create_initial_state
from quantlab.portfolio.rebalancing import target_weight_orders


def test_rebalancing_creates_target_orders():
    portfolio = load_portfolio_config("balanced_6040")
    state = create_initial_state(portfolio, datetime(2024, 1, 2))
    prices = {"SPY": 100.0, "BND": 80.0}
    orders = target_weight_orders(state, portfolio.target_weights, prices)
    assert orders
    assert {order.side for order in orders} == {"buy"}
