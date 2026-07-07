from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    [sys.executable, "-m", "compileall", "src", "tests"],
    [sys.executable, "-m", "pytest"],
    [sys.executable, "-m", "quantlab.main", "validate"],
    [
        sys.executable,
        "-m",
        "quantlab.main",
        "validate-data",
        "--data",
        "examples/sample_data/prices_sample.csv",
    ],
    [
        sys.executable,
        "-m",
        "quantlab.main",
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
        ".tmp/demo",
    ],
    [
        sys.executable,
        "-m",
        "quantlab.main",
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
        ".tmp/demo",
    ],
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
        ".tmp/demo",
    ],
]


def main() -> int:
    for command in COMMANDS:
        subprocess.run(command, check=True)
    print("demo_status=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
