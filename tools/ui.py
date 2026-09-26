#!/usr/bin/env python3
"""Drive the game's menus.

The game ignores absolute pointer warps (both ydotool --absolute and the
compositor's own movecursor): it tracks only relative motion and draws its own
cursor. So move relatively and keep track of where the cursor ended up, which
is found by diffing two frames.
"""
import subprocess
import sys
import time

MONITOR = "DP-2"
STATE = "/tmp/ror2_cursor"
TEMPLATE = "/tmp/cur_tpl.png"
# where the pointer actually points, relative to the template's top-left
HOTSPOT = (4, 8)


def shot(path):
    subprocess.run(["grim", "-o", MONITOR, path], check=True)


def pos():
    try:
        return tuple(int(v) for v in open(STATE).read().split())
    except OSError:
        return None


def set_pos(x, y):
    open(STATE, "w").write(f"{x} {y}")


def find_cursor(near=None, radius=220):
    """Locate the game's own cursor by matching its sprite.

    Frame diffing does not work here: the menu backgrounds animate (trees, water,
    particles), so the biggest change between two frames is rarely the cursor.
    The cursor is a fixed sprite though, so match on it directly. Only the bright
    interior of the triangle is scored, which is what stays constant over any
    background.
    """
    import numpy as np
    from PIL import Image
    shot("/tmp/_f.png")
    img = np.asarray(Image.open("/tmp/_f.png").convert("RGB"), dtype=np.int16)
    tpl = np.asarray(Image.open(TEMPLATE).convert("RGB"), dtype=np.int16)
    mask = tpl.sum(axis=2) > 430          # the pale fill, not the dark border or the background
    ys, xs = np.nonzero(mask)
    pts = np.stack([ys, xs], axis=1)
    vals = tpl[ys, xs]
    th, tw = tpl.shape[:2]
    # Searching the whole screen finds false matches in bright artwork, so when we
    # know roughly where the cursor was, only look around there.
    off_y = off_x = 0
    if near is None:
        near = pos()
    if near is not None:
        off_y = max(0, near[1] - HOTSPOT[1] - radius)
        off_x = max(0, near[0] - HOTSPOT[0] - radius)
        img = img[off_y:near[1] + radius, off_x:near[0] + radius]
    h, w = img.shape[:2]
    if h <= th or w <= tw:
        return None
    # score every position at once: for each sampled template pixel, shift the
    # image and accumulate the absolute difference
    acc = np.zeros((h - th, w - tw), dtype=np.int32)
    for (dy, dx), v in zip(pts[::3], vals[::3]):
        sub = img[dy:dy + h - th, dx:dx + w - tw]
        acc += np.abs(sub - v).sum(axis=2)
    idx = int(acc.argmin())
    y, x = divmod(idx, acc.shape[1])
    x += off_x; y += off_y
    set_pos(x + HOTSPOT[0], y + HOTSPOT[1])
    return x + HOTSPOT[0], y + HOTSPOT[1]


def move_to(x, y, tol=8, tries=8):
    """Converge on a target.

    Pointer acceleration means a relative move of N pixels does not travel N
    pixels, so aim, look where we actually landed, and aim again.
    """
    for _ in range(tries):
        cur = find_cursor()
        if cur is None:
            cur = find_cursor(near=(960, 540), radius=2000)
        if cur is None:
            raise SystemExit("could not locate the cursor")
        dx, dy = x - cur[0], y - cur[1]
        if abs(dx) <= tol and abs(dy) <= tol:
            return cur
        # small steps stay in the pointer's linear range
        step = 40
        while dx or dy:
            sx = max(-step, min(step, dx))
            sy = max(-step, min(step, dy))
            subprocess.run(["ydotool", "mousemove", "-x", str(sx), "-y", str(sy)], check=True)
            dx -= sx; dy -= sy
        time.sleep(0.3)
    return find_cursor()


def click():
    subprocess.run(["ydotool", "click", "0xC0"], check=True)
    time.sleep(0.6)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "find":
        print(find_cursor())
    elif cmd == "findall":
        set_pos(960, 540); print(find_cursor(near=(960, 540), radius=2000))
    elif cmd == "move":
        move_to(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == "click":
        move_to(int(sys.argv[2]), int(sys.argv[3])); click()
    elif cmd == "shot":
        shot(sys.argv[2])
    elif cmd == "set":
        set_pos(int(sys.argv[2]), int(sys.argv[3]))
