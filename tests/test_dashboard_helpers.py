from __future__ import annotations

from datetime import date

import pandas as pd

from quantlab.dashboard.helpers import (
    build_input_signature,
    file_signature,
    filter_price_data,
    limit_trades,
    result_to_frames,
    safe_metric_value,
)


def test_filter_price_data_limits_dates():
    df = pd.DataFrame(
        [
            {"date": "2024-01-01", "symbol": "SPY"},
            {"date": "2024-01-02", "symbol": "SPY"},
            {"date": "2024-01-03", "symbol": "SPY"},
        ]
    )
    filtered = filter_price_data(df, date(2024, 1, 2), date(2024, 1, 3))
    assert list(filtered["date"]) == ["2024-01-02", "2024-01-03"]


def test_result_to_frames_handles_empty_fills():
    frames = result_to_frames(
        {
            "equity_curve": [{"date": "2024-01-01", "total_value": 1000}],
            "drawdown_curve": [],
            "exposures": [],
            "fills": [],
            "order_events": [],
            "risk_events": [],
            "metrics": {"annualized_return": 0.1},
        }
    )
    assert frames["trades"].empty
    assert frames["metrics"].iloc[0]["metric"] == "annualized_return"


def test_limit_trades_caps_large_fill_set():
    trades = pd.DataFrame({"order_id": [str(i) for i in range(500)]})
    limited = limit_trades(trades, max_rows=200)
    assert len(limited) == 200
    assert list(limited["order_id"].head(2)) == ["0", "1"]


def test_input_signature_is_stable():
    args = {
        "portfolio_name": "growth_balanced",
        "strategy_name": "periodic_rebalance",
        "data_path": "examples/sample_data/prices_sample.csv",
        "execution_lag_days": 1,
        "transaction_cost_bps": 5,
        "slippage_bps": 5,
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 31),
        "benchmark_symbol": "SPY",
    }
    assert build_input_signature(**args) == build_input_signature(**dict(reversed(args.items())))


def test_file_signature_includes_size_and_mtime(tmp_path):
    path = tmp_path / "prices.csv"
    path.write_text("date,symbol\n2026-07-06,SPY\n", encoding="utf-8")
    signature = file_signature(str(path))
    assert signature["path"] == str(path)
    assert signature["size"] == path.stat().st_size
    assert isinstance(signature["mtime_ns"], int)


def test_safe_metric_value_formats_missing_and_percent():
    assert safe_metric_value({}, "missing") == "N/A"
    assert safe_metric_value({"return": 0.1234}, "return", percent=True) == "12.34%"
