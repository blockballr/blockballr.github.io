"""Draw the project art banners.

    python brand/build-art.py

A project with nothing deployed has nothing to screenshot, so it gets a drawing
instead of a preview. The drawings are not decoration and they are not stock: each
one is the mark's own vocabulary, a field of blocks with one piece off the block,
bent to say what that particular project does. Radar sweeps a field and lights the
one that matters. The bot watches a stream of messages and pulls one out.

That constraint is the point. A card that says "no screenshot yet" is a hole in a
page. A card drawn in the logo's own geometry is a card, and the site reads as one
thing rather than a live project and two apologies.
"""
import math
import pathlib

from geometry import CHALK, NIGHT, SIGNAL_LIFT, SLATE, extent

OUT = pathlib.Path(__file__).parent.parent / "img"

W, H = 1280, 800
DIM = "#1e222a"          # a block at rest: present, but not speaking
DIMMER = "#171a21"
LINE = "#2a2f38"

NOTE = ("<!-- Drawn from brand/build-art.py in the mark's own geometry.\n"
        "     Do not hand-edit. -->\n")


def tile(cx, cy, size, deg, fill, opacity=1.0):
    """A tilted square, centred on (cx, cy). The one shape the brand owns."""
    h, r = size / 2, math.radians(deg)
    cos, sin = math.cos(r), math.sin(r)
    pts = [(cx + dx * cos - dy * sin, cy + dx * sin + dy * cos)
           for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"
    o = f' opacity="{opacity:g}"' if opacity < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}/>'


def square(x, y, size, fill, opacity=1.0):
    o = f' opacity="{opacity:g}"' if opacity < 1 else ""
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" fill="{fill}"{o}/>'


def write(name, body, label):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        f'{NOTE}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{label}">\n'
        f'  <title>{label}</title>\n'
        f'  <rect width="{W}" height="{H}" fill="{NIGHT}"/>\n  {body}\n</svg>\n',
        encoding="utf-8")
    print(f"  {name}")


# ---------------------------------------------------------------- Radar
# A screener sweeps a field of things that all look alike and lights the one that
# does not. So: a grid at rest, a sweep passing over it, and a single tile that has
# come off the grid and gone hot. The empty cell it left is still there.
def radar():
    parts = []
    ox, oy = 150, 660          # the sweep's origin, bottom-left
    for r in (240, 400, 560, 720, 880):
        parts.append(f'<circle cx="{ox}" cy="{oy}" r="{r}" fill="none" '
                     f'stroke="{LINE}" stroke-width="1.5" opacity="0.55"/>')

    # The sweep. It is a thin leading edge with a short fade behind it, not a filled
    # wedge: a wedge at any opacity that is visible at all reads as a flat maroon
    # triangle laid over the art, which is the one thing this must not look like.
    parts.append(
        f'<defs><linearGradient id="sweep" x1="0.15" y1="1" x2="0.95" y2="0.1">'
        f'<stop offset="0.55" stop-color="{SIGNAL_LIFT}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{SIGNAL_LIFT}" stop-opacity="0.09"/>'
        f'</linearGradient></defs>'
        f'<path d="M{ox},{oy} L{ox + 905},{oy - 300} A955,955 0 0,0 {ox + 700},{oy - 650} Z" '
        f'fill="url(#sweep)"/>'
        f'<line x1="{ox}" y1="{oy}" x2="{ox + 700}" y2="{oy - 650}" '
        f'stroke="{SIGNAL_LIFT}" stroke-width="2" opacity="0.5"/>')

    cell, size = 96, 40
    hot = (7, 2)                                   # the one that is not like the others
    for row in range(6):
        for col in range(11):
            x, y = 180 + col * cell, 150 + row * cell
            if (col, row) == hot:
                continue                            # its cell is empty: it left
            d = math.hypot(x - ox, y - oy)
            # blocks the sweep has just passed sit brighter, and fade behind it
            op = 0.42 + 0.5 * max(0.0, 1 - abs(d - 600) / 420)
            parts.append(square(x, y, size, DIM if op > 0.6 else DIMMER, op))

    hx, hy = 180 + hot[0] * cell, 150 + hot[1] * cell
    parts.append(square(hx, hy, size, "#000", 0.5))          # the void it came out of
    parts.append(f'<circle cx="{hx + size / 2}" cy="{hy + size / 2}" r="86" fill="none" '
                 f'stroke="{SIGNAL_LIFT}" stroke-width="1.5" opacity="0.35"/>')
    parts.append(f'<circle cx="{hx + size / 2}" cy="{hy + size / 2}" r="130" fill="none" '
                 f'stroke="{SIGNAL_LIFT}" stroke-width="1.5" opacity="0.16"/>')
    # off the block, up and to the right, tilted, hot
    parts.append(tile(hx + size / 2 + 62, hy + size / 2 - 58, 56, 14, SIGNAL_LIFT))
    return "\n  ".join(parts)


# ---------------------------------------------------------------- OffTheBlockBot
# A bot watching a stream. Rows of messages, all the same, and one it pulls out of
# the flow and hands to you.
def bot():
    parts = []
    rows = [(0.62, 0.30), (0.42, 0.55), (0.78, 0.30), (0.34, 0.62), (0.55, 0.30),
            (0.70, 0.45), (0.38, 0.30), (0.60, 0.52)]
    y = 130
    for i, (w, op) in enumerate(rows):
        bar_w = 620 * w
        parts.append(f'<rect x="180" y="{y}" width="{bar_w:.0f}" height="26" rx="3" '
                     f'fill="{DIM}" opacity="{op:g}"/>')
        # the little block that starts each message
        parts.append(square(140, y - 1, 28, DIM, min(1, op + 0.12)))
        y += 68

    # the one it pulled: a message that has come off the stack and gone hot
    px, py = 900, 300
    parts.append(f'<path d="M840,352 C900,352 900,300 {px + 6},300" fill="none" '
                 f'stroke="{SIGNAL_LIFT}" stroke-width="2" opacity="0.4" '
                 f'stroke-dasharray="6 6"/>')
    parts.append(f'<rect x="{px}" y="{py - 34}" width="300" height="120" rx="6" '
                 f'fill="#171a21" stroke="{LINE}" stroke-width="1.5"/>')
    parts.append(f'<rect x="{px + 26}" y="{py - 4}" width="190" height="14" rx="2" '
                 f'fill="{CHALK}" opacity="0.75"/>')
    parts.append(f'<rect x="{px + 26}" y="{py + 22}" width="130" height="14" rx="2" '
                 f'fill="{SLATE}" opacity="0.7"/>')
    parts.append(tile(px + 300, py - 34, 54, 14, SIGNAL_LIFT))
    return "\n  ".join(parts)


write("art-radar.svg", radar(), "Radar: a field of blocks, and the one that is not like the others")
write("art-otbbot.svg", bot(), "OffTheBlockBot: a stream of messages, and the one worth having")
print("art written to", OUT)
