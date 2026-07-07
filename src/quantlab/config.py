from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from quantlab.models import AssetConfig, PortfolioConfig


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def load_assets(path: str | Path | None = None) -> dict[str, AssetConfig]:
    raw = load_yaml(path or CONFIG_DIR / "assets.yaml").get("assets", {})
    return {
        symbol: AssetConfig(symbol=symbol, **values)
        for symbol, values in raw.items()
    }


def load_portfolios(path: str | Path | None = None) -> dict[str, PortfolioConfig]:
    raw = load_yaml(path or CONFIG_DIR / "portfolios.yaml").get("portfolios", {})
    return {name: PortfolioConfig(**values) for name, values in raw.items()}


def load_portfolio_config(name: str) -> PortfolioConfig:
    portfolios = load_portfolios()
    if name not in portfolios:
        raise KeyError(f"Unknown portfolio: {name}")
    return portfolios[name]


def load_strategies(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    return load_yaml(path or CONFIG_DIR / "strategies.yaml").get("strategies", {})


def load_strategy_config(name: str) -> dict[str, Any]:
    strategies = load_strategies()
    if name not in strategies:
        raise KeyError(f"Unknown strategy: {name}")
    return strategies[name]


def load_risk_limits(path: str | Path | None = None) -> dict[str, Any]:
    return load_yaml(path or CONFIG_DIR / "risk_limits.yaml").get("risk_limits", {})


def load_backtest_settings(path: str | Path | None = None) -> dict[str, Any]:
    return load_yaml(path or CONFIG_DIR / "backtest_settings.yaml").get("settings", {})
