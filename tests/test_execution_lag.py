from __future__ import annotations

import pandas as pd

from quantlab.backtest.engine import run_backtest
from quantlab.models import PortfolioConfig


def _prices() -> pd.DataFrame:
    rows = []
    for date, spy, bnd in [
        ("2024-01-01", 100, 50),
        ("2024-01-02", 101, 51),
        ("2024-01-03", 102, 52),
    ]:
        for symbol, price in {"SPY": spy, "BND": bnd}.items():
            rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "open": price,
                    "high": price + 1,
                    "low": price - 1,
                    "close": price,
                    "adjusted_close": price,
                    "volume": 100,
                    "currency": "USD",
                }
            )
    return pd.DataFrame(rows)


def _portfolio() -> PortfolioConfig:
    return PortfolioConfig(name="test", initial_cash=1000, target_weights={"SPY": 1.0})


def test_execution_lag_zero_executes_same_day():
    result = run_backtest(
        _prices(),
        _portfolio(),
        {"name": "buy_and_hold", "type": "buy_and_hold"},
        {"execution_lag_days": 0},
    )
    assert result.fills
    assert result.fills[0].date.strftime("%Y-%m-%d") == "2024-01-01"


def test_execution_lag_one_executes_next_day():
    result = run_backtest(
        _prices(),
        _portfolio(),
        {"name": "buy_and_hold", "type": "buy_and_hold"},
        {"execution_lag_days": 1},
    )
    assert result.fills
    assert result.fills[0].date.strftime("%Y-%m-%d") == "2024-01-02"
