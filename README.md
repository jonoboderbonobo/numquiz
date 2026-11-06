# numquiz

A small terminal quiz for practising conversions between **binary**, **hex** and **decimal** (0–15, i.e. up to `0b1111`).
No score, no timer – just a question, your answer, and whether it was right.

```
 numquiz · Random mix (all directions)
     0x3  → dec       3       ✓
      14  dec → hex   0xA     ✗  0xE
     0x7  → bin       ?
──────────────── /options · /skip · /clear · /help · /quit ─
❯ 0b0111
```

## Install

Works on **Linux** and **macOS** (Terminal, iTerm2, …). Needs Python 3.8+.

### macOS: get Python first (one time)

Newer Macs don't have Python ready out of the box. Open Terminal and run:

```bash
xcode-select --install     # installs Apple's command line tools incl. python3 (a few minutes)
```

(or `brew install python` if you use [Homebrew](https://brew.sh)). Check with `python3 --version`.
Linux usually has Python already; otherwise e.g. `sudo apt install python3`.

### Quick way – one line, nothing else needed

```bash
curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh | sh
```

This puts `numquiz` into `~/.local/bin` (change with `NUMQUIZ_DIR=/some/dir`).
If that folder isn't on your PATH yet – the default on macOS – the installer adds it to your shell
config (`~/.zshrc` on macOS, `~/.bashrc` on Linux). Open a new terminal window afterwards and run `numquiz`.

| | |
|---|---|
| Update | run the same command again |
| Uninstall | `curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh \| sh -s uninstall` |

Uninstalling also removes the PATH line the installer added. Your settings in `~/.config/numquiz` are kept.

### With pipx or uv

If you already use [pipx](https://pipx.pypa.io) or [uv](https://docs.astral.sh/uv/):

```bash
pipx install git+https://github.com/jonoboderbonobo/numquiz.git
# or
uv tool install git+https://github.com/jonoboderbonobo/numquiz.git
```

| | pipx | uv |
|---|---|---|
| Update | `pipx upgrade numquiz` | `uv tool upgrade numquiz` |
| Uninstall | `pipx uninstall numquiz` | `uv tool uninstall numquiz` |

Use only one of the two ways, since both put a `numquiz` command into `~/.local/bin`.

### Windows

Use [WSL](https://learn.microsoft.com/windows/wsl/), or the pipx way (it pulls in `windows-curses` automatically; untested).

## Usage

Type your answer at the bottom and press Enter; it moves up next to its question.
Answers may be written with or without prefix and leading zeros (`101`, `0101`, `0b0101` are all fine).

| Command | |
|---|---|
| `/options` or Tab | settings screen |
| `/skip` | show the answer, next question |
| `/clear` or Ctrl+L | clear the board |
| `/help` | list commands |
| `/quit` or Ctrl+D | exit |

### Settings

The settings screen has two tabs (←/→ to switch, ↑/↓ to move, Enter to select, Esc to go back):

- **Mode** – binary → decimal, decimal → binary, binary ↔ hex, hex ↔ decimal, or a random mix
- **Display** – how numbers are shown
  - binary: `10`, `0010`, `0b10`, `0b0010` (default)
  - hex: `A`, `a`, `0xA` (default), `0xa`
  - decimal: `5` (default), `05`

When a prefix is shown, the question leaves out the `bin`/`hex` label since the prefix already says it.

Settings are saved in `~/.config/numquiz/settings.json`.

## Releasing (maintainer notes)

1. Bump `__version__` in `numquiz.py`.
2. Commit, then `git tag v0.2.0 && git push --tags`.
3. The GitHub Action builds and publishes to PyPI.

## License

MIT
