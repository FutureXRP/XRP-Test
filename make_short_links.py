#!/usr/bin/env python3
"""
XRP Valuation Series — Short-link generator
===========================================
Run this script from the root of the repository after adding a field note
(blog/posts.json) or an Observatory piece (OBSERVATORY list below).

It creates one tiny redirect page per article so that short, typeable
addresses work alongside the descriptive ones:

    xrpvaluation.info/blog1          ->  /blog/jit-sourcing/
    xrpvaluation.info/blog18         ->  /blog/coordination-premium/
    xrpvaluation.info/observatory3   ->  /observatory/plumbing-paper/

The descriptive URL stays canonical (so existing links and search results
keep working); the short URL is an alias that forwards instantly.

Usage:
    python3 make_short_links.py

The script is idempotent — re-running it only rewrites the alias pages.
"""

import html
import json
import os
import re

SITE = "https://xrpvaluation.info"

# Observatory pieces, in order of publication number.
OBSERVATORY = [
    (1, "velocity-problem",     "The Velocity Problem"),
    (2, "tokenization-ceiling", "The Success That Could Become the Ceiling"),
    (3, "plumbing-paper",       "The Plumbing Paper"),
    (4, "thick-market-effect",  "The Thick-Market Effect Has a Formula"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — XRP Valuation Series</title>
  <meta name="description" content="Short link for {label}. Redirecting…" />
  <meta name="robots" content="noindex" />
  <meta http-equiv="refresh" content="0; url={path}" />
  <link rel="canonical" href="{site}{path}" />
  <style>
    body {{ background: #fbfaf7; color: #171512; font-family: Georgia, serif; display: grid; place-items: center; min-height: 100vh; margin: 0; padding: 0 24px; text-align: center; }}
    a {{ color: #9b2226; }}
  </style>
</head>
<body>
  <p>{label} &mdash; <a href="{path}">continue to the article &rarr;</a></p>
</body>
</html>
"""


def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def write_alias(alias_dir, path, title, label):
    os.makedirs(alias_dir, exist_ok=True)
    page = TEMPLATE.format(
        title=html.escape(title),
        label=html.escape(label),
        path=path,
        site=SITE,
    )
    target = os.path.join(alias_dir, "index.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  /{alias_dir}/  ->  {path}")


def main():
    with open("blog/posts.json", encoding="utf-8") as f:
        posts = json.load(f)

    print("Field notes:")
    for post in posts:
        number = post["number"]
        slug = post["slug"]
        title = strip_tags(post["title"])
        write_alias(f"blog{number}", f"/blog/{slug}/", title, f"Field Note No. {number}")

    print("Observatory:")
    for number, slug, title in OBSERVATORY:
        if not os.path.exists(os.path.join("observatory", slug, "index.html")):
            print(f"  SKIP: observatory/{slug}/index.html not found")
            continue
        write_alias(f"observatory{number}", f"/observatory/{slug}/", title, f"Observatory No. {number}")

    print("Done.")


if __name__ == "__main__":
    main()
