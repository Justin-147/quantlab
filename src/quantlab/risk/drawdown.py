from __future__ import annotations

import pandas as pd


def calculate_drawdown_curve(equity_curve: list[dict] | pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame(equity_curve).copy()
    if df.empty:
        return pd.DataFrame(columns=["date", "total_value", "running_peak", "drawdown"])
    value_col = "total_value" if "total_value" in df.columns else "equity"
    df["date"] = pd.to_datetime(df["date"])
    df[value_col] = pd.to_numeric(df[value_col])
    df["running_peak"] = df[value_col].cummax()
    df["drawdown"] = df[value_col] / df["running_peak"] - 1.0
    return df[["date", value_col, "running_peak", "drawdown"]].rename(
        columns={value_col: "total_value"}
    )


def max_drawdown(equity_curve: list[dict] | pd.DataFrame) -> float:
    curve = calculate_drawdown_curve(equity_curve)
    if curve.empty:
        return 0.0
    return float(curve["drawdown"].min())


def longest_drawdown_duration(equity_curve: list[dict] | pd.DataFrame) -> int:
    curve = calculate_drawdown_curve(equity_curve)
    longest = 0
    current = 0
    for drawdown in curve["drawdown"].fillna(0):
        if drawdown < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest
