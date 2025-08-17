#!/bin/bash
# PIC32MZ Project Builder Shell Launcher
# Launches the GUI application on Unix systems

echo "======================================"
echo " PIC32MZ Project Builder v1.0"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.7+ from your package manager or https://python.org"
    read -p "Press Enter to exit..."
    exit 1
fi

# Determine Python command
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Found Python: $($PYTHON_CMD --version)"

# Check if tkinter is available
echo "Checking Python modules..."
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo "ERROR: tkinter module not found"
    echo "Please install python3-tk package:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  CentOS/RHEL: sudo yum install tkinter"
    echo "  macOS: tkinter should be included with Python"
    read -p "Press Enter to exit..."
    exit 1
fi

# Make script executable
chmod +x "$0" 2>/dev/null

# Launch the GUI
echo "Starting GUI application..."
$PYTHON_CMD pic32_project_builder.py

echo ""
read -p "Press Enter to exit..."
