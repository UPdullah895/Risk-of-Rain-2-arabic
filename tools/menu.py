#!/usr/bin/env python3
"""Click a main-menu row without needing to know where the cursor is.

Pointer motion reaching the game is scaled by acceleration and the game draws
its own cursor, so open-loop moves miss. The menu highlights whatever row is
hovered, though, so hover, look at what lit up, and step by whole rows until the
right one is lit. That is self-correcting and needs no cursor tracking at all.
"""
import subprocess
import sys
import time

MONITOR = "DP-2"
ROWS = [584, 632, 680, 728, 776, 824, 872]   # y of each main-menu row
PROBE_X = 150                                # inside the menu, left of the label
ROW_H = 48


def shot(path="/tmp/_menu.png"):
    subprocess.run(["grim", "-o", MONITOR, path], check=True)
    return path


# The game is on the right-hand monitor, so the bottom-right of the desktop is
# also the bottom-right of the game. Pinning to the top-left would land on the
# OTHER monitor, where moving right never reaches the game at all.
ORIGIN = (1919, 1079)


def corner():
    """Pin the pointer to the game monitor's bottom-right - a known position
    whatever the pointer acceleration does to a large move.

    The first move after the game takes the pointer is swallowed - right after a
    restart it leaves the cursor parked in the middle of the screen - so nudge
    once, then pin."""
    subprocess.run(["ydotool", "mousemove", "-x", "10", "-y", "10"], check=True)
    time.sleep(0.2)
    subprocess.run(["ydotool", "mousemove", "-x", "5000", "-y", "5000"], check=True)
    time.sleep(0.4)


def step(dx, dy, px=5):
    """Walk to the target in many small moves, which acceleration leaves at ~1:1.

    Each move is whole pixels, so the leftover fraction has to be carried into
    the next one: rounding every step on its own loses the fraction and the
    pointer lands short - for a 1661x495 move that was 320px too high."""
    n = int(max(abs(dx), abs(dy)) // px) or 1
    sent_x = sent_y = 0
    for i in range(1, n + 1):
        want_x, want_y = round(dx * i / n), round(dy * i / n)
        mx, my = want_x - sent_x, want_y - sent_y
        if mx or my:
            subprocess.run(["ydotool", "mousemove", "-x", str(mx), "-y", str(my)], check=True)
            sent_x, sent_y = want_x, want_y
        time.sleep(0.02)
    time.sleep(0.3)


def lit_row():
    """Index of the highlighted row, or None. The hovered row is drawn in a pale
    khaki; the others are dark grey."""
    from PIL import Image
    im = Image.open(shot()).convert("RGB")
    for i, y in enumerate(ROWS):
        r, g, b = im.getpixel((PROBE_X, y))
        if r > 150 and g > 150 and b < 200 and abs(r - g) < 40:
            return i
    return None


def hover(index, tries=12):
    corner()
    step(PROBE_X - ORIGIN[0], ROWS[index] - ORIGIN[1])
    for _ in range(tries):
        cur = lit_row()
        if cur == index:
            return True
        if cur is None:
            corner()
            step(PROBE_X - ORIGIN[0], ROWS[index] - ORIGIN[1])
            continue
        step(0, (index - cur) * ROW_H)
    return lit_row() == index


def click():
    """Activate whatever the pointer is over.

    Synthetic mouse buttons do not reach this game's menus - the row highlights
    under the pointer but never activates, with a press/release pair as much as
    with a single click event. Hovering sets the selection, though, and Return
    activates the selection, so hover with the mouse and commit with the key."""
    subprocess.run(["ydotool", "key", "28:1", "28:0"], check=True)
    time.sleep(1.5)


def point(x, y):
    """Put the pointer at an absolute spot on the game monitor, by anchoring at a
    corner first so the starting position is always known."""
    corner()
    step(x - ORIGIN[0], y - ORIGIN[1])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "lit":
        print(lit_row())
    elif cmd == "hover":
        print(hover(int(sys.argv[2])))
    elif cmd == "point":
        point(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "at":
        point(int(sys.argv[2]), int(sys.argv[3])); click()
    elif cmd == "click":
        # Now that step() lands where it is told, pointing at the row is enough.
        # The lit-row check is no longer trustworthy anyway: rows carrying a
        # "NEW" badge pulse through the same pale khaki as a hovered row.
        point(258, ROWS[int(sys.argv[2])])
        click()
