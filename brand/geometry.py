"""The OffTheBlock mark, as numbers. The single source every build script reads.

A block is the settled thing. It is public, it is final, and by the time something
is on it, everyone already has it. Alpha is what has not hit the block yet. The
community is the room where that gets said, off the block, before it lands.

The mark is a block with one piece off it. A square with a square notch bitten out
of its corner, and the piece that came out now clear of it, tilted.

Two properties are load-bearing.

The first is the tilt. The block is orthogonal and the piece that left is not.
Every edge of the block sits at ninety degrees, because a block is settled. The
loose piece is tilted, because it is not. Set the tile square to the block and the
mark collapses into a diagram of nothing: a square, and a smaller square, tidily
arranged.

The second is the gap, and it is the one that is easy to lose. The piece must fully
clear the notch it came out of, or the notch is covered and the mark reads as a
square with a tile stuck to its corner: an object with a decoration, rather than an
object and its absence. The void is half the logo. So the gap is not a distance
that was nudged until it looked right. It is solved for: place() below computes the
tile's centre from the tilted tile's own extent, so the daylight is guaranteed at
every size and every tilt rather than hoped for.

The tile is the same size as its notch, because it came out of it. Shrink one and
the two shapes stop being one object.
"""

import math

BOX = 64.0

#   (block size, tile size, the guaranteed daylight between them, tilt in degrees)
NORMAL = (36.0, 16.0, 2.5, 14.0)   # 24px and up
MICRO = (33.0, 17.0, 5.0, 10.0)    # under 24px

# The tile is 44% of the block, and that ceiling is deliberate. The notch is the
# tile's own width taken out of the block's edge, so a tile at half the block or
# more bites away more than half that edge and the block stops reading as a square
# with a piece missing. It becomes a plain L, which is a corner, not a block. The
# name is the block. It has to read as one.
#
# The cost is that a 16-unit tile is small at 24px, which is exactly the job the
# micro variant below exists to do. Small sizes get a chunkier tile there rather
# than the primary mark being compromised for them everywhere else.

# A square bounding box of side s only fits inside a circle of diameter D when
# s * sqrt(2) <= D. Telegram and Discord both crop avatars to a circle, and this
# mark runs corner to corner, so at full bleed the tile is the first thing the crop
# takes off. Avatar artwork scales the mark to the inscribed square. This is not a
# style choice and it is not padding taste; it is the geometry of the crop.
CIRCLE_SAFE = 0.707

# Under 24px the gap is the first thing to die. Three units of daylight is under one
# device pixel at 16px, the block and the tile fuse into one grey lump, and the mark
# says nothing. The micro variant widens the gap, grows the tile so it survives as
# more than a speck, and flattens the tilt, because a 14-degree rotation on a
# five-pixel square rasterises to mush. The tilt narrows but never closes, and the
# gap widens but never fills, because those two are the argument.

ASPHALT = "#14161B"
CHALK = "#F0EEE9"
SIGNAL = "#E4326B"
SLATE = "#5E6673"
WHITE = "#FFFFFF"

NIGHT = "#0B0C0F"
ASPHALT_LIFT = "#EAEBEE"
SIGNAL_LIFT = "#FF5C8D"
SLATE_LIFT = "#9AA1AC"


def extent(spec):
    """Half the width of the tilted tile's bounding box.

    A square rotated by d has a bounding box of t*(cos d + sin d). This is what the
    gap has to be measured against; measuring against the tile's own side length
    would let a corner poke back into the notch as the tilt grows.
    """
    _, t, _, deg = spec
    r = math.radians(deg)
    return (t / 2) * (math.cos(r) + math.sin(r))


def place(spec):
    """The tile's centre, solved so it clears the block's corner by the gap.

    The block sits with its top-right corner at the origin of this frame, so the
    tile is up and to the right of (0, 0) and everything below is measured from
    there. Clearing in both axes at once puts the tile out along the diagonal of
    the corner it came from, which is what makes the travel read as a departure
    rather than a slide.
    """
    _, _, gap, _ = spec
    e = extent(spec) + gap
    return e, -e


def block_path(spec):
    """The block: a square with the top-right corner bitten out.

    Drawn as one closed path rather than a rectangle with a rectangle punched from
    it, so the shape survives a fill rule, a mask, and a single-colour print. Its
    top-right corner is the origin, so the block hangs down and to the left and the
    tile leaves up and to the right, into open space.
    """
    b, t, _, _ = spec
    return (f"M{-b:g},0 "
            f"L{-t:g},0 "
            f"L{-t:g},{t:g} "
            f"L0,{t:g} "
            f"L0,{b:g} "
            f"L{-b:g},{b:g} Z")


def tile_corners(spec):
    """The four corners of the loose piece, tilted about its own centre.

    A rotation about the block's corner instead would swing the tile, and a swing
    is a hinge. This piece is not hinged to anything. It came off.
    """
    _, t, _, deg = spec
    cx, cy = place(spec)
    r, h = math.radians(deg), t / 2
    cos, sin = math.cos(r), math.sin(r)
    return [(cx + dx * cos - dy * sin, cy + dx * sin + dy * cos)
            for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]


def tile_path(spec):
    pts = tile_corners(spec)
    return "M" + " L".join(f"{x:.4f},{y:.4f}" for x, y in pts) + " Z"


def shapes(spec):
    """Every shape in the mark: (path, role). Role names the paint."""
    return [(block_path(spec), "block"), (tile_path(spec), "signal")]


def ink(spec):
    """Where the mark's paint actually sits: (x, y, width, height).

    Comes out exactly square, and not by luck: the block runs b back from the
    corner, the tile runs extent+gap forward from it in both axes, so width and
    height are both b + 2*extent + gap. Both shapes are polygons, so their corners
    are the extremes and no curve sampling is needed.
    """
    b, _, _, _ = spec
    xs = [-b, 0] + [x for x, _ in tile_corners(spec)]
    ys = [0, b] + [y for _, y in tile_corners(spec)]
    x0, y0 = min(xs), min(ys)
    return x0, y0, max(xs) - x0, max(ys) - y0


def centre(spec):
    """How far to slide the mark so its ink sits centred in the box."""
    x0, y0, w, h = ink(spec)
    return (BOX - w) / 2 - x0, (BOX - h) / 2 - y0


def block_corners(spec):
    """The notched block as a polygon, in the same frame as tile_corners."""
    b, t, _, _ = spec
    return [(-b, 0), (-t, 0), (-t, t), (0, t), (0, b), (-b, b)]


def _area_centroid(pts):
    """Signed area and centroid of a simple polygon (the shoelace formula)."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    return abs(a), cx / (6 * a), cy / (6 * a)


def balance(spec):
    """The mark's centre of mass, as a fraction across and down its ink box.

    The bounding box lies about where this mark sits. Almost all of its weight is
    the block, down in one corner, and the tile is a small counterweight thrown
    out to the other. Centring anything on the bounding box therefore hangs it off
    a point with no ink anywhere near it, and the stacked lockup visibly leans.
    The area centroid is where the mark actually balances, so that is what the
    word gets centred under.
    """
    ba, bx, by = _area_centroid(block_corners(spec))
    ta, tx, ty = _area_centroid(tile_corners(spec))
    total = ba + ta
    mx = (bx * ba + tx * ta) / total
    my = (by * ba + ty * ta) / total
    x0, y0, w, h = ink(spec)
    return (mx - x0) / w, (my - y0) / h


def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    """WCAG contrast ratio, so the rules in brand.md are checkable rather than felt."""
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


if __name__ == "__main__":
    for name, spec in (("NORMAL", NORMAL), ("MICRO", MICRO)):
        x, y, w, h = ink(spec)
        b, t, gap, deg = spec
        # The gap, in device pixels, at the size this variant is actually used at.
        px = 24 if name == "NORMAL" else 16
        bx, by = balance(spec)
        print(f"{name:>6}  ink {w:.2f}x{h:.2f}  tile/block {t / b:.0%}  "
              f"tilt {deg:g}deg  gap {gap:g}u = {gap * px / w:.2f}px at {px}px")
        print(f"        balances at {bx:.1%} across, {by:.1%} down "
              f"(the bounding box says 50%, 50%)")
    print()
    pairs = [("SIGNAL", SIGNAL, "WHITE", WHITE),
             ("SIGNAL", SIGNAL, "CHALK", CHALK),
             ("SIGNAL_LIFT", SIGNAL_LIFT, "ASPHALT", ASPHALT),
             ("SIGNAL_LIFT", SIGNAL_LIFT, "NIGHT", NIGHT),
             ("ASPHALT", ASPHALT, "CHALK", CHALK),
             ("SLATE", SLATE, "CHALK", CHALK),
             ("SLATE_LIFT", SLATE_LIFT, "NIGHT", NIGHT),
             ("CHALK", CHALK, "NIGHT", NIGHT)]
    for an, a, bn, b in pairs:
        r = contrast(a, b)
        tag = "body" if r >= 4.5 else ("large only" if r >= 3.0 else "SHAPE ONLY")
        print(f"{an:>11} on {bn:<8} {r:5.2f}  {tag}")
