from __future__ import annotations

import math

import numpy as np
import pandas as pd

from quantlab.models import Fill
from quantlab.risk.drawdown import longest_drawdown_duration, max_drawdown


def calculate_metrics(
    equity_curve: list[dict],
    fills: list[Fill] | None = None,
    trading_days_per_year: int = 252,
    risk_free_rate: float = 0.02,
) -> dict[str, float]:
    fills = fills or []
    df = pd.DataFrame(equity_curve)
    if df.empty:
        return _empty_metrics()
    df["date"] = pd.to_datetime(df["date"])
    df["total_value"] = pd.to_numeric(df["total_value"])
    df = df.sort_values("date")
    returns = df["total_value"].pct_change().dropna()
    initial_value = float(df["total_value"].iloc[0])
    final_value = float(df["total_value"].iloc[-1])
    total_return = final_value / initial_value - 1 if initial_value else 0.0
    years = max((df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25, 1 / trading_days_per_year)
    annualized_return = (
        (final_value / initial_value) ** (1 / years) - 1 if initial_value > 0 else 0.0
    )
    annualized_vol = _std(returns) * math.sqrt(trading_days_per_year)
    excess_daily = returns - (risk_free_rate / trading_days_per_year)
    sharpe = _ratio(float(excess_daily.mean() * math.sqrt(trading_days_per_year)), _std(returns))
    downside = returns[returns < 0]
    downside_vol = _std(downside) * math.sqrt(trading_days_per_year)
    sortino = _ratio(float(excess_daily.mean() * math.sqrt(trading_days_per_year)), _std(downside))
    mdd = max_drawdown(df.to_dict("records"))
    calmar = annualized_return / abs(mdd) if mdd < 0 else 0.0
    turnover = _turnover(fills, initial_value)
    positives = returns[returns > 0]
    negatives = returns[returns < 0]
    profit_factor = _ratio(float(positives.sum()), abs(float(negatives.sum())))
    var_95 = float(returns.quantile(0.05)) if not returns.empty else 0.0
    cvar_95 = float(returns[returns <= var_95].mean()) if not returns.empty else 0.0
    rolling_vol = returns.rolling(63).std(ddof=0) * math.sqrt(trading_days_per_year)
    monthly_returns = df.set_index("date")["total_value"].resample("M").last().pct_change().dropna()

    metrics = {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_vol,
        "annualized_downside_volatility": downside_vol,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": mdd,
        "calmar_ratio": calmar,
        "win_rate_daily": float((returns > 0).mean()) if not returns.empty else 0.0,
        "best_day": float(returns.max()) if not returns.empty else 0.0,
        "worst_day": float(returns.min()) if not returns.empty else 0.0,
        "average_positive_day": float(positives.mean()) if not positives.empty else 0.0,
        "average_negative_day": float(negatives.mean()) if not negatives.empty else 0.0,
        "profit_factor": profit_factor,
        "skewness": float(returns.skew()) if len(returns) > 2 else 0.0,
        "kurtosis": float(returns.kurtosis()) if len(returns) > 3 else 0.0,
        "longest_drawdown_duration": float(longest_drawdown_duration(df.to_dict("records"))),
        "recovery_days": float(_recovery_days(df)),
        "rolling_63d_volatility_latest": float(rolling_vol.dropna().iloc[-1])
        if not rolling_vol.dropna().empty
        else 0.0,
        "monthly_return_mean": float(monthly_returns.mean()) if not monthly_returns.empty else 0.0,
        "monthly_return_std": float(monthly_returns.std(ddof=0))
        if not monthly_returns.empty
        else 0.0,
        "var_95": var_95,
        "cvar_95": cvar_95,
        "turnover": turnover,
        "number_of_trades": float(len(fills)),
        "final_value": final_value,
    }
    return {key: _finite(value) for key, value in metrics.items()}


def _turnover(fills: list[Fill], initial_value: float) -> float:
    if initial_value <= 0:
        return 0.0
    traded = sum(abs(fill.quantity * fill.price) for fill in fills)
    return float(traded / initial_value)


def _recovery_days(df: pd.DataFrame) -> int:
    values = df["total_value"]
    peak = values.cummax()
    underwater = values < peak
    if not underwater.any():
        return 0
    last_peak_index = int(np.where(~underwater)[0][-1]) if (~underwater).any() else 0
    if last_peak_index == len(values) - 1:
        return 0
    return len(values) - 1 - last_peak_index


def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0 or not np.isfinite(denominator):
        return 0.0
    return float(numerator / denominator)


def _std(series: pd.Series) -> float:
    return float(series.std(ddof=0)) if len(series) > 1 else 0.0


def _finite(value: float) -> float:
    if value is None or not np.isfinite(value):
        return 0.0
    return float(value)


def _empty_metrics() -> dict[str, float]:
    keys = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "annualized_downside_volatility",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
        "win_rate_daily",
        "best_day",
        "worst_day",
        "average_positive_day",
        "average_negative_day",
        "profit_factor",
        "skewness",
        "kurtosis",
        "longest_drawdown_duration",
        "recovery_days",
        "rolling_63d_volatility_latest",
        "monthly_return_mean",
        "monthly_return_std",
        "var_95",
        "cvar_95",
        "turnover",
        "number_of_trades",
        "final_value",
    ]
    return {key: 0.0 for key in keys}
