from __future__ import annotations

from collections.abc import Mapping

from quantlab.models import Position


def _price_for(symbol: str, prices: Mapping[str, float]) -> float:
    price = float(prices[symbol])
    if price <= 0:
        raise ValueError(f"Price must be positive for {symbol}")
    return price


def value_positions(
    positions: Mapping[str, Position],
    prices: Mapping[str, float],
) -> dict[str, float]:
    return {
        symbol: float(position.quantity) * _price_for(symbol, prices)
        for symbol, position in positions.items()
        if position.quantity > 0 and symbol in prices
    }


def calculate_total_value(
    cash: float,
    positions: Mapping[str, Position],
    prices: Mapping[str, float],
) -> float:
    return float(cash) + sum(value_positions(positions, prices).values())


def calculate_weights(
    cash: float,
    positions: Mapping[str, Position],
    prices: Mapping[str, float],
) -> dict[str, float]:
    values = value_positions(positions, prices)
    total = float(cash) + sum(values.values())
    if total <= 0:
        return {"cash": 0.0}
    weights = {symbol: value / total for symbol, value in values.items()}
    weights["cash"] = float(cash) / total
    return weights
