from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from quantlab.models import Order


def create_order(
    date: datetime,
    symbol: str,
    side: str,
    quantity: float,
    reason: str,
) -> Order:
    return Order(
        id=str(uuid4()),
        date=date,
        symbol=symbol,
        side=side,
        quantity=float(quantity),
        reason=reason,
    )
