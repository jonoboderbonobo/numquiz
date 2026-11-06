#!/usr/bin/env python3
"""numquiz - practice converting between binary, hex and decimal (0..15).

Full-screen terminal app. Questions scroll up, you type at the bottom.

Commands:
  /options  (or Tab)  open the settings screen
  /skip               show the answer and move on
  /help               show commands
  /quit   (or Ctrl+D) exit
"""
import curses
import sys
import json
import locale
import os
import random

__version__ = "0.1.0"

MAX = 0b1111
CONFIG = os.path.expanduser("~/.config/numquiz/settings.json")

NAMES = {"bin": "binary", "hex": "hex", "dec": "decimal"}
MODES = [
    ("bin", "dec"), ("dec", "bin"),
    ("bin", "hex"), ("hex", "bin"),
    ("hex", "dec"), ("dec", "hex"),
    ("mix", "mix"),
]

# display settings: key -> (title, example number, [(value, description)])
DISPLAY = [
    ("bin", "Binary", 2, [
        ("plain", "no padding"),
        ("pad", "padded to 4 digits"),
        ("prefix", "with 0b prefix"),
        ("prefixpad", "0b prefix, padded"),
    ]),
    ("hex", "Hex", 10, [
        ("upper", "uppercase"),
        ("lower", "lowercase"),
        ("prefix", "with 0x prefix"),
        ("prefixlower", "0x prefix, lowercase"),
    ]),
    ("dec", "Decimal", 5, [
        ("plain", "no padding"),
        ("pad", "padded to 2 digits"),
    ]),
]

HELP = [
    "Commands:",
    "  /options  (or Tab)  settings: conversion mode + number display",
    "  /skip               show the answer and move on",
    "  /quit   (or Ctrl+D) exit",
    "Answers may be written with or without prefix / leading zeros.",
]


class State:
    def __init__(self):
        self.mode = MODES[0]
        self.fmt = {"bin": "prefixpad", "hex": "prefix", "dec": "plain"}
        self.load()

    def load(self):
        try:
            with open(CONFIG) as f:
                d = json.load(f)
            m = tuple(d.get("mode", self.mode))
            if m in MODES:
                self.mode = m
            for k, _, _, opts in DISPLAY:
                if d.get("fmt", {}).get(k) in [o[0] for o in opts]:
                    self.fmt[k] = d["fmt"][k]
        except (OSError, ValueError, TypeError):
            pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
            with open(CONFIG, "w") as f:
                json.dump({"mode": list(self.mode), "fmt": self.fmt}, f)
        except OSError:
            pass


def fmt(n, base, style):
    if base == "bin":
        s = format(n, "b")
        if "pad" in style:
            s = s.zfill(4)
        return "0b" + s if "prefix" in style else s
    if base == "hex":
        s = format(n, "x" if "lower" in style else "X")
        return "0x" + s if "prefix" in style else s
    return str(n).zfill(2) if style == "pad" else str(n)


def parse(answer, base):
    s = answer.strip().lower().replace(" ", "").replace("_", "")
    if s[:2] == {"bin": "0b", "hex": "0x", "dec": "0d"}[base]:
        s = s[2:]
    try:
        return int(s, {"bin": 2, "hex": 16, "dec": 10}[base]) if s else None
    except ValueError:
        return None


def mode_label(mode):
    if mode[0] == "mix":
        return "Random mix (all directions)"
    return f"{NAMES[mode[0]].capitalize()} → {NAMES[mode[1]]}"


def put(win, y, x, text, attr=0):
    """addstr that clips to the window and never raises."""
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w:
        return x
    text = text[: max(0, w - x - 1)]
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass
    return x + len(text)


ESC_SEQ = {"[A": curses.KEY_UP, "[B": curses.KEY_DOWN, "[C": curses.KEY_RIGHT, "[D": curses.KEY_LEFT,
           "OA": curses.KEY_UP, "OB": curses.KEY_DOWN, "OC": curses.KEY_RIGHT, "OD": curses.KEY_LEFT,
           "[Z": curses.KEY_BTAB}


def get_ch(scr):
    """get_wch where available; some curses builds (e.g. older macOS ones) only have getch."""
    if hasattr(scr, "get_wch"):
        return scr.get_wch()
    k = scr.getch()
    if k == -1:
        raise curses.error("no input")
    return chr(k) if 0 <= k < 256 else k


def read_key(scr):
    """get_wch, but also decodes raw arrow-key escape sequences that curses missed."""
    k = get_ch(scr)
    if k != "\x1b":
        return k
    scr.nodelay(True)
    seq = ""
    try:
        while len(seq) < 2:
            try:
                c = get_ch(scr)
            except curses.error:
                break
            seq += c if isinstance(c, str) else ""
    finally:
        scr.nodelay(False)
    if not seq:
        return "\x1b"
    return ESC_SEQ.get(seq, None)


# ---------------------------------------------------------------- settings

def settings_screen(scr, st, C):
    tabs = ["Mode", "Display"]
    tab = 0
    disp_rows = [(k, v) for k, _, _, opts in DISPLAY for v, _ in opts]
    cur = [MODES.index(st.mode), disp_rows.index(("bin", st.fmt["bin"]))]

    while True:
        scr.erase()
        h, w = scr.getmaxyx()
        put(scr, 0, 0, " numquiz · settings ".ljust(w), C["bar"])

        x = 2
        for i, t in enumerate(tabs):
            x = put(scr, 2, x, f" {t} ", C["tab_on"] if i == tab else C["dim"]) + 2
        put(scr, 3, 2, "─" * (w - 4), C["dim"])

        y = 5
        if tab == 0:
            put(scr, y, 4, "Conversion", curses.A_BOLD)
            y += 2
            for i, m in enumerate(MODES):
                sel = i == cur[0]
                on = m == st.mode
                put(scr, y, 4, "❯" if sel else " ", C["accent"])
                put(scr, y, 6, ("◉ " if on else "○ ") + mode_label(m),
                    C["accent"] | curses.A_BOLD if sel else 0)
                y += 1
        else:
            row = 0
            for k, title, ex, opts in DISPLAY:
                put(scr, y, 4, title, curses.A_BOLD)
                y += 1
                for v, desc in opts:
                    sel = row == cur[1]
                    on = st.fmt[k] == v
                    put(scr, y, 4, "❯" if sel else " ", C["accent"])
                    x = put(scr, y, 6, ("◉ " if on else "○ ") + fmt(ex, k, v).ljust(8),
                            C["accent"] | curses.A_BOLD if sel else 0)
                    put(scr, y, x + 1, desc, C["dim"])
                    y += 1
                    row += 1
                y += 1
            n = 10
            prev = " · ".join(f"{k} {fmt(n, k, st.fmt[k])}" for k in ("bin", "hex", "dec"))
            put(scr, y, 4, "Preview: ", C["dim"])
            put(scr, y, 13, prev, curses.A_BOLD)

        put(scr, h - 1, 2, "←/→ tab · ↑/↓ move · Enter select · Esc back", C["dim"])
        scr.refresh()

        k = read_key(scr)
        if k in (curses.KEY_LEFT, curses.KEY_BTAB):
            tab = (tab - 1) % len(tabs)
        elif k in (curses.KEY_RIGHT, "\t"):
            tab = (tab + 1) % len(tabs)
        elif k in (curses.KEY_UP, "k"):
            cur[tab] = (cur[tab] - 1) % (len(MODES) if tab == 0 else len(disp_rows))
        elif k in (curses.KEY_DOWN, "j"):
            cur[tab] = (cur[tab] + 1) % (len(MODES) if tab == 0 else len(disp_rows))
        elif k in ("\n", "\r", " ", curses.KEY_ENTER):
            if tab == 0:
                st.mode = MODES[cur[0]]
            else:
                key, val = disp_rows[cur[1]]
                st.fmt[key] = val
            st.save()
        elif k in ("\x1b", "q", "\x04"):
            return


# ---------------------------------------------------------------- game

class Question:
    def __init__(self, mode, last=None):
        while True:
            src, dst = random.choice(MODES[:-1]) if mode[0] == "mix" else mode
            self.n, self.src, self.dst = random.randint(0, MAX), src, dst
            if last is None or (self.n, src, dst) != (last.n, last.src, last.dst):
                break
        self.answer = None   # what the user typed
        self.result = None   # "ok" / "bad" / "skip"


def draw_question(scr, y, q, st, C):
    shown = fmt(q.n, q.src, st.fmt[q.src])
    x = put(scr, y, 2, shown.rjust(6), curses.A_BOLD)
    # a 0b/0x prefix already says what the number is, so the label is only needed without one
    label = f"→ {q.dst}" if "prefix" in st.fmt[q.src] else f"{q.src} → {q.dst}"
    x = put(scr, y, x, f"  {label:<10}  ", C["dim"])
    if q.result is None:
        put(scr, y, x, "?", C["accent"])
    elif q.result == "skip":
        put(scr, y, x, f"skipped · {fmt(q.n, q.dst, st.fmt[q.dst])}", C["dim"])
    else:
        x = put(scr, y, x, q.answer.ljust(7))
        if q.result == "ok":
            put(scr, y, x, " ✓", C["ok"])
        else:
            put(scr, y, x, f" ✗  {fmt(q.n, q.dst, st.fmt[q.dst])}", C["bad"])


def game(scr):
    curses.curs_set(1)
    curses.use_default_colors()
    for i, c in enumerate((curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_CYAN), 1):
        curses.init_pair(i, c, -1)
    C = {
        "ok": curses.color_pair(1) | curses.A_BOLD,
        "bad": curses.color_pair(2) | curses.A_BOLD,
        "accent": curses.color_pair(3),
        "dim": curses.A_DIM,
        "bar": curses.A_REVERSE,
        "tab_on": curses.color_pair(3) | curses.A_REVERSE | curses.A_BOLD,
    }

    st = State()
    log = []   # Question objects or ("text", str) lines
    q = Question(st.mode)
    buf = ""

    while True:
        scr.erase()
        h, w = scr.getmaxyx()
        put(scr, 0, 0, f" numquiz · {mode_label(st.mode)} ".ljust(w), C["bar"])

        # history, bottom-aligned above the input area, current question last
        items = log + [q]
        area = h - 3
        for i, item in enumerate(items[-area:] if area > 0 else []):
            y = 1 + area - min(len(items), area) + i
            if isinstance(item, Question):
                draw_question(scr, y, item, st, C)
            else:
                put(scr, y, 2, item[1], C["dim"])

        put(scr, h - 2, 0, "─" * w, C["dim"])
        hint = " /options · /skip · /help · /quit "
        put(scr, h - 2, max(0, w - len(hint) - 2), hint, C["dim"])
        x = put(scr, h - 1, 0, "❯ ", C["accent"] | curses.A_BOLD)
        put(scr, h - 1, x, buf)
        try:
            scr.move(h - 1, min(x + len(buf), w - 1))
        except curses.error:
            pass
        scr.refresh()

        try:
            k = read_key(scr)
        except KeyboardInterrupt:
            return
        if k == "\x04":
            return
        if k is None or k == curses.KEY_RESIZE or isinstance(k, int) and k not in (
                curses.KEY_BACKSPACE, curses.KEY_ENTER):
            continue
        if k == "\t":
            k, buf = "\n", "/options"
        if k in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            buf = buf[:-1]
        elif k == "\x1b":
            buf = ""
        elif k == "\x15":          # Ctrl+U
            buf = ""
        elif k in ("\n", "\r", curses.KEY_ENTER):
            cmd, buf = buf.strip(), ""
            low = cmd.lower()
            if not cmd:
                continue
            if low in ("/quit", "/exit", "/q"):
                return
            if low in ("/options", "/o", "/settings"):
                old = st.mode
                settings_screen(scr, st, C)
                if st.mode != old:
                    log.append(("text", f"── mode: {mode_label(st.mode)} ──"))
                    q = Question(st.mode)
                continue
            if low in ("/help", "/h", "?"):
                log.extend(("text", line) for line in HELP)
                continue
            if low == "/skip":
                q.result = "skip"
            elif cmd.startswith("/"):
                log.append(("text", f"unknown command {cmd} – try /help"))
                continue
            else:
                q.answer = cmd
                q.result = "ok" if parse(cmd, q.dst) == q.n else "bad"
            log.append(q)
            log = log[-500:]
            q = Question(st.mode, last=q)
        elif isinstance(k, str) and k.isprintable() and len(buf) < 30:
            buf += k


def main():
    args = sys.argv[1:]
    if args and args[0] in ("-V", "--version"):
        print(f"numquiz {__version__}")
        return
    if args:
        print(__doc__.strip())
        print("\nUpdate:    pipx upgrade numquiz\nUninstall: pipx uninstall numquiz")
        return
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    os.environ.setdefault("ESCDELAY", "25")
    try:
        curses.wrapper(game)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
