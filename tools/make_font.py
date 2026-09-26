"""Build an Arabic-capable fallback font for Risk of Rain 2.

Takes the game's own NotoSans-Regular (the TrueType source behind the ROOT TMP
font asset) and merges Noto Sans Arabic into it, keeping the game font's
vertical metrics so line spacing is unchanged.

The result is used as the source font of the *already dynamic* fallback asset
(NotoSansCJKsc-Regular SDF (Dynamic)); TMP rasterises glyphs from it at runtime.
"""
import glob, io, os, sys
import UnityPy
from fontTools.ttLib import TTFont
from fontTools.merge import Merger

AA = ("/run/media/updullah/SSD 480GB/SteamLibrary/steamapps/common/Risk of Rain 2/"
      "Risk of Rain 2_Data/StreamingAssets/aa/StandaloneWindows64")


def game_root_font() -> bytes:
    p = glob.glob(os.path.join(AA, "*fonts-noto*.bundle"))[0]
    for o in UnityPy.load(p).objects:
        if o.type.name == "Font":
            d = o.read()
            if d.m_Name == "NotoSans-Regular":
                return bytes(d.m_FontData)
    raise SystemExit("NotoSans-Regular not found in the noto bundle")


def build(arabic_ttf: str) -> bytes:
    base = game_root_font()
    b = TTFont(io.BytesIO(base)); b["hmtx"]          # force decompile before merging
    vm = (b["hhea"].ascent, b["hhea"].descent, b["hhea"].lineGap,
          b["OS/2"].sTypoAscender, b["OS/2"].sTypoDescender, b["OS/2"].sTypoLineGap,
          b["OS/2"].usWinAscent, b["OS/2"].usWinDescent)
    base_cmap = set(b.getBestCmap())

    merged = Merger().merge([io.BytesIO(base), io.BytesIO(open(arabic_ttf, "rb").read())])
    merged["hmtx"]
    (merged["hhea"].ascent, merged["hhea"].descent, merged["hhea"].lineGap,
     merged["OS/2"].sTypoAscender, merged["OS/2"].sTypoDescender, merged["OS/2"].sTypoLineGap,
     merged["OS/2"].usWinAscent, merged["OS/2"].usWinDescent) = vm
    buf = io.BytesIO(); merged.save(buf); out = buf.getvalue()

    chk = TTFont(io.BytesIO(out)); cm = set(chk.getBestCmap())
    if not base_cmap <= cm:
        raise SystemExit("merge dropped codepoints the game font had")
    pres = [c for c in cm if 0xFB50 <= c <= 0xFDFF or 0xFE70 <= c <= 0xFEFC]
    print(f"{len(out)} bytes, {chk['maxp'].numGlyphs} glyphs, "
          f"{len(pres)} Arabic presentation forms, all base codepoints kept")
    return out


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "fonts/NotoSansArabic-Medium.ttf"
    dst = sys.argv[2] if len(sys.argv) > 2 else "fonts/ror-noto-arabic.ttf"
    open(dst, "wb").write(build(src))
    print("wrote", dst)
