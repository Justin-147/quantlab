from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from quantlab.models import BacktestResult


def build_backtest_charts(
    result: BacktestResult, output_dir: str | Path = "reports/charts"
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    stem = f"{result.portfolio_name}_{result.strategy_name}"
    equity_path = output / f"{stem}_equity.png"
    drawdown_path = output / f"{stem}_drawdown.png"
    weights_path = output / f"{stem}_weights.png"
    plot_equity_curve(result, equity_path)
    plot_drawdown_curve(result, drawdown_path)
    plot_weights(result, weights_path)
    return {"equity": equity_path, "drawdown": drawdown_path, "weights": weights_path}


def plot_equity_curve(result: BacktestResult, path: str | Path) -> Path:
    df = pd.DataFrame(result.equity_curve)
    df["date"] = pd.to_datetime(df["date"])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(df["date"], df["total_value"], color="#1f77b4", linewidth=1.8)
    ax.set_title("Equity Curve")
    ax.set_ylabel("Portfolio Value")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return _save(fig, path)


def plot_drawdown_curve(result: BacktestResult, path: str | Path) -> Path:
    df = pd.DataFrame(result.drawdown_curve)
    df["date"] = pd.to_datetime(df["date"])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.fill_between(df["date"], df["drawdown"], 0, color="#d62728", alpha=0.35)
    ax.set_title("Drawdown")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return _save(fig, path)


def plot_weights(result: BacktestResult, path: str | Path) -> Path:
    df = pd.DataFrame(result.exposures)
    df["date"] = pd.to_datetime(df["date"])
    weight_cols = [col for col in df.columns if col.startswith("weight_")]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    if weight_cols:
        df.plot(x="date", y=weight_cols, ax=ax, linewidth=1.2)
    ax.set_title("Portfolio Weights")
    ax.set_ylabel("Weight")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return _save(fig, path)


def plot_strategy_comparison(comparison: list[dict], path: str | Path) -> Path:
    df = pd.DataFrame(comparison)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    if not df.empty:
        ax.bar(df["strategy"], df["annualized_return"], color="#2ca02c")
    ax.set_title("Strategy Comparison: Annualized Return")
    ax.set_ylabel("Annualized Return")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    return _save(fig, path)


def _save(fig: plt.Figure, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=140)
    plt.close(fig)
    return output
