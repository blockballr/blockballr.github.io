# OffTheBlock brand

OffTheBlock is blockballr's work and the place it is shown. The identity comes back
to one idea, and the name already contains it.

A block is the settled thing. It is public, it is final, and by the time something
is on it, everyone already has it. Alpha is whatever has not hit the block yet.
Off the block is where that gets said first. The line the identity was built
around is "Before it hits the block."

## The mark

A block with one piece off it. A square with a square notch bitten out of its
corner, and the piece that came out now clear of it, tilted.

Two properties carry the whole thing.

The first is the tilt. The block is orthogonal and the piece that left is not.
Every edge of the block sits at ninety degrees, because a block is settled. The
loose piece is tilted, because it is not. Set the tile square to the block and the
mark collapses into a square and a smaller square, tidily arranged, which says
nothing.

The second is the gap, and it is the one that is easy to lose. The piece has to
fully clear the notch it came out of. If it does not, the notch is covered and the
mark reads as a square with a tile stuck to its corner, which is an object with a
decoration rather than an object and its absence. The void is half the logo. So
the gap is not a distance that was nudged until it looked right; it is solved for
from the tilted tile's own bounding extent, and it holds at every size and every
tilt.

The tile is 44 per cent of the block, and that ceiling is deliberate rather than
aesthetic. The notch is the tile's own width taken out of the block's edge, so a
tile at half the block or more bites away more than half that edge, and what is
left stops reading as a square with a piece missing and starts reading as a plain
L. An L is a corner. The name is the block, so it has to read as one.

The cost of that ceiling is that the tile is small at small sizes, which is the
job the micro variant exists to do rather than a reason to compromise the primary
mark everywhere else.

## Colour

Three colours are the identity: asphalt, chalk, and signal. Asphalt is the block,
chalk is the ground, and signal is the piece that left. Nothing else appears inside
the mark.

Asphalt is `#14161B` and Chalk is `#F0EEE9`, a warm off-white rather than a pure
one. Signal is `#FF5A1F`. On a dark ground signal is lifted to `#FF7A45`, because
the base value goes heavy against near-black. Night, `#0B0C0F`, is the dark page
ground. Slate, `#5E6673`, carries secondary text, and lifts to `#9AA1AC` on dark.

Signal is ember orange, and that is a decision, not an accident. Every other room in
this market is navy, green, or violet, which is why they are all invisible next to
each other in a sidebar of circular avatars. A brand that cannot be picked out of
that list at sixteen pixels has failed at the only job the avatar has. Orange is
warm, it is loud, and nobody in this market owns it.

Signal has three values, because it has three jobs. `#FF5A1F` is the tile: a shape,
which only has to be seen, so it stays hot on any ground. `#FF7A45` is signal on a
dark ground, where the base value goes heavy against near-black. `#B33F0C` is the
deepened value, and it is the only one that may be used for accent *text* on a light
ground: the hot ember is 2.69 to 1 on chalk, which fails outright at body size, while
the deep one is 4.99 and passes. A link nobody can read is not a brand decision, it
is a bug.

That split is why the site carries two variables rather than one. `--accent` is
signal as text and has to hold contrast; `--tile` is signal as a shape in the mark
and only has to be seen. They part company on the light theme and nowhere else.

Signal is the strongest colour in the system, so spend it in one place at a time. It
belongs on the tile and on the one thing on a screen that is the alpha. It does not
belong on borders, headings, or general emphasis.

Semantic colour for success, warning, and error is a separate concern and is not
drawn from signal. Signal means "this is the alpha". If it also meant "this
worked", a filled order and a fresh call would be the same colour.

Every pairing in this document is checked rather than felt. Run
`python brand/geometry.py` and it prints the contrast table.

## Type

The wordmark and headings are Chivo, a grotesque with square shoulders and a flat,
blunt black weight. The mark is built out of right angles, and a typeface with soft
humanist bowls would argue with it. Body and interface text are Inter, a plain
workhorse. Anything that lines up in a column, and every contract address, is
JetBrains Mono with `font-variant-numeric: tabular-nums`.

The mono face is not decoration. People paste contract addresses here, and a mono
with a slashed zero and an unmistakable 1, l, and I is the difference between reading
an address and losing money to one.

All three are licensed under the SIL Open Font License, which permits commercial
use and embedding. They are self-hosted in `brand/fonts` as woff2, so nothing
reaches a font CDN at runtime. All three are variable, so one file covers every
weight.

The wordmark is one word with its internal capitals kept: OffTheBlock, not "Off The
Block" and not "offtheblock". It is a handle before it is a title. It is set in
Chivo at weight 800 with tracking pulled to negative 0.022em, because the name is
eleven letters and at default spacing it sprawls. It is a fixed piece of artwork
rather than live text, and `brand/logo` holds it already outlined, so it renders
with no font installed anywhere.

## Lockups

The horizontal lockup stands the block's foot on the word's baseline, so the mark
sits on the same line the type does rather than floating beside it.

Its gap is measured from the block's right edge, not from the mark's bounding box.
The bounding box is defined by the tile, which is up in the corner with nothing
underneath it, so spacing the word off the box opens a hole under the tile and the
lockup falls into two pieces. Measured off the block instead, the word closes up
and runs beneath the tile, and the tile's diagonal points into the name. The one
thing that must not happen is the tile touching the caps; that daylight is asserted
in the build rather than eyeballed, and the build fails if it closes.

The stacked lockup centres the word under the point the mark balances on, which is
38 per cent across, not the 50 per cent its bounding box claims. Almost all of the
mark's weight is block, thrown into one corner, with the tile as a small
counterweight thrown to the other. Centring on the box hangs the word off a point
with no ink anywhere near it, and it visibly leans.

## Sizes and crops

Every icon size is a different crop, and that is the entire job.

Telegram and Discord crop an avatar to a circle of the full width. The mark runs
corner to corner, so at full bleed the tile is the first thing the crop takes off,
and the logo ships as a plain square with a corner missing. A square bounding box
of side s only fits inside a circle of diameter D when s times root two is at most
D, so avatar artwork is scaled to the inscribed square. This is geometry, not
padding taste. Android's maskable icon has a safe circle of 80 per cent of the
width and gets the same treatment against that circle. iOS rounds the corners
itself and rejects transparency, so `apple-touch-icon.png` is a hard square with
the mark held well off the corners.

`build-icons.py` asserts this rather than trusting it: it counts the mark pixels
left outside each crop circle and reports zero.

Below 24 pixels, use the micro variant. The gap is the first thing to die: two and
a half units of daylight is under one device pixel at 16px, the block and the tile
fuse into a single grey lump, and the mark says nothing. Micro widens the gap,
grows the tile so it survives as more than a speck, and flattens the tilt, because
a fourteen degree rotation on a five pixel square rasterises to mush. The tilt
narrows but never closes and the gap widens but never fills, because those two are
the argument.

## Motion

The mark is already a before and an after. The tile starts in the notch, square and
flush, part of the block, and it ends clear of the block and tilted. The animation is
not a new idea laid on top of the logo, it is the interpolation between the logo's own
two states, and the build asserts that the last frame is the mark itself.

Two rules, and they are the same two rules the still mark has.

The block does not move. The block is the settled thing, which is what the word means,
and it is why the tile is the only thing in the mark that carries a tilt. Animate the
block and the mark stops making its argument.

The tile is not hinged. It turns about its own centre while it travels. Rotating it
about the block's corner would swing it, and a swing is a hinge, and a hinge is a lid.
This piece is not attached to anything, it came off.

The departure takes 0.9 seconds on a curve that overshoots slightly, so the piece
leaves fast, arrives, and settles a hair past where it lands. Position and rotation
ride the same curve, so it stops turning exactly when it stops travelling. Letting
those run on separate timings looks like two animations that happen to overlap. The
looping version holds the piece for a beat, lets it go, and shows the empty notch
before the next one comes off, because the empty notch is the point of the logo.

The standalone files animate themselves with SMIL, because they are used inside an
`<img>`, and an `<img>` is an isolated document that a host page's CSS cannot reach
into. The site's inline mark uses CSS instead, so it can be switched off for a reader
who has asked for reduced motion. SMIL cannot be, which is the whole reason the page
does not use it.

## Voice

Plain and direct. This is a room of people who can tell when they are being sold
to, so do not sell to them. Say the thing. Prefer concrete words: alpha, signal,
call, room, shipped. Avoid "ecosystem", "leveraging", "next-generation", and every
other word that survives only because nobody reads it.

The house line is "Before it hits the block." It explains the name and the product
in five words, which is the only reason to have a line at all.

## Files

`brand/geometry.py` is the mark as numbers and the single source every other script
reads. Nothing else decides what the mark looks like. Run it on its own and it
prints the mark's proportions, where it balances, and the contrast table.

`brand/build-fonts.py` fetches Chivo, Inter, and JetBrains Mono from the Google
Fonts repository and writes them as woff2 with their licences beside them. Run it
once.

`brand/build-marks.py` writes the five marks. `offtheblock-mark.svg` is the primary,
asphalt block and signal tile, for light grounds. `-knockout` puts chalk and lifted
signal on a dark ground. `-mono` inherits `currentColor` for single-colour use, and
the notch is what makes it survive: without it, two shapes in one colour say
nothing. `-micro` is the under-24px variant. `-solid` carries its own ground, for
avatars and app icons.

`brand/shaping.py` turns a string into an outlined path, shaping it with HarfBuzz so
the kerning is the font's own rather than something approximated by advancing each
glyph by its own width. Both the wordmark and the tagline on the social card go
through it, so there is one shaper rather than two that drift.

`brand/build-wordmark.py` instances Chivo at weight 800, shapes the name, bakes in
the brand's tracking, and writes the wordmark and both lockups as pure outlines.

`brand/build-icons.py` rasterises the icon set, the favicon, the maskable icon, and
the avatar through Chrome, then checks each circular crop.

`brand/build-art.py` draws the project art banners in the mark's own geometry, for
projects that have nothing deployed to screenshot.

`brand/build-og.py` draws the social card, the image that renders when someone pastes
the site into a chat. For a community whose whole distribution is a shared link, that
card is the first thing anyone sees of the brand, so it is built from the geometry
like everything else rather than being the avatar stretched to fit. It is a PNG at
1200 by 630, because every scraper reads PNG and none of them read SVG, and it is
referenced by an absolute URL, because none of them resolve a relative one.

`brand/motion.py` is the mark in motion as numbers, the way `geometry.py` is the mark
at rest. It holds the two states, the easing, and the timing, and it refuses to build
if the last frame is not the still mark.

`brand/build-motion.py` writes the animated logo as SVG, the social loop as GIF and
APNG, prints the CSS the site needs, and fails if the page has drifted from it.

`brand/build-site-assets.py` copies the fonts and icons the site needs, prints the
mark's inline SVG, and fails if the copy pasted into `index.html` has drifted from
`geometry.py`.

`brand/tokens.css` defines every colour and font stack as custom properties, with
the dark theme responding both to the operating system preference and to a
`data-theme` attribute on the root element. Import it once and read colours through
the tokens rather than hardcoding hex values.

The site is the repository root, because GitHub Pages serves `index.html` from there
and nowhere else, and `offtheblock-brand.pdf` is this document as a guide. The
generator ships in the same repository as the site it generates, so the two cannot
drift apart.

## Rules worth keeping

Do not rotate, recolour, or restyle the mark. Do not close the gap and do not
straighten the tile; those two are the logo. Do not put the signal tile on a signal
ground. Give the mark clear space on every side equal to the tile's width. Below 24
pixels use the micro variant. If the mark must appear in one colour, use the mono
file rather than filling both shapes by hand, because the notch and the gap are
what carry the meaning once the colour is gone.
