# QuantLab: Portfolio Backtesting & Paper Trading Research System

QuantLab is a local-first portfolio research system for backtesting systematic allocation rules, comparing strategies, simulating paper portfolios, and analyzing risk metrics such as drawdown, volatility, Sharpe ratio, turnover, and exposure.

It is designed for research and education only. It does not provide investment advice, trading advice, automated broker execution, or return guarantees.

## What It Does

- Loads historical or synthetic daily price CSV data.
- Builds synthetic portfolio configurations.
- Runs buy-and-hold, periodic rebalance, trend-filter, and drawdown-trigger strategies.
- Models transaction costs and slippage.
- Generates JSON, Markdown, HTML, and chart reports.
- Simulates a local paper account without broker connectivity.
- Provides a simple Streamlit dashboard.
- Includes pytest coverage for the core workflow.

## What It Does Not Do

QuantLab V1 does not trade live capital, connect to brokers, use leverage, trade options or margin, provide buy or sell recommendations, or claim that past performance predicts future results.

## Architecture

```text
config/          Portfolio, asset, strategy, risk, and backtest settings
examples/        Synthetic data, sample configs, curated reports, sample outputs
src/quantlab/    Data, portfolio, strategy, backtest, risk, paper, report, CLI, dashboard code
tests/           Unit and workflow tests
```

## Quick Start

```powershell
cd D:\CodexWork\quantlab
python -m pip install -e .
python -m quantlab.main generate-sample-data
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

If you prefer not to install the package, run commands with `PYTHONPATH` pointing at `src`.

```powershell
$env:PYTHONPATH="src"
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

## CLI Commands

Generate sample data:

```powershell
python -m quantlab.main generate-sample-data
```

Run one backtest:

```powershell
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

Compare strategies:

```powershell
python -m quantlab.main compare --portfolio growth_balanced --strategies buy_and_hold periodic_rebalance trend_filter --data examples/sample_data/prices_sample.csv
```

Run local paper simulation:

```powershell
python -m quantlab.main paper-run --portfolio growth_balanced --strategy trend_filter --data examples/sample_data/prices_sample.csv
```

Start the dashboard:

```powershell
streamlit run src/quantlab/dashboard/app.py
```

## Strategies

- `buy_and_hold`: invest once according to target weights.
- `periodic_rebalance`: rebalance monthly or quarterly and when drift exceeds a threshold.
- `trend_filter`: switch between risk-on and risk-off weights using a moving average signal.
- `drawdown_buy`: simulate adding exposure when reference-asset drawdown thresholds are reached.

## Risk Metrics

QuantLab calculates total return, annualized return, annualized volatility, Sharpe ratio, Sortino ratio, max drawdown, Calmar ratio, daily win rate, best and worst day, turnover, number of trades, and final value.

## Limitations

- Synthetic sample data is for testing and demonstration only.
- Backtests are historical simulations and may contain modeling assumptions.
- Transaction cost and slippage assumptions are simplified.
- Paper trading is local simulation only.
- No real-money order execution exists in V1.

## Disclaimer

This project is for research and education only. It is not investment advice. It is not trading advice. It does not provide recommendations to buy or sell securities. It does not execute real-money trades. Past performance does not guarantee future results.

## Tests

```powershell
pytest
```
