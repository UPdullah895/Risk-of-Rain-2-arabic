# Fonts

`RoR2Arabic-Regular.ttf` is the font the plugin hands to TextMeshPro as a fallback so the
game can draw Arabic at all. It is Noto Sans (the family the game itself uses for its UI)
merged with Noto Sans Arabic, keeping Noto Sans' vertical metrics so line spacing in the
game is unchanged. Both are under the SIL Open Font License 1.1; the licence texts are in
`LICENCES/`.

`tools/make_font.py` rebuilds it. It reads the game's own copy of Noto Sans out of its
asset bundles for the base, which is why the build is not reproducible without the game
installed - the merged result is checked in instead.
