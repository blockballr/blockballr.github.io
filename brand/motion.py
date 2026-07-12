"""The mark in motion, as numbers.

The mark is already a before and an after. The tile starts in the notch, square and
flush, part of the block. It ends clear of the block and tilted. Those two states are
in geometry.py and nothing here invents them: the animation is the interpolation
between the mark's own start and its own end, and the last frame is asserted to be
the logo, to the fourth decimal.

Two rules, and they are the same two rules the still mark has.

The block does not move. The block is the settled thing; that is what the word means
and it is why the tile is the only thing with a tilt. Animate the block and the mark
stops making its argument. Nothing here touches it.

The tile does not rotate about the block's corner. That would be a hinge, and a hinge
is a lid. It rotates about its own centre while it travels, because it came off.

The travel is a departure, not a slide: the tile leaves along the diagonal of the
corner it came out of, because it clears the block in both axes at once, which is
what place() in geometry.py already solves for.
"""
import math

from geometry import NORMAL, place

# The tile's rest state: sitting in the notch it was cut from. The block's top-right
# corner is the origin, and the notch is the square from (-t, 0) to (0, t), so the
# tile at rest is centred on the middle of that square, at no tilt at all.
def start(spec):
    _, t, _, _ = spec
    return (-t / 2, t / 2), 0.0


def end(spec):
    """Where it lands: the mark. Straight out of geometry, never re-derived."""
    _, _, _, deg = spec
    return place(spec), float(deg)


# One easing curve for everything. The SVG, the CSS on the site, and the rasterised
# frames all sample this same function, so the three cannot drift into three slightly
# different animations of the same logo.
#
# It is a hard ease-out with a little overshoot: the piece leaves fast, arrives, and
# settles a hair past where it stops. A linear travel reads as a machine moving a
# part. This reads as something coming loose.
EASE = (0.20, 0.90, 0.20, 1.06)
DURATION = 0.9          # seconds, the departure
HOLD = 1.4              # seconds it sits there, off the block
FADE = 0.35             # seconds it takes to go
BEAT = 0.25             # empty block, before the next piece comes off
LOOP = DURATION + HOLD + FADE + BEAT


def bezier(t, p1x, p1y, p2x, p2y):
    """Solve a CSS cubic-bezier for y at time t, by bisection on x.

    Bisection rather than Newton because this runs a few thousand times at build
    time and never in a hot loop, and a bisection cannot fail to converge on a
    monotonic curve the way Newton can when the control points are steep.
    """
    def curve(a, b, u):
        v = 1 - u
        return 3 * v * v * u * a + 3 * v * u * u * b + u * u * u

    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if curve(p1x, p2x, mid) < t:
            lo = mid
        else:
            hi = mid
    return curve(p1y, p2y, (lo + hi) / 2)


def ease(t):
    return bezier(min(max(t, 0.0), 1.0), *EASE)


def at(spec, t):
    """The tile at progress t in [0, 1]: (centre, degrees).

    Position and rotation ride the same curve, so the piece finishes turning exactly
    when it finishes travelling. Letting them run on separate timings makes it look
    like two animations that happen to overlap.
    """
    (sx, sy), sdeg = start(spec)
    (ex, ey), edeg = end(spec)
    e = ease(t)
    return (sx + (ex - sx) * e, sy + (ey - sy) * e), sdeg + (edeg - sdeg) * e


def corners(spec, centre, deg):
    """The loose piece as four points, rotated about its own centre."""
    _, t, _, _ = spec
    cx, cy = centre
    r, h = math.radians(deg), t / 2
    cos, sin = math.cos(r), math.sin(r)
    return [(cx + dx * cos - dy * sin, cy + dx * sin + dy * cos)
            for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]


def block_points(spec):
    """The block, as the polygon geometry.py draws. It never moves."""
    b, t, _, _ = spec
    return [(-b, 0), (-t, 0), (-t, t), (0, t), (0, b), (-b, b)]


# The animation must END as the logo. If this ever fails, the motion has drifted from
# the mark and the last frame is no longer the brand.
def check(spec=NORMAL):
    from geometry import tile_corners
    got = corners(spec, *at(spec, 1.0))
    want = tile_corners(spec)
    worst = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(got, want))
    assert worst < 1e-4, f"the last frame is not the mark: off by {worst:.6f}"
    return worst


if __name__ == "__main__":
    spec = NORMAL
    (sx, sy), sdeg = start(spec)
    (ex, ey), edeg = end(spec)
    print(f"  rest    centre ({sx:7.3f}, {sy:7.3f})  tilt {sdeg:.0f}deg   in the notch")
    print(f"  gone    centre ({ex:7.3f}, {ey:7.3f})  tilt {edeg:.0f}deg   off the block")
    print(f"  travel  {math.hypot(ex - sx, ey - sy):.3f} units, out along the diagonal")
    print(f"  timing  {DURATION}s out, {HOLD}s held, {FADE}s gone, {BEAT}s empty "
          f"-> {LOOP:.2f}s loop")
    print(f"  easing  cubic-bezier{EASE}")
    print(f"\n  last frame matches the mark to {check(spec):.2e} units")
