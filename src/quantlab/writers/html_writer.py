from __future__ import annotations

from pathlib import Path

import markdown


def write_html(path: str | Path, markdown_content: str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    html_body = markdown.markdown(markdown_content, extensions=["tables"])
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QuantLab Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1040px; margin: 32px auto; line-height: 1.55; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px; text-align: left; }}
    th {{ background: #f3f5f7; }}
    code {{ background: #f3f5f7; padding: 2px 4px; }}
  </style>
</head>
<body>
{html_body}
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
    return output
