#!/usr/bin/env python3
import re, shutil, os

NAVS = {
    "part1/index.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../" class="nav-home">&#8592; XRP Series</a></div>
    <span class="nav-label">Part 1 of 6</span>
    <div><a href="../part2/" class="nav-arrow">Part 2 &#8594;</a></div>
  </div>
</nav>""",
    "part2/index.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part1/" class="nav-arrow">&#8592; Part 1</a></div>
    <span class="nav-label">Part 2 of 6</span>
    <div><a href="../part3/" class="nav-arrow">Part 3 &#8594;</a></div>
  </div>
</nav>""",
    "part3/index.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part2/" class="nav-arrow">&#8592; Part 2</a></div>
    <span class="nav-label">Part 3 of 6</span>
    <div><a href="../part4/" class="nav-arrow">Part 4 &#8594;</a></div>
  </div>
</nav>""",
    "part4/index.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part3/" class="nav-arrow">&#8592; Part 3</a></div>
    <span class="nav-label">Part 4 of 6</span>
    <div><a href="../part5/" class="nav-arrow">Part 5 &#8594;</a></div>
  </div>
</nav>""",
    "part5/index.html": """<nav class="series-nav" aria-label="XRP Valuation Series navigation">
  <div class="series-nav-inner">
    <div><a href="../part4/" class="nav-arrow">&#8592; Part 4</a></div>
    <span class="nav-label">Part 5 of 6</span>
    <div><a href="../part6/" class="nav-arrow">Part 6 &#8594;</a></div>
  </div>
</nav>""",
}

def fix_css(html):
    style_start = html.find('<style>')
    style_end = html.find('</style>')
    if style_start == -1 or style_end == -1:
        return html
    before = html[:style_start]
    style = html[style_start:style_end + 8]
    after = html[style_end + 8:]
    style = style.replace('{{', '{').replace('}}', '}')
    style = re.sub(r'\s*\.series-nav \.nav-sep\s*\{[^}]*\}', '', style)
    return before + style + after

def fix_nav(html, filename):
    new_nav = NAVS.get(filename)
    if not new_nav:
        return html
    pattern = re.compile(r'<!--\s*XRP Series Navigation\s*-->\s*<nav class="series-nav".*?</nav>', re.DOTALL)
    match = pattern.search(html)
    if match:
        return html[:match.start()] + new_nav + html[match.end():]
    pattern2 = re.compile(r'<nav class="series-nav".*?</nav>', re.DOTALL)
    match2 = pattern2.search(html)
    if match2:
        return html[:match2.start()] + new_nav + html[match2.end():]
    print(f"  WARNING: Could not find nav block in {filename}")
    return html

def process(filename):
    if not os.path.exists(filename):
        print(f"  SKIP: {filename} not found")
        return
    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()
    shutil.copy2(filename, filename + '.bak')
    html = fix_css(html)
    html = fix_nav(html, filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  OK: {filename}")

print("Fixing XRP Valuation Series navigation (Parts 1-5)...")
for fname in ["part1/index.html","part2/index.html","part3/index.html","part4/index.html","part5/index.html"]:
    process(fname)
print("Done.")
