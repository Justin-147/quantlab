from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_paper_run_declares_local_simulation_only(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantlab.main",
            "paper-run",
            "--portfolio",
            "growth_balanced",
            "--strategy",
            "trend_filter",
            "--data",
            "examples/sample_data/prices_sample.csv",
            "--as-of",
            "2026-07-06",
            "--output-root",
            str(tmp_path),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "paper_mode: local_simulation_only" in result.stdout
    assert "orders_submitted_to_broker: 0" in result.stdout


def test_no_broker_adapter_module_exists():
    paths = [path.name for path in (PROJECT_ROOT / "src/quantlab").rglob("*broker*")]
    assert paths == []
