#!/usr/bin/env bash

# setup.sh - Prism Pipeline Linux Setup/Installer
#
# This script launches the Prism Installer for initial setup and configuration.
# It supports the --system flag for system-wide installation (requires root).
# Includes optional pause at the end for script window to remain visible.

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

# Check for --system flag (requires root privileges)
if [ "$1" == "--system" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "System-wide installation requires root privileges." >&2
        echo "Please run: sudo $0 --system" >&2
        exit 1
    fi
fi

# On Linux, use system libraries instead of bundled PythonLibs
# Set PRISM_NO_LIBS=1 to skip the bundled libraries check
if [ "$(uname -s)" = "Linux" ]; then
    export PRISM_NO_LIBS=1
fi

# Launch Prism Installer
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismInstaller.py" "$@"

# Optional pause at end (unless --no-pause flag is provided)
# This keeps the terminal window open so users can see any messages
if [ "$1" != "--no-pause" ]; then
    echo ""
    read -p "Press Enter to close this window..."
fi

exit 0
