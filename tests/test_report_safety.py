from __future__ import annotations

from datetime import datetime

from quantlab.models import BacktestResult, PaperAccountState
from quantlab.reports.report_builder import build_backtest_report, build_paper_report
from quantlab.writers.html_writer import write_html


def test_backtest_report_escapes_html_in_dynamic_fields(tmp_path):
    result = BacktestResult(
        portfolio_name="p<script>",
        strategy_name="s<script>",
        start_date=datetime(2026, 7, 1),
        end_date=datetime(2026, 7, 2),
        initial_value=100,
        final_value=101,
        equity_curve=[],
        drawdown_curve=[],
        fills=[],
        order_events=[],
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
    markdown = build_backtest_report(result, report_date=datetime(2026, 7, 6))
    html_path = write_html(tmp_path / "report.html", markdown)
    html = html_path.read_text(encoding="utf-8")

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_paper_report_escapes_notes_in_html(tmp_path):
    account = PaperAccountState(
        account_id="paper<script>",
        date=datetime(2026, 7, 6),
        cash=100000,
        notes=["note<script>alert(1)</script>"],
    )
    markdown = build_paper_report(account, report_date=datetime(2026, 7, 6))
    html_path = write_html(tmp_path / "paper.html", markdown)
    html = html_path.read_text(encoding="utf-8")

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
