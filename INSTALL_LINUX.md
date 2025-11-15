# Prism Pipeline - Guida Installazione Linux

**Versione**: Prism 2.0.17 + Linux Compatibility
**Branch**: `feature/linux-compatibility`

> **Guida Rapida?** Vedi [QUICKSTART.md](QUICKSTART.md) per installazione veloce.

---

## Requisiti di Sistema

- **Sistema Operativo**: Linux (qualsiasi distribuzione)
- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13 o 3.14
- **Display Server**: X11 o Wayland
- **Spazio su Disco**: ~500 MB

---

## Installazione Dipendenze

### Metodo Automatico (Consigliato)

Usa lo script di installazione automatico:

```bash
cd Prism
./install_dependencies.sh
```

Lo script interattivo:
- Rileva automaticamente la tua distribuzione Linux
- Offre installazione tramite package manager di sistema (dnf/apt/pacman)
- Fallback su pip se necessario
- Verifica cosa è già installato

**Modi non-interattivi:**
```bash
./install_dependencies.sh --system  # Usa package manager di sistema
./install_dependencies.sh --pip     # Usa solo pip
./install_dependencies.sh --check   # Verifica dipendenze installate
./install_dependencies.sh --dev     # Installa dipendenze sviluppo
```

### Installazione Manuale per Distribuzione

<details>
<summary><b>Fedora / RHEL / CentOS</b></summary>

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-pyside6 \
    python3-numpy \
    python3-psutil \
    python3-imageio \
    ffmpeg \
    mesa-libGL \
    libxcb \
    xdg-utils
```

**Nota**: Per Python < 3.11, usa `python3-pyside2` invece di `python3-pyside6`
</details>

<details>
<summary><b>Ubuntu / Debian</b></summary>

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-pyside2 \
    python3-numpy \
    python3-psutil \
    ffmpeg \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    xdg-utils
```

**Nota**: Per Python >= 3.11, prova `python3-pyside6` se disponibile
</details>

<details>
<summary><b>Arch Linux / Manjaro</b></summary>

```bash
sudo pacman -S \
    python \
    python-pip \
    python-pyside6 \
    python-numpy \
    python-psutil \
    python-imageio \
    ffmpeg \
    mesa \
    xdg-utils
```
</details>

<details>
<summary><b>openSUSE</b></summary>

```bash
sudo zypper install -y \
    python3 \
    python3-pip \
    python3-pyside6 \
    python3-numpy \
    python3-psutil \
    ffmpeg \
    Mesa-libGL1 \
    xdg-utils
```
</details>

### Installazione via pip

Se preferisci usare pip invece dei pacchetti di sistema:

```bash
pip3 install --user -r requirements.txt
```

**Per Python 3.11+ o Python 3.14+** (Fedora 43+), potresti aver bisogno di:
```bash
pip3 install --user --break-system-packages -r requirements.txt
```

⚠️ **Python 3.14**: Si consiglia **SEMPRE** di usare i pacchetti di sistema invece di pip.

---

## Metodi di Installazione

### Metodo 1: Installazione Utente (Consigliato - Senza Root)

1. **Scarica o clona Prism:**
   ```bash
   cd ~
   git clone https://github.com/PrismPipeline/Prism.git
   cd Prism
   git checkout feature/linux-compatibility
   ```

2. **Installa dipendenze:**
   ```bash
   ./install_dependencies.sh --system
   ```

3. **Esegui l'installazione:**
   ```bash
   cd Prism
   ./setup.sh
   ```

4. **Avvia Prism:**
   ```bash
   ./prism.sh
   ```

### Metodo 2: Installazione di Sistema (Richiede Root)

1. **Clona in /opt:**
   ```bash
   sudo git clone https://github.com/PrismPipeline/Prism.git /opt/Prism
   cd /opt/Prism
   sudo git checkout feature/linux-compatibility
   ```

2. **Installa dipendenze:**
   ```bash
   sudo ./install_dependencies.sh --system
   ```

3. **Esegui setup:**
   ```bash
   cd /opt/Prism/Prism
   sudo ./setup.sh --system
   ```

4. **Crea symlink (opzionale):**
   ```bash
   sudo ln -s /opt/Prism/Prism/prism.sh /usr/local/bin/prism
   ```

5. **Avvia Prism:**
   ```bash
   prism
   # Oppure da menu: Applicazioni > Grafica > Prism Project Browser
   ```

---

## Integrazione con DCC

### Blender

Prism rileva automaticamente Blender in:
- `/usr/bin/blender` (pacchetto di sistema)
- `/usr/share/blender`
- `/opt/blender*` (installazione manuale)
- `/snap/blender/*/` (snap package)

**Configurazione Manuale:**
Se Blender è in una posizione personalizzata: Prism Settings > DCC Apps > Blender

### Houdini

Prism rileva Houdini tramite:
- Variabile d'ambiente `$HFS`
- `/opt/hfs*` (installazione standard Side Effects)

**Setup Houdini:**
1. Source dell'ambiente Houdini:
   ```bash
   cd /opt/hfsXX.X.XXX
   source houdini_setup
   ```

2. Avvia Prism dall'ambiente Houdini, oppure imposta `$HFS` permanentemente nel tuo profilo shell.

### Nuke

Prism cerca Nuke in:
- `/usr/local/Nuke*`
- `/opt/Nuke*`

### Maya

Maya su Linux si trova tipicamente in:
- `/usr/autodesk/maya*`
- Imposta `$MAYA_LOCATION` se in posizione personalizzata

---

## Configurazione

### Directory XDG

Prism rispetta la specifica XDG Base Directory:

- **Config**: `~/.config/Prism2` (o `$XDG_CONFIG_HOME/Prism2`)
- **Data**: `~/.local/share/Prism2` (o `$XDG_DATA_HOME/Prism2`)
- **Cache**: `~/.cache/Prism2` (o `$XDG_CACHE_HOME/Prism2`)

### Integrazione Menu Applicazioni

Il setup crea file .desktop in:
- **Utente**: `~/.local/share/applications/`
- **Sistema**: `/usr/share/applications/`

Le applicazioni appaiono in: **Applicazioni > Grafica**

### Autostart (System Tray)

Per abilitare Prism Tray all'avvio:
1. Apri Prism Settings
2. Vai al tab "User"
3. Spunta "Launch on system startup"

Questo crea: `~/.config/autostart/PrismTray.desktop`

---

## Risoluzione Problemi

### Prism non si avvia

1. **Verifica versione Python:**
   ```bash
   python3 --version  # Deve essere 3.9+
   ```

2. **Verifica dipendenze:**
   ```bash
   ./install_dependencies.sh --check
   ```

   Oppure manualmente:
   ```bash
   python3 -c "from PySide2 import QtCore; print('PySide2 OK')"
   # oppure
   python3 -c "from PySide6 import QtCore; print('PySide6 OK')"
   ```

3. **Controlla i log:**
   ```bash
   cd Prism
   python3 Scripts/PrismCore.py 2>&1 | tee prism.log
   ```

### DCC non rilevata

1. **Verifica installazione:**
   ```bash
   which blender  # Dovrebbe mostrare il percorso
   echo $HFS      # Per Houdini
   ```

2. **Configurazione manuale:**
   - Apri Prism Settings > DCC Apps
   - Clicca "Add" e naviga verso l'eseguibile DCC

### Errori di permessi

Se vedi errori di permessi in `~/.local/share/Prism2`:

```bash
# Correggi ownership
chown -R $USER:$USER ~/.local/share/Prism2
chown -R $USER:$USER ~/.config/Prism2

# Correggi permessi
chmod -R u+rwX ~/.local/share/Prism2
chmod -R u+rwX ~/.config/Prism2
```

### Errori Qt/PySide

Se vedi errori relativi a Qt:

```bash
# Usa pacchetti di sistema (consigliato)
sudo dnf install python3-pyside6  # Fedora
sudo apt install python3-pyside2  # Ubuntu/Debian
```

### Problemi con Wayland

Se usi Wayland e riscontri problemi di visualizzazione:

```bash
# Forza backend X11
QT_QPA_PLATFORM=xcb ./prism.sh
```

### Python 3.14 - Errore installazione PySide6

**Usa SEMPRE i pacchetti di sistema per Python 3.14+:**

```bash
sudo ./install_dependencies.sh --system
```

Questo installerà pacchetti pre-compilati e testati per la tua distribuzione.

---

## Disinstallazione

### Installazione Utente

```bash
cd ~/Prism/Prism
./uninstall.sh
```

Poi rimuovi le directory:
```bash
rm -rf ~/Prism
rm -rf ~/.config/Prism2
rm -rf ~/.local/share/Prism2
rm -rf ~/.cache/Prism2
```

### Installazione di Sistema

```bash
cd /opt/Prism/Prism
sudo ./uninstall.sh
```

Poi rimuovi la directory:
```bash
sudo rm -rf /opt/Prism
```

---

## Aiuto e Supporto

- **Forum**: https://prism-pipeline.com/forum/
- **Documentazione**: https://prism-pipeline.com/docs/
- **GitHub Issues**: https://github.com/PrismPipeline/Prism/issues
- **Quick Start**: Vedi [QUICKSTART.md](QUICKSTART.md)
- **Storia Sviluppo**: Vedi [LINUX_DEVELOPMENT_HISTORY.md](LINUX_DEVELOPMENT_HISTORY.md)

---

## Problemi Noti

1. **System Tray**: Alcuni ambienti desktop (GNOME) non supportano icone system tray di default. Installa l'estensione "AppIndicator".

2. **Snap Blender**: Blender installato via Snap può avere restrizioni di sandboxing. Preferisci pacchetto di sistema o installazione manuale.

3. **Wayland**: Il supporto completo a Wayland è sperimentale. Usa sessione X11 se riscontri problemi.

---

## Compatibilità Python

| Versione Python | Framework Qt | Metodo Consigliato |
|----------------|--------------|-------------------|
| 3.9 - 3.10 | PySide2 | Pacchetti sistema |
| 3.11 - 3.13 | PySide6 | Pacchetti sistema |
| 3.14+ | PySide6 6.8+ | **Solo pacchetti sistema** |

---

**Testato su**:
- Fedora 43 (Python 3.14)
- Ubuntu 22.04 (Python 3.10)
- Arch Linux (Python 3.11)

**Branch**: `feature/linux-compatibility`
**Versione**: Prism 2.0.17 + Linux Support
