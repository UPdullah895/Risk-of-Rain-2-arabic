"""Dump the game's English strings to work/en.json, keeping the source file of each token.

RoR2 language files are JSON-ish: they allow trailing commas and // comments, and
ship both .json and .txt variants of the same content. We read them the way the game
does (loosely), preferring .json when a .txt duplicates it.
"""
import json, os, re, sys
from collections import OrderedDict

GAME = ("/run/media/updullah/SSD 480GB/SteamLibrary/steamapps/common/Risk of Rain 2/"
        "Risk of Rain 2_Data/StreamingAssets")
EN = os.path.join(GAME, "Language", "en")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def loose_json(text: str):
    text = text.lstrip("﻿")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    # only whole-line comments: item lore contains "//--AUTO-TRANSCRIPTION..." inside
    # string literals, which a naive // stripper destroys.
    text = re.sub(r"(?m)^[ \t]*//.*$", "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)      # trailing commas
    # strict=False: the shipped files contain raw newlines/tabs inside string
    # literals, which the game's own lenient parser accepts.
    return json.loads(text, strict=False)


def main():
    files = sorted(os.listdir(EN))
    seen_stems = set()
    strings, source = OrderedDict(), {}
    skipped = []
    for fn in files:
        stem, ext = os.path.splitext(fn)
        if ext not in (".json", ".txt"):
            continue
        if stem in seen_stems:                       # .txt duplicate of a .json
            continue
        path = os.path.join(EN, fn)
        try:
            data = loose_json(open(path, encoding="utf-8-sig").read())
        except Exception as e:
            skipped.append(f"{fn}: {e}")
            continue
        block = data.get("strings") or {}
        if not block:
            continue
        seen_stems.add(stem)
        for k, v in block.items():
            if k in strings and strings[k] != v:
                skipped.append(f"duplicate token {k} ({source[k]} vs {fn})")
            strings[k] = v
            source[k] = fn

    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    out = os.path.join(ROOT, "work", "en.json")
    json.dump(strings, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(source, open(os.path.join(ROOT, "work", "en_source.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"{len(strings)} tokens from {len(seen_stems)} files -> work/en.json")
    counts = {}
    for k, f in source.items():
        counts[f] = counts.get(f, 0) + 1
    for f, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {n:5}  {f}")
    if skipped:
        print("\nnotes:")
        for s in skipped[:10]:
            print("  ", s)


if __name__ == "__main__":
    main()
