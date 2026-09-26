# التعريب العربي للعبة Risk of Rain 2

<div dir="rtl">

مود يضيف **اللغة العربية** إلى Risk of Rain 2، بخطّ يرسم الحروف العربية
وبنصوص مُشكَّلة ومُرتَّبة مسبقًا لتظهر متّصلة وبالاتّجاه الصحيح.

**لا يؤثّر على اللعب الجماعي.** المود لا يرفع `RoR2Application.isModded`، وهو العَلَم
الذي يضيف وسم `mod` إلى الغرفة ويفصل المُطابقة عن اللاعبين العاديّين. المود يضيف
نصًّا وخطًّا فقط ولا يمسّ حالة اللعبة، فتبقى الغرف والمُطابقة والمحاكمات المنشوريّة كما هي.

</div>

---

## Install

**Download the latest release**, unzip it, and run the installer inside:

| | |
|---|---|
| Windows | double-click `install-windows.bat` |
| Linux / Steam Deck | `./install.sh` |

The installer finds the game through Steam, copies the plugin into
`BepInEx/plugins/RoR2Arabic/`, and touches nothing else. Both installers have an
uninstall button (`./install.sh --uninstall` on Linux) that deletes exactly what they
copied.

**BepInEx must be installed first.** Get **BepInEx 5.4.21 (x64)** from
[its releases page](https://github.com/BepInEx/BepInEx/releases), unzip it into the game
folder so `BepInEx/` sits next to `Risk of Rain 2.exe`, and run the game once. If you use
r2modman or Thunderstore Mod Manager, BepInEx is already in the profile folder — point the
installer at that folder instead. The installers check for it and say so if it is missing.

Then start the game and pick **العربية** from the language dropdown at the top right of
the main menu.

### If the language keeps resetting to English

Pick the language **in the game**, not by editing `config.cfg`. The authoritative copy is
the **Steam Cloud** one, and it is restored over any hand edit:

```
~/.local/share/Steam/userdata/<id>/632360/remote/UserProfiles/config.cfg
Risk of Rain 2/Risk of Rain 2_Data/Config/config.cfg
```

Both files use CRLF line endings — if you do edit them, use a text editor, not `sed`.

## Uninstall

Run the installer again and press **إزالة**, or `./install.sh --uninstall`. That deletes
`BepInEx/plugins/RoR2Arabic/` and nothing else; the game's own files were never modified.

## What is translated

4,067 of 4,677 strings. Menus, settings, survivors and their skills, items, equipment,
drones, monsters, stages, achievements, the logbook, boss dialogue, the intro cutscene and
every non-item lore entry are done.

Left in English on purpose:

| | count | why |
|---|---|---|
| `ITEM_*_LORE`, `EQUIPMENT_*_LORE` | 217 | long in-world prose; still being translated |
| `CREDITS_*` | 315 | proper names |
| tokens whose English is `LORE HERE` / `TBD` / empty | 60 | the developers left them blank |
| `LOREM`, `DEFAULT_FONT`, `PERCENT_FORMAT`, `GAME_TITLE`, … | 18 | engine values and format specifiers, not text |

## Building from source

```bash
python -m venv venv && ./venv/bin/pip install -r requirements.txt

./venv/bin/python tools/build_lang.py   # lang/*.json -> language/ar/Strings.json
./tools/stage.sh /tmp/RoR2Arabic        # build the plugin and lay it out as installed
./tools/release.sh                      # the whole thing, zipped, into dist/
./tools/deploy.sh                       # copy straight into the game, for testing
```

Building the plugin needs the game's own assemblies, which are not in this repo. Point the
build at your install with `ROR2_DIR=... dotnet build -c Release src/RoR2Arabic` or
`-p:GameDir=...`.

`build_lang.py` refuses to write anything if a translation drops markup or a `{0}`
placeholder, so a broken string cannot reach the game.

## How it works

- **The language folder.** The plugin appends its own `Language/` directory to
  `Language.collectLanguageRootFolders`, the game's own extension point, so `ar`
  appears in the picker with no file patching.
- **The font.** RoR2's shipped fonts contain zero Arabic codepoints. A Harmony
  prefix on `FontEngine.LoadFontFace(string, int)` redirects the placeholder font to
  `fonts/RoR2Arabic-Regular.ttf`, and the resulting `TMP_FontAsset` is attached as a
  fallback to every font asset the game creates.
- **Shaping and direction.** TextMeshPro has no Arabic shaper and no bidi pass, so
  `tools/build_lang.py` reshapes to presentation forms and emits visual order at
  build time. Markup is handled by parsing each string into a tree and reversing the
  *children* of each span, so `<style=…>…</style>` never ends up inside out.
- **Line breaks.** Given visual-order text, TMP wraps left-to-right and puts the
  logically-first clause on the *last* line (measured in-game). `tools/wrap.py`
  therefore breaks the lines itself, in logical order, against the real font metrics.
  `tools/layout.json` maps a token pattern to its container width in em — resolution
  independent, since an em is the container's width divided by the font size the game
  draws that string at. Wrapping narrower than the container is always safe; wrapping
  wider lets TMP re-wrap and invert the order.

## Known gaps

- Menu text is left-aligned rather than right-aligned. Alignment is set by the
  game's own layouts, not by the strings. Where that put a trailing colon alone on the
  left margin — the settings labels — the colon was dropped instead.
- Harakat are stripped before rendering. TextMeshPro has no mark positioning, so combining
  marks would pile up as spacing glyphs; the reshaper removes them. Diacritics in `lang/`
  are for the reader of the source, and no string may depend on one to be understood.
- `layout.json` covers the containers verified so far (menu descriptions, item and
  equipment descriptions, skill panels, survivor blurbs, logbook unlock hints). A
  wrapping panel that is not listed will be laid out by TMP and may invert its line
  order; add a measured entry when you find one. When one token is drawn in two
  containers, the **narrower** one decides — a skill description appears both in the
  character-select list and in the loadout tooltip, so it is wrapped for the tooltip.
