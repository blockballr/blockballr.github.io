"""Fetch the OffTheBlock typefaces and self-host them as woff2.

    python -m pip install "fonttools[woff]" brotli
    python brand/build-fonts.py

Chivo, Inter, and JetBrains Mono, from the Google Fonts repository. All three are
SIL Open Font License 1.1, which permits commercial use and embedding. Nothing
reaches a font CDN at runtime; tokens.css declares these files directly.

Chivo is the display face. It is a grotesque with square shoulders and a flat,
blunt black weight, which is what the mark wants next to it: the logo is built out
of right angles and a typeface with soft humanist bowls would argue with it.

JetBrains Mono is not decoration. This is a room where people paste contract
addresses, and a mono with a slashed zero and an unmistakable 1, l, and I is the
difference between reading an address and losing money to one.

Run this once. It is only needed again if a typeface changes.
"""
import io
import pathlib
import urllib.request

from fontTools.ttLib import TTFont

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl"

# Several candidate filenames per family: the axis order in a variable font's
# filename changes upstream now and then, and a stale guess would 404 rather than
# fail loudly. Take the first that resolves.
FAMILIES = [
    ("chivo", ["Chivo[wght].ttf"],
     "Chivo-Variable.woff2", "OFL-Chivo.txt"),
    ("inter", ["Inter[opsz,wght].ttf", "Inter[wght].ttf"],
     "Inter-Variable.woff2", "OFL-Inter.txt"),
    ("jetbrainsmono", ["JetBrainsMono[wght].ttf"],
     "JetBrainsMono-Variable.woff2", "OFL-JetBrainsMono.txt"),
]


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read()


def try_get(url):
    try:
        return get(url)
    except Exception:
        return None


FONTS.mkdir(parents=True, exist_ok=True)

for slug, candidates, out_name, licence_name in FAMILIES:
    blob = None
    for candidate in candidates:
        quoted = candidate.replace("[", "%5B").replace("]", "%5D")
        blob = try_get(f"{RAW}/{slug}/{quoted}")
        if blob:
            print(f"  {slug}: {candidate} ({len(blob) // 1024} KB)")
            break
    if not blob:
        raise SystemExit(f"none of {candidates} resolved under {RAW}/{slug}")

    font = TTFont(io.BytesIO(blob))
    axes = [a.axisTag for a in font["fvar"].axes] if "fvar" in font else []
    print(f"    axes: {axes or 'static'}")
    font.flavor = "woff2"
    font.save(FONTS / out_name)
    print(f"    -> {out_name}")

    (FONTS / licence_name).write_bytes(get(f"{RAW}/{slug}/OFL.txt"))
    print(f"    -> {licence_name}")

print("fonts written to", FONTS)
