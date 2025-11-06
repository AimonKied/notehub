#!/bin/bash
# Installation script for NoteHub

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create a launcher script in ~/.local/bin
mkdir -p ~/.local/bin
cat > ~/.local/bin/notehub << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 main.py
EOF

# Make the launcher executable
chmod +x ~/.local/bin/notehub

# Create desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/notehub.desktop << EOF
[Desktop Entry]
Name=NoteHub
Comment=Note-taking app with command line interface
Exec=$HOME/.local/bin/notehub
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
f

echo "✓ NoteHub installed successfully!"
echo ""
echo "You can now:"
echo "  1. Run 'notehub' from the terminal"
echo "  2. Find 'NoteHub' in your application menu"
echo ""
echo "Note: If 'notehub' command is not found, add ~/.local/bin to your PATH:"
echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
echo "  source ~/.bashrc"
