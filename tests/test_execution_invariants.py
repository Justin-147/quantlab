from __future__ import annotations

from datetime import datetime

import pytest

from quantlab.models import PortfolioState, Position
from quantlab.portfolio.invariants import validate_state_invariants


def test_invariants_detect_cash_below_minimum():
    state = PortfolioState(
        date=datetime(2024, 1, 1),
        cash=-1,
        positions={},
        market_value=0,
        total_value=-1,
        weights={"cash": 1},
    )
    assert validate_state_invariants(state, {}, min_cash=0)


def test_invariants_raise_on_negative_position():
    state = PortfolioState(
        date=datetime(2024, 1, 1),
        cash=100,
        positions={"SPY": Position(symbol="SPY", quantity=-1, average_cost=100)},
        market_value=-100,
        total_value=0,
        weights={"SPY": 0, "cash": 1},
    )
    with pytest.raises(ValueError, match="Negative position"):
        validate_state_invariants(state, {"SPY": 100})
