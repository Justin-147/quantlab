from __future__ import annotations

import math
from collections.abc import Mapping

from quantlab.models import PortfolioState


def validate_state_invariants(
    state: PortfolioState,
    prices: Mapping[str, float],
    min_cash: float = -1e-6,
) -> list[str]:
    issues: list[str] = []
    if not math.isfinite(state.total_value):
        raise ValueError("Portfolio total value is not finite")
    if state.cash < min_cash:
        issues.append(f"cash below allowed minimum: {state.cash:.6f}")
    value_tolerance = max(1e-4, state.total_value * 1e-8)
    if abs(state.total_value - (state.cash + state.market_value)) > value_tolerance:
        issues.append("total_value does not match cash + market_value")
    weight_sum = sum(state.weights.values())
    if state.total_value > 0 and abs(weight_sum - 1.0) > 1e-4:
        issues.append(f"weights do not sum to 1.0: {weight_sum:.6f}")
    for symbol, position in state.positions.items():
        if position.quantity < -1e-8:
            raise ValueError(f"Negative position quantity for {symbol}")
        if symbol in prices and float(prices[symbol]) <= 0:
            issues.append(f"non-positive price for {symbol}")
    return issues
