from __future__ import annotations

from quantlab.config import load_assets, load_risk_limits
from quantlab.risk.limits import check_risk_limits


def test_risk_limits_check_technology_and_cash():
    events = check_risk_limits(
        {"QQQ": 0.5, "cash": -0.01},
        drawdown=-0.25,
        limits=load_risk_limits(),
        assets=load_assets(),
    )
    messages = " ".join(event["message"] for event in events)
    assert "Technology" in messages
    assert "Negative cash" in messages
