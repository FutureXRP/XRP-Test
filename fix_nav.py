#!/usr/bin/env python3
"""
fix_nav.py — fixes the series navigation in Parts 1-5 of xrpvaluation.info

Run from the directory containing part1.html, part2.html, etc.:
    python3 fix_nav.py

What it fixes:
  1. CSS double-brace bug: {{ and }} in .series-nav rules -> { and }
  2. Nav HTML: replaces the old nav block with the correct prev/next structure
  3. Updates "Part X of 5" -> "Part X of 6" in the nav label
  4. Removes the .nav-sep rule that's no longer used

Backs up each file as partN.html.bak before writing.
"""

import re
import shutil
import os

# ── Nav HTML for each part ────────────────────────────────────────────────────

NAVS = {
    "part1.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../" class="nav-home">&#8592; XRP Series</a></div>
    <span class="nav-label">Part 1 of 6</span>
    <div><a href="../part2/" class="nav-arrow">Part 2 &#8594;</a></div>
  </div>
</nav>""",

    "part2.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part1/" class="nav-arrow">&#8592; Part 1</a></div>
    <span class="nav-label">Part 2 of 6</span>
    <div><a href="../part3/" class="nav-arrow">Part 3 &#8594;</a></div>
  </div>
</nav>""",

    "part3.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part2/" class="nav-arrow">&#8592; Part 2</a></div>
    <span class="nav-label">Part 3 of 6</span>
    <div><a href="../part4/" class="nav-arrow">Part 4 &#8594;</a></div>
  </div>
</nav>""",

    "part4.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part3/" class="nav-arrow">&#8592; Part 3</a></div>
    <span class="nav-label">Part 4 of 6</span>
    <div><a href="../part5/" class="nav-arrow">Part 5 &#8594;</a></div>
  </div>
</nav>""",

    "part5.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part4/" class="nav-arrow">&#8592; Part 4</a></div>
    <span class="nav-label">Part 5 of 6</span>
    <div><a href="../part6/" class="nav-arrow">Part 6 &#8594;</a></div>
  </div>
</nav>""",
}

# ── CSS fix ───────────────────────────────────────────────────────────────────

def fix_css(html):
    """Replace double-brace CSS artifact {{ }} with single braces { }"""
    # Replace all {{ with { and all }} with } within the style block only
    # Find the style block
    style_start = html.find('<style>')
    style_end = html.find('</style>')
    if style_start == -1 or style_end == -1:
        return html

    before = html[:style_start]
    style = html[style_start:style_end + 8]
    after = html[style_end + 8:]

    # Fix double braces in CSS
    style = style.replace('{{', '{').replace('}}', '}')

    # Remove the .nav-sep rule entirely if present
    style = re.sub(r'\s*\.series-nav \.nav-sep\s*\{[^}]*\}', '', style)

    return before + style + after


# ── Nav HTML fix ──────────────────────────────────────────────────────────────

def fix_nav(html, filename):
    """Replace whatever <nav class="series-nav"> block exists with the correct one"""
    new_nav = NAVS.get(filename)
    if not new_nav:
        print(f"  No nav config for {filename}, skipping nav replacement")
        return html

    # Match any existing series-nav block
    pattern = re.compile(
        r'<!--\s*XRP Series Navigation\s*-->\s*'
        r'<nav class="series-nav".*?</nav>',
        re.DOTALL
    )
    match = pattern.search(html)
    if match:
        return html[:match.start()] + new_nav + html[match.end():]

    # Try without the comment
    pattern2 = re.compile(r'<nav class="series-nav".*?</nav>', re.DOTALL)
    match2 = pattern2.search(html)
    if match2:
        return html[:match2.start()] + new_nav + html[match2.end():]

    print(f"  WARNING: Could not find nav block in {filename}")
    return html


# ── Main ──────────────────────────────────────────────────────────────────────

def process(filename):
    if not os.path.exists(filename):
        print(f"  SKIP: {filename} not found")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    # Backup
    shutil.copy2(filename, filename + '.bak')

    # Apply fixes
    html = fix_css(html)
    html = fix_nav(html, filename)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  OK: {filename} (backup: {filename}.bak)")


if __name__ == '__main__':
    print("Fixing XRP Valuation Series navigation (Parts 1-5)...")
    print()
    for fname in ["part1.html", "part2.html", "part3.html", "part4.html", "part5.html"]:
        process(fname)
    print()
    print("Done. Run: diff partN.html partN.html.bak to review changes.")
    print("Delete .bak files once confirmed.")
