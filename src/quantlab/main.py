from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from quantlab.backtest.engine import run_backtest
from quantlab.backtest.execution import execute_orders
from quantlab.config import (
    load_assets,
    load_backtest_settings,
    load_portfolio_config,
    load_strategy_config,
)
from quantlab.data.loader import get_price_matrix, load_price_csv
from quantlab.data.sample_data import generate_sample_prices
from quantlab.data.validator import summarize_data_issues, validate_price_data_report
from quantlab.models import PortfolioState, model_to_dict
from quantlab.paper.simulator import (
    initialize_paper_account,
    load_paper_account,
    save_paper_account,
)
from quantlab.portfolio.portfolio import refresh_state
from quantlab.reports.chart_builder import build_backtest_charts, plot_strategy_comparison
from quantlab.reports.report_builder import (
    build_backtest_report,
    build_comparison_report,
    build_paper_report,
)
from quantlab.strategies import get_strategy
from quantlab.validation.config_validator import summarize_issues, validate_all_configs
from quantlab.writers.html_writer import write_html
from quantlab.writers.json_writer import write_json
from quantlab.writers.markdown_writer import write_markdown


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args) or 0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QuantLab local portfolio research CLI")
    subparsers = parser.add_subparsers(dest="command")

    generate = subparsers.add_parser(
        "generate-sample-data",
        help="Generate synthetic sample prices",
    )
    generate.add_argument("--output", default="examples/sample_data/prices_sample.csv")
    generate.set_defaults(func=command_generate_sample_data)

    validate = subparsers.add_parser("validate", help="Validate QuantLab config files")
    validate.set_defaults(func=command_validate)

    validate_data = subparsers.add_parser("validate-data", help="Validate a price CSV")
    validate_data.add_argument("--data", required=True)
    validate_data.add_argument("--strict", action="store_true")
    validate_data.set_defaults(func=command_validate_data)

    backtest = subparsers.add_parser("backtest", help="Run a portfolio backtest")
    backtest.add_argument("--portfolio", required=True)
    backtest.add_argument("--strategy", required=True)
    backtest.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    backtest.add_argument("--as-of", type=parse_as_of, default=None)
    backtest.add_argument("--output-root", default=".")
    backtest.set_defaults(func=command_backtest)

    compare = subparsers.add_parser("compare", help="Compare strategies")
    compare.add_argument("--portfolio", required=True)
    compare.add_argument("--strategies", nargs="+", required=True)
    compare.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    compare.add_argument("--as-of", type=parse_as_of, default=None)
    compare.add_argument("--output-root", default=".")
    compare.set_defaults(func=command_compare)

    paper = subparsers.add_parser("paper-run", help="Run local paper account simulation")
    paper.add_argument("--portfolio", required=True)
    paper.add_argument("--strategy", required=True)
    paper.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    paper.add_argument("--as-of", type=parse_as_of, default=None)
    paper.add_argument("--output-root", default=".")
    paper.add_argument("--account-id", default=None)
    paper.add_argument("--reset", action="store_true")
    paper.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit no-op flag; dry run is default",
    )
    paper.add_argument(
        "--apply-local",
        action="store_true",
        help="Persist local paper account changes",
    )
    paper.set_defaults(func=command_paper_run)

    return parser


def parse_as_of(value: str | None) -> datetime | None:
    if value is None:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is not None:
            return parsed.astimezone(UTC).replace(tzinfo=None)
        return parsed
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(
        "--as-of must use YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, "
        "or an ISO-8601 datetime with timezone"
    )


def command_generate_sample_data(args: argparse.Namespace) -> int:
    output = generate_sample_prices(args.output)
    print(f"sample_data: {output}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    issues = validate_all_configs()
    for issue in issues:
        print(f"{issue.level}: {issue.location}: {issue.message}")
    summary = summarize_issues(issues)
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 1 if summary["status"] == "failed" else 0


def command_validate_data(args: argparse.Namespace) -> int:
    try:
        raw = pd.read_csv(args.data)
        validated, issues = validate_price_data_report(
            raw,
            symbols=load_assets().keys(),
            strict=args.strict,
        )
        for issue in issues:
            print(f"{issue.level}: {issue.location}: {issue.message}")
        summary = summarize_data_issues(
            issues,
            rows=len(validated),
            symbols=validated["symbol"].nunique(),
        )
    except Exception as exc:
        print(f"error: {exc}")
        summary = {
            "data_validation_errors": 1,
            "data_validation_warnings": 0,
            "rows": 0,
            "symbols": 0,
            "status": "failed",
        }
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 1 if summary["status"] == "failed" else 0


def command_backtest(args: argparse.Namespace) -> int:
    result, outputs = run_backtest_workflow(
        args.portfolio,
        args.strategy,
        args.data,
        output_root=args.output_root,
        as_of=args.as_of,
    )
    print(f"json: {outputs['json']}")
    print(f"markdown: {outputs['markdown']}")
    print(f"html: {outputs['html']}")
    print(f"final_value: {result.final_value:.2f}")
    print(f"annualized_return: {result.metrics['annualized_return']:.4f}")
    print(f"max_drawdown: {result.metrics['max_drawdown']:.4f}")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    as_of = args.as_of or datetime.now()
    output_root = Path(args.output_root)
    price_df = _load_prices_for_as_of(args.data, args.as_of)
    portfolio = load_portfolio_config(args.portfolio)
    settings = load_backtest_settings()
    rows: list[dict[str, Any]] = []

    for strategy_name in args.strategies:
        strategy_config = load_strategy_config(strategy_name)
        result = run_backtest(price_df, portfolio, strategy_config, settings)
        rows.append({"strategy": strategy_name, **result.metrics})

    stem = f"{as_of:%Y-%m-%d}_{portfolio.name}_comparison"
    chart_path = plot_strategy_comparison(rows, output_root / "reports/charts" / f"{stem}.png")
    markdown = build_comparison_report(portfolio.name, rows, chart_path, report_date=as_of)
    json_path = write_json(output_root / "reports/json" / f"{stem}.json", rows)
    markdown_path = write_markdown(output_root / "reports/markdown" / f"{stem}.md", markdown)
    html_path = write_html(
        output_root / "reports/html" / f"{stem}.html",
        markdown,
        title="QuantLab Strategy Comparison",
        generated_at=as_of.isoformat(),
    )

    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")
    print(f"html: {html_path}")
    return 0


def command_paper_run(args: argparse.Namespace) -> int:
    as_of = args.as_of or datetime.now()
    output_root = Path(args.output_root)
    price_df = _load_prices_for_as_of(args.data, args.as_of)
    portfolio = load_portfolio_config(args.portfolio)
    strategy_config = load_strategy_config(args.strategy)
    account_dir = output_root / "data/paper_accounts"

    if args.account_id and not args.reset:
        account_path = account_dir / f"{args.account_id}.json"
        if account_path.exists():
            account = load_paper_account(args.account_id, account_path)
        else:
            account = initialize_paper_account(portfolio)
    else:
        account = initialize_paper_account(portfolio, account_id=args.account_id, as_of=as_of)

    price_matrix = get_price_matrix(price_df)
    price_matrix.index = pd.to_datetime(price_matrix.index)
    latest_date = price_matrix.index.max()
    prices = price_matrix.loc[latest_date].dropna().to_dict()
    state = PortfolioState(
        date=latest_date.to_pydatetime(),
        cash=account.cash,
        positions=account.positions,
        total_value=account.cash,
        weights={"cash": 1.0},
    )
    state = refresh_state(state, prices, latest_date.to_pydatetime())
    strategy = get_strategy(strategy_config.get("type", args.strategy))
    proposed_orders = strategy.generate_orders(
        latest_date.to_pydatetime(),
        state,
        price_matrix,
        {**strategy_config, "target_weights": portfolio.target_weights},
    )
    account.pending_orders = proposed_orders
    account.date = latest_date.to_pydatetime()
    account.notes.append("paper_mode=local_simulation_only; broker_connection=disabled")

    apply_local = bool(args.apply_local)
    if apply_local:
        cash, positions, fills, order_events = execute_orders(
            proposed_orders,
            latest_date.to_pydatetime(),
            prices,
            account.cash,
            account.positions,
            strategy_config.get("transaction_cost_bps", 5),
            strategy_config.get("slippage_bps", 5),
        )
        account.cash = cash
        account.positions = positions
        account.fills.extend(fills)
        account.pending_orders = []
        account.notes.extend(event.message for event in order_events)
        save_paper_account(account, account_dir / f"{account.account_id}.json")

    markdown = build_paper_report(account, report_date=as_of)
    stem = f"{as_of:%Y-%m-%d}_{portfolio.name}_paper"
    json_path = write_json(output_root / "reports/json" / f"{stem}.json", account)
    markdown_path = write_markdown(output_root / "reports/markdown" / f"{stem}.md", markdown)

    print("paper_mode: local_simulation_only")
    print("broker_connection: disabled")
    print("orders_submitted_to_broker: 0")
    print(f"dry_run: {str(not apply_local).lower()}")
    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")
    return 0


def run_backtest_workflow(
    portfolio_name: str,
    strategy_name: str,
    data_path: str | Path,
    output_root: str | Path = ".",
    as_of: datetime | None = None,
) -> tuple[Any, dict[str, Path]]:
    report_date = as_of or datetime.now()
    output_root = Path(output_root)
    price_df = _load_prices_for_as_of(data_path, as_of)
    portfolio = load_portfolio_config(portfolio_name)
    strategy_config = load_strategy_config(strategy_name)
    result = run_backtest(price_df, portfolio, strategy_config, load_backtest_settings())

    stem = f"{report_date:%Y-%m-%d}_{portfolio.name}_{strategy_config['name']}"
    chart_paths = build_backtest_charts(result, output_root / "reports/charts")
    markdown = build_backtest_report(result, chart_paths, report_date=report_date)
    json_path = write_json(output_root / "reports/json" / f"{stem}.json", model_to_dict(result))
    markdown_path = write_markdown(output_root / "reports/markdown" / f"{stem}.md", markdown)
    html_path = write_html(
        output_root / "reports/html" / f"{stem}.html",
        markdown,
        title="QuantLab Backtest Report",
        generated_at=report_date.isoformat(),
    )
    return result, {"json": json_path, "markdown": markdown_path, "html": html_path}


def _load_prices_for_as_of(data_path: str | Path, as_of: datetime | None) -> pd.DataFrame:
    price_df = load_price_csv(data_path)
    if as_of is None:
        return price_df
    dates = pd.to_datetime(price_df["date"])
    filtered = price_df[dates <= pd.Timestamp(as_of)].copy()
    if filtered.empty:
        raise ValueError(f"No price data available on or before {as_of:%Y-%m-%d}")
    return filtered


if __name__ == "__main__":
    raise SystemExit(main())
