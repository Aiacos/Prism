#!/usr/bin/env bash

# uninstall.sh - Prism Pipeline Linux Uninstaller
#
# This script launches the Prism Installer in uninstall mode.
# It removes Prism from the system and cleans up configuration files.
# Includes a pause at the end so users can see the uninstall messages.

# Get script directory (handles symlinks and relative paths)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect Python executable
# First, try bundled Python 3.11
if [ -f "$SCRIPT_DIR/Python311/bin/python3" ]; then
    PYTHON_PATH="$SCRIPT_DIR/Python311/bin/python3"
# Fallback to system Python 3
else
    PYTHON_PATH="python3"
fi

# Verify Python is available
if ! command -v "$PYTHON_PATH" &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3 or ensure Python311/bin/python3 exists." >&2
    exit 1
fi

# On Linux, use system libraries instead of bundled PythonLibs
# Set PRISM_NO_LIBS=1 to skip the bundled libraries check
if [ "$(uname -s)" = "Linux" ]; then
    export PRISM_NO_LIBS=1
fi

# Launch Prism Uninstaller (pass all arguments through)
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismInstaller.py" uninstall "$@"

# Pause at end so users can see uninstall messages
echo ""
read -p "Press Enter to close this window..."

exit 0
