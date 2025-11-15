# PlatformUtils Module

**Location:** `Prism/Scripts/PrismUtils/PlatformUtils.py`  
**Size:** 778 lines, 28 KB  
**Status:** ✓ Complete and tested

## Overview

Comprehensive cross-platform utilities for Prism Pipeline with full Linux support (XDG-compliant).

## Features

### 1. Directory Paths (XDG-compliant for Linux)

- **getConfigDir()** → Config directory
  - Windows: `%APPDATA%\Prism2`
  - Linux: `$XDG_CONFIG_HOME/Prism2` or `~/.config/Prism2`
  - macOS: `~/Library/Preferences/Prism2`

- **getDataDir()** → Data directory
  - Windows: `%PROGRAMDATA%\Prism2`
  - Linux: `$XDG_DATA_HOME/Prism2` or `~/.local/share/Prism2`
  - macOS: `~/Library/Application Support/Prism2`

- **getCacheDir()** → Cache directory
  - Windows: `%LOCALAPPDATA%\Prism2\Cache`
  - Linux: `$XDG_CACHE_HOME/Prism2` or `~/.cache/Prism2`
  - macOS: `~/Library/Caches/Prism2`

- **getDocumentsDir()** → User documents
  - Windows: Uses `SHGetFolderPath` for My Documents
  - Linux: Uses `xdg-user-dir DOCUMENTS` or `~/Documents`
  - macOS: `~/Documents`

- **getTempDir()** → Temporary files
  - Cross-platform: Uses `tempfile.gettempdir()`

### 2. Shortcuts/Desktop Files

- **createShortcut(link, target, args="", icon="", description="", workingDir="")**
  - Windows: Creates `.lnk` files via VBScript
  - Linux: Creates `.desktop` files (XDG standard)
  - macOS: Creates `.command` script launchers

### 3. File Operations

- **createSymlink(link, target)** → Cross-platform symlink/hardlink
  - Windows: Uses `mklink /H` for hard links
  - Linux/macOS: Uses `os.link()` with fallback to `os.symlink()`

- **openFolder(path)** → Open file manager
  - Windows: Uses `explorer` with `/select,` for files
  - Linux: Tries multiple file managers (xdg-open, nautilus, dolphin, etc.)
  - macOS: Uses `open` with `-R` for files

- **openFile(filepath)** → Open with default app
  - Windows: Uses `os.startfile()`
  - Linux: Uses `xdg-open`
  - macOS: Uses `open`

### 4. Process Management

- **findPrismProcesses()** → Find running Prism instances
  - Windows: Looks for `Prism.exe`
  - Linux/macOS: Searches python processes for Prism scripts

- **killProcess(pid)** → Cross-platform process termination
  - Uses `psutil` with graceful termination (5s timeout) then kill

- **isProcessRunning(name_or_cmdline)** → Check if process is running
  - Searches by process name or command line content

### 5. Admin/Elevated Execution

- **runAsAdmin(script, pythonPath=None)** → Execute with elevated privileges
  - Windows: Uses `ShellExecuteEx` with `runas` verb (UAC prompt)
  - Linux: Uses `pkexec` (graphical) or `sudo` (terminal) fallback
  - macOS: Uses `osascript` with administrator privileges

### 6. Application Detection

- **getDefaultAppForExtension(ext)** → Get default app for file extension
  - Windows: Queries registry (`HKEY_CURRENT_USER`, `HKEY_CLASSES_ROOT`)
  - Linux: Uses `xdg-mime query default` with MIME type lookup
  - macOS: Uses Launch Services via `mdls`

- **findApplication(appName, searchPaths=None, envVar=None, registryPath=None)** → Find application
  - Windows: Registry lookup → Program Files search
  - Linux: `which` command → path search with glob pattern support
  - macOS: `/Applications` lookup

## Implementation Details

### Error Handling
- All methods use `@err_catcher` decorator from `PrismUtils.Decorators`
- Comprehensive try/except blocks with detailed logging
- Graceful fallbacks where appropriate

### Platform Guards
- All platform-specific code properly guarded with `platform.system()` checks
- No hardcoded paths without platform detection
- Supports Windows, Linux (all distros), and macOS

### Dependencies
- **Standard Library:** os, sys, platform, subprocess, tempfile, logging, glob, shutil
- **Optional:** psutil (for process management)
- **Windows-only:** winreg, win32com (pywin32)
- **Decorator:** PrismUtils.Decorators.err_catcher

### XDG Compliance (Linux)
- Respects `$XDG_CONFIG_HOME`, `$XDG_DATA_HOME`, `$XDG_CACHE_HOME`
- Follows XDG Base Directory Specification
- No root permissions required for user installations
- Uses `xdg-user-dir` for localized directory names

## Usage Examples

```python
from PrismUtils.PlatformUtils import PlatformUtils

# Get config directory
config_dir = PlatformUtils.getConfigDir()

# Create desktop shortcut
PlatformUtils.createShortcut(
    link="/usr/share/applications/Prism.desktop",
    target="/usr/bin/python3",
    args="/opt/Prism/Scripts/PrismCore.py",
    icon="/opt/Prism/icon.png",
    description="Prism Pipeline"
)

# Find application
blender_path = PlatformUtils.findApplication(
    appName="blender",
    searchPaths=["/usr/bin", "/opt/blender*"],
    envVar="BLENDER_PATH"
)

# Open folder
PlatformUtils.openFolder("/path/to/folder")

# Run script as admin
PlatformUtils.runAsAdmin("import os; os.makedirs('/opt/prism')")

# Find Prism processes
processes = PlatformUtils.findPrismProcesses()
```

## Testing

Run the test suite:
```bash
python3 test_platformutils.py
```

## Integration with Prism Core

This module is designed to be used by:
- `PrismCore.py` - Replace direct Windows API calls
- `PrismInstaller.py` - Cross-platform installation
- `PrismTray.py` - Process management
- Plugin Integration files - Application detection
- `Standalone_Functions.py` - Menu/shortcut creation

## References

- XDG Base Directory Specification: https://specifications.freedesktop.org/basedir-spec/latest/
- Linux Compatibility Analysis: `LINUX_COMPATIBILITY_ANALYSIS.md`

## Status

✓ All 15 required methods implemented  
✓ Comprehensive error handling  
✓ Platform-specific implementations for Windows/Linux/macOS  
✓ XDG Base Directory compliance  
✓ Syntax validated  
✓ Import tested  
✓ Basic functionality verified  

Ready for integration into Prism Pipeline.
