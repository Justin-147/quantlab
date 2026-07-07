from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from quantlab.main import parse_as_of

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


def test_cli_backtest_command_works(tmp_path):
    result = _run_cli(
        "backtest",
        "--portfolio",
        "growth_balanced",
        "--strategy",
        "periodic_rebalance",
        "--data",
        "examples/sample_data/prices_sample.csv",
        "--as-of",
        "2026-07-06",
        "--output-root",
        str(tmp_path),
    )
    assert "final_value:" in result.stdout
    assert (tmp_path / "reports/markdown").exists()


def test_cli_compare_command_works(tmp_path):
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
        "--as-of",
        "2026-07-06",
        "--output-root",
        str(tmp_path),
    )
    assert "json:" in result.stdout


def test_backtest_result_markdown_and_html_generated(tmp_path):
    _run_cli(
        "backtest",
        "--portfolio",
        "balanced_6040",
        "--strategy",
        "buy_and_hold",
        "--data",
        "examples/sample_data/prices_sample.csv",
        "--as-of",
        "2026-07-06",
        "--output-root",
        str(tmp_path),
    )
    assert list((tmp_path / "reports/json").glob("*balanced_6040_buy_and_hold.json"))
    assert list((tmp_path / "reports/markdown").glob("*balanced_6040_buy_and_hold.md"))
    assert list((tmp_path / "reports/html").glob("*balanced_6040_buy_and_hold.html"))


def test_cli_validate_commands_work():
    assert "status: passed" in _run_cli("validate").stdout
    assert (
        "status: passed"
        in _run_cli(
            "validate-data",
            "--data",
            "examples/sample_data/prices_sample.csv",
        ).stdout
    )


def test_parse_as_of_accepts_timezone_and_returns_utc_naive():
    assert parse_as_of("2026-07-06") == datetime(2026, 7, 6)
    assert parse_as_of("2026-07-06T09:00:00") == datetime(2026, 7, 6, 9)
    assert parse_as_of("2026-07-06T09:00:00+08:00") == datetime(2026, 7, 6, 1)
    with pytest.raises(argparse.ArgumentTypeError):
        parse_as_of("not-a-date")
