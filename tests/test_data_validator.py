from __future__ import annotations

import pandas as pd
import pytest

from quantlab.data.sample_data import generate_sample_prices
from quantlab.data.validator import validate_price_data_report


def _valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "symbol": "SPY",
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10,
                "adjusted_close": 10,
                "volume": 100,
                "currency": "USD",
            },
            {
                "date": "2024-01-02",
                "symbol": "SPY",
                "open": 10,
                "high": 12,
                "low": 9,
                "close": 11,
                "adjusted_close": 11,
                "volume": 100,
                "currency": "USD",
            },
        ]
    )


def test_missing_column_errors():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_price_data_report(_valid_df().drop(columns=["open"]), symbols={"SPY"})


def test_zero_price_errors():
    df = _valid_df()
    df.loc[0, "open"] = 0
    with pytest.raises(ValueError, match="Non-positive"):
        validate_price_data_report(df, symbols={"SPY"})


def test_negative_price_errors():
    df = _valid_df()
    df.loc[0, "close"] = -1
    with pytest.raises(ValueError, match="Non-positive"):
        validate_price_data_report(df, symbols={"SPY"})


def test_high_low_inconsistency_errors():
    df = _valid_df()
    df.loc[0, "high"] = 8
    with pytest.raises(ValueError, match="High price"):
        validate_price_data_report(df, symbols={"SPY"})


def test_unknown_symbol_errors():
    with pytest.raises(ValueError, match="Symbols not present"):
        validate_price_data_report(_valid_df(), symbols={"BND"})


def test_duplicate_symbol_date_errors_in_strict_mode():
    df = pd.concat([_valid_df(), _valid_df().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        validate_price_data_report(df, symbols={"SPY"}, strict=True)


def test_sample_data_passes_validation(tmp_path):
    path = tmp_path / "prices_sample.csv"
    generate_sample_prices(path)
    df, issues = validate_price_data_report(
        pd.read_csv(path), symbols={"SPY", "QQQ", "BND", "GLD", "NVDA", "MSFT"}
    )
    assert not df.empty
    assert [issue for issue in issues if issue.level == "error"] == []
