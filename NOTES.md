# Risk of Rain 2 — Arabic feasibility

Game: Risk of Rain 2 (Gearbox), Steam appid 632360, ver. 1.4.1#912, run under Proton.
Install: the usual Steam library path, `steamapps/common/Risk of Rain 2`.

Verdict: **feasible**. Arabic was rendered in-game on 2026-09-25 (see `screenshots/`).
The game is Mono (not IL2CPP), text is plain JSON, and the font path is reachable.

## Where the text lives

`Risk of Rain 2_Data/StreamingAssets/Language/<folder>/` — one folder per language,
plain JSON/`.txt` files of `{"strings": {"TOKEN": "text"}}`. ~4,970 English tokens
across 41 files in `en/`. No asset repacking needed for the text itself.

A language folder needs:

| file | purpose |
|---|---|
| `language.json` | `{"language": {"selfname": "..."}}` — the name in the picker |
| `icon.png` | flag shown in the picker |
| `*.json` / `*.txt` | the strings; files load in name order, later wins |
| `DEFAULT_FONT` token | which TMP font the language uses |

Languages are discovered by scanning that directory — a new folder appears in the
picker with no code change. `StreamingAssets/LanguageOverrides/` is a further
supported override layer.

## Fonts (verified)

`DEFAULT_FONT` selects the font per language. Latin languages use
`TmpFonts/Bombardier/tmpBombDropShadow`; RU/ja/ko/zh/tr use
`TmpFonts/Noto/NotoSans-Regular SDF(ROOT Extended ASCII + Turkish)`.
Turkish ships `ForceNotoOn.txt`/`zForceNotoOn.txt` doing exactly that.

Bundle `ror2-base-common-fonts-noto_assets_all_*.bundle` holds:

| asset | atlas mode | source font | notes |
|---|---|---|---|
| `NotoSans-Regular SDF(ROOT …)` | **static** | **stripped (PathID 0)**, atlas not readable | falls back to the asset below |
| `NotoSansCJKsc-Regular SDF (Dynamic)` | **dynamic** | `NotoSansCJKsc-Regular` (16 MB, CFF) | rasterises glyphs at runtime |

Neither shipped font has a single Arabic codepoint (0 in U+0600–06FF).

**Do not** flip the ROOT asset from static to dynamic: its source-font pointer and
readable atlas were stripped at build time, and TMP crashes in
`TMP_FontAssetUtilities.GetCharacterFromFontAsset_Internal` on the first lookup.
Verified crash, 2026-09-25.

**Do** replace the source font of the dynamic fallback asset, which is already
wired correctly. That is what `tools/apply.py install` does.

## Shaping and RTL — the real work

TMP has no shaper and no bidi. Confirmed side by side in one screenshot
(`screenshots/4-raw-vs-preshaped.png`):

- raw logical-order Arabic → disconnected letters in reverse order
- pre-shaped presentation forms (U+FB50–FDFF, U+FE70–FEFC) in visual order → correct

So the pipeline must reshape + reorder at build time, same as the 9 Kings work.
Text is also left-aligned in RTL, and mixed Arabic/Latin in one string
(`"العربية (Arabic)"`) misplaces the Latin run and breaks row wrapping.

## Outcome

Those questions are settled; this file is kept as the record of the investigation.
See `README.md` for what was built and how to install it.

- The delivery vehicle is a BepInEx plugin (`src/RoR2Arabic`), not file patching.
  It adds its own `Language/` root through `Language.collectLanguageRootFolders`
  and supplies the font by Harmony-patching `FontEngine.LoadFontFace`, so nothing
  in the game's own files is touched and `tools/apply.py` is no longer used.
- TMP does re-wrap pre-wrapped visual-order text, and re-wrapping inverts the line
  order. `tools/wrap.py` + `tools/layout.json` break the lines first, in logical
  order, against the real font metrics.
- The language selection is stored in the **Steam Cloud** copy of `config.cfg`,
  not the one in the game folder; setting only the local copy silently reverts.

## Commands

```bash
python tools/make_font.py <arabic.ttf> fonts/RoR2Arabic-Regular.ttf
./venv/bin/python tools/build_lang.py   # lang/*.json -> language/ar/Strings.json
./tools/deploy.sh                       # into BepInEx/plugins/RoR2Arabic
python3 tools/game.py start|stop|restart|status
```
