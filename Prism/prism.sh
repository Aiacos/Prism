#!/usr/bin/env bash

# prism.sh - Prism Pipeline Linux Launcher
#
# This script launches the Prism Core application in the background.
# It detects the bundled Python 3.11 or falls back to system Python 3.
# The script exits immediately without waiting for the process to finish.

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

# Launch Prism Core in background and exit immediately
# The '&' puts the process in the background, and 'exit 0' exits without waiting
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismCore.py" "$@" &

# Exit immediately (don't wait for background process)
exit 0
