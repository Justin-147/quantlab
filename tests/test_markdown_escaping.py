from __future__ import annotations

from quantlab.writers.formatting import fmt_number, fmt_pct, md_cell


def test_md_cell_escapes_pipe_and_newline():
    assert md_cell("alpha | beta\ngamma") == r"alpha \| beta gamma"


def test_number_formatters_handle_missing_values():
    assert fmt_number(None) == "N/A"
    assert fmt_pct(None) == "N/A"
    assert fmt_number(1234.5678, digits=2) == "1,234.57"
    assert fmt_pct(0.1234) == "12.34%"
