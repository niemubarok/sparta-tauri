REM Install pip dan fast-alpr jika belum ada
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    set PIP_OK=0
    python -m pip --version >nul 2>nul
    if !ERRORLEVEL!==0 (
        set PIP_OK=1
    )
    REM Cek ulang pip setelah ensurepip
    if !PIP_OK!==0 (
        echo pip not found, trying to install pip with ensurepip...
        python -m ensurepip --upgrade
        python -m pip --version >nul 2>nul
        if !ERRORLEVEL!==0 (
            set PIP_OK=1
        )
    )
    REM Cek ulang pip setelah get-pip.py
    if !PIP_OK!==0 (
        echo ensurepip failed or pip still not available, downloading get-pip.py...
        powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile 'get-pip.py'"
        python get-pip.py
        python -m pip --version >nul 2>nul
        if !ERRORLEVEL!==0 (
            set PIP_OK=1
        )
    )
    if !PIP_OK!==1 (
        echo pip still not available after get-pip.py. Please check your Python installation. Skipping fast-alpr check/install.
    ) else (
        python -m pip show fast-alpr >nul 2>nul
        if !ERRORLEVEL!==0 (
            echo fast-alpr already installed. Skipping fast-alpr install.
        ) else (
            echo Installing fast-alpr with pip...
            python -m pip install --upgrade pip
            python -m pip install fast-alpr
        )
    )
    REM Inisialisasi model alpr
    echo Inisialisasi fast-alpr agar model otomatis terdownload...
    python -c "import fast_alpr; alpr = fast_alpr.ALPR(detector_model='yolo-v9-t-384-license-plate-end2end', ocr_model='global-plates-mobile-vit-v2-model'); import numpy as np; from PIL import Image; dummy = np.zeros((1,1,3), dtype=np.uint8); Image.fromarray(dummy).save('alpr_dummy.jpg'); alpr.predict('alpr_dummy.jpg'); print('fast-alpr model download/init done')" || (echo GAGAL inisialisasi fast-alpr & pause)
    del alpr_dummy.jpg 2>nul
) else (
    echo Python not found in PATH. Please restart your terminal atau add Python ke PATH.
)
@echo off
REM Jalankan script ini SETELAH install_dependencies.cmd dan setelah restart terminal
REM Pastikan python, pip, dan fast-alpr sudah terinstall dan ada di PATH

echo Inisialisasi fast-alpr agar model otomatis terdownload...
python -c "import fast_alpr; alpr = fast_alpr.ALPR(detector_model='yolo-v9-t-384-license-plate-end2end', ocr_model='global-plates-mobile-vit-v2-model'); import numpy as np; from PIL import Image; dummy = np.zeros((1,1,3), dtype=np.uint8); Image.fromarray(dummy).save('alpr_dummy.jpg'); alpr.predict('alpr_dummy.jpg'); print('fast-alpr model download/init done')" || (echo GAGAL inisialisasi fast-alpr & pause)
del alpr_dummy.jpg 2>nul
