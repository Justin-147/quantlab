from __future__ import annotations


def calculate_transaction_costs(
    notional: float,
    transaction_cost_bps: float = 5,
    slippage_bps: float = 5,
) -> tuple[float, float]:
    transaction_cost = float(notional) * float(transaction_cost_bps) / 10_000
    slippage_cost = float(notional) * float(slippage_bps) / 10_000
    return transaction_cost, slippage_cost
