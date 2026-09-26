# How the translation works

Notes for anyone working on the mod rather than playing with it. For installing it, see
the [README](../README.md).

## Working on it

The Python tools want a virtualenv:

```bash
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
```

```bash
./venv/bin/python tools/extract.py      # the game's English -> work/en.json
./venv/bin/python tools/build_lang.py   # lang/*.json -> language/ar/Strings.json
./tools/deploy.sh                       # copy straight into the game, for testing
./tools/stage.sh /tmp/RoR2Arabic        # build the plugin and lay it out as installed
./tools/release.sh                      # the whole thing, zipped, into dist/
```

`build_lang.py` alone is enough to check a translation compiles, once `work/en.json` exists.
`release.sh` produces the archive that players download from Releases: the plugin, both
installers and the licences, zipped under one folder.

Building the plugin needs the game's own assemblies, which are not in this repo. Point the
build at your install with `ROR2_DIR=... dotnet build -c Release src/RoR2Arabic` or
`-p:GameDir=...`. The same `ROR2_DIR` steers `extract.py`, `make_font.py` and `deploy.sh`.

`work/en.json` is the game's own English text and is deliberately not checked in; it is the
reference the validator compares against, and `extract.py` regenerates it from an install.

## Where the text lives

`Risk of Rain 2_Data/StreamingAssets/Language/<folder>/` — one folder per language, holding
plain JSON of `{"strings": {"TOKEN": "text"}}`. Files load in name order and later ones win.
A language folder needs:

| file | purpose |
|---|---|
| `language.json` | `{"language": {"selfname": "…"}}` — the name shown in the picker |
| `icon.png` | the flag beside that name |
| `*.json` / `*.txt` | the strings themselves |
| `DEFAULT_FONT` token | which TMP font the language uses |

Languages are discovered by scanning that directory, which is why adding a folder is enough
and no asset repacking is needed. The plugin adds its own directory to the scan rather than
writing into the game's.

Note that `selfname` goes through the same shaping and reordering as everything else —
written as plain logical text it renders back-to-front, because the picker draws it with the
same engine.

## How it works

Four things have to happen, and the plugin does them in this order.

**1. The language folder.** `Language.collectLanguageRootFolders` is a public `Action<List<string>>`
— the game's own extension point. The plugin appends its own `Language/` directory to it, so
`ar` appears in the picker with no file patching and no asset repacking.

**2. The font.** RoR2's shipped fonts contain zero Arabic codepoints, so every glyph would be
tofu. Unity cannot build a usable `Font` from a loose file at runtime, and TMP's dynamic
rasteriser only ever asks the engine for "the current face", so the plugin creates a
name-only placeholder `Font` and puts a Harmony prefix on `FontEngine.LoadFontFace(Font, …)`
that substitutes the path overload for that one name. The resulting `TMP_FontAsset` is
attached as a **fallback** to every font asset the game creates — not as a replacement — so
Latin text, digits and sprite tags keep RoR2's own typeface.

**3. Shaping and direction.** TextMeshPro has no Arabic shaper and no bidi pass, so raw
logical text renders as disconnected letters in reverse. `tools/build_lang.py` therefore
reshapes to presentation forms and emits **visual order** at build time.

The hard part is the markup. Naively reversing a string containing `<style=…>…</style>` puts
the closing tag before the opening one. Instead each string is parsed into a tree of
`Text` / `Void` / `Span` nodes, the *children* of each node are emitted in reverse order, and
each span keeps its own tags around its own content. Newlines are not reversed — line 1 stays
line 1.

Harakat are stripped by the reshaper before anything is drawn: TMP has no mark positioning,
so combining marks would pile up as spacing glyphs. Diacritics in `lang/` are therefore for
the reader of the source only, and **no string may depend on one to be understood**.

**4. Line breaks.** Given visual-order text, TMP wraps left-to-right and puts the
logically-first clause on the *last* line — measured in-game. `tools/wrap.py` therefore
decides the breaks itself, in logical order, against the real font metrics from
`fonts/RoR2Arabic-Regular.ttf`.

## Layout

`tools/layout.json` maps a token pattern to its container's width in **em**: the container's
width in pixels divided by the font size the game draws that string at. That makes an entry
resolution-independent. First match wins, so specific patterns come before general ones.

Rules of thumb, all learned the hard way:

- Wrapping **narrower** than the container is always safe. TMP only ever re-wraps, and
  re-wrapping is what inverts the order.
- When one token is drawn in **two** containers, the narrower one decides. A skill
  description appears both in the character-select list (~34 em) and in the loadout tooltip
  (~26 em), so it is wrapped for the tooltip.
- Measure off a line the game itself fitted without breaking; that line is a lower bound on
  the container.
- A `<sprite>` tag is markup but it *is* drawn, and it is about one em wide. `width_em`
  counts it.
- RoR2's TMP style sheet draws `cKeywordName` wrapped in brackets — `[ Agile ]` — text that
  is not in the string at all. `wrap.py` adds that allowance to the first line of any
  paragraph containing the style. Without it the line overruns and TMP breaks the stray
  bracket onto a line of its own.
- A placeholder that expands at runtime cannot be measured. `LANGUAGE_PLATFORM` is
  `"الافتراضية\n({0})"` because `{0}` becomes `English` and always wraps; the break is
  written by hand so the two lines stay in order.

Anything not listed is left for TMP, which is correct for text that fits on one line. A
wrapping panel that is not listed may invert its line order; add a measured entry when you
find one.

## Checking

`build_lang.py` refuses to write anything if a translation drops or adds markup, changes the
set of `{0}` placeholders, or empties a token that had English text. A broken string cannot
reach the game.

Two classes of text look like markup and must be passed through verbatim rather than
translated:

- Anything in angle brackets that is **not** a real tag — `<Click>`, `<?SCANNING?>`,
  `< THEY REPAIR MY HULL >`. TMP parses them as tags, so they are never shaped, and the
  validator counts them as markup.
- Anything in braces, because `{…}` is the placeholder pattern. Some lore entries wrap whole
  blocks in braces; those blocks are spliced in from the English and only the prose around
  them is swapped.

## State

4,067 of 4,677 tokens are translated. What is left in English is deliberate and listed in the
README. `tools/build_lang.py` prints the running count on every build.
