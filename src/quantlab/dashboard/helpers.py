from __future__ import annotations

import json
import math
from datetime import date
from typing import Any

import pandas as pd


def filter_price_data(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    dates = pd.to_datetime(df["date"])
    return df[(dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))].copy()


def build_input_signature(
    *,
    portfolio_name: str,
    strategy_name: str,
    data_path: str,
    execution_lag_days: int,
    transaction_cost_bps: float,
    slippage_bps: float,
    start_date: date | str | None = None,
    end_date: date | str | None = None,
    benchmark_symbol: str | None = None,
) -> str:
    payload = {
        "benchmark_symbol": benchmark_symbol,
        "data_path": str(data_path),
        "end_date": str(end_date) if end_date is not None else None,
        "execution_lag_days": int(execution_lag_days),
        "portfolio_name": portfolio_name,
        "slippage_bps": float(slippage_bps),
        "start_date": str(start_date) if start_date is not None else None,
        "strategy_name": strategy_name,
        "transaction_cost_bps": float(transaction_cost_bps),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def result_to_frames(result: dict[str, Any] | Any) -> dict[str, pd.DataFrame]:
    data = _as_dict(result)
    frames = {
        "equity": pd.DataFrame(data.get("equity_curve", [])),
        "drawdown": pd.DataFrame(data.get("drawdown_curve", [])),
        "weights": pd.DataFrame(data.get("exposures", [])),
        "trades": pd.DataFrame(data.get("fills", [])),
        "order_events": pd.DataFrame(data.get("order_events", [])),
        "risk_events": pd.DataFrame(data.get("risk_events", [])),
        "metrics": pd.DataFrame(
            [{"metric": key, "value": value} for key, value in data.get("metrics", {}).items()]
        ),
    }
    for frame in frames.values():
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    return frames


def limit_trades(trades: pd.DataFrame, max_rows: int = 200) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    return trades.head(max_rows).copy()


def safe_metric_value(
    metrics: dict[str, Any],
    key: str,
    *,
    percent: bool = False,
    default: str = "N/A",
) -> str:
    value = metrics.get(key)
    if value is None:
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return default
    if percent:
        return f"{number:.2%}"
    return f"{number:,.2f}"


def _as_dict(value: dict[str, Any] | Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    raise TypeError("result must be a dict or Pydantic model")
