# blockballr.github.io

The OffTheBlock site, and the brand it is built from. Static, no build step, no
dependencies at runtime. Open `index.html` and it runs. Live at
https://blockballr.github.io.

The repository is named `blockballr.github.io`, so GitHub Pages serves it from the
root of this branch with nothing to configure. `index.html`, `fonts/`, and `img/`
are the site. Everything else is source.

The live URL is written into three places that a scraper reads and a person does
not: the canonical tag, the `og:image` and `twitter:image` URLs, and the line printed
along the bottom of the social card. If the site ever moves, grep for
`blockballr.github.io` and rebuild the card, or the link preview will keep pointing
at an address that is no longer there.

## Layout

`index.html` is the whole page: markup, styles, and the terminal script in one file,
because it is one page and a build step for one page is a build step to maintain.

`fonts/` and `img/` are what the page loads. Both are generated. Do not hand-edit
anything in `img/`; the files say so at the top.

`brand/` is where the mark comes from. It is the generator, not a folder of exports.
`brand/geometry.py` holds the mark as numbers and every other script reads it, so
changing the geometry changes the logo, the icons, the social card, the art, and the
PDF guide together. The generator lives in this repository rather than on somebody's
desktop precisely so the site cannot drift from the brand.

`brand.md` is the brand in prose and `offtheblock-brand.pdf` is the same thing as a
guide, generated from the geometry so it cannot lie about its own numbers.

`.nojekyll` stops GitHub Pages putting the files through Jekyll, which is a build
step nobody here asked for.

## Rebuilding

Run these from the repository root. They need Python with `pillow`, `fonttools`,
`brotli`, and `uharfbuzz`, and they rasterise through the Chrome already on the
machine.

    python brand/build-marks.py         the five logo files
    python brand/build-wordmark.py      the wordmark and lockups, as outlines
    python brand/build-icons.py         favicon, apple-touch, maskable, avatar
    python brand/build-art.py           the art banners for unshipped projects
    python brand/build-og.py            the social card
    python brand/build-motion.py        the animated logo, and the social loop
    python brand/build-site-assets.py   copies fonts and icons in, checks the page
    python brand/build-guide.py         the PDF

`build-site-assets.py` is the one to run after any change to the mark. The page
inlines the mark rather than linking it, because an `<img>` is an isolated document
and cannot see `var(--text)`, so the two paths are pasted into `index.html`, and a
pasted path is a path that can silently drift. That script prints the correct
snippet and fails loudly if what is in the page no longer matches `geometry.py`.

## What is on the page

The hero is the brand line, "Before it hits the block", which explains the name, and
a first-person lede. This is one person's site, not a community's, so there is no
panel selling a room to join: just the work, and two ways to reach him.

The work section is driven by what is actually public on GitHub, and it treats a
shipped project and an unshipped one differently on purpose.

A project with a deployment gets a preview window: a browser frame with a real
screenshot of the running app, a live badge, and the whole card is a link through to
it. HandGloss is the only one of these today.

A project with no deployment has nothing to screenshot, so it gets a drawing
instead. Those are in `img/art-*.svg` and they are generated, not stock: each one is
the logo's own vocabulary, a field of blocks with one piece off the block, bent to
say what that project does. Radar sweeps a field and lights the one that is not like
the others. The card links to the source.

That distinction is the point of the section. A card that says "no screenshot yet"
is a hole in a page. A card drawn in the mark's geometry is a card, and the page
reads as one thing rather than a live project and an apology.

## The terminal

Kept, because it was the good part of the old site, and rewritten, because it used
to fill a fake progress bar and then admit it could not think of anything to say.

It now runs a session that says what the room is: who is here, what the rule is, and
what it is watching for. The progress bar survives, but it now belongs to a command
that has a reason to take a moment.

It does not start until it is scrolled into view and it stops when it scrolls away,
because a typewriter nobody is looking at is a timer holding the main thread open. A
reader who has asked for reduced motion gets the finished session printed rather
than typed.

The script is the `script` array near the bottom of `index.html`. Edit that array to
change what the terminal says; everything else follows from it.

## The link preview

The way people arrive here is somebody pasting the link into a Telegram room, so the
social card is the first thing they see of the brand. It is `img/og.png`, drawn by
`brand/build-og.py` in the mark's own geometry.

Two things about it are load-bearing and are easy to undo by accident. The
`og:image` is an absolute URL, because no scraper resolves a relative one, and it is
a PNG, because no scraper reads SVG. Point it at a relative path or at the SVG and
the preview renders with no image at all, silently, which is the same as having no
brand.

## Motion

The header mark loops. A piece comes off the block, is held, goes, and the notch sits
empty for a beat before the next one comes off. The empty notch is the point of the
logo, so the loop is built to show it rather than to hide the reset.

It is CSS, generated by `brand/build-motion.py` from the mark's own geometry, and the
build fails if the page drifts from it. It pauses on hover, because a logo that never
stops moving is a logo nobody can read, and it does not run at all for a reader who
has asked for reduced motion.

The reset is the one piece of sleight of hand: the tile snaps back into its notch
while its opacity is zero. Animating it home would show a piece returning to the
block, which is the opposite of what the mark says.

The standalone animated files are in `brand/logo` (SVG, self-animating, usable in an
`<img>`) and `brand/motion` (a GIF and an APNG of the loop, for posting). Only the
tile ever moves. The block is the settled thing, and that is the entire argument of
the logo.

## Adding a project

The cards are plain HTML in the `.grid`. Copy a card and change it.

Use the preview-window card when there is a URL to open, and put a real screenshot
in `img/`. Capture one with:

    chrome --headless=new --screenshot=img/name.png --window-size=1280,800 <url>

Use the art card when there is only source. Add a drawing to `brand/build-art.py`
rather than reaching for a stock illustration, or the page stops being one thing.

Faultline is on the profile README but is not a public repository, so it is not on
the page. OffTheBlockBot was dropped for the same reason: the repository is under an
org that is no longer reachable and it is empty. When either goes public under
`blockballr`, it is one more card.
