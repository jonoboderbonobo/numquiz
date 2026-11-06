#!/bin/sh
# numquiz installer – no pip/pipx needed, only python3.
#
#   install / update:  curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh | sh
#   uninstall:         curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh | sh -s uninstall
#
# Works on Linux and macOS. Installs to ~/.local/bin by default (override with
# NUMQUIZ_DIR=/some/dir) and adds that folder to your shell's PATH if needed.
set -eu

URL="${NUMQUIZ_URL:-https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/numquiz.py}"
DIR="${NUMQUIZ_DIR:-$HOME/.local/bin}"
BIN="$DIR/numquiz"
CONF="$HOME/.config/numquiz"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

uninstall() {
    if [ -e "$BIN" ] || [ -L "$BIN" ]; then
        rm -f "$BIN"
        say "Removed $BIN"
    else
        say "numquiz is not installed in $DIR"
    fi
    for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
        if grep -qsF "# added by numquiz installer" "$rc"; then
            tmp=$(mktemp)
            grep -vF "# added by numquiz installer" "$rc" > "$tmp" && cat "$tmp" > "$rc"
            rm -f "$tmp"
            say "Removed the PATH line from $rc"
        fi
    done
    if [ -d "$CONF" ]; then
        say "Your settings are kept in $CONF (delete with: rm -r $CONF)"
    fi
}

need_python() {
    if [ "$(uname -s)" = Darwin ]; then
        hint="On macOS run:  xcode-select --install   (or: brew install python), then run this installer again."
    else
        hint="Install it with your package manager, e.g.  sudo apt install python3"
    fi
    die "python3 is required but not available.
$hint"
}

# Adds DIR to PATH in the user's shell startup file (once).
add_to_path() {
    case "${SHELL:-}" in
        */zsh)  rc="$HOME/.zshrc" ;;
        */bash) if [ "$(uname -s)" = Darwin ]; then rc="$HOME/.bash_profile"; else rc="$HOME/.bashrc"; fi ;;
        */fish) rc="" ;;
        *)      rc="$HOME/.profile" ;;
    esac
    if [ -z "$rc" ]; then
        say ""
        say "Note: $DIR is not on your PATH. For fish run:  fish_add_path $DIR"
        return
    fi
    line="export PATH=\"$DIR:\$PATH\"  # added by numquiz installer"
    if ! grep -qsF "$line" "$rc"; then
        printf '\n%s\n' "$line" >> "$rc"
        say "Added $DIR to your PATH in $rc"
    fi
    say "Open a new terminal window, then run: numquiz"
}

install() {
    # on macOS /usr/bin/python3 exists even without Python (it only opens an install dialog),
    # so actually run it instead of just checking that the command exists
    command -v python3 >/dev/null 2>&1 || need_python
    python3 -c "import sys" >/dev/null 2>&1 || need_python
    python3 -c "import curses" 2>/dev/null || die "your python3 has no curses module (on Windows use WSL or 'pipx install numquiz')"

    tmp=$(mktemp)
    trap 'rm -f "$tmp"' EXIT
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$URL" -o "$tmp" || die "download failed: $URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$tmp" "$URL" || die "download failed: $URL"
    else
        die "need curl or wget to download numquiz"
    fi
    python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$tmp" 2>/dev/null \
        || die "downloaded file is not valid Python – try again later"

    action="Installed"
    [ -e "$BIN" ] && action="Updated"
    mkdir -p "$DIR"
    rm -f "$BIN"            # replaces an old symlink instead of writing through it
    mv "$tmp" "$BIN"
    chmod 755 "$BIN"
    trap - EXIT

    say "$action $("$BIN" --version) in $BIN"
    case ":$PATH:" in
        *":$DIR:"*) say "Run it with: numquiz" ;;
        *) add_to_path ;;
    esac
}

case "${1:-install}" in
    install|update) install ;;
    uninstall|remove) uninstall ;;
    *) die "unknown command '$1' (use: install, update or uninstall)" ;;
esac
