from __future__ import annotations

import math

import numpy as np
import pandas as pd


def calculate_benchmark_metrics(
    equity_curve: list[dict],
    price_matrix: pd.DataFrame,
    benchmark_symbol: str = "SPY",
    trading_days_per_year: int = 252,
) -> dict[str, float]:
    if benchmark_symbol not in price_matrix.columns or not equity_curve:
        return _empty()

    equity = pd.DataFrame(equity_curve)
    equity["date"] = pd.to_datetime(equity["date"])
    equity = equity.set_index("date")["total_value"].sort_index()
    benchmark = price_matrix[benchmark_symbol].copy()
    benchmark.index = pd.to_datetime(benchmark.index)
    joined = pd.concat([equity, benchmark], axis=1, join="inner").dropna()
    joined.columns = ["equity", "benchmark"]
    if len(joined) < 2:
        return _empty()

    portfolio_returns = joined["equity"].pct_change().dropna()
    benchmark_returns = joined["benchmark"].pct_change().dropna()
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1, join="inner").dropna()
    aligned.columns = ["portfolio", "benchmark"]
    if aligned.empty:
        return _empty()

    benchmark_total_return = joined["benchmark"].iloc[-1] / joined["benchmark"].iloc[0] - 1
    years = max((joined.index[-1] - joined.index[0]).days / 365.25, 1 / trading_days_per_year)
    benchmark_annualized = (joined["benchmark"].iloc[-1] / joined["benchmark"].iloc[0]) ** (
        1 / years
    ) - 1
    portfolio_total_return = joined["equity"].iloc[-1] / joined["equity"].iloc[0] - 1
    active = aligned["portfolio"] - aligned["benchmark"]
    tracking_error = float(active.std(ddof=0) * math.sqrt(trading_days_per_year))
    information_ratio = _ratio(float(active.mean() * trading_days_per_year), tracking_error)
    benchmark_var = float(aligned["benchmark"].var(ddof=0))
    beta = (
        float(aligned["portfolio"].cov(aligned["benchmark"]) / benchmark_var)
        if benchmark_var > 0
        else 0.0
    )
    alpha = float(
        (aligned["portfolio"].mean() - beta * aligned["benchmark"].mean()) * trading_days_per_year
    )
    correlation = float(aligned["portfolio"].corr(aligned["benchmark"]))
    metrics = {
        "benchmark_total_return": benchmark_total_return,
        "benchmark_annualized_return": benchmark_annualized,
        "active_return": portfolio_total_return - benchmark_total_return,
        "tracking_error": tracking_error,
        "information_ratio": information_ratio,
        "beta": beta,
        "alpha": alpha,
        "correlation": correlation,
    }
    return {key: _finite(value) for key, value in metrics.items()}


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0 or not np.isfinite(denominator):
        return 0.0
    return float(numerator / denominator)


def _finite(value: float) -> float:
    if value is None or not np.isfinite(value):
        return 0.0
    return float(value)


def _empty() -> dict[str, float]:
    return {
        "benchmark_total_return": 0.0,
        "benchmark_annualized_return": 0.0,
        "active_return": 0.0,
        "tracking_error": 0.0,
        "information_ratio": 0.0,
        "beta": 0.0,
        "alpha": 0.0,
        "correlation": 0.0,
    }
