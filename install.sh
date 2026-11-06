#!/bin/sh
# numquiz installer – no pip/pipx needed, only python3.
#
#   install / update:  curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh | sh
#   uninstall:         curl -fsSL https://raw.githubusercontent.com/jonoboderbonobo/numquiz/main/install.sh | sh -s uninstall
#
# Installs to ~/.local/bin by default; override with NUMQUIZ_DIR=/some/dir.
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
    if [ -d "$CONF" ]; then
        say "Your settings are kept in $CONF (delete with: rm -r $CONF)"
    fi
}

install() {
    command -v python3 >/dev/null 2>&1 || die "python3 is required but was not found"
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
        *)
            say ""
            say "Note: $DIR is not on your PATH yet. Add this line to ~/.bashrc or ~/.zshrc:"
            say "    export PATH=\"$DIR:\$PATH\""
            say "then open a new terminal (or run $BIN directly)."
            ;;
    esac
}

case "${1:-install}" in
    install|update) install ;;
    uninstall|remove) uninstall ;;
    *) die "unknown command '$1' (use: install, update or uninstall)" ;;
esac
