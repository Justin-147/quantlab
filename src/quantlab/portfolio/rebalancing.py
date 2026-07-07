from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import uuid4

from quantlab.models import Order, PortfolioState


def target_weight_orders(
    portfolio_state: PortfolioState,
    target_weights: Mapping[str, float],
    prices: Mapping[str, float],
    threshold: float = 0.0,
    min_notional: float = 50.0,
    reason: str = "rebalance",
) -> list[Order]:
    total_value = float(portfolio_state.total_value)
    if total_value <= 0:
        return []

    symbols = set(target_weights) | set(portfolio_state.positions)
    current_values = {
        symbol: _position_value(portfolio_state, symbol, prices)
        for symbol in symbols
    }
    current_weights = {symbol: value / total_value for symbol, value in current_values.items()}

    sells: list[Order] = []
    buys: list[tuple[str, float]] = []
    cash_after_sells = float(portfolio_state.cash)

    for symbol in symbols:
        if symbol not in prices:
            continue
        target_weight = float(target_weights.get(symbol, 0.0))
        current_weight = current_weights.get(symbol, 0.0)
        weight_diff = float(target_weight) - current_weight
        if abs(weight_diff) < threshold:
            continue
        notional_diff = weight_diff * total_value
        if abs(notional_diff) < min_notional:
            continue
        price = float(prices[symbol])
        if notional_diff < 0:
            position = portfolio_state.positions.get(symbol)
            held_quantity = position.quantity if position is not None else 0.0
            quantity = min(
                abs(notional_diff) / price,
                held_quantity,
            )
            if quantity > 0:
                cash_after_sells += quantity * price
                sells.append(_order(portfolio_state.date, symbol, "sell", quantity, reason))
        else:
            buys.append((symbol, notional_diff))

    total_buy_notional = sum(notional for _, notional in buys)
    buy_scale = min(1.0, cash_after_sells / total_buy_notional) if total_buy_notional > 0 else 1.0
    buy_orders = [
        _order(
            portfolio_state.date,
            symbol,
            "buy",
            (notional * buy_scale) / float(prices[symbol]),
            reason,
        )
        for symbol, notional in buys
        if notional * buy_scale >= min_notional
    ]
    return sells + buy_orders


def _position_value(
    portfolio_state: PortfolioState,
    symbol: str,
    prices: Mapping[str, float],
) -> float:
    position = portfolio_state.positions.get(symbol)
    if position is None or symbol not in prices:
        return 0.0
    return position.quantity * float(prices[symbol])


def _order(date: datetime, symbol: str, side: str, quantity: float, reason: str) -> Order:
    return Order(
        id=str(uuid4()),
        date=date,
        symbol=symbol,
        side=side,
        quantity=float(quantity),
        reason=reason,
    )
