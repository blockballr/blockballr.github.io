"""Draw the desktop wallpaper: the mark as an embossed field, the name as a solid.

    python brand/build-wallpaper.py

Two things on a beige ground. The mark repeats across the whole canvas as a
tone-on-tone emboss, and the handle sits in the middle of it as an extruded
isometric solid.

The emboss is not a filter. It is three copies of the same stroked outline: the
highlight offset up and left, the shadow offset down and right, and the ground
colour laid over the middle so the two only survive as slivers along either edge.
That is what an embossed line actually is, and doing it as geometry rather than as
feDiffuseLighting keeps it crisp at any size and keeps it predictable, which a
lighting filter on a near-flat colour is not.

The word is projected onto the isometric ground plane and extruded straight up.
Both of those are the mark's own argument at another size: a block is a solid
thing that sits on a surface and casts a shadow, so the name is drawn as one.

The 30 degree rise is not a style choice either. A 16 by 9 rectangle has a
diagonal of 29.36 degrees and true isometric is 30, so a word laid along one
isometric axis runs corner to corner on a widescreen canvas almost exactly. The
composition falls out of the format rather than being fitted to it.

The extrusion is a stack of <use> references rather than a stack of copied paths,
one per device pixel of depth. A real extrusion would need the silhouette of the
outline swept along the depth vector, which is tractable for a polygon and not for
a font full of curves; stepping the whole shape gets the identical result, because
the union of every step is exactly the swept volume.

Rendered at twice the target size and resampled down, because the walls of the
extrusion are a stack of hairlines and the emboss is a pair of them, and neither
survives being rasterised once at final size.
"""
import math
import pathlib
import subprocess
import time

from PIL import Image

from geometry import (ASPHALT, BOX, NORMAL, SIGNAL, SIGNAL_DEEP, block_path,
                      centre, contrast, tile_path)
from shaping import outline

HERE = pathlib.Path(__file__).parent
CHIVO = HERE / "fonts" / "Chivo-Variable.woff2"
OUT = HERE / "wallpaper"

CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# Layout is written in 1920x1080 and rendered at SCALE, so every number below is
# read against the screen it is actually for.
W, H = 1920, 1080
SCALE = 2

# Beige, warm and mid. Light enough that asphalt reads on it, dark enough that an
# emboss has somewhere to go: a highlight needs headroom above the ground colour
# and a shadow needs room below it, and near-white has neither.
BEIGE = "#DBD0BB"
UMBER = "#4A3B26"                  # the warm dark every shadow is mixed toward

CELL = 112.0                       # pattern pitch
MARK = 62.0                        # the mark inside it
STROKE = 2.0
RELIEF = 1.2                       # how far the highlight and shadow are thrown

WORD = "blockballr"
# Open, where the wordmark is tight. The projection slides every letter up and to
# the right of the one before it, so at the wordmark's negative tracking the
# letters climb into each other's walls and the middle of the word closes up into
# one solid. Tracking here is spacing the projection needs, not a second opinion
# about how the name is set.
TRACKING = 0.055
MAX_W = 0.72 * W                   # of the projected word, before extrusion
MAX_H = 0.62 * H
DEPTH = 0.55                       # extrusion, as a fraction of the ascender
STEP = 1.0 / SCALE                 # one device pixel, so the walls have no banding

ISO = math.radians(30)


def mix(a, b, t):
    """Blend two hex colours, t of the way from a to b."""
    pair = [(int(a[i:i + 2], 16), int(b[i:i + 2], 16)) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in pair)


HIGHLIGHT = mix(BEIGE, "#FFFFFF", 0.70)
SHADOW = mix(BEIGE, UMBER, 0.26)


def project(u, v):
    """A point on the isometric ground plane, in screen coordinates.

    The word's own left-to-right axis rises to the right and its top-to-bottom
    axis falls to the right, which is the ground plane seen from the standard
    isometric eye. Depth is then a straight vertical on screen, which is the
    property that makes the extrusion a stack of vertical offsets and nothing
    more.
    """
    cos, sin = math.cos(ISO), math.sin(ISO)
    return u * cos + v * cos, -u * sin + v * sin


def pattern():
    """The mark, repeated, as an embossed outline.

    Half-dropped every other row. A straight grid of a shape this angular reads as
    a grid first and a mark second, and the mark is the point.

    The field is generated a cell beyond every edge so it bleeds off rather than
    stopping short, which is asserted below rather than eyeballed.
    """
    k = MARK / BOX
    cx, cy = centre(NORMAL)
    cols = int(W / CELL) + 3
    rows = int(H / CELL) + 3

    origins = []
    for row in range(rows):
        drop = (CELL / 2) if row % 2 else 0.0
        for col in range(cols):
            origins.append((-CELL + col * CELL + drop, -CELL + row * CELL))

    xs = [x for x, _ in origins]
    ys = [y for _, y in origins]
    assert min(xs) <= -MARK / 2 and max(xs) + MARK >= W + MARK / 2, "field is short"
    assert min(ys) <= -MARK / 2 and max(ys) + MARK >= H + MARK / 2, "field is short"

    # One stroke width, expressed in the mark's own units, because the group it
    # sits on is scaled and stroke-width scales with it.
    sw = STROKE / k
    passes = [(SHADOW, RELIEF), (HIGHLIGHT, -RELIEF), (BEIGE, 0.0)]

    out = []
    for colour, off in passes:
        uses = "".join(f'<use href="#mark" x="{x + off:.2f}" y="{y + off:.2f}"/>'
                       for x, y in origins)
        out.append(f'<g fill="none" stroke="{colour}" stroke-width="{sw:.3f}" '
                   f'stroke-linejoin="miter">{uses}</g>')
    return "\n  ".join(out), k, cx, cy


def word(face, wall):
    """The handle, projected onto the ground plane and extruded straight up.

    Sized against the projection rather than against the flat text, because the
    projection is what the canvas has to hold: a word laid on this plane is wider
    and shorter than the word it came from, and fitting the flat one would leave
    the real thing overhanging.
    """
    path, (x0, y0, x1, y1) = outline(WORD, CHIVO, 800, TRACKING)

    corners = [project(u, v) for u in (x0, x1) for v in (y0, y1)]
    px0 = min(x for x, _ in corners)
    px1 = max(x for x, _ in corners)
    py0 = min(y for _, y in corners)
    py1 = max(y for _, y in corners)
    pw, ph = px1 - px0, py1 - py0

    # -y0 is the ascender, which is what the depth is read against: the extrusion
    # has to look like the height of the letters, not like a fixed number of pixels.
    s = min(MAX_W / pw, MAX_H / (ph + DEPTH * -y0))
    depth = DEPTH * -y0 * s

    ox = (W - pw * s) / 2 - px0 * s
    oy = (H - (ph * s + depth)) / 2 - (py0 * s - depth)

    assert ox + px0 * s > 0 and ox + px1 * s < W, "the word runs off the sides"
    assert oy + py0 * s - depth > 0 and oy + py1 * s < H, "the word runs off the top"

    cos, sin = math.cos(ISO), math.sin(ISO)
    iso = f"matrix({cos:.6f},{-sin:.6f},{cos:.6f},{sin:.6f},0,0)"

    steps = int(depth / STEP)
    stack = "".join(f'<use href="#word" y="{-i * STEP:.3f}"/>'
                    for i in range(steps + 1))

    # The contact shadow starts at the foot of the extrusion, not under the top
    # face, because the foot is the part that is actually touching the ground.
    lift = f"{-depth:.3f}"
    return (
        f'<defs><path id="word" transform="{iso} scale({s:.6f})" d="{path}"/></defs>\n'
        f'  <g transform="translate({ox:.2f} {oy:.2f})">\n'
        f'    <use href="#word" x="16" y="11" fill="{UMBER}" opacity="0.22" '
        f'filter="url(#soft)"/>\n'
        f'    <g fill="{wall}">{stack}</g>\n'
        f'    <use href="#word" y="{lift}" fill="{face}"/>\n'
        f'  </g>'), s, depth, steps


def render(svg, out):
    td = HERE / ".render"
    td.mkdir(exist_ok=True)
    page, shot = td / "wallpaper.html", td / "wallpaper.png"
    if shot.exists():
        shot.unlink()
    page.write_text('<!doctype html><meta charset="utf-8">'
                    '<style>html,body{margin:0;padding:0;overflow:hidden}'
                    'svg{display:block}</style>' + svg, encoding="utf-8")
    # Chrome exits 0 whether or not it wrote a file, so the exit code is worth
    # nothing and the only honest check is to go and look.
    for attempt in range(6):
        subprocess.run(
            [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", f"--force-device-scale-factor={SCALE}",
             f"--screenshot={shot}", f"--window-size={W},{H}", page.as_uri()],
            timeout=180)
        for _ in range(30):
            if shot.exists() and shot.stat().st_size > 0:
                break
            time.sleep(0.2)
        if shot.exists() and shot.stat().st_size > 0:
            break
        print(f"    chrome missed the wallpaper, retry {attempt + 1}")
    else:
        raise SystemExit("chrome would not render the wallpaper after 6 tries")

    im = Image.open(shot).convert("RGB")
    assert im.size == (W * SCALE, H * SCALE), f"rendered {im.size}"
    im.save(out, optimize=True)
    return im


def build(name, face, wall):
    field, k, cx, cy = pattern()
    solid, s, depth, steps = word(face, wall)

    body = "\n  ".join([
        '<defs>'
        f'<radialGradient id="lift" cx="0.34" cy="0.20" r="0.92">'
        f'<stop offset="0" stop-color="{mix(BEIGE, "#FFFFFF", 0.13)}"/>'
        f'<stop offset="1" stop-color="{mix(BEIGE, UMBER, 0.11)}"/>'
        f'</radialGradient>'
        f'<filter id="soft" x="-25%" y="-25%" width="150%" height="150%">'
        f'<feGaussianBlur stdDeviation="13"/></filter>'
        f'<g id="mark" transform="scale({k:.6f}) translate({cx:.4f} {cy:.4f})">'
        f'<path d="{block_path(NORMAL)}"/><path d="{tile_path(NORMAL)}"/>'
        f'</g></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#lift)"/>',
        field,
        solid,
    ])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n  {body}\n</svg>')

    OUT.mkdir(parents=True, exist_ok=True)
    master = OUT / f"blockballr-{name}-{W * SCALE}x{H * SCALE}.png"
    im = render(svg, master)
    screen = OUT / f"blockballr-{name}-{W}x{H}.png"
    im.resize((W, H), Image.LANCZOS).save(screen, optimize=True)

    print(f"  {name:>6}  face {face} on wall {wall}  "
          f"contrast on beige {contrast(face, BEIGE):.1f}")
    print(f"          word {s * 1000:.1f}/1000 scale, {depth:.0f}px deep, "
          f"{steps} steps")
    for p in (master, screen):
        print(f"          {p.name}  {p.stat().st_size / 1024:.0f} KB")
    return master, screen


VARIANTS = [
    ("ember", ASPHALT, SIGNAL),
    ("burnt", ASPHALT, SIGNAL_DEEP),
    ("mono", ASPHALT, mix(BEIGE, UMBER, 0.62)),
]

if __name__ == "__main__":
    print(f"beige {BEIGE}, highlight {HIGHLIGHT}, shadow {SHADOW}")
    for name, face, wall in VARIANTS:
        build(name, face, wall)
    print("wallpaper written to", OUT)
