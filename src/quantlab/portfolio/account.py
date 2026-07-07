from __future__ import annotations

from quantlab.models import Fill, Position


def apply_fill_to_positions(
    positions: dict[str, Position],
    fill: Fill,
) -> dict[str, Position]:
    updated = dict(positions)
    existing = updated.get(fill.symbol)
    if fill.side == "buy":
        if existing is None:
            updated[fill.symbol] = Position(
                symbol=fill.symbol,
                quantity=fill.quantity,
                average_cost=fill.price,
            )
        else:
            new_qty = existing.quantity + fill.quantity
            average_cost = (
                (existing.quantity * existing.average_cost) + (fill.quantity * fill.price)
            ) / new_qty
            updated[fill.symbol] = Position(
                symbol=fill.symbol,
                quantity=new_qty,
                average_cost=average_cost,
                currency=existing.currency,
            )
    else:
        if existing is None:
            return updated
        new_qty = max(0.0, existing.quantity - fill.quantity)
        if new_qty <= 1e-9:
            updated.pop(fill.symbol, None)
        else:
            updated[fill.symbol] = Position(
                symbol=fill.symbol,
                quantity=new_qty,
                average_cost=existing.average_cost,
                currency=existing.currency,
            )
    return updated
