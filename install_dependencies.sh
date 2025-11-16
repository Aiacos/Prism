#!/usr/bin/env bash
# Prism Pipeline - Dependency Installation Script for Linux
# ==========================================================
# This script helps install Python dependencies for Prism Pipeline on Linux
# It detects your distribution and offers appropriate installation methods

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    else
        echo "unknown"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect Python version
detect_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        print_msg "$GREEN" "✓ Found Python: $PYTHON_VERSION"
        return 0
    else
        print_msg "$RED" "✗ Python 3 not found!"
        return 1
    fi
}

# Install via system package manager
install_system_packages() {
    local distro=$1

    print_msg "$BLUE" "\n=== Installing via System Package Manager ==="

    case "$distro" in
        ubuntu|debian|pop)
            print_msg "$YELLOW" "Installing for Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y \
                python3 \
                python3-pip \
                python3-pyside2 \
                python3-qtpy \
                python3-numpy \
                python3-psutil \
                ffmpeg \
                libgl1-mesa-glx \
                libxcb-xinerama0 \
                xdg-utils
            ;;

        fedora)
            print_msg "$YELLOW" "Installing for Fedora..."

            # Check Python version for PySide choice
            local py_minor=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
            local pyside_pkg="python3-pyside2"
            if [ "$py_minor" -ge 11 ]; then
                pyside_pkg="python3-pyside6"
                print_msg "$YELLOW" "Python 3.11+ detected, using PySide6"
            fi

            sudo dnf install -y \
                python3 \
                python3-pip \
                $pyside_pkg \
                python3-qtpy \
                python3-numpy \
                python3-psutil \
                python3-imageio \
                ffmpeg \
                mesa-libGL \
                libxcb \
                xdg-utils
            ;;

        centos|rhel)
            print_msg "$YELLOW" "Installing for RHEL/CentOS..."
            sudo dnf install -y \
                python3 \
                python3-pip \
                python3-pyside2 \
                python3-qtpy \
                python3-numpy \
                python3-psutil \
                ffmpeg \
                mesa-libGL \
                libxcb \
                xdg-utils
            ;;

        arch|manjaro)
            print_msg "$YELLOW" "Installing for Arch Linux..."
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                python-pyside2 \
                python-qtpy \
                python-numpy \
                python-psutil \
                ffmpeg \
                mesa \
                xdg-utils
            ;;

        opensuse*)
            print_msg "$YELLOW" "Installing for openSUSE..."
            sudo zypper install -y \
                python3 \
                python3-pip \
                python3-pyside2 \
                python3-qtpy \
                python3-numpy \
                python3-psutil \
                ffmpeg \
                Mesa-libGL1 \
                xdg-utils
            ;;

        *)
            print_msg "$RED" "Unknown distribution: $distro"
            print_msg "$YELLOW" "Please install dependencies manually or use pip method below"
            return 1
            ;;
    esac

    print_msg "$GREEN" "✓ System packages installed successfully"
}

# Install via pip
install_pip_packages() {
    print_msg "$BLUE" "\n=== Installing via pip ==="

    if ! command_exists pip3; then
        print_msg "$RED" "pip3 not found. Please install python3-pip first."
        return 1
    fi

    # Check Python version
    local py_major=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    local py_minor=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

    # Warn about Python 3.14+
    if [ "$py_minor" -ge 14 ]; then
        print_msg "$YELLOW" "⚠ WARNING: Python 3.14+ detected!"
        print_msg "$YELLOW" "  PySide6 may not have pip packages for Python 3.14 yet."
        print_msg "$YELLOW" "  Recommended: Use system packages instead (option 1)"
        read -p "Continue with pip anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi

    # Check if we should use --break-system-packages (Fedora 43+, etc.)
    local pip_args=""
    if [ "$py_minor" -ge 11 ]; then
        print_msg "$YELLOW" "Python 3.11+ detected, using --break-system-packages flag"
        pip_args="--break-system-packages"
    fi

    print_msg "$YELLOW" "Installing Python dependencies..."
    if pip3 install $pip_args --user -r "$SCRIPT_DIR/requirements.txt"; then
        print_msg "$GREEN" "✓ pip packages installed successfully"
    else
        print_msg "$RED" "✗ pip installation failed"
        print_msg "$YELLOW" "Try system packages instead: ./install_dependencies.sh --system"
        return 1
    fi
}

# Install development dependencies
install_dev_packages() {
    print_msg "$BLUE" "\n=== Installing Development Dependencies ==="

    if [ ! -f "$SCRIPT_DIR/requirements-dev.txt" ]; then
        print_msg "$YELLOW" "requirements-dev.txt not found, skipping dev dependencies"
        return 0
    fi

    local pip_args=""
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
        pip_args="--break-system-packages"
    fi

    pip3 install $pip_args --user -r "$SCRIPT_DIR/requirements-dev.txt"
    print_msg "$GREEN" "✓ Development dependencies installed"
}

# Main menu
show_menu() {
    print_msg "$BLUE" "╔════════════════════════════════════════════════════════╗"
    print_msg "$BLUE" "║   Prism Pipeline - Dependency Installation Helper     ║"
    print_msg "$BLUE" "╚════════════════════════════════════════════════════════╝"
    echo ""
    print_msg "$YELLOW" "Detected: $(detect_distro)"
    echo ""
    echo "Choose installation method:"
    echo "  1) System packages (recommended - uses dnf/apt/pacman)"
    echo "  2) pip packages (installs to ~/.local)"
    echo "  3) Both (system packages + pip for missing packages)"
    echo "  4) Development dependencies (includes testing tools)"
    echo "  5) Check installed dependencies"
    echo "  6) Exit"
    echo ""
}

# Check what's installed
check_dependencies() {
    print_msg "$BLUE" "\n=== Checking Dependencies ==="

    local deps=("psutil" "imageio" "numpy" "qtpy" "PySide2" "PySide6")

    for dep in "${deps[@]}"; do
        if $PYTHON_CMD -c "import $dep" 2>/dev/null; then
            local version=$($PYTHON_CMD -c "import $dep; print($dep.__version__ if hasattr($dep, '__version__') else 'unknown')" 2>/dev/null)
            print_msg "$GREEN" "✓ $dep ($version)"
        else
            print_msg "$RED" "✗ $dep (not installed)"
        fi
    done

    # Check system tools
    echo ""
    print_msg "$BLUE" "System Tools:"
    for tool in ffmpeg xdg-open; do
        if command_exists "$tool"; then
            print_msg "$GREEN" "✓ $tool"
        else
            print_msg "$RED" "✗ $tool (not installed)"
        fi
    done
}

# Main script
main() {
    print_msg "$GREEN" "Starting Prism dependency installer..."
    echo ""

    # Detect Python
    if ! detect_python; then
        print_msg "$RED" "Please install Python 3.9 or later first."
        exit 1
    fi

    # Detect distribution
    DISTRO=$(detect_distro)

    # Show menu if no arguments
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            read -p "Enter choice [1-6]: " choice

            case $choice in
                1)
                    install_system_packages "$DISTRO"
                    ;;
                2)
                    install_pip_packages
                    ;;
                3)
                    install_system_packages "$DISTRO" || true
                    install_pip_packages
                    ;;
                4)
                    install_dev_packages
                    ;;
                5)
                    check_dependencies
                    ;;
                6)
                    print_msg "$GREEN" "Goodbye!"
                    exit 0
                    ;;
                *)
                    print_msg "$RED" "Invalid choice"
                    ;;
            esac

            echo ""
            read -p "Press Enter to continue..."
        done
    else
        # Non-interactive mode
        case "$1" in
            --system)
                install_system_packages "$DISTRO"
                ;;
            --pip)
                install_pip_packages
                ;;
            --dev)
                install_dev_packages
                ;;
            --check)
                check_dependencies
                ;;
            --help|-h)
                echo "Usage: $0 [OPTION]"
                echo ""
                echo "Options:"
                echo "  --system    Install via system package manager"
                echo "  --pip       Install via pip"
                echo "  --dev       Install development dependencies"
                echo "  --check     Check installed dependencies"
                echo "  --help      Show this help"
                echo ""
                echo "No option: Show interactive menu"
                ;;
            *)
                print_msg "$RED" "Unknown option: $1"
                print_msg "$YELLOW" "Run with --help for usage"
                exit 1
                ;;
        esac
    fi
}

# Run main
main "$@"
