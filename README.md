# QuantLab: Portfolio Backtesting & Paper Trading Research System

[![tests](https://github.com/Justin-147/quantlab/actions/workflows/tests.yml/badge.svg)](https://github.com/Justin-147/quantlab/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/Justin-147/quantlab?label=release)](https://github.com/Justin-147/quantlab/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Dashboard](https://img.shields.io/badge/dashboard-Streamlit-ff4b4b.svg)](README.md#dashboard)
[![Status](https://img.shields.io/badge/status-v0.2.0-green.svg)](CHANGELOG.md)
Current release: **V0.2.0**.

**Research and education only. QuantLab is not investment advice, trading advice, a broker integration, or a real-money trading bot.**

QuantLab is a local-first portfolio research system for backtesting systematic allocation rules, comparing strategies, simulating local paper portfolios, and analyzing risk metrics such as drawdown, volatility, Sharpe ratio, turnover, exposure, benchmark tracking, VaR, and CVaR.

## What It Does

- Loads and validates daily price CSV data.
- Generates deterministic synthetic sample data.
- Validates assets, portfolios, strategies, and risk limits.
- Runs buy-and-hold, periodic rebalance, trend-filter, and drawdown-trigger strategies.
- Supports configurable execution lag, transaction cost, and slippage assumptions.
- Records fills, order events, risk events, equity, drawdown, exposure, and benchmark metrics.
- Generates JSON, Markdown, HTML, and chart reports.
- Runs a local paper simulation with broker execution disabled.
- Provides a Streamlit dashboard.
- Speeds up repeated dashboard runs with cached data, cached fast-mode results, and session state.

## What It Does Not Do

QuantLab does not connect to brokers, submit orders, use leverage, trade options or margin, scrape paid data, store API keys, provide buy/sell recommendations, or guarantee returns.

## Quick Start

```powershell
cd D:\CodexWork\quantlab
python -m pip install -e .[dev]
python -m quantlab.main validate
python -m quantlab.main validate-data --data examples/sample_data/prices_sample.csv
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/demo
```

## CLI Commands

Generate sample data:

```powershell
python -m quantlab.main generate-sample-data
```

Validate configs and data:

```powershell
python -m quantlab.main validate
python -m quantlab.main validate-data --data examples/sample_data/prices_sample.csv
```

Run one backtest:

```powershell
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/backtest
```

Compare strategies:

```powershell
python -m quantlab.main compare --portfolio growth_balanced --strategies buy_and_hold periodic_rebalance trend_filter --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/compare
```

Run local paper simulation:

```powershell
python -m quantlab.main paper-run --portfolio growth_balanced --strategy trend_filter --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/paper
```

Start the dashboard:

```powershell
streamlit run src/quantlab/dashboard/app.py
```

Fast mode is enabled by default in the dashboard. The first run loads data and computes the backtest. Repeated runs with the same inputs reuse cached data and cached JSON-safe backtest output. If the CSV file changes, the dashboard input signature includes file size and modified time, so the cache refreshes for the changed file.

## Strategies

- `buy_and_hold`: invest once according to target weights.
- `periodic_rebalance`: rebalance monthly or quarterly and when drift exceeds a threshold.
- `trend_filter`: switch between risk-on and risk-off weights using a moving average signal.
- `drawdown_buy`: simulate adding exposure when reference-asset drawdown thresholds are reached.

## Documentation

- [Methodology](docs/methodology.md)
- [Backtest Assumptions](docs/backtest_assumptions.md)
- [Input Schema](docs/input_schema.md)
- [Safety Boundary](docs/safety_boundary.md)
- [Dashboard Performance](docs/dashboard_performance.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](docs/roadmap.md)
- [GitHub About](docs/github_about.md)

## Tests and Demo

```powershell
ruff check .
python -m compileall src tests scripts
mypy src/quantlab
pytest
python scripts/run_demo.py
python -m build
```

## Disclaimer

This project is for research and education only. It is not investment advice. It is not trading advice. It does not provide recommendations to buy or sell securities. It does not execute real-money trades. Past performance does not guarantee future results.

## Release Status

Current release: `v0.2.0`.

QuantLab v0.2.0 is a local-first portfolio backtesting and paper trading research system. It supports deterministic backtests, isolated output roots, strategy comparison, risk metrics, local paper simulation, generated reports, and a Streamlit dashboard.

This project is for research and education only. It is not investment advice, trading advice, a broker integration, or a real-money trading bot.

