#!/usr/bin/env python3
"""
XRP Valuation Series — Article Patcher
=======================================
Run this script from the root of your futurexrp.github.io repository.

It will:
  1. Add the Google Analytics gtag to every article's <head>
  2. Add sticky series-navigation CSS to the first <style> block
  3. Inject a <nav> bar after <body> with:
       ← XRP Series   (always links back to ../)
       ← Part N       (previous article, if any)
       Part N+1 →     (next article, if any)

Usage:
    python3 patch_articles.py

The script is idempotent — re-running it will not double-inject anything.
"""

import os
import re
import sys

# ── Config ────────────────────────────────────────────────────────────────────

GTAG_ID = "G-HJE2WE51W8"

# The 5 article directories, in order
PARTS = [
    "part1",
    "part2",
    "part3",
    "part4",
    "part5",
]

# ── Injection snippets ────────────────────────────────────────────────────────

GTAG_BLOCK = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GTAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GTAG_ID}');
</script>
"""

NAV_CSS = """
  /* === XRP Series Navigation ============================================== */
  .series-nav {{
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--bg, #fbfaf7);
    border-bottom: 1px solid rgba(0,0,0,0.10);
  }}
  .series-nav-inner {{
    max-width: 740px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 46px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}
  .series-nav a {{
    text-decoration: none;
    transition: opacity 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-weight: 500;
    border: none !important;
    background: none !important;
    box-shadow: none !important;
  }}
  .series-nav a:hover {{ opacity: 0.6; }}
  .series-nav .nav-home  {{ color: #9b2226; font-weight: 700; }}
  .series-nav .nav-arrow {{ color: #595959; }}
  .series-nav .nav-label {{ color: #7a7a7a; font-size: 10px; letter-spacing: 0.05em; }}
  .series-nav .nav-sep   {{ color: #d4d4d0; margin: 0 8px; font-weight: 300; }}
  @media (max-width: 600px) {{
    .series-nav-inner {{ padding: 0 16px; font-size: 10px; }}
    .series-nav .nav-label {{ display: none; }}
  }}
  /* ======================================================================= */
"""

def make_nav_html(part_index: int, total: int = 5) -> str:
    """Build the <nav> element for a given part (1-indexed)."""
    p = part_index
    prev_n = p - 1
    next_n = p + 1

    # Left side: always ← XRP Series, + ← Part N if not first
    left = '<a href="../" class="nav-home">&#8592; XRP Series</a>'
    if p > 1:
        left += (
            f'<span class="nav-sep">|</span>'
            f'<a href="../part{prev_n}/" class="nav-arrow">&#8592; Part {prev_n}</a>'
        )

    center = f'<span class="nav-label">Part {p} of {total}</span>'

    # Right side: Part N+1 → if not last
    right = ""
    if p < total:
        right = f'<a href="../part{next_n}/" class="nav-arrow">Part {next_n} &#8594;</a>'

    return (
        f'\n  <!-- XRP Series Navigation -->\n'
        f'  <nav class="series-nav" aria-label="XRP Valuation Series navigation">\n'
        f'    <div class="series-nav-inner">\n'
        f'      <div style="display:flex;align-items:center;gap:0">{left}</div>\n'
        f'      {center}\n'
        f'      <div>{right}</div>\n'
        f'    </div>\n'
        f'  </nav>\n'
    )


# ── Core patcher ──────────────────────────────────────────────────────────────

def patch_html(html: str, part_index: int) -> str:
    """Apply all three injections to an HTML string. Idempotent."""

    # 1. Google Analytics — insert after opening <head> tag
    if GTAG_ID not in html:
        html = html.replace("<head>", "<head>\n" + GTAG_BLOCK, 1)

    # 2. Nav CSS — insert before first </style> closing tag
    if ".series-nav" not in html:
        html = html.replace("</style>", NAV_CSS + "\n  </style>", 1)

    # 3. Nav HTML — insert right after <body>
    body_pos = html.find("<body>")
    if body_pos != -1:
        # Only inject if nav isn't already there in the first 800 chars after <body>
        window = html[body_pos : body_pos + 800]
        if "series-nav" not in window:
            nav = make_nav_html(part_index)
            insert_at = body_pos + len("<body>")
            html = html[:insert_at] + nav + html[insert_at:]

    return html


def patch_file(filepath: str, part_index: int) -> bool:
    """Read, patch, and write a single index.html file."""
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filepath} — file not found")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        original = f.read()

    patched = patch_html(original, part_index)

    if patched == original:
        print(f"  [SKIP] {filepath} — already up to date")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(patched)

    delta = len(patched) - len(original)
    print(f"  [OK]   {filepath} (+{delta} bytes)")
    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Detect repository root: look for an index.html at the current dir or parent
    repo_root = os.getcwd()
    if not any(os.path.isdir(os.path.join(repo_root, p)) for p in PARTS):
        # Try parent
        parent = os.path.dirname(repo_root)
        if any(os.path.isdir(os.path.join(parent, p)) for p in PARTS):
            repo_root = parent
        else:
            print(
                "ERROR: Cannot find part1..part5 directories.\n"
                "Run this script from the root of your futurexrp.github.io repo."
            )
            sys.exit(1)

    print(f"Repository root: {repo_root}")
    print()

    patched_count = 0
    for idx, part_dir in enumerate(PARTS, start=1):
        filepath = os.path.join(repo_root, part_dir, "index.html")
        print(f"Part {idx} — {filepath}")
        if patch_file(filepath, idx):
            patched_count += 1

    print()
    if patched_count == 0:
        print("All files already up to date. Nothing changed.")
    else:
        print(f"Done. {patched_count} file(s) updated.")
        print()
        print("What was added to each file:")
        print("  • Google Analytics tag (gtag.js, ID: G-HJE2WE51W8)")
        print("  • Sticky series navigation bar:")
        print("    ← XRP Series  |  ← Part N   [Part X of 5]   Part N+1 →")


if __name__ == "__main__":
    main()
