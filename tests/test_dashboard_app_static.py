from __future__ import annotations

from pathlib import Path

from quantlab.dashboard.helpers import build_input_signature, file_signature


def test_dashboard_app_uses_streamlit_stretch_width():
    source = Path("src/quantlab/dashboard/app.py").read_text(encoding="utf-8")
    assert 'width="stretch"' in source
    assert "use_container_width=True" not in source


def test_file_signature_reports_missing_files(tmp_path):
    missing = tmp_path / "missing.csv"
    assert file_signature(str(missing)) == {
        "path": str(missing),
        "mtime_ns": None,
        "size": None,
    }


def test_input_signature_changes_when_file_signature_changes(tmp_path):
    path = tmp_path / "prices.csv"
    path.write_text("a\n1\n", encoding="utf-8")
    first = build_input_signature(
        portfolio_name="p",
        strategy_name="s",
        data_path=str(path),
        execution_lag_days=1,
        transaction_cost_bps=5,
        slippage_bps=5,
        start_date=None,
        end_date=None,
        benchmark_symbol="SPY",
    )
    path.write_text("a\n1\n2\n", encoding="utf-8")
    second = build_input_signature(
        portfolio_name="p",
        strategy_name="s",
        data_path=str(path),
        execution_lag_days=1,
        transaction_cost_bps=5,
        slippage_bps=5,
        start_date=None,
        end_date=None,
        benchmark_symbol="SPY",
    )

    assert first != second
