#!/bin/bash
set -e

# Script to install Python 3.10 and WebView2 dependencies for Linux/Raspberry Pi

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

install_python_linux() {
    if command -v python3.10 &> /dev/null; then
        echo "Python 3.10 already installed. Skipping Python install."
    else
        echo "Installing Python 3.10..."
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3.10 python3.10-venv python3.10-distutils python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3.10 python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm python310 python-pip
        else
            echo "Please install Python 3.10 manually."
        fi
    fi
}

install_webview2_linux() {
    if pkg-config --exists webkit2gtk-4.0; then
        echo "webkit2gtk already installed. Skipping webkit2gtk install."
    else
        echo "WebView2 is not natively supported on Linux. For Tauri, install webkit2gtk."
        if command -v apt &> /dev/null; then
            sudo apt install -y libwebkit2gtk-4.0-dev
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y webkit2gtk3-devel
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm webkit2gtk
        fi
    fi
}

if [[ "$OS" == "Linux" ]]; then
    install_python_linux
    install_webview2_linux
elif [[ "$OS" == "Darwin" ]]; then
    echo "For macOS, use Homebrew: brew install python@3.10"
else
    echo "Unsupported OS: $OS"
fi


echo "All dependencies installed (or instructions provided)."
