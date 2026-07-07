from __future__ import annotations

from quantlab.models import AssetConfig


def summarize_exposure(
    date: str,
    weights: dict[str, float],
    assets: dict[str, AssetConfig],
) -> dict[str, float | str]:
    equity = 0.0
    bond = 0.0
    gold = 0.0
    for symbol, weight in weights.items():
        if symbol == "cash":
            continue
        asset = assets.get(symbol)
        asset_class = asset.asset_class if asset is not None else "other"
        if asset_class == "equity":
            equity += weight
        elif asset_class == "bond":
            bond += weight
        elif asset_class == "gold":
            gold += weight
    return {
        "date": date,
        "equity_exposure": float(equity),
        "bond_exposure": float(bond),
        "gold_exposure": float(gold),
        "cash_exposure": float(weights.get("cash", 0.0)),
        **{f"weight_{symbol}": float(weight) for symbol, weight in weights.items()},
    }
