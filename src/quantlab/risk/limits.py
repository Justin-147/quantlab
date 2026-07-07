from __future__ import annotations

from quantlab.models import AssetConfig


def check_risk_limits(
    weights: dict[str, float],
    drawdown: float,
    limits: dict,
    equity_symbols: set[str] | None = None,
    assets: dict[str, AssetConfig] | None = None,
    turnover_monthly: float | None = None,
) -> list[dict]:
    events: list[dict] = []
    max_single = float(limits.get("max_single_asset_weight", 1.0))
    for symbol, weight in weights.items():
        if symbol != "cash" and weight > max_single:
            events.append(
                {
                    "type": "limit",
                    "message": f"{symbol} weight exceeds {max_single:.0%}",
                    "value": weight,
                }
            )

    equity_weight = _asset_class_weight(
        weights, assets, "equity", equity_symbols or {"SPY", "QQQ", "NVDA", "MSFT"}
    )
    if equity_weight > float(limits.get("max_equity_weight", 1.0)):
        events.append(
            {"type": "limit", "message": "Equity exposure exceeds limit", "value": equity_weight}
        )

    technology_weight = _technology_weight(weights, assets)
    if technology_weight > float(limits.get("max_technology_weight", 1.0)):
        events.append(
            {
                "type": "limit",
                "message": "Technology exposure exceeds limit",
                "value": technology_weight,
            }
        )

    cash_weight = weights.get("cash", 0.0)
    if cash_weight < float(limits.get("min_cash_weight", -1.0)):
        events.append(
            {"type": "limit", "message": "Cash weight below minimum", "value": cash_weight}
        )

    if turnover_monthly is not None and turnover_monthly > float(
        limits.get("max_turnover_monthly", 1.0)
    ):
        events.append(
            {
                "type": "limit",
                "message": "Monthly turnover exceeds limit",
                "value": turnover_monthly,
            }
        )

    if drawdown <= -float(limits.get("max_drawdown_alert", 1.0)):
        events.append(
            {"type": "drawdown_alert", "message": "Max drawdown alert reached", "value": drawdown}
        )

    if limits.get("no_leverage", True) and cash_weight < -1e-8:
        events.append(
            {"type": "limit", "message": "Negative cash indicates leverage", "value": cash_weight}
        )
    return events


def _asset_class_weight(
    weights: dict[str, float],
    assets: dict[str, AssetConfig] | None,
    asset_class: str,
    fallback_symbols: set[str],
) -> float:
    if not assets:
        return sum(weights.get(symbol, 0.0) for symbol in fallback_symbols)
    return sum(
        weight
        for symbol, weight in weights.items()
        if symbol != "cash" and symbol in assets and assets[symbol].asset_class == asset_class
    )


def _technology_weight(weights: dict[str, float], assets: dict[str, AssetConfig] | None) -> float:
    if not assets:
        return sum(weights.get(symbol, 0.0) for symbol in {"QQQ", "NVDA", "MSFT"})
    return sum(
        weight
        for symbol, weight in weights.items()
        if symbol != "cash"
        and symbol in assets
        and (assets[symbol].sector or "").lower() == "technology"
    )
