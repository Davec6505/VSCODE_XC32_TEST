#!/usr/bin/env python3
"""
Test script to verify Microchip plib directory discovery
"""

import os
import glob


def find_microchip_plib_directory():
    """Find Microchip peripheral library installation directory"""
    # Common Microchip installation paths
    possible_paths = [
        r"C:\Program Files\Microchip\MPLABX",
        r"C:\Program Files (x86)\Microchip\MPLABX",
        r"C:\Microchip\MPLABX",
        r"C:\Program Files\Microchip\xc32",
        r"C:\Program Files (x86)\Microchip\xc32",
        r"C:\Program Files\Microchip\MCC",
        r"C:\Program Files (x86)\Microchip\MCC"
    ]

    # Look for plib files in various locations
    plib_search_patterns = [
        r"packs\Microchip\PIC32MZ-*\plib",
        r"mcc\lib\plib\pic32mz",
        r"v*\packs\Microchip\PIC32MZ-*\plib",
        r"resources\plib\pic32mz",
        r"lib\pic32mz\plib"
    ]

    print("Searching for Microchip plib installation...")

    for base_path in possible_paths:
        print(f"\nChecking base path: {base_path}")
        if os.path.exists(base_path):
            print(f"  ✓ Base path exists")
            for pattern in plib_search_patterns:
                search_path = os.path.join(
                    base_path, pattern.replace('*', '*'))
                print(f"    Searching: {search_path}")
                matches = glob.glob(search_path)
                for match in matches:
                    if os.path.isdir(match):
                        print(f"      → Found directory: {match}")
                        # List contents
                        try:
                            contents = os.listdir(match)[:10]  # First 10 items
                            print(f"        Contents sample: {contents}")
                            return match
                        except:
                            print(f"        Could not list contents")
        else:
            print(f"  ✗ Base path does not exist")

    print("\n❌ No Microchip plib directory found!")
    return None


if __name__ == "__main__":
    result = find_microchip_plib_directory()
    if result:
        print(f"\n✅ Found plib directory: {result}")
    else:
        print("\n❌ Plib directory not found")
