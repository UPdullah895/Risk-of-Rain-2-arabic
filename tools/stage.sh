#!/usr/bin/env bash
# Assemble the plugin into a folder laid out the way it is installed, and nothing else.
#
# BepInEx loads every .dll it finds under plugins/, and the plugin reads the rest by path
# relative to its own assembly, so the layout here is the layout at runtime:
#
#   RoR2Arabic/
#     RoR2Arabic.dll
#     fonts/RoR2Arabic-Regular.ttf
#     Language/ar/...
set -euo pipefail
DEST="${1:?usage: stage.sh <folder>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

[ -f "$HERE/language/ar/Strings.json" ] || {
    echo "missing language/ar/Strings.json - run tools/build_lang.py first" >&2; exit 1; }

dotnet build -c Release -v q --nologo "$HERE/src/RoR2Arabic/RoR2Arabic.csproj"

mkdir -p "$DEST/fonts"
# Drop what we put there last time, so a renamed font or a removed data file does not linger.
rm -rf "$DEST/Language" "$DEST/fonts"
mkdir -p "$DEST/fonts"
cp "$HERE/src/RoR2Arabic/bin/Release/RoR2Arabic.dll" "$DEST/RoR2Arabic.dll"
cp "$HERE/fonts/RoR2Arabic-Regular.ttf" "$DEST/fonts/"
mkdir -p "$DEST/Language"
cp -R "$HERE/language/ar" "$DEST/Language/ar"
