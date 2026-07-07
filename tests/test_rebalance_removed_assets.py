from __future__ import annotations

from datetime import datetime

from quantlab.models import PortfolioState, Position
from quantlab.portfolio.rebalancing import target_weight_orders


def test_removed_target_asset_is_sold():
    state = PortfolioState(
        date=datetime(2024, 1, 1),
        cash=0,
        positions={"SPY": Position(symbol="SPY", quantity=10, average_cost=100)},
        market_value=1000,
        total_value=1000,
        weights={"SPY": 1.0, "cash": 0.0},
    )
    orders = target_weight_orders(state, {"BND": 1.0}, {"SPY": 100, "BND": 50})
    assert any(order.symbol == "SPY" and order.side == "sell" for order in orders)
