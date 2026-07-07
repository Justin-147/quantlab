from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from quantlab.config import load_assets, load_risk_limits, load_strategies


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    location: str
    message: str


ALLOWED_ASSET_CLASSES = {"equity", "bond", "gold", "cash", "commodity", "crypto", "other"}
ALLOWED_STRATEGIES = {"buy_and_hold", "periodic_rebalance", "trend_filter", "drawdown_buy"}


def validate_assets_config(assets: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for symbol, asset in assets.items():
        asset_class = _get(asset, "asset_class")
        currency = _get(asset, "currency")
        if not str(symbol).strip():
            issues.append(_error("assets", "asset symbol cannot be empty"))
        if asset_class not in ALLOWED_ASSET_CLASSES:
            issues.append(_error(f"assets.{symbol}.asset_class", "unsupported asset class"))
        if not str(currency or "").strip():
            issues.append(_error(f"assets.{symbol}.currency", "currency cannot be empty"))
    return issues


def validate_portfolios_config(
    portfolios: dict[str, Any], assets: dict[str, Any]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name, portfolio in portfolios.items():
        initial_cash = float(_get(portfolio, "initial_cash", 0) or 0)
        target_weights = _get(portfolio, "target_weights", {}) or {}
        if initial_cash <= 0:
            issues.append(_error(f"portfolios.{name}.initial_cash", "initial_cash must be > 0"))
        if not target_weights:
            issues.append(
                _error(f"portfolios.{name}.target_weights", "target_weights cannot be empty")
            )
        total = 0.0
        for symbol, weight in target_weights.items():
            if symbol not in assets:
                issues.append(
                    _error(f"portfolios.{name}.target_weights.{symbol}", "unknown symbol")
                )
            weight = float(weight)
            total += weight
            if weight < 0:
                issues.append(
                    _error(f"portfolios.{name}.target_weights.{symbol}", "weight must be >= 0")
                )
        if total > 1.000001:
            issues.append(_error(f"portfolios.{name}.target_weights", "weights must sum to <= 1.0"))
        elif total < 0.99:
            issues.append(
                _warning(f"portfolios.{name}.target_weights", "remaining weight is treated as cash")
            )
    return issues


def validate_strategies_config(
    strategies: dict[str, Any], assets: dict[str, Any]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name, strategy in strategies.items():
        strategy_type = _get(strategy, "type")
        if strategy_type not in ALLOWED_STRATEGIES:
            issues.append(_error(f"strategies.{name}.type", "unsupported strategy type"))
        if float(_get(strategy, "transaction_cost_bps", 0) or 0) < 0:
            issues.append(_error(f"strategies.{name}.transaction_cost_bps", "must be >= 0"))
        if float(_get(strategy, "slippage_bps", 0) or 0) < 0:
            issues.append(_error(f"strategies.{name}.slippage_bps", "must be >= 0"))
        if strategy_type == "periodic_rebalance" and _get(strategy, "rebalance_frequency") not in {
            "monthly",
            "quarterly",
        }:
            issues.append(
                _error(f"strategies.{name}.rebalance_frequency", "must be monthly or quarterly")
            )
        if strategy_type == "trend_filter":
            signal_asset = _get(strategy, "signal_asset")
            if signal_asset not in assets:
                issues.append(_error(f"strategies.{name}.signal_asset", "unknown signal asset"))
            for key in ("risk_on_weights", "risk_off_weights"):
                issues.extend(
                    _validate_weight_map(
                        f"strategies.{name}.{key}", _get(strategy, key, {}), assets
                    )
                )
        if strategy_type == "drawdown_buy":
            reference_asset = _get(strategy, "reference_asset")
            if reference_asset not in assets:
                issues.append(
                    _error(f"strategies.{name}.reference_asset", "unknown reference asset")
                )
            for index, trigger in enumerate(_get(strategy, "drawdown_triggers", []) or []):
                drawdown = float(_get(trigger, "drawdown", -1) or -1)
                amount = float(_get(trigger, "amount_pct_of_cash", 0) or 0)
                if not 0 < drawdown < 1:
                    issues.append(
                        _error(
                            f"strategies.{name}.drawdown_triggers.{index}.drawdown",
                            "must be between 0 and 1",
                        )
                    )
                if "amount_pct_of_cash" in trigger and not 0 <= amount <= 1:
                    issues.append(
                        _error(
                            f"strategies.{name}.drawdown_triggers.{index}.amount_pct_of_cash",
                            "must be between 0 and 1",
                        )
                    )
    return issues


def validate_risk_limits_config(risk_limits: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    expected = {
        "no_leverage": True,
        "live_trading_enabled": False,
        "broker_execution_enabled": False,
        "manual_confirmation_required": True,
    }
    for key, expected_value in expected.items():
        if risk_limits.get(key) is not expected_value:
            issues.append(_error(f"risk_limits.{key}", f"must be {str(expected_value).lower()}"))
    for key, value in risk_limits.items():
        if key.startswith(("max_", "min_")) and isinstance(value, int | float):
            if not 0 <= float(value) <= 1:
                issues.append(_error(f"risk_limits.{key}", "threshold must be between 0 and 1"))
    return issues


def validate_all_configs() -> list[ValidationIssue]:
    from quantlab.config import load_portfolios

    assets = load_assets()
    portfolios = load_portfolios()
    strategies = load_strategies()
    risk_limits = load_risk_limits()
    issues: list[ValidationIssue] = []
    issues.extend(validate_assets_config(assets))
    issues.extend(validate_portfolios_config(portfolios, assets))
    issues.extend(validate_strategies_config(strategies, assets))
    issues.extend(validate_risk_limits_config(risk_limits))
    return issues


def summarize_issues(issues: list[ValidationIssue]) -> dict[str, int | str]:
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    return {
        "validation_errors": errors,
        "validation_warnings": warnings,
        "status": "passed" if errors == 0 else "failed",
    }


def _validate_weight_map(
    location: str, weights: dict[str, float], assets: dict[str, Any]
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    total = 0.0
    for symbol, weight in (weights or {}).items():
        if symbol not in assets:
            issues.append(_error(f"{location}.{symbol}", "unknown symbol"))
        weight = float(weight)
        total += weight
        if weight < 0:
            issues.append(_error(f"{location}.{symbol}", "weight must be >= 0"))
    if total > 1.000001:
        issues.append(_error(location, "weights must sum to <= 1.0"))
    return issues


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _error(location: str, message: str) -> ValidationIssue:
    return ValidationIssue("error", location, message)


def _warning(location: str, message: str) -> ValidationIssue:
    return ValidationIssue("warning", location, message)
