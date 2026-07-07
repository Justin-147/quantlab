from __future__ import annotations

import subprocess
import sys


def test_paper_run_is_dry_run_by_default(tmp_path):
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
        text=True,
        capture_output=True,
        check=True,
    )

    assert "paper_mode: local_simulation_only" in result.stdout
    assert "broker_connection: disabled" in result.stdout
    assert "orders_submitted_to_broker: 0" in result.stdout
    assert "dry_run: true" in result.stdout
    assert not (tmp_path / "data" / "paper_accounts").exists()
