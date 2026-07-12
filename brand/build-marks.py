"""Rebuild the OffTheBlock marks as SVG.

    python brand/build-marks.py

Every file here is drawn from geometry.py. Nothing in this script decides what the
mark looks like; it only decides what colour it is and what ground it sits on.
"""
import pathlib

from geometry import (ASPHALT, BOX, CHALK, MICRO, NIGHT, NORMAL, SIGNAL,
                      SIGNAL_LIFT, WHITE, centre, shapes)

OUT = pathlib.Path(__file__).parent / "logo"

NOTE = ("<!-- Drawn from brand/geometry.py. Do not hand-edit.\n"
        "     Regenerate with: python brand/build-marks.py -->\n")


def svg(name, body, label="OffTheBlock", ground=None):
    rect = f'<rect width="{BOX:g}" height="{BOX:g}" fill="{ground}"/>' if ground else ""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(
        f'{NOTE}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX:g} {BOX:g}" '
        f'width="{BOX:g}" height="{BOX:g}" role="img" aria-label="{label}">\n'
        f'  <title>{label}</title>\n'
        f'  {rect}{body}\n</svg>\n', encoding="utf-8")
    print(f"  {name}")


def mark(spec, block, signal):
    """The two shapes, slid so their combined ink sits centred in the box."""
    dx, dy = centre(spec)
    paint = {"block": block, "signal": signal}
    paths = "".join(f'<path d="{d}" fill="{paint[role]}"/>' for d, role in shapes(spec))
    return f'<g transform="translate({dx:.3f} {dy:.3f})">{paths}</g>'


# Primary. Asphalt block, signal tile, for light grounds.
svg("offtheblock-mark.svg", mark(NORMAL, ASPHALT, SIGNAL))

# Knockout. On a near-black ground the base signal goes heavy and the block
# disappears into the page, so the block takes chalk and the tile takes the lift.
svg("offtheblock-mark-knockout.svg", mark(NORMAL, CHALK, SIGNAL_LIFT))

# One colour, inherited. The tilt alone carries the meaning here, which is exactly
# why the notch exists: without it, two same-coloured squares say nothing.
svg("offtheblock-mark-mono.svg", mark(NORMAL, "currentColor", "currentColor"))

# Under 24px. Bigger tile, shorter travel, flatter tilt.
svg("offtheblock-mark-micro.svg", mark(MICRO, ASPHALT, SIGNAL))

# Solid. The mark held inside its own ground, for app icons and avatars, where the
# artwork cannot rely on the page behind it being any particular colour.
svg("offtheblock-mark-solid.svg", mark(NORMAL, CHALK, SIGNAL_LIFT), ground=NIGHT)

print("marks written to", OUT)
