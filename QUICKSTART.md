# Prism Pipeline - Quick Start Guide (Linux)

## Installazione Rapida

### 1. Clona il Repository

```bash
cd ~
git clone https://github.com/PrismPipeline/Prism.git
cd Prism
git checkout feature/linux-compatibility
```

### 2. Installa le Dipendenze

**Metodo consigliato** - usa i pacchetti di sistema:

```bash
sudo ./install_dependencies.sh --system
```

**Oppure** usa il menu interattivo:

```bash
./install_dependencies.sh
# Scegli opzione 1 (System packages)
```

<details>
<summary>Installazione manuale per distribuzione</summary>

**Fedora / RHEL / CentOS:**
```bash
sudo dnf install -y python3 python3-pip python3-pyside6 \
    python3-numpy python3-psutil python3-imageio \
    ffmpeg mesa-libGL libxcb xdg-utils
```

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pyside2 \
    python3-numpy python3-psutil ffmpeg \
    libgl1-mesa-glx libxcb-xinerama0 xdg-utils
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip python-pyside2 \
    python-numpy python-psutil python-imageio \
    ffmpeg mesa xdg-utils
```
</details>

### 3. Verifica Dipendenze

```bash
./install_dependencies.sh --check
```

Dovresti vedere:
```
✓ psutil
✓ imageio
✓ numpy
✓ qtpy
✓ PySide6 (o PySide2)
✓ ffmpeg
✓ xdg-open
```

### 4. Avvia Prism

```bash
cd Prism
./prism.sh
```

**Oppure** esegui direttamente:

```bash
cd Prism
python3 Scripts/PrismCore.py
```

## Primi Passi

### Crea il Tuo Primo Progetto

1. Avvia Prism: `./prism.sh`
2. Clicca "Create Project"
3. Imposta nome e cartella del progetto
4. Clicca "Create"

### Integrazione con DCC

Prism rileva automaticamente:
- **Blender** → `/usr/bin/blender`, `/opt/blender*`, `/snap/blender`
- **Houdini** → `$HFS`, `/opt/hfs*`
- **Maya** → `/usr/autodesk/maya*`
- **Nuke** → `/usr/local/Nuke*`, `/opt/Nuke*`

Per configurazione manuale: **Prism Settings → DCC Apps → Add**

### System Tray

Avvia Prism Tray per accesso rapido:

```bash
cd Prism
python3 Scripts/PrismTray.py &
```

Per avvio automatico: **Prism Settings → User → Launch on system startup**

## Versioni Python Supportate

| Python | Qt Framework | Raccomandazione |
|--------|-------------|-----------------|
| 3.9-3.10 | PySide2 | Usa pacchetti sistema |
| 3.11-3.13 | PySide6 | Usa pacchetti sistema |
| 3.14+ | PySide6 6.8+ | **Solo pacchetti sistema** |

## Comandi Utili

```bash
# Verifica dipendenze
./install_dependencies.sh --check

# Installazione completa (sistema + pip)
./install_dependencies.sh

# Installazione dipendenze sviluppo
./install_dependencies.sh --dev

# Avvia Project Browser
cd Prism && ./prism.sh

# Avvia Settings
cd Prism && python3 Scripts/PrismSettings.py

# Avvia System Tray
cd Prism && python3 Scripts/PrismTray.py
```

## Risoluzione Problemi

### Prism non si avvia

```bash
# Controlla Python
python3 --version  # Deve essere 3.9+

# Controlla dipendenze
python3 -c "from PySide2 import QtCore; print('OK')"
# oppure per PySide6
python3 -c "from PySide6 import QtCore; print('OK')"

# Verifica log
cd Prism
python3 Scripts/PrismCore.py 2>&1 | tee prism.log
```

### DCC non rilevato

```bash
# Verifica percorso
which blender  # Per Blender
echo $HFS      # Per Houdini

# Aggiungi manualmente in Prism Settings → DCC Apps
```

### Errori Qt/PySide

```bash
# Usa pacchetti sistema invece di pip
sudo dnf install python3-pyside6  # Fedora
sudo apt install python3-pyside2  # Ubuntu/Debian
```

### Python 3.14 - Errore PySide6

**Usa sempre pacchetti sistema per Python 3.14+:**
```bash
sudo ./install_dependencies.sh --system
```

## Percorsi Importanti

| Cosa | Percorso |
|------|----------|
| Config | `~/.config/Prism2` |
| Data | `~/.local/share/Prism2` |
| Cache | `~/.cache/Prism2` |
| Menu Apps | `~/.local/share/applications/` |
| Autostart | `~/.config/autostart/` |

## Risorse

- **Documentazione**: https://prism-pipeline.com/docs/
- **Forum**: https://prism-pipeline.com/forum/
- **GitHub**: https://github.com/PrismPipeline/Prism
- **Guida Completa Linux**: Vedi `INSTALL_LINUX.md`
- **Documentazione Sviluppo**: Vedi `CLAUDE.md`

## Prossimi Passi

1. ✅ Dipendenze installate
2. ✅ Prism avviato
3. 📝 Crea il tuo primo progetto
4. 🎨 Configura le tue DCC apps
5. 🚀 Inizia a lavorare!

---

**Versione**: Prism 2.0.17 + Linux Compatibility
**Branch**: `feature/linux-compatibility`
**Testato su**: Fedora 43, Ubuntu 22.04, Arch Linux
