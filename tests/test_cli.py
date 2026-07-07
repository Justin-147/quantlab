from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "quantlab.main", *args],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )


def test_cli_backtest_command_works():
    result = _run_cli(
        "backtest",
        "--portfolio",
        "growth_balanced",
        "--strategy",
        "periodic_rebalance",
        "--data",
        "examples/sample_data/prices_sample.csv",
    )
    assert "final_value:" in result.stdout
    assert Path(PROJECT_ROOT / "reports/markdown").exists()


def test_cli_compare_command_works():
    result = _run_cli(
        "compare",
        "--portfolio",
        "growth_balanced",
        "--strategies",
        "buy_and_hold",
        "periodic_rebalance",
        "trend_filter",
        "--data",
        "examples/sample_data/prices_sample.csv",
    )
    assert "json:" in result.stdout


def test_backtest_result_markdown_and_html_generated():
    _run_cli(
        "backtest",
        "--portfolio",
        "balanced_6040",
        "--strategy",
        "buy_and_hold",
        "--data",
        "examples/sample_data/prices_sample.csv",
    )
    assert list((PROJECT_ROOT / "reports/json").glob("*balanced_6040_buy_and_hold.json"))
    assert list((PROJECT_ROOT / "reports/markdown").glob("*balanced_6040_buy_and_hold.md"))
    assert list((PROJECT_ROOT / "reports/html").glob("*balanced_6040_buy_and_hold.html"))
