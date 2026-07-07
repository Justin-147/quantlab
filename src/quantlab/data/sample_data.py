from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SYMBOLS = ["SPY", "QQQ", "BND", "GLD", "NVDA", "MSFT"]


def _daily_return(symbol: str, date: pd.Timestamp, rng: np.random.Generator) -> float:
    params = {
        "SPY": (0.00032, 0.011),
        "QQQ": (0.00042, 0.014),
        "BND": (0.00009, 0.003),
        "GLD": (0.00018, 0.009),
        "NVDA": (0.00065, 0.026),
        "MSFT": (0.00045, 0.016),
    }
    drift, vol = params[symbol]
    shock = rng.normal(drift, vol)

    if pd.Timestamp("2020-02-20") <= date <= pd.Timestamp("2020-04-10"):
        if symbol in {"SPY", "QQQ", "NVDA", "MSFT"}:
            shock += rng.normal(-0.006, vol * 1.4)
        elif symbol == "BND":
            shock += rng.normal(0.0004, 0.002)
        else:
            shock += rng.normal(0.001, 0.010)

    if pd.Timestamp("2022-01-03") <= date <= pd.Timestamp("2022-10-31"):
        if symbol in {"SPY", "QQQ", "NVDA", "MSFT"}:
            shock += rng.normal(-0.0012, vol * 0.7)
        elif symbol == "BND":
            shock += rng.normal(-0.00045, 0.004)
        else:
            shock += rng.normal(0.00015, 0.009)

    return float(shock)


def generate_sample_prices(
    path: str | Path = "examples/sample_data/prices_sample.csv",
    start: str = "2018-01-01",
    end: str = "2025-12-31",
    seed: int = 42,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, end=end)
    starting_prices = {
        "SPY": 267.0,
        "QQQ": 156.0,
        "BND": 80.0,
        "GLD": 124.0,
        "NVDA": 48.0,
        "MSFT": 86.0,
    }
    rows: list[dict[str, object]] = []

    for symbol in SYMBOLS:
        close = starting_prices[symbol]
        for date in dates:
            daily_return = _daily_return(symbol, date, rng)
            close = max(1.0, close * float(np.exp(daily_return)))
            open_price = close * (1 + rng.normal(0, 0.0025))
            high = max(open_price, close) * (1 + abs(rng.normal(0.003, 0.003)))
            low = min(open_price, close) * (1 - abs(rng.normal(0.003, 0.003)))
            volume_base = 2_000_000 if symbol in {"BND", "GLD"} else 10_000_000
            volume = int(max(100_000, rng.lognormal(np.log(volume_base), 0.35)))
            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "open": round(open_price, 4),
                    "high": round(high, 4),
                    "low": round(low, 4),
                    "close": round(close, 4),
                    "adjusted_close": round(close, 4),
                    "volume": volume,
                    "currency": "USD",
                }
            )

    df = pd.DataFrame(rows).sort_values(["date", "symbol"])
    df.to_csv(output, index=False)
    return output


def ensure_sample_prices(path: str | Path = "examples/sample_data/prices_sample.csv") -> Path:
    output = Path(path)
    if not output.exists():
        return generate_sample_prices(output)
    return output
