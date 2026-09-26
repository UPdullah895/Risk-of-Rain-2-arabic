#!/usr/bin/env bash
#
# Install the Arabic translation of Risk of Rain 2.
#
#   ./install.sh                            find the game and install
#   ./install.sh "/path/to/Risk of Rain 2"  install into a folder you name
#   ./install.sh --uninstall                remove it again
#   ./install.sh --where                    just print where the game is
#
# The mod is a folder inside BepInEx/plugins; installing copies it in and uninstalling
# deletes it, and the game's own files are untouched either way.
set -euo pipefail

APPID=632360
MOD=RoR2Arabic
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

say()  { printf '%s\n' "$*"; }
warn() { printf '%s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
    sed -n '3,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

# --- finding the game ------------------------------------------------------------------

# Every place a Steam install puts its root, including the Flatpak one and the Steam Deck's.
steam_roots() {
    printf '%s\n' \
        "$HOME/.local/share/Steam" \
        "$HOME/.steam/steam" \
        "$HOME/.steam/root" \
        "$HOME/.var/app/com.valvesoftware.Steam/.local/share/Steam" \
        "$HOME/Library/Application Support/Steam" \
        "/usr/local/share/Steam" \
        "/usr/share/steam"
}

# Steam keeps its library list in a Valve key-value file. Pulling the "path" lines out of it
# is enough; a full parser is not worth it for one field.
library_paths() {
    local root=$1 vdf="$1/steamapps/libraryfolders.vdf"
    printf '%s\n' "$root"
    [ -f "$vdf" ] || return 0
    sed -n 's/^[[:space:]]*"path"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$vdf"
}

# A folder is the game if the executable or its data folder is in it. Risk of Rain 2 ships
# only a Windows build, which on Linux runs through Proton, so the .exe is the right thing
# to look for on every platform.
is_game() {
    [ -n "${1:-}" ] && { [ -f "$1/Risk of Rain 2.exe" ] || [ -d "$1/Risk of Rain 2_Data" ]; }
}

find_game() {
    local root lib manifest installdir
    for root in $(steam_roots); do
        [ -d "$root" ] || continue
        while IFS= read -r lib; do
            [ -d "$lib" ] || continue
            manifest="$lib/steamapps/appmanifest_$APPID.acf"
            installdir="Risk of Rain 2"
            if [ -f "$manifest" ]; then
                installdir=$(sed -n 's/^[[:space:]]*"installdir"[[:space:]]*"\(.*\)"[[:space:]]*$/\1/p' "$manifest")
                [ -n "$installdir" ] || installdir="Risk of Rain 2"
            fi
            # No manifest is not disqualifying - a moved or copied install still has the
            # folder - so the same check runs either way.
            if is_game "$lib/steamapps/common/$installdir"; then
                printf '%s\n' "$lib/steamapps/common/$installdir"; return 0
            fi
        done < <(library_paths "$root")
    done
    return 1
}

# Explains itself before giving up, because the caller runs it in a command substitution -
# where an exit would only leave the subshell - and so cannot add anything useful afterwards.
ask_for_game() {
    local answer
    warn "Could not find Risk of Rain 2 automatically."
    if [ ! -t 0 ]; then
        warn "Run: $0 \"/path/to/Risk of Rain 2\""
        return 1
    fi
    warn "Give the folder that has 'Risk of Rain 2.exe' in it, or press Enter to give up."
    while true; do
        printf 'Game folder: ' >&2
        IFS= read -r answer || { warn "Nothing installed."; return 1; }
        [ -n "$answer" ] || { warn "Nothing installed."; return 1; }
        answer="${answer/#\~/$HOME}"
        if is_game "$answer"; then printf '%s\n' "$answer"; return 0; fi
        warn "There is no 'Risk of Rain 2.exe' in that folder."
    done
}

# --- the mod itself --------------------------------------------------------------------

find_payload() {
    local dir
    for dir in "$HERE/$MOD" "$HERE/dist/$MOD"; do
        [ -f "$dir/$MOD.dll" ] && { printf '%s\n' "$dir"; return 0; }
    done
    return 1
}

# The translation is a BepInEx plugin, so BepInEx has to be there first. Saying so plainly
# beats installing into a folder nothing will ever read.
check_bepinex() {
    [ -f "$1/BepInEx/core/BepInEx.dll" ] && return 0
    warn ""
    warn "BepInEx is not installed in:"
    warn "  $1"
    warn ""
    warn "The translation is a BepInEx plugin and cannot load without it. Install BepInEx"
    warn "5.4.21 for x64 from https://github.com/BepInEx/BepInEx/releases - unzip it into"
    warn "the game folder so that BepInEx/ sits next to 'Risk of Rain 2.exe' - then run"
    warn "this installer again. (If you use r2modman or Thunderstore Mod Manager, BepInEx"
    warn "is already inside the profile folder; point this installer at that folder.)"
    return 1
}

# --- go --------------------------------------------------------------------------------

action=install
game=

while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)      usage ;;
        -u|--uninstall) action=uninstall ;;
        -w|--where)     action=where ;;
        --game)         game=${2:?--game needs a path}; shift ;;
        -*)             warn "unknown option: $1"; usage 1 ;;
        *)              game=$1 ;;
    esac
    shift
done

if [ -n "$game" ]; then
    game="${game/#\~/$HOME}"
    is_game "$game" || die "no 'Risk of Rain 2.exe' in $game"
    [ "$action" = where ] || say "Game: $game"
elif game=$(find_game); then
    [ "$action" = where ] || say "Found the game: $game"
else
    game=$(ask_for_game) || exit 1
fi

if [ "$action" = where ]; then
    printf '%s\n' "$game"
    exit 0
fi

target="$game/BepInEx/plugins/$MOD"

if [ "$action" = uninstall ]; then
    if [ -d "$target" ]; then
        rm -rf "$target"
        say "Removed. Risk of Rain 2 is back to English."
    else
        say "Nothing to remove - the translation is not installed."
    fi
    exit 0
fi

check_bepinex "$game" || exit 1

payload=$(find_payload) || die "the mod is missing from $HERE.
Download the release archive and run install.sh from inside it, or build it with tools/release.sh."

rm -rf "$target"
mkdir -p "$target"
cp -R "$payload/." "$target/"

say ""
say "Installed into $target"
say "Start the game, open Settings, and choose العربية in the language list."
say "To remove it later: $0 --uninstall"
