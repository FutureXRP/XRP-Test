#!/usr/bin/env python3
"""
fix_bg.py — fixes Part 4 and Part 5 background colors to match Parts 1-3 and 6

Run from your repo root:
    python3 fix_bg.py

Changes:
  part4/index.html:
    - Page background #F4EDDD -> #fbfaf7 (matches series bg)
    - Content box bg #EDE3CC -> #f7f3ea (warmer white for boxes)
    - Highlight layer bg #E4D6B8 -> #eee8dc (softer highlight)

  part5/index.html:
    - Page background #f5f0e8 -> #fbfaf7 (matches series bg)
    - Content box bg #ede6d6 -> #f7f3ea (warmer white for boxes)
    - Card bg #efe9db -> #f4f0e8 (softer card bg)

Backs up each file as index.html.bak before writing.
"""

import shutil, os

FILES = {
    "part4/index.html": [
        # (old, new) — ordered most-specific first
        ("#F4EDDD", "#fbfaf7"),   # --cream -> page bg
        ("#EDE3CC", "#f7f3ea"),   # --cream-deep -> box bg
        ("#E4D6B8", "#eee8dc"),   # --cream-shadow -> highlight layer
    ],
    "part5/index.html": [
        ("#f5f0e8", "#fbfaf7"),   # --cream -> page bg
        ("#ede6d6", "#f7f3ea"),   # --cream-deep -> box bg
        ("#efe9db", "#f4f0e8"),   # --cream-card -> card bg
    ],
}

def process(filename, replacements):
    if not os.path.exists(filename):
        print(f"  SKIP: {filename} not found")
        return

    with open(filename, "r", encoding="utf-8") as f:
        html = f.read()

    shutil.copy2(filename, filename + ".bak")

    for old, new in replacements:
        count = html.count(old)
        html = html.replace(old, new)
        print(f"    {old} -> {new}  ({count} replacements)")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  OK: {filename}")

print("Fixing Part 4 and Part 5 background colors...")
print()
for fname, replacements in FILES.items():
    print(f"Processing {fname}:")
    process(fname, replacements)
    print()

print("Done. Verify in browser, then delete .bak files.")
