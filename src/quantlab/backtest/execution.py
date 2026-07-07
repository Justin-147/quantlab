from __future__ import annotations

from datetime import datetime
from typing import Mapping

from quantlab.backtest.transaction_costs import calculate_transaction_costs
from quantlab.models import Fill, Order, Position


def execute_orders(
    orders: list[Order],
    date: datetime,
    prices: Mapping[str, float],
    cash: float,
    positions: dict[str, Position],
    transaction_cost_bps: float = 5,
    slippage_bps: float = 5,
    min_quantity: float = 1e-8,
) -> tuple[float, dict[str, Position], list[Fill]]:
    updated_positions = dict(positions)
    updated_cash = float(cash)
    fills: list[Fill] = []

    for order in orders:
        if order.symbol not in prices:
            continue
        price = float(prices[order.symbol])
        if price <= 0:
            continue

        quantity = max(0.0, float(order.quantity))
        if order.side == "sell":
            held = updated_positions.get(order.symbol)
            quantity = min(quantity, held.quantity if held else 0.0)
        else:
            cost_rate = (transaction_cost_bps + slippage_bps) / 10_000
            affordable_qty = updated_cash / (price * (1 + cost_rate))
            quantity = min(quantity, affordable_qty)

        if quantity <= min_quantity:
            continue

        notional = quantity * price
        transaction_cost, slippage_cost = calculate_transaction_costs(
            notional,
            transaction_cost_bps,
            slippage_bps,
        )
        total_fee = transaction_cost + slippage_cost

        if order.side == "buy":
            cash_impact = notional + total_fee
            if cash_impact > updated_cash + 1e-6:
                continue
            updated_cash -= cash_impact
            updated_positions = _apply_buy(updated_positions, order.symbol, quantity, price)
            total_cost = cash_impact
        else:
            cash_impact = notional - total_fee
            updated_cash += max(0.0, cash_impact)
            updated_positions = _apply_sell(updated_positions, order.symbol, quantity)
            total_cost = total_fee

        fills.append(
            Fill(
                order_id=order.id,
                date=date,
                symbol=order.symbol,
                side=order.side,
                quantity=quantity,
                price=price,
                transaction_cost=transaction_cost,
                slippage_cost=slippage_cost,
                total_cost=total_cost,
            )
        )

    return updated_cash, updated_positions, fills


def _apply_buy(
    positions: dict[str, Position],
    symbol: str,
    quantity: float,
    price: float,
) -> dict[str, Position]:
    updated = dict(positions)
    existing = updated.get(symbol)
    if existing is None:
        updated[symbol] = Position(symbol=symbol, quantity=quantity, average_cost=price)
        return updated
    new_quantity = existing.quantity + quantity
    average_cost = ((existing.quantity * existing.average_cost) + (quantity * price)) / new_quantity
    updated[symbol] = Position(
        symbol=symbol,
        quantity=new_quantity,
        average_cost=average_cost,
        currency=existing.currency,
    )
    return updated


def _apply_sell(
    positions: dict[str, Position],
    symbol: str,
    quantity: float,
) -> dict[str, Position]:
    updated = dict(positions)
    existing = updated.get(symbol)
    if existing is None:
        return updated
    new_quantity = max(0.0, existing.quantity - quantity)
    if new_quantity <= 1e-8:
        updated.pop(symbol, None)
    else:
        updated[symbol] = Position(
            symbol=symbol,
            quantity=new_quantity,
            average_cost=existing.average_cost,
            currency=existing.currency,
        )
    return updated
