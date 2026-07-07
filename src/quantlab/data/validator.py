from __future__ import annotations

from collections.abc import Iterable

import pandas as pd


REQUIRED_COLUMNS = {
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "currency",
}


def validate_price_data(df: pd.DataFrame, symbols: Iterable[str] | None = None) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    validated = df.copy()
    validated["date"] = pd.to_datetime(validated["date"], errors="raise")
    price_cols = ["open", "high", "low", "close", "adjusted_close"]
    for col in price_cols:
        validated[col] = pd.to_numeric(validated[col], errors="raise")
        if (validated[col] < 0).any():
            raise ValueError(f"Negative prices found in {col}")

    if validated.duplicated(["date", "symbol"]).any():
        validated = validated.drop_duplicates(["date", "symbol"], keep="last")

    if symbols is not None:
        unknown = set(validated["symbol"]) - set(symbols)
        if unknown:
            raise ValueError(f"Symbols not present in config: {sorted(unknown)}")

    validated = validated.sort_values(["symbol", "date"])
    validated[price_cols] = validated.groupby("symbol", group_keys=False)[price_cols].ffill()
    if validated[price_cols].isna().any().any():
        raise ValueError("Price data contains missing values after forward fill")

    return validated.sort_values(["date", "symbol"]).reset_index(drop=True)
