from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

import pandas as pd

from quantlab.backtest.execution import execute_orders
from quantlab.config import load_assets, load_backtest_settings, load_risk_limits
from quantlab.data.loader import get_price_matrix
from quantlab.models import BacktestResult, Order, OrderEvent, PortfolioConfig
from quantlab.portfolio.invariants import validate_state_invariants
from quantlab.portfolio.portfolio import create_initial_state, refresh_state
from quantlab.risk.benchmark import calculate_benchmark_metrics
from quantlab.risk.drawdown import calculate_drawdown_curve
from quantlab.risk.exposure import summarize_exposure
from quantlab.risk.limits import check_risk_limits
from quantlab.risk.metrics import calculate_metrics
from quantlab.strategies import get_strategy
from quantlab.strategies.base import Strategy


def run_backtest(
    price_df: pd.DataFrame,
    portfolio_config: PortfolioConfig,
    strategy_config: dict[str, Any],
    settings: dict[str, Any] | None = None,
    strategy: Strategy | None = None,
) -> BacktestResult:
    settings = {**load_backtest_settings(), **(settings or {})}
    assets = load_assets()
    risk_limits = load_risk_limits()
    price_matrix = get_price_matrix(price_df)
    price_matrix.index = pd.to_datetime(price_matrix.index)
    price_matrix = price_matrix.sort_index()
    dates = list(price_matrix.index)
    if not dates:
        raise ValueError("Price data is empty")

    strategy_type = strategy_config.get("type", strategy_config.get("name", "buy_and_hold"))
    strategy = strategy or get_strategy(strategy_type)
    merged_strategy_config = {**strategy_config, "target_weights": portfolio_config.target_weights}
    transaction_cost_bps = float(
        strategy_config.get(
            "transaction_cost_bps",
            settings.get("default_transaction_cost_bps", 5),
        )
    )
    slippage_bps = float(
        strategy_config.get("slippage_bps", settings.get("default_slippage_bps", 5))
    )
    execution_lag = int(settings.get("execution_lag_days", 1))

    state = create_initial_state(portfolio_config, dates[0].to_pydatetime())
    pending_orders: dict[pd.Timestamp, list[Order]] = defaultdict(list)
    equity_curve: list[dict[str, Any]] = []
    exposures: list[dict[str, Any]] = []
    fills = []
    risk_events: list[dict[str, Any]] = []
    order_events: list[OrderEvent] = []
    running_peak = float(state.total_value)

    for i, date in enumerate(dates):
        prices = price_matrix.loc[date].dropna().to_dict()
        orders_to_execute = pending_orders.pop(date, [])
        if orders_to_execute:
            state.cash, state.positions, new_fills, new_order_events = execute_orders(
                orders_to_execute,
                date.to_pydatetime(),
                prices,
                state.cash,
                state.positions,
                transaction_cost_bps,
                slippage_bps,
            )
            fills.extend(new_fills)
            order_events.extend(new_order_events)

        state = refresh_state(state, prices, date.to_pydatetime())
        history = price_matrix.iloc[: i + 1]
        generated_orders = strategy.generate_orders(
            date.to_pydatetime(),
            state,
            history,
            merged_strategy_config,
        )
        risk_events.extend(strategy.consume_risk_events())
        if generated_orders:
            if execution_lag == 0:
                state.cash, state.positions, new_fills, new_order_events = execute_orders(
                    generated_orders,
                    date.to_pydatetime(),
                    prices,
                    state.cash,
                    state.positions,
                    transaction_cost_bps,
                    slippage_bps,
                )
                fills.extend(new_fills)
                order_events.extend(new_order_events)
                state = refresh_state(state, prices, date.to_pydatetime())
            else:
                execute_index = i + execution_lag
                if execute_index < len(dates):
                    execute_date = dates[execute_index]
                    pending_orders[execute_date].extend(generated_orders)
                else:
                    order_events.extend(
                        _expired_order_events(date.to_pydatetime(), generated_orders)
                    )

        for invariant_issue in validate_state_invariants(state, prices):
            risk_events.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "invariant",
                    "message": invariant_issue,
                }
            )

        equity_curve.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "cash": float(state.cash),
                "market_value": float(state.market_value),
                "total_value": float(state.total_value),
            }
        )
        exposures.append(summarize_exposure(date.strftime("%Y-%m-%d"), state.weights, assets))

        running_peak = max(running_peak, float(state.total_value))
        drawdown_now = (
            float(state.total_value) / running_peak - 1.0
            if running_peak > 0
            else 0.0
        )
        for event in check_risk_limits(
            state.weights,
            drawdown_now,
            risk_limits,
            assets=assets,
        ):
            event["date"] = date.strftime("%Y-%m-%d")
            risk_events.append(event)

    drawdown_df = calculate_drawdown_curve(equity_curve)
    drawdown_curve = [
        {
            "date": row.date.strftime("%Y-%m-%d"),
            "total_value": float(row.total_value),
            "running_peak": float(row.running_peak),
            "drawdown": float(row.drawdown),
        }
        for row in drawdown_df.itertuples(index=False)
    ]
    metrics = calculate_metrics(
        equity_curve,
        fills,
        int(settings.get("trading_days_per_year", 252)),
        float(settings.get("risk_free_rate", 0.02)),
    )
    metrics.update(
        calculate_benchmark_metrics(
            equity_curve,
            price_matrix,
            benchmark_symbol=str(settings.get("benchmark_symbol", "SPY")),
        )
    )
    return BacktestResult(
        portfolio_name=portfolio_config.name,
        strategy_name=strategy_config.get("name", strategy_type),
        start_date=dates[0].to_pydatetime(),
        end_date=dates[-1].to_pydatetime(),
        initial_value=float(portfolio_config.initial_cash),
        final_value=float(equity_curve[-1]["total_value"]),
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
        fills=fills,
        order_events=order_events,
        metrics=metrics,
        exposures=exposures,
        risk_events=risk_events,
    )


def _expired_order_events(date: datetime, orders: list[Order]) -> list[OrderEvent]:
    return [
        OrderEvent(
            date=date,
            order_id=order.id,
            symbol=order.symbol,
            event_type="expired",
            message="Order expired because no future trading date was available",
            metadata={"reason": order.reason},
        )
        for order in orders
    ]
