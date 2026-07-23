"""Draw the ship: OTB-01, block class, with its offcut tender.

    python brand/build-ship.py

A concept sheet in the industrial-design convention, which is where a vehicle
design actually lives before anyone renders it: orthographic views, one plane each,
three line weights that mean something, and callouts that say what a part is for.

The hull is not a spaceship with the brand's colours put on it. It is the mark,
built out to vehicle scale, and the design falls out of the two rules the mark
already has.

The block is the settled thing, so the hull is orthogonal. Every structural edge on
it sits at ninety degrees and the only tilted object anywhere on the sheet is the
piece that left. A square notch is bitten out of the hull's top-forward corner,
exactly as the mark bites its block, and the corner that is now missing is implied
by the two edges that survive it: the top deck running aft of the bite, and the
hull's forward face running below it. Those two are drawn on as construction lines
to where they would have met, because that is what makes the shape read as an
absence rather than as a step.

The piece that came out of the notch is the tender, T-1, and the sheet calls it the
offcut, which is the word for what a block loses when it is cut. It flies ahead of
the hull rather than behind it, because the line the identity is built on is
"before it hits the block", and the thing that has not landed yet is the thing out
in front.

The daylight between them is dimensioned rather than drawn by eye. The mark solves
its tile's centre from the tilted piece's own extent plus a gap, so the tender's
position here is that same solve at hull scale, and the figure on the drawing is
generated from it. Move the geometry and the number moves, because it is read out
of geometry.py rather than typed onto the sheet.

The tender is drawn twice, which is standard practice and also the whole argument:
once as a phantom, dashed, sitting in the notch it came out of, and once solid and
clear of it. It is the only object on the sheet carrying signal and the only one
filled rather than outlined, because on a sheet of line work the one solid is where
the eye goes, and it should go to the piece that is off the block.
"""
import math
import pathlib
import subprocess
import time

from PIL import Image

from geometry import ASPHALT, NORMAL, SIGNAL, SLATE
from shaping import outline

HERE = pathlib.Path(__file__).parent
CHIVO = HERE / "fonts" / "Chivo-Variable.woff2"
MONO = HERE / "fonts" / "JetBrainsMono-Variable.woff2"
OUT = HERE / "ship"

CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

W, H = 1600, 1130                  # A4 landscape, near enough (1.416 against 1.414)
SCALE = 2
DATE = "2026-07-23"

PAPER = "#F2EFE7"
HULL = "#E7E2D6"                   # a lit plane
SHADE = "#D5CFC0"                  # a plane turned away, or a recess
INK = ASPHALT
THIN = SLATE
HOT = SIGNAL

# Three line weights and no more: the silhouette, the structure inside it, and the
# drafting that is not part of the object.
W_EDGE, W_PANEL, W_CONSTRUCT = 2.2, 1.0, 0.7

# ---------------------------------------------------------------- the hull
#
# Ship space runs 0 at the stern to 1000 at the nose tip, y down from 0. Every view
# is drawn in it and placed by a transform, so no two views can disagree about a
# length.

DECK = 96.0                        # top of the block
NOTCH = 85.0                       # the bite, square, as the mark's is
NOTCH_X = 700.0                    # its outer corner: where the hull's corner was
FLOOR = DECK + NOTCH               # the bay floor
KEEL = 340.0

# The forward hull sits a full notch below the bay floor, and that drop is the
# whole reason the bite reads. Bring the forward deck up near the floor and the
# two edges that imply the missing corner shrink to nothing, and what is left is a
# recessed panel at the end of a superstructure. The corner has to be inferable
# from the hull that survived it.
FWD = FLOOR + NOTCH

HULL_SIDE = [
    (200, DECK), (NOTCH_X - NOTCH, DECK),          # top deck, running forward
    (NOTCH_X - NOTCH, FLOOR),                      # down the bay's back wall
    (NOTCH_X, FLOOR),                              # forward along its floor
    (NOTCH_X, FWD),                                # down the hull's forward face
    (884, FWD), (966, 286), (988, 302), (988, 314),
    (930, KEEL), (250, KEEL), (200, 316),          # under-nose, keel, stern rake
]

FIN = [(300, DECK), (334, 40), (426, 40), (452, DECK)]
MAST = [(360, 40), (368, 12), (376, 12), (384, 40)]
BRIDGE = [(506, 117), (600, 117), (592, 140), (514, 140)]
ENGINE = [(122, 128), (200, 116), (200, 320), (122, 308)]
NOZZLES = [164, 218, 272]
HANGAR = [(744, 292), (874, 292), (874, 322), (744, 322)]
THRUSTERS = [(286, KEEL, 40), (600, KEEL, 46)]

# Small stuff, and it is not decoration. A hull this plain has no scale in it: at
# 900 units long and 240 tall it could be a shuttle or a carrier, and a few hatches
# a person could fit through are what settle the question.
HATCHES = [(232, 128, 26, 18), (232, 156, 26, 18), (232, 184, 26, 18),
           (476, 196, 62, 24), (476, 234, 62, 24), (610, 292, 54, 22)]
SENSOR = [(896, 292), (946, 302), (946, 312), (896, 306)]


def tilt(dx, dy, cx, cy, deg):
    r = math.radians(deg)
    cos, sin = math.cos(r), math.sin(r)
    return cx + dx * cos - dy * sin, cy + dx * sin + dy * cos


def tender_frame():
    """Where the piece sits, solved the way the mark solves it.

    The mark places its tile out along the diagonal of the corner it came from, at
    the tilted piece's own half-extent plus a gap, so the daylight holds at any
    tilt and any size. This is that solve, with the notch as the piece and the
    hull's missing corner as the origin, so the ship inherits the rule instead of
    restating it.
    """
    _, t, gap, deg = NORMAL
    ratio = gap / t                                # the gap as a share of the piece
    half = NOTCH / 2
    r = math.radians(deg)
    extent = half * (math.cos(r) + math.sin(r))
    return (NOTCH_X + extent + NOTCH * ratio,
            DECK - extent - NOTCH * ratio, deg, NOTCH * ratio, extent)


TX, TY, TILT, GAP, EXTENT = tender_frame()

# The tender carries the same bite the hull does: an offcut is itself a block with
# a piece gone.
BITE = 17.0
H2 = NOTCH / 2
TENDER = [
    (-H2, -H2 + 10), (-H2 + 10, -H2), (H2 - BITE, -H2),
    (H2 - BITE, -H2 + BITE), (H2, -H2 + BITE),
    (H2, H2 - 10), (H2 - 10, H2), (-H2 + 10, H2), (-H2, H2 - 10),
]
CANOPY = [(2, -H2 + 13), (H2 - 21, -H2 + 13), (H2 - 21, -H2 + 27), (2, -H2 + 27)]
TDRIVE = [(-H2, -H2 + 24), (-H2 - 13, -H2 + 31), (-H2 - 13, H2 - 31), (-H2, H2 - 24)]


def tender_pts(pts):
    return [tilt(dx, dy, TX, TY, TILT) for dx, dy in pts]


# ---------------------------------------------------------------- plan and front

# One straight run and one hard wedge. A nose stepped down in three or four goes
# reads as a curve at this size, and a curve on this hull is the one thing the
# block is not.
PLAN = [(95, 104), (180, 152), (280, 162), (700, 162), (884, 140), (988, 24)]
WING = [(255, 162), (300, 252), (430, 252), (462, 162)]
BEAM = 162.0                       # beam through the bay

FRONT = [(-150, FLOOR), (150, FLOOR), (150, 316), (128, KEEL),
         (-128, KEEL), (-150, 316)]
FRONT_FIN = [(-52, 40), (52, 40), (52, DECK), (-52, DECK)]
FRONT_WING = [(150, 208), (256, 222), (256, 280), (150, 288)]


# ---------------------------------------------------------------- drawing

def d(pts, close=True):
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + (" Z" if close else "")


def path(pts, fill="none", stroke=INK, width=W_PANEL, close=True, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d(pts, close)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linejoin="miter"{dd}/>')


def line(x1, y1, x2, y2, stroke=THIN, width=W_CONSTRUCT, dash=None):
    return path([(x1, y1), (x2, y2)], stroke=stroke, width=width, close=False,
                dash=dash)


def mirror(pts):
    """A half, closed into a whole about the centreline."""
    return [(x, -y) for x, y in pts] + [(x, y) for x, y in reversed(pts)]


def text(txt, x, y, px, fill=INK, src=MONO, weight=500, tracking=0.03,
         anchor="start"):
    p, (x0, y0, x1, _) = outline(txt, src, weight, tracking)
    s = px / -y0 * 0.74
    w = (x1 - x0) * s
    off = {"start": 0.0, "middle": -w / 2, "end": -w}[anchor]
    return (f'<g transform="translate({x - x0 * s + off:.2f} {y:.2f}) '
            f'scale({s:.6f})"><path fill="{fill}" d="{p}"/></g>')


# ---------------------------------------------------------------- the views

def side():
    """The hero. Everything the design argues sits in this one view."""
    bay = [(NOTCH_X - NOTCH, DECK), (NOTCH_X, DECK), (NOTCH_X, FLOOR),
           (NOTCH_X - NOTCH, FLOOR)]
    return "\n  ".join([
        # The corner that is gone, as construction: the two edges that survive the
        # bite, carried on to where they would have met.
        line(NOTCH_X - NOTCH - 74, DECK, NOTCH_X + 92, DECK, THIN, W_CONSTRUCT, "8 5"),
        line(NOTCH_X, FWD + 34, NOTCH_X, DECK - 76, THIN, W_CONSTRUCT, "8 5"),
        line(NOTCH_X, DECK, TX, TY, THIN, W_CONSTRUCT, "3 4"),

        path(ENGINE, SHADE, INK, W_EDGE),
        *[path([(122, cy - 17), (95, cy - 24), (95, cy + 24), (122, cy + 17)],
               SHADE, INK, W_PANEL) for cy in NOZZLES],
        path(MAST, SHADE, INK, W_PANEL),
        path(FIN, HULL, INK, W_EDGE),
        *[path([(x - w / 2, y), (x + w / 2, y), (x + w / 2 - 6, y + 16),
                (x - w / 2 + 6, y + 16)], SHADE, INK, W_PANEL)
          for x, y, w in THRUSTERS],
        path(HULL_SIDE, HULL, INK, W_EDGE),

        # Structure. Both deck lines run aft of the bite, which is what ties the
        # bay into the hull instead of leaving it a dent in the outline.
        line(200, FLOOR, NOTCH_X - NOTCH, FLOOR, INK, W_PANEL),
        line(200, FWD, NOTCH_X, FWD, INK, W_PANEL),
        line(430, DECK, 430, KEEL, INK, W_PANEL),
        line(560, DECK, 560, FWD, INK, W_PANEL),
        line(300, FWD, 300, KEEL, INK, W_PANEL),
        line(NOTCH_X, 322, 936, 322, INK, W_PANEL),
        line(884, FWD, 908, 322, INK, W_PANEL),
        path(HANGAR, SHADE, INK, W_PANEL),
        path([(352, 322), (556, 322), (556, KEEL)], stroke=INK, width=W_PANEL,
             close=False),
        *[path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], SHADE, INK,
               W_PANEL) for x, y, w, h in HATCHES],
        *[line(x, 132, x, 304, INK, W_PANEL) for x in (144, 164, 184)],
        path(SENSOR, INK, INK, W_PANEL),
        path(BRIDGE, SHADE, INK, W_PANEL),
        path(bay, SHADE, INK, W_PANEL),

        # The piece, shown twice: where it was, and where it is.
        path(bay, "none", HOT, W_PANEL, dash="7 5"),
        path(tender_pts(TENDER), HOT, INK, W_EDGE),
        path(tender_pts(TDRIVE), SHADE, INK, W_PANEL),
        path(tender_pts(CANOPY), INK, INK, W_PANEL),
    ])


def plan():
    bay = [(NOTCH_X - NOTCH, -BEAM), (NOTCH_X, -BEAM),
           (NOTCH_X, BEAM), (NOTCH_X - NOTCH, BEAM)]
    return "\n  ".join([
        path(mirror(WING), SHADE, INK, W_EDGE),
        path([(-x, -y) for x, y in WING], SHADE, INK, W_EDGE),
        path(mirror(PLAN), HULL, INK, W_EDGE),
        path(bay, SHADE, INK, W_PANEL),
        path(bay, "none", HOT, W_PANEL, dash="7 5"),
        line(60, 0, 1030, 0, THIN, W_CONSTRUCT, "14 5 3 5"),
        line(280, -162, 280, 162, INK, W_PANEL),
        line(180, -152, 180, 152, INK, W_PANEL),
        line(460, -162, 460, 162, INK, W_PANEL),
        line(884, -140, 884, 140, INK, W_PANEL),
        # T-1 flies over the deck, so in plan it is a thing in another plane.
        path([(TX - H2, -H2), (TX + H2, -H2), (TX + H2, H2), (TX - H2, H2)],
             "none", HOT, W_PANEL, dash="7 5"),
    ])


def front():
    return "\n  ".join([
        path(FRONT_WING, SHADE, INK, W_EDGE),
        path([(-x, y) for x, y in FRONT_WING], SHADE, INK, W_EDGE),
        path(FRONT, HULL, INK, W_EDGE),
        path(FRONT_FIN, HULL, INK, W_EDGE),
        # The bite is taken across the full beam, so from the front you look into
        # the bay and the top deck is behind it. Dashed, because it is beyond.
        line(-150, DECK, 150, DECK, INK, W_PANEL, "7 5"),
        line(-150, 316, 150, 316, INK, W_PANEL),
        line(0, 16, 0, KEEL + 26, THIN, W_CONSTRUCT, "14 5 3 5"),
    ])


# ---------------------------------------------------------------- annotation
#
# Balloons on the drawing, the words in a block. Long labels beside an object
# either collide with each other or run off the sheet, and a leader that crosses
# the whole hull to reach its text costs more than the text is worth.

BALLOONS = [
    (1, 400, 210, 392, 406),
    (2, 615, 139, 548, 20),
    (3, 790, 18, 906, 2),
    (4, 710, 88, 772, 194),
    (5, 108, 218, 40, 300),
    (6, 553, 128, 470, 6),
    (7, 454, KEEL, 524, 406),
]

NOTES = [
    "MAIN BLOCK. Heavy hull, orthogonal throughout.",
    "NOTCH BAY. The bite. T-1 launches from here.",
    "T-1 OFFCUT. The piece. The only tilt on the sheet.",
    "GAP. Solved, not styled. Held at 15.6% of the piece.",
    "DRIVE. Three block nozzles, fixed, no gimbal.",
    "BRIDGE. Set aft of the bay, behind the cradle.",
    "KEEL BAY. Ventral hold, doors port and starboard.",
]


def hero_place(scale, top):
    """Ship space to sheet space, so annotation is drawn at true type size.

    Annotation inside the scaled group would come out at the group's scale, which
    means every label on a sheet with three views would be a different size.
    """
    width = (988 - 95) * scale
    x0 = (W - width) / 2 - 95 * scale
    y0 = top - (TY - EXTENT) * scale
    return x0, y0, lambda x, y: (x0 + x * scale, y0 + y * scale)


def balloons(at):
    out = []
    for n, tx, ty, bx, by in BALLOONS:
        px, py = at(tx, ty)
        cx, cy = at(bx, by)
        dx, dy = px - cx, py - cy
        m = math.hypot(dx, dy) or 1
        sx, sy = cx + dx / m * 13, cy + dy / m * 13
        out += [
            line(sx, sy, px, py, THIN, W_CONSTRUCT),
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.8" fill="{INK}"/>',
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="12.5" fill="{PAPER}" '
            f'stroke="{INK}" stroke-width="1.2"/>',
            text(str(n), cx, cy + 5, 14, INK, MONO, 600, 0, "middle"),
        ]
    return "\n  ".join(out)


def gap_dimension(at):
    """The daylight, dimensioned off the hull's missing corner.

    Extension lines up from the corner and from the piece's nearest extent, the
    dimension between them, and the figure set off to one side because the
    distance is far narrower than the text that names it.

    The piece's nearest vertex lands at exactly one gap clear of the corner in x,
    which is not an accident of these numbers but the thing place() solves for in
    the mark, so it is asserted here rather than trusted.
    """
    lx, ly = tilt(-H2, H2, TX, TY, TILT)
    assert abs(lx - (NOTCH_X + GAP)) < 1e-9, "the piece is not a gap clear"

    px1, py1 = at(NOTCH_X, DECK)
    px2, py2 = at(lx, ly)
    _, y = at(0, DECK - 66)
    return "\n  ".join([
        line(px1, py1, px1, y - 7, INK, W_CONSTRUCT),
        line(px2, py2, px2, y - 7, INK, W_CONSTRUCT),
        line(px1 - 8, y, px2 + 8, y, INK, W_CONSTRUCT),
        line(px1, y - 4, px1, y + 4, INK, 1.4),
        line(px2, y - 4, px2, y + 4, INK, 1.4),
        text(f"GAP {GAP:.1f}", px1 - 15, y + 4, 11.5, INK, MONO, 500, 0.03, "end"),
    ])


def notes(x, y):
    out = [text("NOTES", x, y, 12, INK, MONO, 700, 0.12)]
    out.append(line(x, y + 10, x + 470, y + 10, INK, 1.0))
    for i, txt in enumerate(NOTES):
        row = y + 36 + i * 25
        out += [
            f'<circle cx="{x + 9:.2f}" cy="{row - 4:.2f}" r="9.5" fill="none" '
            f'stroke="{THIN}" stroke-width="1"/>',
            text(str(i + 1), x + 9, row, 11, INK, MONO, 600, 0, "middle"),
            text(txt, x + 30, row, 11.5, THIN, MONO, 500, 0.03),
        ]
    return "\n  ".join(out)


def titleblock(x, y):
    out = [
        text("OTB-01", x, y, 30, INK, CHIVO, 800, -0.02),
        text("BLOCK CLASS  /  HEAVY HULL", x, y + 26, 12, INK),
        text("with T-1 OFFCUT tender", x, y + 47, 12, THIN),
        line(x, y + 64, x + 470, y + 64, INK, 1.0),
    ]
    for i, txt in enumerate(("CONCEPT SHEET 01  /  SIDE, PLAN, FRONT",
                             "HULL GEOMETRY DERIVED FROM THE MARK",
                             f"GAP HELD AT {GAP / NOTCH:.1%} OF THE PIECE")):
        out.append(text(txt, x, y + 86 + i * 19, 11.5, THIN))
    return "\n  ".join(out)


def frame():
    m, t = 34, 16
    parts = [f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" '
             f'fill="none" stroke="{INK}" stroke-width="1.2"/>']
    for cx, cy, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1),
                           (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        parts.append(line(cx, cy + sy * t, cx + sx * t, cy + sy * t, INK, 1.2))
        parts.append(line(cx + sx * t, cy, cx + sx * t, cy + sy * t, INK, 1.2))
    return "\n  ".join(parts)


def render(svg, out):
    td = HERE / ".render"
    td.mkdir(exist_ok=True)
    page, shot = td / "ship.html", td / "ship.png"
    if shot.exists():
        shot.unlink()
    page.write_text('<!doctype html><meta charset="utf-8">'
                    '<style>html,body{margin:0;padding:0;overflow:hidden}'
                    'svg{display:block}</style>' + svg, encoding="utf-8")
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
        print(f"    chrome missed the sheet, retry {attempt + 1}")
    else:
        raise SystemExit("chrome would not render the sheet after 6 tries")
    im = Image.open(shot).convert("RGB")
    assert im.size == (W * SCALE, H * SCALE), f"rendered {im.size}"
    im.save(out, optimize=True)
    return im


# ---------------------------------------------------------------- the sheet

S_HERO, S_ORTHO = 0.95, 0.56
HX, HY, at = hero_place(S_HERO, 178)
PX, PY = 90 - 95 * S_ORTHO, 812
FX, FY = 800, 954 - KEEL * S_ORTHO

assert at(988, 0)[0] < W - 62, "the hero runs into the right margin"
assert at(95, 0)[0] > 62, "the hero runs into the left margin"
assert PX + 988 * S_ORTHO < 620, "the plan runs into the front view"

body = "\n  ".join([
    f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
    frame(),

    text("blockballr", 62, 104, 34, INK, CHIVO, 800, -0.018),
    text("SPACEFRAME  /  CONCEPT  /  ONE OF ONE", 62, 128, 12, THIN),
    text("OTB-01", W - 62, 104, 22, INK, MONO, 700, 0.04, "end"),
    text(DATE, W - 62, 128, 12, THIN, MONO, 500, 0.04, "end"),
    line(62, 148, W - 62, 148, INK, 1.0),

    f'<g transform="translate({HX:.2f} {HY:.2f}) scale({S_HERO})">'
    f'\n  {side()}\n  </g>',
    gap_dimension(at),
    balloons(at),
    text("SIDE ELEVATION", 62, 612, 13, INK, MONO, 700, 0.12),
    line(62, 628, W - 62, 628, THIN, W_CONSTRUCT),

    f'<g transform="translate({PX:.2f} {PY}) scale({S_ORTHO})">\n  {plan()}\n  </g>',
    text("PLAN", 90, 1006, 13, INK, MONO, 700, 0.12),

    f'<g transform="translate({FX} {FY:.2f}) scale({S_ORTHO})">\n  {front()}\n  </g>',
    text("FRONT", FX - 150 * S_ORTHO, 1006, 13, INK, MONO, 700, 0.12),

    titleblock(1000, 700),
    notes(1000, 866),
])

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}">\n  {body}\n</svg>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "otb-01.svg").write_text(
    "<!-- Drawn from brand/build-ship.py. Do not hand-edit. -->\n" + svg + "\n",
    encoding="utf-8")
im = render(svg, OUT / "otb-01.png")

print(f"  tender at ({TX:.1f}, {TY:.1f}), {TILT:g} deg, extent {EXTENT:.1f}")
print(f"  gap {GAP:.2f} = {GAP / NOTCH:.1%} of the piece, as the mark holds it")
print(f"  otb-01.png  {im.size[0]}x{im.size[1]}, "
      f"{(OUT / 'otb-01.png').stat().st_size / 1024:.0f} KB")
print("ship written to", OUT)
