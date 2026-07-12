"""Build the mark in motion.

    python brand/build-motion.py

Writes the animated logo as SVG, the social loop as GIF and APNG, and prints the CSS
the site needs, then checks the site still matches it.

Everything here samples motion.py, which samples geometry.py. There is one animation
of this logo, expressed three times because three players need three formats, and the
build fails if the last frame stops being the mark.

  offtheblock-mark-motion.svg          plays once and stops on the logo
  offtheblock-mark-motion-knockout.svg the same, for dark grounds
  offtheblock-mark-loop.svg            loops: a piece comes off, and another
  motion/offtheblock-loop.gif          the loop, for anywhere that eats a GIF
  motion/offtheblock-loop.png          the same as APNG, which has real alpha

The SVGs use SMIL rather than CSS, because these files get used inside an <img>, and
an <img> is an isolated document: a CSS animation defined by the host page cannot
reach into it. SMIL travels with the file. The site's own inline mark is the opposite
case and uses CSS, so it can be turned off for a reader who asked for less motion.
"""
import math
import pathlib

from PIL import Image, ImageDraw

import motion
from geometry import (ASPHALT, CHALK, NIGHT, NORMAL, SIGNAL, SIGNAL_LIFT, ink)

HERE = pathlib.Path(__file__).parent
LOGO = HERE / "logo"
OUT = HERE / "motion"
SITE = HERE.parent

SPEC = NORMAL
SAMPLES = 32          # how finely the ease is baked into the SVG's value list
FPS = 20
PX = 512              # the raster loop's size

worst = motion.check(SPEC)
X0, Y0, W, H = ink(SPEC)


# ------------------------------------------------------------------ SVG
def values(fn, whole_loop):
    """Bake the easing into a list of samples, with the times they land on.

    The curve is sampled rather than handed to SMIL as keySplines because SMIL's
    spline support cannot express an overshoot past 1, and this ease overshoots on
    purpose. Sampling is exact and every player agrees on what a straight line is.
    """
    ts, vs = [], []
    if not whole_loop:
        for i in range(SAMPLES + 1):
            t = i / SAMPLES
            ts.append(t)
            vs.append(fn(motion.at(SPEC, t)))
        return ts, vs

    L = motion.LOOP
    gone = motion.DURATION + motion.HOLD + motion.FADE     # when it has finished going
    for i in range(SAMPLES + 1):                            # the departure
        t = (i / SAMPLES) * motion.DURATION
        ts.append(t / L)
        vs.append(fn(motion.at(SPEC, i / SAMPLES)))
    ts.append(gone / L)                                     # holds, then is gone
    vs.append(fn(motion.at(SPEC, 1.0)))
    ts.append(gone / L + 1e-4)                              # snaps back, under opacity 0
    vs.append(fn(motion.at(SPEC, 0.0)))
    ts.append(1.0)
    vs.append(fn(motion.at(SPEC, 0.0)))
    return ts, vs


def anim(loop):
    dur = motion.LOOP if loop else motion.DURATION
    ts, tr = values(lambda s: f"{s[0][0]:.4f} {s[0][1]:.4f}", loop)
    _, rot = values(lambda s: f"{s[1]:.4f}", loop)
    keys = ";".join(f"{t:.5f}" for t in ts)
    rep = 'repeatCount="indefinite"' if loop else 'fill="freeze"'

    # translate first, then rotate about the tile's own centre. additive="sum" keeps
    # them as one transform; a rotate written on its own would spin about the origin,
    # which is the block's corner, which is a hinge.
    out = (f'<animateTransform attributeName="transform" type="translate" '
           f'dur="{dur}s" {rep} calcMode="linear" '
           f'keyTimes="{keys}" values="{";".join(tr)}"/>'
           f'<animateTransform attributeName="transform" type="rotate" additive="sum" '
           f'dur="{dur}s" {rep} calcMode="linear" '
           f'keyTimes="{keys}" values="{";".join(rot)}"/>')

    if loop:
        # It leaves, it is held, it goes, and the notch sits empty for a beat before
        # the next one comes off. The empty notch is the point of the logo, so the
        # loop is built to show it.
        L = motion.LOOP
        k = [0, (motion.DURATION + motion.HOLD) / L,
             (motion.DURATION + motion.HOLD + motion.FADE) / L, 1]
        out += (f'<animate attributeName="opacity" dur="{L}s" repeatCount="indefinite" '
                f'keyTimes="{";".join(f"{x:.5f}" for x in k)}" values="1;1;0;0"/>')
    return out


def svg(name, block, signal, loop=False, ground=None):
    _, t, _, _ = SPEC
    h = t / 2
    bg = f'<rect x="{X0:.4f}" y="{Y0:.4f}" width="{W:.4f}" height="{H:.4f}" fill="{ground}"/>' if ground else ""
    body = (
        f'<g transform="translate({-X0:.4f} {-Y0:.4f})">'
        f'{bg}'
        f'<path d="{__import__("geometry").block_path(SPEC)}" fill="{block}"/>'
        # the loose piece, drawn once at the origin and moved by the transform, so the
        # animation is one shape being carried rather than a path being redrawn
        f'<g><path d="M{-h:g},{-h:g} L{h:g},{-h:g} L{h:g},{h:g} L{-h:g},{h:g} Z" '
        f'fill="{signal}"/>{anim(loop)}</g>'
        f'</g>')
    label = "OffTheBlock: a piece comes off the block"
    (LOGO / name).write_text(
        f'<!-- Animated from brand/motion.py. The last frame is the mark, asserted at\n'
        f'     build time. Do not hand-edit. -->\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}" '
        f'width="{W:.0f}" height="{H:.0f}" role="img" aria-label="{label}">'
        f'<title>{label}</title>{body}</svg>\n', encoding="utf-8")
    print(f"  logo/{name}")


LOGO.mkdir(parents=True, exist_ok=True)
svg("offtheblock-mark-motion.svg", ASPHALT, SIGNAL)
svg("offtheblock-mark-motion-knockout.svg", CHALK, SIGNAL_LIFT)
svg("offtheblock-mark-loop.svg", CHALK, SIGNAL_LIFT, loop=True)


# ------------------------------------------------------------------ raster
def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def frames():
    """Draw the loop with Pillow. Supersampled 4x, because the tile is a rotated
    square and an aliased diagonal is the one thing that makes a logo look cheap."""
    ss, pad = 4, 0.84
    size = PX * ss
    scale = size * pad / max(W, H)
    ox = (size - W * scale) / 2 - X0 * scale
    oy = (size - H * scale) / 2 - Y0 * scale

    def to_px(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    n = max(1, round(motion.LOOP * FPS))
    out = []
    for i in range(n):
        t = i / n * motion.LOOP
        im = Image.new("RGBA", (size, size), rgb(NIGHT) + (255,))
        d = ImageDraw.Draw(im)
        d.polygon([to_px(p) for p in motion.block_points(SPEC)], fill=rgb(CHALK))

        if t <= motion.DURATION:
            p = t / motion.DURATION
            a = 255
        elif t <= motion.DURATION + motion.HOLD:
            p, a = 1.0, 255
        elif t <= motion.DURATION + motion.HOLD + motion.FADE:
            p = 1.0
            a = round(255 * (1 - (t - motion.DURATION - motion.HOLD) / motion.FADE))
        else:
            p, a = 0.0, 0                       # gone; the notch sits empty
        if a > 0:
            tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ImageDraw.Draw(tile).polygon(
                [to_px(p2) for p2 in motion.corners(SPEC, *motion.at(SPEC, p))],
                fill=rgb(SIGNAL_LIFT) + (a,))
            im = Image.alpha_composite(im, tile)
        out.append(im.resize((PX, PX), Image.LANCZOS))
    return out


OUT.mkdir(parents=True, exist_ok=True)
fr = frames()
ms = round(1000 / FPS)

fr[0].convert("RGB").save(OUT / "offtheblock-loop.gif", save_all=True,
                          append_images=[f.convert("RGB") for f in fr[1:]],
                          duration=ms, loop=0, optimize=True)
fr[0].save(OUT / "offtheblock-loop.png", save_all=True, append_images=fr[1:],
           duration=ms, loop=0)

gif_kb = (OUT / "offtheblock-loop.gif").stat().st_size / 1024
png_kb = (OUT / "offtheblock-loop.png").stat().st_size / 1024
# X will not autoplay a GIF over 15MB and Telegram is slower for every byte, so this
# is checked rather than hoped for.
assert gif_kb < 4096, f"the loop is {gif_kb:.0f} KB, too heavy to post"
print(f"  motion/offtheblock-loop.gif  {len(fr)} frames, {PX}px, {gif_kb:.0f} KB")
print(f"  motion/offtheblock-loop.png  APNG, {png_kb:.0f} KB")


# ------------------------------------------------------------------ the site
# The page's mark is inline SVG, so it animates with CSS and can therefore be turned
# off for a reader who has asked for reduced motion. SMIL cannot be, which is exactly
# why the page does not use it.
(sx, sy), _ = motion.start(SPEC)
(ex, ey), deg = motion.end(SPEC)
DX, DY = sx - ex, sy - ey
L = motion.LOOP
REST = f"translate({DX:.3f}px,{DY:.3f}px) rotate({-deg:g}deg)"   # in the notch, square
K_OUT = 100 * motion.DURATION / L                       # it has left
K_HELD = 100 * (motion.DURATION + motion.HOLD) / L      # it stops being held
K_GONE = 100 * (motion.DURATION + motion.HOLD + motion.FADE) / L   # it has gone
EASE_CSS = f"cubic-bezier({','.join(f'{v:g}' for v in motion.EASE)})"

# The keyframe just past K_GONE is the one doing the quiet work: the tile snaps back
# into its notch while its opacity is zero, so the loop restarts with a piece on the
# block and nobody sees it travel backwards. Without that, the tile would visibly fly
# home, and a piece returning to the block is the opposite of what the mark says.
SNAP = K_GONE + 0.01

CSS = f"""/* The loop: a piece comes off the block, is held, goes, and the notch sits
   empty for a beat before the next one. Generated by brand/build-motion.py from the
   mark's own geometry. The block never moves; only the tile does. */
.logo .tile{{
  transform-box:fill-box; transform-origin:center;
  animation:otb-loop {L:g}s linear infinite;
}}
@keyframes otb-loop{{
  0%{{transform:{REST}; opacity:1; animation-timing-function:{EASE_CSS}}}
  {K_OUT:.3f}%{{transform:none; opacity:1}}
  {K_HELD:.3f}%{{transform:none; opacity:1}}
  {K_GONE:.3f}%{{transform:none; opacity:0}}
  {SNAP:.3f}%{{transform:{REST}; opacity:0}}
  100%{{transform:{REST}; opacity:0}}
}}
/* A logo that never stops moving is a logo nobody can read, so it holds still while
   anything on the page is being pointed at, and for anyone who asked for less. */
.logo:hover .tile{{animation-play-state:paused}}
@media(prefers-reduced-motion:reduce){{ .logo .tile{{animation:none}} }}"""

print("\n--- CSS for index.html ---")
print(CSS)

page = (SITE / "index.html").read_text(encoding="utf-8")
need = [REST, "@keyframes otb-loop", f"{K_OUT:.3f}%", f"{K_GONE:.3f}%", 'class="tile"']
missing = [n for n in need if n not in page]
if missing:
    raise SystemExit(
        f"\nindex.html's mark animation is stale or absent: {missing}\n"
        f"Paste the CSS above into the <style> block and give the tile path "
        f'class="tile".')
print("\nindex.html's mark animation matches motion.py")
print(f"last frame matches the still mark to {worst:.1e} units")
