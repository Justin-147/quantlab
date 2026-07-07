from __future__ import annotations

from datetime import datetime

import pandas as pd

from quantlab.backtest.engine import run_backtest
from quantlab.backtest.execution import execute_orders
from quantlab.models import Order, PortfolioConfig


def test_missing_price_creates_order_event():
    order = Order(
        id="o1", date=datetime(2024, 1, 1), symbol="SPY", side="buy", quantity=1, reason="test"
    )
    cash, positions, fills, events = execute_orders([order], datetime(2024, 1, 1), {}, 1000, {})
    assert cash == 1000
    assert positions == {}
    assert fills == []
    assert events and events[0].event_type == "missing_price"


def test_execution_records_audit_events_for_reductions_and_fills():
    buy = Order(
        id="buy",
        date=datetime(2024, 1, 1),
        symbol="SPY",
        side="buy",
        quantity=100,
        reason="test",
    )
    cash, positions, fills, events = execute_orders(
        [buy],
        datetime(2024, 1, 1),
        {"SPY": 100},
        1_000,
        {},
    )
    assert cash >= 0
    assert positions["SPY"].quantity > 0
    assert fills
    assert {event.event_type for event in events} >= {"insufficient_cash", "executed"}

    sell = Order(
        id="sell",
        date=datetime(2024, 1, 2),
        symbol="SPY",
        side="sell",
        quantity=1_000,
        reason="test",
    )
    _, _, _, sell_events = execute_orders(
        [sell],
        datetime(2024, 1, 2),
        {"SPY": 100},
        cash,
        positions,
    )
    assert "insufficient_position" in {event.event_type for event in sell_events}


def test_last_day_unexecuted_order_records_expired():
    df = pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "symbol": "SPY",
                "open": 100,
                "high": 101,
                "low": 99,
                "close": 100,
                "adjusted_close": 100,
                "volume": 100,
                "currency": "USD",
            }
        ]
    )
    portfolio = PortfolioConfig(name="test", initial_cash=1000, target_weights={"SPY": 1.0})
    result = run_backtest(
        df, portfolio, {"name": "buy_and_hold", "type": "buy_and_hold"}, {"execution_lag_days": 1}
    )
    assert any(event.event_type == "expired" for event in result.order_events)
