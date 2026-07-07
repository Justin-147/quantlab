from __future__ import annotations

from quantlab.writers.html_writer import write_html


def test_html_writer_escapes_title_and_notice(tmp_path):
    path = write_html(
        tmp_path / "report.html",
        "# Hello",
        title="<QuantLab>",
        generated_at="<now>",
        data_source_notice="<data>",
    )
    content = path.read_text(encoding="utf-8")
    assert "<title>&lt;QuantLab&gt;</title>" in content
    assert "&lt;now&gt;" in content
    assert "&lt;data&gt;" in content
