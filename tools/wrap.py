"""Break Arabic into lines before it is shaped, so TMP never re-wraps it.

TMP has no bidi pass. Given a string that has already been reversed into visual
order it breaks lines left-to-right, which puts the logically-first clause on the
LAST line (measured in-game). The only reliable fix is to decide the line breaks
here, in logical order, and hand TMP text it has no reason to re-wrap.

Widths are measured against the real font in em units, so the table in
layout.json is resolution-independent: an entry is the container's width divided
by the font size the game draws that string at.
"""
from __future__ import annotations

import json
import os
import re

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "fonts", "RoR2Arabic-Regular.ttf")
LAYOUT = os.path.join(ROOT, "tools", "layout.json")

TAG_RE = re.compile(r"<[^<>]+>")
# A sprite is markup but it is drawn, and it comes out about one em wide.
SPRITE_RE = re.compile(r"<sprite\b[^<>]*>", re.I)
# The reshaper drops harakat before anything is drawn - TMP has no mark positioning, so
# they would pile up as spacing glyphs - which means they take no room on screen either.
HARAKAT_RE = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
# RoR2's TMP style sheet draws cKeywordName wrapped in brackets - "[ Agile ]" - so a
# keyword line is wider on screen than the string we measure. Measured in-game: without
# this the line overruns its panel and TMP breaks the stray bracket onto a line of its own.
KEYWORD_STYLE = "<style=cKeywordName>"
KEYWORD_BRACKETS = "[  ]"

_widths = None
_rules = None


def _load_font():
    global _widths
    if _widths is not None:
        return _widths
    font = TTFont(FONT, lazy=True)
    upem = font["head"].unitsPerEm
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    _widths = {}
    for cp, name in cmap.items():
        try:
            _widths[cp] = hmtx[name][0] / upem
        except KeyError:
            pass
    return _widths


def _load_rules():
    global _rules
    if _rules is not None:
        return _rules
    raw = json.load(open(LAYOUT, encoding="utf-8")) if os.path.exists(LAYOUT) else {}
    # Only "_comment" is a note; a real pattern may well start with "_".
    raw = {k: v for k, v in raw.items() if k != "_comment"}
    _rules = [(re.compile(p), float(w)) for p, w in raw.items()]
    return _rules


def width_em(s: str) -> float:
    """Advance width of the visible characters, in em. Markup is not drawn."""
    w = _load_font()
    plain = HARAKAT_RE.sub("", TAG_RE.sub("", s))
    # 0.5em is a reasonable stand-in for a glyph the font does not cover; it only
    # affects where a line breaks, never what is rendered.
    return len(SPRITE_RE.findall(s)) + sum(w.get(ord(c), 0.5) for c in plain)


def limit_for(token: str):
    for pattern, em in _load_rules():
        if pattern.search(token):
            return em
    return None


def _words(para: str):
    """Split on spaces, but never inside a tag: <sprite name="TP" tint=1> has
    spaces in it and has to stay in one piece."""
    held = []

    def hold(m):
        held.append(m.group(0))
        return f"\x00{len(held) - 1}\x00"

    masked = TAG_RE.sub(hold, para)
    words = []
    for w in masked.split(" "):
        for i, tag in enumerate(held):
            w = w.replace(f"\x00{i}\x00", tag)
        words.append(w)
    return words


def wrap(token: str, text: str) -> str:
    """Insert line breaks into logical-order text. Returns it unchanged when the
    token has no width rule or already fits."""
    limit = limit_for(token)
    if not limit:
        return text
    out = []
    for para in text.split("\n"):
        # The brackets sit at the head of the paragraph, so only its first line pays for them.
        head = width_em(KEYWORD_BRACKETS) if KEYWORD_STYLE in para else 0.0
        if head + width_em(para) <= limit:
            out.append(para)
            continue
        line, cur = [], head
        for word in _words(para):
            ww = width_em(word)
            space = width_em(" ") if line else 0.0
            if line and cur + space + ww > limit:
                out.append(" ".join(line))
                line, cur = [word], ww
            else:
                line.append(word)
                cur += space + ww
        if line:
            out.append(" ".join(line))
    return "\n".join(out)
