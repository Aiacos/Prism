# Prism Pipeline

This is the official repository of the Prism Pipeline.

Prism automates and simplifies the workflow of animation and VFX projects.

You can find more information on the website:

https://prism-pipeline.com/

This repository contains the Prism core application and the officially available open source plugins.
Additional features and plugins are available on the Prism website.


## Getting Started

On the [website](https://prism-pipeline.com/downloads/) you can find the latest official installer.

For a getting started guide about how to use Prism see the [Documentation](https://prism-pipeline.com/docs/latest/).


## Installing

### Windows

Download the installer from the [website](https://prism-pipeline.com/downloads/)
(This version allows you to automatically update Prism and install new plugins)

or to install Prism manually:
* Download or clone this repository and download the [Prism dependencies](https://www.dropbox.com/scl/fi/bmgsht89nb9u04sqprzrp/Prism_dependencies_v2.0.5.zip?rlkey=wy0rtw56chky6kt1mnxnept0t&st=jkiho4o9&dl=1).

* Extract the dependencies and copy the extracted folders into the "Prism" folder of this repository.

* Now the "Prism" folder should contain the folders like:
"Plugins", "Python39", "PythonLibs", "Scripts", ...

* Execute the setup.bat file to launch Prism.

### Linux (Beta - `feature/linux-compatibility` branch)

**Quick Start:**

```bash
git clone https://github.com/PrismPipeline/Prism.git
cd Prism
git checkout feature/linux-compatibility
sudo ./install_dependencies.sh --system
cd Prism
./prism.sh
```

**Complete Guides:**
- 🚀 [Quick Start Guide](QUICKSTART.md) - Fast installation
- 📖 [Complete Linux Installation Guide](INSTALL_LINUX.md) - Detailed instructions
- 🔧 [Developer Documentation](CLAUDE.md) - For contributors
- 📚 [Development History](LINUX_DEVELOPMENT_HISTORY.md) - Technical details

**Supported Distributions:**
- Fedora / RHEL / CentOS
- Ubuntu / Debian / Pop!_OS
- Arch Linux / Manjaro
- openSUSE

**Python Support:** 3.9, 3.10, 3.11, 3.12, 3.13, 3.14

## License

This project is licensed under the GNU LGPL-3.0-or-later License - see the [license-LGPL.txt](license-LGPL.txt) file for details.