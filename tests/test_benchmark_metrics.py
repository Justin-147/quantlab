from __future__ import annotations

import pandas as pd

from quantlab.risk.benchmark import calculate_benchmark_metrics


def test_benchmark_metrics_return_expected_keys():
    equity = [
        {"date": "2024-01-01", "total_value": 100},
        {"date": "2024-01-02", "total_value": 102},
        {"date": "2024-01-03", "total_value": 103},
    ]
    prices = pd.DataFrame(
        {"SPY": [100, 101, 102]}, index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    )
    metrics = calculate_benchmark_metrics(equity, prices)
    assert "information_ratio" in metrics
    assert "benchmark_total_return" in metrics
