#!/usr/bin/env python3
"""
PowerSage - Smart Battery Saver for Windows
Complete single-file implementation with system tray and instant toggle
"""

import os
import sys
import json
import time
import ctypes
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import pystray
from PIL import Image, ImageDraw
from plyer import notification
import keyboard
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('PowerSage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PowerSage:
    def __init__(self):
        self.config_file = "PowerSage_config.json"
        self.eco_mode_active = False
        self.tray_icon = None
        self.gui_window = None
        self.monitoring = True
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main root window
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        
        # Default configuration
        self.config = {
            "eco_threshold": 40,
            "restore_threshold": 80,
            "kill_apps": ["chrome.exe", "steam.exe", "discord.exe", "spotify.exe"],
            "disable_wifi": True,
            "disable_bluetooth": True,
            "reduce_brightness": True,
            "auto_eco_mode": True,
            "show_notifications": True
        }
        
        # Check admin privileges
        self.is_admin = self.check_admin_privileges()
        if not self.is_admin:
            logger.warning("Running without administrator privileges - some features may not work")
        
        self.load_config()
        self.setup_tray()
        self.setup_hotkey()
        self.start_monitoring()

    def check_admin_privileges(self):
        """Check if running with administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_icon_image(self, color="green"):
        """Create a simple icon for the tray"""
        image = Image.new('RGB', (64, 64), color="black")
        draw = ImageDraw.Draw(image)
        
        # Battery outline
        draw.rectangle([10, 20, 50, 50], outline=color, width=2)
        draw.rectangle([50, 28, 54, 42], fill=color)
        
        # Battery level indicator
        if self.eco_mode_active:
            draw.rectangle([12, 22, 48, 48], fill="orange")
            draw.text((15, 25), "ECO", fill="black")
        else:
            battery = psutil.sensors_battery()
            if battery:
                level = int(battery.percent / 100 * 36)
                draw.rectangle([12, 22, 12 + level, 48], fill=color)
        
        return image

    def setup_tray(self):
        """Setup system tray icon"""
        icon_image = self.create_icon_image()
        
        menu = pystray.Menu(
            pystray.MenuItem("Toggle Eco Mode", self.toggle_eco_mode),
            pystray.MenuItem("Battery Status", self.show_battery_status),
            pystray.MenuItem("Settings", self.show_gui),
            pystray.MenuItem("Kill Heavy Apps", self.kill_heavy_processes),
            pystray.MenuItem("Toggle WiFi", self.toggle_wifi),
            pystray.MenuItem("Toggle Bluetooth", self.toggle_bluetooth),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_application)
        )
        
        self.tray_icon = pystray.Icon("PowerSage", icon_image, "PowerSage Battery Saver", menu)

    def setup_hotkey(self):
        """Setup global hotkey for instant toggle (Ctrl+Alt+P)"""
        try:
            keyboard.add_hotkey('ctrl+alt+p', self.toggle_eco_mode)
            logger.info("Hotkey registered: Ctrl+Alt+P for instant toggle")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
                logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get_battery_info(self):
        """Get battery information"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': round(battery.percent),
                    'charging': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except Exception as e:
            logger.error(f"Failed to get battery info: {e}")
        return {'percent': 0, 'charging': False, 'time_left': None}

    def get_wifi_interface_name(self):
        """Dynamically detect WiFi interface name"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Name' in line and ':' in line:
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            logger.error(f"Failed to detect WiFi interface: {e}")
        return "Wi-Fi"  # Fallback

    def toggle_wifi(self):
        """Toggle WiFi on/off"""
        if not self.is_admin:
            self.notify("Admin privileges required for WiFi control")
            return
            
        try:
            interface_name = self.get_wifi_interface_name()
            # Try to disable first, then enable if it was already disabled
            result = subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'disabled'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.notify("WiFi disabled")
                logger.info("WiFi disabled")
                # Set up to re-enable after a short delay
                threading.Timer(1.0, self.enable_wifi).start()
            else:
                # Try to enable
                subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'], 
                             capture_output=True, text=True, timeout=10)
                self.notify("WiFi enabled")
                logger.info("WiFi enabled")
        except Exception as e:
            logger.error(f"Failed to toggle WiFi: {e}")
            self.notify("Failed to toggle WiFi")

    def enable_wifi(self):
        """Re-enable WiFi"""
        try:
            interface_name = self.get_wifi_interface_name()
            subprocess.run(['netsh', 'interface', 'set', 'interface', interface_name, 'enabled'], 
                         capture_output=True, text=True, timeout=10)
        except Exception as e:
            logger.error(f"Failed to re-enable WiFi: {e}")

    def toggle_bluetooth(self):
        """Toggle Bluetooth on/off"""
        if not self.is_admin:
            self.notify("Admin privileges required for Bluetooth control")
            return
            
        try:
            # More robust PowerShell command for Bluetooth
            ps_cmd = '''
            $bt = Get-PnpDevice | Where-Object {$_.FriendlyName -like "*Bluetooth*" -and $_.Status -eq "OK"}
            if ($bt) {
                if ($bt.Status -eq "OK") {
                    $bt | Disable-PnpDevice -Confirm:$false
                    Write-Output "Disabled"
                } else {
                    $bt | Enable-PnpDevice -Confirm:$false
                    Write-Output "Enabled"
                }
            }
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                self.notify(f"Bluetooth {output.lower()}")
                logger.info(f"Bluetooth {output.lower()}")
            else:
                logger.error(f"Bluetooth toggle failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to toggle Bluetooth: {e}")
            self.notify("Failed to toggle Bluetooth")

    def set_power_plan(self, plan_type="power_saver"):
        """Set Windows power plan"""
        try:
            if plan_type == "power_saver":
                # Power Saver GUID
                guid = "a1841308-3541-4fab-bc81-f71556f20b4a"
            else:
                # Balanced GUID
                guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
                
            result = subprocess.run(['powercfg', '/setactive', guid], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Power plan set to {plan_type}")
                return True
            else:
                logger.error(f"Failed to set power plan: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to set power plan: {e}")
        return False

    def adjust_brightness(self, reduce=True):
        """Adjust screen brightness"""
        try:
            if reduce:
                # Set brightness to 30%
                brightness = 30
            else:
                # Restore brightness to 80%
                brightness = 80
                
            subprocess.run(['powershell', '-Command', 
                          f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{brightness})'],
                         capture_output=True, text=True, timeout=10)
            logger.info(f"Brightness adjusted to {brightness}%")
            
        except Exception as e:
            logger.error(f"Failed to adjust brightness: {e}")

    def kill_heavy_processes(self):
        """Kill heavy/specified processes"""
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in [app.lower() for app in self.config['kill_apps']]:
                    proc.terminate()
                    killed_count += 1
                    logger.info(f"Terminated process: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.warning(f"Could not terminate {proc.info['name']}: {e}")
            except Exception as e:
                logger.error(f"Error terminating process: {e}")
                
        if killed_count > 0:
            self.notify(f"Terminated {killed_count} heavy processes")
        else:
            self.notify("No heavy processes found to terminate")

    def activate_eco_mode(self):
        """Activate eco mode with all optimizations"""
        logger.info("Activating Eco Mode")
        
        # Set power saver plan
        self.set_power_plan("power_saver")
        
        # Reduce brightness
        if self.config['reduce_brightness']:
            self.adjust_brightness(reduce=True)
        
        # Disable WiFi if configured
        if self.config['disable_wifi']:
            threading.Thread(target=self.toggle_wifi, daemon=True).start()
        
        # Disable Bluetooth if configured
        if self.config['disable_bluetooth']:
            threading.Thread(target=self.toggle_bluetooth, daemon=True).start()
        
        # Kill heavy processes
        threading.Thread(target=self.kill_heavy_processes, daemon=True).start()
        
        self.eco_mode_active = True
        self.update_tray_icon()
        
        if self.config['show_notifications']:
            battery_info = self.get_battery_info()
            self.notify(f"Eco Mode activated at {battery_info['percent']}% battery")

    def deactivate_eco_mode(self):
        """Deactivate eco mode and restore normal settings"""
        logger.info("Deactivating Eco Mode")
        
        # Set balanced power plan
        self.set_power_plan("balanced")
        
        # Restore brightness
        if self.config['reduce_brightness']:
            self.adjust_brightness(reduce=False)
        
        # Re-enable WiFi
        if self.config['disable_wifi']:
            threading.Thread(target=self.enable_wifi, daemon=True).start()
        
        self.eco_mode_active = False
        self.update_tray_icon()
        
        if self.config['show_notifications']:
            battery_info = self.get_battery_info()
            self.notify(f"Eco Mode deactivated at {battery_info['percent']}% battery")

    def toggle_eco_mode(self):
        """Toggle eco mode on/off"""
        if self.eco_mode_active:
            self.deactivate_eco_mode()
        else:
            self.activate_eco_mode()

    def update_tray_icon(self):
        """Update tray icon based on current state"""
        if self.tray_icon:
            color = "orange" if self.eco_mode_active else "green"
            self.tray_icon.icon = self.create_icon_image(color)

    def monitor_battery(self):
        """Monitor battery and auto-toggle eco mode"""
        while self.monitoring:
            try:
                battery_info = self.get_battery_info()
                
                if self.config['auto_eco_mode'] and not battery_info['charging']:
                    # Auto-enable eco mode when battery is low
                    if (battery_info['percent'] <= self.config['eco_threshold'] and 
                        not self.eco_mode_active):
                        self.activate_eco_mode()
                    
                    # Auto-disable eco mode when battery is sufficient or charging
                    elif (battery_info['percent'] >= self.config['restore_threshold'] and 
                          self.eco_mode_active):
                        self.deactivate_eco_mode()
                
                # Disable eco mode when plugged in
                if battery_info['charging'] and self.eco_mode_active:
                    self.deactivate_eco_mode()
                
                # Update tray icon periodically
                self.update_tray_icon()
                
            except Exception as e:
                logger.error(f"Error in battery monitoring: {e}")
            
            time.sleep(30)  # Check every 30 seconds

    def start_monitoring(self):
        """Start background battery monitoring"""
        monitor_thread = threading.Thread(target=self.monitor_battery, daemon=True)
        monitor_thread.start()

    def show_battery_status(self):
        """Show battery status notification"""
        battery_info = self.get_battery_info()
        status = "Charging" if battery_info['charging'] else "Discharging"
        eco_status = "ON" if self.eco_mode_active else "OFF"
        
        time_left = ""
        if battery_info['time_left']:
            hours = battery_info['time_left'] // 3600
            minutes = (battery_info['time_left'] % 3600) // 60
            time_left = f" ({hours}h {minutes}m left)"
        
        message = f"Battery: {battery_info['percent']}% - {status}{time_left}\nEco Mode: {eco_status}"
        self.notify("Battery Status", message)

    def notify(self, title, message=""):
        """Show desktop notification"""
        try:
            if not message:
                message = title
                title = "PowerSage"
            
            notification.notify(
                title=title,
                message=message,
                timeout=3
            )
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")

    def show_gui(self):
        """Show GUI settings window"""
        # Check if GUI window exists and is valid
        try:
            if hasattr(self, 'gui_window') and self.gui_window and self.gui_window.winfo_exists():
                self.gui_window.lift()
                self.gui_window.focus_force()
                return
        except tk.TclError:
            # Window was destroyed, reset reference
            self.gui_window = None
            
        # Create hidden root window if it doesn't exist
        # self.root = tk.Tk()
        # self.root.withdraw()  # Hide the main root window
        # self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        # Create new settings window
        self.gui_window = tk.Toplevel(self.root)
        self.gui_window.title("PowerSage Settings")
        self.gui_window.geometry("450x600")
        self.gui_window.configure(bg='#1E1E1E')
        self.gui_window.resizable(True, True)
        self.gui_window.minsize(400, 500)
        
        # Make sure window appears on top
        self.gui_window.lift()
        self.gui_window.focus_force()
        self.gui_window.grab_set()  # Make it modal
        
        # Handle window closing
        self.gui_window.protocol("WM_DELETE_WINDOW", self.close_gui)
        
        # Configure styles properly
        try:
            style = ttk.Style(self.gui_window)
            style.theme_use('clam')
            
            # Configure dark theme styles
            style.configure('Dark.TFrame', background='#1E1E1E')
            style.configure('Dark.TLabel', background='#1E1E1E', foreground='#00FFAA', font=('Arial', 10))
            style.configure('Dark.TCheckbutton', background='#1E1E1E', foreground='#00FFAA', focuscolor='none')
            style.configure('Dark.TButton', background='#2D2D2D', foreground='#00FFAA', font=('Arial', 9))
            style.configure('Dark.TEntry', background='#2D2D2D', foreground='#FFFFFF', fieldbackground='#2D2D2D')
            
        except Exception as e:
            logger.warning(f"Style configuration failed: {e}")
        
        # Create scrollable main frame
        canvas = tk.Canvas(self.gui_window, bg='#1E1E1E', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.gui_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Dark.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = ttk.Label(scrollable_frame, text="⚡ PowerSage Settings", 
                               style='Dark.TLabel', font=('Arial', 16, 'bold'))
        title_label.pack(pady=(10, 20))
        
        # Status frame
        status_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame', relief='solid', borderwidth=1)
        status_frame.pack(fill='x', pady=(0, 20), padx=10)
        
        # Battery status
        battery_info = self.get_battery_info()
        status_text = f"🔋 Battery: {battery_info['percent']}% - {'⚡ Charging' if battery_info['charging'] else '🔌 Discharging'}"
        status_label = ttk.Label(status_frame, text=status_text, style='Dark.TLabel', font=('Arial', 11))
        status_label.pack(pady=10)
        
        # Eco mode status
        eco_text = f"💡 Eco Mode: {'🟢 ACTIVE' if self.eco_mode_active else '⭕ INACTIVE'}"
        eco_status = ttk.Label(status_frame, text=eco_text, 
                              style='Dark.TLabel', font=('Arial', 12, 'bold'))
        eco_status.pack(pady=(0, 10))
        
        # Settings section
        settings_label = ttk.Label(scrollable_frame, text="⚙️ Configuration", 
                                 style='Dark.TLabel', font=('Arial', 14, 'bold'))
        settings_label.pack(pady=(10, 15))
        
        # Threshold settings frame
        threshold_frame = ttk.LabelFrame(scrollable_frame, text="Battery Thresholds", style='Dark.TFrame')
        threshold_frame.pack(fill='x', pady=(0, 15), padx=10)
        
        # Store variables as instance variables to prevent garbage collection
        self.eco_threshold_var = tk.StringVar(value=str(self.config['eco_threshold']))
        self.restore_threshold_var = tk.StringVar(value=str(self.config['restore_threshold']))
        
        threshold_inner = ttk.Frame(threshold_frame, style='Dark.TFrame')
        threshold_inner.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(threshold_inner, text="Activate Eco Mode at (%):", style='Dark.TLabel').grid(row=0, column=0, sticky='w', pady=2)
        threshold_entry = ttk.Entry(threshold_inner, textvariable=self.eco_threshold_var, width=8, style='Dark.TEntry')
        threshold_entry.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(threshold_inner, text="Deactivate Eco Mode at (%):", style='Dark.TLabel').grid(row=1, column=0, sticky='w', pady=2)
        restore_entry = ttk.Entry(threshold_inner, textvariable=self.restore_threshold_var, width=8, style='Dark.TEntry')
        restore_entry.grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Feature toggles
        features_label = ttk.Label(scrollable_frame, text="🔧 Eco Mode Features", 
                                 style='Dark.TLabel', font=('Arial', 12, 'bold'))
        features_label.pack(pady=(20, 10))
        
        # Store checkbox variables as instance variables
        self.auto_eco_var = tk.BooleanVar(value=self.config['auto_eco_mode'])
        self.disable_wifi_var = tk.BooleanVar(value=self.config['disable_wifi'])
        self.disable_bt_var = tk.BooleanVar(value=self.config['disable_bluetooth'])
        self.reduce_bright_var = tk.BooleanVar(value=self.config['reduce_brightness'])
        self.show_notif_var = tk.BooleanVar(value=self.config['show_notifications'])
        
        checkbox_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame')
        checkbox_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Checkbutton(checkbox_frame, text="🤖 Auto Eco Mode (based on battery %)", 
                       variable=self.auto_eco_var, style='Dark.TCheckbutton').pack(anchor='w', pady=2)
        ttk.Checkbutton(checkbox_frame, text="📶 Disable WiFi in Eco Mode", 
                       variable=self.disable_wifi_var, style='Dark.TCheckbutton').pack(anchor='w', pady=2)
        ttk.Checkbutton(checkbox_frame, text="📡 Disable Bluetooth in Eco Mode", 
                       variable=self.disable_bt_var, style='Dark.TCheckbutton').pack(anchor='w', pady=2)
        ttk.Checkbutton(checkbox_frame, text="🔆 Reduce Screen Brightness", 
                       variable=self.reduce_bright_var, style='Dark.TCheckbutton').pack(anchor='w', pady=2)
        ttk.Checkbutton(checkbox_frame, text="🔔 Show Desktop Notifications", 
                       variable=self.show_notif_var, style='Dark.TCheckbutton').pack(anchor='w', pady=2)
        
        # Action buttons frame
        button_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame')
        button_frame.pack(fill='x', pady=(20, 10), padx=10)
        
        def save_settings():
            try:
                eco_val = int(self.eco_threshold_var.get())
                restore_val = int(self.restore_threshold_var.get())
                
                if not (1 <= eco_val <= 99) or not (1 <= restore_val <= 99):
                    raise ValueError("Thresholds must be between 1-99")
                if eco_val >= restore_val:
                    raise ValueError("Eco threshold must be less than restore threshold")
                    
                self.config['eco_threshold'] = eco_val
                self.config['restore_threshold'] = restore_val
                self.config['auto_eco_mode'] = self.auto_eco_var.get()
                self.config['disable_wifi'] = self.disable_wifi_var.get()
                self.config['disable_bluetooth'] = self.disable_bt_var.get()
                self.config['reduce_brightness'] = self.reduce_bright_var.get()
                self.config['show_notifications'] = self.show_notif_var.get()
                
                self.save_config()
                messagebox.showinfo("✅ Success", "Settings saved successfully!", parent=self.gui_window)
                
            except ValueError as e:
                messagebox.showerror("❌ Error", f"Invalid input: {str(e)}", parent=self.gui_window)
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to save settings: {str(e)}", parent=self.gui_window)
        
        def refresh_status():
            try:
                battery_info = self.get_battery_info()
                status_text = f"🔋 Battery: {battery_info['percent']}% - {'⚡ Charging' if battery_info['charging'] else '🔌 Discharging'}"
                status_label.config(text=status_text)
                
                eco_text = f"💡 Eco Mode: {'🟢 ACTIVE' if self.eco_mode_active else '⭕ INACTIVE'}"
                eco_status.config(text=eco_text)
            except Exception as e:
                logger.error(f"Failed to refresh status: {e}")
        
        # Button grid
        btn_row1 = ttk.Frame(button_frame, style='Dark.TFrame')
        btn_row1.pack(fill='x', pady=2)
        
        ttk.Button(btn_row1, text="💾 Save Settings", command=save_settings, style='Dark.TButton').pack(side='left', padx=2)
        ttk.Button(btn_row1, text="🔄 Refresh Status", command=refresh_status, style='Dark.TButton').pack(side='left', padx=2)
        ttk.Button(btn_row1, text="⚡ Toggle Eco Mode", command=self.toggle_eco_mode, style='Dark.TButton').pack(side='left', padx=2)
        
        btn_row2 = ttk.Frame(button_frame, style='Dark.TFrame')
        btn_row2.pack(fill='x', pady=2)
        
        ttk.Button(btn_row2, text="🔪 Kill Heavy Apps", command=self.kill_heavy_processes, style='Dark.TButton').pack(side='left', padx=2)
        ttk.Button(btn_row2, text="📶 Toggle WiFi", command=self.toggle_wifi, style='Dark.TButton').pack(side='left', padx=2)
        ttk.Button(btn_row2, text="📡 Toggle Bluetooth", command=self.toggle_bluetooth, style='Dark.TButton').pack(side='left', padx=2)
        
        # Info section
        info_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame')
        info_frame.pack(fill='x', pady=(20, 10), padx=10)
        
        info_label = ttk.Label(info_frame, text="ℹ️ Hotkey: Ctrl+Alt+P for instant toggle", 
                             style='Dark.TLabel', font=('Arial', 10, 'italic'))
        info_label.pack()
        
        # Admin warning
        if not self.is_admin:
            warning_frame = ttk.Frame(scrollable_frame, style='Dark.TFrame')
            warning_frame.pack(fill='x', pady=(10, 20), padx=10)
            
            warning_label = ttk.Label(warning_frame, text="⚠️ Administrator privileges required for full functionality\n(WiFi, Bluetooth, Process management)", 
                                    style='Dark.TLabel', foreground='#FF6B6B', font=('Arial', 9))
            warning_label.pack()
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def close_gui(self):
        """Properly close the GUI window"""
        try:
            if hasattr(self, 'gui_window') and self.gui_window:
                self.gui_window.grab_release()
                self.gui_window.destroy()
                self.gui_window = None
        except Exception as e:
            logger.error(f"Error closing GUI: {e}")
    
    def on_root_close(self):
        """Handle root window close event"""
        try:
            self.close_gui()
        except Exception as e:
            logger.error(f"Error handling root close: {e}")

    def quit_application(self):
        """Quit the application"""
        self.monitoring = False
        try:
            if hasattr(self, 'gui_window') and self.gui_window:
                self.gui_window.grab_release()
                self.gui_window.destroy()
                self.gui_window = None
        except:
            pass
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        
        if hasattr(self, 'root') and self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error destroying root window: {e}")

    def run(self):
        """Run the application"""
        logger.info("PowerSage started")
        logger.info(f"Administrator privileges: {self.is_admin}")
        logger.info("Use Ctrl+Alt+P for instant eco mode toggle")
        
        if self.tray_icon:
            # Run the tray icon in a separate thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            # Start the Tkinter main loop in the main thread
            self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = PowerSage()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting PowerSage...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
