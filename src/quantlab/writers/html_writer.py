from __future__ import annotations

from html import escape
from pathlib import Path

import markdown


def write_html(
    path: str | Path,
    markdown_content: str,
    title: str = "QuantLab Report",
    generated_at: str | None = None,
    data_source_notice: str = (
        "Data may be synthetic or user supplied. "
        "Review assumptions before interpreting results."
    ),
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    html_body = markdown.markdown(markdown_content, extensions=["tables"])
    safe_title = escape(title)
    safe_generated_at = escape(generated_at or "")
    safe_data_source_notice = escape(data_source_notice)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      max-width: 1040px;
      margin: 32px auto;
      line-height: 1.55;
      color: #17202a;
    }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px; text-align: left; }}
    th {{ background: #f3f5f7; }}
    code {{ background: #f3f5f7; padding: 2px 4px; }}
    .notice {{
      border: 1px solid #d7dde5;
      background: #f7f9fb;
      padding: 12px 14px;
      margin: 16px 0;
    }}
    .disclaimer {{
      border-left: 4px solid #9b1c1c;
      background: #fff5f5;
      padding: 12px 14px;
      margin: 16px 0;
    }}
  </style>
</head>
<body>
<div class="notice">
  <strong>Generated at:</strong> {safe_generated_at}<br>
  <strong>Data notice:</strong> {safe_data_source_notice}<br>
  <a href="../../docs/methodology.md">Methodology</a>
</div>
{html_body}
<div class="disclaimer">
  Research and education only. Not investment advice. Not trading advice.
  No real-money trading.
</div>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
    return output
