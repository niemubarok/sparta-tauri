@echo off
title Parking System Launcher

echo === Parking System Development Launcher ===
echo.

echo Starting components...

echo Starting Server...
start "Parking Server" cmd /k "python server/websocket_server.py"
timeout /t 3 /nobreak > nul

echo Starting Entry Gate...
start "Entry Gate" cmd /k "python entry-gate/entry_gate.py"

echo Starting Exit Gate...
start "Exit Gate" cmd /k "python exit-gate/exit_gate_gui.py"

echo Starting Admin Interface...
start "Admin Interface" cmd /k "python admin/app.py"

echo.
echo === All Components Started ===
echo.
echo Admin interface will be available at: http://localhost:5000
echo.
echo Each component is running in its own window.
echo Close the windows to stop individual components.
echo.
pause
