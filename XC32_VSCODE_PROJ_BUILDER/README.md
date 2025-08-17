# PIC32MZ Project Builder - GUI Application

A modern, user-friendly GUI application for creating PIC32MZ embedded projects with MCC peripheral library integration.

## Features

### 🎯 **Core Functionality**
- **Visual Project Configuration**: Easy-to-use GUI interface for project setup
- **Device Selection**: Support for multiple PIC32MZ devices (EFH064, EFH100, EFG064, etc.)
- **MikroC Startup Support**: Optional assembly startup files for MikroC compatibility
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🔧 **Peripheral Library Integration**
- **UART**: Serial communication with configurable baud rates
- **Timer**: TMR1 with interrupt support and callbacks
- **GPIO**: LED and button control with pin definitions
- **Clock System**: System clock configuration and frequency management
- **DMA**: Direct Memory Access (planned)
- **SPI**: Serial Peripheral Interface (planned)
- **I2C**: Inter-Integrated Circuit (planned)

### 📁 **Project Generation**
- **Complete Project Structure**: Generates all necessary files and directories
- **Build System**: Integrated Makefile system with XC32 compiler support
- **Cross-Platform Paths**: Automatic detection of Windows/Unix paths
- **Device Family Pack (DFP) Integration**: Uses MPLAB X DFP files

### 💾 **Template System**
- **Save/Load Templates**: Store common project configurations
- **Pre-built Templates**: Includes Basic, Full-Featured, and Minimal templates
- **JSON Format**: Easy to edit and share templates

## Requirements

- **Python 3.7+** with tkinter (usually built-in)
- **XC32 Compiler v4.60+** installed at standard locations
- **MPLAB X IDE v6.25+** (for Device Family Pack files)

## Installation

1. **Clone or download** this repository
2. **Ensure Python is installed** and in your PATH
3. **Verify XC32 compiler** is installed in standard locations:
   - Windows: `C:\Program Files\Microchip\xc32\`
   - Unix: `/opt/microchip/xc32/`

## Usage

### Quick Start
1. **Launch the application**:
   - Windows: Double-click `launch_gui.bat` or run `launch_gui.ps1`
   - Unix/Mac: Run `./launch_gui.sh` or `python3 pic32_project_builder.py`

2. **Configure your project**:
   - Enter project name
   - Select PIC32MZ device
   - Choose output directory
   - Enable desired peripherals

3. **Generate project**:
   - Click "Generate Project"
   - Wait for completion
   - Open the created project directory

### Advanced Usage

#### Template Management
- **Save Template**: Save current configuration for reuse
- **Load Template**: Load a previously saved configuration
- **Pre-built Templates**: Use included templates for quick setup

#### Peripheral Configuration
- **UART**: Enable for serial communication (default: 115200 baud)
- **Timer1**: Enable for periodic interrupts (default: 1ms)
- **GPIO**: Enable for LED/button control
- **Clock**: Enable for system clock management
- **Advanced Peripherals**: DMA, SPI, I2C (coming soon)

## Generated Project Structure

```
MyProject/
├── srcs/                   # Source files
│   ├── main.c              # Main application
│   ├── initialization.c    # System initialization
│   ├── interrupts.c        # Interrupt handlers
│   ├── exceptions.c        # Exception handlers
│   ├── peripheral/         # Peripheral library sources
│   │   ├── uart/           # UART implementation
│   │   ├── tmr1/           # Timer1 implementation
│   │   ├── gpio/           # GPIO implementation
│   │   └── clk/            # Clock system
│   └── startup/            # Startup files (if MikroC enabled)
│       └── startup.S       # Assembly startup
├── incs/                   # Header files
│   ├── definitions.h       # System definitions
│   ├── device.h            # Device-specific headers
│   └── peripheral/         # Peripheral library headers
├── objs/                   # Object files (build output)
├── bins/                   # Binary output
├── other/                  # Map files and other outputs
├── docs/                   # Documentation
├── Makefile                # Root build file
├── README.md               # Project documentation
└── .gitignore              # Git ignore file
```

## Build System

The generated projects use a **GNU Make**-based build system with:

- **Cross-platform support**: Automatic detection of Windows/Unix paths
- **XC32 integration**: Uses installed XC32 compiler and DFP files
- **Dependency tracking**: Automatic header dependency generation
- **Assembly support**: Handles both C and assembly source files

### Build Commands
```bash
# Create build directories
make build_dir

# Build the project
make

# Clean build outputs
make clean
```

## Hardware Support

### PIC32MZ Clicker Pinout
- **LED1**: RB8
- **LED2**: RB9
- **Button1**: RA6
- **Button2**: RA7
- **UART2 TX**: RF5
- **UART2 RX**: RF4

### Supported Devices
- PIC32MZ1024EFH064
- PIC32MZ2048EFH064
- PIC32MZ1024EFH100
- PIC32MZ2048EFH100
- PIC32MZ1024EFG064
- PIC32MZ2048EFG064

## Output Log

The GUI includes a comprehensive output log that shows:
- Project generation progress
- File creation status
- Error messages and warnings
- Template loading/saving status

## Error Handling

The application includes robust error handling for:
- Missing Python dependencies
- Invalid project configurations
- File system permission issues
- Missing compiler installations

## Troubleshooting

### Common Issues

**Python not found**
- Install Python 3.7+ from python.org
- Ensure Python is in your system PATH

**XC32 compiler not found**
- Install XC32 compiler from Microchip
- Verify installation in standard locations

**tkinter not available (Linux)**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

**Permission errors**
- Ensure write permissions to output directory
- Run as administrator if necessary

## Integration with Existing Workflow

This GUI application is designed to work alongside your existing project generators:
- **Maintains compatibility** with existing `generate_project.py`, `generate_project.sh`, and `generate_project.bat`
- **Uses same project structure** as command-line generators
- **Shares templates** and configuration format
- **Generates identical output** to command-line tools

## Contributing

The application is designed to be easily extensible:
- Add new peripheral support in the `generate_*_files()` methods
- Add new devices to the device combo box
- Create additional templates for common configurations
- Enhance the GUI with additional features

## Version History

- **v1.0**: Initial release with core functionality
  - Visual project configuration
  - UART, Timer, GPIO, Clock support
  - Template system
  - Cross-platform support

## License

This project is part of the PIC32MZ development toolkit and follows the same licensing as the parent project.

## Support

For issues and questions:
1. Check this README for troubleshooting
2. Review the output log for error messages
3. Verify XC32 and MPLAB X installation
4. Check file permissions and paths

---
**PIC32MZ Project Builder v1.0** - Making embedded development easier with visual project generation.
