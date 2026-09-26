"""Turn the human-readable Arabic in lang/ into what the game can actually draw.

Source files under lang/ hold Arabic in normal logical order with the English
markup left in place, so they stay reviewable and diffable. The game cannot do
this itself: TMP in Risk of Rain 2 has no Arabic shaper and no bidi pass, so raw
logical text renders as disconnected letters in reverse (verified in-game). The
build therefore reshapes to presentation forms and emits visual order.

The hard part is the markup. Reversing a string that contains <style=...>...</style>
naively puts the closing tag before the opening one. Instead the string is parsed
into a tree of spans, the *children* of each node are emitted in reverse order, and
each span keeps its own open/close tags around its own content. Newlines are not
reversed - line 1 stays line 1.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from typing import List

import arabic_reshaper
from bidi.algorithm import get_display

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wrap as prewrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG_SRC = os.path.join(ROOT, "lang")
EN_PATH = os.path.join(ROOT, "work", "en.json")
OUT_DIR = os.path.join(ROOT, "language", "ar")

# What the language picker calls this language. It goes through the same shaping and
# reordering as everything else - written straight into language.json as logical text it
# renders back-to-front, because the picker draws it with the same engine.
SELF_NAME = "العربية"

TAG_RE = re.compile(r"<[^<>]+>")
# Tags that wrap content. Anything else inside <> is emitted as-is and never paired.
PAIRED = {
    "style", "color", "i", "b", "u", "s", "size", "mspace", "font", "align",
    "cspace", "line-height", "indent", "link", "lowercase", "uppercase",
    "smallcaps", "margin", "mark", "nobr", "noparse", "pos", "voffset", "width", "sub", "sup",
}
# Also covers .NET format specs such as {0:00}, {0:0.0%} and {0:#00.00}, whose
# punctuation would otherwise be reordered by the bidi pass.
PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}")


# --------------------------------------------------------------------------- parsing

class Text:
    __slots__ = ("s",)

    def __init__(self, s: str):
        self.s = s


class Void:
    """A self-contained tag such as <sprite name="TP" tint=1> or <br>."""
    __slots__ = ("s",)

    def __init__(self, s: str):
        self.s = s


class Span:
    __slots__ = ("open", "close", "children")

    def __init__(self, open_tag: str):
        self.open = open_tag
        self.close = ""
        self.children: List = []


def tag_name(tag: str) -> str:
    m = re.match(r"</?\s*([A-Za-z0-9_-]+)", tag)
    return (m.group(1).lower() if m else "")


def parse(s: str):
    """Parse one line into a flat-ish tree of Text / Void / Span nodes."""
    root = Span("")
    stack = [root]
    pos = 0
    for m in TAG_RE.finditer(s):
        if m.start() > pos:
            stack[-1].children.append(Text(s[pos:m.start()]))
        pos = m.end()
        tag = m.group(0)
        name = tag_name(tag)
        if tag.startswith("</"):
            # close the nearest matching span; ignore strays rather than corrupting
            for i in range(len(stack) - 1, 0, -1):
                if tag_name(stack[i].open) == name:
                    stack[i].close = tag
                    del stack[i + 1:]
                    stack.pop()
                    break
            else:
                stack[-1].children.append(Void(tag))
        elif name in PAIRED:
            node = Span(tag)
            stack[-1].children.append(node)
            stack.append(node)
        else:
            stack[-1].children.append(Void(tag))
    if pos < len(s):
        stack[-1].children.append(Text(s[pos:]))
    return root


# --------------------------------------------------------------------------- shaping

def shape_text(t: str) -> str:
    if not t.strip():
        return t
    # A placeholder like {0} is braces plus a digit, but at runtime it becomes a
    # plain number. Those resolve differently under bidi - "({0}%)" and "(45%)"
    # come out in different orders - so shape with a stand-in number and put the
    # placeholder back afterwards.
    stand_ins = {}
    def hold(m):
        key = str(9700 + len(stand_ins))
        stand_ins[key] = m.group(0)
        return key
    held = PLACEHOLDER_RE.sub(hold, t)
    out = get_display(arabic_reshaper.reshape(held), base_dir="R")
    for key, original in stand_ins.items():
        out = out.replace(key, original)
    return out


def render(node) -> str:
    if isinstance(node, Text):
        return shape_text(node.s)
    if isinstance(node, Void):
        return node.s
    # A span's children are laid out right-to-left, so emit them reversed; the
    # span's own tags stay wrapped around its own content.
    inner = "".join(render(c) for c in reversed(node.children))
    return node.open + inner + node.close


def to_visual(s: str) -> str:
    # Vertical order is not reversed: each line is shaped on its own.
    return "\n".join(render(parse(line)) for line in s.split("\n"))


# --------------------------------------------------------------------------- checking

def signature(s: str):
    """What must survive translation: the markup and the placeholders."""
    return Counter(TAG_RE.findall(s)), Counter(PLACEHOLDER_RE.findall(s))


def check(token: str, english: str, arabic: str) -> List[str]:
    problems = []
    en_tags, en_ph = signature(english)
    ar_tags, ar_ph = signature(arabic)
    if en_tags != ar_tags:
        missing = en_tags - ar_tags
        extra = ar_tags - en_tags
        if missing:
            problems.append(f"{token}: markup dropped {list(missing.elements())}")
        if extra:
            problems.append(f"{token}: markup added {list(extra.elements())}")
    if en_ph != ar_ph:
        problems.append(f"{token}: placeholders {sorted(en_ph.elements())} -> {sorted(ar_ph.elements())}")
    # Some tokens are blank in English too (unused subtitles); only an Arabic
    # blank where English had text is a real omission.
    if arabic.strip() == "" and english.strip() != "":
        problems.append(f"{token}: empty")
    return problems


# --------------------------------------------------------------------------- build

def main() -> int:
    english = {k: v for k, v in json.load(open(EN_PATH, encoding="utf-8")).items()
               if isinstance(v, str)}
    if not os.path.isdir(LANG_SRC):
        print(f"no source directory: {LANG_SRC}")
        return 1

    merged, per_file, problems = {}, {}, []
    for fn in sorted(os.listdir(LANG_SRC)):
        if not fn.endswith(".json"):
            continue
        data = json.load(open(os.path.join(LANG_SRC, fn), encoding="utf-8"))
        per_file[fn] = data
        for token, arabic in data.items():
            if token in merged:
                problems.append(f"{token}: defined twice")
            merged[token] = arabic
            if token in english:
                problems.extend(check(token, english[token], arabic))
            else:
                problems.append(f"{token}: not a token in this game version")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems[:40]:
            print("  " + p)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    # Pre-wrap first: TMP would otherwise break the reversed string left-to-right
    # and put the logically-first clause on the last line.
    visual = {t: to_visual(prewrap.wrap(t, a)) for t, a in merged.items()}
    out = os.path.join(OUT_DIR, "Strings.json")
    json.dump({"strings": visual}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"language": {"selfname": to_visual(SELF_NAME)}},
              open(os.path.join(OUT_DIR, "language.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    untranslated = len(english) - len(merged)
    print(f"{len(merged)} tokens built -> language/ar/Strings.json "
          f"({untranslated} of {len(english)} still English)")
    for fn, data in per_file.items():
        print(f"  {len(data):5}  {fn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
