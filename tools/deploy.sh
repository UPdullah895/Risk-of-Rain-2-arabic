#!/bin/bash
# Deploy the built plugin into the game's BepInEx plugins folder.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Override with ROR2_DIR for a different install; install.sh is the one players use.
GAME="${ROR2_DIR:-/run/media/updullah/SSD 480GB/SteamLibrary/steamapps/common/Risk of Rain 2}"
DEST="$GAME/BepInEx/plugins/RoR2Arabic"

mkdir -p "$DEST/fonts" "$DEST/Language"
cp "$ROOT/src/RoR2Arabic/bin/Release/RoR2Arabic.dll" "$DEST/"
cp "$ROOT/fonts/RoR2Arabic-Regular.ttf" "$DEST/fonts/"
rm -rf "$DEST/Language/ar"
cp -r "$ROOT/language/ar" "$DEST/Language/ar"

echo "deployed to $DEST"
find "$DEST" -type f | sed "s|$DEST/|  |"
