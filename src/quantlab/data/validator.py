from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS = {
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "currency",
}
PRICE_COLUMNS = ["open", "high", "low", "close", "adjusted_close"]


@dataclass(frozen=True)
class DataValidationIssue:
    level: str
    location: str
    message: str


def validate_price_data(
    df: pd.DataFrame,
    symbols: Iterable[str] | None = None,
    strict: bool = False,
    return_issues: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, list[DataValidationIssue]]:
    validated, issues = validate_price_data_report(df, symbols=symbols, strict=strict)
    if return_issues:
        return validated, issues
    return validated


def validate_price_data_report(
    df: pd.DataFrame,
    symbols: Iterable[str] | None = None,
    strict: bool = False,
) -> tuple[pd.DataFrame, list[DataValidationIssue]]:
    issues: list[DataValidationIssue] = []
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    validated = df.copy()
    _require_non_empty(validated, "date")
    _require_non_empty(validated, "symbol")
    _require_non_empty(validated, "currency")

    validated["date"] = pd.to_datetime(validated["date"], errors="raise")
    for col in PRICE_COLUMNS:
        validated[col] = pd.to_numeric(validated[col], errors="raise")
        if (validated[col] <= 0).any():
            raise ValueError(f"Non-positive prices found in {col}")

    if "volume" in validated.columns:
        validated["volume"] = pd.to_numeric(validated["volume"], errors="coerce")
        if (validated["volume"].dropna() < 0).any():
            raise ValueError("Negative volume found")

    if (validated["high"] < validated[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("High price is inconsistent with open/close/low")
    if (validated["low"] > validated[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("Low price is inconsistent with open/close/high")

    duplicates = validated.duplicated(["date", "symbol"], keep=False)
    if duplicates.any():
        issue = DataValidationIssue(
            level="error" if strict else "warning",
            location="date+symbol",
            message="duplicate date and symbol rows found",
        )
        issues.append(issue)
        if strict:
            raise ValueError(issue.message)
        validated = validated.drop_duplicates(["date", "symbol"], keep="last")

    for symbol, group in validated.groupby("symbol", sort=False):
        if len(group) < 2:
            raise ValueError(f"Symbol {symbol} must contain at least two rows")
        if not group["date"].is_monotonic_increasing:
            raise ValueError(f"Dates must be monotonic increasing for {symbol}")

    if symbols is not None:
        unknown = set(validated["symbol"]) - set(symbols)
        if unknown:
            raise ValueError(f"Symbols not present in config: {sorted(unknown)}")

    validated = validated.sort_values(["symbol", "date"])
    validated[PRICE_COLUMNS] = validated.groupby("symbol", group_keys=False)[PRICE_COLUMNS].ffill()
    if validated[PRICE_COLUMNS].isna().any().any():
        raise ValueError("Price data contains missing values after forward fill")

    return validated.sort_values(["date", "symbol"]).reset_index(drop=True), issues


def summarize_data_issues(
    issues: list[DataValidationIssue],
    rows: int,
    symbols: int,
) -> dict[str, int | str]:
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    return {
        "data_validation_errors": errors,
        "data_validation_warnings": warnings,
        "rows": rows,
        "symbols": symbols,
        "status": "passed" if errors == 0 else "failed",
    }


def _require_non_empty(df: pd.DataFrame, column: str) -> None:
    if df[column].isna().any() or (df[column].astype(str).str.strip() == "").any():
        raise ValueError(f"{column} cannot be empty")
