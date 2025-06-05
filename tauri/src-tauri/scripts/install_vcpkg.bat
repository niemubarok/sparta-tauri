@echo off
echo Installing vcpkg and FFmpeg dependencies...

:: Cek apakah folder vcpkg sudah ada
if exist vcpkg (
    echo vcpkg sudah ada, menggunakan cache...
    cd vcpkg
) else (
    echo Meng-clone vcpkg...
    git clone https://github.com/Microsoft/vcpkg.git
    cd vcpkg
    call bootstrap-vcpkg.bat
)

:: Integrasi vcpkg dengan Visual Studio (opsional, bisa dicek juga jika perlu)
call vcpkg integrate install

:: Cek apakah FFmpeg sudah terinstall
if exist installed\x64-windows\bin\ffmpeg.exe (
    echo FFmpeg sudah terinstall, menggunakan cache...
) else (
    echo Menginstall FFmpeg...
    call vcpkg install ffmpeg:x64-windows
)

:: Set environment variables
setx VCPKG_ROOT "%CD%"
setx PKG_CONFIG_PATH "%CD%\installed\x64-windows\lib\pkgconfig"

echo Installation completed!
echo Please restart your terminal/IDE for the environment variables to take effect. 