#!/usr/bin/env python3
"""
Test the enhanced project generation with JSON config file
"""

import os
import sys
import json

# Add the current directory to Python path
sys.path.insert(0, '.')

try:
    from pic32_project_builder import PIC32ProjectBuilderGUI
    import tkinter as tk

    print("Testing enhanced project generation...")

    # Create a test instance
    root = tk.Tk()
    app = PIC32ProjectBuilderGUI(root)

    # Set up test configuration
    test_project_name = "TestConfigProject"
    app.config['project_name'].set(test_project_name)
    app.config['output_dir'].set(".")
    app.config['device'].set("32MZ1024EFH064")

    # Set up some UART configuration
    app.uart_config['uart_module'].set('UART3')
    app.uart_config['baud_rate'].set('230400')
    app.uart_config['data_bits'].set('9')

    # Set up some clock configuration
    app.clock_config['input_freq'].set('12.0')
    app.clock_config['pll_mult'].set('15')

    print(f"🔧 Creating project with enhanced config...")

    # Create project
    project_path = os.path.join(".", test_project_name)
    app.create_project_structure(
        project_path, test_project_name, "32MZ1024EFH064", True)
    app.generate_peripheral_files(project_path, test_project_name)
    app.create_project_config_file(project_path, test_project_name)

    # Check if config file was created
    config_file = os.path.join(
        project_path, f"{test_project_name}_config.json")

    if os.path.exists(config_file):
        print(f"✅ Configuration file created: {test_project_name}_config.json")

        # Load and display config content
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = json.load(f)

        print(f"📄 Project info: {config_content['project_info']['name']}")
        print(f"📄 Device: {config_content['project_info']['device']}")
        print(
            f"📄 UART Module: {config_content['uart_configuration']['uart_module']}")
        print(
            f"📄 UART Baud: {config_content['uart_configuration']['baud_rate']}")
        print(
            f"📄 Clock Input: {config_content['clock_configuration']['input_freq']} MHz")
        print(
            f"📄 PLL Mult: {config_content['clock_configuration']['pll_mult']}")

        print("🎉 Enhanced project generation successful!")
    else:
        print("❌ Configuration file was not created!")

    # Clean up
    root.destroy()

except Exception as e:
    print(f"❌ Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()
