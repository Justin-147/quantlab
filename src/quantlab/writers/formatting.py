from __future__ import annotations

import math
import re


def md_cell(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("|", r"\|")
    return re.sub(r"\s+", " ", text).strip()


def fmt_number(value: float | int | None, digits: int = 4) -> str:
    if value is None:
        return "N/A"
    number = float(value)
    if not math.isfinite(number):
        return "N/A"
    return f"{number:,.{digits}f}"


def fmt_pct(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    number = float(value)
    if not math.isfinite(number):
        return "N/A"
    return f"{number:.{digits}%}"
