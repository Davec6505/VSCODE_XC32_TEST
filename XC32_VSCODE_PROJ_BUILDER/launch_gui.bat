@echo off
REM PIC32MZ Project Builder Launcher
REM Launches the GUI application

echo ======================================
echo  PIC32MZ Project Builder v1.0
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Launch the GUI
echo Starting GUI application...
python pic32_project_builder.py

pause
