from __future__ import annotations

import math

import numpy as np
import pandas as pd

from quantlab.models import Fill
from quantlab.risk.drawdown import max_drawdown


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
    annualized_return = (final_value / initial_value) ** (1 / years) - 1 if initial_value > 0 else 0.0
    annualized_vol = float(returns.std(ddof=0) * math.sqrt(trading_days_per_year)) if not returns.empty else 0.0
    excess_daily = returns - (risk_free_rate / trading_days_per_year)
    sharpe = float(excess_daily.mean() / returns.std(ddof=0) * math.sqrt(trading_days_per_year)) if returns.std(ddof=0) > 0 else 0.0
    downside = returns[returns < 0]
    sortino = float(excess_daily.mean() / downside.std(ddof=0) * math.sqrt(trading_days_per_year)) if len(downside) > 1 and downside.std(ddof=0) > 0 else 0.0
    mdd = max_drawdown(df.to_dict("records"))
    calmar = annualized_return / abs(mdd) if mdd < 0 else 0.0
    turnover = _turnover(fills, initial_value)
    win_rate = float((returns > 0).mean()) if not returns.empty else 0.0
    best_day = float(returns.max()) if not returns.empty else 0.0
    worst_day = float(returns.min()) if not returns.empty else 0.0
    return {
        "total_return": _finite(total_return),
        "annualized_return": _finite(annualized_return),
        "annualized_volatility": _finite(annualized_vol),
        "sharpe_ratio": _finite(sharpe),
        "sortino_ratio": _finite(sortino),
        "max_drawdown": _finite(mdd),
        "calmar_ratio": _finite(calmar),
        "win_rate_daily": _finite(win_rate),
        "best_day": _finite(best_day),
        "worst_day": _finite(worst_day),
        "turnover": _finite(turnover),
        "number_of_trades": float(len(fills)),
        "final_value": _finite(final_value),
    }


def _turnover(fills: list[Fill], initial_value: float) -> float:
    if initial_value <= 0:
        return 0.0
    traded = sum(abs(fill.quantity * fill.price) for fill in fills)
    return float(traded / initial_value)


def _finite(value: float) -> float:
    if value is None or not np.isfinite(value):
        return 0.0
    return float(value)


def _empty_metrics() -> dict[str, float]:
    keys = [
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
        "win_rate_daily",
        "best_day",
        "worst_day",
        "turnover",
        "number_of_trades",
        "final_value",
    ]
    return {key: 0.0 for key in keys}
