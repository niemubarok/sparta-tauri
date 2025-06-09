#!/bin/bash
# Jalankan script ini SETELAH install_dependencies.sh dan setelah restart terminal
# Pastikan python3.10, pip, dan fast-alpr sudah terinstall dan ada di PATH

if command -v python3.10 &> /dev/null; then
    pip_ok=0
    python3.10 -m pip --version &> /dev/null && pip_ok=1
    if [ $pip_ok -eq 0 ]; then
        echo "pip not found, trying to install pip with ensurepip..."
        python3.10 -m ensurepip --upgrade || true
        python3.10 -m pip --version &> /dev/null && pip_ok=1
    fi
    if [ $pip_ok -eq 0 ]; then
        echo "ensurepip failed or pip still not available, downloading get-pip.py..."
        curl -sSLo get-pip.py https://bootstrap.pypa.io/get-pip.py
        python3.10 get-pip.py
        python3.10 -m pip --version &> /dev/null && pip_ok=1
    fi
    if [ $pip_ok -eq 0 ]; then
        echo "pip still not available after get-pip.py. Please check your Python installation. Skipping fast-alpr check/install."
    else
        if python3.10 -m pip show fast-alpr &> /dev/null; then
            echo "fast-alpr already installed. Skipping fast-alpr install."
        else
            echo "Installing fast-alpr with pip..."
            python3.10 -m pip install --upgrade pip
            python3.10 -m pip install fast-alpr
        fi
        echo "Inisialisasi fast-alpr agar model otomatis terdownload..."
        python3.10 -c "import fast_alpr; alpr = fast_alpr.ALPR(detector_model='yolo-v9-t-384-license-plate-end2end', ocr_model='global-plates-mobile-vit-v2-model'); import numpy as np; from PIL import Image; dummy = np.zeros((1,1,3), dtype=np.uint8); Image.fromarray(dummy).save('alpr_dummy.jpg'); alpr.predict('alpr_dummy.jpg'); print('fast-alpr model download/init done')" || { echo 'GAGAL inisialisasi fast-alpr'; exit 1; }
        rm -f alpr_dummy.jpg
    fi
else
    echo "python3.10 not found in PATH. Please restart your terminal or add Python 3.10 to PATH."
fi
