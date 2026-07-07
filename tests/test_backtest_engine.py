from __future__ import annotations

from quantlab.backtest.engine import run_backtest
from quantlab.config import load_backtest_settings, load_portfolio_config, load_strategy_config
from quantlab.data.loader import load_price_csv
from quantlab.data.sample_data import generate_sample_prices


def test_buy_and_hold_produces_equity_curve(tmp_path):
    csv_path = tmp_path / "prices_sample.csv"
    generate_sample_prices(csv_path)
    result = run_backtest(
        load_price_csv(csv_path),
        load_portfolio_config("balanced_6040"),
        load_strategy_config("buy_and_hold"),
        load_backtest_settings(),
    )
    assert result.equity_curve
    assert result.final_value > 0


def test_periodic_rebalance_produces_trades(tmp_path):
    csv_path = tmp_path / "prices_sample.csv"
    generate_sample_prices(csv_path)
    result = run_backtest(
        load_price_csv(csv_path),
        load_portfolio_config("growth_balanced"),
        load_strategy_config("periodic_rebalance"),
        load_backtest_settings(),
    )
    assert result.fills


def test_no_negative_cash_by_default(tmp_path):
    csv_path = tmp_path / "prices_sample.csv"
    generate_sample_prices(csv_path)
    result = run_backtest(
        load_price_csv(csv_path),
        load_portfolio_config("ai_tilt"),
        load_strategy_config("periodic_rebalance"),
        load_backtest_settings(),
    )
    assert min(point["cash"] for point in result.equity_curve) >= -1e-5
