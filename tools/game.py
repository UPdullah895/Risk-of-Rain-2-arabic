#!/usr/bin/env python3
"""Start/stop the game without killing the shell that asks.

`pkill -f "Risk of Rain 2.exe"` matches its own command line, and so does any
shell running it, so a naive kill takes this session down with the game. Match
on the executable path instead, and never touch anything in our own ancestry.
"""
import os
import signal
import subprocess
import sys
import time

APPID = "632360"
EXE = "Risk of Rain 2.exe"


def ancestry() -> set:
    seen, pid = set(), os.getpid()
    while pid > 1:
        seen.add(pid)
        try:
            pid = int(open(f"/proc/{pid}/stat").read().rsplit(") ", 1)[1].split()[1])
        except OSError:
            break
    return seen


def game_pids() -> list:
    mine = ancestry()
    out = subprocess.run(["ps", "-eo", "pid,cmd"], capture_output=True, text=True).stdout
    pids = []
    for line in out.splitlines()[1:]:
        pid, _, cmd = line.strip().partition(" ")
        pid = int(pid)
        # the real game is launched by absolute path; our own tooling is not
        if pid not in mine and EXE in cmd and "/steamapps/common/" in cmd:
            pids.append(pid)
    return pids


def stop(timeout=20) -> None:
    pids = game_pids()
    if not pids:
        print("not running")
        return
    print("stopping", pids)
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for p in pids:
            try:
                os.kill(p, sig)
            except ProcessLookupError:
                pass
        for _ in range(timeout):
            if not game_pids():
                print("stopped")
                return
            time.sleep(1)
    print("still running:", game_pids())


def start(wait=90) -> None:
    subprocess.Popen(["steam", "-applaunch", APPID],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    for i in range(wait):
        time.sleep(1)
        if game_pids():
            print(f"running after {i + 1}s")
            return
    print("did not appear")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "stop":
        stop()
    elif cmd == "start":
        start()
    elif cmd == "restart":
        stop(); time.sleep(3); start()
    else:
        print(game_pids() or "not running")
