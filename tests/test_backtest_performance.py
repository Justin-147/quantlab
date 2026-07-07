from __future__ import annotations

from quantlab.backtest import engine as engine_module
from quantlab.config import load_backtest_settings, load_portfolio_config, load_strategy_config
from quantlab.data.loader import load_price_csv


def test_backtest_drawdown_curve_is_not_rebuilt_inside_daily_loop(monkeypatch):
    calls = {"count": 0}
    original = engine_module.calculate_drawdown_curve

    def counted_calculate_drawdown_curve(equity_curve):
        calls["count"] += 1
        return original(equity_curve)

    monkeypatch.setattr(
        engine_module,
        "calculate_drawdown_curve",
        counted_calculate_drawdown_curve,
    )
    result = engine_module.run_backtest(
        load_price_csv("examples/sample_data/prices_sample.csv"),
        load_portfolio_config("growth_balanced"),
        load_strategy_config("periodic_rebalance"),
        load_backtest_settings(),
    )

    assert result.final_value > 0
    assert calls["count"] == 1
