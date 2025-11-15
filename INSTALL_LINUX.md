# Prism Pipeline - Linux Installation Guide

## System Requirements

- **Operating System:** Linux (any distribution)
- **Python:** 3.9, 3.10, or 3.11
- **Display Server:** X11 or Wayland
- **Disk Space:** ~500 MB

## Dependencies

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyside2 \
    ffmpeg \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    xdg-utils
```

### Fedora/RHEL/CentOS

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-pyside2 \
    ffmpeg \
    mesa-libGL \
    libxcb \
    xdg-utils
```

### Arch Linux

```bash
sudo pacman -S \
    python \
    python-pip \
    python-pyside2 \
    ffmpeg \
    mesa \
    xdg-utils
```

### Python Dependencies (Alternative to System Packages)

If you prefer using pip instead of system packages:

```bash
pip3 install -r requirements.txt
```

## Installation Methods

### Method 1: User Installation (Recommended - No Root Required)

1. **Download or Clone Prism:**
   ```bash
   cd ~
   git clone https://github.com/PrismPipeline/Prism.git
   cd Prism
   git checkout feature/linux-compatibility
   ```

2. **Download Dependencies** (optional):
   Download the [Prism dependencies package](https://prism-pipeline.com/downloads/) and extract:
   ```bash
   # Extract dependencies
   unzip Prism_dependencies_v2.0.5.zip
   # Copy CrossPlatform libraries
   cp -r PythonLibs/CrossPlatform Prism/PythonLibs/
   ```

3. **Run Setup:**
   ```bash
   cd Prism
   ./setup.sh
   ```

4. **Launch Prism:**
   ```bash
   ./prism.sh
   ```

### Method 2: System-Wide Installation (Requires Root)

1. **Clone to /opt:**
   ```bash
   sudo git clone https://github.com/PrismPipeline/Prism.git /opt/Prism
   cd /opt/Prism
   sudo git checkout feature/linux-compatibility
   ```

2. **Download Dependencies:**
   ```bash
   # Download and extract dependencies
   sudo unzip Prism_dependencies_v2.0.5.zip -d /opt/Prism/Prism/PythonLibs/
   ```

3. **Run Setup:**
   ```bash
   cd /opt/Prism/Prism
   sudo ./setup.sh --system
   ```

4. **Create Symlink (optional):**
   ```bash
   sudo ln -s /opt/Prism/Prism/prism.sh /usr/local/bin/prism
   ```

5. **Launch Prism:**
   ```bash
   prism
   # Or from menu: Applications > Graphics > Prism Project Browser
   ```

## DCC Integration

### Blender

Prism automatically detects Blender in:
- `/usr/bin/blender` (system package)
- `/usr/share/blender`
- `/opt/blender*` (manual installation)
- `/snap/blender/*/` (snap package)

**Manual Configuration:**
If Blender is in a custom location, specify the path in Prism Settings > DCC Apps > Blender.

### Houdini

Prism detects Houdini via:
- `$HFS` environment variable
- `/opt/hfs*` (standard Side Effects installation)

**Setup Houdini:**
1. Source Houdini environment:
   ```bash
   cd /opt/hfsXX.X.XXX
   source houdini_setup
   ```

2. Launch Prism from within Houdini environment, or set `$HFS` permanently in your shell profile.

### Nuke

Prism looks for Nuke in:
- `/usr/local/Nuke*`
- `/opt/Nuke*`

### Maya

Maya on Linux is typically in:
- `/usr/autodesk/maya*`
- Set `$MAYA_LOCATION` if in custom location

## Configuration

### XDG Directories

Prism respects XDG Base Directory specification:

- **Config:** `~/.config/Prism2` (or `$XDG_CONFIG_HOME/Prism2`)
- **Data:** `~/.local/share/Prism2` (or `$XDG_DATA_HOME/Prism2`)
- **Cache:** `~/.cache/Prism2` (or `$XDG_CACHE_HOME/Prism2`)

### Application Menu Integration

Setup creates .desktop files in:
- **User:** `~/.local/share/applications/`
- **System:** `/usr/share/applications/`

Applications appear in: **Applications > Graphics**

### Autostart (System Tray)

To enable Prism Tray on login:
1. Open Prism Settings
2. Go to "User" tab
3. Check "Launch on system startup"

This creates: `~/.config/autostart/PrismTray.desktop`

## Troubleshooting

### Prism doesn't start

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.9, 3.10, or 3.11
   ```

2. **Check dependencies:**
   ```bash
   python3 -c "from PySide2 import QtCore; print('PySide2 OK')"
   python3 -c "import imageio, numpy, psutil; print('All OK')"
   ```

3. **Check logs:**
   ```bash
   python3 ~/Prism/Prism/Scripts/PrismCore.py 2>&1 | tee prism.log
   ```

### DCC not detected

1. **Verify installation:**
   ```bash
   which blender  # Should show path
   echo $HFS      # For Houdini
   ```

2. **Manual configuration:**
   - Open Prism Settings > DCC Apps
   - Click "Add" and browse to DCC executable

### Permission errors

If you see permission errors in `~/.local/share/Prism2`:

```bash
# Fix ownership
chown -R $USER:$USER ~/.local/share/Prism2
chown -R $USER:$USER ~/.config/Prism2

# Fix permissions
chmod -R u+rwX ~/.local/share/Prism2
chmod -R u+rwX ~/.config/Prism2
```

### Qt/PySide errors

If you see Qt-related errors:

```bash
# Option 1: Use system Qt
sudo apt install python3-pyside2  # Ubuntu/Debian
sudo dnf install python3-pyside2  # Fedora

# Option 2: Use pip Qt (may conflict with system Qt)
pip3 install --user PySide2
```

### Wayland issues

If running on Wayland and experiencing display issues:

```bash
# Force X11 backend
QT_QPA_PLATFORM=xcb ./prism.sh
```

## Uninstallation

### User Installation

```bash
cd ~/Prism/Prism
./uninstall.sh
```

Then remove directory:
```bash
rm -rf ~/Prism
rm -rf ~/.config/Prism2
rm -rf ~/.local/share/Prism2
rm -rf ~/.cache/Prism2
```

### System Installation

```bash
cd /opt/Prism/Prism
sudo ./uninstall.sh
```

Then remove directory:
```bash
sudo rm -rf /opt/Prism
```

## Getting Help

- **Forum:** https://prism-pipeline.com/forum/
- **Documentation:** https://prism-pipeline.com/docs/
- **GitHub Issues:** https://github.com/PrismPipeline/Prism/issues
- **Discord:** (if available)

## Known Issues

1. **System Tray:** Some desktop environments (GNOME) don't support system tray icons by default. Install "AppIndicator" extension.

2. **Snap Blender:** Snap-installed Blender may have sandboxing restrictions. Prefer system package or manual installation.

3. **Wayland:** Full Wayland support is experimental. Use X11 session if issues occur.

## Contributing

Linux support is actively being developed. Contributions welcome!

See `LINUX_COMPATIBILITY_ANALYSIS.md` for development roadmap.
