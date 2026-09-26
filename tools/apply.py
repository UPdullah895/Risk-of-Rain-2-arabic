"""Install or remove the Arabic test language and font in Risk of Rain 2.

    apply.py install   copy language/ar into the game and swap the fallback font
    apply.py restore   put the stock font bundle back and remove the ar language
    apply.py status    say what is currently installed

The font swap replaces the source font of the *already dynamic* fallback asset
(NotoSansCJKsc-Regular SDF (Dynamic)). That asset is the only one in the bundle
wired for runtime rasterisation, so it is the only one worth feeding.

NOTE: while installed, the swap removes CJK coverage - Japanese, Korean and
Chinese will show tofu. A shippable version needs one font carrying both.
"""
import glob, os, shutil, sys, UnityPy

GAME = ("/run/media/updullah/SSD 480GB/SteamLibrary/steamapps/common/Risk of Rain 2/"
        "Risk of Rain 2_Data/StreamingAssets")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "fonts", "ror-noto-arabic.ttf")
LANG_SRC = os.path.join(ROOT, "language", "ar")
LANG_DST = os.path.join(GAME, "Language", "ar")
TARGET = "NotoSansCJKsc-Regular"          # the dynamic fallback's source font


def bundle() -> str:
    return glob.glob(os.path.join(GAME, "aa/StandaloneWindows64/*fonts-noto*.bundle"))[0]


def font_size() -> int:
    for o in UnityPy.load(bundle()).objects:
        if o.type.name == "Font" and o.read().m_Name == TARGET:
            return len(o.read().m_FontData)
    return -1


def status() -> str:
    n = font_size()
    font = "stock" if n > 5_000_000 else f"patched ({n} bytes)"
    return f"font: {font}    language/ar: {'present' if os.path.isdir(LANG_DST) else 'absent'}"


def install() -> None:
    b = bundle()
    if not os.path.exists(b + ".orig"):
        shutil.copyfile(b, b + ".orig")
        print("backed up stock bundle ->", os.path.basename(b) + ".orig")
    shutil.copyfile(b + ".orig", b)
    data = open(FONT, "rb").read()
    env = UnityPy.load(b)
    for o in env.objects:
        if o.type.name == "Font":
            d = o.read()
            if d.m_Name == TARGET:
                d.m_FontData = data
                d.save()
    open(b, "wb").write(env.file.save())
    shutil.rmtree(LANG_DST, ignore_errors=True)
    shutil.copytree(LANG_SRC, LANG_DST)
    print("installed.", status())


def restore() -> None:
    b = bundle()
    if os.path.exists(b + ".orig"):
        shutil.copyfile(b + ".orig", b)
        os.remove(b + ".orig")
        print("font bundle restored from backup")
    else:
        print("no backup found - verify game files in Steam if the font looks wrong")
    shutil.rmtree(LANG_DST, ignore_errors=True)
    print("restored.", status())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"install": install, "restore": restore, "status": lambda: print(status())}[cmd]()
