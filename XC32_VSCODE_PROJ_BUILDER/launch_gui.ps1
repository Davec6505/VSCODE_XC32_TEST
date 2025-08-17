# PIC32MZ Project Builder PowerShell Launcher
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " PIC32MZ Project Builder v1.0" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required modules are available (tkinter is built-in)
Write-Host "Checking Python modules..." -ForegroundColor Yellow

# Launch the GUI
Write-Host "Starting GUI application..." -ForegroundColor Green
try {
    python pic32_project_builder.py
} catch {
    Write-Host "ERROR: Failed to launch GUI application" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Read-Host "Press Enter to exit"
