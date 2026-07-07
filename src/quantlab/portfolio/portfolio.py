from __future__ import annotations

from datetime import datetime
from typing import Mapping

from quantlab.models import PortfolioConfig, PortfolioState, Position
from quantlab.portfolio.valuation import calculate_total_value, calculate_weights


def create_initial_state(config: PortfolioConfig, date: datetime) -> PortfolioState:
    return PortfolioState(
        date=date,
        cash=float(config.initial_cash),
        positions={},
        market_value=0.0,
        total_value=float(config.initial_cash),
        weights={"cash": 1.0},
    )


def initialize_portfolio_from_target(
    config: PortfolioConfig,
    prices: Mapping[str, float],
    date: datetime,
) -> PortfolioState:
    positions: dict[str, Position] = {}
    cash = float(config.initial_cash)
    for symbol, weight in config.target_weights.items():
        if weight <= 0:
            continue
        notional = config.initial_cash * weight
        quantity = notional / float(prices[symbol])
        cash -= notional
        positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            average_cost=float(prices[symbol]),
            currency=config.currency,
        )
    total = calculate_total_value(cash, positions, prices)
    return PortfolioState(
        date=date,
        cash=cash,
        positions=positions,
        market_value=total - cash,
        total_value=total,
        weights=calculate_weights(cash, positions, prices),
    )


def refresh_state(
    state: PortfolioState,
    prices: Mapping[str, float],
    date: datetime,
) -> PortfolioState:
    total = calculate_total_value(state.cash, state.positions, prices)
    return PortfolioState(
        date=date,
        cash=state.cash,
        positions=state.positions,
        market_value=total - state.cash,
        total_value=total,
        weights=calculate_weights(state.cash, state.positions, prices),
    )
