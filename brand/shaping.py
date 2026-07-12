"""Turn a string into an outlined SVG path.

The brand ships artwork that renders with no font installed anywhere, which means
every piece of type in a fixed asset has to become a path. Two things need that:
the wordmark, and the tagline on the social card. This is the machinery both use,
so there is one shaper rather than two that drift.

HarfBuzz does the shaping so the kerning is the font's own rather than something
approximated by advancing each glyph by its own width. Chivo kerns its own capitals
and the name is three of them jammed together, so this is not a subtlety.
"""
import pathlib

import uharfbuzz as hb
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = pathlib.Path(__file__).parent


def outline(text, src, weight, tracking_em=0.0, verbose=False):
    """Shape `text` and return (svg path data, (xmin, ymin, xmax, ymax)).

    The path lands in SVG space with the baseline at y=0, so a caller positions it
    by its baseline and does not have to care about the font's metrics.

    `src` is a variable woff2. It is instanced to `weight` first: HarfBuzz cannot
    read woff2 and will not apply a variation axis, so shaping the source directly
    would silently return the default weight.
    """
    font = TTFont(src)
    axes = {a.axisTag: (a.minValue, a.maxValue) for a in font["fvar"].axes}
    lo, hi = axes["wght"]
    loc = {"wght": min(max(weight, lo), hi)}  # clamp rather than fail on a bad guess
    if verbose:
        print(f"  axes {axes}")
        print(f"  instancing at {loc}")

    static = instancer.instantiateVariableFont(font, loc)
    # The source is woff2 and the flavor rides along. Drop it and write a plain TTF,
    # because HarfBuzz cannot read a compressed one.
    static.flavor = None
    tmp = HERE / f".{pathlib.Path(src).stem}-{int(loc['wght'])}.ttf"
    static.save(tmp)

    try:
        f = TTFont(tmp)
        upem = f["head"].unitsPerEm
        glyphs = f.getGlyphSet()
        order = f.getGlyphOrder()

        hb_font = hb.Font(hb.Face(hb.Blob(tmp.read_bytes())))
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf, {"kern": True, "liga": True})

        tracking = tracking_em * upem
        pen = SVGPathPen(glyphs)
        bounds = BoundsPen(glyphs)

        x = 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = order[info.codepoint]
            # Flip y so the path lands in SVG space with the baseline at zero.
            t = Transform(1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)
            glyphs[name].draw(TransformPen(pen, t))
            glyphs[name].draw(TransformPen(bounds, t))
            x += pos.x_advance + tracking
    finally:
        tmp.unlink(missing_ok=True)

    return pen.getCommands(), bounds.bounds


if __name__ == "__main__":
    path, (x0, y0, x1, y1) = outline(
        "OffTheBlock", HERE / "fonts" / "Chivo-Variable.woff2", 800, -0.022)
    print(f"OffTheBlock in Chivo 800: {len(path)} chars of path, "
          f"ink {x1 - x0:.0f} x {y1 - y0:.0f} units, ascent {-y0:.0f}")
