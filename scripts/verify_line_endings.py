from __future__ import annotations

from pathlib import Path

FILES = [
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
    "LICENSE",
    "pyproject.toml",
    ".gitignore",
    ".gitattributes",
    ".github/workflows/tests.yml",
    "src/quantlab/main.py",
    "src/quantlab/backtest/engine.py",
    "src/quantlab/backtest/execution.py",
    "src/quantlab/dashboard/app.py",
    "src/quantlab/dashboard/helpers.py",
    "src/quantlab/writers/formatting.py",
    "src/quantlab/writers/html_writer.py",
    "tests/test_cli.py",
    "tests/test_dashboard_helpers.py",
    "tests/test_report_safety.py",
    "scripts/run_demo.py",
]

MIN_LF_LINES = {
    ".gitattributes": 5,
    ".gitignore": 5,
    "CHANGELOG.md": 5,
    "LICENSE": 5,
    "README.md": 20,
    "README.zh-CN.md": 20,
    "pyproject.toml": 20,
    "scripts/run_demo.py": 20,
    "scripts/verify_line_endings.py": 20,
    "src/quantlab/dashboard/app.py": 50,
    "src/quantlab/dashboard/helpers.py": 40,
    "src/quantlab/writers/formatting.py": 20,
    "tests/test_report_safety.py": 20,
}


def main() -> int:
    errors: list[str] = []
    for relative in FILES:
        path = Path(relative)
        if not path.exists():
            errors.append(f"missing file: {relative}")
            continue
        data = path.read_bytes()
        if b"\r" in data:
            errors.append(f"{relative}: contains CR characters; expected LF line endings")
        lf_count = data.count(b"\n")
        min_lf = MIN_LF_LINES.get(relative, 3)
        if lf_count < min_lf:
            errors.append(f"{relative}: only {lf_count} LF line endings; expected >= {min_lf}")
        literal_newlines = data.count(b"\\n")
        if literal_newlines > max(20, lf_count):
            errors.append(
                f"{relative}: suspicious literal \\\\n count "
                f"({literal_newlines}) exceeds threshold"
            )

    if errors:
        for error in errors:
            print(f"line_ending_error: {error}")
        return 1
    print("line_endings: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
