"""Rebuild the OffTheBlock icon set, avatar, and banner.

    python -m pip install pillow
    python brand/build-icons.py

Rasterises the mark through Chrome, because it is the renderer the artwork will
actually be seen in and it is already on the machine. Pillow then assembles the
.ico and writes the contact sheet.

Every size here is a different crop, and that is the whole job:

  favicon      a square, shown as drawn
  apple-touch  a square, corners rounded by iOS, so the corners cannot hold ink
  maskable     Android may crop to a circle of 80% of the width
  avatar       Telegram and Discord crop to a circle of the full width

The mark runs corner to corner, so a naive full-bleed placement loses the tile to
the first circular crop it meets. Each size below is scaled to fit the shape it is
actually cropped to. See CIRCLE_SAFE in geometry.py.
"""
import math
import pathlib
import subprocess
import tempfile
import time

from PIL import Image

from geometry import (BOX, CHALK, CIRCLE_SAFE, MICRO, NIGHT, NORMAL, SIGNAL_LIFT,
                      centre, shapes)

HERE = pathlib.Path(__file__).parent
ICON = HERE / "icon"
PNG = ICON / "png"
ASSETS = HERE.parent / "assets"

CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# How much of the frame the mark may occupy, per crop.
#   square   nothing is taken; leave a normal icon margin
#   rounded  iOS rounds the corners; keep the ink off them
#   circle   the full width becomes a circle: the inscribed square is 0.707
#   maskable Android's safe area is a circle of 80% of the width
FIT_SQUARE = 0.84
FIT_ROUNDED = 0.76
FIT_CIRCLE = CIRCLE_SAFE * 0.96          # a hair inside the inscribed square
FIT_MASKABLE = CIRCLE_SAFE * 0.80        # inscribed square of the 80% safe circle


def mark_svg(size, fit, ground, spec=NORMAL, block=CHALK, signal=SIGNAL_LIFT,
             radius=0):
    dx, dy = centre(spec)
    paint = {"block": block, "signal": signal}
    paths = "".join(f'<path d="{d}" fill="{paint[r]}"/>' for d, r in shapes(spec))
    off = BOX * (1 - fit) / 2
    rect = (f'<rect width="{BOX}" height="{BOX}" rx="{radius}" fill="{ground}"/>'
            if ground else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOX:g} {BOX:g}" '
            f'width="{size}" height="{size}">{rect}'
            f'<g transform="translate({off:.4f} {off:.4f}) scale({fit:.4f})">'
            f'<g transform="translate({dx:.4f} {dy:.4f})">{paths}</g></g></svg>')


def render(svg, w, h, out):
    """Chrome renders the SVG at exactly w by h, with no page chrome around it.

    Chrome refuses to open a window smaller than roughly 50px, so a 16px favicon
    cannot be screenshotted directly. The SVG is laid at the top-left of a roomier
    window at its true CSS size and the corner is cropped back out, which keeps the
    native rasterisation at the size the icon is actually used at. Rendering it big
    and scaling down would blur exactly the edges a 16px icon has left.
    """
    # Chrome also enforces a minimum window, so the window is always roomy and the
    # icon is cropped back out of its top-left corner.
    win_w, win_h = max(w + 64, 300), max(h + 64, 300)
    # The scratch page lives here, not in %TEMP%: headless Chrome on this machine
    # will not load a file:// page out of the temp directory and, true to form,
    # says nothing about it and exits 0.
    td = HERE / ".render"
    td.mkdir(exist_ok=True)
    if True:
        page = td / "i.html"
        shot = td / "s.png"
        if shot.exists():
            shot.unlink()
        page.write_text(
            '<!doctype html><meta charset="utf-8">'
            '<style>html,body{margin:0;padding:0;background:transparent;'
            'overflow:hidden}svg{display:block}</style>' + svg, encoding="utf-8")
        # Headless Chrome exits 0 whether or not it wrote the file, and on Windows
        # it intermittently does not. There is no error to catch and no exit code
        # to trust, so the only honest check is to look for the file, wait a moment
        # in case the write is still landing, and try again if it never does. A
        # silent miss here would ship an icon set with holes in it.
        for attempt in range(6):
            subprocess.run(
                [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                 "--hide-scrollbars", "--default-background-color=00000000",
                 "--force-device-scale-factor=1", f"--screenshot={shot}",
                 f"--window-size={win_w},{win_h}", page.as_uri()],
                timeout=90)
            for _ in range(20):
                if shot.exists() and shot.stat().st_size > 0:
                    break
                time.sleep(0.15)
            if shot.exists() and shot.stat().st_size > 0:
                break
            print(f"    chrome missed {out.name}, retry {attempt + 1}")
        else:
            raise SystemExit(f"chrome would not render {out} after 6 tries")
        Image.open(shot).convert("RGBA").crop((0, 0, w, h)).save(out)


PNG.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

# The web and PWA sizes. Under 24px the micro variant takes over, which is the
# only reason the 16px favicon reads as two shapes rather than one grey smudge.
for size in (16, 32, 48, 64, 128, 192, 256, 512):
    spec = MICRO if size < 24 else NORMAL
    radius = BOX * 0.16 if size >= 48 else 0     # a tile, not a chip, at tab sizes
    out = PNG / f"offtheblock-{size}.png"
    render(mark_svg(size, FIT_SQUARE, NIGHT, spec=spec, radius=radius), size, size, out)
    print(f"  offtheblock-{size}.png")

# iOS masks the corners itself and rejects transparency, so this one is a hard
# square and the mark stays well off the corners.
render(mark_svg(180, FIT_ROUNDED, NIGHT), 180, 180, PNG / "apple-touch-icon.png")
print("  apple-touch-icon.png")

# Android may crop this to a circle of 80% of the width.
render(mark_svg(512, FIT_MASKABLE, NIGHT), 512, 512, PNG / "maskable-512.png")
print("  maskable-512.png")

# Telegram and Discord crop to a circle of the full width. This is the file that
# would have lost its tile.
render(mark_svg(512, FIT_CIRCLE, NIGHT), 512, 512, ASSETS / "offtheblock-avatar.png")
print("  ../assets/offtheblock-avatar.png")

# favicon.ico carries the three sizes a browser actually asks for.
ims = [Image.open(PNG / f"offtheblock-{s}.png").convert("RGBA") for s in (16, 32, 48)]
ims[0].save(ICON / "favicon.ico", format="ICO",
            sizes=[(s, s) for s in (16, 32, 48)], append_images=ims[1:])
print("  favicon.ico")


def ground_rgb(hex_colour):
    return tuple(int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))


def mark_outside_circle(path, radius_frac=0.5):
    """Count pixels of *mark* left outside the crop circle.

    The ground is meant to be cropped away; it bleeds to the edges on purpose. The
    only thing that must not cross the circle is the mark itself, so this ignores
    anything that is still the background colour and counts what is left. Checking
    for "any ink" instead just counts the ground and always screams.

    This is the rule the whole icon set exists to obey, so it is tested rather than
    trusted. If the tile pokes out, Telegram shaves it off and the mark ships as a
    plain square with a corner missing.
    """
    im = Image.open(path).convert("RGB")
    w, h = im.size
    r, cx, cy = w * radius_frac, w / 2, h / 2
    bg = ground_rgb(NIGHT)
    px = im.load()
    outside = 0
    for y in range(h):
        for x in range(w):
            if math.hypot(x - cx + 0.5, y - cy + 0.5) > r:
                p = px[x, y]
                if sum(abs(a - b) for a, b in zip(p, bg)) > 24:
                    outside += 1
    return outside


print()
for label, path, frac in (
        ("avatar (circle crop, full width)", ASSETS / "offtheblock-avatar.png", 0.5),
        ("maskable (Android safe circle, 80%)", PNG / "maskable-512.png", 0.4)):
    bad = mark_outside_circle(path, frac)
    print(f"  {label:38} {bad:>5} px of mark outside "
          f"-> {'CLIPS' if bad else 'clean'}")

print("\nicons written to", PNG)
