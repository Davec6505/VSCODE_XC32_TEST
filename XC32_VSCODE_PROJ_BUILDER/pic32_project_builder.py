#!/usr/bin/env python3
"""
PIC32MZ Project Builder - GUI Application
Creates embedded projects with MCC peripheral library integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import subprocess
import threading
from pathlib import Path
import json
import shutil
import glob
import datetime


class ClockConfigDialog:
    """Clock Configuration Dialog - Similar to MCC Standalone"""

    def __init__(self, parent, clock_config, update_callback):
        self.parent = parent
        self.clock_config = clock_config
        self.update_callback = update_callback

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("PIC32MZ Clock Configuration")
        self.dialog.geometry("700x700")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()  # Make modal

        # Center the dialog
        self.center_dialog()

        self.setup_clock_ui()

        # Bind trace to input fields for real-time calculation
        self.setup_calculations()

        # Try to load saved configuration
        self.load_config_from_file()

    def center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - \
            (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - \
            (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def setup_clock_ui(self):
        """Setup the clock configuration UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="PIC32MZ Clock Configuration",
                                font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Primary Oscillator Section
        self.setup_primary_osc_section(main_frame, row=1)

        # PLL Configuration Section
        self.setup_pll_section(main_frame, row=2)

        # System Clock Section
        self.setup_system_clock_section(main_frame, row=3)

        # Peripheral Clock Section
        self.setup_peripheral_clock_section(main_frame, row=4)

        # PBCLK Configuration Section
        self.setup_pbclk_section(main_frame, row=5)

        # Clock Tree Visualization
        self.setup_clock_tree(main_frame, row=6)

        # Buttons
        self.setup_dialog_buttons(main_frame, row=7)

    def setup_primary_osc_section(self, parent, row):
        """Setup primary oscillator configuration"""
        osc_frame = ttk.LabelFrame(
            parent, text="Primary Oscillator Configuration", padding="10")
        osc_frame.grid(row=row, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        osc_frame.columnconfigure(1, weight=1)

        # Oscillator type
        ttk.Label(osc_frame, text="Oscillator Type:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        osc_combo = ttk.Combobox(osc_frame, textvariable=self.clock_config['primary_osc'],
                                 width=20, state="readonly")
        osc_combo['values'] = ('HS', 'XT', 'EC')
        osc_combo.grid(row=0, column=1, sticky=(tk.W), padx=(10, 0), pady=2)

        # Input frequency
        ttk.Label(osc_frame, text="Input Frequency (MHz):").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        freq_entry = ttk.Entry(
            osc_frame, textvariable=self.clock_config['input_freq'], width=15)
        freq_entry.grid(row=1, column=1, sticky=(tk.W), padx=(10, 0), pady=2)

        # Description
        desc_text = {
            'HS': 'High Speed Crystal/Ceramic Resonator (4-40 MHz)',
            'XT': 'Crystal/Ceramic Resonator (100 kHz - 4 MHz)',
            'EC': 'External Clock (DC - 40 MHz)'
        }
        self.osc_desc_label = ttk.Label(
            osc_frame, text=desc_text['HS'], foreground='blue')
        self.osc_desc_label.grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Update description when oscillator changes
        def update_osc_desc(*args):
            osc_type = self.clock_config['primary_osc'].get()
            self.osc_desc_label.config(text=desc_text.get(osc_type, ''))
        self.clock_config['primary_osc'].trace('w', update_osc_desc)

    def setup_pll_section(self, parent, row):
        """Setup PLL configuration"""
        pll_frame = ttk.LabelFrame(
            parent, text="Phase Locked Loop (PLL) Configuration", padding="10")
        pll_frame.grid(row=row, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        pll_frame.columnconfigure(1, weight=1)

        # PLL Enable
        ttk.Checkbutton(pll_frame, text="Enable PLL",
                        variable=self.clock_config['pll_enabled']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)

        # PLL Input Divider
        ttk.Label(pll_frame, text="Input Divider (PLLINDIV):").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        pll_indiv_combo = ttk.Combobox(pll_frame, textvariable=self.clock_config['pll_input_div'],
                                       width=10, state="readonly")
        pll_indiv_combo['values'] = ('1', '2', '3', '4', '5', '6', '7', '8')
        pll_indiv_combo.grid(row=1, column=1, sticky=(
            tk.W), padx=(10, 0), pady=2)

        # PLL Multiplier
        ttk.Label(pll_frame, text="Multiplier (PLLMULT):").grid(
            row=2, column=0, sticky=tk.W, pady=2)
        pll_mult_combo = ttk.Combobox(pll_frame, textvariable=self.clock_config['pll_mult'],
                                      width=10, state="readonly")
        # PLL multiplier range for PIC32MZ (typically 15-128)
        pll_mult_combo['values'] = tuple(str(i) for i in range(15, 129))
        pll_mult_combo.grid(row=2, column=1, sticky=(tk.W),
                            padx=(10, 0), pady=2)

        # PLL Output Divider
        ttk.Label(pll_frame, text="Output Divider (PLLODIV):").grid(
            row=3, column=0, sticky=tk.W, pady=2)
        pll_odiv_combo = ttk.Combobox(pll_frame, textvariable=self.clock_config['pll_output_div'],
                                      width=10, state="readonly")
        pll_odiv_combo['values'] = ('1', '2', '4', '8', '16', '32')
        pll_odiv_combo.grid(row=3, column=1, sticky=(tk.W),
                            padx=(10, 0), pady=2)

        # VCO Frequency display
        self.vco_freq_label = ttk.Label(
            pll_frame, text="VCO Frequency: 0.0 MHz", foreground='green')
        self.vco_freq_label.grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)

    def setup_system_clock_section(self, parent, row):
        """Setup system clock configuration"""
        sys_frame = ttk.LabelFrame(parent, text="System Clock", padding="10")
        sys_frame.grid(row=row, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        sys_frame.columnconfigure(1, weight=1)

        # System frequency display
        self.sys_freq_label = ttk.Label(sys_frame, text="System Frequency: 0.0 MHz",
                                        font=('Arial', 10, 'bold'), foreground='red')
        self.sys_freq_label.grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Maximum frequency warning
        self.freq_warning_label = ttk.Label(
            sys_frame, text="", foreground='red')
        self.freq_warning_label.grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=2)

    def setup_peripheral_clock_section(self, parent, row):
        """Setup peripheral clock configuration"""
        periph_frame = ttk.LabelFrame(
            parent, text="Peripheral Clock", padding="10")
        periph_frame.grid(row=row, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=5)
        periph_frame.columnconfigure(1, weight=1)

        # Peripheral frequency (typically same as system for PIC32MZ)
        self.periph_freq_label = ttk.Label(periph_frame, text="Peripheral Frequency: 0.0 MHz",
                                           font=('Arial', 10, 'bold'), foreground='blue')
        self.periph_freq_label.grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=2)

    def setup_pbclk_section(self, parent, row):
        """Setup peripheral bus clock (PBCLK) configuration"""
        pbclk_frame = ttk.LabelFrame(
            parent, text="Peripheral Bus Clock Configuration (PBCLK)", padding="10")
        pbclk_frame.grid(row=row, column=0, columnspan=3,
                         sticky=(tk.W, tk.E), pady=5)

        # Add explanation label
        info_label = ttk.Label(pbclk_frame,
                               text="PIC32MZ PBCLK Assignment: PBCLK1=CPU/System, PBCLK2=UART/SPI/I2C, PBCLK3=Timers/PWM, PBCLK4=Ports, PBCLK5=Flash/Crypto, PBCLK6=USB/CAN/Ethernet, PBCLK7=Debug",
                               foreground='blue', font=('Arial', 8))
        info_label.pack(anchor=tk.W, pady=(0, 5))

        # Create a scrollable frame for PBCLK options
        canvas = tk.Canvas(pbclk_frame, height=120)
        scrollbar = ttk.Scrollbar(
            pbclk_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # PBCLK configurations
        pbclk_configs = [
            ("PBCLK1", "CPU/System Bus", "pbclk1"),
            ("PBCLK2", "UART/SPI/I2C Peripherals", "pbclk2"),
            ("PBCLK3", "Timer/PWM/Input Capture/Output Compare", "pbclk3"),
            ("PBCLK4", "Ports/Change Notification", "pbclk4"),
            ("PBCLK5", "Flash Controller/Crypto", "pbclk5"),
            ("PBCLK6", "USB/CAN/Ethernet", "pbclk6"),
            ("PBCLK7", "CPU Trace/Debug", "pbclk7"),
        ]

        for i, (name, desc, var_prefix) in enumerate(pbclk_configs):
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, pady=2)

            # Enable checkbox
            ttk.Checkbutton(row_frame, text=f"{name}:",
                            variable=self.clock_config[f'{var_prefix}_enabled']).pack(side=tk.LEFT)

            # Description
            ttk.Label(row_frame, text=desc, foreground='gray').pack(
                side=tk.LEFT, padx=(5, 10))

            # Divider selection
            ttk.Label(row_frame, text="Div:").pack(side=tk.LEFT, padx=(10, 2))
            div_combo = ttk.Combobox(row_frame, textvariable=self.clock_config[f'{var_prefix}_div'],
                                     width=8, state="readonly")
            # PIC32MZ PBCLK dividers: 0=÷1, 1=÷2, 2=÷3, ..., 127=÷128
            # Show format: "0 = ÷1", "1 = ÷2", etc.
            div_values = [f"{i} = ÷{i+1}" for i in range(128)]
            div_combo['values'] = tuple(div_values)
            div_combo.pack(side=tk.LEFT, padx=(2, 10))

            # Frequency display
            freq_label = ttk.Label(
                row_frame, text="0.0 MHz", foreground='blue', width=12)
            freq_label.pack(side=tk.LEFT)

            # Store reference for updates
            setattr(self, f'{var_prefix}_freq_label', freq_label)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_clock_tree(self, parent, row):
        """Setup clock tree visualization"""
        tree_frame = ttk.LabelFrame(
            parent, text="Clock Tree Summary", padding="10")
        tree_frame.grid(row=row, column=0, columnspan=3,
                        sticky=(tk.W, tk.E), pady=5)

        # Create a text widget for clock tree
        tree_text = tk.Text(tree_frame, height=6, width=60, state='disabled')
        tree_text.pack(fill=tk.BOTH, expand=True)

        self.clock_tree_text = tree_text

    def setup_dialog_buttons(self, parent, row):
        """Setup dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Apply & Save",
                   command=self.apply_and_save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh",
                   command=self.refresh_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Default",
                   command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                   command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def setup_calculations(self):
        """Setup real-time clock calculations"""
        # Trace all relevant variables
        trace_vars = ['input_freq', 'pll_input_div',
                      'pll_mult', 'pll_output_div', 'pll_enabled']

        # Add PBCLK variables
        for i in range(1, 8):
            trace_vars.extend([f'pbclk{i}_enabled', f'pbclk{i}_div'])

        for var in trace_vars:
            if var in self.clock_config:
                self.clock_config[var].trace('w', self.calculate_frequencies)

        # Initial calculation
        self.calculate_frequencies()

    def calculate_frequencies(self, *args):
        """Calculate system and peripheral frequencies"""
        try:
            input_freq = float(self.clock_config['input_freq'].get())
            pll_enabled = self.clock_config['pll_enabled'].get()

            if pll_enabled:
                # PLL calculations
                pll_indiv = int(self.clock_config['pll_input_div'].get())
                pll_mult = int(self.clock_config['pll_mult'].get())
                pll_odiv = int(self.clock_config['pll_output_div'].get())

                # VCO frequency = (Input Freq / Input Div) * Multiplier
                vco_freq = (input_freq / pll_indiv) * pll_mult

                # System frequency = VCO Freq / Output Div
                system_freq = vco_freq / pll_odiv

                # Update VCO display
                self.vco_freq_label.config(
                    text=f"VCO Frequency: {vco_freq:.1f} MHz")

                # Check VCO limits (typically 350-700 MHz for PIC32MZ)
                if vco_freq < 350 or vco_freq > 700:
                    self.vco_freq_label.config(foreground='red')
                else:
                    self.vco_freq_label.config(foreground='green')

            else:
                # No PLL, system frequency = input frequency
                system_freq = input_freq
                self.vco_freq_label.config(
                    text="VCO Frequency: N/A (PLL Disabled)")

            # Update system frequency
            self.clock_config['system_freq'].set(f"{system_freq:.1f}")
            self.sys_freq_label.config(
                text=f"System Frequency: {system_freq:.1f} MHz")

            # Check system frequency limits (max 200 MHz for PIC32MZ)
            if system_freq > 200:
                self.sys_freq_label.config(foreground='red')
                self.freq_warning_label.config(
                    text="⚠️ Warning: Frequency exceeds maximum (200 MHz)")
            elif system_freq > 180:
                self.sys_freq_label.config(foreground='orange')
                self.freq_warning_label.config(
                    text="⚠️ Caution: High frequency operation")
            else:
                self.sys_freq_label.config(foreground='green')
                self.freq_warning_label.config(text="")

            # Peripheral frequency (same as system for PIC32MZ)
            peripheral_freq = system_freq
            self.clock_config['peripheral_freq'].set(f"{peripheral_freq:.1f}")
            self.periph_freq_label.config(
                text=f"Peripheral Frequency: {peripheral_freq:.1f} MHz")

            # Calculate PBCLK frequencies
            self.calculate_pbclk_frequencies(system_freq)

            # Update clock tree
            self.update_clock_tree(
                input_freq, system_freq, peripheral_freq, pll_enabled)

        except (ValueError, ZeroDivisionError):
            # Handle invalid input
            self.sys_freq_label.config(
                text="System Frequency: Invalid", foreground='red')
            self.periph_freq_label.config(
                text="Peripheral Frequency: Invalid", foreground='red')

    def calculate_pbclk_frequencies(self, system_freq):
        """Calculate peripheral bus clock frequencies"""
        try:
            pbclk_configs = ["pbclk1", "pbclk2", "pbclk3",
                             "pbclk4", "pbclk5", "pbclk6", "pbclk7"]

            for pbclk in pbclk_configs:
                enabled = self.clock_config[f'{pbclk}_enabled'].get()
                if enabled:
                    try:
                        # Parse the divider format "0 = ÷1" to extract actual divisor
                        div_str = self.clock_config[f'{pbclk}_div'].get()
                        if ' = ÷' in div_str:
                            # Extract the divisor from format "X = ÷Y"
                            divisor = int(div_str.split(' = ÷')[1])
                        else:
                            # Fallback for old format or plain number
                            divisor = int(div_str) if div_str.isdigit() else 1

                        pbclk_freq = system_freq / divisor

                        # Update frequency display
                        freq_label = getattr(self, f'{pbclk}_freq_label', None)
                        if freq_label:
                            freq_label.config(text=f"{pbclk_freq:.1f} MHz")

                            # Color code based on frequency
                            if pbclk_freq > 100:
                                freq_label.config(foreground='red')
                            elif pbclk_freq > 80:
                                freq_label.config(foreground='orange')
                            else:
                                freq_label.config(foreground='blue')
                    except (ValueError, ZeroDivisionError):
                        freq_label = getattr(self, f'{pbclk}_freq_label', None)
                        if freq_label:
                            freq_label.config(text="Invalid", foreground='red')
                else:
                    # Disabled - show as off
                    freq_label = getattr(self, f'{pbclk}_freq_label', None)
                    if freq_label:
                        freq_label.config(text="Disabled", foreground='gray')

        except Exception as e:
            # Handle any unexpected errors silently
            pass

    def update_clock_tree(self, input_freq, system_freq, peripheral_freq, pll_enabled):
        """Update the clock tree visualization"""
        # Build PBCLK information
        pbclk_info = []
        pbclk_configs = [
            ("PBCLK1", "pbclk1", "CPU/System Bus"),
            ("PBCLK2", "pbclk2", "UART/SPI/I2C"),
            ("PBCLK3", "pbclk3", "Timer/PWM/IC/OC"),
            ("PBCLK4", "pbclk4", "Ports/Change Notify"),
            ("PBCLK5", "pbclk5", "Flash/Crypto"),
            ("PBCLK6", "pbclk6", "USB/CAN/Ethernet"),
            ("PBCLK7", "pbclk7", "CPU Trace/Debug"),
        ]

        for name, var_prefix, desc in pbclk_configs:
            enabled = self.clock_config[f'{var_prefix}_enabled'].get()
            if enabled:
                try:
                    # Parse the divider format "0 = ÷1" to extract actual divisor
                    div_str = self.clock_config[f'{var_prefix}_div'].get()
                    if ' = ÷' in div_str:
                        # Extract the divisor from format "X = ÷Y"
                        divisor = int(div_str.split(' = ÷')[1])
                        # Register value for display
                        reg_val = div_str.split(' = ÷')[0]
                    else:
                        # Fallback for old format
                        divisor = int(div_str) if div_str.isdigit() else 1
                        reg_val = div_str

                    freq = system_freq / divisor
                    pbclk_info.append(
                        f"│   ├── {name}: {freq:.1f} MHz (÷{divisor}) - {desc}")
                except:
                    pbclk_info.append(
                        f"│   ├── {name}: Invalid (÷{self.clock_config[f'{var_prefix}_div'].get()}) - {desc}")
            else:
                pbclk_info.append(f"│   ├── {name}: Disabled - {desc}")

        tree_info = f"""
Clock Tree Configuration:
├── Primary Oscillator: {self.clock_config['primary_osc'].get()} ({input_freq:.1f} MHz)
├── PLL: {'Enabled' if pll_enabled else 'Disabled'}
{'│   ├── Input Divider: /' + self.clock_config['pll_input_div'].get() if pll_enabled else ''}
{'│   ├── Multiplier: x' + self.clock_config['pll_mult'].get() if pll_enabled else ''}
{'│   └── Output Divider: /' + self.clock_config['pll_output_div'].get() if pll_enabled else ''}
├── System Clock: {system_freq:.1f} MHz
├── Peripheral Bus Clocks:
{chr(10).join(pbclk_info)}
└── Base Peripheral Clock: {peripheral_freq:.1f} MHz
        """.strip()

        self.clock_tree_text.config(state='normal')
        self.clock_tree_text.delete(1.0, tk.END)
        self.clock_tree_text.insert(1.0, tree_info)
        self.clock_tree_text.config(state='disabled')

    def apply_config(self):
        """Apply the clock configuration"""
        self.update_callback()  # Update the main GUI
        messagebox.showinfo(
            "Applied", "Clock configuration applied successfully!")
        self.dialog.destroy()

    def apply_and_save_config(self):
        """Apply and save the clock configuration"""
        self.save_config_to_file()
        self.update_callback()  # Update the main GUI
        messagebox.showinfo(
            "Applied & Saved", "Clock configuration applied and saved successfully!")
        self.dialog.destroy()

    def refresh_config(self):
        """Refresh configuration from saved file"""
        if self.load_config_from_file():
            self.calculate_frequencies()
            messagebox.showinfo(
                "Refreshed", "Clock configuration refreshed from saved settings!")
        else:
            messagebox.showinfo(
                "Info", "No saved configuration found. Using current settings.")

    def save_config_to_file(self):
        """Save clock configuration to file"""
        try:
            import json
            import os

            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, 'clock_config.json')

            # Convert tkinter variables to serializable format
            config_data = {}
            for key, var in self.clock_config.items():
                if isinstance(var, tk.BooleanVar):
                    config_data[key] = var.get()
                elif isinstance(var, tk.StringVar):
                    config_data[key] = var.get()

            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            return True
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to save configuration: {str(e)}")
            return False

    def load_config_from_file(self):
        """Load clock configuration from file"""
        try:
            import json
            import os

            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, 'clock_config.json')

            if not os.path.exists(config_file):
                return False

            with open(config_file, 'r') as f:
                config_data = json.load(f)

            # Apply loaded configuration to tkinter variables
            for key, value in config_data.items():
                if key in self.clock_config:
                    self.clock_config[key].set(value)

            return True
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to load configuration: {str(e)}")
            return False

    def reset_config(self):
        """Reset to default configuration"""
        if messagebox.askyesno("Reset", "Reset all clock settings to default values?"):
            self.clock_config['primary_osc'].set('HS')
            self.clock_config['pll_enabled'].set(True)
            self.clock_config['input_freq'].set('8.0')
            self.clock_config['pll_input_div'].set('2')
            self.clock_config['pll_mult'].set('20')
            self.clock_config['pll_output_div'].set('1')

            # Reset PBCLK settings to defaults (enable essential buses)
            self.clock_config['pbclk1_enabled'].set(
                True)   # CPU/System bus - always needed
            self.clock_config['pbclk1_div'].set('0 = ÷1')
            self.clock_config['pbclk2_enabled'].set(
                True)   # UART/SPI/I2C - commonly used
            self.clock_config['pbclk2_div'].set('0 = ÷1')
            self.clock_config['pbclk3_enabled'].set(
                True)   # Timers/PWM - commonly used
            self.clock_config['pbclk3_div'].set('0 = ÷1')

            # Disable optional PBCLK by default
            for i in range(4, 8):
                self.clock_config[f'pbclk{i}_enabled'].set(False)
                self.clock_config[f'pbclk{i}_div'].set('0 = ÷1')


class PIC32ProjectBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PIC32MZ Project Builder v1.0")
        # Increased window size to accommodate GPIO section
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Project configuration
        self.config = {
            'project_name': tk.StringVar(value='MyProject'),
            'device': tk.StringVar(value='32MZ1024EFH064'),
            'output_dir': tk.StringVar(value=os.getcwd()),
            'mikroc_support': tk.BooleanVar(value=True),
            'uart_enabled': tk.BooleanVar(value=True),
            'timer_enabled': tk.BooleanVar(value=True),
            'gpio_enabled': tk.BooleanVar(value=True),
            'clock_enabled': tk.BooleanVar(value=True),
            'dma_enabled': tk.BooleanVar(value=False),
            'spi_enabled': tk.BooleanVar(value=False),
            'i2c_enabled': tk.BooleanVar(value=False),
        }

        # UART Configuration
        self.uart_config = {
            'uart_module': tk.StringVar(value='UART2'),
            'baud_rate': tk.StringVar(value='115200'),
            'data_bits': tk.StringVar(value='8'),
            'parity': tk.StringVar(value='None'),
            'stop_bits': tk.StringVar(value='1'),
            'flow_control': tk.StringVar(value='None'),
            'rx_interrupt': tk.BooleanVar(value=True),
            'tx_interrupt': tk.BooleanVar(value=False),
            'error_interrupt': tk.BooleanVar(value=True),
            'rx_buffer_size': tk.StringVar(value='128'),
            'tx_buffer_size': tk.StringVar(value='128'),
            'wake_on_start': tk.BooleanVar(value=False),
            'loopback': tk.BooleanVar(value=False),
            'auto_address': tk.BooleanVar(value=False),
            'address_mask': tk.StringVar(value='0xFF'),
            'rx_polarity': tk.StringVar(value='Normal'),
            'tx_polarity': tk.StringVar(value='Normal'),
        }

        # Timer Configuration
        self.timer_config = {
            # TMR1, TMR2, TMR3, etc.
            'timer_module': tk.StringVar(value='TMR1'),
            'timer_mode': tk.StringVar(value='16-bit'),  # 16-bit, 32-bit
            # 1:1, 1:8, 1:64, 1:256
            'prescaler': tk.StringVar(value='1:1'),
            # Frequency, Period, Count
            'period_mode': tk.StringVar(value='Frequency'),
            'frequency': tk.StringVar(value='1000'),      # Hz
            'period_ms': tk.StringVar(value='1.0'),       # milliseconds
            'period_us': tk.StringVar(value='1000'),      # microseconds
            'period_count': tk.StringVar(value='80000'),  # Timer count value
            'interrupt_enabled': tk.BooleanVar(value=True),
            'interrupt_priority': tk.StringVar(value='4'),
            'auto_start': tk.BooleanVar(value=True),
            'gate_enable': tk.BooleanVar(value=False),
            'gate_polarity': tk.StringVar(value='Active High'),
            'external_clock': tk.BooleanVar(value=False),
            'clock_source': tk.StringVar(value='PBCLK3'),
            'output_enable': tk.BooleanVar(value=False),
            'output_polarity': tk.StringVar(value='Active High'),
            'stop_in_idle': tk.BooleanVar(value=False),
        }

        # Clock configuration
        self.clock_config = {
            'primary_osc': tk.StringVar(value='HS'),  # HS, XT, EC
            'pll_enabled': tk.BooleanVar(value=True),
            'input_freq': tk.StringVar(value='8.0'),  # MHz
            'pll_input_div': tk.StringVar(value='2'),  # PLLINDIV
            'pll_mult': tk.StringVar(value='20'),      # PLLMULT
            'pll_output_div': tk.StringVar(value='1'),  # PLLODIV
            'system_freq': tk.StringVar(value='80.0'),  # Calculated
            'peripheral_freq': tk.StringVar(value='80.0'),  # PBCLK
            'usb_pll_enabled': tk.BooleanVar(value=False),
            'reference_clock_enabled': tk.BooleanVar(value=False),
            # Peripheral Bus Clock Dividers (PIC32MZ has 7 PBCLK buses)
            'pbclk1_enabled': tk.BooleanVar(value=True),   # CPU/System bus
            'pbclk1_div': tk.StringVar(value='0 = ÷1'),         # PBDIV1
            # UART/SPI/I2C peripherals
            'pbclk2_enabled': tk.BooleanVar(value=True),
            'pbclk2_div': tk.StringVar(value='0 = ÷1'),         # PBDIV2
            'pbclk3_enabled': tk.BooleanVar(value=True),   # Timer/PWM/IC/OC
            'pbclk3_div': tk.StringVar(value='0 = ÷1'),         # PBDIV3
            # Ports/Change notification
            'pbclk4_enabled': tk.BooleanVar(value=False),
            'pbclk4_div': tk.StringVar(value='0 = ÷1'),         # PBDIV4
            # Flash controller/Crypto
            'pbclk5_enabled': tk.BooleanVar(value=False),
            'pbclk5_div': tk.StringVar(value='0 = ÷1'),         # PBDIV5
            'pbclk6_enabled': tk.BooleanVar(value=False),  # USB/CAN/Ethernet
            'pbclk6_div': tk.StringVar(value='0 = ÷1'),         # PBDIV6
            'pbclk7_enabled': tk.BooleanVar(value=False),  # CPU Trace/Debug
            'pbclk7_div': tk.StringVar(value='0 = ÷1'),         # PBDIV7
        }

        # GPIO Configuration - Comprehensive pin-by-pin configuration
        # PIC32MZ has multiple ports: A, B, C, D, E, F, G, H, J, K
        self.gpio_pins = {}
        self.gpio_config = {
            'selected_pins': [],  # List of selected pins for configuration
            # individual, port, global
            'configuration_mode': tk.StringVar(value='individual'),
        }

        # Create comprehensive pin database for PIC32MZ1024EFH064
        # Format: {'port': 'A', 'pin': 0, 'name': 'RA0', 'analog': 'AN0', 'alt_functions': [...]}
        self.init_gpio_pin_database()

        # UI state variables
        # Track UART section collapse state
        self.uart_collapsed = tk.BooleanVar(value=False)
        # Track Timer section collapse state
        self.timer_collapsed = tk.BooleanVar(value=False)
        # Track GPIO section collapse state
        self.gpio_collapsed = tk.BooleanVar(value=False)

        self.setup_ui()
        self.load_templates()

    def init_gpio_pin_database(self):
        """Initialize comprehensive GPIO pin database for PIC32MZ1024EFH064"""
        # This creates a comprehensive database of all GPIO pins with their capabilities
        # Based on PIC32MZ1024EFH064 datasheet

        self.pin_database = {
            # Port A pins
            'RA0': {'port': 'A', 'pin': 0, 'analog': 'AN0', 'alt_functions': ['VREF+'], 'package_pin': '17'},
            'RA1': {'port': 'A', 'pin': 1, 'analog': 'AN1', 'alt_functions': ['VREF-'], 'package_pin': '18'},
            'RA2': {'port': 'A', 'pin': 2, 'analog': 'AN2', 'alt_functions': ['C2IN+', 'C1IN+'], 'package_pin': '58'},
            'RA3': {'port': 'A', 'pin': 3, 'analog': 'AN3', 'alt_functions': ['C2IN-', 'C1IN-'], 'package_pin': '59'},
            'RA4': {'port': 'A', 'pin': 4, 'analog': 'AN4', 'alt_functions': ['C1OUT'], 'package_pin': '60'},
            'RA5': {'port': 'A', 'pin': 5, 'analog': 'AN5', 'alt_functions': ['C2OUT'], 'package_pin': '61'},
            'RA6': {'port': 'A', 'pin': 6, 'analog': None, 'alt_functions': ['TRCLK'], 'package_pin': '91'},
            'RA7': {'port': 'A', 'pin': 7, 'analog': None, 'alt_functions': ['TRD3'], 'package_pin': '92'},
            'RA9': {'port': 'A', 'pin': 9, 'analog': None, 'alt_functions': ['VBUS'], 'package_pin': '28'},
            'RA10': {'port': 'A', 'pin': 10, 'analog': None, 'alt_functions': ['PMA1'], 'package_pin': '29'},
            'RA14': {'port': 'A', 'pin': 14, 'analog': None, 'alt_functions': ['SCK1', 'U1ATX'], 'package_pin': '66'},
            'RA15': {'port': 'A', 'pin': 15, 'analog': None, 'alt_functions': ['SS1', 'U1ARX'], 'package_pin': '67'},

            # Port B pins - commonly used for peripheral functions
            'RB0': {'port': 'B', 'pin': 0, 'analog': 'AN0', 'alt_functions': ['PGD1', 'AN0'], 'package_pin': '21'},
            'RB1': {'port': 'B', 'pin': 1, 'analog': 'AN1', 'alt_functions': ['PGC1', 'AN1'], 'package_pin': '22'},
            'RB2': {'port': 'B', 'pin': 2, 'analog': 'AN2', 'alt_functions': ['PGD2', 'C1OUT', 'AN2'], 'package_pin': '23'},
            'RB3': {'port': 'B', 'pin': 3, 'analog': 'AN3', 'alt_functions': ['PGC2', 'C2OUT', 'AN3'], 'package_pin': '24'},
            'RB4': {'port': 'B', 'pin': 4, 'analog': 'AN4', 'alt_functions': ['PGD3', 'AN4'], 'package_pin': '25'},
            'RB5': {'port': 'B', 'pin': 5, 'analog': 'AN5', 'alt_functions': ['PGC3', 'AN5'], 'package_pin': '26'},
            'RB6': {'port': 'B', 'pin': 6, 'analog': 'AN6', 'alt_functions': ['OPAMP2OUT', 'AN6'], 'package_pin': '27'},
            'RB7': {'port': 'B', 'pin': 7, 'analog': 'AN7', 'alt_functions': ['OPAMP1OUT', 'AN7'], 'package_pin': '28'},
            'RB8': {'port': 'B', 'pin': 8, 'analog': 'AN8', 'alt_functions': ['U6RX', 'AN8'], 'package_pin': '32'},
            'RB9': {'port': 'B', 'pin': 9, 'analog': 'AN9', 'alt_functions': ['U6TX', 'AN9'], 'package_pin': '33'},
            'RB10': {'port': 'B', 'pin': 10, 'analog': 'AN10', 'alt_functions': ['PGD4', 'TMS', 'AN10'], 'package_pin': '34'},
            'RB11': {'port': 'B', 'pin': 11, 'analog': 'AN11', 'alt_functions': ['PGC4', 'TDO', 'AN11'], 'package_pin': '35'},
            'RB12': {'port': 'B', 'pin': 12, 'analog': 'AN12', 'alt_functions': ['TCK', 'AN12'], 'package_pin': '36'},
            'RB13': {'port': 'B', 'pin': 13, 'analog': 'AN13', 'alt_functions': ['TDI', 'AN13'], 'package_pin': '37'},
            'RB14': {'port': 'B', 'pin': 14, 'analog': 'AN14', 'alt_functions': ['CVREF', 'AN14'], 'package_pin': '38'},
            'RB15': {'port': 'B', 'pin': 15, 'analog': 'AN15', 'alt_functions': ['PGD5', 'U4TX', 'AN15'], 'package_pin': '44'},

            # Port C pins
            'RC1': {'port': 'C', 'pin': 1, 'analog': None, 'alt_functions': ['T2CK'], 'package_pin': '6'},
            'RC2': {'port': 'C', 'pin': 2, 'analog': None, 'alt_functions': ['T3CK'], 'package_pin': '7'},
            'RC3': {'port': 'C', 'pin': 3, 'analog': None, 'alt_functions': ['T4CK'], 'package_pin': '8'},
            'RC4': {'port': 'C', 'pin': 4, 'analog': None, 'alt_functions': ['T5CK'], 'package_pin': '9'},
            'RC12': {'port': 'C', 'pin': 12, 'analog': None, 'alt_functions': ['SOSCI'], 'package_pin': '63'},
            'RC13': {'port': 'C', 'pin': 13, 'analog': None, 'alt_functions': ['SOSCO'], 'package_pin': '73'},
            'RC14': {'port': 'C', 'pin': 14, 'analog': None, 'alt_functions': ['SOSCO', 'T1CK'], 'package_pin': '74'},
            'RC15': {'port': 'C', 'pin': 15, 'analog': None, 'alt_functions': ['SOSCI'], 'package_pin': '75'},

            # Port D pins - commonly used for parallel interfaces
            'RD0': {'port': 'D', 'pin': 0, 'analog': None, 'alt_functions': ['PMD0', 'SQI0D0'], 'package_pin': '46'},
            'RD1': {'port': 'D', 'pin': 1, 'analog': None, 'alt_functions': ['PMD1', 'SQI0D1'], 'package_pin': '47'},
            'RD2': {'port': 'D', 'pin': 2, 'analog': None, 'alt_functions': ['PMD2', 'SQI0D2'], 'package_pin': '48'},
            'RD3': {'port': 'D', 'pin': 3, 'analog': None, 'alt_functions': ['PMD3', 'SQI0D3'], 'package_pin': '49'},
            'RD4': {'port': 'D', 'pin': 4, 'analog': None, 'alt_functions': ['PMD4', 'SQID4'], 'package_pin': '50'},
            'RD5': {'port': 'D', 'pin': 5, 'analog': None, 'alt_functions': ['PMD5', 'SQID5'], 'package_pin': '51'},
            'RD6': {'port': 'D', 'pin': 6, 'analog': None, 'alt_functions': ['PMD6', 'SQICS'], 'package_pin': '52'},
            'RD7': {'port': 'D', 'pin': 7, 'analog': None, 'alt_functions': ['PMD7', 'SQICK'], 'package_pin': '53'},
            'RD9': {'port': 'D', 'pin': 9, 'analog': None, 'alt_functions': ['PMD9', 'SS2'], 'package_pin': '54'},
            'RD10': {'port': 'D', 'pin': 10, 'analog': None, 'alt_functions': ['PMD10', 'SCK2'], 'package_pin': '55'},
            'RD11': {'port': 'D', 'pin': 11, 'analog': None, 'alt_functions': ['PMD11', 'SDI2'], 'package_pin': '56'},
            'RD12': {'port': 'D', 'pin': 12, 'analog': None, 'alt_functions': ['PMD12', 'IC1'], 'package_pin': '57'},
            'RD13': {'port': 'D', 'pin': 13, 'analog': None, 'alt_functions': ['PMD13', 'IC2'], 'package_pin': '12'},
            'RD14': {'port': 'D', 'pin': 14, 'analog': None, 'alt_functions': ['PMD14', 'IC3'], 'package_pin': '13'},
            'RD15': {'port': 'D', 'pin': 15, 'analog': None, 'alt_functions': ['PMD15', 'IC4'], 'package_pin': '14'},

            # Port E pins
            'RE0': {'port': 'E', 'pin': 0, 'analog': None, 'alt_functions': ['PMD0', 'RE0'], 'package_pin': '93'},
            'RE1': {'port': 'E', 'pin': 1, 'analog': None, 'alt_functions': ['PMD1', 'RE1'], 'package_pin': '94'},
            'RE2': {'port': 'E', 'pin': 2, 'analog': None, 'alt_functions': ['PMD2', 'RE2'], 'package_pin': '95'},
            'RE3': {'port': 'E', 'pin': 3, 'analog': None, 'alt_functions': ['PMD3', 'RE3'], 'package_pin': '96'},
            'RE4': {'port': 'E', 'pin': 4, 'analog': None, 'alt_functions': ['PMD4', 'RE4'], 'package_pin': '97'},
            'RE5': {'port': 'E', 'pin': 5, 'analog': None, 'alt_functions': ['PMD5', 'RE5'], 'package_pin': '98'},
            'RE6': {'port': 'E', 'pin': 6, 'analog': None, 'alt_functions': ['PMD6', 'RE6'], 'package_pin': '99'},
            'RE7': {'port': 'E', 'pin': 7, 'analog': None, 'alt_functions': ['PMD7', 'RE7'], 'package_pin': '100'},

            # Port F pins - often used for SPI, I2C
            'RF0': {'port': 'F', 'pin': 0, 'analog': None, 'alt_functions': ['C1RX', 'ETXD1'], 'package_pin': '39'},
            'RF1': {'port': 'F', 'pin': 1, 'analog': None, 'alt_functions': ['C1TX', 'ETXD0'], 'package_pin': '40'},
            'RF2': {'port': 'F', 'pin': 2, 'analog': None, 'alt_functions': ['U1RTS', 'SCL2'], 'package_pin': '77'},
            'RF3': {'port': 'F', 'pin': 3, 'analog': None, 'alt_functions': ['U1CTS', 'SDA2'], 'package_pin': '78'},
            'RF4': {'port': 'F', 'pin': 4, 'analog': None, 'alt_functions': ['U2RTS', 'SCL3'], 'package_pin': '79'},
            'RF5': {'port': 'F', 'pin': 5, 'analog': None, 'alt_functions': ['U2CTS', 'SDA3'], 'package_pin': '80'},
            'RF8': {'port': 'F', 'pin': 8, 'analog': None, 'alt_functions': ['U3RTS', 'SCL4'], 'package_pin': '81'},
            'RF12': {'port': 'F', 'pin': 12, 'analog': None, 'alt_functions': ['U5RTS', 'SCL1'], 'package_pin': '83'},
            'RF13': {'port': 'F', 'pin': 13, 'analog': None, 'alt_functions': ['U5CTS', 'SDA1'], 'package_pin': '84'},

            # Port G pins - often used for UART, timers
            'RG0': {'port': 'G', 'pin': 0, 'analog': None, 'alt_functions': ['PMD8', 'U3TX'], 'package_pin': '89'},
            'RG1': {'port': 'G', 'pin': 1, 'analog': None, 'alt_functions': ['PMD9', 'U3RX'], 'package_pin': '90'},
            'RG6': {'port': 'G', 'pin': 6, 'analog': None, 'alt_functions': ['PMD14', 'SCK3'], 'package_pin': '10'},
            'RG7': {'port': 'G', 'pin': 7, 'analog': None, 'alt_functions': ['PMD15', 'SDI3'], 'package_pin': '11'},
            'RG8': {'port': 'G', 'pin': 8, 'analog': None, 'alt_functions': ['PMD10', 'SDO3'], 'package_pin': '1'},
            'RG9': {'port': 'G', 'pin': 9, 'analog': None, 'alt_functions': ['PMD11', 'SS3'], 'package_pin': '2'},
            'RG12': {'port': 'G', 'pin': 12, 'analog': None, 'alt_functions': ['TRD1'], 'package_pin': '85'},
            'RG13': {'port': 'G', 'pin': 13, 'analog': None, 'alt_functions': ['TRD0'], 'package_pin': '86'},
            'RG14': {'port': 'G', 'pin': 14, 'analog': None, 'alt_functions': ['TRD2'], 'package_pin': '87'},
            'RG15': {'port': 'G', 'pin': 15, 'analog': None, 'alt_functions': ['TRD3'], 'package_pin': '88'},
        }

        # Initialize pin configurations - each pin gets its own configuration
        for pin_name, pin_info in self.pin_database.items():
            self.gpio_pins[pin_name] = {
                # Basic configuration
                'enabled': tk.BooleanVar(value=False),
                'direction': tk.StringVar(value='Input'),  # Input, Output
                # Low, High (for outputs)
                'initial_state': tk.StringVar(value='Low'),

                # Pin characteristics
                # Analog function
                'analog_enabled': tk.BooleanVar(value=False),
                # Open drain output
                'open_drain': tk.BooleanVar(value=False),
                # Pull-up resistor
                'pull_up': tk.BooleanVar(value=False),
                # Pull-down resistor
                'pull_down': tk.BooleanVar(value=False),
                'slew_rate': tk.StringVar(value='Standard'),   # Standard, Fast

                # Interrupt configuration
                'interrupt_enabled': tk.BooleanVar(value=False),
                # Rising, Falling, Both
                'interrupt_edge': tk.StringVar(value='Rising'),
                'change_notification': tk.BooleanVar(value=False),

                # Alternative function
                # GPIO or specific peripheral function
                'alt_function': tk.StringVar(value='GPIO'),
                # PPS mapping if applicable
                'peripheral_mapping': tk.StringVar(value='None'),

                # Advanced features
                'schmidt_trigger': tk.BooleanVar(value=False),
                # Standard, High
                'drive_strength': tk.StringVar(value='Standard'),
            }

    def setup_ui(self):
        """Setup the main UI layout"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="PIC32MZ Project Builder",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Project Settings Section
        self.setup_project_section(main_frame, row=1)

        # Peripheral Configuration Section
        self.setup_peripheral_section(main_frame, row=2)

        # Communication/Timer Configuration Section
        # This section switches between UART and Timer based on what's enabled
        self.setup_communication_timer_section(main_frame, row=3)

        # GPIO Configuration Section
        self.setup_gpio_section(main_frame, row=4)

        # Advanced Options Section
        self.setup_advanced_section(main_frame, row=5)

        # Action Buttons
        self.setup_buttons(main_frame, row=6)

        # Output/Log Section
        self.setup_output_section(main_frame, row=7)

    def setup_project_section(self, parent, row):
        """Setup project configuration section"""
        project_frame = ttk.LabelFrame(
            parent, text="Project Configuration", padding="10")
        project_frame.grid(row=row, column=0, columnspan=3,
                           sticky=(tk.W, tk.E), pady=5)
        project_frame.columnconfigure(1, weight=1)

        # Project Name
        ttk.Label(project_frame, text="Project Name:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(project_frame, textvariable=self.config['project_name'], width=30).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)

        # Device Selection
        ttk.Label(project_frame, text="PIC32MZ Device:").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        device_combo = ttk.Combobox(
            project_frame, textvariable=self.config['device'], width=27)
        device_combo['values'] = ('32MZ1024EFH064', '32MZ2048EFH064', '32MZ1024EFH100',
                                  '32MZ2048EFH100', '32MZ1024EFG064', '32MZ2048EFG064')
        device_combo.grid(row=1, column=1, sticky=(
            tk.W, tk.E), padx=(10, 0), pady=2)

        # Output Directory
        ttk.Label(project_frame, text="Output Directory:").grid(
            row=2, column=0, sticky=tk.W, pady=2)
        dir_frame = ttk.Frame(project_frame)
        dir_frame.grid(row=2, column=1, sticky=(
            tk.W, tk.E), padx=(10, 0), pady=2)
        dir_frame.columnconfigure(0, weight=1)

        ttk.Entry(dir_frame, textvariable=self.config['output_dir']).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(
            row=0, column=1)

    def setup_peripheral_section(self, parent, row):
        """Setup peripheral configuration section"""
        periph_frame = ttk.LabelFrame(
            parent, text="Peripheral Library Configuration", padding="10")
        periph_frame.grid(row=row, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=5)

        # Create two columns for peripherals
        left_frame = ttk.Frame(periph_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))

        right_frame = ttk.Frame(periph_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.N))

        # Left column peripherals
        ttk.Checkbutton(left_frame, text="UART (Serial Communication)",
                        variable=self.config['uart_enabled']).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(left_frame, text="Timer (TMR1)",
                        variable=self.config['timer_enabled']).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(left_frame, text="GPIO (General Purpose I/O)",
                        variable=self.config['gpio_enabled']).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(left_frame, text="Clock System",
                        variable=self.config['clock_enabled']).pack(anchor=tk.W, pady=2)

        # Right column peripherals
        ttk.Checkbutton(right_frame, text="DMA (Direct Memory Access)",
                        variable=self.config['dma_enabled']).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(right_frame, text="SPI (Serial Peripheral Interface)",
                        variable=self.config['spi_enabled']).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(right_frame, text="I2C (Inter-Integrated Circuit)",
                        variable=self.config['i2c_enabled']).pack(anchor=tk.W, pady=2)

    def setup_communication_timer_section(self, parent, row):
        """Setup combined communication/timer configuration section that shows either UART or Timer based on selection"""

        # Create both UART and Timer sections
        self.setup_uart_section(parent, row)
        self.setup_timer_section(parent, row)

        # Initially show/hide based on current enabled state
        self.update_communication_timer_visibility()

        # Bind to changes in peripheral selection
        self.config['uart_enabled'].trace(
            'w', self.update_communication_timer_visibility)
        self.config['timer_enabled'].trace(
            'w', self.update_communication_timer_visibility)

    def update_communication_timer_visibility(self, *args):
        """Update visibility of UART vs Timer sections based on what's enabled"""
        uart_enabled = self.config['uart_enabled'].get()
        timer_enabled = self.config['timer_enabled'].get()

        if uart_enabled:
            # Show UART section, hide Timer section
            if hasattr(self, 'uart_container'):
                self.uart_container.grid()
            if hasattr(self, 'timer_container'):
                self.timer_container.grid_remove()
        elif timer_enabled:
            # Show Timer section, hide UART section
            if hasattr(self, 'uart_container'):
                self.uart_container.grid_remove()
            if hasattr(self, 'timer_container'):
                self.timer_container.grid()
        else:
            # Hide both sections
            if hasattr(self, 'uart_container'):
                self.uart_container.grid_remove()
            if hasattr(self, 'timer_container'):
                self.timer_container.grid_remove()

    def setup_uart_section(self, parent, row):
        """Setup UART configuration section with collapsible functionality"""

        # Create main container frame
        self.uart_container = ttk.Frame(parent)
        self.uart_container.grid(row=row, column=0, columnspan=3,
                                 sticky=(tk.W, tk.E), pady=5)
        self.uart_container.columnconfigure(0, weight=1)

        # Create header frame with title and toggle button
        header_frame = ttk.Frame(self.uart_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)

        # UART Configuration label (acts like LabelFrame title)
        title_label = ttk.Label(header_frame, text="UART Configuration",
                                font=("TkDefaultFont", 9, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Toggle button
        self.uart_toggle_btn = ttk.Button(header_frame, text="▼ Hide", width=8,
                                          command=self.toggle_uart_collapse)
        self.uart_toggle_btn.grid(row=0, column=1, sticky=tk.E)

        # Create the actual content frame (replaces the old LabelFrame)
        self.uart_frame = ttk.Frame(
            self.uart_container, relief="ridge", borderwidth=1)
        self.uart_frame.grid(row=1, column=0, sticky=(
            tk.W, tk.E), padx=2, pady=2)
        self.uart_frame.columnconfigure(1, weight=1)

        # Add padding to the frame content
        content_frame = ttk.Frame(self.uart_frame)
        content_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E), padx=10, pady=10)
        content_frame.columnconfigure(1, weight=1)

        # Initially hidden - will show when UART is enabled
        self.uart_container.grid_remove()

        # UART Module Selection
        ttk.Label(content_frame, text="UART Module:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        uart_combo = ttk.Combobox(content_frame, textvariable=self.uart_config['uart_module'],
                                  width=15, state="readonly")
        uart_combo['values'] = ('UART1', 'UART2', 'UART3',
                                'UART4', 'UART5', 'UART6')
        uart_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Communication Settings Frame
        comm_frame = ttk.LabelFrame(
            content_frame, text="Communication Settings", padding="5")
        comm_frame.grid(row=1, column=0, columnspan=3,
                        sticky=(tk.W, tk.E), pady=5)
        comm_frame.columnconfigure(1, weight=1)
        comm_frame.columnconfigure(3, weight=1)

        # Baud Rate
        ttk.Label(comm_frame, text="Baud Rate:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        baud_combo = ttk.Combobox(comm_frame, textvariable=self.uart_config['baud_rate'],
                                  width=12)
        baud_combo['values'] = ('9600', '19200', '38400',
                                '57600', '115200', '230400', '460800', '921600')
        baud_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # Data Bits
        ttk.Label(comm_frame, text="Data Bits:").grid(
            row=0, column=2, sticky=tk.W, pady=2)
        data_combo = ttk.Combobox(comm_frame, textvariable=self.uart_config['data_bits'],
                                  width=8, state="readonly")
        data_combo['values'] = ('8', '9')
        data_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # Parity
        ttk.Label(comm_frame, text="Parity:").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        parity_combo = ttk.Combobox(comm_frame, textvariable=self.uart_config['parity'],
                                    width=12, state="readonly")
        parity_combo['values'] = ('None', 'Even', 'Odd')
        parity_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # Stop Bits
        ttk.Label(comm_frame, text="Stop Bits:").grid(
            row=1, column=2, sticky=tk.W, pady=2)
        stop_combo = ttk.Combobox(comm_frame, textvariable=self.uart_config['stop_bits'],
                                  width=8, state="readonly")
        stop_combo['values'] = ('1', '2')
        stop_combo.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # Flow Control
        ttk.Label(comm_frame, text="Flow Control:").grid(
            row=2, column=0, sticky=tk.W, pady=2)
        flow_combo = ttk.Combobox(comm_frame, textvariable=self.uart_config['flow_control'],
                                  width=12, state="readonly")
        flow_combo['values'] = ('None', 'RTS/CTS', 'XON/XOFF')
        flow_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # Interrupt Settings Frame
        int_frame = ttk.LabelFrame(
            content_frame, text="Interrupt Settings", padding="5")
        int_frame.grid(row=2, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)

        # Create two columns for interrupts
        int_left = ttk.Frame(int_frame)
        int_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        int_right = ttk.Frame(int_frame)
        int_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        ttk.Checkbutton(int_left, text="RX Interrupt Enable",
                        variable=self.uart_config['rx_interrupt']).pack(anchor=tk.W, pady=1)
        ttk.Checkbutton(int_left, text="TX Interrupt Enable",
                        variable=self.uart_config['tx_interrupt']).pack(anchor=tk.W, pady=1)
        ttk.Checkbutton(int_right, text="Error Interrupt Enable",
                        variable=self.uart_config['error_interrupt']).pack(anchor=tk.W, pady=1)

        # Buffer Settings Frame
        buf_frame = ttk.LabelFrame(
            content_frame, text="Buffer Settings", padding="5")
        buf_frame.grid(row=3, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        buf_frame.columnconfigure(1, weight=1)
        buf_frame.columnconfigure(3, weight=1)

        # RX Buffer Size
        ttk.Label(buf_frame, text="RX Buffer Size:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(buf_frame, textvariable=self.uart_config['rx_buffer_size'],
                  width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # TX Buffer Size
        ttk.Label(buf_frame, text="TX Buffer Size:").grid(
            row=0, column=2, sticky=tk.W, pady=2)
        ttk.Entry(buf_frame, textvariable=self.uart_config['tx_buffer_size'],
                  width=10).grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # Advanced Settings Frame
        adv_frame = ttk.LabelFrame(
            content_frame, text="Advanced Settings", padding="5")
        adv_frame.grid(row=4, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        adv_frame.columnconfigure(1, weight=1)
        adv_frame.columnconfigure(3, weight=1)

        # Advanced checkboxes
        adv_left = ttk.Frame(adv_frame)
        adv_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        adv_right = ttk.Frame(adv_frame)
        adv_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        ttk.Checkbutton(adv_left, text="Wake on Start Bit",
                        variable=self.uart_config['wake_on_start']).pack(anchor=tk.W, pady=1)
        ttk.Checkbutton(adv_left, text="Loopback Mode",
                        variable=self.uart_config['loopback']).pack(anchor=tk.W, pady=1)
        ttk.Checkbutton(adv_right, text="Auto Address Detect",
                        variable=self.uart_config['auto_address']).pack(anchor=tk.W, pady=1)

        # Address Mask (for 9-bit mode)
        ttk.Label(adv_frame, text="Address Mask (9-bit):").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(adv_frame, textvariable=self.uart_config['address_mask'],
                  width=10).grid(row=1, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # Polarity Settings
        pol_frame = ttk.LabelFrame(
            content_frame, text="Signal Polarity", padding="5")
        pol_frame.grid(row=5, column=0, columnspan=3,
                       sticky=(tk.W, tk.E), pady=5)
        pol_frame.columnconfigure(1, weight=1)
        pol_frame.columnconfigure(3, weight=1)

        # RX Polarity
        ttk.Label(pol_frame, text="RX Polarity:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        rx_pol_combo = ttk.Combobox(pol_frame, textvariable=self.uart_config['rx_polarity'],
                                    width=12, state="readonly")
        rx_pol_combo['values'] = ('Normal', 'Inverted')
        rx_pol_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)

        # TX Polarity
        ttk.Label(pol_frame, text="TX Polarity:").grid(
            row=0, column=2, sticky=tk.W, pady=2)
        tx_pol_combo = ttk.Combobox(pol_frame, textvariable=self.uart_config['tx_polarity'],
                                    width=12, state="readonly")
        tx_pol_combo['values'] = ('Normal', 'Inverted')
        tx_pol_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # Bind UART enable checkbox to show/hide section
        self.config['uart_enabled'].trace('w', self.toggle_uart_section)

    def toggle_uart_collapse(self):
        """Toggle the collapse/expand state of UART section content"""
        if self.uart_collapsed.get():
            # Currently collapsed, so expand
            self.uart_frame.grid()
            self.uart_toggle_btn.config(text="▼ Hide")
            self.uart_collapsed.set(False)
        else:
            # Currently expanded, so collapse (but preserve values)
            self.uart_frame.grid_remove()
            self.uart_toggle_btn.config(text="▶ Show")
            self.uart_collapsed.set(True)

    def toggle_uart_section(self, *args):
        """Show/hide UART configuration section based on UART enabled checkbox"""
        if self.config['uart_enabled'].get():
            self.uart_container.grid()
            # Respect the collapse state when showing
            if not self.uart_collapsed.get():
                self.uart_frame.grid()
                self.uart_toggle_btn.config(text="▼ Hide")
            else:
                self.uart_frame.grid_remove()
                self.uart_toggle_btn.config(text="▶ Show")
        else:
            self.uart_container.grid_remove()

    def setup_timer_section(self, parent, row):
        """Setup Timer configuration section with collapsible functionality"""

        # Create main container frame
        self.timer_container = ttk.Frame(parent)
        self.timer_container.grid(row=row, column=0, columnspan=3,
                                  sticky=(tk.W, tk.E), pady=5)
        self.timer_container.columnconfigure(0, weight=1)

        # Create header frame with title and toggle button
        header_frame = ttk.Frame(self.timer_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)

        # Timer Configuration label (acts like LabelFrame title)
        title_label = ttk.Label(header_frame, text="Timer Configuration",
                                font=("TkDefaultFont", 9, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Toggle button
        self.timer_toggle_btn = ttk.Button(header_frame, text="▼ Hide", width=8,
                                           command=self.toggle_timer_collapse)
        self.timer_toggle_btn.grid(row=0, column=1, sticky=tk.E)

        # Create the actual content frame (replaces the old LabelFrame)
        self.timer_frame = ttk.Frame(
            self.timer_container, relief="ridge", borderwidth=1)
        self.timer_frame.grid(row=1, column=0, sticky=(
            tk.W, tk.E), padx=2, pady=2)
        self.timer_frame.columnconfigure(1, weight=1)

        # Add padding to the frame content
        content_frame = ttk.Frame(self.timer_frame)
        content_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E), padx=10, pady=10)
        content_frame.columnconfigure(1, weight=1)

        # Initially hidden - will show when Timer is enabled
        self.timer_container.grid_remove()

        # Timer Module Selection
        ttk.Label(content_frame, text="Timer Module:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        timer_combo = ttk.Combobox(content_frame, textvariable=self.timer_config['timer_module'],
                                   width=15, state="readonly")
        timer_combo['values'] = (
            'TMR1', 'TMR2', 'TMR3', 'TMR4', 'TMR5', 'TMR6', 'TMR7', 'TMR8', 'TMR9')
        timer_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # Timer Mode Selection
        ttk.Label(content_frame, text="Timer Mode:").grid(
            row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        mode_combo = ttk.Combobox(content_frame, textvariable=self.timer_config['timer_mode'],
                                  width=15, state="readonly")
        mode_combo['values'] = ('16-bit', '32-bit (TMRx/TMRy)')
        mode_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 0), pady=2)

        # Clock Settings Frame
        clock_frame = ttk.LabelFrame(
            content_frame, text="Clock Configuration", padding="5")
        clock_frame.grid(row=1, column=0, columnspan=4,
                         sticky=(tk.W, tk.E), pady=5)
        clock_frame.columnconfigure(1, weight=1)
        clock_frame.columnconfigure(3, weight=1)

        # Prescaler
        ttk.Label(clock_frame, text="Prescaler:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        prescaler_combo = ttk.Combobox(clock_frame, textvariable=self.timer_config['prescaler'],
                                       width=12, state="readonly")
        prescaler_combo['values'] = ('1:1', '1:8', '1:64', '1:256')
        prescaler_combo.grid(row=0, column=1, sticky=tk.W,
                             padx=(5, 10), pady=2)

        # Clock Source
        ttk.Label(clock_frame, text="Clock Source:").grid(
            row=0, column=2, sticky=tk.W, pady=2)
        clock_combo = ttk.Combobox(clock_frame, textvariable=self.timer_config['clock_source'],
                                   width=12, state="readonly")
        clock_combo['values'] = ('PBCLK3', 'External', 'LPRC', 'SOSC')
        clock_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # External Clock Options
        ext_clock_frame = ttk.Frame(clock_frame)
        ext_clock_frame.grid(row=1, column=0, columnspan=4,
                             sticky=(tk.W, tk.E), pady=2)

        ttk.Checkbutton(ext_clock_frame, text="External Clock Input",
                        variable=self.timer_config['external_clock']).grid(row=0, column=0, sticky=tk.W)

        # Period/Frequency Settings Frame
        period_frame = ttk.LabelFrame(
            content_frame, text="Period Configuration", padding="5")
        period_frame.grid(row=2, column=0, columnspan=4,
                          sticky=(tk.W, tk.E), pady=5)
        period_frame.columnconfigure(1, weight=1)
        period_frame.columnconfigure(3, weight=1)

        # Period Mode Selection
        ttk.Label(period_frame, text="Configure by:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        period_mode_combo = ttk.Combobox(period_frame, textvariable=self.timer_config['period_mode'],
                                         width=12, state="readonly")
        period_mode_combo['values'] = (
            'Frequency', 'Period (ms)', 'Period (μs)', 'Count Value')
        period_mode_combo.grid(
            row=0, column=1, sticky=tk.W, padx=(5, 10), pady=2)
        period_mode_combo.bind('<<ComboboxSelected>>',
                               self.on_period_mode_change)

        # Create frames for different period input modes
        self.frequency_frame = ttk.Frame(period_frame)
        self.period_ms_frame = ttk.Frame(period_frame)
        self.period_us_frame = ttk.Frame(period_frame)
        self.count_frame = ttk.Frame(period_frame)

        # Frequency input
        ttk.Label(self.frequency_frame, text="Frequency (Hz):").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Entry(self.frequency_frame, textvariable=self.timer_config['frequency'], width=15).grid(
            row=0, column=1, padx=5)

        # Period (ms) input
        ttk.Label(self.period_ms_frame, text="Period (ms):").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Entry(self.period_ms_frame, textvariable=self.timer_config['period_ms'], width=15).grid(
            row=0, column=1, padx=5)

        # Period (μs) input
        ttk.Label(self.period_us_frame, text="Period (μs):").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Entry(self.period_us_frame, textvariable=self.timer_config['period_us'], width=15).grid(
            row=0, column=1, padx=5)

        # Count value input
        ttk.Label(self.count_frame, text="Count Value:").grid(
            row=0, column=0, sticky=tk.W)
        ttk.Entry(self.count_frame, textvariable=self.timer_config['period_count'], width=15).grid(
            row=0, column=1, padx=5)

        # Initially show frequency frame
        self.frequency_frame.grid(
            row=1, column=0, columnspan=4, sticky=tk.W, pady=2)

        # Interrupt Settings Frame
        int_frame = ttk.LabelFrame(
            content_frame, text="Interrupt Settings", padding="5")
        int_frame.grid(row=3, column=0, columnspan=4,
                       sticky=(tk.W, tk.E), pady=5)
        int_frame.columnconfigure(1, weight=1)

        # Create two columns for interrupt settings
        int_left = ttk.Frame(int_frame)
        int_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        int_right = ttk.Frame(int_frame)
        int_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        ttk.Checkbutton(int_left, text="Interrupt Enable",
                        variable=self.timer_config['interrupt_enabled']).pack(anchor=tk.W, pady=1)

        priority_frame = ttk.Frame(int_left)
        priority_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(priority_frame, text="Priority:").pack(side=tk.LEFT)
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.timer_config['interrupt_priority'],
                                      width=3, state="readonly")
        priority_combo['values'] = ('1', '2', '3', '4', '5', '6', '7')
        priority_combo.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Checkbutton(int_right, text="Auto Start Timer",
                        variable=self.timer_config['auto_start']).pack(anchor=tk.W, pady=1)

        # Advanced Settings Frame
        adv_frame = ttk.LabelFrame(
            content_frame, text="Advanced Settings", padding="5")
        adv_frame.grid(row=4, column=0, columnspan=4,
                       sticky=(tk.W, tk.E), pady=5)
        adv_frame.columnconfigure(1, weight=1)
        adv_frame.columnconfigure(3, weight=1)

        # Advanced checkboxes
        adv_left = ttk.Frame(adv_frame)
        adv_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        adv_right = ttk.Frame(adv_frame)
        adv_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        ttk.Checkbutton(adv_left, text="Gate Control Enable",
                        variable=self.timer_config['gate_enable']).pack(anchor=tk.W, pady=1)
        ttk.Checkbutton(adv_left, text="Stop in Idle Mode",
                        variable=self.timer_config['stop_in_idle']).pack(anchor=tk.W, pady=1)

        ttk.Checkbutton(adv_right, text="Output Enable",
                        variable=self.timer_config['output_enable']).pack(anchor=tk.W, pady=1)

        # Gate Polarity
        gate_frame = ttk.Frame(adv_frame)
        gate_frame.grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(gate_frame, text="Gate Polarity:").pack(side=tk.LEFT)
        gate_combo = ttk.Combobox(gate_frame, textvariable=self.timer_config['gate_polarity'],
                                  width=12, state="readonly")
        gate_combo['values'] = ('Active High', 'Active Low')
        gate_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Output Polarity
        output_frame = ttk.Frame(adv_frame)
        output_frame.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(output_frame, text="Output Polarity:").pack(side=tk.LEFT)
        output_combo = ttk.Combobox(output_frame, textvariable=self.timer_config['output_polarity'],
                                    width=12, state="readonly")
        output_combo['values'] = ('Active High', 'Active Low')
        output_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Bind Timer enable checkbox to show/hide section
        self.config['timer_enabled'].trace('w', self.toggle_timer_section)

    def on_period_mode_change(self, *args):
        """Handle changes in period configuration mode"""
        mode = self.timer_config['period_mode'].get()

        # Hide all frames first
        self.frequency_frame.grid_remove()
        self.period_ms_frame.grid_remove()
        self.period_us_frame.grid_remove()
        self.count_frame.grid_remove()

        # Show the appropriate frame
        if mode == 'Frequency':
            self.frequency_frame.grid(
                row=1, column=0, columnspan=4, sticky=tk.W, pady=2)
        elif mode == 'Period (ms)':
            self.period_ms_frame.grid(
                row=1, column=0, columnspan=4, sticky=tk.W, pady=2)
        elif mode == 'Period (μs)':
            self.period_us_frame.grid(
                row=1, column=0, columnspan=4, sticky=tk.W, pady=2)
        elif mode == 'Count Value':
            self.count_frame.grid(
                row=1, column=0, columnspan=4, sticky=tk.W, pady=2)

    def toggle_timer_collapse(self):
        """Toggle the collapse/expand state of Timer section content"""
        if self.timer_collapsed.get():
            # Currently collapsed, so expand
            self.timer_frame.grid()
            self.timer_toggle_btn.config(text="▼ Hide")
            self.timer_collapsed.set(False)
        else:
            # Currently expanded, so collapse (but preserve values)
            self.timer_frame.grid_remove()
            self.timer_toggle_btn.config(text="▶ Show")
            self.timer_collapsed.set(True)

    def toggle_timer_section(self, *args):
        """Show/hide Timer configuration section based on Timer enabled checkbox"""
        if self.config['timer_enabled'].get():
            self.timer_container.grid()
            # Respect the collapse state when showing
            if not self.timer_collapsed.get():
                self.timer_frame.grid()
                self.timer_toggle_btn.config(text="▼ Hide")
            else:
                self.timer_frame.grid_remove()
                self.timer_toggle_btn.config(text="▶ Show")
        else:
            self.timer_container.grid_remove()

    def setup_gpio_section(self, parent, row):
        """Setup comprehensive GPIO configuration section"""
        if not self.config['gpio_enabled'].get():
            return

        # Create main container frame
        self.gpio_container = ttk.Frame(parent)
        self.gpio_container.grid(row=row, column=0, columnspan=3,
                                 sticky=(tk.W, tk.E), pady=5)
        self.gpio_container.columnconfigure(0, weight=1)

        # Create header frame with title and toggle button
        header_frame = ttk.Frame(self.gpio_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(0, weight=1)

        # GPIO Configuration label
        title_label = ttk.Label(header_frame, text="GPIO Configuration",
                                font=("TkDefaultFont", 9, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Toggle button
        self.gpio_toggle_btn = ttk.Button(header_frame, text="▼ Hide", width=8,
                                          command=self.toggle_gpio_collapse)
        self.gpio_toggle_btn.grid(row=0, column=1, sticky=tk.E)

        # Create scrollable content frame
        self.gpio_canvas = tk.Canvas(
            self.gpio_container, relief="ridge", borderwidth=1, height=400)
        self.gpio_scrollbar = ttk.Scrollbar(
            self.gpio_container, orient="vertical", command=self.gpio_canvas.yview)
        self.gpio_frame = ttk.Frame(self.gpio_canvas)

        self.gpio_frame.bind(
            "<Configure>",
            lambda e: self.gpio_canvas.configure(
                scrollregion=self.gpio_canvas.bbox("all"))
        )

        self.gpio_canvas.create_window(
            (0, 0), window=self.gpio_frame, anchor="nw")
        self.gpio_canvas.configure(yscrollcommand=self.gpio_scrollbar.set)

        # Add mouse wheel scrolling support
        def _on_mousewheel(event):
            self.gpio_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self.gpio_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.gpio_frame.bind("<MouseWheel>", _on_mousewheel)

        self.gpio_canvas.grid(row=1, column=0, sticky=(
            tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        self.gpio_scrollbar.grid(row=1, column=1, sticky=(
            tk.N, tk.S), padx=(0, 2), pady=2)

        self.gpio_container.columnconfigure(0, weight=1)
        self.gpio_container.rowconfigure(1, weight=1)

        # Add padding to the frame content
        content_frame = ttk.Frame(self.gpio_frame)
        content_frame.grid(row=0, column=0, sticky=(
            tk.W, tk.E), padx=10, pady=10)
        content_frame.columnconfigure(1, weight=1)

        # Configuration Mode Selection
        mode_frame = ttk.LabelFrame(
            content_frame, text="Configuration Mode", padding="5")
        mode_frame.grid(row=0, column=0, columnspan=2,
                        sticky=(tk.W, tk.E), pady=5)

        ttk.Radiobutton(mode_frame, text="Individual Pin Configuration",
                        variable=self.gpio_config['configuration_mode'], value='individual').pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Port-based Configuration",
                        variable=self.gpio_config['configuration_mode'], value='port').pack(anchor=tk.W)

        # Pin Selection Frame - Make it more compact
        selection_frame = ttk.LabelFrame(
            content_frame, text="Pin Selection", padding="5")
        selection_frame.grid(row=1, column=0, columnspan=2,
                             sticky=(tk.W, tk.E), pady=5)
        selection_frame.columnconfigure(0, weight=1)

        # Create notebook for different ports with reduced height
        self.gpio_notebook = ttk.Notebook(selection_frame)
        self.gpio_notebook.grid(row=0, column=0, sticky=(
            tk.W, tk.E), pady=5)

        # Create tabs for each port
        self.port_frames = {}
        ports = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

        for port in ports:
            # Create frame for this port
            port_frame = ttk.Frame(self.gpio_notebook)
            self.gpio_notebook.add(port_frame, text=f"Port {port}")
            self.port_frames[port] = port_frame

            # Create scrollable frame for pins with compact layout
            self.setup_port_pin_selection(port_frame, port)

        # Pin Configuration Details Frame
        config_frame = ttk.LabelFrame(
            content_frame, text="Pin Configuration", padding="5")
        config_frame.grid(row=2, column=0, columnspan=2,
                          sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)

        # Selected Pin Info
        self.selected_pin_label = ttk.Label(config_frame, text="Select a pin to configure",
                                            font=("TkDefaultFont", 9, "italic"))
        self.selected_pin_label.grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Configuration options frame (initially hidden)
        self.pin_config_frame = ttk.Frame(config_frame)
        self.pin_config_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.pin_config_frame.columnconfigure(1, weight=1)

        self.setup_pin_configuration_options()

        # Initially hide configuration until a pin is selected
        self.pin_config_frame.grid_remove()

        # Bind GPIO enable checkbox to show/hide section
        self.config['gpio_enabled'].trace('w', self.toggle_gpio_section)

    def setup_port_pin_selection(self, parent, port):
        """Setup pin selection for a specific port"""
        # Create scrollable frame with reduced height
        canvas = tk.Canvas(parent, height=120)  # Reduced from 200 to 120
        scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # Add pins for this port in a more compact layout
        row = 0
        col = 0
        max_cols = 2  # Show pins in multiple columns to save space

        for pin_name, pin_info in self.pin_database.items():
            if pin_info['port'] == port:
                pin_frame = ttk.Frame(scrollable_frame)
                pin_frame.grid(row=row, column=col,
                               sticky=tk.W, padx=5, pady=1)
                pin_frame.columnconfigure(2, weight=1)

                # Pin checkbox
                pin_check = ttk.Checkbutton(pin_frame, text=pin_name,
                                            variable=self.gpio_pins[pin_name]['enabled'],
                                            command=lambda pn=pin_name: self.on_pin_selected(pn))
                pin_check.grid(row=0, column=0, sticky=tk.W)

                # Package pin info
                pkg_pin_label = ttk.Label(pin_frame, text=f"Pin {pin_info['package_pin']}",
                                          font=("TkDefaultFont", 8))
                pkg_pin_label.grid(row=0, column=1, padx=(5, 0), sticky=tk.W)

                # Alternative functions info (compact)
                alt_funcs = ", ".join(
                    pin_info['alt_functions'][:1]) if pin_info['alt_functions'] else ""
                if len(pin_info['alt_functions']) > 1:
                    alt_funcs += "..."

                if alt_funcs:
                    alt_label = ttk.Label(pin_frame, text=alt_funcs,
                                          font=("TkDefaultFont", 7), foreground="blue")
                    alt_label.grid(row=0, column=2, padx=(5, 0), sticky=tk.W)

                # Analog function info (compact)
                if pin_info['analog']:
                    analog_label = ttk.Label(pin_frame, text=pin_info['analog'],
                                             font=("TkDefaultFont", 7), foreground="red")
                    analog_label.grid(
                        row=0, column=3, padx=(5, 0), sticky=tk.W)

                # Move to next position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def setup_pin_configuration_options(self):
        """Setup detailed pin configuration options"""
        # Basic Configuration
        basic_frame = ttk.LabelFrame(
            self.pin_config_frame, text="Basic Configuration", padding="5")
        basic_frame.grid(row=0, column=0, columnspan=2,
                         sticky=(tk.W, tk.E), pady=5)
        basic_frame.columnconfigure(1, weight=1)

        # Direction
        ttk.Label(basic_frame, text="Direction:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.direction_combo = ttk.Combobox(
            basic_frame, width=15, state="readonly")
        self.direction_combo['values'] = ('Input', 'Output')
        self.direction_combo.grid(
            row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # Initial State (for outputs)
        ttk.Label(basic_frame, text="Initial State:").grid(
            row=0, column=2, sticky=tk.W, padx=(20, 0), pady=2)
        self.initial_state_combo = ttk.Combobox(
            basic_frame, width=10, state="readonly")
        self.initial_state_combo['values'] = ('Low', 'High')
        self.initial_state_combo.grid(
            row=0, column=3, sticky=tk.W, padx=(5, 0), pady=2)

        # Pin Characteristics
        char_frame = ttk.LabelFrame(
            self.pin_config_frame, text="Pin Characteristics", padding="5")
        char_frame.grid(row=1, column=0, columnspan=2,
                        sticky=(tk.W, tk.E), pady=5)

        # Create two columns for characteristics
        char_left = ttk.Frame(char_frame)
        char_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        char_right = ttk.Frame(char_frame)
        char_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        # Left column characteristics
        self.analog_check = ttk.Checkbutton(char_left, text="Analog Function")
        self.analog_check.pack(anchor=tk.W, pady=1)

        self.open_drain_check = ttk.Checkbutton(
            char_left, text="Open Drain Output")
        self.open_drain_check.pack(anchor=tk.W, pady=1)

        self.pull_up_check = ttk.Checkbutton(
            char_left, text="Internal Pull-up")
        self.pull_up_check.pack(anchor=tk.W, pady=1)

        self.pull_down_check = ttk.Checkbutton(
            char_left, text="Internal Pull-down")
        self.pull_down_check.pack(anchor=tk.W, pady=1)

        # Right column characteristics
        self.schmidt_check = ttk.Checkbutton(
            char_right, text="Schmitt Trigger Input")
        self.schmidt_check.pack(anchor=tk.W, pady=1)

        # Slew Rate
        slew_frame = ttk.Frame(char_right)
        slew_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(slew_frame, text="Slew Rate:").pack(side=tk.LEFT)
        self.slew_rate_combo = ttk.Combobox(
            slew_frame, width=10, state="readonly")
        self.slew_rate_combo['values'] = ('Standard', 'Fast')
        self.slew_rate_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Drive Strength
        drive_frame = ttk.Frame(char_right)
        drive_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(drive_frame, text="Drive Strength:").pack(side=tk.LEFT)
        self.drive_strength_combo = ttk.Combobox(
            drive_frame, width=10, state="readonly")
        self.drive_strength_combo['values'] = ('Standard', 'High')
        self.drive_strength_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Interrupt Configuration
        int_frame = ttk.LabelFrame(
            self.pin_config_frame, text="Interrupt Configuration", padding="5")
        int_frame.grid(row=2, column=0, columnspan=2,
                       sticky=(tk.W, tk.E), pady=5)
        int_frame.columnconfigure(1, weight=1)

        # Interrupt settings
        int_left = ttk.Frame(int_frame)
        int_left.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 20))
        int_right = ttk.Frame(int_frame)
        int_right.grid(row=0, column=1, sticky=(tk.W, tk.N))

        self.interrupt_check = ttk.Checkbutton(
            int_left, text="External Interrupt")
        self.interrupt_check.pack(anchor=tk.W, pady=1)

        self.change_notify_check = ttk.Checkbutton(
            int_left, text="Change Notification")
        self.change_notify_check.pack(anchor=tk.W, pady=1)

        # Interrupt edge
        edge_frame = ttk.Frame(int_right)
        edge_frame.pack(anchor=tk.W, pady=2)
        ttk.Label(edge_frame, text="Interrupt Edge:").pack(side=tk.LEFT)
        self.interrupt_edge_combo = ttk.Combobox(
            edge_frame, width=10, state="readonly")
        self.interrupt_edge_combo['values'] = ('Rising', 'Falling', 'Both')
        self.interrupt_edge_combo.pack(side=tk.LEFT, padx=(5, 0))

        # Alternative Function Configuration
        alt_frame = ttk.LabelFrame(
            self.pin_config_frame, text="Alternative Function", padding="5")
        alt_frame.grid(row=3, column=0, columnspan=2,
                       sticky=(tk.W, tk.E), pady=5)
        alt_frame.columnconfigure(1, weight=1)

        ttk.Label(alt_frame, text="Function:").grid(
            row=0, column=0, sticky=tk.W, pady=2)
        self.alt_function_combo = ttk.Combobox(
            alt_frame, width=20, state="readonly")
        self.alt_function_combo.grid(
            row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        # PPS Mapping (if applicable)
        ttk.Label(alt_frame, text="PPS Mapping:").grid(
            row=1, column=0, sticky=tk.W, pady=2)
        self.pps_mapping_combo = ttk.Combobox(
            alt_frame, width=20, state="readonly")
        self.pps_mapping_combo.grid(
            row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)

    def on_pin_selected(self, pin_name):
        """Handle pin selection and update configuration options"""
        if self.gpio_pins[pin_name]['enabled'].get():
            # Pin was selected, show configuration
            self.selected_pin_label.config(text=f"Configuring: {pin_name}")
            self.pin_config_frame.grid()

            # Load pin-specific configuration
            self.load_pin_configuration(pin_name)
        else:
            # Check if any pins are still selected
            any_selected = any(pin['enabled'].get()
                               for pin in self.gpio_pins.values())
            if not any_selected:
                self.selected_pin_label.config(
                    text="Select a pin to configure")
                self.pin_config_frame.grid_remove()

    def load_pin_configuration(self, pin_name):
        """Load configuration options for the selected pin"""
        pin_config = self.gpio_pins[pin_name]
        pin_info = self.pin_database[pin_name]

        # Connect the UI elements to the pin configuration
        self.direction_combo.configure(textvariable=pin_config['direction'])
        self.initial_state_combo.configure(
            textvariable=pin_config['initial_state'])
        self.slew_rate_combo.configure(textvariable=pin_config['slew_rate'])
        self.drive_strength_combo.configure(
            textvariable=pin_config['drive_strength'])
        self.interrupt_edge_combo.configure(
            textvariable=pin_config['interrupt_edge'])

        # Connect checkboxes
        self.analog_check.configure(variable=pin_config['analog_enabled'])
        self.open_drain_check.configure(variable=pin_config['open_drain'])
        self.pull_up_check.configure(variable=pin_config['pull_up'])
        self.pull_down_check.configure(variable=pin_config['pull_down'])
        self.schmidt_check.configure(variable=pin_config['schmidt_trigger'])
        self.interrupt_check.configure(
            variable=pin_config['interrupt_enabled'])
        self.change_notify_check.configure(
            variable=pin_config['change_notification'])

        # Load alternative functions
        alt_functions = ['GPIO'] + (pin_info['alt_functions'] or [])
        self.alt_function_combo['values'] = alt_functions
        self.alt_function_combo.configure(
            textvariable=pin_config['alt_function'])

        # Load PPS mappings (simplified - in real implementation would be device-specific)
        pps_options = ['None', 'U1TX', 'U1RX',
                       'U2TX', 'U2RX', 'SPI1OUT', 'SPI1IN']
        self.pps_mapping_combo['values'] = pps_options
        self.pps_mapping_combo.configure(
            textvariable=pin_config['peripheral_mapping'])

    def toggle_gpio_collapse(self):
        """Toggle the collapse/expand state of GPIO section content"""
        if self.gpio_collapsed.get():
            # Currently collapsed, so expand
            self.gpio_canvas.grid()
            self.gpio_scrollbar.grid()
            self.gpio_toggle_btn.config(text="▼ Hide")
            self.gpio_collapsed.set(False)
        else:
            # Currently expanded, so collapse
            self.gpio_canvas.grid_remove()
            self.gpio_scrollbar.grid_remove()
            self.gpio_toggle_btn.config(text="▶ Show")
            self.gpio_collapsed.set(True)

    def toggle_gpio_section(self, *args):
        """Show/hide GPIO configuration section based on GPIO enabled checkbox"""
        if self.config['gpio_enabled'].get():
            if not hasattr(self, 'gpio_container'):
                # Create the GPIO section if it doesn't exist
                self.setup_gpio_section(self.root.children['!frame'], 4)
            else:
                self.gpio_container.grid()
                # Respect the collapse state when showing
                if not self.gpio_collapsed.get():
                    self.gpio_frame.grid()
                    self.gpio_toggle_btn.config(text="▼ Hide")
                else:
                    self.gpio_frame.grid_remove()
                    self.gpio_toggle_btn.config(text="▶ Show")
        else:
            if hasattr(self, 'gpio_container'):
                self.gpio_container.grid_remove()

    def setup_advanced_section(self, parent, row):
        """Setup advanced options section"""
        advanced_frame = ttk.LabelFrame(
            parent, text="Advanced Options", padding="10")
        advanced_frame.grid(row=row, column=0, columnspan=3,
                            sticky=(tk.W, tk.E), pady=5)

        ttk.Checkbutton(advanced_frame, text="Include MikroC Startup Support",
                        variable=self.config['mikroc_support']).pack(anchor=tk.W, pady=2)

        # Clock Configuration Button
        clock_config_frame = ttk.Frame(advanced_frame)
        clock_config_frame.pack(fill=tk.X, pady=5)

        ttk.Button(clock_config_frame, text="Configure Clock System",
                   command=self.open_clock_config).pack(side=tk.LEFT)

        # Clock summary label
        self.clock_summary_label = ttk.Label(clock_config_frame,
                                             text="System: Initializing...")
        self.clock_summary_label.pack(side=tk.LEFT, padx=(10, 0))

        # Update the initial clock summary
        self.update_clock_summary()

    def setup_buttons(self, parent, row):
        """Setup action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Generate Project",
                   command=self.generate_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Template",
                   command=self.load_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Template",
                   command=self.save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log",
                   command=self.clear_log).pack(side=tk.LEFT, padx=5)

    def setup_output_section(self, parent, row):
        """Setup output/log section"""
        output_frame = ttk.LabelFrame(parent, text="Output Log", padding="10")
        output_frame.grid(row=row, column=0, columnspan=3,
                          sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            output_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add initial welcome message
        self.log("PIC32MZ Project Builder initialized")
        self.log("Ready to create embedded projects with MCC peripheral libraries")

    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)

    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.config['output_dir'].get())
        if directory:
            self.config['output_dir'].set(directory)

    def open_clock_config(self):
        """Open clock configuration dialog"""
        ClockConfigDialog(self.root, self.clock_config,
                          self.update_clock_summary)

    def update_clock_summary(self):
        """Update the clock summary display"""
        system_freq = self.clock_config['system_freq'].get()
        osc_type = self.clock_config['primary_osc'].get()
        pll_enabled = self.clock_config['pll_enabled'].get()
        input_freq = self.clock_config['input_freq'].get()

        # Build comprehensive status string
        if pll_enabled:
            pll_mult = self.clock_config['pll_mult'].get()
            status_text = f"System: {system_freq}MHz ({osc_type} {input_freq}MHz → PLL×{pll_mult} → {system_freq}MHz)"
        else:
            status_text = f"System: {system_freq}MHz ({osc_type} {input_freq}MHz, No PLL)"

        # Add PBCLK2 status (UART/SPI/I2C) if enabled
        if self.clock_config['pbclk2_enabled'].get():
            pbclk2_div_str = self.clock_config['pbclk2_div'].get()
            if ' = ÷' in pbclk2_div_str:
                divisor = int(pbclk2_div_str.split(' = ÷')[1])
                pbclk2_freq = float(system_freq) / divisor
                status_text += f" | PBCLK2: {pbclk2_freq:.1f}MHz"

        self.clock_summary_label.config(text=status_text)

    def validate_config(self):
        """Validate project configuration"""
        if not self.config['project_name'].get().strip():
            messagebox.showerror("Error", "Project name is required!")
            return False

        if not self.config['device'].get():
            messagebox.showerror("Error", "Device selection is required!")
            return False

        if not os.path.exists(self.config['output_dir'].get()):
            messagebox.showerror("Error", "Output directory does not exist!")
            return False

        return True

    def generate_project(self):
        """Generate the project"""
        if not self.validate_config():
            return

        # Start generation in separate thread to avoid UI freeze
        threading.Thread(target=self._generate_project_thread,
                         daemon=True).start()

    def _generate_project_thread(self):
        """Generate project in separate thread"""
        try:
            self.log("Starting project generation...")

            project_name = self.config['project_name'].get()
            device = self.config['device'].get()
            output_dir = self.config['output_dir'].get()
            mikroc = self.config['mikroc_support'].get()

            # Create project directory
            project_path = os.path.join(output_dir, project_name)
            self.log(f"Creating project directory: {project_path}")

            # Generate using the project generator
            self.create_project_structure(
                project_path, project_name, device, mikroc)

            # Generate peripheral files based on configuration
            self.generate_peripheral_files(project_path, project_name)

            # Create project configuration file
            self.create_project_config_file(project_path, project_name)

            self.log(f"✅ Project '{project_name}' generated successfully!")
            self.log(f"📁 Location: {project_path}")

            # Ask if user wants to open the project directory
            if messagebox.askyesno("Success", "Project generated successfully! Open project directory?"):
                self.open_project_directory(project_path)

        except Exception as e:
            self.log(f"❌ Error generating project: {str(e)}")
            messagebox.showerror(
                "Error", f"Failed to generate project: {str(e)}")

    def create_project_structure(self, project_path, project_name, device, mikroc):
        """Create the basic project structure"""
        # Create directories
        dirs = ['srcs', 'incs', 'objs', 'bins', 'other', 'docs']
        if mikroc:
            dirs.append('srcs/startup')

        for dir_name in dirs:
            full_path = os.path.join(project_path, dir_name)
            os.makedirs(full_path, exist_ok=True)

        # Create Makefiles
        self.create_root_makefile(project_path, project_name, device)
        self.create_srcs_makefile(project_path, mikroc)

        # Create main.c
        self.create_main_c(project_path, project_name)

        # Create startup files if requested
        if mikroc:
            self.create_startup_files(project_path)

        # Create README and .gitignore
        self.create_readme(project_path, project_name, device)
        self.create_gitignore(project_path)

    def find_microchip_plib_directory(self):
        """Find Microchip peripheral library installation directory"""
        # Harmony 3 MCC-specific path (found in user's .mcc directory)
        user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))
        harmony_mcc_path = os.path.join(
            user_profile, '.mcc', 'harmony', 'content', 'csp')

        # Check for Harmony 3 CSP peripheral libraries first
        if os.path.exists(harmony_mcc_path):
            # Find the latest version directory
            try:
                version_dirs = [d for d in os.listdir(harmony_mcc_path)
                                if d.startswith('v') and os.path.isdir(os.path.join(harmony_mcc_path, d))]
                if version_dirs:
                    # Sort versions and get the latest
                    version_dirs.sort(
                        key=lambda x: [int(n) for n in x[1:].split('.')])
                    latest_version = version_dirs[-1]
                    csp_peripheral_path = os.path.join(
                        harmony_mcc_path, latest_version, 'peripheral')

                    if os.path.exists(csp_peripheral_path):
                        self.log(
                            f"✅ Found Harmony 3 CSP peripheral library: {csp_peripheral_path}")
                        self.log(f"📦 Using version: {latest_version}")
                        return csp_peripheral_path
            except Exception as e:
                self.log(f"⚠️ Error checking Harmony 3 MCC path: {str(e)}")

        # Common Microchip installation paths (fallback)
        possible_paths = [
            r"C:\Program Files\Microchip\MPLABX",
            r"C:\Program Files (x86)\Microchip\MPLABX",
            r"C:\Microchip\MPLABX",
            r"C:\Program Files\Microchip\xc32",
            r"C:\Program Files (x86)\Microchip\xc32",
            r"C:\Program Files\Microchip\MCC",
            r"C:\Program Files (x86)\Microchip\MCC",
            r"C:\microchip\harmony\v3",
            r"C:\Users\*\harmony3_repo",
            r"C:\harmony3"
        ]

        # Look for plib files in various locations
        plib_search_patterns = [
            # Traditional plib locations
            r"packs\Microchip\PIC32MZ-*\plib",
            r"v*\packs\Microchip\PIC32MZ-*\plib",
            r"mcc\lib\plib\pic32mz",
            r"resources\plib\pic32mz",
            r"lib\pic32mz\plib",

            # Harmony 3 peripheral locations
            r"csp\peripheral\**\plib_*",
            r"peripheral\**\plib_*",
            r"csp\drivers\**\plib_*",
            r"drivers\**\plib_*",

            # Alternative search patterns
            r"**\peripheral\uart\*",
            r"**\peripheral\gpio\*",
            r"**\peripheral\tmr\*",
            r"**\plib\*uart*",
            r"**\plib\*gpio*",
            r"**\plib\*tmr*"
        ]

        self.log("Searching for traditional Microchip peripheral library files...")
        found_locations = []

        for base_path in possible_paths:
            if os.path.exists(base_path):
                self.log(f"  Checking: {base_path}")
                for pattern in plib_search_patterns:
                    # Use glob to find matching files/directories
                    search_path = os.path.join(
                        base_path, pattern.replace('*', '*'))
                    try:
                        matches = glob.glob(search_path, recursive=True)
                        for match in matches:
                            if os.path.isfile(match) and ('plib_' in os.path.basename(match) or 'uart' in match.lower()):
                                parent_dir = os.path.dirname(match)
                                if parent_dir not in found_locations:
                                    found_locations.append(parent_dir)
                                    self.log(
                                        f"    Found peripheral files in: {parent_dir}")
                    except Exception as e:
                        # Ignore glob errors for invalid patterns
                        pass

        # Return the first valid location found, or None
        if found_locations:
            best_location = found_locations[0]  # Use first found location
            self.log(
                f"✅ Selected peripheral library location: {best_location}")
            return best_location

        self.log("❌ No Microchip peripheral library files found")
        return None

    def verify_plib_directory(self, plib_path):
        """Verify that directory contains expected plib structure"""
        # Check for common peripheral directories
        expected_dirs = ['uart', 'gpio', 'tmr', 'clk', 'sys']
        found_dirs = 0

        if not os.path.exists(plib_path):
            return False

        for item in os.listdir(plib_path):
            item_path = os.path.join(plib_path, item)
            if os.path.isdir(item_path):
                if any(expected in item.lower() for expected in expected_dirs):
                    found_dirs += 1

        # Return True if we found at least 2 expected peripheral directories
        return found_dirs >= 2

    def generate_peripheral_files(self, project_path, project_name):
        """Copy and configure Microchip peripheral library files"""
        self.log("🔍 Locating Microchip peripheral library files...")

        # Find Microchip plib installation
        microchip_plib_path = self.find_microchip_plib_directory()

        if not microchip_plib_path:
            self.log(
                "⚠️  No Microchip peripheral library files found in standard locations.")
            self.log("💡 This is normal for newer Harmony 3 installations.")
            self.log("📝 Generating custom MCC-compatible peripheral files...")
            self.generate_custom_peripheral_files(project_path, project_name)
            return

        # Create peripheral directories
        periph_base_inc = os.path.join(project_path, 'incs', 'peripheral')
        periph_base_src = os.path.join(project_path, 'srcs', 'peripheral')
        os.makedirs(periph_base_inc, exist_ok=True)
        os.makedirs(periph_base_src, exist_ok=True)

        self.log(f"📂 Using Microchip files from: {microchip_plib_path}")

        # Detect if this is Harmony 3 CSP peripheral directory
        is_harmony3 = 'csp' in microchip_plib_path and 'peripheral' in microchip_plib_path

        if is_harmony3:
            self.log("🎯 Detected Harmony 3 CSP peripheral library")
            self.log("🔧 Processing Harmony 3 template files...")

            # Use Harmony 3 template processing
            if self.config['uart_enabled'].get():
                uart_inc_dir = os.path.join(periph_base_inc, 'uart')
                uart_src_dir = os.path.join(periph_base_src, 'uart')
                os.makedirs(uart_inc_dir, exist_ok=True)
                os.makedirs(uart_src_dir, exist_ok=True)
                self.copy_harmony3_peripheral_templates(
                    microchip_plib_path, uart_inc_dir, uart_src_dir, 'uart')

            if self.config['timer_enabled'].get():
                timer_inc_dir = os.path.join(periph_base_inc, 'tmr')
                timer_src_dir = os.path.join(periph_base_src, 'tmr')
                os.makedirs(timer_inc_dir, exist_ok=True)
                os.makedirs(timer_src_dir, exist_ok=True)
                self.copy_harmony3_peripheral_templates(
                    microchip_plib_path, timer_inc_dir, timer_src_dir, 'tmr')

            if self.config['gpio_enabled'].get():
                gpio_inc_dir = os.path.join(periph_base_inc, 'gpio')
                gpio_src_dir = os.path.join(periph_base_src, 'gpio')
                os.makedirs(gpio_inc_dir, exist_ok=True)
                os.makedirs(gpio_src_dir, exist_ok=True)
                self.generate_gpio_files(gpio_inc_dir, gpio_src_dir)

            if self.config['clock_enabled'].get():
                clk_inc_dir = os.path.join(periph_base_inc, 'clk')
                clk_src_dir = os.path.join(periph_base_src, 'clk')
                os.makedirs(clk_inc_dir, exist_ok=True)
                os.makedirs(clk_src_dir, exist_ok=True)
                self.copy_harmony3_peripheral_templates(
                    microchip_plib_path, clk_inc_dir, clk_src_dir, 'clk')

            if self.config['i2c_enabled'].get():
                i2c_inc_dir = os.path.join(periph_base_inc, 'i2c')
                i2c_src_dir = os.path.join(periph_base_src, 'i2c')
                os.makedirs(i2c_inc_dir, exist_ok=True)
                os.makedirs(i2c_src_dir, exist_ok=True)
                self.copy_harmony3_peripheral_templates(
                    microchip_plib_path, i2c_inc_dir, i2c_src_dir, 'i2c')

            if self.config['spi_enabled'].get():
                spi_inc_dir = os.path.join(periph_base_inc, 'spi')
                spi_src_dir = os.path.join(periph_base_src, 'spi')
                os.makedirs(spi_inc_dir, exist_ok=True)
                os.makedirs(spi_src_dir, exist_ok=True)
                self.copy_harmony3_peripheral_templates(
                    microchip_plib_path, spi_inc_dir, spi_src_dir, 'spi')

        else:
            self.log("🔧 Processing traditional peripheral library files...")

            # Copy and configure enabled peripherals using traditional methods
            if self.config['uart_enabled'].get():
                self.copy_and_configure_uart_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['timer_enabled'].get():
                self.copy_and_configure_timer_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['gpio_enabled'].get():
                self.copy_and_configure_gpio_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['clock_enabled'].get():
                self.copy_and_configure_clock_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['dma_enabled'].get():
                self.copy_and_configure_dma_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['spi_enabled'].get():
                self.copy_and_configure_spi_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

            if self.config['i2c_enabled'].get():
                self.copy_and_configure_i2c_files(
                    microchip_plib_path, periph_base_inc, periph_base_src)

        # Create system files
        self.generate_system_files(project_path, project_name)
        self.log("✅ Peripheral library integration complete!")

    def generate_custom_peripheral_files(self, project_path, project_name):
        """Fallback method - generate custom peripheral files if Microchip plib not found"""
        self.log("Generating custom peripheral library files...")

        # Create peripheral directories
        periph_base_inc = os.path.join(project_path, 'incs', 'peripheral')
        periph_base_src = os.path.join(project_path, 'srcs', 'peripheral')

        # Generate enabled peripherals using original methods
        if self.config['uart_enabled'].get():
            self.generate_uart_files(periph_base_inc, periph_base_src)

        if self.config['timer_enabled'].get():
            self.generate_timer_files(periph_base_inc, periph_base_src)

        if self.config['gpio_enabled'].get():
            self.generate_gpio_files(periph_base_inc, periph_base_src)

        if self.config['clock_enabled'].get():
            self.generate_clock_files(periph_base_inc, periph_base_src)

        if self.config['dma_enabled'].get():
            self.generate_dma_files(periph_base_inc, periph_base_src)

        if self.config['spi_enabled'].get():
            self.generate_spi_files(periph_base_inc, periph_base_src)

        if self.config['i2c_enabled'].get():
            self.generate_i2c_files(periph_base_inc, periph_base_src)

        # Create system files
        self.generate_system_files(project_path, project_name)

    def generate_uart_files(self, inc_base, src_base):
        """Generate UART peripheral files"""
        uart_module = self.uart_config['uart_module'].get()
        uart_num = uart_module[-1]  # Extract number from UART1, UART2, etc.

        self.log(f"  → Creating {uart_module} files...")

        uart_inc_dir = os.path.join(inc_base, 'uart')
        uart_src_dir = os.path.join(src_base, 'uart')
        os.makedirs(uart_inc_dir, exist_ok=True)
        os.makedirs(uart_src_dir, exist_ok=True)

        # Get UART configuration values
        baud_rate = self.uart_config['baud_rate'].get()
        data_bits = self.uart_config['data_bits'].get()
        parity = self.uart_config['parity'].get()
        stop_bits = self.uart_config['stop_bits'].get()
        rx_interrupt = self.uart_config['rx_interrupt'].get()
        tx_interrupt = self.uart_config['tx_interrupt'].get()
        error_interrupt = self.uart_config['error_interrupt'].get()

        # Calculate BRG value (simplified for 80MHz system clock)
        try:
            baud_val = int(baud_rate)
            brg_value = int((80000000 / (16 * baud_val)) - 1)
        except:
            brg_value = 129  # Default for 115200 @ 80MHz

        # Build UART mode register configuration
        uart_mode_bits = []
        uart_mode_comments = []

        if data_bits == '9':
            uart_mode_bits.append('0x0008')  # PDSEL = 11 (9-bit, no parity)
            uart_mode_comments.append('9-bit data, no parity')
        elif parity == 'Even':
            uart_mode_bits.append('0x0002')  # PDSEL = 10 (8-bit, even parity)
            uart_mode_comments.append('8-bit data, even parity')
        elif parity == 'Odd':
            uart_mode_bits.append('0x0004')  # PDSEL = 01 (8-bit, odd parity)
            uart_mode_comments.append('8-bit data, odd parity')
        else:
            uart_mode_bits.append('0x0000')  # PDSEL = 00 (8-bit, no parity)
            uart_mode_comments.append('8-bit data, no parity')

        if stop_bits == '2':
            uart_mode_bits.append('0x0001')  # STSEL = 1 (2 stop bits)
            uart_mode_comments.append('2 stop bits')
        else:
            uart_mode_comments.append('1 stop bit')

        uart_mode_value = ' | '.join(
            ['0x8000'] + uart_mode_bits) if uart_mode_bits else '0x8000'

        # UART header template
        uart_header = f'''/*******************************************************************************
  {uart_module} Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart{uart_num}.h

  Summary:
    {uart_module} peripheral library interface.

  Description:
    This file defines the interface to the {uart_module} peripheral library.
    
  Configuration:
    Baud Rate: {baud_rate}
    Data Bits: {data_bits}
    Parity: {parity}
    Stop Bits: {stop_bits}
*******************************************************************************/

#ifndef PLIB_UART{uart_num}_H
#define PLIB_UART{uart_num}_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"
#include "plib_uart_common.h"

#ifdef __cplusplus
extern "C" {{
#endif

// {uart_module} API
void UART{uart_num}_Initialize(void);
bool UART{uart_num}_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq);
size_t UART{uart_num}_Read(uint8_t* buffer, const size_t size);
size_t UART{uart_num}_Write(uint8_t* buffer, const size_t size);
bool UART{uart_num}_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART{uart_num}_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART{uart_num}_TransmitComplete(void);
bool UART{uart_num}_ReceiverIsReady(void);
bool UART{uart_num}_TransmitBufferIsFull(void);
uint32_t UART{uart_num}_ErrorGet(void);

#ifdef __cplusplus
}}
#endif

#endif /* PLIB_UART{uart_num}_H */
'''

        # UART common header
        uart_common_header = '''/*******************************************************************************
  UART Peripheral Library Common Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart_common.h

  Summary:
    UART peripheral library common interface.

  Description:
    This file defines the common interface to the UART peripheral library.
*******************************************************************************/

#ifndef PLIB_UART_COMMON_H
#define PLIB_UART_COMMON_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// UART callback function pointer
typedef void (*UART_CALLBACK)(uintptr_t context);

// UART serial setup structure
typedef struct
{
    uint32_t baudRate;
    uint8_t dataWidth;
    uint8_t parity;
    uint8_t stopBits;
} UART_SERIAL_SETUP;

// UART object structure
typedef struct
{
    UART_CALLBACK txCallback;
    uintptr_t txContext;
    UART_CALLBACK rxCallback;
    uintptr_t rxContext;
    bool txBusyStatus;
    bool rxBusyStatus;
} UART_OBJECT;

#ifdef __cplusplus
}
#endif

#endif /* PLIB_UART_COMMON_H */
'''

        # UART source template
        uart_source = f'''/*******************************************************************************
  {uart_module} Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart{uart_num}.c

  Summary:
    {uart_module} peripheral library implementation.

  Description:
    This file contains the source code for {uart_module} peripheral library.
    
  Configuration:
    Baud Rate: {baud_rate} ({uart_mode_comments[0] if uart_mode_comments else "8-bit, no parity"})
    BRG Value: {brg_value}
*******************************************************************************/

#include "peripheral/uart/plib_uart{uart_num}.h"
#include "interrupts.h"

// {uart_module} object
static UART_OBJECT uart{uart_num}Obj;

void UART{uart_num}_Initialize(void)
{{
    /* Setup {uart_module} */
    U{uart_num}MODE = {uart_mode_value}; // Enable UART with configuration
    U{uart_num}STA = 0x1400;  // Enable TX and RX
    U{uart_num}BRG = {brg_value};     // {baud_rate} baud @ 80MHz

    uart{uart_num}Obj.rxBusyStatus = false;
    uart{uart_num}Obj.txBusyStatus = false;
    
    /* Configure interrupts */'''

        # Add interrupt configuration
        if rx_interrupt:
            uart_source += f'''
    IFS{(int(uart_num)-1)//4}bits.U{uart_num}RXIF = 0;  // Clear RX interrupt flag
    IEC{(int(uart_num)-1)//4}bits.U{uart_num}RXIE = 1;  // Enable RX interrupt'''

        if tx_interrupt:
            uart_source += f'''
    IFS{(int(uart_num)-1)//4}bits.U{uart_num}TXIF = 0;  // Clear TX interrupt flag
    IEC{(int(uart_num)-1)//4}bits.U{uart_num}TXIE = 1;  // Enable TX interrupt'''

        if error_interrupt:
            uart_source += f'''
    IFS{(int(uart_num)-1)//4}bits.U{uart_num}EIF = 0;   // Clear error interrupt flag
    IEC{(int(uart_num)-1)//4}bits.U{uart_num}EIE = 1;   // Enable error interrupt'''

        uart_source += f'''
}}

bool UART{uart_num}_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq)
{{
    if (setup == NULL) return false;

    uint32_t brgValue = ((srcClkFreq / setup->baudRate) / 16) - 1;
    U{uart_num}BRG = brgValue;

    return true;
}}

size_t UART{uart_num}_Read(uint8_t* buffer, const size_t size)
{{
    size_t nBytesRead = 0;

    while (nBytesRead < size && U{uart_num}STAbits.URXDA)
    {{
        buffer[nBytesRead++] = U{uart_num}RXREG;
    }}

    return nBytesRead;
}}

size_t UART{uart_num}_Write(uint8_t* buffer, const size_t size)
{{
    size_t nBytesWritten = 0;

    while (nBytesWritten < size)
    {{
        while (U{uart_num}STAbits.UTXBF); // Wait for TX buffer space
        U{uart_num}TXREG = buffer[nBytesWritten++];
    }}

    return nBytesWritten;
}}

bool UART{uart_num}_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{{
    uart{uart_num}Obj.txCallback = callback;
    uart{uart_num}Obj.txContext = context;
    return true;
}}

bool UART{uart_num}_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{{
    uart{uart_num}Obj.rxCallback = callback;
    uart{uart_num}Obj.rxContext = context;
    return true;
}}

bool UART{uart_num}_TransmitComplete(void)
{{
    return U{uart_num}STAbits.TRMT;
}}

bool UART{uart_num}_ReceiverIsReady(void)
{{
    return U{uart_num}STAbits.URXDA;
}}

bool UART{uart_num}_TransmitBufferIsFull(void)
{{
    return U{uart_num}STAbits.UTXBF;
}}

uint32_t UART{uart_num}_ErrorGet(void)
{{
    return (U{uart_num}STA & (_U{uart_num}STA_OERR_MASK | _U{uart_num}STA_FERR_MASK | _U{uart_num}STA_PERR_MASK));
}}
'''

        # Write files
        with open(os.path.join(uart_inc_dir, f'plib_uart{uart_num}.h'), 'w', encoding='utf-8') as f:
            f.write(uart_header)
        with open(os.path.join(uart_inc_dir, 'plib_uart_common.h'), 'w', encoding='utf-8') as f:
            f.write(uart_common_header)
        with open(os.path.join(uart_src_dir, f'plib_uart{uart_num}.c'), 'w', encoding='utf-8') as f:
            f.write(uart_source)

    def generate_timer_files(self, inc_base, src_base):
        """Generate Timer peripheral files with user configuration"""
        timer_module = self.timer_config['timer_module'].get()
        # Extract number from TMR1, TMR2, etc.
        timer_num = timer_module.replace('TMR', '')

        self.log(f"  → Creating {timer_module} files...")

        timer_inc_dir = os.path.join(inc_base, f'tmr{timer_num}')
        timer_src_dir = os.path.join(src_base, f'tmr{timer_num}')
        os.makedirs(timer_inc_dir, exist_ok=True)
        os.makedirs(timer_src_dir, exist_ok=True)

        # Get timer configuration values
        timer_mode = self.timer_config['timer_mode'].get()
        prescaler = self.timer_config['prescaler'].get()
        period_mode = self.timer_config['period_mode'].get()
        frequency = self.timer_config['frequency'].get()
        period_ms = self.timer_config['period_ms'].get()
        period_us = self.timer_config['period_us'].get()
        period_count = self.timer_config['period_count'].get()
        interrupt_enabled = self.timer_config['interrupt_enabled'].get()
        interrupt_priority = self.timer_config['interrupt_priority'].get()
        auto_start = self.timer_config['auto_start'].get()
        gate_enable = self.timer_config['gate_enable'].get()
        gate_polarity = self.timer_config['gate_polarity'].get()
        external_clock = self.timer_config['external_clock'].get()
        clock_source = self.timer_config['clock_source'].get()
        output_enable = self.timer_config['output_enable'].get()
        output_polarity = self.timer_config['output_polarity'].get()
        stop_in_idle = self.timer_config['stop_in_idle'].get()

        # Calculate prescaler register value and divisor
        prescaler_map = {
            '1:1': (0, 1),      # TCKPS = 00, divisor = 1
            '1:8': (1, 8),      # TCKPS = 01, divisor = 8
            '1:64': (2, 64),    # TCKPS = 10, divisor = 64
            '1:256': (3, 256)   # TCKPS = 11, divisor = 256
        }
        prescaler_reg, prescaler_div = prescaler_map.get(prescaler, (0, 1))

        # Calculate period register value based on period mode
        try:
            if period_mode == 'Frequency':
                freq_val = float(frequency)
                # Calculate period count for given frequency
                # Period = (PR + 1) * prescaler / input_clock
                # PR = (input_clock / (prescaler * frequency)) - 1
                input_clock = 80000000  # Assume 80MHz PBCLK3
                pr_value = int((input_clock / (prescaler_div * freq_val)) - 1)
            elif period_mode == 'Period (ms)':
                period_val = float(period_ms) / 1000.0  # Convert to seconds
                input_clock = 80000000
                pr_value = int((input_clock * period_val / prescaler_div) - 1)
            elif period_mode == 'Period (μs)':
                period_val = float(period_us) / 1000000.0  # Convert to seconds
                input_clock = 80000000
                pr_value = int((input_clock * period_val / prescaler_div) - 1)
            elif period_mode == 'Count Value':
                pr_value = int(period_count)
            else:
                pr_value = 80000  # Default 1ms @ 80MHz
        except:
            pr_value = 80000  # Default fallback

        # Limit PR value based on timer mode
        if timer_mode == '16-bit':
            pr_value = min(pr_value, 0xFFFF)
        else:
            pr_value = min(pr_value, 0xFFFFFFFF)

        # Build T1CON register configuration
        tcon_bits = []
        tcon_comments = []

        # Timer mode (16-bit vs 32-bit)
        if timer_mode == '32-bit (TMRx/TMRy)':
            # Enable 32-bit mode
            tcon_bits.append(f'_T{timer_num}CON_T32_MASK')
            tcon_comments.append('32-bit mode enabled')
        else:
            tcon_comments.append('16-bit mode')

        # Prescaler
        if prescaler_reg > 0:
            tcon_bits.append(
                f'({prescaler_reg} << _T{timer_num}CON_TCKPS_POSITION)')
            tcon_comments.append(f'Prescaler {prescaler} (÷{prescaler_div})')
        else:
            tcon_comments.append(f'No prescaler (÷1)')

        # Gate control
        if gate_enable:
            tcon_bits.append(f'_T{timer_num}CON_TGATE_MASK')
            gate_pol = 'active high' if gate_polarity == 'Active High' else 'active low'
            tcon_comments.append(f'Gate control enabled ({gate_pol})')

        # External clock
        if external_clock:
            tcon_bits.append(f'_T{timer_num}CON_TCS_MASK')
            tcon_comments.append('External clock source')
        else:
            tcon_comments.append(f'Internal clock ({clock_source})')

        # Stop in idle
        if stop_in_idle:
            tcon_bits.append(f'_T{timer_num}CON_SIDL_MASK')
            tcon_comments.append('Stop in idle mode')

        # Build final TCON value
        tcon_value = ' | '.join(tcon_bits) if tcon_bits else '0x0000'

        # Calculate actual frequency for comments
        try:
            actual_freq = 80000000 / (prescaler_div * (pr_value + 1))
            if actual_freq >= 1000:
                freq_display = f"{actual_freq/1000:.1f} kHz"
            else:
                freq_display = f"{actual_freq:.1f} Hz"
        except:
            freq_display = "Calculated frequency"

        # Timer header template
        timer_header = f'''/*******************************************************************************
  {timer_module} Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_tmr{timer_num}.h

  Summary:
    {timer_module} peripheral library interface.

  Description:
    This file defines the interface to the {timer_module} peripheral library.
    
  Configuration:
    Timer Mode: {timer_mode}
    Prescaler: {prescaler}
    Period Mode: {period_mode}
    Frequency: {freq_display}
    Interrupt: {'Enabled' if interrupt_enabled else 'Disabled'}
    Priority: {interrupt_priority}
*******************************************************************************/

#ifndef PLIB_TMR{timer_num}_H
#define PLIB_TMR{timer_num}_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

#ifdef __cplusplus
extern "C" {{
#endif

typedef void (*TMR{timer_num}_CALLBACK)(uint32_t status, uintptr_t context);

typedef struct
{{
    TMR{timer_num}_CALLBACK callback;
    uintptr_t context;
}} TMR{timer_num}_OBJECT;

// {timer_module} API
void TMR{timer_num}_Initialize(void);
void TMR{timer_num}_Start(void);
void TMR{timer_num}_Stop(void);
void TMR{timer_num}_PeriodSet({'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} period);
{'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} TMR{timer_num}_PeriodGet(void);
{'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} TMR{timer_num}_CounterGet(void);
void TMR{timer_num}_CounterSet({'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} count);
uint32_t TMR{timer_num}_FrequencyGet(void);
bool TMR{timer_num}_CallbackRegister(TMR{timer_num}_CALLBACK callback, uintptr_t context);

#ifdef __cplusplus
}}
#endif

#endif /* PLIB_TMR{timer_num}_H */
'''

        # Timer source template
        timer_source = f'''/*******************************************************************************
  {timer_module} Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_tmr{timer_num}.c

  Summary:
    {timer_module} peripheral library implementation.

  Description:
    This file contains the source code for {timer_module} peripheral library.
    
  Configuration:
    Timer: {timer_module} ({timer_mode})
    Clock Source: {clock_source}
    Prescaler: {prescaler} (÷{prescaler_div})
    Period Value: {pr_value}
    Frequency: {freq_display}
    Interrupt Priority: {interrupt_priority}
*******************************************************************************/

#include "peripheral/tmr{timer_num}/plib_tmr{timer_num}.h"
#include "interrupts.h"

// {timer_module} object
static TMR{timer_num}_OBJECT tmr{timer_num}Obj;

void TMR{timer_num}_Initialize(void)
{{
    /* Setup {timer_module} */
    T{timer_num}CON = 0x0000;  // Stop and reset timer
    TMR{timer_num} = 0x0000;   // Clear counter
    PR{timer_num} = {pr_value};     // Period value for {freq_display}

    /* Configure Timer Control Register */'''

        # Add timer configuration comments
        for comment in tcon_comments:
            timer_source += f'\n    /* {comment} */'

        timer_source += f'''
    T{timer_num}CON = {tcon_value};  // Configure timer'''

        # Add interrupt configuration
        if interrupt_enabled:
            # Map timer number to interrupt register
            ipc_reg = f"IPC{(int(timer_num)-1)//4 + 1}"
            if_reg = f"IFS{(int(timer_num)-1)//4}"
            ie_reg = f"IEC{(int(timer_num)-1)//4}"

            timer_source += f'''

    /* Configure Timer Interrupt */
    {ipc_reg}bits.T{timer_num}IP = {interrupt_priority};  // Priority {interrupt_priority}
    {if_reg}bits.T{timer_num}IF = 0;  // Clear interrupt flag
    {ie_reg}bits.T{timer_num}IE = 1;  // Enable interrupt'''

        # Add auto-start option
        if auto_start:
            timer_source += f'''
    
    /* Auto-start timer */
    T{timer_num}CONbits.ON = 1;   // Enable timer'''
        else:
            timer_source += f'''
    
    /* Timer configured but not started - call TMR{timer_num}_Start() to begin */'''

        timer_source += f'''
}}

void TMR{timer_num}_Start(void)
{{
    T{timer_num}CONbits.ON = 1;
}}

void TMR{timer_num}_Stop(void)
{{
    T{timer_num}CONbits.ON = 0;
}}

void TMR{timer_num}_PeriodSet({'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} period)
{{
    PR{timer_num} = period;
}}

{'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} TMR{timer_num}_PeriodGet(void)
{{
    return PR{timer_num};
}}

{'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} TMR{timer_num}_CounterGet(void)
{{
    return TMR{timer_num};
}}

void TMR{timer_num}_CounterSet({'uint32_t' if timer_mode == '32-bit (TMRx/TMRy)' else 'uint16_t'} count)
{{
    TMR{timer_num} = count;
}}

uint32_t TMR{timer_num}_FrequencyGet(void)
{{
    /* Calculate frequency: Input_Clock / (Prescaler * (PR + 1)) */
    uint32_t prescaler_div = {prescaler_div};
    uint32_t period = PR{timer_num} + 1;
    uint32_t input_clock = 80000000;  // Assume 80MHz PBCLK3
    
    return input_clock / (prescaler_div * period);
}}

bool TMR{timer_num}_CallbackRegister(TMR{timer_num}_CALLBACK callback, uintptr_t context)
{{
    tmr{timer_num}Obj.callback = callback;
    tmr{timer_num}Obj.context = context;
    return true;
}}'''

        # Add interrupt handler if interrupts are enabled
        if interrupt_enabled:
            timer_source += f'''

// Interrupt handler (called from interrupts.c)
void TMR{timer_num}_InterruptHandler(void)
{{
    IFS{(int(timer_num)-1)//4}bits.T{timer_num}IF = 0;  // Clear interrupt flag

    if (tmr{timer_num}Obj.callback != NULL)
    {{
        tmr{timer_num}Obj.callback(0, tmr{timer_num}Obj.context);
    }}
}}'''

        timer_source += '''
'''

        # Write files
        with open(os.path.join(timer_inc_dir, f'plib_tmr{timer_num}.h'), 'w', encoding='utf-8') as f:
            f.write(timer_header)
        with open(os.path.join(timer_src_dir, f'plib_tmr{timer_num}.c'), 'w', encoding='utf-8') as f:
            f.write(timer_source)

    def generate_gpio_files(self, gpio_inc_dir, gpio_src_dir):
        """Generate comprehensive GPIO peripheral library files based on user configuration"""
        try:
            self.log("🔧 Generating GPIO configuration files...")

            # Count enabled pins
            enabled_pins = []
            for pin_name, config in self.gpio_pins.items():
                if config['enabled'].get():
                    enabled_pins.append(pin_name)

            if not enabled_pins:
                self.log(
                    "⚠️  No GPIO pins selected - skipping GPIO file generation")
                return

            self.log(
                f"📌 Generating configuration for {len(enabled_pins)} pins: {', '.join(enabled_pins[:5])}{' ...' if len(enabled_pins) > 5 else ''}")

            # Generate plib_gpio.h header file
            self.generate_gpio_header(gpio_inc_dir, enabled_pins)

            # Generate plib_gpio.c implementation file
            self.generate_gpio_source(gpio_src_dir, enabled_pins)

            self.log("✅ GPIO files generated successfully")

        except Exception as e:
            self.log(f"❌ Error generating GPIO files: {str(e)}")
            raise

    def generate_gpio_header(self, gpio_inc_dir, enabled_pins):
        """Generate plib_gpio.h header file with pin definitions and function prototypes"""

        # Build pin definitions and macros
        pin_definitions = []
        pin_enums = []
        function_prototypes = []

        # Group pins by port for efficient register operations
        ports_used = set()
        for pin_name in enabled_pins:
            if pin_name in self.pin_database:
                pin_info = self.pin_database[pin_name]
                port = pin_info['port']
                ports_used.add(port)

                # Add pin definitions
                pin_num = int(pin_name[2:])  # Extract number from RXn
                pin_definitions.append(
                    f"#define GPIO_PIN_{pin_name}     (1U << {pin_num})")

                # Add to enum
                pin_enums.append(
                    f"    GPIO_PIN_{pin_name} = (1U << {pin_num}),")

        # Sort for consistent output
        pin_definitions.sort()
        pin_enums.sort()

        # Generate header content
        header_content = f'''/*******************************************************************************
  GPIO Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_gpio.h

  Summary:
    GPIO peripheral library interface.

  Description:
    This file defines the interface to the GPIO peripheral library. This
    library provides access to and control of the associated peripheral
    instance.

  Remarks:
    Generated by PIC32MZ Project Builder
    Configuration: {len(enabled_pins)} pins configured across ports {', '.join(sorted(ports_used))}
*******************************************************************************/

#ifndef PLIB_GPIO_H
#define PLIB_GPIO_H

#include <stdbool.h>
#include <stdint.h>
#include "device.h"

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Pin Definitions
// *****************************************************************************
// *****************************************************************************

// Pin definitions for configured GPIO pins
{chr(10).join(pin_definitions)}

// GPIO Pin enumeration
typedef enum {{
{chr(10).join(pin_enums)}
}} GPIO_PIN;

// GPIO Port enumeration  
typedef enum {{
    GPIO_PORT_A = 0,
    GPIO_PORT_B = 1,
    GPIO_PORT_C = 2,
    GPIO_PORT_D = 3,
    GPIO_PORT_E = 4,
    GPIO_PORT_F = 5,
    GPIO_PORT_G = 6,
}} GPIO_PORT;

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Pin Direction and State Functions
// *****************************************************************************
// *****************************************************************************

void GPIO_Initialize(void);

void GPIO_PinWrite(GPIO_PIN pin, bool value);
bool GPIO_PinRead(GPIO_PIN pin);
bool GPIO_PinLatchRead(GPIO_PIN pin);
void GPIO_PinToggle(GPIO_PIN pin);
void GPIO_PinSet(GPIO_PIN pin);
void GPIO_PinClear(GPIO_PIN pin);

void GPIO_PinInputEnable(GPIO_PIN pin);
void GPIO_PinOutputEnable(GPIO_PIN pin);

bool GPIO_PinInterruptFlagGet(GPIO_PIN pin);
void GPIO_PinInterruptFlagClear(GPIO_PIN pin);
void GPIO_PinInterruptEnable(GPIO_PIN pin);
void GPIO_PinInterruptDisable(GPIO_PIN pin);

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Port Functions
// *****************************************************************************
// *****************************************************************************

void GPIO_PortWrite(GPIO_PORT port, uint32_t mask, uint32_t value);
uint32_t GPIO_PortRead(GPIO_PORT port);
uint32_t GPIO_PortLatchRead(GPIO_PORT port);
void GPIO_PortSet(GPIO_PORT port, uint32_t mask);
void GPIO_PortClear(GPIO_PORT port, uint32_t mask);
void GPIO_PortToggle(GPIO_PORT port, uint32_t mask);
void GPIO_PortInputEnable(GPIO_PORT port, uint32_t mask);
void GPIO_PortOutputEnable(GPIO_PORT port, uint32_t mask);

#endif // PLIB_GPIO_H
'''

        # Write header file
        header_file = os.path.join(gpio_inc_dir, 'plib_gpio.h')
        with open(header_file, 'w') as f:
            f.write(header_content)

        self.log(f"📄 Generated {header_file}")

    def generate_gpio_source(self, gpio_src_dir, enabled_pins):
        """Generate plib_gpio.c implementation file with initialization and functions"""

        # Build initialization code for each enabled pin
        init_code_lines = []
        ports_used = {}  # Track which ports need configuration

        for pin_name in enabled_pins:
            if pin_name not in self.pin_database:
                continue

            pin_info = self.pin_database[pin_name]
            config = self.gpio_pins[pin_name]
            port = pin_info['port']
            pin_num = int(pin_name[2:])  # Extract number from RXn

            # Track ports used
            if port not in ports_used:
                ports_used[port] = {'pins': [], 'configs': []}
            ports_used[port]['pins'].append(pin_num)
            ports_used[port]['configs'].append(config)

            init_code_lines.append(f"    // {pin_name} Configuration")

            # Set direction
            direction = config['direction'].get()
            if direction == 'Output':
                init_code_lines.append(
                    f"    TRIS{port}CLR = (1U << {pin_num});  // Output")
                # Set initial state
                initial_state = config['initial_state'].get()
                if initial_state == 'High':
                    init_code_lines.append(
                        f"    LAT{port}SET = (1U << {pin_num});   // Initial High")
                else:
                    init_code_lines.append(
                        f"    LAT{port}CLR = (1U << {pin_num});   // Initial Low")
            else:
                init_code_lines.append(
                    f"    TRIS{port}SET = (1U << {pin_num});  // Input")

            # Configure analog function
            if config['analog_enabled'].get():
                if pin_info['analog']:
                    init_code_lines.append(
                        f"    ANSEL{port}SET = (1U << {pin_num}); // Analog")
                else:
                    init_code_lines.append(
                        f"    // Note: {pin_name} does not support analog function")
            else:
                init_code_lines.append(
                    f"    ANSEL{port}CLR = (1U << {pin_num}); // Digital")

            # Configure pull-up/pull-down
            if config['pull_up'].get():
                init_code_lines.append(
                    f"    CN{port}PUESET = (1U << {pin_num}); // Pull-up")
            if config['pull_down'].get():
                init_code_lines.append(
                    f"    CN{port}PDSET = (1U << {pin_num});  // Pull-down")

            # Configure open drain
            if config['open_drain'].get() and direction == 'Output':
                init_code_lines.append(
                    f"    ODC{port}SET = (1U << {pin_num});   // Open drain")

            # Configure Schmitt trigger
            if config['schmidt_trigger'].get():
                # Not all PIC32MZ pins support this, but include for completeness
                init_code_lines.append(
                    f"    // Schmitt trigger enabled (if supported)")

            # Configure slew rate
            slew_rate = config['slew_rate'].get()
            if slew_rate == 'Fast':
                init_code_lines.append(
                    f"    SR{port}CLR = (1U << {pin_num});    // Fast slew rate")
            else:
                init_code_lines.append(
                    f"    SR{port}SET = (1U << {pin_num});    // Standard slew rate")

            # Configure interrupts
            if config['interrupt_enabled'].get() or config['change_notification'].get():
                edge = config['interrupt_edge'].get()
                init_code_lines.append(
                    f"    // Interrupt/Change notification configuration")
                init_code_lines.append(
                    f"    CN{port}IESET = (1U << {pin_num});  // Input edge detect")
                if edge == 'Rising':
                    init_code_lines.append(
                        f"    CNEN0SET = (1U << {pin_num});     // Rising edge")
                elif edge == 'Falling':
                    init_code_lines.append(
                        f"    CNEN1SET = (1U << {pin_num});     // Falling edge")
                else:  # Both
                    init_code_lines.append(
                        f"    CNEN0SET = (1U << {pin_num});     // Both edges")
                    init_code_lines.append(
                        f"    CNEN1SET = (1U << {pin_num});     // Both edges")

            # Alternative function configuration
            alt_function = config['alt_function'].get()
            if alt_function and alt_function != 'GPIO':
                init_code_lines.append(
                    f"    // Alternative function: {alt_function}")
                # Note: PPS configuration would be device-specific
                init_code_lines.append(
                    f"    // PPS configuration for {alt_function} would be added here")

            init_code_lines.append("")  # Add spacing

        # Generate source content
        source_content = f'''/*******************************************************************************
  GPIO Peripheral Library Implementation File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_gpio.c

  Summary:
    GPIO peripheral library implementation.

  Description:
    This file contains the implementation of the interface functions and 
    interrupt handlers for the GPIO peripheral library.

  Remarks:
    Generated by PIC32MZ Project Builder
    Configuration: {len(enabled_pins)} pins configured across ports {', '.join(sorted(ports_used.keys()))}
*******************************************************************************/

#include "plib_gpio.h"

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Port Register Access
// *****************************************************************************
// *****************************************************************************

// Port register base addresses for efficient access
static volatile uint32_t* const PORT_REGS[] = {{
    &PORTA, &PORTB, &PORTC, &PORTD, &PORTE, &PORTF, &PORTG
}};

static volatile uint32_t* const LAT_REGS[] = {{
    &LATA, &LATB, &LATC, &LATD, &LATE, &LATF, &LATG
}};

static volatile uint32_t* const TRIS_REGS[] = {{
    &TRISA, &TRISB, &TRISC, &TRISD, &TRISE, &TRISF, &TRISG
}};

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Initialization
// *****************************************************************************
// *****************************************************************************

void GPIO_Initialize(void)
{{
    /* Configure GPIO pins based on user settings */
    
{chr(10).join(init_code_lines)}
    
    /* GPIO initialization complete */
}}

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Pin Control Functions
// *****************************************************************************
// *****************************************************************************

void GPIO_PinWrite(GPIO_PIN pin, bool value)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask (simplified for generated pins)
    if (pin_mask & 0x0FFF) port = 0;        // Port A
    else if (pin_mask & 0xFFFF000) port = 1; // Port B  
    // Add more port detection as needed
    
    if (value)
        *LAT_REGS[port] |= pin_mask;
    else
        *LAT_REGS[port] &= ~pin_mask;
}}

bool GPIO_PinRead(GPIO_PIN pin)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask
    if (pin_mask & 0x0FFF) port = 0;
    else if (pin_mask & 0xFFFF000) port = 1;
    
    return ((*PORT_REGS[port] & pin_mask) != 0);
}}

bool GPIO_PinLatchRead(GPIO_PIN pin)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask
    if (pin_mask & 0x0FFF) port = 0;
    else if (pin_mask & 0xFFFF000) port = 1;
    
    return ((*LAT_REGS[port] & pin_mask) != 0);
}}

void GPIO_PinToggle(GPIO_PIN pin)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask
    if (pin_mask & 0x0FFF) port = 0;
    else if (pin_mask & 0xFFFF000) port = 1;
    
    *LAT_REGS[port] ^= pin_mask;
}}

void GPIO_PinSet(GPIO_PIN pin)
{{
    GPIO_PinWrite(pin, true);
}}

void GPIO_PinClear(GPIO_PIN pin)
{{
    GPIO_PinWrite(pin, false);
}}

void GPIO_PinInputEnable(GPIO_PIN pin)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask
    if (pin_mask & 0x0FFF) port = 0;
    else if (pin_mask & 0xFFFF000) port = 1;
    
    *TRIS_REGS[port] |= pin_mask;
}}

void GPIO_PinOutputEnable(GPIO_PIN pin)
{{
    uint32_t port = 0;
    uint32_t pin_mask = (uint32_t)pin;
    
    // Determine port from pin mask  
    if (pin_mask & 0x0FFF) port = 0;
    else if (pin_mask & 0xFFFF000) port = 1;
    
    *TRIS_REGS[port] &= ~pin_mask;
}}

// Placeholder interrupt functions (would need device-specific implementation)
bool GPIO_PinInterruptFlagGet(GPIO_PIN pin)
{{
    // Device-specific interrupt flag reading would be implemented here
    return false;
}}

void GPIO_PinInterruptFlagClear(GPIO_PIN pin)
{{
    // Device-specific interrupt flag clearing would be implemented here
}}

void GPIO_PinInterruptEnable(GPIO_PIN pin)
{{
    // Device-specific interrupt enabling would be implemented here
}}

void GPIO_PinInterruptDisable(GPIO_PIN pin)
{{
    // Device-specific interrupt disabling would be implemented here
}}

// *****************************************************************************
// *****************************************************************************
// Section: GPIO Port Control Functions
// *****************************************************************************
// *****************************************************************************

void GPIO_PortWrite(GPIO_PORT port, uint32_t mask, uint32_t value)
{{
    *LAT_REGS[port] = (*LAT_REGS[port] & (~mask)) | (mask & value);
}}

uint32_t GPIO_PortRead(GPIO_PORT port)
{{
    return *PORT_REGS[port];
}}

uint32_t GPIO_PortLatchRead(GPIO_PORT port)
{{
    return *LAT_REGS[port];
}}

void GPIO_PortSet(GPIO_PORT port, uint32_t mask)
{{
    *LAT_REGS[port] |= mask;
}}

void GPIO_PortClear(GPIO_PORT port, uint32_t mask)
{{
    *LAT_REGS[port] &= ~mask;
}}

void GPIO_PortToggle(GPIO_PORT port, uint32_t mask)
{{
    *LAT_REGS[port] ^= mask;
}}

void GPIO_PortInputEnable(GPIO_PORT port, uint32_t mask)
{{
    *TRIS_REGS[port] |= mask;
}}

void GPIO_PortOutputEnable(GPIO_PORT port, uint32_t mask)
{{
    *TRIS_REGS[port] &= ~mask;
}}
'''

        # Write source file
        source_file = os.path.join(gpio_src_dir, 'plib_gpio.c')
        with open(source_file, 'w') as f:
            f.write(source_content)

        self.log(f"📄 Generated {source_file}")

    def generate_clock_files(self, inc_base, src_base):
        """Generate Clock peripheral files"""
        self.log("  → Creating Clock files...")

        clock_inc_dir = os.path.join(inc_base, 'clk')
        clock_src_dir = os.path.join(src_base, 'clk')
        os.makedirs(clock_inc_dir, exist_ok=True)
        os.makedirs(clock_src_dir, exist_ok=True)

        # Get clock configuration values
        system_freq = float(
            self.clock_config['system_freq'].get()) * 1000000  # Convert to Hz
        peripheral_freq = float(
            self.clock_config['peripheral_freq'].get()) * 1000000
        input_freq = float(self.clock_config['input_freq'].get()) * 1000000
        pll_enabled = self.clock_config['pll_enabled'].get()
        osc_type = self.clock_config['primary_osc'].get()

        # Build PBCLK configuration
        pbclk_defines = []
        pbclk_comments = []
        pbclk_configs = [
            ("PBCLK1", "pbclk1", "CPU/System Bus"),
            ("PBCLK2", "pbclk2", "UART/SPI/I2C Peripherals"),
            ("PBCLK3", "pbclk3", "Timer/PWM/Input Capture/Output Compare"),
            ("PBCLK4", "pbclk4", "Ports/Change Notification"),
            ("PBCLK5", "pbclk5", "Flash Controller/Crypto"),
            ("PBCLK6", "pbclk6", "USB/CAN/Ethernet"),
            ("PBCLK7", "pbclk7", "CPU Trace/Debug"),
        ]

        for name, var_prefix, desc in pbclk_configs:
            enabled = self.clock_config[f'{var_prefix}_enabled'].get()

            if enabled:
                # Parse the divider format "0 = ÷1" to extract actual divisor and register value
                div_str = self.clock_config[f'{var_prefix}_div'].get()
                if ' = ÷' in div_str:
                    # Extract the register value and divisor from format "X = ÷Y"
                    reg_val = int(div_str.split(' = ÷')[0])
                    divisor = int(div_str.split(' = ÷')[1])
                else:
                    # Fallback for old format
                    reg_val = int(div_str) if div_str.isdigit() else 0
                    divisor = reg_val + 1 if reg_val >= 0 else 1
            else:
                reg_val = 0
                divisor = 1

            freq = int(system_freq / divisor) if enabled else 0

            pbclk_defines.append(
                f"#define CLK_{name}_ENABLED       {1 if enabled else 0}")
            pbclk_defines.append(f"#define CLK_{name}_FREQUENCY     {freq}UL")
            pbclk_defines.append(f"#define CLK_{name}_DIVIDER_REG   {reg_val}")
            pbclk_defines.append(f"#define CLK_{name}_DIVIDER_VAL   {divisor}")
            pbclk_comments.append(
                f" {name}: {'Enabled' if enabled else 'Disabled'} - {desc}")
            if enabled:
                pbclk_comments.append(
                    f"    ├── Register Value: {reg_val} (÷{divisor})")
                pbclk_comments.append(
                    f"    └── Frequency: {freq/1000000:.1f} MHz")
            pbclk_defines.append(f"#define CLK_{name}_FREQUENCY     {freq}UL")
            pbclk_defines.append(f"#define CLK_{name}_DIVIDER_REG   {reg_val}")
            pbclk_defines.append(f"#define CLK_{name}_DIVIDER_VAL   {divisor}")
            pbclk_comments.append(
                f" {name}: {'Enabled' if enabled else 'Disabled'} - {desc}")
            if enabled:
                pbclk_comments.append(
                    f"    ├── Register Value: {reg_val} (÷{divisor})")
                pbclk_comments.append(
                    f"    └── Frequency: {freq/1000000:.1f} MHz")

        clock_header = f'''/*******************************************************************************
  CLK Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_clk.h

  Summary:
    CLK peripheral library interface.
    
  Description:
    Generated clock configuration based on user settings:
    - Primary Oscillator: {osc_type} ({self.clock_config['input_freq'].get()} MHz)
    - PLL: {'Enabled' if pll_enabled else 'Disabled'}
    - System Frequency: {self.clock_config['system_freq'].get()} MHz
    - Peripheral Frequency: {self.clock_config['peripheral_freq'].get()} MHz
*******************************************************************************/

#ifndef PLIB_CLK_H
#define PLIB_CLK_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {{
#endif

// Clock configuration constants
#define CLK_SYSTEM_FREQUENCY    {int(system_freq)}UL
#define CLK_PERIPHERAL_FREQUENCY {int(peripheral_freq)}UL
#define CLK_INPUT_FREQUENCY     {int(input_freq)}UL

// Oscillator configuration
#define CLK_PRIMARY_OSC         "{osc_type}"
#define CLK_PLL_ENABLED         {1 if pll_enabled else 0}

{"// PLL Configuration" if pll_enabled else "// PLL Disabled"}
{f"#define CLK_PLL_INPUT_DIV       {self.clock_config['pll_input_div'].get()}" if pll_enabled else ""}
{f"#define CLK_PLL_MULTIPLIER      {self.clock_config['pll_mult'].get()}" if pll_enabled else ""}
{f"#define CLK_PLL_OUTPUT_DIV      {self.clock_config['pll_output_div'].get()}" if pll_enabled else ""}

// Peripheral Bus Clock Configuration
// PIC32MZ PBCLK Assignments (based on datasheet):
//   PBCLK1: CPU/System Bus - CPU instructions, system bus
//   PBCLK2: UART/SPI/I2C Peripherals - Serial communication modules  
//   PBCLK3: Timer/PWM/Input Capture/Output Compare - Time-based peripherals
//   PBCLK4: Ports/Change Notification - GPIO and pin change notifications
//   PBCLK5: Flash Controller/Crypto - Flash memory and cryptographic engine
//   PBCLK6: USB/CAN/Ethernet - High-speed communication interfaces
//   PBCLK7: CPU Trace/Debug - Development and debugging features
// Register Values: 1=÷1 (no division), 2=÷2, 3=÷3, etc.
{chr(10).join(pbclk_defines)}

// Clock API
void CLK_Initialize(void);
uint32_t CLK_SystemFrequencyGet(void);
uint32_t CLK_PeripheralFrequencyGet(void);
uint32_t CLK_InputFrequencyGet(void);
bool CLK_PLLIsEnabled(void);

// PBCLK API
uint32_t CLK_PBCLKFrequencyGet(uint8_t pbclkNum);
bool CLK_PBCLKIsEnabled(uint8_t pbclkNum);

#ifdef __cplusplus
}}
#endif

#endif /* PLIB_CLK_H */
'''

        clock_source = f'''/*******************************************************************************
  CLK Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_clk.c

  Summary:
    CLK peripheral library implementation.
    
  Description:
    Generated clock implementation with user-configured settings:
    - System Clock: {self.clock_config['system_freq'].get()} MHz
    - PLL: {'Enabled' if pll_enabled else 'Disabled'}
*******************************************************************************/

#include "peripheral/clk/plib_clk.h"

void CLK_Initialize(void)
{{
    /* Primary Oscillator Configuration: {osc_type} */
    /* Input Frequency: {self.clock_config['input_freq'].get()} MHz */
    
{"    /* PLL Configuration */" if pll_enabled else "    /* PLL Disabled - Using primary oscillator directly */"}
{f"    /* Input Divider: {self.clock_config['pll_input_div'].get()} */" if pll_enabled else ""}
{f"    /* Multiplier: {self.clock_config['pll_mult'].get()} */" if pll_enabled else ""}
{f"    /* Output Divider: {self.clock_config['pll_output_div'].get()} */" if pll_enabled else ""}
    
    /* Note: Actual hardware configuration would be implemented here */
    /* This typically involves setting configuration bits and control registers */
    
    /* Example PIC32MZ clock configuration registers:
     * - OSCCON: Oscillator Control Register
     * - SPLLCON: System PLL Control Register  
     * - PB1DIV: Peripheral Bus 1 Clock Divisor
     * Configuration bits would also be set for oscillator selection
     */
     
    /* For this implementation, we assume configuration bits are set correctly */
    /* and the hardware is configured to produce the specified frequencies */
}}

uint32_t CLK_SystemFrequencyGet(void)
{{
    return CLK_SYSTEM_FREQUENCY;
}}

uint32_t CLK_PeripheralFrequencyGet(void)
{{
    return CLK_PERIPHERAL_FREQUENCY;
}}

uint32_t CLK_InputFrequencyGet(void)
{{
    return CLK_INPUT_FREQUENCY;
}}

bool CLK_PLLIsEnabled(void)
{{
    return {str(pll_enabled).lower()};
}}

uint32_t CLK_PBCLKFrequencyGet(uint8_t pbclkNum)
{{
    switch(pbclkNum)
    {{
        case 1: return CLK_PBCLK1_ENABLED ? CLK_PBCLK1_FREQUENCY : 0;
        case 2: return CLK_PBCLK2_ENABLED ? CLK_PBCLK2_FREQUENCY : 0;
        case 3: return CLK_PBCLK3_ENABLED ? CLK_PBCLK3_FREQUENCY : 0;
        case 4: return CLK_PBCLK4_ENABLED ? CLK_PBCLK4_FREQUENCY : 0;
        case 5: return CLK_PBCLK5_ENABLED ? CLK_PBCLK5_FREQUENCY : 0;
        case 6: return CLK_PBCLK6_ENABLED ? CLK_PBCLK6_FREQUENCY : 0;
        case 7: return CLK_PBCLK7_ENABLED ? CLK_PBCLK7_FREQUENCY : 0;
        default: return 0;
    }}
}}

bool CLK_PBCLKIsEnabled(uint8_t pbclkNum)
{{
    switch(pbclkNum)
    {{
        case 1: return CLK_PBCLK1_ENABLED;
        case 2: return CLK_PBCLK2_ENABLED;
        case 3: return CLK_PBCLK3_ENABLED;
        case 4: return CLK_PBCLK4_ENABLED;
        case 5: return CLK_PBCLK5_ENABLED;
        case 6: return CLK_PBCLK6_ENABLED;
        case 7: return CLK_PBCLK7_ENABLED;
        default: return false;
    }}
}}

/*******************************************************************************
 Clock Configuration Summary:
 
 Primary Oscillator: {osc_type} @ {self.clock_config['input_freq'].get()} MHz
 PLL Status: {'Enabled' if pll_enabled else 'Disabled'}
{f" PLL Input Divider: /{self.clock_config['pll_input_div'].get()}" if pll_enabled else ""}
{f" PLL Multiplier: x{self.clock_config['pll_mult'].get()}" if pll_enabled else ""}
{f" PLL Output Divider: /{self.clock_config['pll_output_div'].get()}" if pll_enabled else ""}
 System Clock: {self.clock_config['system_freq'].get()} MHz
 Peripheral Clock: {self.clock_config['peripheral_freq'].get()} MHz
 
 Peripheral Bus Clocks:
{chr(10).join(pbclk_comments)}
 
 Clock Tree:
 {osc_type} Oscillator ({self.clock_config['input_freq'].get()} MHz)
    ↓
{" PLL Processing" if pll_enabled else " Direct Connection (No PLL)"}
{f"    ├── ÷{self.clock_config['pll_input_div'].get()} → {float(self.clock_config['input_freq'].get()) / int(self.clock_config['pll_input_div'].get()):.1f} MHz" if pll_enabled else ""}
{f"    ├── ×{self.clock_config['pll_mult'].get()} → {(float(self.clock_config['input_freq'].get()) / int(self.clock_config['pll_input_div'].get())) * int(self.clock_config['pll_mult'].get()):.1f} MHz (VCO)" if pll_enabled else ""}
{f"    └── ÷{self.clock_config['pll_output_div'].get()} → {self.clock_config['system_freq'].get()} MHz" if pll_enabled else ""}
    ↓
 System Clock: {self.clock_config['system_freq'].get()} MHz
 Peripheral Clock: {self.clock_config['peripheral_freq'].get()} MHz
 
*******************************************************************************/
'''

        with open(os.path.join(clock_inc_dir, 'plib_clk.h'), 'w', encoding='utf-8') as f:
            f.write(clock_header)
        with open(os.path.join(clock_src_dir, 'plib_clk.c'), 'w', encoding='utf-8') as f:
            f.write(clock_source)

    def generate_dma_files(self, inc_base, src_base):
        """Generate DMA peripheral files"""
        self.log("  → Creating DMA files...")

        dma_inc_dir = os.path.join(inc_base, 'dma')
        dma_src_dir = os.path.join(src_base, 'dma')
        os.makedirs(dma_inc_dir, exist_ok=True)
        os.makedirs(dma_src_dir, exist_ok=True)

        # DMA header template
        dma_header = '''/*******************************************************************************
  DMA System Service Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_dma.h

  Summary:
    DMA system service interface.

  Description:
    This file defines the interface to the DMA system service.
*******************************************************************************/

#ifndef PLIB_DMA_H
#define PLIB_DMA_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

#ifdef __cplusplus
extern "C" {
#endif

// DMA callback function pointer
typedef void (*DMA_CALLBACK)(uintptr_t context);

// DMA channel enumeration
typedef enum
{
    DMA_CHANNEL_0 = 0,
    DMA_CHANNEL_1,
    DMA_CHANNEL_2,
    DMA_CHANNEL_3,
    DMA_CHANNEL_4,
    DMA_CHANNEL_5,
    DMA_CHANNEL_6,
    DMA_CHANNEL_7
} DMA_CHANNEL;

// DMA transfer width enumeration
typedef enum
{
    DMA_WIDTH_8_BIT = 0,
    DMA_WIDTH_16_BIT,
    DMA_WIDTH_32_BIT
} DMA_TRANSFER_WIDTH;

// DMA API
void DMA_Initialize(void);
void DMA_ChannelTransfer(DMA_CHANNEL channel, const void* srcAddr, size_t srcSize, 
                        const void* destAddr, size_t destSize, size_t cellSize);
bool DMA_ChannelIsBusy(DMA_CHANNEL channel);
void DMA_ChannelDisable(DMA_CHANNEL channel);
bool DMA_ChannelCallbackRegister(DMA_CHANNEL channel, DMA_CALLBACK eventHandler, uintptr_t contextHandle);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_DMA_H */
'''

        # DMA source template
        dma_source = '''/*******************************************************************************
  DMA System Service Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_dma.c

  Summary:
    DMA system service implementation.

  Description:
    This file contains the source code for DMA system service.
*******************************************************************************/

#include "peripheral/dma/plib_dma.h"
#include "interrupts.h"

// DMA object structure
typedef struct
{
    DMA_CALLBACK callback;
    uintptr_t context;
    bool inUse;
} DMA_CHANNEL_OBJECT;

// DMA channel objects
static DMA_CHANNEL_OBJECT dmaChannelObj[8];

void DMA_Initialize(void)
{
    /* Initialize DMA controller */
    DMACON = 0x0000;        // Disable DMA controller
    
    /* Initialize channel objects */
    for (int i = 0; i < 8; i++)
    {
        dmaChannelObj[i].callback = NULL;
        dmaChannelObj[i].context = 0;
        dmaChannelObj[i].inUse = false;
    }
    
    /* Enable DMA controller */
    DMACONbits.ON = 1;
    
    /* Configure DMA priorities and settings as needed */
    /* This would typically involve setting up interrupt priorities */
}

void DMA_ChannelTransfer(DMA_CHANNEL channel, const void* srcAddr, size_t srcSize, 
                        const void* destAddr, size_t destSize, size_t cellSize)
{
    if (channel >= 8) return;
    
    volatile uint32_t* dchCon = (volatile uint32_t*)(&DCH0CON + (channel * 0x30));
    volatile uint32_t* dchEcon = (volatile uint32_t*)(&DCH0ECON + (channel * 0x30));
    volatile uint32_t* dchSsa = (volatile uint32_t*)(&DCH0SSA + (channel * 0x30));
    volatile uint32_t* dchDsa = (volatile uint32_t*)(&DCH0DSA + (channel * 0x30));
    volatile uint32_t* dchSsiz = (volatile uint32_t*)(&DCH0SSIZ + (channel * 0x30));
    volatile uint32_t* dchDsiz = (volatile uint32_t*)(&DCH0DSIZ + (channel * 0x30));
    volatile uint32_t* dchCsiz = (volatile uint32_t*)(&DCH0CSIZ + (channel * 0x30));
    
    /* Disable the channel */
    *dchCon = 0x0000;
    
    /* Configure source and destination addresses */
    *dchSsa = (uint32_t)srcAddr;
    *dchDsa = (uint32_t)destAddr;
    
    /* Configure transfer sizes */
    *dchSsiz = srcSize;
    *dchDsiz = destSize;
    *dchCsiz = cellSize;
    
    /* Configure channel control */
    *dchCon = 0x0080;  // CHAEN = 1, enable auto mode
    
    /* Mark channel as in use */
    dmaChannelObj[channel].inUse = true;
    
    /* Enable channel */
    *dchCon |= 0x0080;  // CHEN = 1
    
    /* Force start transfer */
    *dchEcon |= 0x0080;  // CFORCE = 1
}

bool DMA_ChannelIsBusy(DMA_CHANNEL channel)
{
    if (channel >= 8) return false;
    
    volatile uint32_t* dchCon = (volatile uint32_t*)(&DCH0CON + (channel * 0x30));
    
    return ((*dchCon & 0x0080) != 0) && dmaChannelObj[channel].inUse;
}

void DMA_ChannelDisable(DMA_CHANNEL channel)
{
    if (channel >= 8) return;
    
    volatile uint32_t* dchCon = (volatile uint32_t*)(&DCH0CON + (channel * 0x30));
    
    /* Disable channel */
    *dchCon &= ~0x0080;  // CHEN = 0
    
    /* Mark channel as not in use */
    dmaChannelObj[channel].inUse = false;
}

bool DMA_ChannelCallbackRegister(DMA_CHANNEL channel, DMA_CALLBACK eventHandler, uintptr_t contextHandle)
{
    if (channel >= 8) return false;
    
    dmaChannelObj[channel].callback = eventHandler;
    dmaChannelObj[channel].context = contextHandle;
    
    return true;
}

/* DMA interrupt handlers would be implemented here */
/* These would typically be called from the main interrupt handler */
void DMA_ChannelInterruptHandler(DMA_CHANNEL channel)
{
    if (channel >= 8) return;
    
    if (dmaChannelObj[channel].callback != NULL)
    {
        dmaChannelObj[channel].callback(dmaChannelObj[channel].context);
    }
    
    /* Clear channel transfer complete flag */
    volatile uint32_t* dchInt = (volatile uint32_t*)(&DCH0INT + (channel * 0x30));
    *dchInt &= ~0x0008;  // Clear CHBCIF
}
'''

        # Write files
        with open(os.path.join(dma_inc_dir, 'plib_dma.h'), 'w', encoding='utf-8') as f:
            f.write(dma_header)
        with open(os.path.join(dma_src_dir, 'plib_dma.c'), 'w', encoding='utf-8') as f:
            f.write(dma_source)

    def generate_spi_files(self, inc_base, src_base):
        """Generate SPI peripheral files"""
        self.log("  → Creating SPI files...")

        spi_inc_dir = os.path.join(inc_base, 'spi')
        spi_src_dir = os.path.join(src_base, 'spi')
        os.makedirs(spi_inc_dir, exist_ok=True)
        os.makedirs(spi_src_dir, exist_ok=True)

        # SPI header template
        spi_header = '''/*******************************************************************************
  SPI1 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_spi1.h

  Summary:
    SPI1 peripheral library interface.

  Description:
    This file defines the interface to the SPI1 peripheral library.
*******************************************************************************/

#ifndef PLIB_SPI1_H
#define PLIB_SPI1_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"
#include "plib_spi_common.h"

#ifdef __cplusplus
extern "C" {
#endif

// SPI1 API
void SPI1_Initialize(void);
bool SPI1_WriteRead(void* pWriteData, size_t writeSize, void* pReadData, size_t readSize);
bool SPI1_Write(void* pWriteData, size_t writeSize);
bool SPI1_Read(void* pReadData, size_t readSize);
bool SPI1_IsTransmitterBusy(void);
bool SPI1_CallbackRegister(SPI_CALLBACK callback, uintptr_t context);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_SPI1_H */
'''

        # SPI common header
        spi_common_header = '''/*******************************************************************************
  SPI Peripheral Library Common Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_spi_common.h

  Summary:
    SPI peripheral library common interface.

  Description:
    This file defines the common interface to the SPI peripheral library.
*******************************************************************************/

#ifndef PLIB_SPI_COMMON_H
#define PLIB_SPI_COMMON_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// SPI callback function pointer
typedef void (*SPI_CALLBACK)(uintptr_t context);

// SPI transfer status enumeration
typedef enum
{
    SPI_TRANSFER_STATUS_IDLE,
    SPI_TRANSFER_STATUS_BUSY,
    SPI_TRANSFER_STATUS_COMPLETE,
    SPI_TRANSFER_STATUS_ERROR
} SPI_TRANSFER_STATUS;

// SPI object structure
typedef struct
{
    SPI_CALLBACK callback;
    uintptr_t context;
    bool transferInProgress;
} SPI_OBJECT;

#ifdef __cplusplus
}
#endif

#endif /* PLIB_SPI_COMMON_H */
'''

        # SPI source template
        spi_source = '''/*******************************************************************************
  SPI1 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_spi1.c

  Summary:
    SPI1 peripheral library implementation.

  Description:
    This file contains the source code for SPI1 peripheral library.
*******************************************************************************/

#include "peripheral/spi/plib_spi1.h"
#include "interrupts.h"

// SPI1 object
static SPI_OBJECT spi1Obj;

void SPI1_Initialize(void)
{
    /* Setup SPI1 */
    SPI1CON = 0x0000;      // Disable SPI and reset
    
    /* Configure SPI1 for master mode */
    SPI1CONbits.MSTEN = 1;    // Master mode
    SPI1CONbits.CKP = 0;      // Clock polarity: idle state low
    SPI1CONbits.CKE = 1;      // Clock edge: data transmitted on rising edge
    SPI1CONbits.MODE16 = 0;   // 8-bit mode
    SPI1CONbits.MODE32 = 0;   // 8-bit mode
    SPI1CONbits.SMP = 0;      // Sample at middle of data output time
    
    /* Set baud rate (PBCLK2 / (2 * (SPI1BRG + 1))) */
    /* For 1MHz SPI clock @ 80MHz PBCLK2: BRG = 39 */
    SPI1BRG = 39;             // ~1MHz SPI clock
    
    // Clear status flags
    SPI1STAT = 0x0000;
    
    // Initialize SPI object
    spi1Obj.transferInProgress = false;
    spi1Obj.callback = NULL;
    spi1Obj.context = 0;
    
    // Enable SPI module
    SPI1CONbits.ON = 1;
}

bool SPI1_WriteRead(void* pWriteData, size_t writeSize, void* pReadData, size_t readSize)
{
    if (spi1Obj.transferInProgress || pWriteData == NULL)
        return false;

    spi1Obj.transferInProgress = true;
    
    uint8_t* writeBuffer = (uint8_t*)pWriteData;
    uint8_t* readBuffer = (uint8_t*)pReadData;
    
    size_t maxSize = (writeSize > readSize) ? writeSize : readSize;
    
    for (size_t i = 0; i < maxSize; i++)
    {
        uint8_t writeData = 0x00;
        
        // Get write data if available
        if (i < writeSize)
            writeData = writeBuffer[i];
        
        // Wait for TX buffer to be empty
        while (SPI1STATbits.SPITBF);
        
        // Send data
        SPI1BUF = writeData;
        
        // Wait for receive buffer to have data
        while (!SPI1STATbits.SPIRBF);
        
        // Read received data
        uint8_t receivedData = SPI1BUF;
        
        // Store received data if buffer provided
        if (readBuffer != NULL && i < readSize)
            readBuffer[i] = receivedData;
    }
    
    spi1Obj.transferInProgress = false;
    return true;
}

bool SPI1_Write(void* pWriteData, size_t writeSize)
{
    return SPI1_WriteRead(pWriteData, writeSize, NULL, 0);
}

bool SPI1_Read(void* pReadData, size_t readSize)
{
    if (spi1Obj.transferInProgress || pReadData == NULL)
        return false;

    spi1Obj.transferInProgress = true;
    
    uint8_t* readBuffer = (uint8_t*)pReadData;
    
    for (size_t i = 0; i < readSize; i++)
    {
        // Wait for TX buffer to be empty
        while (SPI1STATbits.SPITBF);
        
        // Send dummy data to generate clock
        SPI1BUF = 0xFF;
        
        // Wait for receive buffer to have data
        while (!SPI1STATbits.SPIRBF);
        
        // Read received data
        readBuffer[i] = SPI1BUF;
    }
    
    spi1Obj.transferInProgress = false;
    return true;
}

bool SPI1_IsTransmitterBusy(void)
{
    return spi1Obj.transferInProgress || SPI1STATbits.SPITBF;
}

bool SPI1_CallbackRegister(SPI_CALLBACK callback, uintptr_t context)
{
    spi1Obj.callback = callback;
    spi1Obj.context = context;
    return true;
}
'''

        # Write files
        with open(os.path.join(spi_inc_dir, 'plib_spi1.h'), 'w', encoding='utf-8') as f:
            f.write(spi_header)
        with open(os.path.join(spi_inc_dir, 'plib_spi_common.h'), 'w', encoding='utf-8') as f:
            f.write(spi_common_header)
        with open(os.path.join(spi_src_dir, 'plib_spi1.c'), 'w', encoding='utf-8') as f:
            f.write(spi_source)

    def generate_i2c_files(self, inc_base, src_base):
        """Generate I2C peripheral files"""
        self.log("  → Creating I2C files...")

        i2c_inc_dir = os.path.join(inc_base, 'i2c')
        i2c_src_dir = os.path.join(src_base, 'i2c')
        os.makedirs(i2c_inc_dir, exist_ok=True)
        os.makedirs(i2c_src_dir, exist_ok=True)

        # I2C header template
        i2c_header = '''/*******************************************************************************
  I2C1 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_i2c1.h

  Summary:
    I2C1 peripheral library interface.

  Description:
    This file defines the interface to the I2C1 peripheral library.
*******************************************************************************/

#ifndef PLIB_I2C1_H
#define PLIB_I2C1_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"
#include "plib_i2c_common.h"

#ifdef __cplusplus
extern "C" {
#endif

// I2C1 API
void I2C1_Initialize(void);
bool I2C1_Read(uint16_t address, uint8_t* rdata, size_t rlength);
bool I2C1_Write(uint16_t address, uint8_t* wdata, size_t wlength);
bool I2C1_WriteRead(uint16_t address, uint8_t* wdata, size_t wlength, uint8_t* rdata, size_t rlength);
bool I2C1_IsBusy(void);
I2C_ERROR I2C1_ErrorGet(void);
bool I2C1_CallbackRegister(I2C_CALLBACK callback, uintptr_t contextHandle);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_I2C1_H */
'''

        # I2C common header
        i2c_common_header = '''/*******************************************************************************
  I2C Peripheral Library Common Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_i2c_common.h

  Summary:
    I2C peripheral library common interface.

  Description:
    This file defines the common interface to the I2C peripheral library.
*******************************************************************************/

#ifndef PLIB_I2C_COMMON_H
#define PLIB_I2C_COMMON_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// I2C callback function pointer
typedef void (*I2C_CALLBACK)(uintptr_t context);

// I2C error enumeration
typedef enum
{
    I2C_ERROR_NONE = 0,
    I2C_ERROR_NACK = 1,
    I2C_ERROR_BUS_COLLISION = 2,
    I2C_ERROR_OVERFLOW = 4,
    I2C_ERROR_RECEIVE_OVERFLOW = 8,
    I2C_ERROR_TRANSMIT_UNDERFLOW = 16,
    I2C_ERROR_ACKNOWLEDGE_STATUS = 32
} I2C_ERROR;

// I2C transfer status enumeration
typedef enum
{
    I2C_TRANSFER_STATUS_IN_PROGRESS,
    I2C_TRANSFER_STATUS_SUCCESS,
    I2C_TRANSFER_STATUS_ERROR
} I2C_TRANSFER_STATUS;

// I2C object structure
typedef struct
{
    I2C_CALLBACK callback;
    uintptr_t context;
    bool transferInProgress;
    I2C_ERROR error;
} I2C_OBJECT;

#ifdef __cplusplus
}
#endif

#endif /* PLIB_I2C_COMMON_H */
'''

        # I2C source template
        i2c_source = '''/*******************************************************************************
  I2C1 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_i2c1.c

  Summary:
    I2C1 peripheral library implementation.

  Description:
    This file contains the source code for I2C1 peripheral library.
*******************************************************************************/

#include "peripheral/i2c/plib_i2c1.h"
#include "interrupts.h"

// I2C1 object
static I2C_OBJECT i2c1Obj;

void I2C1_Initialize(void)
{
    /* Setup I2C1 */
    I2C1CON = 0x0000;      // Disable I2C and reset
    I2C1BRG = 0x4F;        // 100kHz @ 80MHz PBCLK2 (BRG = (PBCLK2/(2*FSCL))-1)
    I2C1CONbits.DISSLW = 1; // Disable slew rate control for standard speed
    
    // Clear status and error flags
    I2C1STAT = 0x0000;
    
    // Initialize I2C object
    i2c1Obj.transferInProgress = false;
    i2c1Obj.error = I2C_ERROR_NONE;
    i2c1Obj.callback = NULL;
    i2c1Obj.context = 0;
    
    // Enable I2C module
    I2C1CONbits.ON = 1;
}

bool I2C1_Read(uint16_t address, uint8_t* rdata, size_t rlength)
{
    if (i2c1Obj.transferInProgress || rdata == NULL || rlength == 0)
        return false;

    i2c1Obj.transferInProgress = true;
    i2c1Obj.error = I2C_ERROR_NONE;

    // Start condition
    I2C1CONbits.SEN = 1;
    while (I2C1CONbits.SEN);

    // Send address with read bit
    I2C1TRN = (address << 1) | 0x01;
    while (I2C1STATbits.TRSTAT);

    // Check for ACK
    if (I2C1STATbits.ACKSTAT)
    {
        i2c1Obj.error = I2C_ERROR_NACK;
        I2C1CONbits.PEN = 1; // Stop condition
        while (I2C1CONbits.PEN);
        i2c1Obj.transferInProgress = false;
        return false;
    }

    // Read data bytes
    for (size_t i = 0; i < rlength; i++)
    {
        I2C1CONbits.RCEN = 1; // Enable receive
        while (!I2C1STATbits.RBF); // Wait for data
        rdata[i] = I2C1RCV;

        // Send ACK/NACK
        if (i < (rlength - 1))
            I2C1CONbits.ACKDT = 0; // ACK
        else
            I2C1CONbits.ACKDT = 1; // NACK on last byte
        
        I2C1CONbits.ACKEN = 1;
        while (I2C1CONbits.ACKEN);
    }

    // Stop condition
    I2C1CONbits.PEN = 1;
    while (I2C1CONbits.PEN);

    i2c1Obj.transferInProgress = false;
    return true;
}

bool I2C1_Write(uint16_t address, uint8_t* wdata, size_t wlength)
{
    if (i2c1Obj.transferInProgress || wdata == NULL || wlength == 0)
        return false;

    i2c1Obj.transferInProgress = true;
    i2c1Obj.error = I2C_ERROR_NONE;

    // Start condition
    I2C1CONbits.SEN = 1;
    while (I2C1CONbits.SEN);

    // Send address with write bit
    I2C1TRN = (address << 1) & 0xFE;
    while (I2C1STATbits.TRSTAT);

    // Check for ACK
    if (I2C1STATbits.ACKSTAT)
    {
        i2c1Obj.error = I2C_ERROR_NACK;
        I2C1CONbits.PEN = 1; // Stop condition
        while (I2C1CONbits.PEN);
        i2c1Obj.transferInProgress = false;
        return false;
    }

    // Send data bytes
    for (size_t i = 0; i < wlength; i++)
    {
        I2C1TRN = wdata[i];
        while (I2C1STATbits.TRSTAT);

        // Check for ACK
        if (I2C1STATbits.ACKSTAT)
        {
            i2c1Obj.error = I2C_ERROR_NACK;
            I2C1CONbits.PEN = 1; // Stop condition
            while (I2C1CONbits.PEN);
            i2c1Obj.transferInProgress = false;
            return false;
        }
    }

    // Stop condition
    I2C1CONbits.PEN = 1;
    while (I2C1CONbits.PEN);

    i2c1Obj.transferInProgress = false;
    return true;
}

bool I2C1_WriteRead(uint16_t address, uint8_t* wdata, size_t wlength, uint8_t* rdata, size_t rlength)
{
    if (i2c1Obj.transferInProgress || wdata == NULL || rdata == NULL || wlength == 0 || rlength == 0)
        return false;

    i2c1Obj.transferInProgress = true;
    i2c1Obj.error = I2C_ERROR_NONE;

    // Start condition
    I2C1CONbits.SEN = 1;
    while (I2C1CONbits.SEN);

    // Send address with write bit
    I2C1TRN = (address << 1) & 0xFE;
    while (I2C1STATbits.TRSTAT);

    // Check for ACK
    if (I2C1STATbits.ACKSTAT)
    {
        i2c1Obj.error = I2C_ERROR_NACK;
        I2C1CONbits.PEN = 1; // Stop condition
        while (I2C1CONbits.PEN);
        i2c1Obj.transferInProgress = false;
        return false;
    }

    // Send data bytes
    for (size_t i = 0; i < wlength; i++)
    {
        I2C1TRN = wdata[i];
        while (I2C1STATbits.TRSTAT);

        if (I2C1STATbits.ACKSTAT)
        {
            i2c1Obj.error = I2C_ERROR_NACK;
            I2C1CONbits.PEN = 1; // Stop condition
            while (I2C1CONbits.PEN);
            i2c1Obj.transferInProgress = false;
            return false;
        }
    }

    // Restart condition
    I2C1CONbits.RSEN = 1;
    while (I2C1CONbits.RSEN);

    // Send address with read bit
    I2C1TRN = (address << 1) | 0x01;
    while (I2C1STATbits.TRSTAT);

    // Check for ACK
    if (I2C1STATbits.ACKSTAT)
    {
        i2c1Obj.error = I2C_ERROR_NACK;
        I2C1CONbits.PEN = 1; // Stop condition
        while (I2C1CONbits.PEN);
        i2c1Obj.transferInProgress = false;
        return false;
    }

    // Read data bytes
    for (size_t i = 0; i < rlength; i++)
    {
        I2C1CONbits.RCEN = 1; // Enable receive
        while (!I2C1STATbits.RBF); // Wait for data
        rdata[i] = I2C1RCV;

        // Send ACK/NACK
        if (i < (rlength - 1))
            I2C1CONbits.ACKDT = 0; // ACK
        else
            I2C1CONbits.ACKDT = 1; // NACK on last byte
        
        I2C1CONbits.ACKEN = 1;
        while (I2C1CONbits.ACKEN);
    }

    // Stop condition
    I2C1CONbits.PEN = 1;
    while (I2C1CONbits.PEN);

    i2c1Obj.transferInProgress = false;
    return true;
}

bool I2C1_IsBusy(void)
{
    return i2c1Obj.transferInProgress;
}

I2C_ERROR I2C1_ErrorGet(void)
{
    return i2c1Obj.error;
}

bool I2C1_CallbackRegister(I2C_CALLBACK callback, uintptr_t contextHandle)
{
    i2c1Obj.callback = callback;
    i2c1Obj.context = contextHandle;
    return true;
}
'''

        # Write files
        with open(os.path.join(i2c_inc_dir, 'plib_i2c1.h'), 'w', encoding='utf-8') as f:
            f.write(i2c_header)
        with open(os.path.join(i2c_inc_dir, 'plib_i2c_common.h'), 'w', encoding='utf-8') as f:
            f.write(i2c_common_header)
        with open(os.path.join(i2c_src_dir, 'plib_i2c1.c'), 'w', encoding='utf-8') as f:
            f.write(i2c_source)

    def copy_and_configure_uart_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure UART files from Microchip installation"""
        uart_module = self.uart_config['uart_module'].get()
        uart_num = uart_module[-1]

        self.log(f"  → Searching for {uart_module} files...")

        # Create target directories
        uart_inc_dir = os.path.join(inc_base, 'uart')
        uart_src_dir = os.path.join(src_base, 'uart')
        os.makedirs(uart_inc_dir, exist_ok=True)
        os.makedirs(uart_src_dir, exist_ok=True)

        # Search for UART files more broadly
        uart_search_patterns = [
            f'**/uart*/plib_uart{uart_num}*',
            f'**/uart*/plib_uart_common*',
            f'**/*uart{uart_num}*',
            f'**/plib_uart{uart_num}*',
            f'**/plib_uart_common*',
            '**/uart**/*',
            '**/plib*uart*'
        ]

        copied_files = []

        # Start from a broader search base if needed
        search_bases = [microchip_plib_path]
        # Also search parent directories in case we found a subdirectory
        if microchip_plib_path:
            search_bases.append(os.path.dirname(microchip_plib_path))
            search_bases.append(os.path.dirname(
                os.path.dirname(microchip_plib_path)))

        for search_base in search_bases:
            if not search_base or not os.path.exists(search_base):
                continue

            for pattern in uart_search_patterns:
                search_path = os.path.join(search_base, pattern)
                try:
                    matches = glob.glob(search_path, recursive=True)
                    for match in matches:
                        if os.path.isfile(match):
                            filename = os.path.basename(match)
                            # Filter for relevant UART files
                            if (f'uart{uart_num}' in filename.lower() or
                                'uart_common' in filename.lower() or
                                    ('uart' in filename.lower() and filename.endswith(('.h', '.c')))):

                                if match.endswith('.h'):
                                    dest_path = os.path.join(
                                        uart_inc_dir, filename)
                                else:
                                    dest_path = os.path.join(
                                        uart_src_dir, filename)

                                # Avoid duplicates
                                if not os.path.exists(dest_path):
                                    try:
                                        shutil.copy2(match, dest_path)
                                        copied_files.append((match, dest_path))
                                        self.log(f"    ✓ Copied: {filename}")
                                    except Exception as e:
                                        self.log(
                                            f"    ⚠ Failed to copy {filename}: {e}")
                except Exception:
                    # Ignore glob errors
                    continue

        if not copied_files:
            self.log(
                f"    No {uart_module} files found in Microchip installation")
            self.log(f"    Generating custom {uart_module} files...")
            self.generate_uart_files(inc_base, src_base)
            return

        self.log(f"    ✅ Copied {len(copied_files)} {uart_module} files")
        # Reconfigure copied files with user settings
        self.reconfigure_uart_files(uart_inc_dir, uart_src_dir, uart_num)

    def copy_and_configure_timer_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure Timer files from Microchip installation"""
        self.log("  → Copying and configuring Timer1 files...")

        # Create target directories
        timer_inc_dir = os.path.join(inc_base, 'tmr1')
        timer_src_dir = os.path.join(src_base, 'tmr1')
        os.makedirs(timer_inc_dir, exist_ok=True)
        os.makedirs(timer_src_dir, exist_ok=True)

        # Look for Timer1 files in Microchip plib
        timer_patterns = [
            'tmr1/plib_tmr1*',
            'tmr/plib_tmr1*',
            'timer/plib_tmr1*',
            '**/tmr1/plib_tmr1*',
            '**/tmr/plib_tmr1*'
        ]

        copied_files = []
        for pattern in timer_patterns:
            search_path = os.path.join(microchip_plib_path, pattern)
            matches = glob.glob(search_path, recursive=True)
            for match in matches:
                if os.path.isfile(match):
                    filename = os.path.basename(match)
                    if match.endswith('.h'):
                        dest_path = os.path.join(timer_inc_dir, filename)
                    else:
                        dest_path = os.path.join(timer_src_dir, filename)

                    try:
                        shutil.copy2(match, dest_path)
                        copied_files.append((match, dest_path))
                        self.log(f"    Copied: {filename}")
                    except Exception as e:
                        self.log(f"    Failed to copy {filename}: {e}")

        if not copied_files:
            self.log("    No Timer1 files found, generating custom files...")
            self.generate_timer_files(inc_base, src_base)

    def copy_and_configure_gpio_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure GPIO files from Microchip installation"""
        self.log("  → Copying and configuring GPIO files...")

        # Create target directories
        gpio_inc_dir = os.path.join(inc_base, 'gpio')
        gpio_src_dir = os.path.join(src_base, 'gpio')
        os.makedirs(gpio_inc_dir, exist_ok=True)
        os.makedirs(gpio_src_dir, exist_ok=True)

        # Look for GPIO files in Microchip plib
        gpio_patterns = [
            'gpio/plib_gpio*',
            'ports/plib_gpio*',
            '**/gpio/plib_gpio*',
            '**/ports/plib_gpio*'
        ]

        copied_files = []
        for pattern in gpio_patterns:
            search_path = os.path.join(microchip_plib_path, pattern)
            matches = glob.glob(search_path, recursive=True)
            for match in matches:
                if os.path.isfile(match):
                    filename = os.path.basename(match)
                    if match.endswith('.h'):
                        dest_path = os.path.join(gpio_inc_dir, filename)
                    else:
                        dest_path = os.path.join(gpio_src_dir, filename)

                    try:
                        shutil.copy2(match, dest_path)
                        copied_files.append((match, dest_path))
                        self.log(f"    Copied: {filename}")
                    except Exception as e:
                        self.log(f"    Failed to copy {filename}: {e}")

        if not copied_files:
            self.log("    No GPIO files found, generating custom files...")
            self.generate_gpio_files(inc_base, src_base)

    def copy_and_configure_clock_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure Clock files from Microchip installation"""
        self.log("  → Copying and configuring Clock files...")

        # Create target directories
        clock_inc_dir = os.path.join(inc_base, 'clk')
        clock_src_dir = os.path.join(src_base, 'clk')
        os.makedirs(clock_inc_dir, exist_ok=True)
        os.makedirs(clock_src_dir, exist_ok=True)

        # Look for Clock files in Microchip plib
        clock_patterns = [
            'clk/plib_clk*',
            'clock/plib_clk*',
            'osc/plib_clk*',
            '**/clk/plib_clk*',
            '**/clock/plib_clk*'
        ]

        copied_files = []
        for pattern in clock_patterns:
            search_path = os.path.join(microchip_plib_path, pattern)
            matches = glob.glob(search_path, recursive=True)
            for match in matches:
                if os.path.isfile(match):
                    filename = os.path.basename(match)
                    if match.endswith('.h'):
                        dest_path = os.path.join(clock_inc_dir, filename)
                    else:
                        dest_path = os.path.join(clock_src_dir, filename)

                    try:
                        shutil.copy2(match, dest_path)
                        copied_files.append((match, dest_path))
                        self.log(f"    Copied: {filename}")
                    except Exception as e:
                        self.log(f"    Failed to copy {filename}: {e}")

        if not copied_files:
            self.log("    No Clock files found, generating custom files...")
            self.generate_clock_files(inc_base, src_base)
        else:
            # Reconfigure copied clock files with user settings
            self.reconfigure_clock_files(clock_inc_dir, clock_src_dir)

    def copy_and_configure_dma_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure DMA files from Microchip installation"""
        self.log("  → Copying and configuring DMA files...")
        # DMA copy implementation would go here
        pass

    def copy_and_configure_spi_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure SPI files from Microchip installation"""
        self.log("  → Searching for SPI files...")

        # Create target directories
        spi_inc_dir = os.path.join(inc_base, 'spi')
        spi_src_dir = os.path.join(src_base, 'spi')
        os.makedirs(spi_inc_dir, exist_ok=True)
        os.makedirs(spi_src_dir, exist_ok=True)

        # Search for SPI files more broadly
        spi_search_patterns = [
            '**/spi*/plib_spi1*',
            '**/spi*/plib_spi_common*',
            '**/*spi1*',
            '**/plib_spi1*',
            '**/plib_spi_common*',
            '**/spi**/*',
            '**/plib*spi*'
        ]

        copied_files = []

        # Start from a broader search base if needed
        search_bases = [microchip_plib_path]
        # Also search parent directories in case we found a subdirectory
        if microchip_plib_path:
            parent_dir = os.path.dirname(microchip_plib_path)
            grandparent_dir = os.path.dirname(parent_dir)
            search_bases.extend([parent_dir, grandparent_dir])

        for search_base in search_bases:
            if not os.path.exists(search_base):
                continue

            for pattern in spi_search_patterns:
                search_pattern = os.path.join(search_base, pattern)

                try:
                    for file_path in glob.glob(search_pattern, recursive=True):
                        if os.path.isfile(file_path):
                            file_name = os.path.basename(file_path)
                            file_ext = os.path.splitext(file_name)[1]

                            # Determine target directory based on file extension
                            if file_ext in ['.h']:
                                target_dir = spi_inc_dir
                            elif file_ext in ['.c']:
                                target_dir = spi_src_dir
                            else:
                                continue

                            target_path = os.path.join(target_dir, file_name)

                            # Copy file if not already copied
                            if target_path not in copied_files:
                                try:
                                    shutil.copy2(file_path, target_path)
                                    copied_files.append(target_path)
                                    self.log(f"    ✓ Copied {file_name}")
                                except Exception as e:
                                    self.log(
                                        f"    ⚠ Error copying {file_name}: {str(e)}")
                except Exception as e:
                    self.log(
                        f"    ⚠ Error searching pattern {pattern}: {str(e)}")

        if not copied_files:
            self.log(
                "    ⚠ No Microchip SPI files found, generating custom files...")
            # Generate our own SPI files if none found
            self.generate_spi_files(inc_base, src_base)
            return

        self.log(f"    ✅ Copied {len(copied_files)} SPI files")
        # Optionally reconfigure copied files with user settings if needed
        self.log(f"    📝 SPI files ready for use")

    def copy_and_configure_i2c_files(self, microchip_plib_path, inc_base, src_base):
        """Copy and configure I2C files from Microchip installation"""
        self.log("  → Searching for I2C files...")

        # Create target directories
        i2c_inc_dir = os.path.join(inc_base, 'i2c')
        i2c_src_dir = os.path.join(src_base, 'i2c')
        os.makedirs(i2c_inc_dir, exist_ok=True)
        os.makedirs(i2c_src_dir, exist_ok=True)

        # Search for I2C files more broadly
        i2c_search_patterns = [
            '**/i2c*/plib_i2c1*',
            '**/i2c*/plib_i2c_common*',
            '**/*i2c1*',
            '**/plib_i2c1*',
            '**/plib_i2c_common*',
            '**/i2c**/*',
            '**/plib*i2c*'
        ]

        copied_files = []

        # Start from a broader search base if needed
        search_bases = [microchip_plib_path]
        # Also search parent directories in case we found a subdirectory
        if microchip_plib_path:
            parent_dir = os.path.dirname(microchip_plib_path)
            grandparent_dir = os.path.dirname(parent_dir)
            search_bases.extend([parent_dir, grandparent_dir])

        for search_base in search_bases:
            if not os.path.exists(search_base):
                continue

            for pattern in i2c_search_patterns:
                search_pattern = os.path.join(search_base, pattern)

                try:
                    for file_path in glob.glob(search_pattern, recursive=True):
                        if os.path.isfile(file_path):
                            file_name = os.path.basename(file_path)
                            file_ext = os.path.splitext(file_name)[1]

                            # Determine target directory based on file extension
                            if file_ext in ['.h']:
                                target_dir = i2c_inc_dir
                            elif file_ext in ['.c']:
                                target_dir = i2c_src_dir
                            else:
                                continue

                            target_path = os.path.join(target_dir, file_name)

                            # Copy file if not already copied
                            if target_path not in copied_files:
                                try:
                                    shutil.copy2(file_path, target_path)
                                    copied_files.append(target_path)
                                    self.log(f"    ✓ Copied {file_name}")
                                except Exception as e:
                                    self.log(
                                        f"    ⚠ Error copying {file_name}: {str(e)}")
                except Exception as e:
                    self.log(
                        f"    ⚠ Error searching pattern {pattern}: {str(e)}")

        if not copied_files:
            self.log(
                "    ⚠ No Microchip I2C files found, generating custom files...")
            # Generate our own I2C files if none found
            self.generate_i2c_files(inc_base, src_base)
            return

        self.log(f"    ✅ Copied {len(copied_files)} I2C files")
        # Optionally reconfigure copied files with user settings if needed
        self.log(f"    📝 I2C files ready for use")

    def reconfigure_uart_files(self, uart_inc_dir, uart_src_dir, uart_num):
        """Reconfigure copied UART files with user settings"""
        self.log(f"    Reconfiguring UART{uart_num} with user settings...")

        # Get user configuration values
        baud_rate = self.uart_config['baud_rate'].get()
        data_bits = self.uart_config['data_bits'].get()
        parity = self.uart_config['parity'].get()
        stop_bits = self.uart_config['stop_bits'].get()

        # Find and modify configuration files
        config_files = []
        for file in os.listdir(uart_src_dir):
            if file.endswith('.c') and 'uart' in file.lower():
                config_files.append(os.path.join(uart_src_dir, file))

        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Apply user configurations (basic replacements)
                # This is a simplified approach - in practice you'd want more sophisticated parsing
                if 'Initialize' in content:
                    # Calculate BRG value for baud rate
                    try:
                        baud_val = int(baud_rate)
                        brg_value = int((80000000 / (16 * baud_val)) - 1)
                        content = content.replace(
                            '/*BRG_PLACEHOLDER*/', f'U{uart_num}BRG = {brg_value};  // {baud_rate} baud')
                    except:
                        pass

                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(content)

            except Exception as e:
                self.log(
                    f"    Warning: Could not reconfigure {config_file}: {e}")

    def reconfigure_clock_files(self, clock_inc_dir, clock_src_dir):
        """Reconfigure copied Clock files with user settings"""
        self.log("    Reconfiguring Clock system with user settings...")

        # Get user clock configuration
        system_freq = self.clock_config['system_freq'].get()
        pll_enabled = self.clock_config['pll_enabled'].get()

        # Find and modify configuration files
        config_files = []
        for file in os.listdir(clock_src_dir):
            if file.endswith('.c') and 'clk' in file.lower():
                config_files.append(os.path.join(clock_src_dir, file))

        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Apply basic clock configurations
                # Add configuration comments
                clock_comment = f'''/*
 * User Clock Configuration:
 * System Frequency: {system_freq} MHz
 * PLL: {'Enabled' if pll_enabled else 'Disabled'}
 */'''

                if 'CLK_Initialize' in content:
                    content = content.replace('void CLK_Initialize(void)',
                                              f'{clock_comment}\nvoid CLK_Initialize(void)')

                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(content)

            except Exception as e:
                self.log(
                    f"    Warning: Could not reconfigure {config_file}: {e}")

    def copy_harmony3_peripheral_templates(self, harmony_peripheral_path, target_inc_dir, target_src_dir, peripheral_type):
        """Copy Harmony 3 peripheral template files and process them"""
        # Map peripheral types to their corresponding Harmony directory patterns
        harmony_peripheral_map = {
            'uart': ['uart_00734', 'uart_02478', 'uart_03076', 'uart_39', 'uart_6418'],
            'tmr': ['tmr_00745', 'tmr_02815', 'tmr1_00687', 'tmr1_02141'],
            'gpio': ['gpio_01166', 'gpio_01618', 'gpio_02467', 'gpio_02922', 'gpio_04928', 'gpio_26'],
            'clk': ['clk_pic32mz'],
            'i2c': ['i2c_00774', 'i2c_01441', 'i2c_05155'],
            'spi': ['spi_00753', 'spi_01329', 'spi_01482', 'spi_6088']
        }

        if peripheral_type not in harmony_peripheral_map:
            self.log(f"    ⚠️ Unknown peripheral type: {peripheral_type}")
            return False

        # Find the appropriate peripheral directory
        peripheral_dirs = harmony_peripheral_map[peripheral_type]
        found_peripheral_dir = None

        for periph_dir in peripheral_dirs:
            periph_path = os.path.join(harmony_peripheral_path, periph_dir)
            if os.path.exists(periph_path):
                found_peripheral_dir = periph_path
                self.log(
                    f"    ✅ Found {peripheral_type} peripheral: {periph_dir}")
                break

        if not found_peripheral_dir:
            self.log(f"    ❌ No {peripheral_type} peripheral directory found")
            return False

        # Copy template files
        templates_dir = os.path.join(found_peripheral_dir, 'templates')
        if not os.path.exists(templates_dir):
            self.log(
                f"    ❌ No templates directory found in {found_peripheral_dir}")
            return False

        try:
            # Copy .ftl template files and process them
            for file_name in os.listdir(templates_dir):
                if file_name.endswith(('.ftl', '.h', '.c')):
                    source_file = os.path.join(templates_dir, file_name)

                    # Determine target file name (remove .ftl extension if present)
                    target_name = file_name.replace('.ftl', '')

                    # Determine target directory (header or source)
                    if target_name.endswith('.h'):
                        target_file = os.path.join(target_inc_dir, target_name)
                    elif target_name.endswith('.c'):
                        target_file = os.path.join(target_src_dir, target_name)
                    else:
                        continue

                    # Copy and process the file
                    self.process_harmony3_template_file(
                        source_file, target_file, peripheral_type)
                    self.log(f"      → Processed: {target_name}")

            return True

        except Exception as e:
            self.log(
                f"    ❌ Error copying {peripheral_type} templates: {str(e)}")
            return False

    def process_harmony3_template_file(self, source_file, target_file, peripheral_type):
        """Process a Harmony 3 template file and substitute placeholders"""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic template processing (simplified FreeMarker-like processing)
            content = self.substitute_harmony3_placeholders(
                content, peripheral_type)

            # Ensure target directory exists
            os.makedirs(os.path.dirname(target_file), exist_ok=True)

            # Write processed content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            self.log(
                f"    ⚠️ Error processing template {source_file}: {str(e)}")
            # Fallback: just copy the file as-is
            try:
                import shutil
                shutil.copy2(source_file, target_file)
            except:
                pass

    def substitute_harmony3_placeholders(self, content, peripheral_type):
        """Substitute Harmony 3 template placeholders with actual values"""
        # Common substitutions for all peripherals
        substitutions = {
            # System configuration
            '${SYS_CLK_FREQ}': '80000000',  # 80MHz system clock
            '${PERIPHERAL_CLK}': '80000000',  # 80MHz peripheral clock
            '${.vars}': '',  # Remove template variable declarations

            # Device-specific
            '${__PROCESSOR}': 'PIC32MZ1024EFH064',
            '${core.DEVICE_FAMILY}': 'PIC32MZ',
            '${core.DEVICE_SERIES}': 'PIC32MZEF',
        }

        # Add peripheral-specific substitutions
        if peripheral_type == 'uart':
            uart_module = self.uart_config['uart_module'].get()
            uart_num = uart_module[-1]
            baud_rate = self.uart_config['baud_rate'].get()

            # Calculate BRG value for given baud rate (simplified)
            try:
                pbclk_freq = 80000000  # 80MHz
                brg_value = int((pbclk_freq / (16 * int(baud_rate))) - 1)
            except:
                brg_value = 42  # Default for 115200 at 80MHz

            uart_substitutions = {
                '${UART_INSTANCE_NUM}': uart_num,
                '${UART_INSTANCE_NAME}': uart_module,
                '${UART_INSTANCE_NAME?lower_case}': uart_module.lower(),
                '${UART_INSTANCE_NAME?upper_case}': uart_module.upper(),
                '${USART_BAUD_RATE}': baud_rate,
                '${BRG_VALUE}': str(brg_value),
                '${UART_DATA_BITS}': self.uart_config['data_bits'].get(),
                '${UART_PARITY}': self.uart_config['parity'].get().upper(),
                '${UART_STOP_BITS}': self.uart_config['stop_bits'].get(),
                '${UART_RX_INT_ENABLE}': str(self.uart_config['rx_interrupt'].get()).lower(),
                '${UART_TX_INT_ENABLE}': str(self.uart_config['tx_interrupt'].get()).lower(),
            }
            substitutions.update(uart_substitutions)

        elif peripheral_type == 'tmr':
            timer_module = self.timer_config['timer_module'].get()
            timer_num = timer_module[-1]
            prescaler_map = {'1:1': '0', '1:8': '1', '1:64': '2', '1:256': '3'}
            prescaler_val = prescaler_map.get(
                self.timer_config['prescaler'].get(), '0')

            # Calculate period register value
            freq = float(self.timer_config['frequency'].get() or '1000')
            pbclk_freq = 80000000
            prescaler_div = {'0': 1, '1': 8, '2': 64, '3': 256}[prescaler_val]
            period_reg = int((pbclk_freq / (prescaler_div * freq)) - 1)

            timer_substitutions = {
                '${TMR_INSTANCE_NUM}': timer_num,
                '${TMR_INSTANCE_NAME}': timer_module,
                '${TMR_INSTANCE_NAME?lower_case}': timer_module.lower(),
                '${TMR_INSTANCE_NAME?upper_case}': timer_module.upper(),
                '${TIMER_PRESCALER}': prescaler_val,
                '${TIMER_PERIOD_MS}': self.timer_config['period_ms'].get(),
                '${TIMER_FREQ}': self.timer_config['frequency'].get(),
                '${TIMER_PERIOD_REG}': str(period_reg),
                '${TIMER_INT_ENABLE}': str(self.timer_config['interrupt_enabled'].get()).lower(),
                '${TIMER_INT_PRIORITY}': self.timer_config['interrupt_priority'].get(),
            }
            substitutions.update(timer_substitutions)

        elif peripheral_type == 'gpio':
            gpio_substitutions = {
                '${GPIO_INSTANCE_NAME}': 'GPIO',
                '${PORT_GROUP_0}': 'A',
                '${PORT_GROUP_1}': 'B',
                '${PORT_GROUP_2}': 'C',
            }
            substitutions.update(gpio_substitutions)

        elif peripheral_type == 'clk':
            clk_substitutions = {
                '${CLK_INSTANCE_NAME}': 'CLK',
                '${SYSCLK_FREQ}': '80000000',
                '${PBCLK_FREQ}': '80000000',
            }
            substitutions.update(clk_substitutions)

        elif peripheral_type == 'i2c':
            i2c_substitutions = {
                '${I2C_INSTANCE_NUM}': '1',
                '${I2C_INSTANCE_NAME}': 'I2C1',
                '${I2C_INSTANCE_NAME?lower_case}': 'i2c1',
                '${I2C_CLOCK_SPEED}': '100000',  # 100kHz default
            }
            substitutions.update(i2c_substitutions)

        elif peripheral_type == 'spi':
            spi_substitutions = {
                '${SPI_INSTANCE_NUM}': '1',
                '${SPI_INSTANCE_NAME}': 'SPI1',
                '${SPI_INSTANCE_NAME?lower_case}': 'spi1',
                '${SPI_CLOCK_SPEED}': '1000000',  # 1MHz default
            }
            substitutions.update(spi_substitutions)

        # Apply substitutions (multiple passes for nested substitutions)
        for _ in range(3):  # Up to 3 passes to resolve nested references
            for placeholder, value in substitutions.items():
                content = content.replace(placeholder, value)

        # Remove FreeMarker template directives (improved cleanup)
        import re

        # Remove <#-- comments -->
        content = re.sub(r'<#--.*?-->', '', content, flags=re.DOTALL)

        # Remove conditional blocks <#if...></#if>
        content = re.sub(r'<#if[^>]*>.*?</#if>', '', content, flags=re.DOTALL)

        # Remove list blocks <#list...></#list>
        content = re.sub(r'<#list[^>]*>.*?</#list>',
                         '', content, flags=re.DOTALL)

        # Remove variable assignments <#assign...>
        content = re.sub(r'<#assign[^>]*>', '', content)

        # Remove include directives <#include...>
        content = re.sub(r'<#include[^>]*>', '', content)

        # Remove other FreeMarker directives
        content = re.sub(r'<#[^>]*>', '', content)

        # Clean up remaining ${...} placeholders that weren't substituted
        content = re.sub(r'\$\{[^}]+\}', '', content)

        # Clean up extra whitespace and blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)

        return content

    def generate_system_files(self, project_path, project_name):
        """Generate system files (definitions.h, device.h, etc.)"""
        self.log("  → Creating system files...")

        # definitions.h
        includes = []
        if self.config['uart_enabled'].get():
            uart_module = self.uart_config['uart_module'].get()
            # Extract number from UART1, UART2, etc.
            uart_num = uart_module[-1]
            includes.append(
                f'#include "peripheral/uart/plib_uart{uart_num}.h"')
        if self.config['timer_enabled'].get():
            includes.append('#include "peripheral/tmr1/plib_tmr1.h"')
        if self.config['gpio_enabled'].get():
            includes.append('#include "peripheral/gpio/plib_gpio.h"')
        if self.config['clock_enabled'].get():
            includes.append('#include "peripheral/clk/plib_clk.h"')

        definitions_content = f'''/*******************************************************************************
  System Definitions

  File Name:
    definitions.h

  Summary:
    Project system definitions.

  Description:
    This file contains the system-wide inclusions and definitions for {project_name}.
*******************************************************************************/

#ifndef DEFINITIONS_H
#define DEFINITIONS_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

// System initialization
void SYS_Initialize(void *data);

// Peripheral includes
{chr(10).join(includes)}

#ifdef __cplusplus
extern "C" {{
#endif

// System APIs would go here

#ifdef __cplusplus
}}
#endif

#endif /* DEFINITIONS_H */
'''

        # device.h
        device_content = f'''/*******************************************************************************
  Device Header

  File Name:
    device.h

  Summary:
    Device specific definitions and includes.

  Description:
    This file contains device-specific definitions for {self.config['device'].get()}.
*******************************************************************************/

#ifndef DEVICE_H
#define DEVICE_H

// Include XC32 compiler headers
#include <xc.h>
#include <sys/attribs.h>

// Device: {self.config['device'].get()}
#define DEVICE_FAMILY_PIC32MZ

// Configuration bits would typically go here
// #pragma config statements for device configuration

#ifdef __cplusplus
extern "C" {{
#endif

// Device-specific definitions and macros

#ifdef __cplusplus
}}
#endif

#endif /* DEVICE_H */
'''

        # initialization.c - system initialization
        init_content = f'''/*******************************************************************************
  System Initialization File

  File Name:
    initialization.c

  Summary:
    This file initializes all system components.

  Description:
    This file contains the "SYS_Initialize" function.
*******************************************************************************/

#include "definitions.h"

void SYS_Initialize(void *data)
{{
    /* Initialize all enabled peripherals */

{f"    CLK_Initialize();" if self.config['clock_enabled'].get() else ""}
{f"    GPIO_Initialize();" if self.config['gpio_enabled'].get() else ""}
{f"    TMR1_Initialize();" if self.config['timer_enabled'].get() else ""}
{f"    UART{self.uart_config['uart_module'].get()[-1]}_Initialize();" if self.config['uart_enabled'].get() else ""}

    /* Enable global interrupts */
    __builtin_enable_interrupts();
}}
'''

        # interrupts.c - interrupt handlers
        interrupts_content = '''/*******************************************************************************
  System Interrupts File

  File Name:
    interrupts.c

  Summary:
    Interrupt handlers for all system interrupts.

  Description:
    This file contains interrupt handlers for all enabled peripherals.
*******************************************************************************/

#include "definitions.h"

/* Timer1 interrupt handler */
void __ISR(_TIMER_1_VECTOR, ipl4SRS) TIMER_1_Handler(void)
{
    // Clear interrupt flag handled in TMR1_InterruptHandler
    TMR1_InterruptHandler();
}

/* Add other interrupt handlers as needed */
'''

        # exceptions.c - exception handlers
        exceptions_content = '''/*******************************************************************************
  System Exceptions File

  File Name:
    exceptions.c

  Summary:
    Exception handlers for system exceptions.

  Description:
    This file contains exception handlers.
*******************************************************************************/

#include "definitions.h"

/* General Exception Handler */
void _general_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}

/* Simple TLB Refill Handler */
void _simple_tlb_refill_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}

/* Cache Error Exception Handler */
void _cache_err_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}
'''

        # Write system files
        with open(os.path.join(project_path, 'incs', 'definitions.h'), 'w', encoding='utf-8') as f:
            f.write(definitions_content)
        with open(os.path.join(project_path, 'incs', 'device.h'), 'w', encoding='utf-8') as f:
            f.write(device_content)
        with open(os.path.join(project_path, 'srcs', 'initialization.c'), 'w', encoding='utf-8') as f:
            f.write(init_content)
        with open(os.path.join(project_path, 'srcs', 'interrupts.c'), 'w', encoding='utf-8') as f:
            f.write(interrupts_content)
        with open(os.path.join(project_path, 'srcs', 'exceptions.c'), 'w', encoding='utf-8') as f:
            f.write(exceptions_content)

    def create_root_makefile(self, project_path, project_name, device):
        """Create root Makefile - similar to your existing one"""
        makefile_content = f'''# Name of the project binary
MODULE := {project_name}

# Device configuration
DEVICE := {device}

# Cross-platform compiler and DFP paths
ifeq ($(OS),Windows_NT)
    COMPILER_LOCATION := C:/Program Files/Microchip/xc32/v4.60/bin
    DFP_LOCATION := C:/Program Files/Microchip/MPLABX/v6.25/packs
else
    COMPILER_LOCATION := /opt/microchip/xc32/v4.60/bin
    DFP_LOCATION := /opt/microchip/mplabx/v6.25/packs
endif
DFP := $(DFP_LOCATION)/Microchip/PIC32MZ-EF_DFP/1.4.168

# Build system
BUILD=make
CLEAN=make clean
BUILD_DIR=make build_dir

all:
	@echo "######  BUILDING {project_name.upper()} FOR {device.upper()}   ########"
	cd srcs && $(BUILD) COMPILER_LOCATION="$(COMPILER_LOCATION)" DFP_LOCATION="$(DFP_LOCATION)" DFP="$(DFP)" DEVICE=$(DEVICE) MODULE=$(MODULE)
	@echo "###### BIN TO HEX ########"
	cd bins && "$(COMPILER_LOCATION)/xc32-bin2hex" $(MODULE)
	@echo "######  BUILD COMPLETE   ########"

build_dir:
	@echo "#######BUILDING DIRECTORIES FOR OUTPUT BINARIES#######"
	cd srcs && $(BUILD_DIR)

clean:
	@echo "####### CLEANING OUTPUTS #######"
	cd srcs && $(CLEAN)

.PHONY: all build_dir clean
'''

        with open(os.path.join(project_path, 'Makefile'), 'w', encoding='utf-8') as f:
            f.write(makefile_content)

    def create_srcs_makefile(self, project_path, mikroc):
        """Create srcs/Makefile"""
        makefile_content = f'''# Makefile for {self.config['project_name'].get()} - Generated by PIC32MZ Project Builder
DFP_DIR := $(DFP)
DFP_INCLUDE := $(DFP)/include

# Source files (current directory and peripheral subdirectories)
SRCS := $(wildcard *.c) $(wildcard peripheral/*/*.c)
OBJS := $(SRCS:%.c=../objs/%.o)

{"# Assembly files in startup directory" if mikroc else ""}
{"ASM_SRCS := $(wildcard startup/*.S)" if mikroc else ""}
{"ASM_OBJS := $(ASM_SRCS:%.S=../objs/%.o)" if mikroc else ""}
{"OBJS += $(ASM_OBJS)" if mikroc else ""}

# Compiler and flags
CC := "$(COMPILER_LOCATION)/xc32-gcc"
MCU := -mprocessor=$(DEVICE)
FLAGS := -Werror -Wall -MP -MMD -g -O1 -ffunction-sections -fdata-sections -fno-common

# Include directories
INCS := -I"../incs" -I"$(DFP_INCLUDE)" -I"../incs/peripheral"

# Linker script
LINKER_SCRIPT := "$(DFP)/xc32/$(DEVICE)/p{self.config['device'].get()[:3].lower()}{self.config['device'].get()[3:]}.ld"

# Default target
../bins/$(MODULE): $(OBJS)
	@echo "Linking $(MODULE) for $(DEVICE)"
	$(CC) $(MCU) -nostartfiles -DXPRJ_default=default -mdfp="$(DFP)" -Wl,--script=$(LINKER_SCRIPT) -Wl,--defsym=__MPLAB_BUILD=1 -Wl,-Map="../other/$(MODULE).map" -o $@ $^

# Compile C source files
../objs/%.o: %.c
	@echo "Compiling $< to $@"
	@mkdir -p $(dir $@)
	$(CC) -x c -c $(MCU) $(FLAGS) $(INCS) -DXPRJ_default=default -mdfp="$(DFP)" -MF $(@:.o=.d) $< -o $@

# Compile assembly files
'''

        if mikroc:
            makefile_content += '''
../objs/%.o: %.S
	@echo "Compiling assembly $< to $@"
	@mkdir -p $(dir $@)
	$(CC) $(MCU) -c -DXPRJ_default=default -Wa,--defsym=__MPLAB_BUILD=1,--gdwarf-2 -mdfp="$(DFP)" -MMD -MF $(@:.o=.d) $< -o $@
'''

        makefile_content += '''
build_dir:
	@mkdir -p ../objs ../bins ../other ../objs/peripheral ../objs/startup

clean:
	@rm -rf ../objs/* ../bins/* ../other/*

.PHONY: build_dir clean
'''

        with open(os.path.join(project_path, 'srcs', 'Makefile'), 'w', encoding='utf-8') as f:
            f.write(makefile_content)

    def create_main_c(self, project_path, project_name):
        """Create main.c with enabled peripherals"""
        includes = ['#include "definitions.h"']

        callbacks = []
        main_loop = []
        init_code = []

        if self.config['timer_enabled'].get():
            callbacks.append('''
// Timer1 callback function
void timer_callback(uint32_t status, uintptr_t context)
{
    // Timer interrupt occurred - toggle LED2 if GPIO enabled
''' + ('#ifdef LED2_Toggle\n    LED2_Toggle();\n#endif' if self.config['gpio_enabled'].get() else '') + '''
}''')
            init_code.append(
                '    // Setup Timer1 callback\n    TMR1_CallbackRegister(timer_callback, 0);\n    TMR1_Start();')

        if self.config['uart_enabled'].get():
            init_code.append(
                '    // Send startup message via UART\n    UART2_Write((uint8_t*)"\\r\\nPIC32MZ Project Started!\\r\\n", 29);')
            main_loop.append('        // UART processing can be added here')

        if self.config['gpio_enabled'].get():
            main_loop.append(
                '        // LED1_Toggle(); // Uncomment to toggle LED1 in main loop')
            main_loop.append(
                '        // Simple delay\n        for(volatile int i = 0; i < 1000000; i++);')

        main_content = f'''/*******************************************************************************
  Main Source File - {project_name}

  Company:
    Your Company Name

  File Name:
    main.c

  Summary:
    This file contains the "main" function for {project_name}.

  Description:
    Generated by PIC32MZ Project Builder v1.0
    Device: {self.config['device'].get()}
    
    Enabled Peripherals:
    {"- UART2 (Serial Communication)" if self.config['uart_enabled'].get() else ""}
    {"- Timer1 (Periodic Interrupt)" if self.config['timer_enabled'].get() else ""}
    {"- GPIO (LED/Button Control)" if self.config['gpio_enabled'].get() else ""}
    {"- Clock System" if self.config['clock_enabled'].get() else ""}
*******************************************************************************/

#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdint.h>
{chr(10).join(includes)}

{''.join(callbacks)}

/*******************************************************************************
  Function:
    int main ( void )

  Summary:
    main function
*******************************************************************************/

int main(void)
{{
    /* Initialize all modules */
    SYS_Initialize(NULL);
    
{chr(10).join(init_code)}
    
    /* Main application loop */
    while (true)
    {{
        /* Maintain state machines of all polled MPLAB Harmony modules. */
{chr(10).join(main_loop) if main_loop else "        // Add your main application code here"}
    }}

    /* Execution should not come here during normal operation */
    return (EXIT_FAILURE);
}}
'''

        with open(os.path.join(project_path, 'srcs', 'main.c'), 'w', encoding='utf-8') as f:
            f.write(main_content)

    def create_startup_files(self, project_path):
        """Create startup.S file"""
        startup_content = '''/*******************************************************************************
  System Startup File

  File Name:
    startup.S

  Summary:
    System startup code for PIC32MZ microcontrollers.
    
  Description:
    This file contains the system startup code including vector table
    and initialization routines.
*******************************************************************************/

#include <xc.h>

    .section .vector_0,code, keep
    .equ __vector_spacing_0, 0x00000001
    .align 4
    .set nomips16
    .set noreorder
    .ent __vector_0
__vector_0:
    j  _startup
    nop
    .end __vector_0
    .size __vector_0, .-__vector_0

    .section .startup,code, keep
    .align 4
    .set nomips16  
    .set noreorder
    .ent _startup
_startup:
    /* Initialize stack pointer */
    la   $sp, _stack
    
    /* Initialize global pointer */
    la   $gp, _gp
    
    /* Jump to main */
    la   $t0, main
    jr   $t0
    nop
    .end _startup
    .size _startup, .-_startup
'''

        with open(os.path.join(project_path, 'srcs', 'startup', 'startup.S'), 'w', encoding='utf-8') as f:
            f.write(startup_content)

    def create_readme(self, project_path, project_name, device):
        """Create README.md"""
        enabled_peripherals = []
        if self.config['uart_enabled'].get():
            enabled_peripherals.append(
                "- **UART2**: Serial communication (115200 baud)")
        if self.config['timer_enabled'].get():
            enabled_peripherals.append(
                "- **Timer1**: Periodic interrupts (1ms)")
        if self.config['gpio_enabled'].get():
            enabled_peripherals.append("- **GPIO**: LED and button control")
        if self.config['clock_enabled'].get():
            enabled_peripherals.append(
                "- **Clock**: System clock configuration (80MHz)")
        if self.config['dma_enabled'].get():
            enabled_peripherals.append("- **DMA**: Direct memory access")
        if self.config['spi_enabled'].get():
            enabled_peripherals.append(
                "- **SPI**: Serial peripheral interface")
        if self.config['i2c_enabled'].get():
            enabled_peripherals.append("- **I2C**: Inter-integrated circuit")

        readme_content = f'''# {project_name}

PIC32MZ Embedded Project created with **PIC32MZ Project Builder v1.0**

## Project Details
- **Device**: {device}
- **Compiler**: XC32 v4.60+
- **Build System**: GNU Make
- **MikroC Support**: {"[YES] Enabled" if self.config['mikroc_support'].get() else "[NO] Disabled"}

## Enabled Peripherals
{chr(10).join(enabled_peripherals) if enabled_peripherals else "- Basic project template (no peripherals enabled)"}

## Project Structure
```
{project_name}/
├── srcs/           # Source files
│   ├── main.c      # Main application
│   ├── initialization.c
│   ├── interrupts.c
│   ├── exceptions.c
│   ├── peripheral/ # Peripheral library sources
{"│   └── startup/   # Startup assembly files" if self.config['mikroc_support'].get() else ""}
├── incs/           # Header files
│   ├── definitions.h
│   ├── device.h
│   └── peripheral/ # Peripheral library headers
├── objs/           # Object files (generated)
├── bins/           # Binary output (generated)
├── other/          # Map files, etc. (generated)
├── docs/           # Documentation
├── Makefile        # Root build file
└── README.md       # This file
```

## Building the Project

### Prerequisites
- XC32 Compiler v4.60 or later
- MPLAB X IDE v6.25 or later (for DFP)
- GNU Make

### Build Commands
```bash
# Create build directories
make build_dir

# Build the project
make

# Clean build outputs
make clean
```

### Build Output
- **Binary**: `bins/{project_name}`
- **Hex File**: `bins/{project_name}.hex`
- **Map File**: `other/{project_name}.map`

## Hardware Configuration
This project is configured for the **PIC32MZ Clicker** board with the following pinout:

{"### LEDs" if self.config['gpio_enabled'].get() else ""}
{"- **LED1**: RB8" if self.config['gpio_enabled'].get() else ""}
{"- **LED2**: RB9" if self.config['gpio_enabled'].get() else ""}

{"### Buttons" if self.config['gpio_enabled'].get() else ""}
{"- **BTN1**: RA6" if self.config['gpio_enabled'].get() else ""}
{"- **BTN2**: RA7" if self.config['gpio_enabled'].get() else ""}

{"### UART" if self.config['uart_enabled'].get() else ""}
{"- **UART2 TX**: RF5" if self.config['uart_enabled'].get() else ""}
{"- **UART2 RX**: RF4" if self.config['uart_enabled'].get() else ""}
{"- **Baud Rate**: 115200" if self.config['uart_enabled'].get() else ""}

## Usage

{"### UART Communication" if self.config['uart_enabled'].get() else ""}
{"Connect a serial terminal to the UART2 pins at 115200 baud to see startup messages." if self.config['uart_enabled'].get() else ""}

{"### LED Operation" if self.config['gpio_enabled'].get() else ""}
{"- LED1: Controlled in main loop (uncomment code to enable)" if self.config['gpio_enabled'].get() else ""}
{"- LED2: Toggles every 1ms via Timer1 interrupt" if self.config['timer_enabled'].get() and self.config['gpio_enabled'].get() else ""}

## Customization
- Modify `srcs/main.c` for your application logic
- Add peripheral configurations in respective plib files
- Adjust timing and interrupt priorities as needed

## Generated by
**PIC32MZ Project Builder v1.0**  
Created: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Support
For issues or questions about this generated project, refer to:
- [Microchip MPLAB Harmony Documentation](https://microchip-mplab-harmony.github.io/)
- [XC32 Compiler Documentation](https://www.microchip.com/en-us/tools-resources/develop/mplab-xc-compilers)
- [PIC32MZ Family Reference Manual](https://www.microchip.com/en-us/product/PIC32MZ1024EFH064)
'''

        with open(os.path.join(project_path, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def create_gitignore(self, project_path):
        """Create .gitignore"""
        gitignore_content = '''# Build outputs
objs/
bins/
other/
*.o
*.d
*.hex
*.elf
*.map
*.xml

# IDE files
*.X/
.generated_files/
nbproject/
.vs/
*.iml

# System files
.DS_Store
Thumbs.db
*~

# Logs
*.log

# Temporary files
*.tmp
*.temp
*.bak
*.swp
'''

        with open(os.path.join(project_path, '.gitignore'), 'w', encoding='utf-8') as f:
            f.write(gitignore_content)

    def create_project_config_file(self, project_path, project_name):
        """Create comprehensive project configuration JSON file"""
        import datetime

        # Collect all configuration data
        config_data = {
            "project_info": {
                "name": project_name,
                "device": self.config['device'].get(),
                "generated_date": datetime.datetime.now().isoformat(),
                "generator_version": "PIC32MZ Project Builder v1.0",
                "mikroc_support": self.config['mikroc_support'].get()
            },
            "project_configuration": {
                key: var.get() for key, var in self.config.items()
            },
            "uart_configuration": {
                key: var.get() for key, var in self.uart_config.items()
            },
            "clock_configuration": {
                key: var.get() for key, var in self.clock_config.items()
            },
            "enabled_peripherals": {
                "uart": self.config['uart_enabled'].get(),
                "timer": self.config['timer_enabled'].get(),
                "gpio": self.config['gpio_enabled'].get(),
                "clock": self.config['clock_enabled'].get(),
                "dma": self.config['dma_enabled'].get(),
                "spi": self.config['spi_enabled'].get(),
                "i2c": self.config['i2c_enabled'].get()
            },
            "peripheral_details": {
                "uart": {
                    "module": self.uart_config['uart_module'].get(),
                    "baud_rate": self.uart_config['baud_rate'].get(),
                    "data_bits": self.uart_config['data_bits'].get(),
                    "parity": self.uart_config['parity'].get(),
                    "stop_bits": self.uart_config['stop_bits'].get(),
                    "interrupts_enabled": {
                        "rx": self.uart_config['rx_interrupt'].get(),
                        "tx": self.uart_config['tx_interrupt'].get(),
                        "error": self.uart_config['error_interrupt'].get()
                    }
                },
                "clock": {
                    "primary_oscillator": self.clock_config['primary_osc'].get(),
                    "input_frequency_mhz": self.clock_config['input_freq'].get(),
                    "pll_enabled": self.clock_config['pll_enabled'].get(),
                    "system_frequency_mhz": self.clock_config['system_freq'].get(),
                    "peripheral_bus_clocks": {
                        f"pbclk{i}": {
                            "enabled": self.clock_config[f'pbclk{i}_enabled'].get(),
                            "divider": self.clock_config[f'pbclk{i}_div'].get()
                        } for i in range(1, 8)
                    }
                }
            },
            "build_information": {
                "compiler": "XC32 v4.60+",
                "build_system": "GNU Make",
                "target_architecture": "PIC32MZ",
                "configuration_notes": [
                    "This file contains the complete project configuration",
                    "It can be used to recreate the project with identical settings",
                    "Import this file using 'Load Template' in PIC32MZ Project Builder"
                ]
            }
        }

        config_filename = f"{project_name}_config.json"
        config_path = os.path.join(project_path, config_filename)

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.log(f"  → Created project configuration: {config_filename}")

        except Exception as e:
            self.log(f"Warning: Could not create config file: {e}")

    def open_project_directory(self, project_path):
        """Open project directory in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(project_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', project_path])
        except Exception as e:
            self.log(f"Could not open directory: {e}")

    def save_template(self):
        """Save current configuration as template"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Project Template"
        )

        if filename:
            # Create comprehensive configuration data
            import datetime

            config_data = {
                "project_info": {
                    "template_name": os.path.splitext(os.path.basename(filename))[0],
                    "created_date": datetime.datetime.now().isoformat(),
                    "generator_version": "PIC32MZ Project Builder v1.0"
                },
                "project_configuration": {
                    key: var.get() for key, var in self.config.items()
                },
                "uart_configuration": {
                    key: var.get() for key, var in self.uart_config.items()
                },
                "clock_configuration": {
                    key: var.get() for key, var in self.clock_config.items()
                },
                "template_notes": [
                    "This is a comprehensive project template",
                    "It includes all peripheral and clock configurations",
                    "Load this template to restore all settings exactly as saved"
                ]
            }

            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                self.log(
                    f"Comprehensive template saved: {os.path.basename(filename)}")
                messagebox.showinfo("Success", "Template saved successfully!")
            except Exception as e:
                self.log(f"Error saving template: {e}")
                messagebox.showerror("Error", f"Failed to save template: {e}")

    def load_template(self):
        """Load configuration from template"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Project Template"
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Handle comprehensive config format (new format)
                if 'project_configuration' in config_data:
                    self.log("Loading comprehensive project configuration...")

                    # Load basic project config
                    for key, value in config_data.get('project_configuration', {}).items():
                        if key in self.config:
                            self.config[key].set(value)

                    # Load UART configuration
                    for key, value in config_data.get('uart_configuration', {}).items():
                        if key in self.uart_config:
                            self.uart_config[key].set(value)

                    # Load clock configuration
                    for key, value in config_data.get('clock_configuration', {}).items():
                        if key in self.clock_config:
                            self.clock_config[key].set(value)

                    # Update clock summary after loading
                    self.update_clock_summary()

                    self.log(
                        f"Comprehensive template loaded: {os.path.basename(filename)}")

                # Handle legacy config format (old format)
                else:
                    self.log("Loading legacy project configuration...")
                    for key, value in config_data.items():
                        if key in self.config:
                            self.config[key].set(value)

                    self.log(
                        f"Legacy template loaded: {os.path.basename(filename)}")

                messagebox.showinfo("Success", "Template loaded successfully!")
            except Exception as e:
                self.log(f"Error loading template: {e}")
                messagebox.showerror("Error", f"Failed to load template: {e}")

    def load_templates(self):
        """Load available templates on startup"""
        self.log("Scanning for templates...")
        # Look for templates in the same directory
        try:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(app_dir, 'templates')
            if os.path.exists(templates_dir):
                templates = [f for f in os.listdir(
                    templates_dir) if f.endswith('.json')]
                if templates:
                    self.log(
                        f"Found {len(templates)} template(s): {', '.join(templates)}")
                else:
                    self.log("No templates found in templates/ directory")
            else:
                self.log("Templates directory not found - creating...")
                os.makedirs(templates_dir, exist_ok=True)
        except Exception as e:
            self.log(f"Error loading templates: {e}")


def main():
    root = tk.Tk()
    app = PIC32ProjectBuilderGUI(root)

    # Configure modern theme
    style = ttk.Style()
    if 'vista' in style.theme_names():
        style.theme_use('vista')
    elif 'clam' in style.theme_names():
        style.theme_use('clam')

    # Set window icon (if icon file exists)
    try:
        # Try to set an icon - you can add an icon file
        pass
    except:
        pass

    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
