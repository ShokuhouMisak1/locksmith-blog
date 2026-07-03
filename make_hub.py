#!/usr/bin/env python3
"""Generate hub.html (the ARA-Hub srcDoc embed) from index.html.

The hub fetches one self-contained HTML file into an <iframe srcdoc>, so:
  1. every assets/*.png <img> is inlined as a base64 data URI;
  2. assets/frames.js is inlined as a <script> block;
  3. the two in-repo links (trajectory.html, l7_showcase.html) are rewritten
     to absolute raw.githack URLs (relative links don't resolve in srcdoc).

Usage: python3 make_hub.py   (run from the repo root; writes hub.html)
"""
import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
RAW = "https://raw.githack.com/ShokuhouMisak1/locksmith-blog/main/"

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    def inline_img(m):
        rel = m.group(1)
        data = base64.b64encode((ROOT / rel).read_bytes()).decode()
        return 'src="data:image/png;base64,' + data + '"'

    html, n_img = re.subn(r'src="(assets/[^"]+\.png)"', inline_img, html)

    js = (ROOT / "assets/frames.js").read_text(encoding="utf-8")
    html, n_js = re.subn(
        r'<script src="assets/frames\.js"></script>',
        lambda m: "<script>\n" + js + "\n</script>",
        html,
    )

    n_link = 0
    for rel in ("trajectory.html", "l7_showcase.html"):
        html, n = re.subn(f'href="{rel}"', f'href="{RAW}{rel}"', html)
        n_link += n

    leftovers = re.findall(r'(?:src|href)="assets/[^"]*"', html)
    if leftovers:
        sys.exit(f"unresolved asset refs: {leftovers}")

    # completeness guard: a truncated index.html once shipped with the whole
    # tail (§6–§8, footnotes, scripts) missing — refuse to build one again.
    if n_js != 1 or n_link < 2:
        sys.exit(f"index.html looks truncated: {n_js} scripts / {n_link} links processed")
    for marker in ("</html>", 'id="fn4"', "GAME COMPLETE"):
        if marker not in html:
            sys.exit(f"index.html looks truncated: missing {marker!r}")

    (ROOT / "hub.html").write_text(html, encoding="utf-8")
    print(f"hub.html written: {n_img} images inlined, {n_js} script inlined, {n_link} links absolutized")

if __name__ == "__main__":
    main()
