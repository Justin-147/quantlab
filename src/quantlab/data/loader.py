from __future__ import annotations

from pathlib import Path

import pandas as pd

from quantlab.config import load_assets
from quantlab.data.sample_data import ensure_sample_prices
from quantlab.data.validator import validate_price_data


def load_price_csv(path: str | Path) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists() and csv_path.name == "prices_sample.csv":
        ensure_sample_prices(csv_path)
    df = pd.read_csv(csv_path)
    assets = load_assets()
    return validate_price_data(df, symbols=assets.keys())


def get_price_matrix(df: pd.DataFrame, price_col: str = "adjusted_close") -> pd.DataFrame:
    if price_col not in df.columns:
        raise ValueError(f"Missing price column: {price_col}")
    matrix = df.pivot(index="date", columns="symbol", values=price_col).sort_index()
    return matrix.ffill().dropna(how="all")
