"""Rebuild the OffTheBlock wordmark and lockups as outlines.

    python -m pip install "fonttools[woff]" brotli uharfbuzz
    python brand/build-wordmark.py

Instances Chivo at weight 800, shapes the name with HarfBuzz so the kerning is the
font's own rather than something approximated, bakes in the brand's tracking, and
writes the wordmark and both lockups as pure paths. The output depends on no font
being installed anywhere.

The name is set as one word with its internal capitals kept: OffTheBlock, not
"Off The Block" and not "offtheblock". It is a handle before it is a title. The
three capitals give the word its rhythm and they are the only structure it needs,
which is why the wordmark takes no space between the parts.

The mark is drawn from geometry.py, the same numbers build-marks.py uses.
"""
import pathlib

from geometry import (ASPHALT, CHALK, NORMAL, SIGNAL, SIGNAL_LIFT, balance,
                      extent, ink, shapes)
from shaping import outline

HERE = pathlib.Path(__file__).parent
SRC = HERE / "fonts" / "Chivo-Variable.woff2"
OUT = HERE / "logo"

TEXT = "OffTheBlock"
WEIGHT = 800
TRACKING_EM = -0.022

# The name is eleven letters, which is long. Negative tracking is not a flourish
# here: at default spacing the word sprawls, and beside a mark this compact it
# reads as a caption rather than a name.

MX, MY, MW, MH = ink(NORMAL)
BLOCK_W, TILE_W, _, _ = NORMAL
BLOCK_RIGHT = BLOCK_W / MW                        # where the block's edge ends, across the ink
TILE_BOTTOM = (2 * extent(NORMAL)) / MH           # where the tile's underside ends, down the ink
BAL_X, _ = balance(NORMAL)                        # where the mark actually balances


PATH, (XMIN, YMIN, XMAX, YMAX) = outline(TEXT, SRC, WEIGHT, TRACKING_EM, verbose=True)
BW, ASC, BH = XMAX - XMIN, -YMIN, (-YMIN) + YMAX

NOTE = ("<!-- Wordmark outlined from Chivo at weight 800 with the brand's -0.022em\n"
        "     tracking baked in. No font is required to render this file.\n"
        "     Regenerate with: python brand/build-wordmark.py -->\n")


def word(x, baseline, s, fill):
    return (f'<g transform="translate({x - XMIN * s:.3f} {baseline:.3f}) scale({s:.6f})">'
            f'<path fill="{fill}" d="{PATH}"/></g>')


def mark(x, y, height, block, signal):
    """Place the mark so its ink sits at (x, y) and is `height` tall."""
    s = height / MH
    paint = {"block": block, "signal": signal}
    paths = "".join(f'<path d="{d}" fill="{paint[role]}"/>' for d, role in shapes(NORMAL))
    return (f'<g transform="translate({x - MX * s:.3f} {y - MY * s:.3f}) '
            f'scale({s:.6f})">{paths}</g>')


def write(name, *parts, w, h, label="OffTheBlock"):
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" role="img" aria-label="{label}">\n'
            f'  <title>{label}</title>')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(NOTE + head + "\n  " + "\n  ".join(parts) + "\n</svg>\n",
                            encoding="utf-8")
    print(f"  {name}")


write("offtheblock-wordmark.svg", word(0, ASC, 1.0, ASPHALT), w=BW, h=BH)
write("offtheblock-wordmark-knockout.svg", word(0, ASC, 1.0, CHALK), w=BW, h=BH)

# Horizontal. The block's foot sits on the word's baseline, so the mark stands on
# the same line the type does rather than floating beside it.
#
# The gap is measured from the block's right edge, not from the mark's bounding
# box. The bounding box is defined by the tile, which is up in the corner with
# nothing under it, so spacing the word off the box opens a hole beneath the tile
# and the lockup falls into two pieces. Measured off the block instead, the word
# closes up and runs under the tile, and the tile's diagonal now points into the
# name. The one thing this must not do is let the tile touch the caps: CLEARANCE
# below is that daylight, and it is asserted rather than eyeballed.
MARK_H, CAP_PX, GAP = 90.0, 44.0, 20.0
s = CAP_PX / ASC
CLEARANCE = (MARK_H - CAP_PX) - TILE_BOTTOM * MARK_H
assert CLEARANCE > 0.12 * MARK_H, f"tile crowds the caps: {CLEARANCE:.1f}px"
print(f"  horizontal: tile clears the caps by {CLEARANCE:.1f}px "
      f"({CLEARANCE / MARK_H:.0%} of the mark)")

wx = BLOCK_RIGHT * MARK_H + GAP
for name, block, signal in (("offtheblock-lockup-horizontal.svg", ASPHALT, SIGNAL),
                            ("offtheblock-lockup-horizontal-knockout.svg", CHALK, SIGNAL_LIFT)):
    write(name,
          mark(0, 0, MARK_H, block, signal),
          word(wx, MARK_H, s, block),
          w=wx + BW * s, h=MARK_H + (BH - ASC) * s)

# Stacked. The word is centred under the point the mark balances on, not under the
# middle of its bounding box: the mark's weight is almost all block, thrown into
# one corner, and centring on the box would hang the word off empty space.
MARK_H2, VGAP, CAP2 = 76.0, 20.0, 34.0
s2 = CAP2 / ASC
mark_w2, word_w2 = MARK_H2 * (MW / MH), BW * s2
axis = max(BAL_X * mark_w2, word_w2 / 2)          # the shared centre line
W2 = max(axis + (mark_w2 - BAL_X * mark_w2), axis + word_w2 / 2)
for name, block, signal in (("offtheblock-lockup-stacked.svg", ASPHALT, SIGNAL),
                            ("offtheblock-lockup-stacked-knockout.svg", CHALK, SIGNAL_LIFT)):
    write(name,
          mark(axis - BAL_X * mark_w2, 0, MARK_H2, block, signal),
          word(axis - word_w2 / 2, MARK_H2 + VGAP + ASC * s2, s2, block),
          w=W2, h=MARK_H2 + VGAP + BH * s2)

print("wordmark and lockups written to", OUT)
