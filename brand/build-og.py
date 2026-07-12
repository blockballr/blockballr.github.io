"""Draw the social card.

    python brand/build-og.py

This is the image that renders when someone pastes the site into Telegram, X, or
Discord, which for a community whose entire distribution is people sharing a link
is the first thing anybody sees of the brand. It gets built from the same geometry
as everything else rather than being an avatar stretched to fit.

It is a PNG on purpose. Every scraper worth having reads PNG and none of them read
SVG, so the drawing is done in SVG and rasterised through Chrome, the same way the
icon set is.

Two rules the card has to obey, and they are the reason it is not just the lockup
centred on a square:

  X crops a 1200x630 card to 2:1, taking 15px off the top and bottom, so nothing
  that matters may sit within about 40px of either edge.

  A link preview is shown small, in a list, next to other link previews. So the
  card carries the lockup and the line and nothing else. A card with a paragraph
  on it is a card nobody reads.
"""
import math
import pathlib
import re
import subprocess
import time

from PIL import Image

from geometry import CHALK, NIGHT, SIGNAL_LIFT, SLATE_LIFT
from shaping import outline

HERE = pathlib.Path(__file__).parent
LOGO = HERE / "logo" / "offtheblock-lockup-horizontal-knockout.svg"
INTER = HERE / "fonts" / "Inter-Variable.woff2"
OUT = HERE.parent / "img"

CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

W, H = 1200, 630
MARGIN = 88
SAFE = 40                      # X's 2:1 crop takes 15px; this is that with room to spare

TAGLINE = "Before it hits the block."
TAG_PX = 38

DIM = "#1e222a"
DIMMER = "#171a21"


def lockup(x, y, width):
    """Nest the generated lockup, so the card cannot drift from the real one.

    The lockup is already outlined, so this needs no font and no re-shaping. It is
    read rather than rebuilt because a second copy of the lockup's layout constants
    is a second copy that goes stale.
    """
    svg = LOGO.read_text(encoding="utf-8")
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    lw, lh = float(vb.group(1)), float(vb.group(2))
    inner = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    height = width * (lh / lw)
    return (f'<svg x="{x}" y="{y:.1f}" width="{width}" height="{height:.1f}" '
            f'viewBox="0 0 {lw} {lh}">{inner}</svg>'), height


def tile(cx, cy, size, deg, fill, opacity=1.0):
    h, r = size / 2, math.radians(deg)
    cos, sin = math.cos(r), math.sin(r)
    pts = [(cx + dx * cos - dy * sin, cy + dx * sin + dy * cos)
           for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]
    d = "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts) + " Z"
    o = f' opacity="{opacity:g}"' if opacity < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}/>'


def field():
    """A field of blocks at rest, with one gone. The card says the name twice.

    It sits behind and to the right of the type, and it is dim on purpose: at the
    size a link preview is actually shown, anything busier than this turns to noise
    and the lockup stops being the thing you see. It fades toward the type so the
    two never fight.

    The cell the loose piece came out of is drawn as an outline rather than as a
    darker square. On a near-black ground a darker square is not a hole, it is just
    another block, and the absence is the whole point.
    """
    parts = []
    cols, rows, cell, size = 5, 5, 88, 58
    x0, y0 = 722, 104
    gone = (2, 2)                                  # the one that left, mid-field

    assert x0 + (cols - 1) * cell + size <= W - SAFE, "field runs into the crop"
    assert y0 + (rows - 1) * cell + size <= H - SAFE, "field runs into the crop"

    for row in range(rows):
        for col in range(cols):
            if (col, row) == gone:
                continue
            x, y = x0 + col * cell, y0 + row * cell
            # brighten to the right, away from the type
            op = 0.20 + 0.42 * (col / (cols - 1))
            parts.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" '
                         f'rx="2" fill="{DIM if op > 0.4 else DIMMER}" '
                         f'opacity="{op:.2f}"/>')

    gx, gy = x0 + gone[0] * cell, y0 + gone[1] * cell
    parts.append(f'<rect x="{gx + 0.75}" y="{gy + 0.75}" width="{size - 1.5}" '
                 f'height="{size - 1.5}" rx="2" fill="none" stroke="{SIGNAL_LIFT}" '
                 f'stroke-width="1.5" opacity="0.34"/>')
    # the piece that left: off the block, up and to the right, tilted, hot
    parts.append(tile(gx + size / 2 + 66, gy + size / 2 - 62, 50, 14, SIGNAL_LIFT))
    return "\n  ".join(parts)


def text(txt, x, baseline, px, fill, src=INTER, weight=600, tracking=-0.006):
    path, (x0, y0, _, _) = outline(txt, src, weight, tracking)
    s = px / -y0 * 0.72          # -y0 is the ascent; 0.72 lands px on the cap height
    return (f'<g transform="translate({x - x0 * s:.2f} {baseline:.2f}) '
            f'scale({s:.6f})"><path fill="{fill}" d="{path}"/></g>')


def render(svg, out):
    td = HERE / ".render"
    td.mkdir(exist_ok=True)
    page, shot = td / "og.html", td / "og.png"
    if shot.exists():
        shot.unlink()
    page.write_text('<!doctype html><meta charset="utf-8">'
                    '<style>html,body{margin:0;padding:0;overflow:hidden}'
                    'svg{display:block}</style>' + svg, encoding="utf-8")
    # Headless Chrome exits 0 whether or not it wrote anything, so the exit code is
    # worth nothing and the only honest check is to go and look for the file.
    for attempt in range(6):
        subprocess.run(
            [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", "--force-device-scale-factor=1",
             f"--screenshot={shot}", f"--window-size={W},{H}", page.as_uri()],
            timeout=90)
        for _ in range(20):
            if shot.exists() and shot.stat().st_size > 0:
                break
            time.sleep(0.15)
        if shot.exists() and shot.stat().st_size > 0:
            break
        print(f"    chrome missed the card, retry {attempt + 1}")
    else:
        raise SystemExit("chrome would not render the social card after 6 tries")
    Image.open(shot).convert("RGB").crop((0, 0, W, H)).save(out, optimize=True)


LOCKUP_Y = 214
mark_svg, mark_h = lockup(MARGIN, LOCKUP_Y, 520)
body = "\n  ".join([
    f'<rect width="{W}" height="{H}" fill="{NIGHT}"/>',
    field(),
    mark_svg,
    text(TAGLINE, MARGIN, LOCKUP_Y + mark_h + 74, TAG_PX, CHALK),
    text("blockballr.github.io", MARGIN, H - 66, 22, SLATE_LIFT,
         weight=500),
    f'<rect x="{MARGIN}" y="{H - 44}" width="64" height="4" fill="{SIGNAL_LIFT}"/>',
])
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}">\n  {body}\n</svg>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "og.svg").write_text(
    "<!-- Drawn from brand/build-og.py. Do not hand-edit. -->\n" + svg + "\n",
    encoding="utf-8")
render(svg, OUT / "og.png")

png = OUT / "og.png"
im = Image.open(png)
assert im.size == (W, H), f"card is {im.size}, must be {(W, H)}"
kb = png.stat().st_size / 1024
# Telegram gives up on an og:image over about 5MB and every scraper is slower for
# a heavy one, so this is checked rather than hoped for.
assert kb < 1024, f"card is {kb:.0f} KB, too heavy for a link preview"
print(f"  og.png  {im.size[0]}x{im.size[1]}, {kb:.0f} KB")
print(f"  og.svg")
print("social card written to", OUT)
