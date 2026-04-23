#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
PUBLIC_FEEDS_DIR = PUBLIC_DIR / "feeds"


def build_feeds() -> None:
    subprocess.run(
        ["python3", str(ROOT / "scripts" / "build_feeds.py"), "--output", str(PUBLIC_FEEDS_DIR)],
        check=True,
    )


def build_index() -> None:
    manifest_path = PUBLIC_FEEDS_DIR / "github-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = manifest["assets"]

    items = []
    for name in sorted(assets):
        meta = assets[name]
        href = f"./feeds/{escape(name)}"
        label = escape(name)
        category = escape(str(meta["category"]))
        family = escape(str(meta["family"]))
        count = escape(str(meta["count"]))
        items.append(
            f'<li><a href="{href}">{label}</a> '
            f'<span>provider=github category={category} family={family} count={count}</span></li>'
        )

    generated_at = escape(str(manifest["generated_at_utc"]))
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>network-prefix-feeds</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f7fb;
        --fg: #141824;
        --muted: #5d677d;
        --card: #ffffff;
        --line: #d8deeb;
        --accent: #0f62fe;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        padding: 32px 20px 48px;
        font: 16px/1.5 ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--fg);
        background: linear-gradient(180deg, #eef3ff 0%, var(--bg) 45%, #fbfcff 100%);
      }}
      main {{
        max-width: 900px;
        margin: 0 auto;
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 16px 40px rgba(28, 39, 76, 0.08);
      }}
      h1 {{
        margin: 0 0 8px;
        font-size: 32px;
      }}
      p {{
        margin: 0 0 16px;
        color: var(--muted);
      }}
      code {{
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 0.95em;
      }}
      ul {{
        margin: 24px 0 0;
        padding: 0;
        list-style: none;
      }}
      li {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        padding: 10px 0;
        border-top: 1px solid var(--line);
      }}
      li:first-child {{ border-top: 0; }}
      a {{
        color: var(--accent);
        text-decoration: none;
        font-weight: 600;
      }}
      span {{
        color: var(--muted);
        text-align: right;
        font-size: 14px;
      }}
      @media (max-width: 720px) {{
        li {{
          display: block;
        }}
        span {{
          display: block;
          margin-top: 4px;
          text-align: left;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>network-prefix-feeds</h1>
      <p>Static prefix feeds for routers and policy-routing consumers.</p>
      <p>Generated at <code>{generated_at}</code>.</p>
      <ul>
        {"".join(items)}
      </ul>
    </main>
  </body>
</html>
"""
    (PUBLIC_DIR / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_FEEDS_DIR.mkdir(parents=True, exist_ok=True)
    build_feeds()
    build_index()


if __name__ == "__main__":
    main()
