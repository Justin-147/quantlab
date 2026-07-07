from __future__ import annotations

from quantlab.validation.config_validator import validate_all_configs, validate_portfolios_config


def test_project_configs_validate_cleanly():
    issues = validate_all_configs()
    assert [issue for issue in issues if issue.level == "error"] == []


def test_portfolio_validation_catches_unknown_symbol():
    issues = validate_portfolios_config(
        {"bad": {"initial_cash": 1000, "target_weights": {"NOPE": 1.0}}},
        assets={"SPY": object()},
    )
    assert any(issue.level == "error" and "unknown symbol" in issue.message for issue in issues)
