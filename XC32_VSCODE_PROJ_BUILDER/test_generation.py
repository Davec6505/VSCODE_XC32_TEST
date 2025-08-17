#!/usr/bin/env python3
"""
Test script to debug PIC32 project generation issues
"""

import os
import sys
import traceback

# Add the current directory to Python path
sys.path.insert(0, '.')

try:
    # Import the main application
    from pic32_project_builder import PIC32ProjectBuilderGUI
    import tkinter as tk

    print("✅ Import successful")

    # Create a test instance
    root = tk.Tk()
    app = PIC32ProjectBuilderGUI(root)

    print("✅ GUI initialization successful")

    # Test project generation with minimal config
    test_project_name = "TestProject"
    test_output_dir = "."
    test_device = "32MZ1024EFH064"

    # Set up test configuration
    app.config['project_name'].set(test_project_name)
    app.config['output_dir'].set(test_output_dir)
    app.config['device'].set(test_device)

    print("✅ Configuration set")

    # Try to create project structure
    project_path = os.path.join(test_output_dir, test_project_name)

    print(f"🔧 Attempting to create project at: {project_path}")

    # Test the project structure creation
    app.create_project_structure(
        project_path, test_project_name, test_device, True)

    print("✅ Project structure created successfully")

    # Test peripheral files generation
    app.generate_peripheral_files(project_path, test_project_name)

    print("✅ Peripheral files generated successfully")

    print("🎉 All tests passed! Project generation should work.")

    # Clean up
    root.destroy()

except Exception as e:
    print(f"❌ Error occurred: {str(e)}")
    print("📋 Full traceback:")
    traceback.print_exc()
