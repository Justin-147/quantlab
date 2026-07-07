from __future__ import annotations

from datetime import datetime

from quantlab.models import BacktestResult
from quantlab.reports.report_builder import DISCLAIMER, build_backtest_report, md_cell


def test_markdown_cells_escape_tables():
    assert md_cell("a | b\nc") == r"a \| b c"


def test_backtest_report_contains_disclaimer():
    result = BacktestResult(
        portfolio_name="p",
        strategy_name="s",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        initial_value=100,
        final_value=101,
        equity_curve=[],
        drawdown_curve=[],
        fills=[],
        metrics={
            "total_return": 0.01,
            "annualized_return": 0.01,
            "annualized_volatility": 0.1,
            "max_drawdown": 0.0,
            "turnover": 0.0,
        },
        exposures=[],
        risk_events=[],
    )
    assert DISCLAIMER in build_backtest_report(result, report_date=datetime(2026, 7, 6))
