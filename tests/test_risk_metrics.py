from __future__ import annotations

import math

from quantlab.risk.drawdown import max_drawdown
from quantlab.risk.metrics import calculate_metrics


def test_max_drawdown_calculation_is_correct():
    equity = [
        {"date": "2024-01-01", "total_value": 100.0},
        {"date": "2024-01-02", "total_value": 120.0},
        {"date": "2024-01-03", "total_value": 90.0},
    ]
    assert abs(max_drawdown(equity) - -0.25) < 1e-9


def test_sharpe_ratio_returns_finite_value_when_possible():
    equity = [
        {"date": "2024-01-01", "total_value": 100.0},
        {"date": "2024-01-02", "total_value": 101.0},
        {"date": "2024-01-03", "total_value": 100.0},
        {"date": "2024-01-04", "total_value": 103.0},
    ]
    metrics = calculate_metrics(equity)
    assert math.isfinite(metrics["sharpe_ratio"])
