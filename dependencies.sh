#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Try pipx first (recommended and safest)
if command -v pipx >/dev/null 2>&1; then
    echo "Installing with pipx..."
    while IFS= read -r package || [ -n "$package" ]; do
        [[ -z "$package" || "$package" =~ ^[[:space:]]*# ]] && continue
        package_name=$(echo "$package" | sed 's/[>=<~!].*//' | xargs)
        pipx install "$package" --force 2>/dev/null || true
    done < "$REQUIREMENTS"
    echo "Done!"
    exit 0
fi

# Suggest installing pipx if not found
echo "pipx not found. Please install it first (recommended):"
if command -v brew >/dev/null 2>&1; then
    echo "  brew install pipx"
else
    echo "  python3 -m pip install --user pipx"
fi
echo "  pipx ensurepath"
echo ""
echo "Or, to continue anyway, use one of these:"
echo "  1. Create a venv manually: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
echo "  2. Use pip3 --user with --break-system-packages (safe when combined with --user)"
echo ""
read -p "Continue with pip3 --user anyway? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Try pip3 --user only if user confirms
if command -v pip3 >/dev/null 2>&1; then
    echo "Installing with pip3 --user..."
    pip3 install --user --break-system-packages -r "$REQUIREMENTS"
    
    # Warn about PATH if needed
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "Warning: Add ~/.local/bin to your PATH:"
        echo 'export PATH="$HOME/.local/bin:$PATH"'
    fi
    echo "Done!"
    exit 0
fi

# Fallback to venv
echo "Installing in virtual environment..."
VENV_DIR="${SCRIPT_DIR}/venv"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install -r "$REQUIREMENTS"
deactivate

echo "Done! Activate with: source venv/bin/activate"