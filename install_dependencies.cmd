@echo off
setlocal enabledelayedexpansion
REM Batch script to install Python 3.10, VC_redist_X64, and MicrosoftEdgeWebView2RuntimeInstallerX64 on Windows
echo Pastikan di Run sebagai Administrator

set PYTHON_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
set VCREDIST_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe
set WEBVIEW2_URL=https://go.microsoft.com/fwlink/p/?LinkId=2124703
set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py

REM Use OS temp folder for downloads
set "TEMP_DIR=%TEMP%"

echo Downloading dependencies...
REM Check if Python 3.10 is installed
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python --version 2>nul | findstr /C:"3.10" >nul
    if %ERRORLEVEL%==0 (
        set PYTHON_INSTALLED=1
    ) else (
        set PYTHON_INSTALLED=0
    )
) else (
    set PYTHON_INSTALLED=0
)

if %PYTHON_INSTALLED%==0 (
    if not exist "%TEMP_DIR%\python-3.10.11-amd64.exe" (
        powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile '%TEMP_DIR%\python-3.10.11-amd64.exe'"
    )
    echo Installing...
    start /wait "" "%TEMP_DIR%\python-3.10.11-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1
)

REM Check if VC_redist_X64 is installed
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>nul
if %ERRORLEVEL%==0 (
    echo VC_redist_X64 already installed. Skipping VC_redist install.
) else (
    if not exist "%TEMP_DIR%\vc_redist.x64.exe" (
        echo Downloading VC_redist_X64...
        powershell -Command "Invoke-WebRequest -Uri %VCREDIST_URL% -OutFile '%TEMP_DIR%\vc_redist.x64.exe'"
    )
    echo Installing VC_redist_X64...
    start /wait "" "%TEMP_DIR%\vc_redist.x64.exe" /install /quiet /norestart
)

REM Check WebView2 Evergreen Runtime via registry key and pv value
set WEBVIEW2_GUID={F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}
set WEBVIEW2_INSTALLED=0

REM 64-bit HKLM
for /f "skip=2 tokens=3" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\%WEBVIEW2_GUID%" /v pv 2^>nul') do (
    if not "%%A"=="0.0.0.0" if not "%%A"=="" set WEBVIEW2_INSTALLED=1
)
REM 64-bit/32-bit HKCU
for /f "skip=2 tokens=3" %%A in ('reg query "HKCU\Software\Microsoft\EdgeUpdate\Clients\%WEBVIEW2_GUID%" /v pv 2^>nul') do (
    if not "%%A"=="0.0.0.0" if not "%%A"=="" set WEBVIEW2_INSTALLED=1
)
REM 32-bit HKLM
for /f "skip=2 tokens=3" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\%WEBVIEW2_GUID%" /v pv 2^>nul') do (
    if not "%%A"=="0.0.0.0" if not "%%A"=="" set WEBVIEW2_INSTALLED=1
)

if %WEBVIEW2_INSTALLED%==1 (
    REM echo MicrosoftEdgeWebView2Runtime already installed. Skipping WebView2 install.
) else (
    echo Downloading...
    if not exist "%TEMP_DIR%\MicrosoftEdgeWebView2RuntimeInstallerX64.exe" (
        powershell -Command "Invoke-WebRequest -Uri %WEBVIEW2_URL% -OutFile '%TEMP_DIR%\MicrosoftEdgeWebView2RuntimeInstallerX64.exe'"
    )

    echo installing....
    start /wait "" "%TEMP_DIR%\MicrosoftEdgeWebView2RuntimeInstallerX64.exe" /silent /install
)

echo All dependencies installed.
endlocal

