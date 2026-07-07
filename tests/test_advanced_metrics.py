from __future__ import annotations

import math

from quantlab.risk.metrics import calculate_metrics


def test_advanced_metrics_are_json_safe_floats():
    equity = [
        {"date": "2024-01-01", "total_value": 100},
        {"date": "2024-01-02", "total_value": 101},
        {"date": "2024-01-03", "total_value": 99},
        {"date": "2024-01-04", "total_value": 103},
    ]
    metrics = calculate_metrics(equity)
    for key in ["var_95", "cvar_95", "profit_factor", "skewness", "kurtosis"]:
        assert math.isfinite(metrics[key])
