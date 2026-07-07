from __future__ import annotations


def check_risk_limits(
    weights: dict[str, float],
    drawdown: float,
    limits: dict,
    equity_symbols: set[str] | None = None,
) -> list[dict]:
    events: list[dict] = []
    max_single = float(limits.get("max_single_asset_weight", 1.0))
    for symbol, weight in weights.items():
        if symbol != "cash" and weight > max_single:
            events.append({"type": "limit", "message": f"{symbol} weight exceeds {max_single:.0%}", "value": weight})

    equity_symbols = equity_symbols or {"SPY", "QQQ", "NVDA", "MSFT"}
    equity_weight = sum(weights.get(symbol, 0.0) for symbol in equity_symbols)
    if equity_weight > float(limits.get("max_equity_weight", 1.0)):
        events.append({"type": "limit", "message": "Equity exposure exceeds limit", "value": equity_weight})

    if drawdown <= -float(limits.get("max_drawdown_alert", 1.0)):
        events.append({"type": "drawdown_alert", "message": "Max drawdown alert reached", "value": drawdown})

    if limits.get("no_leverage", True) and weights.get("cash", 0.0) < -1e-8:
        events.append({"type": "limit", "message": "Negative cash indicates leverage", "value": weights.get("cash", 0.0)})
    return events
