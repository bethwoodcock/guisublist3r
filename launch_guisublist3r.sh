#!/usr/bin/env bash
# GUI Sublist3r - macOS / Linux launcher
# Make executable once:  chmod +x launch_guisublist3r.sh
# Then double-click in file manager, or run: ./launch_guisublist3r.sh

cd "$(dirname "$0")"

# Prefer python3, fall back to python
if command -v python3 &>/dev/null; then
    python3 gui_sublist3r.py
elif command -v python &>/dev/null; then
    python gui_sublist3r.py
else
    echo "Python not found. Install Python 3 from https://www.python.org/"
    read -p "Press Enter to exit..."
fi
