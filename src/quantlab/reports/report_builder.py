from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from quantlab.models import BacktestResult, PaperAccountState


DISCLAIMER = (
    "This report is for research and education only. It is not investment advice, "
    "trading advice, or a recommendation to buy or sell securities. It does not "
    "execute real-money trades. Past performance does not guarantee future results."
)


def build_backtest_report(
    result: BacktestResult,
    chart_paths: dict[str, Path] | None = None,
) -> str:
    chart_paths = chart_paths or {}
    metrics = result.metrics
    lines = [
        f"# QuantLab Backtest Report | {result.portfolio_name} | {result.strategy_name} | {datetime.now():%Y-%m-%d}",
        "",
        "## Executive Summary",
        f"- Portfolio: {result.portfolio_name}",
        f"- Strategy: {result.strategy_name}",
        f"- Total return: {_pct(metrics.get('total_return', 0))}",
        f"- Annualized return: {_pct(metrics.get('annualized_return', 0))}",
        f"- Volatility: {_pct(metrics.get('annualized_volatility', 0))}",
        f"- Max drawdown: {_pct(metrics.get('max_drawdown', 0))}",
        "- Key risk observations: generated from synthetic or user-supplied historical data.",
        "",
        "## Portfolio and Strategy Setup",
        "| Parameter | Value |",
        "|---|---|",
        f"| Start date | {result.start_date:%Y-%m-%d} |",
        f"| End date | {result.end_date:%Y-%m-%d} |",
        f"| Initial value | {result.initial_value:,.2f} |",
        f"| Final value | {result.final_value:,.2f} |",
        "",
        "## Performance Metrics",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key} | {_format_metric(key, value)} |")

    lines.extend(
        [
            "",
            "## Risk Metrics",
            "| Metric | Value |",
            "|---|---|",
            f"| max_drawdown | {_pct(metrics.get('max_drawdown', 0))} |",
            f"| volatility | {_pct(metrics.get('annualized_volatility', 0))} |",
            f"| turnover | {_number(metrics.get('turnover', 0))} |",
            "",
            "## Equity Curve",
            f"Chart: {chart_paths.get('equity', 'reports/charts/equity.png')}",
            "",
            "## Drawdown Analysis",
            f"Chart: {chart_paths.get('drawdown', 'reports/charts/drawdown.png')}",
            "",
            "## Trade Summary",
            "| Date | Symbol | Side | Quantity | Price | Transaction Cost | Slippage Cost | Reason |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for fill in result.fills[:80]:
        lines.append(
            f"| {fill.date:%Y-%m-%d} | {fill.symbol} | {fill.side} | {fill.quantity:.4f} | "
            f"{fill.price:.2f} | {fill.transaction_cost:.2f} | {fill.slippage_cost:.2f} | {fill.order_id[:8]} |"
        )
    if len(result.fills) > 80:
        lines.append(f"| ... | ... | ... | ... | ... | ... | ... | {len(result.fills) - 80} more fills |")

    lines.extend(
        [
            "",
            "## Exposure Analysis",
            "- equity exposure",
            "- bond exposure",
            "- gold exposure",
            "- cash exposure",
            f"- top asset weights chart: {chart_paths.get('weights', 'reports/charts/weights.png')}",
            "",
            "## Strategy Interpretation",
            "- What worked: compare return, drawdown, turnover, and exposure against alternatives.",
            "- What failed: review costs, regime changes, and drawdown events.",
            "- Regimes where strategy struggled: inspect the drawdown chart and trade log.",
            "",
            "## Limitations",
            "- Historical simulation only.",
            "- Synthetic sample data if applicable.",
            "- No guarantee of future returns.",
            "- Transaction cost assumptions are simplified.",
            "- No live trading.",
            "- No investment advice.",
            "",
            "## Disclaimer",
            DISCLAIMER,
        ]
    )
    return "\n".join(lines) + "\n"


def build_comparison_report(portfolio_name: str, rows: list[dict[str, Any]], chart_path: Path | None = None) -> str:
    lines = [
        f"# QuantLab Strategy Comparison | {portfolio_name} | {datetime.now():%Y-%m-%d}",
        "",
        "## Summary",
        "| Strategy | Final Value | Annualized Return | Volatility | Max Drawdown | Sharpe | Turnover | Trades |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['strategy']} | {row['final_value']:,.2f} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['annualized_volatility'])} | {_pct(row['max_drawdown'])} | "
            f"{row['sharpe_ratio']:.2f} | {row['turnover']:.2f} | {row['number_of_trades']:.0f} |"
        )
    lines.extend(
        [
            "",
            "## Chart",
            f"Chart: {chart_path or 'reports/charts/strategy_comparison.png'}",
            "",
            "## Disclaimer",
            DISCLAIMER,
        ]
    )
    return "\n".join(lines) + "\n"


def build_paper_report(account: PaperAccountState) -> str:
    lines = [
        f"# QuantLab Paper Account Report | {account.account_id} | {datetime.now():%Y-%m-%d}",
        "",
        "## Account Status",
        f"- Date: {account.date:%Y-%m-%d}",
        f"- Cash: {account.cash:,.2f}",
        f"- Positions: {len(account.positions)}",
        f"- Pending orders: {len(account.pending_orders)}",
        f"- Fills: {len(account.fills)}",
        f"- Risk status: {account.risk_status}",
        "",
        "## Notes",
    ]
    lines.extend(f"- {note}" for note in account.notes)
    lines.extend(["", "## Disclaimer", DISCLAIMER])
    return "\n".join(lines) + "\n"


def _format_metric(key: str, value: float) -> str:
    if key in {"total_return", "annualized_return", "annualized_volatility", "max_drawdown", "win_rate_daily", "best_day", "worst_day"}:
        return _pct(value)
    return _number(value)


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _number(value: float) -> str:
    return f"{value:,.4f}"
