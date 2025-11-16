# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.


import os
import sys
import platform
import subprocess
import tempfile
import logging
import glob
import shutil

from PrismUtils.Decorators import err_catcher


logger = logging.getLogger(__name__)


class PlatformUtils:
    """Cross-platform utilities for Prism Pipeline.

    This module provides platform-specific abstractions for:
    - Directory paths (XDG-compliant for Linux)
    - Shortcuts/Desktop files
    - File operations
    - Process management
    - Admin/Elevated execution
    - Application detection
    """

    # ========================================
    # Directory Paths (XDG-compliant for Linux)
    # ========================================

    @staticmethod
    @err_catcher(name=__name__)
    def getConfigDir():
        """Get the configuration directory for the current platform.

        Returns:
            str: Path to config directory
                - Windows: %APPDATA%\\Prism2
                - Linux: $XDG_CONFIG_HOME/Prism2 or ~/.config/Prism2
                - macOS: ~/Library/Preferences/Prism2
        """
        if platform.system() == "Windows":
            return os.path.join(os.environ.get("APPDATA", ""), "Prism2")
        elif platform.system() == "Linux":
            xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            return os.path.join(xdg_config, "Prism2")
        elif platform.system() == "Darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Preferences", "Prism2")
        else:
            return os.path.join(os.path.expanduser("~"), ".config", "Prism2")

    @staticmethod
    @err_catcher(name=__name__)
    def getCacheDir():
        """Get the cache directory for the current platform.

        Returns:
            str: Path to cache directory
                - Windows: %LOCALAPPDATA%\\Prism2\\Cache
                - Linux: $XDG_CACHE_HOME/Prism2 or ~/.cache/Prism2
                - macOS: ~/Library/Caches/Prism2
        """
        if platform.system() == "Windows":
            return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Prism2", "Cache")
        elif platform.system() == "Linux":
            xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
            return os.path.join(xdg_cache, "Prism2")
        elif platform.system() == "Darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Caches", "Prism2")
        else:
            return os.path.join(os.path.expanduser("~"), ".cache", "Prism2")

    @staticmethod
    @err_catcher(name=__name__)
    def getTempDir():
        """Get the temporary directory for the current platform.

        Returns:
            str: Path to temp directory
        """
        return tempfile.gettempdir()

    @staticmethod
    @err_catcher(name=__name__)
    def getDocumentsDir():
        """
        Get the user's Documents directory in a cross-platform way.

        Returns:
            str: Path to the user's Documents directory
        """
        if platform.system() == "Windows":
            import ctypes.wintypes
            CSIDL_PERSONAL = 5       # My Documents
            SHGFP_TYPE_CURRENT = 0   # Get current, not default value

            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            return buf.value
        elif platform.system() == "Linux":
            # Try xdg-user-dir first (respects user configuration)
            try:
                docs = subprocess.check_output(['xdg-user-dir', 'DOCUMENTS'],
                                             stderr=subprocess.DEVNULL).decode().strip()
                if docs and os.path.exists(docs):
                    return docs
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            # Fallback to standard location
            return os.path.expanduser("~/Documents")
        elif platform.system() == "Darwin":
            return os.path.expanduser("~/Documents")
        else:
            return os.path.expanduser("~")

    @staticmethod
    @err_catcher(name=__name__)
    def getDataDir():
        """
        Get the system data directory in a cross-platform way.
        Uses XDG Base Directory specification on Linux.

        Returns:
            str: Path to the data directory
        """
        if platform.system() == "Windows":
            return os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        elif platform.system() == "Linux":
            # XDG Base Directory - user-specific, no root required
            return os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        elif platform.system() == "Darwin":
            return os.path.expanduser("~/Library/Application Support")
        else:
            return os.path.expanduser("~/.local/share")

    @staticmethod
    def createShortcut(link, target, args="", icon="", workingDir="", ignoreError=False):
        """
        Create a shortcut/launcher in a cross-platform way.
        Creates .lnk files on Windows, .desktop files on Linux.

        Args:
            link: Path where the shortcut should be created
            target: Path to the target executable/file
            args: Command line arguments
            icon: Path to icon file
            workingDir: Working directory for the shortcut
            ignoreError: If True, don't show warnings on failure

        Returns:
            bool: True if successful, False otherwise
        """
        if platform.system() == "Windows":
            import tempfile

            link = link.replace("/", "\\")
            target = target.replace("/", "\\")

            logger.debug("creating shortcut: %s - target: %s - args: %s" % (link, target, args))

            c = (
                'Set oWS = WScript.CreateObject("WScript.Shell")\n'
                'sLinkFile = "%s"\n'
                "Set oLink = oWS.CreateShortcut(sLinkFile)\n"
                'oLink.TargetPath = "%s"\n'
                'oLink.Arguments = "%s"\n'
                "oLink.Save"
            ) % (link, target, args)

            tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".vbs")
            try:
                tmp.write(c)
                tmp.close()
                cmd = "cscript /nologo %s" % tmp.name
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                result = proc.communicate()
            except Exception as e:
                result = str(e)
            finally:
                tmp.close()
                os.remove(tmp.name)

            if os.path.exists(link):
                return True
            else:
                if not ignoreError:
                    logger.warning("failed to create shortcut: %s %s" % (link, result))
                return False

        elif platform.system() in ["Linux", "Darwin"]:
            # Create .desktop file for Linux
            logger.debug("creating desktop entry: %s - target: %s - args: %s" % (link, target, args))

            # Ensure link ends with .desktop
            if not link.endswith('.desktop'):
                link = link + '.desktop'

            # Get the name from the link filename
            name = os.path.basename(link).replace('.desktop', '').replace('_', ' ')

            # Build .desktop file content
            desktop_content = "[Desktop Entry]\n"
            desktop_content += "Version=1.0\n"
            desktop_content += "Type=Application\n"
            desktop_content += "Name=%s\n" % name
            desktop_content += "Exec=%s %s\n" % (target, args) if args else "Exec=%s\n" % target
            desktop_content += "Icon=%s\n" % icon if icon else "Icon=%s\n" % target
            desktop_content += "Terminal=false\n"
            desktop_content += "Categories=Graphics;\n"
            if workingDir:
                desktop_content += "Path=%s\n" % workingDir

            try:
                # Ensure parent directory exists
                link_dir = os.path.dirname(link)
                if link_dir and not os.path.exists(link_dir):
                    os.makedirs(link_dir, exist_ok=True)

                # Write .desktop file
                with open(link, 'w') as f:
                    f.write(desktop_content)

                # Make executable
                os.chmod(link, 0o755)

                return True
            except Exception as e:
                if not ignoreError:
                    logger.warning("failed to create desktop entry: %s - %s" % (link, str(e)))
                return False
        else:
            if not ignoreError:
                logger.warning("createShortcut not implemented for platform: %s" % platform.system())
            return False

    @staticmethod
    def createSymlink(link, target):
        """
        Create a symbolic link or hard link in a cross-platform way.

        Args:
            link: Path where the link should be created
            target: Path to the target file

        Returns:
            bool: True if successful, False otherwise
        """
        if os.path.exists(link):
            os.remove(link)

        if platform.system() == "Windows":
            link = link.replace("/", "\\")
            target = target.replace("/", "\\")
            logger.debug("creating hardlink from: %s to %s" % (target, link))
            subprocess.call(["mklink", "/H", link, target], shell=True)
        else:
            # Linux/macOS - use native os functions
            logger.debug("creating hardlink from: %s to %s" % (target, link))
            try:
                # Try hard link first
                os.link(target, link)
            except (OSError, AttributeError):
                # Fallback to symbolic link
                try:
                    os.symlink(target, link)
                except Exception as e:
                    logger.warning("failed to create symlink: %s" % str(e))
                    return False

        return os.path.exists(link)

    # ========================================
    # File Operations
    # ========================================

    @staticmethod
    @err_catcher(name=__name__)
    def openFolder(path):
        """Open file manager at the specified path.

        Args:
            path (str): Path to open in file manager

        Returns:
            bool: True if successful, False otherwise
        """
        logger.debug("Opening folder: %s" % path)

        try:
            if platform.system() == "Windows":
                explorer = os.getenv("PRISM_FILE_EXPLORER", "explorer")
                if os.path.isfile(path):
                    # Select file in explorer
                    subprocess.Popen([explorer, "/select,", path])
                else:
                    subprocess.Popen([explorer, path])
                return True
            elif platform.system() == "Linux":
                # Try common file managers
                file_managers = [
                    "xdg-open",
                    "nautilus",
                    "dolphin",
                    "thunar",
                    "nemo",
                    "caja",
                    "pcmanfm"
                ]

                folder = path if os.path.isdir(path) else os.path.dirname(path)

                for fm in file_managers:
                    try:
                        subprocess.Popen([fm, folder], stderr=subprocess.DEVNULL)
                        return True
                    except FileNotFoundError:
                        continue

                logger.warning("No file manager found on Linux")
                return False
            elif platform.system() == "Darwin":
                if os.path.isfile(path):
                    subprocess.Popen(["open", "-R", path])
                else:
                    subprocess.Popen(["open", path])
                return True
            else:
                logger.warning("openFolder not implemented for platform: %s" % platform.system())
                return False
        except Exception as e:
            logger.error("Failed to open folder: %s" % e)
            return False

    @staticmethod
    @err_catcher(name=__name__)
    def openFile(filepath):
        """Open file with default application.

        Args:
            filepath (str): Path to file to open

        Returns:
            bool: True if successful, False otherwise
        """
        logger.debug("Opening file: %s" % filepath)

        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
                return True
            elif platform.system() == "Linux":
                subprocess.Popen(["xdg-open", filepath], stderr=subprocess.DEVNULL)
                return True
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", filepath])
                return True
            else:
                logger.warning("openFile not implemented for platform: %s" % platform.system())
                return False
        except Exception as e:
            logger.error("Failed to open file: %s" % e)
            return False

    # ========================================
    # Process Management
    # ========================================

    @staticmethod
    @err_catcher(name=__name__)
    def findPrismProcesses():
        """Find running Prism instances.

        Returns:
            list: List of psutil.Process objects for Prism instances
        """
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not available")
            return []

        prism_processes = []

        if platform.system() == "Windows":
            # Look for Prism.exe
            proc_names = ["Prism.exe", "python.exe", "pythonw.exe"]
        else:
            # Look for python processes running Prism scripts
            proc_names = ["python", "python3", "python2"]

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username']):
            try:
                if platform.system() == "Windows":
                    if proc.info.get('name') in proc_names:
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('Prism' in str(arg) for arg in cmdline):
                            prism_processes.append(proc)
                else:
                    # Linux/macOS: check cmdline for Prism scripts
                    if proc.info.get('name') in proc_names:
                        cmdline = proc.info.get('cmdline', [])
                        if cmdline and any('Prism' in str(arg) for arg in cmdline):
                            prism_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return prism_processes

    @staticmethod
    @err_catcher(name=__name__)
    def killProcess(pid):
        """Kill a process by PID.

        Args:
            pid (int): Process ID to kill

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
            return True
        except Exception as e:
            logger.error("Failed to kill process %s: %s" % (pid, e))
            return False

    @staticmethod
    @err_catcher(name=__name__)
    def isProcessRunning(name_or_cmdline):
        """Check if a process is running by name or command line.

        Args:
            name_or_cmdline (str): Process name or part of command line to search for

        Returns:
            bool: True if process is found, False otherwise
        """
        try:
            import psutil
        except ImportError:
            logger.warning("psutil not available")
            return False

        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                # Check name
                if proc.info.get('name', '').lower() == name_or_cmdline.lower():
                    return True

                # Check command line
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(name_or_cmdline in str(arg) for arg in cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return False

    # ========================================
    # Admin/Elevated Execution
    # ========================================

    @staticmethod
    @err_catcher(name=__name__)
    def runAsAdmin(script, pythonPath=None):
        """Execute a Python script with elevated privileges.

        Args:
            script (str): Python code to execute
            pythonPath (str): Path to Python executable (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        if not pythonPath:
            pythonPath = sys.executable

        logger.debug("Running as admin: %s" % script[:100])

        try:
            if platform.system() == "Windows":
                # Use ShellExecuteEx with runas verb
                try:
                    from win32comext.shell import shellcon
                    import win32comext.shell.shell as shell
                    import win32event
                    import win32process
                    import win32con

                    procInfo = shell.ShellExecuteEx(
                        nShow=win32con.SW_SHOWNORMAL,
                        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                        lpVerb="runas",
                        lpFile=pythonPath,
                        lpParameters='-c "%s"' % script.replace('"', '\\"')
                    )

                    if procInfo.get("hProcess"):
                        win32event.WaitForSingleObject(procInfo["hProcess"], -1)
                        exitcode = win32process.GetExitCodeProcess(procInfo["hProcess"])
                        return exitcode == 0
                    return False
                except ImportError:
                    logger.warning("pywin32 not available, cannot run as admin on Windows")
                    return False
            elif platform.system() == "Linux":
                # Try pkexec (PolicyKit) first, fallback to sudo
                try:
                    # pkexec provides graphical authentication
                    cmd = ["pkexec", pythonPath, "-c", script]
                    result = subprocess.run(cmd, capture_output=True)
                    return result.returncode == 0
                except FileNotFoundError:
                    # Fallback to sudo (requires terminal)
                    logger.debug("pkexec not found, trying sudo")
                    try:
                        cmd = ["sudo", pythonPath, "-c", script]
                        result = subprocess.run(cmd)
                        return result.returncode == 0
                    except Exception as e:
                        logger.error("sudo failed: %s" % e)
                        return False
            elif platform.system() == "Darwin":
                # macOS: use osascript to prompt for admin
                try:
                    applescript = 'do shell script "%s -c \\"%s\\"" with administrator privileges' % (
                        pythonPath, script.replace('"', '\\"').replace("\\", "\\\\")
                    )
                    result = subprocess.run(["osascript", "-e", applescript], capture_output=True)
                    return result.returncode == 0
                except Exception as e:
                    logger.error("osascript failed: %s" % e)
                    return False
            else:
                logger.warning("runAsAdmin not implemented for platform: %s" % platform.system())
                return False
        except Exception as e:
            logger.error("Failed to run as admin: %s" % e)
            return False

    # ========================================
    # Application Detection
    # ========================================

    @staticmethod
    @err_catcher(name=__name__)
    def getDefaultAppForExtension(ext):
        """Get the default application for a file extension.

        Args:
            ext (str): File extension (e.g., '.txt', '.jpg')

        Returns:
            str: Default application path/identifier or None
        """
        try:
            if platform.system() == "Windows":
                try:
                    import winreg

                    # Ensure extension starts with dot
                    if not ext.startswith('.'):
                        ext = '.' + ext

                    # Try user choice first
                    try:
                        with winreg.OpenKey(
                            winreg.HKEY_CURRENT_USER,
                            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\%s\UserChoice' % ext
                        ) as key:
                            progid = winreg.QueryValueEx(key, 'ProgId')[0]
                            return progid
                    except WindowsError:
                        pass

                    # Fallback to default association
                    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, ext) as key:
                        progid = winreg.QueryValueEx(key, '')[0]
                        return progid
                except Exception as e:
                    logger.debug("Failed to get Windows default app: %s" % e)
                    return None
            elif platform.system() == "Linux":
                try:
                    import mimetypes

                    # Ensure extension starts with dot
                    if not ext.startswith('.'):
                        ext = '.' + ext

                    # Get MIME type for extension
                    mimetype = mimetypes.types_map.get(ext)
                    if not mimetype:
                        return None

                    # Query default application using xdg-mime
                    result = subprocess.check_output(
                        ['xdg-mime', 'query', 'default', mimetype],
                        stderr=subprocess.DEVNULL
                    ).decode().strip()

                    return result if result else None
                except Exception as e:
                    logger.debug("Failed to get Linux default app: %s" % e)
                    return None
            elif platform.system() == "Darwin":
                # macOS: use Launch Services
                try:
                    # Ensure extension starts with dot
                    if not ext.startswith('.'):
                        ext = '.' + ext

                    # Create a dummy file with the extension
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp_path = tmp.name

                    try:
                        result = subprocess.check_output(
                            ['mdls', '-name', 'kMDItemContentType', tmp_path],
                            stderr=subprocess.DEVNULL
                        ).decode().strip()
                        return result
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                except Exception as e:
                    logger.debug("Failed to get macOS default app: %s" % e)
                    return None
            else:
                logger.warning("getDefaultAppForExtension not implemented for platform: %s" % platform.system())
                return None
        except Exception as e:
            logger.error("Failed to get default app for extension %s: %s" % (ext, e))
            return None

    @staticmethod
    @err_catcher(name=__name__)
    def findApplication(appName, searchPaths=None, envVar=None, registryPath=None):
        """Find an application across different platforms.

        Args:
            appName (str): Application name (e.g., 'maya', 'blender')
            searchPaths (list): List of paths to search (for Linux/macOS)
            envVar (str): Environment variable to check
            registryPath (str): Windows registry path to check

        Returns:
            str: Path to application or None if not found
        """
        logger.debug("Finding application: %s" % appName)

        # Check environment variable first
        if envVar and os.environ.get(envVar):
            env_path = os.environ.get(envVar)
            if os.path.exists(env_path):
                return env_path

        if platform.system() == "Windows":
            # Windows: Check registry
            if registryPath:
                try:
                    import winreg

                    for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                        try:
                            with winreg.OpenKey(
                                hive,
                                registryPath,
                                0,
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                            ) as key:
                                path = winreg.QueryValueEx(key, "InstallPath")[0]
                                if path and os.path.exists(path):
                                    return path
                        except WindowsError:
                            continue
                except Exception as e:
                    logger.debug("Registry search failed: %s" % e)

            # Fallback to common program files locations
            program_files = [
                os.environ.get("ProgramFiles", "C:\\Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
                "C:\\Program Files",
                "C:\\Program Files (x86)"
            ]

            for pf in program_files:
                if searchPaths:
                    for sp in searchPaths:
                        test_path = os.path.join(pf, sp)
                        if os.path.exists(test_path):
                            return test_path

        elif platform.system() == "Linux":
            # Linux: Check common paths and use which
            # Try using 'which' command first
            try:
                result = subprocess.check_output(
                    ['which', appName],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                if result and os.path.exists(result):
                    return os.path.dirname(result)
            except Exception:
                pass

            # Search in provided paths
            if searchPaths:
                for path in searchPaths:
                    # Handle glob patterns
                    if '*' in path:
                        matches = glob.glob(path)
                        if matches:
                            # Return newest version (sort and take last)
                            matches.sort()
                            if os.path.exists(matches[-1]):
                                return matches[-1]
                    else:
                        if os.path.exists(path):
                            return path

        elif platform.system() == "Darwin":
            # macOS: Check /Applications
            if searchPaths:
                for path in searchPaths:
                    if os.path.exists(path):
                        return path

            # Check /Applications
            app_path = os.path.join("/Applications", appName + ".app")
            if os.path.exists(app_path):
                return app_path

        logger.debug("Application %s not found" % appName)
        return None
