@echo off
echo ====================================
echo Entry Manual Gate - Starting...
echo ====================================
echo.
echo Device: Entry Manual Gate
echo Mode: Manual (dengan operator)
echo Port: 8001
echo.
echo Press Ctrl+C to stop the system
echo.

REM Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Virtual environment not found, using system Python
)

REM Install requirements if needed
if not exist requirements_installed.flag (
    echo Installing requirements...
    pip install -r requirements.txt
    echo. > requirements_installed.flag
)

REM Run the application
python main.py

pause
