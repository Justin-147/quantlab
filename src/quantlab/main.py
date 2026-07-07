from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from quantlab.backtest.engine import run_backtest
from quantlab.config import load_backtest_settings, load_portfolio_config, load_strategy_config
from quantlab.data.loader import load_price_csv
from quantlab.data.sample_data import generate_sample_prices
from quantlab.models import model_to_dict
from quantlab.paper.simulator import initialize_paper_account, run_paper_day, save_paper_account
from quantlab.reports.chart_builder import build_backtest_charts, plot_strategy_comparison
from quantlab.reports.report_builder import build_backtest_report, build_comparison_report, build_paper_report
from quantlab.writers.html_writer import write_html
from quantlab.writers.json_writer import write_json
from quantlab.writers.markdown_writer import write_markdown


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    args.func(args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QuantLab local portfolio research CLI")
    subparsers = parser.add_subparsers(dest="command")

    generate = subparsers.add_parser("generate-sample-data", help="Generate synthetic sample prices")
    generate.add_argument("--output", default="examples/sample_data/prices_sample.csv")
    generate.set_defaults(func=command_generate_sample_data)

    backtest = subparsers.add_parser("backtest", help="Run a portfolio backtest")
    backtest.add_argument("--portfolio", required=True)
    backtest.add_argument("--strategy", required=True)
    backtest.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    backtest.set_defaults(func=command_backtest)

    compare = subparsers.add_parser("compare", help="Compare strategies")
    compare.add_argument("--portfolio", required=True)
    compare.add_argument("--strategies", nargs="+", required=True)
    compare.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    compare.set_defaults(func=command_compare)

    paper = subparsers.add_parser("paper-run", help="Run local paper account simulation")
    paper.add_argument("--portfolio", required=True)
    paper.add_argument("--strategy", required=True)
    paper.add_argument("--data", default="examples/sample_data/prices_sample.csv")
    paper.set_defaults(func=command_paper_run)

    return parser


def command_generate_sample_data(args: argparse.Namespace) -> None:
    output = generate_sample_prices(args.output)
    print(f"sample_data: {output}")


def command_backtest(args: argparse.Namespace) -> None:
    result, outputs = run_backtest_workflow(args.portfolio, args.strategy, args.data)
    print(f"json: {outputs['json']}")
    print(f"markdown: {outputs['markdown']}")
    print(f"html: {outputs['html']}")
    print(f"final_value: {result.final_value:.2f}")
    print(f"annualized_return: {result.metrics['annualized_return']:.4f}")
    print(f"max_drawdown: {result.metrics['max_drawdown']:.4f}")


def command_compare(args: argparse.Namespace) -> None:
    price_df = load_price_csv(args.data)
    portfolio = load_portfolio_config(args.portfolio)
    settings = load_backtest_settings()
    rows: list[dict[str, Any]] = []

    for strategy_name in args.strategies:
        strategy_config = load_strategy_config(strategy_name)
        result = run_backtest(price_df, portfolio, strategy_config, settings)
        rows.append({"strategy": strategy_name, **result.metrics})

    today = datetime.now().strftime("%Y-%m-%d")
    stem = f"{today}_{portfolio.name}_comparison"
    chart_path = plot_strategy_comparison(rows, Path("reports/charts") / f"{stem}.png")
    markdown = build_comparison_report(portfolio.name, rows, chart_path)
    json_path = write_json(Path("reports/json") / f"{stem}.json", rows)
    markdown_path = write_markdown(Path("reports/markdown") / f"{stem}.md", markdown)
    html_path = write_html(Path("reports/html") / f"{stem}.html", markdown)

    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")
    print(f"html: {html_path}")


def command_paper_run(args: argparse.Namespace) -> None:
    price_df = load_price_csv(args.data)
    portfolio = load_portfolio_config(args.portfolio)
    account = initialize_paper_account(portfolio)
    latest_date = pd.to_datetime(price_df["date"]).max().to_pydatetime()
    latest_prices = (
        price_df[pd.to_datetime(price_df["date"]) == latest_date]
        .set_index("symbol")["adjusted_close"]
        .to_dict()
    )
    account = run_paper_day(account, latest_date, latest_prices)
    account.notes.append(f"Strategy selected for paper review: {args.strategy}")

    today = datetime.now().strftime("%Y-%m-%d")
    stem = f"{today}_{portfolio.name}_paper"
    json_path = write_json(Path("reports/json") / f"{stem}.json", account)
    markdown = build_paper_report(account)
    markdown_path = write_markdown(Path("reports/markdown") / f"{stem}.md", markdown)
    save_paper_account(account)
    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")


def run_backtest_workflow(
    portfolio_name: str,
    strategy_name: str,
    data_path: str | Path,
) -> tuple[Any, dict[str, Path]]:
    price_df = load_price_csv(data_path)
    portfolio = load_portfolio_config(portfolio_name)
    strategy_config = load_strategy_config(strategy_name)
    result = run_backtest(price_df, portfolio, strategy_config, load_backtest_settings())

    today = datetime.now().strftime("%Y-%m-%d")
    stem = f"{today}_{portfolio.name}_{strategy_config['name']}"
    chart_paths = build_backtest_charts(result, "reports/charts")
    markdown = build_backtest_report(result, chart_paths)
    json_path = write_json(Path("reports/json") / f"{stem}.json", model_to_dict(result))
    markdown_path = write_markdown(Path("reports/markdown") / f"{stem}.md", markdown)
    html_path = write_html(Path("reports/html") / f"{stem}.html", markdown)
    return result, {"json": json_path, "markdown": markdown_path, "html": html_path}


if __name__ == "__main__":
    raise SystemExit(main())
