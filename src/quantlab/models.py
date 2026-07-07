from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, validator


class PriceBar(BaseModel):
    date: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: float | None = None
    currency: str = "USD"


class AssetConfig(BaseModel):
    symbol: str
    name: str
    asset_class: str
    currency: str = "USD"


class PortfolioConfig(BaseModel):
    name: str
    currency: str = "USD"
    initial_cash: float
    target_weights: dict[str, float]

    @validator("initial_cash")
    def initial_cash_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("initial_cash must be positive")
        return value

    @validator("target_weights")
    def validate_target_weights(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            raise ValueError("target_weights cannot be empty")
        if any(weight < 0 for weight in value.values()):
            raise ValueError("target weights must be non-negative")
        total = sum(value.values())
        if total > 1.000001:
            raise ValueError("target weights must sum to <= 1.0")
        return value


class Position(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    currency: str = "USD"


class PortfolioState(BaseModel):
    date: datetime
    cash: float
    positions: dict[str, Position] = Field(default_factory=dict)
    market_value: float = 0.0
    total_value: float = 0.0
    weights: dict[str, float] = Field(default_factory=dict)


class Order(BaseModel):
    id: str
    date: datetime
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    reason: str
    status: str = "pending"

    @validator("side")
    def side_must_be_supported(cls, value: str) -> str:
        if value not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        return value


class Fill(BaseModel):
    order_id: str
    date: datetime
    symbol: str
    side: str
    quantity: float
    price: float
    transaction_cost: float
    slippage_cost: float
    total_cost: float


class BacktestResult(BaseModel):
    portfolio_name: str
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_value: float
    final_value: float
    equity_curve: list[dict[str, Any]]
    drawdown_curve: list[dict[str, Any]]
    fills: list[Fill]
    metrics: dict[str, float]
    exposures: list[dict[str, Any]]
    risk_events: list[dict[str, Any]]


class PaperAccountState(BaseModel):
    account_id: str
    date: datetime
    cash: float
    positions: dict[str, Position] = Field(default_factory=dict)
    pending_orders: list[Order] = Field(default_factory=list)
    fills: list[Fill] = Field(default_factory=list)
    equity_history: list[dict[str, Any]] = Field(default_factory=list)
    risk_status: str = "ok"
    notes: list[str] = Field(default_factory=list)


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")
    return _jsonable(model.dict())


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return model_to_dict(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
