# Analisi Completa: Compatibilità Linux per Prism Pipeline

**Data Analisi:** 2025-11-15
**Versione Prism Analizzata:** 2.0.17
**Stato Attuale:** Windows Only
**Obiettivo:** Piena compatibilità con Linux

---

## Sommario Esecutivo

Prism Pipeline 2.0 è attualmente **supportato solo su Windows**, nonostante la versione 1.x avesse supporto multipiattaforma. L'analisi del codebase rivela che il porting a Linux richiede modifiche in **circa 50+ file** con **200+ punti di intervento**, principalmente concentrati su:

1. **Sostituzione del Windows Registry** con metodi di rilevamento DCC nativi Linux
2. **Conversione dei file .bat in script .sh** (3 file)
3. **Eliminazione dipendenze pywin32** e uso di alternative cross-platform
4. **Implementazione sistema .desktop files** per menu e autostart Linux
5. **Gestione percorsi XDG-compliant** invece di APPDATA/PROGRAMDATA
6. **Rilevamento processi cross-platform** (Prism.exe → python3)
7. **Creazione sistema di packaging** per distribuzioni Linux

**Tempo Stimato:** 4-6 settimane di sviluppo full-time
**Complessità:** Media-Alta
**Rischio:** Medio (molte modifiche ma pattern ripetitivi)

---

## Contesto e Ricerca

### Stato del Progetto

**Repository GitHub:** PrismPipeline/Prism
**Branch Principale:** development
**Ultimo Commit:** 87d6992 (v2.0.17)

#### Pull Request Rilevanti

**PR #33 - "Small Linux compatibility changes"** (APERTA dal 2021)
- Autore: Contributo community
- Modifiche:
  - Rende PythonLibs opzionale (Linux può usare librerie di sistema)
  - Aggiorna percorsi predefiniti Blender/Houdini
  - Sposta controlli winreg dentro blocchi platform-specific
- Stato: NON MERGIATA - necessita revisione e testing
- File modificati: 4 (PrismCore.py, Blender/Houdini Integration, PrismSettings.py)

#### Issues Rilevanti

- **Issue #13:** "Installer does not see Blender on Linux" - percorsi non rilevati
- **Issue #19:** "python is python2 in Manjaro" - problemi compatibilità Python 2/3
- **Issue #10:** "Setup QtGui error" - dipendenze PySide mancanti su Linux

#### Fork Community

**deltahoch3/Prism-Linux** (GitHub)
- Fork attivo per testing Prism2 su Linux
- Richiede dipendenze: `imageio`, `imageio_ffmpeg`, `numpy`, `oiio`, `psutil`, `pyside2/pyside6`, `ffmpeg`
- Launcher: `prism.sh` invece di `prism.bat`
- Usa librerie CrossPlatform da dependencies package

### Dichiarazioni Ufficiali

Dal sito ufficiale e comunicazioni sviluppatori (2024):
> "At this time Prism 2 is supported on Windows only. A Linux/Mac version will be considered for the future roadmap."

**Motivazione:** Focus su piccoli studi (principalmente Windows) per sviluppo rapido feature, con intenzione di supportare Linux/Mac successivamente.

---

## Architettura Attuale e Dipendenze Windows

### Dipendenze Python Critiche

#### Windows-Only (DA RIMUOVERE o RENDERE OPZIONALI)

```python
# pywin32 - Usato in 3 file
import win32com.client          # PrismCore.py - Creazione shortcuts
from win32comext.shell import shellcon, shell  # PrismInstaller.py - Percorsi system
import win32con, win32event, win32process  # PrismCore.py - Esecuzione privilegiata

# winreg - Usato in 10 file
import winreg  # (Python 3)
import _winreg  # (Python 2)
```

**File che usano winreg:**
1. PrismCore.py - Rilevamento app predefinite per estensioni
2. PrismInstaller.py - Registrazione/rimozione uninstaller
3. Tutti i plugin Integration.py (Maya, Blender, Houdini, 3dsMax, Cinema4D, Photoshop)
4. Standalone_Functions.py - Registrazione nel registro Windows

#### Cross-Platform (GIÀ COMPATIBILI)

```python
from qtpy.QtCore import *      # Astrazione Qt (PySide2/6, PyQt5)
import psutil                  # Rilevamento processi (cross-platform)
import imageio                 # I/O immagini
import numpy                   # Calcoli numerici
# import oiio                  # OpenImageIO (opzionale)
```

### Percorsi e Environment Variables Windows-Specific

#### Variabili d'Ambiente da Sostituire

```python
# Windows
os.environ["PROGRAMDATA"]      # C:\ProgramData
os.environ["APPDATA"]          # C:\Users\{user}\AppData\Roaming
os.environ["LOCALAPPDATA"]     # C:\Users\{user}\AppData\Local
os.environ["USERPROFILE"]      # C:\Users\{user}
os.environ["PUBLIC"]           # C:\Users\Public
os.environ["temp"]             # C:\Users\{user}\AppData\Local\Temp

# Linux Equivalenti (XDG Base Directory Specification)
os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))  # Config
os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))  # Data
os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))  # Cache
os.path.expanduser("~")        # Home directory
"/tmp"                         # Temporary files
```

#### Percorsi Hardcoded da Modificare

**Start Menu Windows:**
```
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\
C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\
```

**Linux Equivalente:**
```
/usr/share/applications/           # System-wide
~/.local/share/applications/       # Per-user
```

**Autostart Windows:**
```
{StartMenu}\Startup\Prism.lnk
```

**Linux Equivalente:**
```
/etc/xdg/autostart/PrismTray.desktop
~/.config/autostart/PrismTray.desktop
```

---

## Analisi Dettagliata File per File

### CATEGORIA 1: Core System (CRITICI)

#### 1.1 `/Prism/Scripts/PrismCore.py` (3700+ righe)

**Gravità:** CRITICA - File centrale dell'applicazione

**Problemi Identificati:** 20+ interventi necessari

##### A. Librerie Windows (Linee 94-101)
```python
# ATTUALE (Windows)
if platform.system() == "Windows" and pyLibs:
    sys.path.insert(0, os.path.join(pyLibPath, "win32"))
    sys.path.insert(0, os.path.join(pyLibPath, "win32", "lib"))
    pywinpath = os.path.join(pyLibPath, "pywin32_system32")
    os.environ["PATH"] = pywinpath + os.pathsep + os.environ["PATH"]
```

**Soluzione:** Già corretto con guard `if platform.system() == "Windows"`, ma verificare che PythonLibs sia opzionale su Linux (PR #33).

##### B. Percorso Documenti (Linee 344-355)
```python
# ATTUALE
def getWindowsDocumentsPath(self):
    # Solo Windows implementato
    if platform.system() == "Windows":
        from win32comext.shell import shell, shellcon
        path = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
```

**Soluzione:**
```python
def getDocumentsPath(self):
    if platform.system() == "Windows":
        from win32comext.shell import shell, shellcon
        return shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
    elif platform.system() == "Linux":
        # XDG User Dirs
        docs = subprocess.check_output(['xdg-user-dir', 'DOCUMENTS']).decode().strip()
        return docs if docs else os.path.expanduser("~/Documents")
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Documents")
```

##### C. Directory Dati Prism (Linee 373-384)
```python
# ATTUALE
def getPrismDataDir(self):
    if platform.system() == "Windows":
        path = os.path.join(os.environ["PROGRAMDATA"], "Prism2")
    elif platform.system() == "Linux":
        path = "/var/lib/Prism2"  # PROBLEMA: Richiede root!
```

**Soluzione:**
```python
def getPrismDataDir(self):
    if platform.system() == "Windows":
        return os.path.join(os.environ["PROGRAMDATA"], "Prism2")
    elif platform.system() == "Linux":
        # XDG compliant - no root needed
        return os.path.join(
            os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
            "Prism2"
        )
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Prism2")
```

##### D. Rilevamento App Predefinita (Linee 2614-2646)
```python
# ATTUALE
def getDefaultWindowsAppByExtension(self, ext):
    import winreg as _winreg
    with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{}\UserChoice'.format(ext)) as key:
        progid = _winreg.QueryValueEx(key, 'ProgId')[0]
```

**Soluzione:**
```python
def getDefaultAppByExtension(self, ext):
    if platform.system() == "Windows":
        import winreg as _winreg
        # ... codice esistente
    elif platform.system() == "Linux":
        try:
            # xdg-mime query default <mimetype>
            import mimetypes
            mimetype = mimetypes.types_map.get(ext, "application/octet-stream")
            cmd = ["xdg-mime", "query", "default", mimetype]
            result = subprocess.check_output(cmd).decode().strip()
            return result
        except:
            return None
```

##### E. Creazione Shortcut - VBScript (Linee 2770-2813)
```python
# ATTUALE
def createShortcut(self, link, target, args="", ignoreError=False):
    if platform.system() == "Windows":
        # Crea file .vbs temporaneo
        c = 'Set oWS = WScript.CreateObject("WScript.Shell")\n' + ...
        subprocess.Popen("cscript /nologo %s" % tmp.name, shell=True)
    else:
        logger.warning("not implemented")
```

**Soluzione:**
```python
def createShortcut(self, link, target, args="", icon="", ignoreError=False):
    if platform.system() == "Windows":
        # ... codice VBScript esistente
    elif platform.system() == "Linux":
        # Crea .desktop file
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={os.path.basename(link).replace('.desktop', '')}
Exec={target} {args}
Icon={icon if icon else target}
Terminal=false
"""
        desktop_path = link if link.endswith('.desktop') else f"{link}.desktop"
        os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
        os.chmod(desktop_path, 0o755)
    elif platform.system() == "Darwin":
        # Implementare alias macOS
        pass
```

##### F. Creazione Symlink (Linee 2816-2827)
```python
# ATTUALE
def createSymlink(self, link, target):
    if platform.system() == "Windows":
        subprocess.call(["mklink", "/H", link, target], shell=True)
    else:
        logger.warning("not implemented")
```

**Soluzione:**
```python
def createSymlink(self, link, target):
    if platform.system() == "Windows":
        # Windows richiede mklink per hardlinks
        link = link.replace("/", "\\")
        target = target.replace("/", "\\")
        subprocess.call(["mklink", "/H", link, target], shell=True)
    else:
        # Linux/macOS - usa os.link per hardlink, os.symlink per symlink
        try:
            os.link(target, link)  # Hard link
        except OSError:
            os.symlink(target, link)  # Fallback a symbolic link
```

##### G. Apertura Cartelle (Linee 2323-2349)
```python
# ATTUALE
def openFolder(self, path):
    if platform.system() == "Windows":
        cmd = [os.getenv("PRISM_FILE_EXPLORER", "explorer")]
        if os.path.isfile(path):
            cmd = [cmd[0], "/select,", path]  # /select non esiste su Linux!
```

**Soluzione:** Già implementato per Linux, ma rimuovere /select su altre piattaforme.

##### H. Esecuzione Privilegiata (Linee 4059-4091)
```python
# ATTUALE
def winRunAsAdmin(self, script):
    from win32comext.shell import shellcon
    import win32comext.shell.shell as shell
    shell.ShellExecuteEx(lpVerb="runas", ...)
```

**Soluzione:**
```python
def runAsAdmin(self, script):
    if platform.system() == "Windows":
        from win32comext.shell import shellcon
        import win32comext.shell.shell as shell
        # ... codice esistente
    elif platform.system() == "Linux":
        # Usa pkexec (PolicyKit) o sudo
        pythonPath = self.getPythonPath()
        try:
            # Prova pkexec (interfaccia grafica)
            cmd = ["pkexec", pythonPath, "-c", script]
            subprocess.run(cmd, check=True)
            return True
        except:
            # Fallback a sudo (richiede terminale)
            cmd = ["sudo", pythonPath, "-c", script]
            result = subprocess.run(cmd)
            return result.returncode == 0
```

##### I. Percorso Python (Linee 3283-3323)
```python
# ATTUALE
def getPythonPath(self, executable=None, root=None):
    if platform.system() == "Windows":
        pythonPath = os.path.join(root, "Python311", "pythonw.exe")  # Hardcoded!
```

**Soluzione:**
```python
def getPythonPath(self, executable=None, root=None):
    if platform.system() == "Windows":
        root = root or self.prismLibs
        pythonVersion = getattr(self, 'pythonVersion', 'Python311')
        if executable:
            return os.path.join(root, pythonVersion, f"{executable}.exe")
        return os.path.join(root, pythonVersion, "pythonw.exe")
    elif platform.system() == "Linux":
        # Prova prima bundled Python, poi system
        root = root or self.prismLibs
        pythonVersion = getattr(self, 'pythonVersion', 'Python311')
        bundled = os.path.join(root, pythonVersion, "bin", "python3")
        if os.path.exists(bundled):
            return bundled
        # Fallback a system Python
        return sys.executable or "python3"
    elif platform.system() == "Darwin":
        return sys.executable or "python3"
```

**RIEPILOGO PrismCore.py:**
- **20+ modifiche necessarie**
- **Priorità:** MASSIMA
- **Complessità:** Alta (file centrale)
- **Testing richiesto:** Estensivo

---

#### 1.2 `/Prism/Scripts/PrismInstaller.py` (1400+ righe)

**Gravità:** CRITICA - Gestisce installazione e rimozione

##### A. Import Platform-Specific (Linee 50-59)
```python
# ATTUALE
if platform.system() == "Windows":
    from win32comext.shell import shellcon
    import win32comext.shell.shell as shell
    import win32con, win32event, win32process
    import winreg as _winreg
else:
    import pwd  # Corretto!
```

**Stato:** Già corretto con guard, ma verificare uso di pwd.

##### B. Percorso Documenti (Linee 375-378)
```python
# ATTUALE
if platform.system() == "Windows":
    self.documents = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
```

**Soluzione:** Usare metodo getDocumentsPath() di PrismCore.

##### C. User Folders (Linee 430-438)
```python
# ATTUALE
if platform.system() == "Windows":
    userFolders = {
        "LocalAppdata": os.environ["localappdata"],
        "AppData": os.environ["appdata"],
        "UserProfile": os.environ["Userprofile"],
        "Documents": self.documents,
    }
else:
    userFolders = {}  # VUOTO!
```

**Soluzione:**
```python
if platform.system() == "Windows":
    userFolders = {
        "LocalAppdata": os.environ["localappdata"],
        "AppData": os.environ["appdata"],
        "UserProfile": os.environ["Userprofile"],
        "Documents": self.documents,
    }
elif platform.system() == "Linux":
    userFolders = {
        "ConfigHome": os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "DataHome": os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
        "CacheHome": os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")),
        "Home": os.path.expanduser("~"),
        "Documents": subprocess.check_output(['xdg-user-dir', 'DOCUMENTS']).decode().strip(),
    }
```

##### D. Finalize/Cleanup (Linee 717-726)
```python
# ATTUALE
def finalize(self, postDeletePaths):
    if postDeletePaths:
        cmd = "timeout /t 5 /nobreak > nul"  # Windows CMD!
        for path in postDeletePaths:
            cmd += " & rmdir /S /Q \"%s\"" % path  # Windows CMD!
        subprocess.Popen(cmd, shell=True)
```

**Soluzione:**
```python
def finalize(self, postDeletePaths):
    if not postDeletePaths:
        return

    if platform.system() == "Windows":
        cmd = "timeout /t 5 /nobreak > nul"
        for path in postDeletePaths:
            cmd += " & rmdir /S /Q \"%s\"" % path.replace("\\", "\\\\")
        subprocess.Popen(cmd, shell=True)
    else:
        # Linux/macOS
        import shutil
        import time
        def delayed_cleanup():
            time.sleep(5)
            for path in postDeletePaths:
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    logger.warning(f"Failed to remove {path}: {e}")

        import threading
        thread = threading.Thread(target=delayed_cleanup, daemon=True)
        thread.start()
```

##### E. Chiusura Processi (Linee 807-827)
```python
# ATTUALE
def closePrismProcesses(self):
    import psutil
    PROCNAMES = ["Prism.exe"]  # Solo Windows!
```

**Soluzione:**
```python
def closePrismProcesses(self):
    try:
        import psutil
    except:
        return

    if platform.system() == "Windows":
        PROCNAMES = ["Prism.exe"]
    else:
        # Linux: cerca processi python che eseguono script Prism
        PROCNAMES = ["python", "python3", "python2"]

    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if platform.system() == "Windows":
                if proc.info['name'] in PROCNAMES:
                    proc.terminate()
            else:
                # Linux: controlla cmdline per script Prism
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('Prism' in arg for arg in cmdline):
                    proc.terminate()
        except:
            pass
```

##### F. Rimozione Registro (Linee 891-901)
```python
# ATTUALE
def removeUninstallerFromWindowsRegistry(self):
    _winreg.DeleteKey(
        _winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Prism Pipeline 2.0"
    )
```

**Stato:** Solo Windows, nessun equivalente Linux necessario.

##### G. Rimozione File Linux (Linee 904-937)
```python
# GIÀ IMPLEMENTATO
def removeLinuxSpecificData(self):
    trayStartup = "/etc/xdg/autostart/PrismTray.desktop"
    trayStartMenu = "/usr/share/applications/PrismTray.desktop"
    # ...
```

**Stato:** Implementazione base esistente, ma percorsi hardcoded. Migliorare con XDG.

**RIEPILOGO PrismInstaller.py:**
- **8+ modifiche necessarie**
- **Priorità:** ALTA
- **Complessità:** Media
- Buona base Linux già presente

---

#### 1.3 `/Prism/Scripts/PrismTray.py` (System Tray)

**Gravità:** ALTA - Tray icon e gestione processi

##### A. Rilevamento Istanze (Linee 309-330)
```python
# ATTUALE
def isAlreadyRunning():
    if platform.system() == "Windows":
        for proc in psutil.process_iter():
            if os.path.basename(proc.exe()) == "Prism.exe":  # Windows-only!
                return True
```

**Soluzione:**
```python
def isAlreadyRunning():
    ignoredPids = [os.getpid()]
    for arg in sys.argv:
        if arg.startswith("ignore_pid="):
            ignoredPids.append(int(arg.split("=")[-1]))

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username']):
        try:
            if proc.info['pid'] in ignoredPids:
                continue

            if platform.system() == "Windows":
                if os.path.basename(proc.info.get('exe', '')) == "Prism.exe":
                    if proc.info.get('username') == psutil.Process(os.getpid()).username():
                        return True
            else:
                # Linux: controlla se esegue PrismTray.py
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'PrismTray.py' in ' '.join(cmdline):
                    if proc.info.get('username') == psutil.Process(os.getpid()).username():
                        return True
        except:
            pass

    return False
```

##### B. Restart Tray (Linee 224-231)
```python
# ATTUALE
def restartTray(self):
    cmd = """start "" "%s" "%s" showSplash ignore_pid=%s""" % (
        pythonPath, filepath, os.getpid()
    )  # 'start' è Windows CMD!
    subprocess.Popen(cmd, shell=True)
```

**Soluzione:**
```python
def restartTray(self):
    self.listenerThread.shutDown()
    pythonPath = self.core.getPythonPath()
    filepath = os.path.join(self.core.prismRoot, "Scripts", "PrismTray.py")

    if platform.system() == "Windows":
        cmd = f"""start "" "{pythonPath}" "{filepath}" showSplash ignore_pid={os.getpid()}"""
        subprocess.Popen(cmd, cwd=self.core.prismRoot, shell=True, env=self.core.startEnv)
    else:
        # Linux/macOS: usa nohup o subprocess diretto
        cmd = [pythonPath, filepath, "showSplash", f"ignore_pid={os.getpid()}"]
        subprocess.Popen(
            cmd,
            cwd=self.core.prismRoot,
            env=self.core.startEnv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach dal parent
        )
```

**RIEPILOGO PrismTray.py:**
- **3-4 modifiche necessarie**
- **Priorità:** MEDIA
- **Complessità:** Bassa

---

### CATEGORIA 2: Plugin System (CRITICI)

#### 2.1 Plugin DCC Integrations - Rilevamento Applicazioni

**PROBLEMA COMUNE:** Tutti i plugin DCC usano Windows Registry per rilevare le applicazioni.

##### A. Maya (`Prism_Maya_Integration.py`)

**Attuale (Linee 89-119):**
```python
def getMayaPath(self):
    try:
        key = _winreg.OpenKey(
            _winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Autodesk\\Maya\\%s\\Setup\\InstallPath" % vers,
            0,
            _winreg.KEY_READ | _winreg.KEY_WOW64_64KEY
        )
        return (_winreg.QueryValueEx(key, "MAYA_INSTALL_LOCATION"))[0]
    except:
        return ""
```

**Soluzione Linux:**
```python
def getMayaPath(self):
    if platform.system() == "Windows":
        # ... codice registry esistente
    elif platform.system() == "Linux":
        # Percorsi standard Maya Linux
        mayaPaths = [
            "/usr/autodesk/maya2024",
            "/usr/autodesk/maya2023",
            "/usr/autodesk/maya2022",
            "/opt/autodesk/maya",
        ]
        # Cerca anche tramite versioni installate
        import glob
        mayaPaths.extend(glob.glob("/usr/autodesk/maya*"))
        mayaPaths.extend(glob.glob("/opt/autodesk/maya*"))

        for path in mayaPaths:
            if os.path.exists(path):
                return path

        # Fallback: usa MAYA_LOCATION env var
        return os.environ.get("MAYA_LOCATION", "")
    elif platform.system() == "Darwin":
        # macOS paths
        return "/Applications/Autodesk/maya2024"
```

##### B. Blender (`Prism_Blender_Integration.py`)

**Attuale (Linee 82-89):**
```python
def getBlenderPath(self):
    key = _winreg.OpenKey(
        _winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Classes\\blenderfile\\shell\\open\\command"
    )
    blenderPath = (_winreg.QueryValueEx(key, ""))[0].split(' "%1"')[0]
```

**Soluzione Linux (PARZIALMENTE in PR #33):**
```python
def getBlenderPath(self):
    if platform.system() == "Windows":
        # ... codice registry esistente
    elif platform.system() == "Linux":
        # Prova prima system binary
        import shutil
        blender_bin = shutil.which("blender")
        if blender_bin:
            return os.path.dirname(blender_bin)

        # Percorsi standard
        blenderPaths = [
            "/usr/share/blender",
            "/usr/bin",
            "/opt/blender",
        ]
        import glob
        blenderPaths.extend(glob.glob("/opt/blender*"))
        blenderPaths.extend(glob.glob("/snap/blender/*/"))

        for path in blenderPaths:
            if os.path.exists(path):
                return path

        return ""
```

##### C. Houdini (`Prism_Houdini_Integration.py`)

**Attuale (Linee 76-91):**
```python
def getHoudiniPath(self):
    key = _winreg.OpenKey(
        _winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Side Effects Software"
    )
    validVersion = (_winreg.QueryValueEx(key, "ActiveVersion"))[0]
```

**Soluzione Linux (PARZIALMENTE in PR #33):**
```python
def getHoudiniPath(self):
    if platform.system() == "Windows":
        # ... codice registry esistente
    elif platform.system() == "Linux":
        # Houdini su Linux usa $HFS
        hfs = os.environ.get("HFS")
        if hfs and os.path.exists(hfs):
            return hfs

        # Percorsi standard
        import glob
        houdiniPaths = glob.glob("/opt/hfs*")
        if houdiniPaths:
            # Ritorna la versione più recente
            return sorted(houdiniPaths)[-1]

        return ""
```

##### D. Nuke (`Prism_Nuke_Integration.py`)

**Soluzione:**
```python
def getNukePath(self):
    if platform.system() == "Windows":
        # ... usa registry
    elif platform.system() == "Linux":
        nukePaths = [
            "/usr/local/Nuke14.0v5",
            "/usr/local/Nuke13.2v7",
            "/opt/Nuke",
        ]
        import glob
        nukePaths.extend(glob.glob("/usr/local/Nuke*"))
        nukePaths.extend(glob.glob("/opt/Nuke*"))

        for path in nukePaths:
            if os.path.exists(path):
                return path

        return ""
```

**RIEPILOGO Plugin Integrations:**
- **6+ plugin da modificare** (Maya, Blender, Houdini, Nuke, 3dsMax, Cinema4D, Photoshop)
- **Pattern ripetitivo:** Sostituire registry con filesystem search
- **Priorità:** ALTA
- **Complessità:** Media (pattern ripetitivo)

---

#### 2.2 Standalone Plugin (`Prism_Standalone_Functions.py`)

**Gravità:** CRITICA - Gestisce menu Start e shortcuts

##### A. Start Menu Windows (Linee 120-194)
```python
def createWinStartMenu(self, origin, allUsers=False):
    if platform.system() == "Windows":
        startMenuPath = os.path.join(
            os.environ["PROGRAMDATA"], "Microsoft", "Windows", "Start Menu", "Programs"
        )
        # Crea .lnk shortcuts
```

**Soluzione:** Creare metodo `createLinuxStartMenu`:
```python
def createLinuxStartMenu(self, origin, allUsers=False):
    """Crea menu entries e desktop shortcuts per Linux"""

    # Percorsi XDG
    if allUsers:
        applicationsDir = "/usr/share/applications"
        autostartDir = "/etc/xdg/autostart"
    else:
        applicationsDir = os.path.expanduser("~/.local/share/applications")
        autostartDir = os.path.expanduser("~/.config/autostart")

    os.makedirs(applicationsDir, exist_ok=True)
    os.makedirs(autostartDir, exist_ok=True)

    pythonPath = self.core.getPythonPath()
    prismRoot = self.core.prismRoot
    iconPath = os.path.join(prismRoot, "Scripts", "UserInterfacesPrism", "p_tray.png")

    # Prism Tray
    trayDesktop = os.path.join(applicationsDir, "PrismTray.desktop")
    trayContent = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Prism Tray
Comment=Prism Pipeline Tray Application
Exec={pythonPath} "{prismRoot}/Scripts/PrismTray.py"
Icon={iconPath}
Terminal=false
Categories=Graphics;
"""
    with open(trayDesktop, 'w') as f:
        f.write(trayContent)
    os.chmod(trayDesktop, 0o755)

    # Project Browser
    pbDesktop = os.path.join(applicationsDir, "PrismProjectBrowser.desktop")
    pbContent = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Prism Project Browser
Comment=Browse Prism Projects
Exec={pythonPath} "{prismRoot}/Scripts/PrismTray.py" projectBrowser
Icon={iconPath}
Terminal=false
Categories=Graphics;
"""
    with open(pbDesktop, 'w') as f:
        f.write(pbContent)
    os.chmod(pbDesktop, 0o755)

    # Settings
    settingsDesktop = os.path.join(applicationsDir, "PrismSettings.desktop")
    settingsContent = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Prism Settings
Comment=Prism Pipeline Settings
Exec={pythonPath} "{prismRoot}/Scripts/PrismSettings.py"
Icon={iconPath}
Terminal=false
Categories=Settings;Graphics;
"""
    with open(settingsDesktop, 'w') as f:
        f.write(settingsContent)
    os.chmod(settingsDesktop, 0o755)

    # Desktop shortcut (opzionale, chiede permesso)
    desktopDir = subprocess.check_output(['xdg-user-dir', 'DESKTOP']).decode().strip()
    if desktopDir and os.path.exists(desktopDir):
        desktopShortcut = os.path.join(desktopDir, "PrismProjectBrowser.desktop")
        import shutil
        shutil.copy(pbDesktop, desktopShortcut)
        os.chmod(desktopShortcut, 0o755)
```

##### B. Registry Uninstaller (Linee 241-277)
```python
def addUninstallerToWindowsRegistry(self):
    if platform.system() != "Windows":
        return
    # ... aggiungi chiave registro
```

**Stato:** Già gated per Windows. Non serve equivalente Linux (gestori pacchetti).

**RIEPILOGO Standalone_Functions.py:**
- **2-3 metodi da creare** per Linux
- **Priorità:** ALTA
- **Complessità:** Media

---

### CATEGORIA 3: Build System e Launcher Scripts

#### 3.1 File Batch Windows → Shell Scripts Linux

##### A. `prism.bat` → `prism.sh`

**Attuale:**
```batch
start "" "%~dp0/Python311/pythonw.exe" "%~dp0/Scripts/PrismCore.py"
::PAUSE
```

**Soluzione Linux:**
```bash
#!/usr/bin/env bash

# prism.sh - Prism Pipeline Linux Launcher

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python path
if [ -f "$SCRIPT_DIR/Python311/bin/python3" ]; then
    PYTHON_PATH="$SCRIPT_DIR/Python311/bin/python3"
else
    # Fallback to system Python
    PYTHON_PATH="python3"
fi

# Launch Prism Core
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismCore.py" "$@" &

# Exit immediately (don't wait for background process)
exit 0
```

**Rendere eseguibile:**
```bash
chmod +x prism.sh
```

##### B. `setup.bat` → `setup.sh`

**Attuale:**
```batch
"%~dp0/Python311/python.exe" "%~dp0/Scripts/PrismInstaller.py"
::PAUSE
```

**Soluzione Linux:**
```bash
#!/usr/bin/env bash

# setup.sh - Prism Pipeline Linux Setup

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python path
if [ -f "$SCRIPT_DIR/Python311/bin/python3" ]; then
    PYTHON_PATH="$SCRIPT_DIR/Python311/bin/python3"
else
    PYTHON_PATH="python3"
fi

# Check for root if installing system-wide
if [ "$1" == "--system" ]; then
    if [ "$EUID" -ne 0 ]; then
        echo "System-wide installation requires root privileges."
        echo "Please run: sudo $0 --system"
        exit 1
    fi
fi

# Launch Installer
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismInstaller.py" "$@"

# Pause equivalent (optional)
if [ "$1" != "--no-pause" ]; then
    read -p "Press Enter to continue..."
fi
```

##### C. `uninstall.bat` → `uninstall.sh`

**Attuale:**
```batch
"%~dp0/Python311/python.exe" "%~dp0/Scripts/PrismInstaller.py" uninstall
::PAUSE
```

**Soluzione Linux:**
```bash
#!/usr/bin/env bash

# uninstall.sh - Prism Pipeline Linux Uninstaller

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Python path
if [ -f "$SCRIPT_DIR/Python311/bin/python3" ]; then
    PYTHON_PATH="$SCRIPT_DIR/Python311/bin/python3"
else
    PYTHON_PATH="python3"
fi

# Launch Uninstaller
"$PYTHON_PATH" "$SCRIPT_DIR/Scripts/PrismInstaller.py" uninstall "$@"

# Pause equivalent
read -p "Press Enter to continue..."
```

**RIEPILOGO Script Files:**
- **3 file .sh da creare**
- **Priorità:** ALTA
- **Complessità:** BASSA
- **Test:** Verificare su diverse shell (bash, zsh, sh)

---

### CATEGORIA 4: Dipendenze e Packaging

#### 4.1 Dipendenze Python Richieste

**Da includere in `requirements.txt` o nel bundle:**

```
# Core Qt
PySide2>=5.15.0; python_version<'3.11'
PySide6>=6.2.0; python_version>='3.11'
qtpy>=2.0.0

# Media Processing
imageio>=2.9.0
imageio-ffmpeg>=0.4.0
numpy>=1.19.0
# OpenImageIO (opzionale, build complessa)

# System Utilities
psutil>=5.8.0

# Linux-Specific (opzionali)
pyxdg>=0.27  # XDG Base Directory support
```

**Dipendenze Sistema Linux:**
```bash
# Debian/Ubuntu
sudo apt install \
    python3 \
    python3-pip \
    python3-pyside2 \  # or python3-pyside6
    ffmpeg \
    libgl1-mesa-glx \
    libxcb-xinerama0

# Fedora/RHEL
sudo dnf install \
    python3 \
    python3-pip \
    python3-pyside2 \
    ffmpeg \
    mesa-libGL \
    libxcb

# Arch Linux
sudo pacman -S \
    python \
    python-pip \
    python-pyside2 \
    ffmpeg \
    mesa
```

#### 4.2 Struttura Directory Linux

**Attuale (Windows):**
```
Prism/
├── Python311/
│   ├── python.exe
│   ├── pythonw.exe
│   └── ...
├── PythonLibs/
│   ├── CrossPlatform/
│   ├── Python311/
│   │   ├── win32/
│   │   └── ...
│   └── ...
├── Scripts/
├── Plugins/
├── prism.bat
└── setup.bat
```

**Proposta Linux:**
```
Prism/
├── Python311/           # Opzionale su Linux (può usare system Python)
│   └── bin/
│       └── python3
├── PythonLibs/
│   ├── CrossPlatform/   # RICHIESTO
│   └── Python311/       # Solo se non usa system libs
├── Scripts/
├── Plugins/
├── prism.sh             # NUOVO
├── setup.sh             # NUOVO
└── uninstall.sh         # NUOVO
```

**Opzione alternativa - System Python:**
```
Prism/
├── PythonLibs/
│   └── CrossPlatform/   # Solo questo necessario
├── Scripts/
├── Plugins/
├── prism.sh
├── setup.sh
└── uninstall.sh
```

#### 4.3 Packaging per Distribuzioni Linux

##### A. AppImage (Raccomandato)

**Pro:**
- Singolo file eseguibile
- Funziona su tutte le distribuzioni
- Bundle completo con dipendenze
- Nessuna installazione root richiesta

**Struttura:**
```
Prism.AppImage
└── AppDir/
    ├── AppRun              # Script launcher
    ├── prism.desktop       # Desktop entry
    ├── prism.png           # Icon
    ├── usr/
    │   ├── bin/
    │   │   └── prism
    │   ├── lib/
    │   │   └── python3.11/
    │   └── share/
    │       └── Prism/
    │           ├── Scripts/
    │           ├── Plugins/
    │           └── PythonLibs/
    └── ...
```

**Build AppImage:**
```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p Prism.AppDir/usr/share/Prism
cp -r Prism/* Prism.AppDir/usr/share/Prism/

# Create AppRun launcher
cat > Prism.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/share/Prism/PythonLibs/CrossPlatform:${PYTHONPATH}"
exec python3 "${HERE}/usr/share/Prism/Scripts/PrismCore.py" "$@"
EOF
chmod +x Prism.AppDir/AppRun

# Create desktop file
cat > Prism.AppDir/prism.desktop << 'EOF'
[Desktop Entry]
Name=Prism Pipeline
Exec=prism
Icon=prism
Type=Application
Categories=Graphics;
EOF

# Copy icon
cp Prism/Scripts/UserInterfacesPrism/p_tray.png Prism.AppDir/prism.png

# Build AppImage
./appimagetool-x86_64.AppImage Prism.AppDir Prism-2.0.17-x86_64.AppImage
```

##### B. Flatpak

**Pro:**
- Sandbox sicuro
- Integrazione con software center
- Aggiornamenti automatici

**Manifest (`com.prism_pipeline.Prism.yaml`):**
```yaml
app-id: com.prism_pipeline.Prism
runtime: org.freedesktop.Platform
runtime-version: '23.08'
sdk: org.freedesktop.Sdk
command: prism
finish-args:
  - --share=ipc
  - --socket=x11
  - --socket=wayland
  - --device=dri
  - --filesystem=home
  - --filesystem=xdg-run/dconf
  - --filesystem=~/.config/dconf:ro
  - --talk-name=ca.desrt.dconf
  - --env=DCONF_USER_CONFIG_DIR=.config/dconf

modules:
  - name: python-dependencies
    buildsystem: simple
    build-commands:
      - pip3 install --prefix=/app --no-deps imageio imageio-ffmpeg numpy psutil PySide6 qtpy

  - name: prism
    buildsystem: simple
    build-commands:
      - cp -r Prism /app/
      - install -Dm755 prism.sh /app/bin/prism
      - install -Dm644 com.prism_pipeline.Prism.desktop /app/share/applications/com.prism_pipeline.Prism.desktop
      - install -Dm644 prism.png /app/share/icons/hicolor/256x256/apps/com.prism_pipeline.Prism.png
    sources:
      - type: archive
        url: https://github.com/PrismPipeline/Prism/archive/refs/tags/v2.0.17.tar.gz
```

##### C. Snap

**Pro:**
- Supporto ufficiale Ubuntu
- Auto-update
- Confinamento

**`snapcraft.yaml`:**
```yaml
name: prism-pipeline
version: '2.0.17'
summary: Animation and VFX Pipeline Management
description: |
  Prism automates and simplifies the workflow of animation and VFX projects.

base: core22
confinement: strict
grade: stable

apps:
  prism-pipeline:
    command: bin/prism.sh
    plugs:
      - home
      - desktop
      - desktop-legacy
      - wayland
      - x11
      - opengl
      - network

parts:
  prism:
    plugin: dump
    source: .
    stage-packages:
      - python3
      - python3-pyside2
      - ffmpeg
      - libgl1-mesa-glx
    organize:
      Prism: opt/prism/
      prism.sh: bin/prism.sh
```

##### D. Debian/RPM Package (Avanzato)

**Debian (.deb):**
```
prism-pipeline_2.0.17_amd64.deb
├── DEBIAN/
│   ├── control
│   ├── postinst
│   └── prerm
├── opt/
│   └── prism/
│       ├── Scripts/
│       ├── Plugins/
│       └── ...
├── usr/
│   ├── bin/
│   │   └── prism -> /opt/prism/prism.sh
│   └── share/
│       ├── applications/
│       │   └── prism.desktop
│       └── icons/
│           └── hicolor/256x256/apps/prism.png
```

**control file:**
```
Package: prism-pipeline
Version: 2.0.17
Section: graphics
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.9), python3-pyside2, ffmpeg, libgl1-mesa-glx
Maintainer: Prism Software GmbH <contact@prism-pipeline.com>
Description: Animation and VFX Pipeline Management
 Prism automates and simplifies the workflow of animation
 and VFX projects.
```

---

## Piano di Implementazione Consigliato

### FASE 1: Preparazione (Settimana 1)

**Obiettivo:** Setup ambiente e merge PR esistente

#### Task 1.1: Setup Ambiente Sviluppo Linux
- [ ] Installare VM/container Linux (Ubuntu 22.04 LTS raccomandato)
- [ ] Installare DCC test: Blender, Houdini (Apprentice), Nuke (trial)
- [ ] Installare dipendenze Python: `pip install PySide6 imageio imageio-ffmpeg numpy psutil pyxdg`
- [ ] Clone repository e checkout branch `development`

#### Task 1.2: Review e Merge PR #33
- [ ] Testare modifiche di PR #33 su Linux
- [ ] Verificare compatibilità con Windows (no regressioni)
- [ ] Merge PR #33 o incorporare modifiche nel branch principale
- [ ] Documentare modifiche nel changelog

#### Task 1.3: Creazione Branch Linux
- [ ] Creare branch `feature/linux-support` da `development`
- [ ] Setup CI/CD per test Linux (GitHub Actions)

### FASE 2: Core System (Settimana 2-3)

**Obiettivo:** Rendere PrismCore.py e file centrali cross-platform

#### Task 2.1: Creare Modulo PlatformUtils
```python
# Prism/Scripts/PrismUtils/PlatformUtils.py
class PlatformUtils:
    @staticmethod
    def getConfigDir():
        """Ritorna directory config XDG-compliant"""

    @staticmethod
    def getDataDir():
        """Ritorna directory data XDG-compliant"""

    @staticmethod
    def createShortcut(link, target, args="", icon=""):
        """Crea shortcut cross-platform (.lnk su Windows, .desktop su Linux)"""

    @staticmethod
    def openFolder(path):
        """Apri file manager cross-platform"""

    @staticmethod
    def runAsAdmin(script):
        """Esegui script con privilegi elevati"""

    # ... altri metodi utility
```

#### Task 2.2: Modificare PrismCore.py
- [ ] Sostituire tutte le chiamate dirette a PROGRAMDATA/APPDATA con PlatformUtils
- [ ] Implementare `createShortcut()` per .desktop files
- [ ] Implementare `getDefaultAppByExtension()` con xdg-mime
- [ ] Rendere pywin32 opzionale (solo import su Windows)
- [ ] Fix `getPythonPath()` per Linux
- [ ] Test completo su Windows (no regressioni)
- [ ] Test su Linux

#### Task 2.3: Modificare PrismInstaller.py
- [ ] Popolare `userFolders` dictionary per Linux
- [ ] Implementare `finalize()` con cleanup cross-platform
- [ ] Fix `closePrismProcesses()` per Linux
- [ ] Test installazione/disinstallazione Linux

#### Task 2.4: Modificare PrismTray.py
- [ ] Fix `isAlreadyRunning()` per Linux (cmdline check)
- [ ] Fix `restartTray()` con subprocess detached
- [ ] Test system tray su Linux (necessita status icon support)

### FASE 3: Plugin System (Settimana 3-4)

**Obiettivo:** Rendere tutti i plugin DCC compatibili Linux

#### Task 3.1: Creare Metodo Generico DCC Detection
```python
# In PlatformUtils o base Integration class
class DCCDetection:
    @staticmethod
    def findApplication(appName, registryPath=None, linuxPaths=None, envVar=None):
        """
        Trova applicazione DCC cross-platform

        Args:
            appName: Nome app (es. "maya", "blender")
            registryPath: Path registro Windows
            linuxPaths: Lista percorsi Linux da controllare
            envVar: Variabile ambiente da controllare
        """
        if platform.system() == "Windows":
            return DCCDetection._findWindows(registryPath)
        elif platform.system() == "Linux":
            return DCCDetection._findLinux(appName, linuxPaths, envVar)
        elif platform.system() == "Darwin":
            return DCCDetection._findMacOS(appName)
```

#### Task 3.2: Aggiornare Plugin Integrations
- [ ] **Maya:** `/usr/autodesk/maya*`, `MAYA_LOCATION`
- [ ] **Blender:** `which blender`, `/opt/blender*`, snap paths
- [ ] **Houdini:** `$HFS`, `/opt/hfs*`
- [ ] **Nuke:** `/usr/local/Nuke*`, `/opt/Nuke*`
- [ ] **3dsMax:** Skip (non disponibile su Linux)
- [ ] **Cinema4D:** Verificare disponibilità Linux
- [ ] **Photoshop:** Skip (non disponibile su Linux)
- [ ] Test detection su sistemi con DCC installati

#### Task 3.3: Aggiornare Standalone Plugin
- [ ] Implementare `createLinuxStartMenu()`
- [ ] Test creazione .desktop files
- [ ] Test integrazione con menu applicazioni
- [ ] Test desktop shortcuts

### FASE 4: Build System (Settimana 4-5)

**Obiettivo:** Creare launcher scripts e sistema di packaging

#### Task 4.1: Creare Shell Scripts
- [ ] Creare `prism.sh` (launcher)
- [ ] Creare `setup.sh` (installer)
- [ ] Creare `uninstall.sh` (uninstaller)
- [ ] Rendere eseguibili: `chmod +x *.sh`
- [ ] Test su diverse shell (bash, zsh, sh)

#### Task 4.2: Gestione Dipendenze
- [ ] Creare `requirements.txt`
- [ ] Creare script `install_dependencies.sh`
- [ ] Documentare dipendenze sistema per diverse distro
- [ ] Test con system Python vs bundled Python

#### Task 4.3: Packaging - AppImage (Raccomandato per rilascio iniziale)
- [ ] Creare struttura AppDir
- [ ] Creare AppRun launcher
- [ ] Bundle dipendenze Python
- [ ] Build AppImage
- [ ] Test su multiple distro (Ubuntu, Fedora, Arch)

### FASE 5: Testing e Debugging (Settimana 5-6)

**Obiettivo:** Test completo su diverse configurazioni

#### Task 5.1: Test Funzionali
- [ ] Installazione/disinstallazione
- [ ] Creazione progetto
- [ ] Import/Export assets
- [ ] Rendering/Playblast
- [ ] Publishing
- [ ] Version management
- [ ] System tray functionality
- [ ] Settings management

#### Task 5.2: Test DCC Integration
- [ ] Maya integration (se disponibile su Linux)
- [ ] Blender integration
- [ ] Houdini integration
- [ ] Nuke integration (se disponibile)
- [ ] Standalone mode

#### Task 5.3: Test Distribuzioni
- [ ] Ubuntu 20.04 LTS
- [ ] Ubuntu 22.04 LTS
- [ ] Fedora 38+
- [ ] Arch Linux
- [ ] openSUSE
- [ ] Debian 12

#### Task 5.4: Test Scenari
- [ ] Installazione utente singolo (no root)
- [ ] Installazione system-wide (con root)
- [ ] Upgrade da versione precedente
- [ ] Multiple instance contemporanee
- [ ] Diverse versioni Python (3.9, 3.10, 3.11)

### FASE 6: Documentazione e Release (Settimana 6)

**Obiettivo:** Documentare e preparare rilascio

#### Task 6.1: Documentazione
- [ ] Aggiornare README.md con istruzioni Linux
- [ ] Creare `INSTALL_LINUX.md`
- [ ] Documentare dipendenze per distro
- [ ] Creare troubleshooting guide
- [ ] Aggiornare CLAUDE.md con info Linux

#### Task 6.2: Changelog
- [ ] Documentare tutte le modifiche
- [ ] Creare lista breaking changes (se presenti)
- [ ] Documentare nuove features Linux

#### Task 6.3: Release
- [ ] Tag versione `v2.1.0-linux-beta`
- [ ] Creare release notes
- [ ] Pubblicare AppImage su GitHub releases
- [ ] Annunciare su forum/community

---

## Checklist Modifiche File

### File da Modificare (50+ file)

#### Core Scripts (13 file)
- [x] Analizzato - [ ] Modificato - `Prism/Scripts/PrismCore.py` (20+ modifiche)
- [x] Analizzato - [ ] Modificato - `Prism/Scripts/PrismInstaller.py` (8+ modifiche)
- [x] Analizzato - [ ] Modificato - `Prism/Scripts/PrismTray.py` (4 modifiche)
- [x] Analizzato - [ ] Modificato - `Prism/Scripts/PrismSettings.py` (2 modifiche)
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/PrismUtils/Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/PrismUtils/Projects.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/PrismUtils/MediaManager.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/PrismUtils/Products.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/PrismUtils/MediaProducts.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/ProjectScripts/StateManagerNodes/default_Export.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/ProjectScripts/StateManagerNodes/default_ImageRender.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Scripts/ProjectScripts/StateManagerNodes/default_Playblast.py`
- [ ] Creato - `Prism/Scripts/PrismUtils/PlatformUtils.py` (NUOVO)

#### Plugin Apps (10 file)
- [x] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Maya/Scripts/Prism_Maya_Integration.py`
- [x] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Blender/Scripts/Prism_Blender_Integration.py`
- [x] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Houdini/Scripts/Prism_Houdini_Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Nuke/Scripts/Prism_Nuke_Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/3dsMax/Scripts/Prism_3dsMax_Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Cinema4D/Scripts/Prism_Cinema4D_Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Photoshop/Scripts/Prism_Photoshop_Integration.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Photoshop/Scripts/Prism_Photoshop_Functions.py`
- [x] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/Standalone/Scripts/Prism_Standalone_Functions.py`
- [ ] Analizzato - [ ] Modificato - `Prism/Plugins/Apps/PureRef/Scripts/Prism_PureRef_externalAccess_Functions.py`

#### Launcher Scripts (3 file NUOVI)
- [ ] Creato - `Prism/prism.sh`
- [ ] Creato - `Prism/setup.sh`
- [ ] Creato - `Prism/uninstall.sh`

#### Build/Package Files (4 file NUOVI)
- [ ] Creato - `requirements.txt`
- [ ] Creato - `install_dependencies.sh`
- [ ] Creato - `INSTALL_LINUX.md`
- [ ] Creato - `AppImage/AppRun` (per AppImage build)

#### Altri File
- [ ] Aggiornato - `README.md`
- [ ] Aggiornato - `CLAUDE.md`
- [ ] Creato - `CHANGELOG_LINUX.md`

---

## Rischi e Mitigazioni

### Rischi Tecnici

#### 1. Incompatibilità Qt/PySide
**Rischio:** Differenze tra PySide2/PySide6 su Linux
**Probabilità:** Media
**Impatto:** Alto
**Mitigazione:**
- Usare qtpy come astrazione (già presente)
- Testare con entrambe le versioni
- Documentare versioni supportate

#### 2. Dipendenze Sistema Mancanti
**Rischio:** Librerie sistema non disponibili su alcune distro
**Probabilità:** Alta
**Impatto:** Medio
**Mitigazione:**
- Bundle dipendenze in AppImage
- Documentare chiaramente requirements per distro
- Fornire script check dipendenze

#### 3. Permessi File System
**Rischio:** Problemi permessi /opt, /usr/share su Linux
**Probabilità:** Media
**Impatto:** Medio
**Mitigazione:**
- Preferire installazione user-local (~/.local)
- Implementare fallback se permessi insufficienti
- Supportare sia root che non-root install

#### 4. Path Differences
**Rischio:** Percorsi hardcoded causano errori
**Probabilità:** Alta
**Impatto:** Alto
**Mitigazione:**
- Sostituire TUTTI i percorsi hardcoded con utility cross-platform
- Testing estensivo su diverse configurazioni
- Logging dettagliato per debugging path issues

#### 5. DCC Detection Failure
**Rischio:** Non rilevamento DCC installate in path non standard
**Probabilità:** Media
**Impatto:** Alto
**Mitigazione:**
- Implementare fallback a ricerca manuale
- Permettere configurazione manuale path
- Usare environment variables quando disponibili
- Logging chiaro per debugging

### Rischi di Progetto

#### 6. Scope Creep
**Rischio:** Aggiunta features non previste durante porting
**Probabilità:** Media
**Impatto:** Medio
**Mitigazione:**
- Definire chiaramente scope: solo porting, no new features
- Creare issue separate per enhancement
- Focus su parità funzionale Windows

#### 7. Testing Insufficiente
**Rischio:** Bug non scoperti su configurazioni specifiche
**Probabilità:** Alta
**Impatto:** Alto
**Mitigazione:**
- Test su multiple distro (Ubuntu, Fedora, Arch minimo)
- Beta testing con community
- Setup CI/CD con test automatici
- Creare suite test completa

#### 8. Regressioni Windows
**Rischio:** Modifiche rompono funzionalità Windows
**Probabilità:** Media
**Impatto:** CRITICO
**Mitigazione:**
- Test Windows dopo OGNI modifica
- CI/CD con test Windows automatici
- Code review attento
- Uso estensivo di platform guards (`if platform.system() == ...`)

---

## Stima Effort

### Breakdown Ore

| Fase | Task | Ore Stimate | Difficoltà |
|------|------|-------------|------------|
| **FASE 1: Preparazione** | | | |
| | Setup ambiente | 8h | Bassa |
| | Review/merge PR #33 | 8h | Media |
| | Setup CI/CD | 8h | Media |
| | **Subtotale Fase 1** | **24h** | |
| **FASE 2: Core System** | | | |
| | Creare PlatformUtils | 16h | Media |
| | Modificare PrismCore.py | 32h | Alta |
| | Modificare PrismInstaller.py | 16h | Media |
| | Modificare PrismTray.py | 8h | Bassa |
| | Testing core | 16h | Media |
| | **Subtotale Fase 2** | **88h** | |
| **FASE 3: Plugin System** | | | |
| | Creare DCC Detection utility | 8h | Media |
| | Maya plugin | 8h | Media |
| | Blender plugin | 8h | Media |
| | Houdini plugin | 8h | Media |
| | Nuke plugin | 8h | Media |
| | Altri plugin (Cinema4D, etc) | 8h | Bassa |
| | Standalone plugin | 16h | Alta |
| | Testing plugins | 16h | Media |
| | **Subtotale Fase 3** | **80h** | |
| **FASE 4: Build System** | | | |
| | Shell scripts (.sh) | 8h | Bassa |
| | Requirements & deps | 8h | Media |
| | AppImage packaging | 24h | Alta |
| | Testing packaging | 8h | Media |
| | **Subtotale Fase 4** | **48h** | |
| **FASE 5: Testing** | | | |
| | Test funzionali | 24h | Media |
| | Test DCC integration | 16h | Media |
| | Test multi-distro | 24h | Alta |
| | Bug fixing | 40h | Alta |
| | **Subtotale Fase 5** | **104h** | |
| **FASE 6: Documentazione** | | | |
| | Documentazione utente | 16h | Bassa |
| | Documentazione sviluppatore | 8h | Bassa |
| | Release notes | 4h | Bassa |
| | Release preparation | 4h | Bassa |
| | **Subtotale Fase 6** | **32h** | |
| **TOTALE** | | **376h** | |

**Conversione in Settimane:**
- A 40 ore/settimana: **9.4 settimane** (~2.5 mesi)
- A 30 ore/settimana: **12.5 settimane** (~3 mesi)
- Con buffer 30%: **12-16 settimane** (3-4 mesi)

---

## Conclusioni e Raccomandazioni

### Fattibilità

Il porting di Prism Pipeline a Linux è **FATTIBILE** ma richiede:
- **Effort significativo:** 3-4 mesi di sviluppo full-time
- **Testing estensivo:** Multiple distro e configurazioni
- **Attenzione ai dettagli:** Molti piccoli punti di integrazione

### Priorità Azioni

#### PRIORITÀ 1 (Immediata) - Fondamenta
1. **Merge PR #33** - Integrare lavoro già fatto
2. **Creare PlatformUtils** - Astrazione cross-platform
3. **Modificare PrismCore.py** - Cuore dell'applicazione
4. **Creare shell scripts** - Launcher funzionanti

#### PRIORITÀ 2 (Breve termine) - Funzionalità Core
1. **Plugin Blender/Houdini** - DCC più usati su Linux
2. **AppImage packaging** - Distribuzione facile
3. **Testing Ubuntu/Fedora** - Distro più comuni

#### PRIORITÀ 3 (Medio termine) - Completezza
1. **Altri plugin DCC**
2. **Testing distro aggiuntive**
3. **Flatpak/Snap packaging**
4. **Documentazione completa**

### Raccomandazioni Strategiche

#### 1. Approccio Incrementale
- **Non** fare "big bang release"
- Rilasciare **beta Linux-only** per feedback community
- Iterare rapidamente su bug reports
- Mantenere parità con versione Windows

#### 2. Community Engagement
- **Coinvolgere** contributor di PR #33
- **Accettare** contributi community per testing
- Creare **Linux beta tester group**
- Forum dedicato per issue Linux

#### 3. Quality Assurance
- **Setup CI/CD** immediato per test continui
- **Test Windows** dopo ogni modifica (evitare regressioni)
- **Test matrix:** Python versions × Distros × DCC versions
- **Code review** rigoroso per modifiche cross-platform

#### 4. Documentazione
- Documentare **TUTTE** le differenze Linux/Windows
- Creare **troubleshooting guide** dettagliata
- Video tutorial per installazione Linux
- FAQ dedicata per problemi comuni Linux

### Alternativa: Supporto Community

Se il tempo di sviluppo (3-4 mesi) è eccessivo, considerare:

#### Opzione A: Community-Driven Port
- **Accettare PR** da community (come PR #33)
- **Fornire guidelines** per contributi
- **Review e merge** incrementale
- **Supporto limitato** (best effort)

#### Opzione B: Fork Ufficiale Linux
- Sponsorizzare fork **deltahoch3/Prism-Linux**
- Fornire supporto tecnico
- Merge periodico modifiche upstream
- Convergenza eventuale in futuro

### Benefici Attesi

#### Per Utenti
- **Accesso** a Prism su Linux (richiesta alta in VFX industry)
- **Performance** migliori su Linux (tipico per VFX workstations)
- **Integrazione** con pipeline esistenti Linux
- **Costi** ridotti (no licenze Windows)

#### Per Progetto
- **User base** ampliata significativamente
- **Contributi** community aumentati
- **Reputazione** migliorata in industry VFX
- **Competitività** con altre pipeline (Kitsu, Zou, etc.)

#### Per Codebase
- **Qualità** migliorata (cross-platform = meno hardcoding)
- **Architettura** più pulita (astrazione piattaforma)
- **Testing** più robusto
- **Manutenibilità** aumentata

---

## Next Steps Immediati

### Per Iniziare OGGI

1. **Creare issue GitHub:** "Linux Support - Master Tracking Issue"
2. **Setup environment Linux:** VM o container per sviluppo
3. **Review PR #33 in dettaglio:** Capire modifiche già fatte
4. **Contattare autore PR #33:** Verificare interesse continuare lavoro
5. **Creare project board:** Tracciare tutte le task identificate
6. **Decisione commitment:** Validare se procedere con porting completo

### Contatti e Risorse

- **GitHub Issues:** Per domande tecniche
- **Community Forum:** https://prism-pipeline.com/forum/
- **Discord/Slack:** Per discussioni real-time (se disponibile)
- **Email:** contact@prism-pipeline.com

---

## Appendice: Comandi Utili Linux

### Test Dipendenze
```bash
# Check Python version
python3 --version

# Check PySide2/6
python3 -c "from PySide2 import QtCore; print(QtCore.__version__)" 2>/dev/null || echo "PySide2 not installed"
python3 -c "from PySide6 import QtCore; print(QtCore.__version__)" 2>/dev/null || echo "PySide6 not installed"

# Check altre dipendenze
python3 -c "import imageio, numpy, psutil; print('OK')"

# Check ffmpeg
ffmpeg -version

# Check XDG directories
echo $XDG_CONFIG_HOME
echo $XDG_DATA_HOME
echo $XDG_CACHE_HOME
```

### Troubleshooting
```bash
# Log completo esecuzione
python3 -u /path/to/Prism/Scripts/PrismCore.py 2>&1 | tee prism.log

# Check permessi
ls -la ~/.local/share/Prism2
ls -la ~/.config/Prism2

# Cleanup
rm -rf ~/.local/share/Prism2
rm -rf ~/.config/Prism2
rm -rf ~/.cache/Prism2
rm -f ~/.local/share/applications/Prism*.desktop
rm -f ~/.config/autostart/PrismTray.desktop
```

### Build Test AppImage
```bash
# Estrai AppImage per debug
./Prism-2.0.17-x86_64.AppImage --appimage-extract

# Esegui extracted
./squashfs-root/AppRun

# Check dipendenze AppImage
ldd ./squashfs-root/usr/bin/python3
```

---

**Fine Analisi**

Documento compilato: 2025-11-15
Autore: Claude Code Analysis
Versione: 1.0
