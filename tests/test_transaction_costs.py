from __future__ import annotations

from quantlab.backtest.transaction_costs import calculate_transaction_costs


def test_transaction_cost_calculation_is_correct():
    transaction_cost, slippage_cost = calculate_transaction_costs(10000, 5, 10)
    assert transaction_cost == 5.0
    assert slippage_cost == 10.0
