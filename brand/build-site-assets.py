"""Assemble the site's assets and print the mark's exact inline SVG.

    python brand/build-site-assets.py

The site inlines the mark rather than linking it, because the mark has to inherit
the page's theme colours: an <img> is an isolated document and cannot see
var(--text). Inlining means the two shapes are pasted into index.html, and a pasted
path is a path that silently drifts from geometry.py the moment anything changes.

So it is printed from geometry.py here rather than typed by hand, and the check at
the bottom fails loudly if what is in index.html no longer matches.
"""
import pathlib
import re
import shutil

from geometry import NORMAL, block_path, ink, shapes, tile_path

HERE = pathlib.Path(__file__).parent
SITE = HERE.parent                  # the site is the repository root: GitHub Pages
IMG = SITE / "img"                  # serves index.html from there and nowhere else
FONTS = SITE / "fonts"

X0, Y0, W, H = ink(NORMAL)

MARK = (
    f'<svg viewBox="0 0 {W:.2f} {H:.2f}" aria-hidden="true">\n'
    f'      <g transform="translate({-X0:.4f} {-Y0:.4f})">\n'
    f'        <path d="{block_path(NORMAL)}" fill="var(--text)"/>\n'
    f'        <path d="{tile_path(NORMAL)}" fill="var(--tile)"/>\n'
    f'      </g>\n'
    f'    </svg>'
)

# The hero uses the same two shapes at a larger size, so it is the same snippet.
print("--- inline mark for index.html ---")
print(MARK)
print()

# Fonts and icons the page actually asks for.
FONTS.mkdir(parents=True, exist_ok=True)
IMG.mkdir(parents=True, exist_ok=True)
for f in ("Chivo-Variable.woff2", "Inter-Variable.woff2", "JetBrainsMono-Variable.woff2"):
    shutil.copy2(HERE / "fonts" / f, FONTS / f)
    print(f"  fonts/{f}")
for f in ("OFL-Chivo.txt", "OFL-Inter.txt", "OFL-JetBrainsMono.txt"):
    shutil.copy2(HERE / "fonts" / f, FONTS / f)

shutil.copy2(HERE / "icon" / "favicon.ico", IMG / "favicon.ico")
shutil.copy2(HERE / "icon" / "png" / "apple-touch-icon.png", IMG / "apple-touch-icon.png")
shutil.copy2(SITE / "assets" / "offtheblock-avatar.png", IMG / "offtheblock-avatar.png")
print("  img/favicon.ico, apple-touch-icon.png, offtheblock-avatar.png")

# The paths in index.html must be the paths geometry.py draws. If someone tweaks the
# mark and forgets the page, this is the line that says so.
page = (SITE / "index.html").read_text(encoding="utf-8")
missing = [name for name, d in (("block", block_path(NORMAL)), ("tile", tile_path(NORMAL)))
           if d not in page]
if missing:
    raise SystemExit(
        f"\nindex.html's inline mark is stale: {', '.join(missing)} path does not match "
        f"geometry.py.\nPaste the snippet above over the <svg> in the .logo anchor.")
print("\nindex.html's inline mark matches geometry.py")
