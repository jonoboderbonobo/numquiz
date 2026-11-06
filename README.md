# numquiz

A small terminal quiz for practising conversions between **binary**, **hex** and **decimal** (0–15, i.e. up to `0b1111`).
No score, no timer – just a question, your answer, and whether it was right.

```
 numquiz · Random mix (all directions)
     0x3  → dec       3       ✓
      14  dec → hex   0xA     ✗  0xE
     0x7  → bin       ?
──────────────────────── /options · /skip · /help · /quit ─
❯ 0b0111
```

## Install

Needs Python 3.8+. The recommended way is [pipx](https://pipx.pypa.io) (or [uv](https://docs.astral.sh/uv/)), which installs it as its own command:

```bash
pipx install numquiz            # or: uv tool install numquiz
```

Then just run `numquiz`.

| | pipx | uv |
|---|---|---|
| Update | `pipx upgrade numquiz` | `uv tool upgrade numquiz` |
| Uninstall | `pipx uninstall numquiz` | `uv tool uninstall numquiz` |

Latest development version straight from GitHub:

```bash
pipx install git+https://github.com/jonoboderbonobo/numquiz.git
```

## Usage

Type your answer at the bottom and press Enter; it moves up next to its question.
Answers may be written with or without prefix and leading zeros (`101`, `0101`, `0b0101` are all fine).

| Command | |
|---|---|
| `/options` or Tab | settings screen |
| `/skip` | show the answer, next question |
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
