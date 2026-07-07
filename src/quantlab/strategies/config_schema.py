from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, validator


class StrategyConfigBase(BaseModel):
    name: str
    transaction_cost_bps: float = Field(default=5, ge=0)
    slippage_bps: float = Field(default=5, ge=0)


class BuyAndHoldConfig(StrategyConfigBase):
    type: Literal["buy_and_hold"]


class PeriodicRebalanceConfig(StrategyConfigBase):
    type: Literal["periodic_rebalance"]
    rebalance_frequency: Literal["monthly", "quarterly"] = "monthly"
    rebalance_threshold: float = Field(default=0.05, ge=0, le=1)


class TrendFilterConfig(StrategyConfigBase):
    type: Literal["trend_filter"]
    signal_asset: str
    moving_average_window: int = Field(default=200, ge=2)
    cooldown_days: int = Field(default=20, ge=0)
    risk_on_weights: dict[str, float]
    risk_off_weights: dict[str, float]

    @validator("risk_on_weights", "risk_off_weights")
    def weights_sum_to_one_or_less(cls, value: dict[str, float]) -> dict[str, float]:
        if any(weight < 0 for weight in value.values()):
            raise ValueError("weights must be non-negative")
        if sum(value.values()) > 1.000001:
            raise ValueError("weights must sum to <= 1.0")
        return value


class DrawdownTriggerConfig(BaseModel):
    drawdown: float = Field(gt=0, lt=1)
    action: str
    amount_pct_of_cash: float | None = Field(default=None, ge=0, le=1)


class DrawdownBuyConfig(StrategyConfigBase):
    type: Literal["drawdown_buy"]
    reference_asset: str
    drawdown_triggers: list[DrawdownTriggerConfig]


def validate_strategy_schema(config: dict) -> None:
    strategy_type = str(config.get("type", ""))
    model_by_type = {
        "buy_and_hold": BuyAndHoldConfig,
        "periodic_rebalance": PeriodicRebalanceConfig,
        "trend_filter": TrendFilterConfig,
        "drawdown_buy": DrawdownBuyConfig,
    }
    model = model_by_type.get(strategy_type)
    if model is None:
        raise ValueError(f"Unsupported strategy type: {strategy_type}")
    model(**config)
