"""Render the OffTheBlock brand guide to PDF.

    python brand/build-guide.py

Builds an HTML guide and prints it through headless Chrome. Every colour, every
proportion, and every contrast figure on the page is pulled from geometry.py at
build time rather than typed in, so the guide cannot drift from the artwork it
documents. If the mark changes, the guide changes with it.
"""
import pathlib
import subprocess
import time

from geometry import (ASPHALT, BOX, CHALK, CIRCLE_SAFE, MICRO, NIGHT, NORMAL,
                      SIGNAL, SIGNAL_LIFT, SLATE, SLATE_LIFT, WHITE, balance,
                      block_path, centre, contrast, extent, ink, shapes, tile_path)

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "offtheblock-brand.pdf"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FONTS = (HERE / "fonts").as_uri()

B, T, GAP, TILT = NORMAL
IX, IY, IW, IH = ink(NORMAL)
BAL_X, BAL_Y = balance(NORMAL)


def mark(size, block, signal, spec=NORMAL, ground=None, fit=1.0):
    dx, dy = centre(spec)
    paint = {"block": block, "signal": signal}
    paths = "".join(f'<path d="{d}" fill="{paint[r]}"/>' for d, r in shapes(spec))
    off = BOX * (1 - fit) / 2
    rect = f'<rect width="{BOX}" height="{BOX}" fill="{ground}"/>' if ground else ""
    return (f'<svg viewBox="0 0 {BOX:g} {BOX:g}" width="{size}" height="{size}">{rect}'
            f'<g transform="translate({off:.3f} {off:.3f}) scale({fit:.4f})">'
            f'<g transform="translate({dx:.3f} {dy:.3f})">{paths}</g></g></svg>')


def swatch(name, hexv, on, note):
    c = contrast(hexv, on)
    verdict = "body text" if c >= 4.5 else ("display only" if c >= 3.0 else "shapes only")
    return f"""
    <div class="sw">
      <div class="chip" style="background:{hexv}"></div>
      <div class="swb">
        <b>{name}</b>
        <code>{hexv.upper()}</code>
        <span>{note}</span>
        <em>{c:.2f}:1 on {'chalk' if on == CHALK else 'night'} &middot; {verdict}</em>
      </div>
    </div>"""


CONTRASTS = [
    ("Signal on chalk", SIGNAL, CHALK),
    ("Signal lift on night", SIGNAL_LIFT, NIGHT),
    ("Asphalt on chalk", ASPHALT, CHALK),
    ("Chalk on night", CHALK, NIGHT),
    ("Slate on chalk", SLATE, CHALK),
    ("Slate lift on night", SLATE_LIFT, NIGHT),
]
rows = ""
for label, a, bg in CONTRASTS:
    c = contrast(a, bg)
    v = "body" if c >= 4.5 else ("display only" if c >= 3.0 else "shapes only")
    cls = "" if c >= 4.5 else ("warn" if c >= 3.0 else "bad")
    rows += (f'<tr><td>{label}</td><td class="n">{c:.2f}:1</td>'
             f'<td class="{cls}">{v}</td></tr>')

HTML = f"""<!doctype html><meta charset="utf-8"><title>OffTheBlock brand</title>
<style>
@font-face{{font-family:"Chivo";src:url("{FONTS}/Chivo-Variable.woff2") format("woff2-variations");font-weight:100 900}}
@font-face{{font-family:"Inter";src:url("{FONTS}/Inter-Variable.woff2") format("woff2-variations");font-weight:100 900}}
@font-face{{font-family:"JetBrains Mono";src:url("{FONTS}/JetBrainsMono-Variable.woff2") format("woff2-variations");font-weight:100 800}}
@page{{size:A4;margin:17mm 16mm}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Inter",sans-serif;color:{ASPHALT};font-size:10pt;line-height:1.62;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
h1,h2,h3{{font-family:"Chivo",sans-serif;letter-spacing:-.022em;font-weight:800;margin:0}}
.page{{page-break-after:always}}
.page:last-child{{page-break-after:auto}}
p{{margin:0 0 10px}}
.dim{{color:{SLATE}}}
code,.mono{{font-family:"JetBrains Mono",monospace;font-size:8.5pt}}

/* cover */
.cover{{height:252mm;display:flex;flex-direction:column;justify-content:space-between;
  background:{NIGHT};color:{CHALK};margin:-17mm -16mm;padding:20mm 16mm}}
.cover h1{{font-size:42pt;line-height:1.02;margin:0}}
.cover .sig{{color:{SIGNAL_LIFT}}}
.cover .lede{{color:{SLATE_LIFT};max-width:78mm;margin-top:6mm;font-size:10.5pt}}
.cover .foot{{display:flex;justify-content:space-between;align-items:flex-end;
  color:{SLATE_LIFT};font-family:"JetBrains Mono",monospace;font-size:8pt}}

h2{{font-size:19pt;margin:0 0 2mm}}
.kicker{{font-family:"JetBrains Mono",monospace;font-size:7.5pt;letter-spacing:.16em;
  text-transform:uppercase;color:{SIGNAL};margin:0 0 2mm}}
.rule{{height:1px;background:#dcd9d3;margin:5mm 0}}
h3{{font-size:11.5pt;margin:6mm 0 2mm}}

.row{{display:flex;gap:8mm;align-items:center}}
.box{{border:1px solid #dcd9d3;border-radius:3px;padding:6mm;text-align:center}}
.box.dark{{background:{NIGHT};border-color:#262a31}}
.cap{{font-family:"JetBrains Mono",monospace;font-size:7pt;color:{SLATE};
  letter-spacing:.06em;margin-top:3mm;text-transform:uppercase}}
.box.dark .cap{{color:{SLATE_LIFT}}}

.sw{{display:flex;gap:4mm;align-items:center;margin-bottom:3.5mm}}
.chip{{width:17mm;height:17mm;border-radius:3px;border:1px solid rgba(0,0,0,.14);flex:none}}
.swb{{display:flex;flex-direction:column;line-height:1.45}}
.swb b{{font-family:"Chivo",sans-serif;font-size:10.5pt}}
.swb code{{color:{SLATE}}}
.swb span{{font-size:9pt}}
.swb em{{font-family:"JetBrains Mono",monospace;font-size:7.5pt;color:{SLATE};font-style:normal}}

table{{width:100%;border-collapse:collapse;font-size:9pt}}
th,td{{text-align:left;padding:2.2mm 2mm;border-bottom:1px solid #e6e3dd}}
th{{font-family:"JetBrains Mono",monospace;font-size:7pt;letter-spacing:.1em;
  text-transform:uppercase;color:{SLATE};font-weight:400}}
td.n{{font-family:"JetBrains Mono",monospace}}
td.warn{{color:#a8720c}}
td.bad{{color:#c0392b}}

.two{{display:flex;gap:7mm}}
.two>*{{flex:1}}
.note{{border-left:2px solid {SIGNAL};padding-left:4mm;color:{SLATE};font-size:9pt}}
.spec{{font-family:"JetBrains Mono",monospace;font-size:8pt;color:{SLATE};
  background:#f4f2ee;border-radius:3px;padding:3mm 4mm;line-height:1.7}}
.wrong{{border:1px solid #e8c9c9;background:#fdf6f6;border-radius:3px;padding:4mm;text-align:center}}
.right{{border:1px solid #cbe4d5;background:#f5faf7;border-radius:3px;padding:4mm;text-align:center}}
.verdict{{font-family:"JetBrains Mono",monospace;font-size:7.5pt;letter-spacing:.08em;
  text-transform:uppercase;margin-top:2.5mm}}
.verdict.no{{color:#c0392b}}
.verdict.yes{{color:#2e7d51}}
.type-spec{{font-family:"Chivo",sans-serif;font-weight:800;letter-spacing:-.022em;line-height:1}}
</style>

<!-- ============================================================= cover -->
<div class="page">
  <div class="cover">
    <div>
      {mark(96, CHALK, SIGNAL_LIFT)}
      <h1 style="margin-top:14mm">Before it hits<br>the <span class="sig">block</span>.</h1>
      <p class="lede">A block is the settled thing. Public, final, already priced
      in. Alpha is what has not landed on it yet. This is the room where it gets
      said first.</p>
    </div>
    <div class="foot"><span>OffTheBlock &middot; brand guide</span><span>v1</span></div>
  </div>
</div>

<!-- ============================================================= the idea -->
<div class="page">
  <p class="kicker">01 &middot; The idea</p>
  <h2>A block, with one piece off it</h2>
  <div class="rule"></div>

  <p>The name already contains the idea. A block is public, final, and by the time
  something is on it, everyone already has it. Alpha is whatever has not hit the
  block yet. Off the block is where that gets said first.</p>

  <p>So the mark is a square with a square notch bitten out of its corner, and the
  piece that came out is now clear of it, tilted. Two properties carry the whole
  thing, and both of them are the kind that quietly disappear if nobody writes
  them down.</p>

  <h3>One: the block is orthogonal, the piece that left is not</h3>
  <p>Every edge of the block sits at ninety degrees, because a block is settled.
  The loose piece is tilted {TILT:g} degrees, because it is not.</p>

  <div class="row" style="margin:5mm 0">
    <div class="wrong" style="flex:1">
      {mark(70, ASPHALT, SIGNAL, spec=(B, T, GAP, 0.0))}
      <div class="verdict no">Tilt removed &middot; says nothing</div>
    </div>
    <div class="right" style="flex:1">
      {mark(70, ASPHALT, SIGNAL)}
      <div class="verdict yes">The mark</div>
    </div>
  </div>
  <p class="note">Set the tile square to the block and it collapses into a square
  and a smaller square, tidily arranged. The tilt is the argument.</p>

  <h3>Two: the piece must clear the hole it came out of</h3>
  <p>The void is half the logo. If the tile does not fully clear its notch, the
  notch is covered and the mark reads as a square with a tile stuck on it: an
  object with a decoration, rather than an object and its absence.</p>

  <div class="row" style="margin:5mm 0">
    <div class="wrong" style="flex:1">
      {mark(70, ASPHALT, SIGNAL, spec=(B, T, -9.0, TILT))}
      <div class="verdict no">Gap closed &middot; the void is gone</div>
    </div>
    <div class="right" style="flex:1">
      {mark(70, ASPHALT, SIGNAL)}
      <div class="verdict yes">The mark</div>
    </div>
  </div>
  <p class="note">So the gap is not a distance that was nudged until it looked
  right. It is solved for from the tilted tile's own bounding extent, which is why
  it holds at every size and every tilt.</p>
</div>

<!-- ============================================================= geometry -->
<div class="page">
  <p class="kicker">02 &middot; Geometry</p>
  <h2>The mark, as numbers</h2>
  <div class="rule"></div>

  <div class="two">
    <div>
      <p>Everything is derived from four numbers. The build scripts read them from
      <code>geometry.py</code>; nothing else decides what the mark looks like.</p>
      <div class="spec">
        block &nbsp;{B:g}<br>
        tile &nbsp;&nbsp;{T:g} &nbsp;({T / B:.0%} of the block)<br>
        gap &nbsp;&nbsp;&nbsp;{GAP:g} &nbsp;(guaranteed, both axes)<br>
        tilt &nbsp;&nbsp;{TILT:g}&deg;<br>
        <br>
        ink &nbsp;&nbsp;&nbsp;{IW:.2f} &times; {IH:.2f} &nbsp;(square)<br>
        balance {BAL_X:.1%} across, {BAL_Y:.1%} down
      </div>
      <p style="margin-top:4mm">The ink comes out exactly square, and not by luck:
      the block runs back from its corner and the tile runs forward from it by the
      same extent plus the gap in both axes.</p>
    </div>
    <div class="box" style="flex:none;width:62mm">
      {mark(120, ASPHALT, SIGNAL)}
      <div class="cap">Primary</div>
    </div>
  </div>

  <h3>Why the tile stops at {T / B:.0%} of the block</h3>
  <p>The notch is the tile's own width taken out of the block's edge. A tile at
  half the block or more bites away more than half that edge, and what is left
  stops reading as a square with a piece missing. It becomes a plain L. An L is a
  corner. The name is the block, so it has to read as one.</p>

  <div class="row" style="margin:5mm 0">
    <div class="wrong" style="flex:1">
      {mark(62, ASPHALT, SIGNAL, spec=(30.0, 20.0, GAP, TILT))}
      <div class="verdict no">Tile at 67% &middot; reads as an L</div>
    </div>
    <div class="right" style="flex:1">
      {mark(62, ASPHALT, SIGNAL)}
      <div class="verdict yes">Tile at {T / B:.0%} &middot; reads as a block</div>
    </div>
  </div>

  <h3>The micro variant, below 24px</h3>
  <p>The gap is the first thing to die. At 16px, {GAP:g} units of daylight is under
  one device pixel: the block and the tile fuse into one grey lump and the mark
  says nothing. Micro widens the gap, grows the tile so it survives as more than a
  speck, and flattens the tilt, because a {TILT:g} degree rotation on a five pixel
  square rasterises to mush. The tilt narrows but never closes and the gap widens
  but never fills, because those two are the argument.</p>

  <div class="row">
    <div class="box"><div style="display:flex;gap:5mm;align-items:flex-end">
      {mark(32, ASPHALT, SIGNAL, spec=MICRO)}{mark(24, ASPHALT, SIGNAL, spec=MICRO)}{mark(16, ASPHALT, SIGNAL, spec=MICRO)}
    </div><div class="cap">Micro &middot; 32 / 24 / 16</div></div>
    <div class="box"><div style="display:flex;gap:5mm;align-items:flex-end">
      {mark(32, ASPHALT, SIGNAL)}{mark(24, ASPHALT, SIGNAL)}{mark(16, ASPHALT, SIGNAL)}
    </div><div class="cap">Primary at the same sizes</div></div>
  </div>
</div>

<!-- ============================================================= colour -->
<div class="page">
  <p class="kicker">03 &middot; Colour</p>
  <h2>Asphalt, chalk, signal</h2>
  <div class="rule"></div>

  <p>Asphalt is the block, chalk is the ground, and signal is the piece that left.
  Nothing else appears inside the mark.</p>

  <div class="two" style="margin-top:5mm">
    <div>
      {swatch("Asphalt", ASPHALT, CHALK, "The block. Sets type on light grounds.")}
      {swatch("Chalk", CHALK, NIGHT, "The ground. A warm off-white, not a pure one.")}
      {swatch("Signal", SIGNAL, CHALK, "The alpha. One place at a time.")}
    </div>
    <div>
      {swatch("Signal lift", SIGNAL_LIFT, NIGHT, "Signal on dark grounds.")}
      {swatch("Night", NIGHT, CHALK, "The dark page ground.")}
      {swatch("Slate", SLATE, CHALK, "Secondary text.")}
    </div>
  </div>

  <h3>Why hot pink</h3>
  <p>Every other room in this market is navy and green, which is why none of them
  can be told apart in a sidebar of circular avatars. A brand that cannot be picked
  out of that list at sixteen pixels has failed at the only job the avatar has.
  Signal is a decision, not an accident.</p>

  <h3>Contrast, checked rather than felt</h3>
  <table>
    <tr><th>Pairing</th><th>Ratio</th><th>Safe for</th></tr>
    {rows}
  </table>
  <p class="note" style="margin-top:4mm">Signal on chalk is
  {contrast(SIGNAL, CHALK):.2f} to 1. That is fine for the tile, which is a shape
  rather than something to be read, and fine for display type. Signal at body size
  on a light ground fails. Set it large, or set it on asphalt.</p>

  <h3>Semantic colour is not drawn from signal</h3>
  <p>Signal means "this is the alpha". If it also meant "this worked", a filled
  order and a fresh call would be the same colour.</p>
</div>

<!-- ============================================================= type -->
<div class="page">
  <p class="kicker">04 &middot; Type</p>
  <h2>Chivo, Inter, JetBrains Mono</h2>
  <div class="rule"></div>

  <div class="type-spec" style="font-size:34pt">OffTheBlock</div>
  <p class="dim mono" style="margin-top:2mm">Chivo 800 &middot; tracking -0.022em &middot; outlined, no font required</p>

  <p style="margin-top:5mm">The wordmark is one word with its internal capitals
  kept. It is a handle before it is a title, so it is not "Off The Block" and it is
  not "offtheblock". The tracking is pulled in because the name is eleven letters
  and at default spacing it sprawls.</p>

  <h3>Chivo, for the wordmark and headings</h3>
  <p>A grotesque with square shoulders and a flat, blunt black weight. The mark is
  built out of right angles, and a typeface with soft humanist bowls would argue
  with it.</p>

  <h3>Inter, for body and interface</h3>
  <p style="font-size:11pt">A plain workhorse. It gets out of the way, which is the
  entire job.</p>

  <h3>JetBrains Mono, for anything that lines up</h3>
  <p class="mono" style="font-size:11pt">0O 1lI &middot; So1anaVsPh...9xKq &middot; 1,284.05</p>
  <p>This is not decoration. This is a room where people paste contract addresses,
  and a mono with a slashed zero and an unmistakable 1, l, and I is the difference
  between reading an address and losing money to one. Columns of figures take
  <code>tabular-nums</code>, or a price list jitters as its digits change.</p>

  <p class="note" style="margin-top:5mm">All three are SIL Open Font License, which
  permits commercial use and embedding. They are self-hosted as woff2, so nothing
  reaches a font CDN at runtime. All three are variable, so one file covers every
  weight.</p>
</div>

<!-- ============================================================= lockups -->
<div class="page">
  <p class="kicker">05 &middot; Lockups</p>
  <h2>Where the word goes</h2>
  <div class="rule"></div>

  <div class="box" style="text-align:left;padding:7mm">
    <img src="{(HERE / 'logo' / 'offtheblock-lockup-horizontal.svg').as_uri()}" style="height:15mm">
    <div class="cap">Horizontal</div>
  </div>

  <p style="margin-top:5mm">The block's foot stands on the word's baseline, so the
  mark sits on the same line the type does rather than floating beside it.</p>

  <p>The gap is measured from the block's right edge, not from the mark's bounding
  box. The bounding box is defined by the tile, which is up in the corner with
  nothing underneath it, so spacing the word off the box opens a hole under the
  tile and the lockup falls into two pieces. Measured off the block instead, the
  word closes up and runs beneath the tile, and the tile's diagonal points into the
  name. The tile must never touch the caps; that daylight is asserted in the build,
  and the build fails if it closes.</p>

  <div class="row" style="margin-top:6mm">
    <div class="box" style="flex:1">
      <img src="{(HERE / 'logo' / 'offtheblock-lockup-stacked.svg').as_uri()}" style="height:24mm">
      <div class="cap">Stacked</div>
    </div>
    <div class="box dark" style="flex:1">
      <img src="{(HERE / 'logo' / 'offtheblock-lockup-horizontal-knockout.svg').as_uri()}" style="height:11mm">
      <div class="cap">Knockout</div>
    </div>
  </div>

  <h3>The stacked lockup does not centre on the bounding box</h3>
  <p>The mark balances at {BAL_X:.0%} across, not the 50% its bounding box claims.
  Almost all of its weight is block, thrown into one corner, with the tile as a
  small counterweight thrown to the other. Centring the word on the box hangs it
  off a point with no ink anywhere near it, and it visibly leans.</p>
</div>

<!-- ============================================================= crops -->
<div class="page">
  <p class="kicker">06 &middot; Sizes and crops</p>
  <h2>Every size is a different crop</h2>
  <div class="rule"></div>

  <p>Telegram and Discord crop an avatar to a circle of the full width. The mark
  runs corner to corner, so at full bleed the tile is the first thing the crop takes
  off, and the logo ships as a plain square with a corner missing.</p>

  <div class="row" style="margin:5mm 0">
    <div class="wrong" style="flex:1">
      <div style="width:26mm;height:26mm;border-radius:50%;overflow:hidden;margin:0 auto">
        {mark(98, CHALK, SIGNAL_LIFT, ground=NIGHT, fit=1.0)}
      </div>
      <div class="verdict no">Full bleed &middot; the tile is shaved off</div>
    </div>
    <div class="right" style="flex:1">
      <div style="width:26mm;height:26mm;border-radius:50%;overflow:hidden;margin:0 auto">
        {mark(98, CHALK, SIGNAL_LIFT, ground=NIGHT, fit=CIRCLE_SAFE * 0.96)}
      </div>
      <div class="verdict yes">Scaled to the inscribed square</div>
    </div>
  </div>

  <p>A square bounding box of side <em>s</em> only fits inside a circle of diameter
  <em>D</em> when <em>s</em> &times; &radic;2 &le; <em>D</em>. So avatar artwork is
  scaled to {CIRCLE_SAFE:.3f} of the frame. This is geometry, not padding taste.</p>

  <div class="spec" style="margin:5mm 0">
    favicon &nbsp;&nbsp;&nbsp;a square, shown as drawn<br>
    apple-touch &nbsp;a square; iOS rounds the corners, so they hold no ink<br>
    maskable &nbsp;&nbsp;&nbsp;&nbsp;Android may crop to a circle of 80% of the width<br>
    avatar &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Telegram and Discord crop to a circle of the full width
  </div>

  <p class="note"><code>build-icons.py</code> asserts this rather than trusting it:
  it counts the mark pixels left outside each crop circle and reports zero. A silent
  miss here ships a broken avatar to every member of the room.</p>

  <h3>Clear space</h3>
  <p>Give the mark clear space on every side equal to the tile's width.</p>
</div>

<!-- ============================================================= rules -->
<div class="page">
  <p class="kicker">07 &middot; Voice and rules</p>
  <h2>How it talks</h2>
  <div class="rule"></div>

  <p>Plain and direct. This is a room of people who can tell when they are being
  sold to, so do not sell to them. Say the thing. Prefer concrete words: alpha,
  signal, call, room, shipped. Avoid "ecosystem", "leveraging", "next-generation",
  and every other word that survives only because nobody reads it.</p>

  <p>The house line is <b>"Before it hits the block."</b> It explains the name and
  the product in five words, which is the only reason to have a line at all.</p>

  <h2 style="margin-top:9mm">Rules worth keeping</h2>
  <div class="rule"></div>
  <ul style="padding-left:5mm;margin:0">
    <li>Do not rotate, recolour, or restyle the mark.</li>
    <li>Do not close the gap and do not straighten the tile. Those two are the logo.</li>
    <li>Do not put the signal tile on a signal ground.</li>
    <li>Clear space on every side equal to the tile's width.</li>
    <li>Below 24px, use the micro variant.</li>
    <li>One colour? Use the mono file, and let the notch and the gap carry it.</li>
    <li>Signal goes in one place at a time. It is the alpha, not an accent.</li>
    <li>Never draw semantic colour out of signal.</li>
  </ul>

  <div class="rule" style="margin-top:9mm"></div>
  <p class="dim mono" style="font-size:8pt">Every figure in this guide is read from
  brand/geometry.py at build time. Change the mark and the guide changes
  with it. Rebuild: python brand/build-guide.py</p>
</div>
"""

page = HERE / ".guide.html"
page.write_text(HTML, encoding="utf-8")

if OUT.exists():
    OUT.unlink()

# Chrome exits before it has finished flushing the PDF, and it exits 0 either way.
# Retrying too eagerly starts a second Chrome that races the first one onto the same
# path, and what lands is a truncated file that still looks like a PDF. So: wait
# generously, and only then try again. The guide embeds three fonts and several
# images, so a file of a few KB is a failure wearing a success's clothes.
FLOOR = 120_000
for attempt in range(4):
    subprocess.run(
        [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", f"--print-to-pdf={OUT}", page.as_uri()],
        timeout=240)
    size = 0
    for _ in range(150):                       # up to 30s for the write to settle
        if OUT.exists():
            grown = OUT.stat().st_size
            if grown == size and size > FLOOR:
                break                          # stopped growing, and big enough
            size = grown
        time.sleep(0.2)
    if OUT.exists() and OUT.stat().st_size > FLOOR:
        break
    print(f"  pdf came out at {size} bytes, under the {FLOOR} floor. "
          f"retry {attempt + 1}")
else:
    raise SystemExit("chrome would not print a complete guide")

if not OUT.read_bytes().rstrip().endswith(b"%%EOF"):
    raise SystemExit(f"{OUT} is truncated: no %%EOF marker")

page.unlink()
print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB)")
