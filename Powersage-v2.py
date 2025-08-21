# ⚡ PowerWhisper - Intelligent Battery Saver and System Optimizer for Windows
# A single-file Python utility with a professional UI and smart process management.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import json
import os
import subprocess
import logging
import ctypes
import sys
from datetime import datetime, timedelta

# --- Smart Kill List ---
# A predefined list of common non-essential, resource-heavy background processes.
# These are generally safe to terminate to save power.
SMART_KILL_LIST = [
    # Communication & Social
    "Discord.exe", "Teams.exe", "slack.exe", "Zoom.exe",
    # Game Launchers & Overlays
    "Steam.exe", "steamwebhelper.exe", "EpicGamesLauncher.exe", "UbisoftGameLauncher.exe",
    "Battle.net.exe", "Origin.exe", "RiotClientServices.exe", "GOG.exe", "GalaxyClient.exe",
    # Media Players
    "Spotify.exe", "iTunes.exe", "Music.UI.exe",
    # Cloud Sync & Updaters
    "OneDrive.exe", "AdobeUpdateService.exe", "Creative Cloud.exe",
    # Other Common Background Apps
    "Cortana.exe", "YourPhone.exe", "GameBar.exe", "NVIDIA GeForce Overlay.exe"
]

# Common non-essential Windows Services (service_name: display_name)
WINDOWS_SERVICES = {
    "Spooler": "Print Spooler",
    "Fax": "Fax",
    "TabletInputService": "Tablet Input Service",
    "DiagTrack": "Connected Devices Platform User Service",
    "SysMain": "Superfetch/SysMain",
    "DoSvc": "Delivery Optimization",
    "PcaSvc": "Program Compatibility Assistant Service",
    "XboxGipSvc": "Xbox Accessory Management Service",
    "XblGameSave": "Xbox Live Game Save",
    "CDPUserSvc": "Connected Devices Platform User Service", # This is a dynamic service, might need careful handling
    "WSearch": "Windows Search",
    "Themes": "Themes"
}


# Import third-party libraries
try:
    import psutil
    import pystray
    from PIL import Image, ImageDraw
    from plyer import notification
    import keyboard
except ImportError as e:
    root = tk.Tk()
    root.withdraw()
    missing_module = str(e).split("'")[1]
    messagebox.showerror(
        "Dependency Error",
        f"Required module '{missing_module}' is not installed.\n\n"
        f"Please install it by running:\n"
        f"pip install psutil pystray pillow plyer keyboard\n\n"
        "The application will now exit."
    )
    sys.exit(1)

# --- Constants and Configuration ---
CONFIG_FILE = "powerwhisper_config.json"
CONFIG_BACKUP_FILE = "powerwhisper_config_backup.json"
LOG_FILE = "powerwhisper.log"
BATTERY_HISTORY_FILE = "powerwhisper_battery_history.json"
APP_NAME = "PowerWhisper"
POLL_INTERVAL_SECONDS = 15 # Reduced for more responsive monitoring

# --- Logging Setup ---
# Configure logging to write to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler()
    ]
)

# --- Helper Functions ---
def is_admin():
    """Checks if the application is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def create_tray_icon(primary_color, secondary_color):
    """Generates an image for the system tray icon."""
    width, height = 64, 64
    image = Image.new('RGB', (width, height), primary_color)
    dc = ImageDraw.Draw(image)
    # A simple, modern "bolt" icon
    dc.polygon([(20, 4), (44, 4), (32, 28), (40, 28), (24, 60), (32, 36), (24, 36)], fill=secondary_color)
    return image

def get_power_plan_guid(plan_name):
    """
    Retrieves the GUID for a given Windows Power Plan name.
    Returns the GUID or None if not found.
    """
    try:
        # List all power schemes and their GUIDs
        result = subprocess.run(
            ["powercfg", "/list"],
            capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.splitlines():
            if plan_name.lower() in line.lower():
                # Expected format: "Power Scheme GUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX  (Plan Name)"
                parts = line.split("Power Scheme GUID: ")
                if len(parts) > 1:
                    guid_part = parts[1].split(" ")[0]
                    return guid_part.strip()
        logging.warning(f"Power plan '{plan_name}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error getting power plan GUID for '{plan_name}': {e}")
        return None

def get_current_power_plan():
    """Retrieves the currently active Windows Power Plan name."""
    try:
        result = subprocess.run(
            ["powercfg", "/getactivescheme"],
            capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Expected format: "Active Power Scheme: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX (Plan Name)"
        line = result.stdout.splitlines()[0]
        if "Active Power Scheme:" in line:
            return line.split('(')[-1].replace(')', '').strip()
        return "Unknown"
    except Exception as e:
        logging.error(f"Error getting current power plan: {e}")
        return "Unknown"

def get_current_wifi_ssid():
    """Retrieves the current Wi-Fi SSID."""
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        for line in result.stdout.splitlines():
            if "SSID" in line and "BSSID" not in line: # Avoid BSSID line
                return line.split(":")[1].strip()
        return None
    except Exception as e:
        logging.error(f"Error getting Wi-Fi SSID: {e}")
        return None

class Tooltip:
    """Helper class to create tooltips for Tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Displays the tooltip."""
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True) # Keep tooltip on top

        label = tk.Label(self.tooltip_window, text=self.text, background="#FFFFCC", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """Hides the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class ScrollableFrame(ttk.Frame):
    """A scrollable frame that can be used to hold other widgets."""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Use the container's background color for the canvas
        style = ttk.Style()
        bg_color = style.lookup('TFrame', 'background')

        canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # This is the frame that will contain the widgets and be scrolled
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_canvas_configure(event):
            # Resize the inner frame to match the canvas width
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", on_canvas_configure)

        def on_mouse_wheel(event):
            # Platform-specific mouse wheel scrolling
            if sys.platform == "win32":
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif sys.platform == "darwin":
                canvas.yview_scroll(int(-1 * event.delta), "units")
            else:  # Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        # This binding allows scrolling when the mouse is over any widget in the frame
        self.bind_all("<MouseWheel>", on_mouse_wheel, add="+")


        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# --- Main Application Class ---
class PowerWhisperApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.settings_window = None
        self.config = {}
        self.active_profile_name = "Balanced" # Default profile
        self.is_admin = is_admin()
        self.tray_icon = None
        self.stop_event = threading.Event()
        self.battery_history = []
        self.last_battery_percent = -1 # To track changes for history logging

        logging.info(f"{APP_NAME} starting up...")
        if not self.is_admin:
            logging.warning("Not running as administrator. Key features will be limited.")

        # Initialize config with default structure
        self.load_config()
        # Ensure the active profile is set correctly after loading config
        self.active_profile_name = self.config.get("active_profile", "Balanced")
        if self.active_profile_name not in self.config["profiles"]:
            self.active_profile_name = "Balanced" # Fallback if active profile is invalid
            self.config["active_profile"] = "Balanced"
            self.save_config() # Save corrected active profile

    def load_config(self):
        """Loads configuration from file, merging with defaults."""
        default_profile_settings = {
            "eco_threshold": 40,
            "restore_threshold": 80,
            "enable_smart_kill": True,
            "user_kill_apps": ["msedge.exe"],
            "disable_wifi": False,
            "disable_bluetooth": False,
            "reduce_brightness": True,
            "brightness_level": 70,
            "windows_power_plan": "Balanced",
            "stop_services": [] # List of service_names to stop in this profile
        }
        
        default_config = {
            "active_profile": "Balanced",
            "profiles": {
                "Balanced": default_profile_settings,
                "Max Battery": {
                    **default_profile_settings,
                    "eco_threshold": 99,
                    "restore_threshold": 100,
                    "brightness_level": 20,
                    "disable_wifi": True,
                    "disable_bluetooth": True,
                    "user_kill_apps": ["chrome.exe", "spotify.exe"],
                    "windows_power_plan": "Power Saver",
                    "stop_services": [
                        {"service_name": "Spooler", "display_name": "Print Spooler"},
                        {"service_name": "Themes", "display_name": "Themes"}
                    ]
                },
                "Gaming": {
                    **default_profile_settings,
                    "eco_threshold": 0,
                    "restore_threshold": 0,
                    "enable_smart_kill": False,
                    "brightness_level": 100,
                    "user_kill_apps": [],
                    "windows_power_plan": "High Performance"
                }
            },
            "auto_profile_switching": {
                "battery_level": True,
                "app_triggers": [], # {"app_name": "steam.exe", "profile": "Gaming"}
                "network_triggers": [], # {"ssid": "MyOfficeWiFi", "profile": "Work"}
                "time_triggers": [] # {"start_time": "22:00", "end_time": "07:00", "profile": "Quiet Hours"}
            },
            "show_notifications": True
        }

        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                
                # Deep merge loaded config with default config to handle new keys/structures
                def deep_merge(target, source):
                    for k, v in source.items():
                        if k in target and isinstance(target[k], dict) and isinstance(v, dict):
                            deep_merge(target[k], v)
                        else:
                            target[k] = v
                
                self.config = default_config
                deep_merge(self.config, loaded_config)

                # Ensure all profiles have all default settings
                for profile_name, profile_data in self.config["profiles"].items():
                    for key, value in default_profile_settings.items():
                        profile_data.setdefault(key, value)

                logging.info("Configuration loaded.")
            else:
                self.config = default_config
                self.save_config()
                logging.info("Default configuration created.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Config load error: {e}. Using defaults.", exc_info=True)
            self.config = default_config
        
        self.load_battery_history()

    def save_config(self):
        """Saves current configuration to file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info("Configuration saved.")
        except IOError as e:
            logging.error(f"Config save error: {e}", exc_info=True)

    def load_battery_history(self):
        """Loads battery history from file."""
        try:
            if os.path.exists(BATTERY_HISTORY_FILE):
                with open(BATTERY_HISTORY_FILE, 'r') as f:
                    self.battery_history = json.load(f)
                logging.info(f"Loaded {len(self.battery_history)} battery history entries.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Battery history load error: {e}. Starting fresh.", exc_info=True)
            self.battery_history = []

    def save_battery_history(self):
        """Saves battery history to file."""
        try:
            # Keep history to last 24 hours (approx 24 * 60 / 15 = 96 entries)
            one_day_ago = (datetime.now() - timedelta(hours=24)).timestamp()
            self.battery_history = [
                entry for entry in self.battery_history 
                if datetime.fromisoformat(entry['timestamp']).timestamp() >= one_day_ago
            ]
            
            with open(BATTERY_HISTORY_FILE, 'w') as f:
                json.dump(self.battery_history, f, indent=4)
            logging.info("Battery history saved.")
        except IOError as e:
            logging.error(f"Battery history save error: {e}", exc_info=True)

    # --- Power Management Actions ---
    def set_brightness(self, level):
        """Sets screen brightness using PowerShell."""
        if not self.is_admin:
            logging.warning("Admin rights required to set brightness. Skipping.")
            return False
        level = max(0, min(100, int(level))) # Ensure level is between 0 and 100
        logging.info(f"Setting brightness to {level}%")
        command = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})"
        try:
            subprocess.run(["powershell", "-Command", command], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            logging.error(f"Failed to set brightness: {e}")
            self.send_notification("Brightness Error", f"Failed to set brightness: {e}", is_error=True)
            return False

    def toggle_network_adapter(self, adapter_name, enable=True):
        """Enables or disables a network adapter (e.g., Wi-Fi)."""
        if not self.is_admin:
            logging.warning(f"Admin rights required to toggle {adapter_name}. Skipping.")
            return False
        state = "enable" if enable else "disable"
        logging.info(f"Attempting to {state} {adapter_name}.")
        command = f'netsh interface set interface "{adapter_name}" admin={state}d'
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logging.info(f"{adapter_name} successfully {state}d.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to toggle {adapter_name}. Error: {e.stderr.strip()}")
            self.send_notification("Network Error", f"Failed to toggle {adapter_name}: {e.stderr.strip()}", is_error=True)
            return False
        except Exception as e:
            logging.error(f"Failed to toggle {adapter_name}. Unexpected error: {e}")
            self.send_notification("Network Error", f"Failed to toggle {adapter_name}: {e}", is_error=True)
            return False

    def toggle_bluetooth(self, enable=True):
        """Enables or disables Bluetooth."""
        if not self.is_admin:
            logging.warning("Admin rights required to toggle Bluetooth. Skipping.")
            return False
        state_action = "Enable-PnpDevice" if enable else "Disable-PnpDevice"
        logging.info(f"Attempting to {state_action.split('-')[0].lower()} Bluetooth.")
        # Find Bluetooth radio device and toggle its state
        command = f'Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | Where-Object {{ $_.FriendlyName -like "*Bluetooth Radio*" }} | ForEach-Object {{ {state_action} -InstanceId $_.InstanceId -Confirm:$false }}'
        try:
            subprocess.run(["powershell", "-Command", command], check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logging.info("Bluetooth command executed.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to toggle Bluetooth. Error: {e.stderr.strip()}")
            self.send_notification("Bluetooth Error", f"Failed to toggle Bluetooth: {e.stderr.strip()}", is_error=True)
            return False
        except Exception as e:
            logging.error(f"Failed to toggle Bluetooth. Unexpected error: {e}")
            self.send_notification("Bluetooth Error", f"Failed to toggle Bluetooth: {e}", is_error=True)
            return False
    
    def set_power_plan(self, plan_name):
        """Sets the active Windows Power Plan."""
        if not self.is_admin:
            logging.warning("Admin rights required to change power plan. Skipping.")
            return False
        
        plan_guid = get_power_plan_guid(plan_name)
        if not plan_guid:
            logging.error(f"Could not find GUID for power plan '{plan_name}'. Skipping.")
            self.send_notification("Power Plan Error", f"Could not find '{plan_name}' power plan.", is_error=True)
            return False

        logging.info(f"Attempting to set power plan to '{plan_name}' (GUID: {plan_guid}).")
        command = f"powercfg /setactive {plan_guid}"
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logging.info(f"Power plan set to '{plan_name}'.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set power plan to '{plan_name}'. Error: {e.stderr.strip()}")
            self.send_notification("Power Plan Error", f"Failed to set power plan: {e.stderr.strip()}", is_error=True)
            return False
        except Exception as e:
            logging.error(f"Failed to set power plan to '{plan_name}'. Unexpected error: {e}")
            self.send_notification("Power Plan Error", f"Failed to set power plan: {e}", is_error=True)
            return False

    def toggle_windows_service(self, service_name, enable=True):
        """Starts or stops a Windows service."""
        if not self.is_admin:
            logging.warning(f"Admin rights required to toggle service '{service_name}'. Skipping.")
            return False
        
        action = "start" if enable else "stop"
        logging.info(f"Attempting to {action} service '{service_name}'.")
        command = f"net {action} {service_name}"
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logging.info(f"Service '{service_name}' successfully {action}ed.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to {action} service '{service_name}'. Error: {e.stderr.strip()}")
            self.send_notification("Service Control Error", f"Failed to {action} service '{service_name}': {e.stderr.strip()}", is_error=True)
            return False
        except Exception as e:
            logging.error(f"Failed to {action} service '{service_name}'. Unexpected error: {e}")
            self.send_notification("Service Control Error", f"Failed to {action} service '{service_name}': {e}", is_error=True)
            return False

    def kill_processes(self, process_list):
        """Terminates processes from a given list."""
        if not process_list:
            logging.info("No processes configured for termination in current profile.")
            return

        killed_count = 0
        failed_kills = []
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() in [p.lower() for p in process_list]:
                try:
                    p = psutil.Process(proc.info['pid'])
                    p.kill()
                    logging.info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logging.warning(f"Could not kill {proc.info['name']}: {e}")
                    failed_kills.append(f"{proc.info['name']} (Access Denied)")
                except Exception as e:
                    logging.error(f"Unexpected error killing {proc.info['name']}: {e}")
                    failed_kills.append(f"{proc.info['name']} (Error: {e})")
        
        if killed_count > 0:
            self.send_notification("Apps Terminated", f"Closed {killed_count} non-essential application(s).")
        if failed_kills:
            self.send_notification("App Killer Warning", f"Failed to kill some apps: {', '.join(failed_kills)}", is_error=True)


    # --- Core Logic: Profile Application ---
    def apply_profile(self, profile_name):
        """Applies settings defined in the specified profile."""
        if profile_name not in self.config["profiles"]:
            logging.error(f"Profile '{profile_name}' not found. Aborting application.")
            self.send_notification("Error", f"Profile '{profile_name}' not found.", is_error=True)
            return

        # Get settings for the current and target profiles
        # This is crucial for only toggling what needs to be toggled
        current_profile_settings = self.config["profiles"].get(self.active_profile_name, {})
        target_profile_settings = self.config["profiles"][profile_name]

        logging.info(f"Activating profile: {profile_name}")
        self.send_notification("Profile Activated", f"Switching to '{profile_name}' profile.")
        
        # Store previous settings to restore if needed (for manual toggle)
        self.config["active_profile"] = profile_name
        self.active_profile_name = profile_name
        self.save_config() # Save the new active profile

        # Apply brightness
        target_brightness_level = target_profile_settings.get("brightness_level", 70)
        current_brightness_level = current_profile_settings.get("brightness_level", 70) # Assume default if not set
        
        if target_profile_settings.get("reduce_brightness") and self.set_brightness(target_brightness_level):
            logging.info(f"Brightness set to {target_brightness_level}% as per profile '{profile_name}'.")
        elif not target_profile_settings.get("reduce_brightness") and self.set_brightness(90): # Restore to a higher default
            logging.info(f"Brightness restored to 90% (not reducing) as per profile '{profile_name}'.")


        # Toggle Wi-Fi
        target_disable_wifi = target_profile_settings.get("disable_wifi")
        current_disable_wifi = current_profile_settings.get("disable_wifi")
        if target_disable_wifi != current_disable_wifi:
            self.toggle_network_adapter("Wi-Fi", enable=not target_disable_wifi)
        
        # Toggle Bluetooth
        target_disable_bluetooth = target_profile_settings.get("disable_bluetooth")
        current_disable_bluetooth = current_profile_settings.get("disable_bluetooth")
        if target_disable_bluetooth != current_disable_bluetooth:
            self.toggle_bluetooth(enable=not target_disable_bluetooth)

        # Kill processes
        processes_to_kill = set()
        if target_profile_settings.get("enable_smart_kill"):
            processes_to_kill.update([p.lower() for p in SMART_KILL_LIST])
        
        user_list = target_profile_settings.get("user_kill_apps", [])
        processes_to_kill.update([p.lower() for p in user_list])
        self.kill_processes(list(processes_to_kill))

        # Set Windows Power Plan
        target_power_plan = target_profile_settings.get("windows_power_plan")
        if target_power_plan and get_current_power_plan().lower() != target_power_plan.lower():
            self.set_power_plan(target_power_plan)

        # Toggle Windows Services
        # Stop services defined in the target profile
        for service_info in target_profile_settings.get("stop_services", []):
            service_name = service_info.get("service_name")
            if service_name:
                self.toggle_windows_service(service_name, enable=False) # Stop services

        # Start services that were stopped by the *previous* profile but are NOT in the current profile's stop list
        # This is a basic attempt at restoration. A more robust solution would track services explicitly stopped by PowerWhisper.
        current_stop_services_names = {s.get("service_name") for s in target_profile_settings.get("stop_services", [])}
        previous_stop_services_names = {s.get("service_name") for s in current_profile_settings.get("stop_services", [])}

        for service_name in previous_stop_services_names:
            if service_name not in current_stop_services_names:
                self.toggle_windows_service(service_name, enable=True) # Try to start it back

        self.update_tray_icon()
        logging.info(f"Profile '{profile_name}' applied successfully.")

    def send_notification(self, title, message, is_error=False):
        """Sends a desktop notification. Can be marked as error."""
        if self.config.get("show_notifications"):
            try:
                app_icon = os.path.join(os.path.dirname(sys.executable), 'icon.ico') if getattr(sys, 'frozen', False) else None
                notification.notify(
                    title=f"{APP_NAME}: {title}",
                    message=message,
                    app_name=APP_NAME,
                    timeout=8,
                    app_icon=app_icon # Add an icon for better native look
                )
            except Exception as e:
                logging.error(f"Failed to send notification: {e}", exc_info=True)

    # --- System Tray ---
    def setup_tray_icon(self):
        """Sets up the system tray icon and its menu."""
        def create_profile_menu_item(profile_name):
            return pystray.MenuItem(
                profile_name,
                lambda: self.apply_profile(profile_name),
                checked=lambda item: self.active_profile_name == profile_name
            )

        profile_menu_items = [create_profile_menu_item(name) for name in self.config["profiles"].keys()]

        menu = pystray.Menu(
            pystray.MenuItem('Active Profile: ' + self.active_profile_name, None), # Display current profile
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Profiles', pystray.Menu(*profile_menu_items)),
            pystray.MenuItem('Settings', self.show_settings_gui),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self.exit_app)
        )
        icon_image = create_tray_icon('#1A1A1A', '#007ACC')
        self.tray_icon = pystray.Icon(APP_NAME, icon_image, APP_NAME, menu)
        
    def update_tray_icon(self):
        """Updates the tray icon's appearance and menu based on active profile."""
        if not self.tray_icon: return

        # Change icon color based on a simple heuristic (e.g., if it's a "power saving" profile)
        active_profile_settings = self.config["profiles"].get(self.active_profile_name, {})
        is_power_saving = active_profile_settings.get("reduce_brightness") and active_profile_settings.get("brightness_level", 70) < 50 \
                          or active_profile_settings.get("disable_wifi") \
                          or active_profile_settings.get("disable_bluetooth") \
                          or active_profile_settings.get("windows_power_plan", "").lower() == "power saver"

        self.tray_icon.icon = create_tray_icon('#1A1A1A', '#FF8C00') if is_power_saving else create_tray_icon('#1A1A1A', '#007ACC')
        
        # Rebuild the menu to update the checked state for profiles
        def create_profile_menu_item(profile_name):
            return pystray.MenuItem(
                profile_name,
                lambda: self.apply_profile(profile_name),
                checked=lambda item: self.active_profile_name == profile_name
            )
        profile_menu_items = [create_profile_menu_item(name) for name in self.config["profiles"].keys()]
        
        self.tray_icon.menu = pystray.Menu(
            pystray.MenuItem('Active Profile: ' + self.active_profile_name, None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Profiles', pystray.Menu(*profile_menu_items)),
            pystray.MenuItem('Settings', self.show_settings_gui),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.tray_icon.update_menu()

    # --- GUI Management ---
    def show_settings_gui(self):
        """Displays the main settings GUI window."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title(f"{APP_NAME} Control Panel")
        self.settings_window.geometry("800x700")
        self.settings_window.minsize(700, 650)
        self.settings_window.configure(bg="#252525")

        # --- Professional Dark Theme Styling ---
        style = ttk.Style(self.settings_window)
        style.theme_use("clam")
        
        # Colors
        BG_COLOR = "#252525"
        FG_COLOR = "#E0E0E0"
        FIELD_BG = "#3A3A3A"
        ACCENT_COLOR = "#007ACC"
        ACCENT_ACTIVE = "#0098E5"
        BORDER_COLOR = "#4A4A4A"

        style.configure(".", background=BG_COLOR, foreground=FG_COLOR, fieldbackground=FIELD_BG, borderwidth=1, lightcolor=BG_COLOR, darkcolor=BG_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_COLOR)
        style.configure("Status.TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), background=ACCENT_COLOR, foreground="white", borderwidth=0, padding=(10, 8))
        style.map("TButton", background=[("active", ACCENT_ACTIVE)])
        style.configure("TCheckbutton", font=("Segoe UI", 10), indicatorrelief=tk.FLAT)
        style.map("TCheckbutton", indicatorbackground=[("selected", ACCENT_COLOR)])
        style.configure("TLabelframe", font=("Segoe UI", 11, "bold"), bordercolor=BORDER_COLOR)
        style.configure("TLabelframe.Label", foreground=FG_COLOR, background=BG_COLOR)
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 8], background=FIELD_BG, foreground="#AAAAAA", borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "white")])
        style.configure("TCombobox", fieldbackground=FIELD_BG, foreground=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground="white")
        style.map("TCombobox", fieldbackground=[("readonly", FIELD_BG)])


        notebook = ttk.Notebook(self.settings_window)
        notebook.pack(expand=True, fill="both", padx=15, pady=15)

        # Create a dictionary to hold the main frame for each tab
        tabs = {}
        tab_names = ["Dashboard", "Profiles", "Automation", "App Killer", "Analytics", "Log Viewer", "Advanced"]
        
        # Create frames for each tab, using ScrollableFrame for specific tabs
        tabs["Dashboard"] = ttk.Frame(notebook, padding=15)
        tabs["Profiles"] = ScrollableFrame(notebook)
        tabs["Automation"] = ScrollableFrame(notebook)
        tabs["App Killer"] = ttk.Frame(notebook, padding=15)
        tabs["Analytics"] = ttk.Frame(notebook, padding=15)
        tabs["Log Viewer"] = ttk.Frame(notebook, padding=15)
        tabs["Advanced"] = ttk.Frame(notebook, padding=15)

        # Add tabs to the notebook
        for name in tab_names:
            notebook.add(tabs[name], text=f" {name} ")

        # Get the actual content frame for scrollable tabs
        profile_content_frame = tabs["Profiles"].scrollable_frame
        profile_content_frame.configure(padding=15)

        automation_content_frame = tabs["Automation"].scrollable_frame
        automation_content_frame.configure(padding=15)

        # --- Populate Dashboard ---
        ttk.Label(tabs["Dashboard"], text="System Dashboard", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        self.status_label = ttk.Label(tabs["Dashboard"], text="Initializing...", style="Status.TLabel", justify="left")
        self.status_label.pack(anchor="w", pady=5, fill="x")
        
        ttk.Separator(tabs["Dashboard"], orient="horizontal").pack(fill='x', pady=20)
        
        manual_frame = ttk.LabelFrame(tabs["Dashboard"], text="Manual Profile Activation", padding=15)
        manual_frame.pack(fill="x", pady=10)
        
        ttk.Label(manual_frame, text="Select Profile:").pack(side="left", padx=5)
        self.profile_selector_var = tk.StringVar(value=self.active_profile_name)
        self.profile_selector = ttk.Combobox(manual_frame, textvariable=self.profile_selector_var, 
                                            values=list(self.config["profiles"].keys()), state="readonly")
        self.profile_selector.pack(side="left", expand=True, fill="x", padx=5)
        self.profile_selector.bind("<<ComboboxSelected>>", self._on_profile_selected_from_dashboard)
        
        ttk.Button(manual_frame, text="Apply Selected Profile", command=lambda: self.apply_profile(self.profile_selector_var.get())).pack(side="right", padx=5)

        # --- Populate Profiles Tab ---
        ttk.Label(profile_content_frame, text="Manage Power Profiles", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        
        profile_list_frame = ttk.LabelFrame(profile_content_frame, text="Existing Profiles", padding=10)
        profile_list_frame.pack(fill="x", pady=10)
        
        self.profile_listbox = tk.Listbox(profile_list_frame, height=5, bg=FIELD_BG, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground="white", relief=tk.FLAT)
        self.profile_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.profile_listbox.bind("<<ListboxSelect>>", self._load_profile_settings)
        
        profile_buttons_frame = ttk.Frame(profile_list_frame)
        profile_buttons_frame.pack(side="right", fill="y", padx=5, pady=5)
        ttk.Button(profile_buttons_frame, text="Add New", command=self._add_new_profile).pack(fill="x", pady=2)
        ttk.Button(profile_buttons_frame, text="Rename", command=self._rename_profile).pack(fill="x", pady=2)
        ttk.Button(profile_buttons_frame, text="Delete", command=self._delete_profile).pack(fill="x", pady=2)
        ttk.Button(profile_buttons_frame, text="Duplicate", command=self._duplicate_profile).pack(fill="x", pady=2)

        self.profile_settings_frame = ttk.LabelFrame(profile_content_frame, text="Profile Settings", padding=15)
        self.profile_settings_frame.pack(fill="both", expand=True, pady=10)
        
        # Profile settings variables
        self.current_profile_name_var = tk.StringVar()
        self.profile_eco_thresh_var = tk.IntVar()
        self.profile_restore_thresh_var = tk.IntVar()
        self.profile_enable_smart_kill_var = tk.BooleanVar()
        self.profile_reduce_bright_var = tk.BooleanVar()
        self.profile_brightness_level_var = tk.IntVar()
        self.profile_disable_wifi_var = tk.BooleanVar()
        self.profile_disable_bt_var = tk.BooleanVar()
        self.profile_windows_power_plan_var = tk.StringVar()
        self.profile_user_kill_apps_text = scrolledtext.ScrolledText(self.profile_settings_frame, height=4, font=("Consolas", 9), bg="#1E1E1E", fg="white", insertbackground="white", relief=tk.FLAT)
        self.profile_stop_services_vars = {} # Dict to hold BooleanVars for services

        # Layout for profile settings
        settings_grid_frame = ttk.Frame(self.profile_settings_frame)
        settings_grid_frame.pack(fill="x", pady=5)
        settings_grid_frame.columnconfigure(1, weight=1)

        # Row 0: Eco Threshold
        ttk.Label(settings_grid_frame, text="Eco Threshold (%):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        eco_entry = ttk.Entry(settings_grid_frame, textvariable=self.profile_eco_thresh_var, width=10)
        eco_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        Tooltip(eco_entry, "Battery percentage below which this profile will be automatically activated (if auto-switching is enabled).")

        # Row 1: Restore Threshold
        ttk.Label(settings_grid_frame, text="Restore Threshold (%):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        restore_entry = ttk.Entry(settings_grid_frame, textvariable=self.profile_restore_thresh_var, width=10)
        restore_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        Tooltip(restore_entry, "Battery percentage above which the previous profile will be restored (if auto-switching is enabled and on battery).")
        
        # Row 2: Smart Kill
        smart_kill_check = ttk.Checkbutton(settings_grid_frame, text="Enable Smart Kill", variable=self.profile_enable_smart_kill_var)
        smart_kill_check.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        Tooltip(smart_kill_check, "Automatically terminate common non-essential background applications when this profile is active.")

        # Row 3: Brightness
        reduce_bright_check = ttk.Checkbutton(settings_grid_frame, text="Reduce Screen Brightness", variable=self.profile_reduce_bright_var)
        reduce_bright_check.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        Tooltip(reduce_bright_check, "Reduce screen brightness to the specified level when this profile is active.")
        
        brightness_frame = ttk.Frame(settings_grid_frame)
        brightness_frame.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(brightness_frame, text="Level (%):").pack(side="left")
        brightness_entry = ttk.Entry(brightness_frame, textvariable=self.profile_brightness_level_var, width=5)
        brightness_entry.pack(side="left", padx=5)
        Tooltip(brightness_entry, "The target brightness level (0-100) if 'Reduce Screen Brightness' is enabled.")

        # Row 4: Wi-Fi
        disable_wifi_check = ttk.Checkbutton(settings_grid_frame, text="Disable Wi-Fi", variable=self.profile_disable_wifi_var)
        disable_wifi_check.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        Tooltip(disable_wifi_check, "Disable the Wi-Fi adapter when this profile is active. Requires Administrator privileges.")

        # Row 5: Bluetooth
        disable_bt_check = ttk.Checkbutton(settings_grid_frame, text="Disable Bluetooth", variable=self.profile_disable_bt_var)
        disable_bt_check.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        Tooltip(disable_bt_check, "Disable Bluetooth when this profile is active. Requires Administrator privileges.")
        
        # Row 6: Power Plan
        ttk.Label(settings_grid_frame, text="Windows Power Plan:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.power_plan_combobox = ttk.Combobox(settings_grid_frame, textvariable=self.profile_windows_power_plan_var, state="readonly")
        self.power_plan_combobox.grid(row=6, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        Tooltip(self.power_plan_combobox, "Select the Windows Power Plan to activate with this profile. Requires Administrator privileges.")
        self.power_plan_combobox['values'] = self._get_available_power_plans()

        ttk.Label(self.profile_settings_frame, text="Additional Apps to Kill (one per line):").pack(anchor="w", pady=(10, 2))
        self.profile_user_kill_apps_text.pack(fill="x", pady=5)
        Tooltip(self.profile_user_kill_apps_text, "List additional application executable names (e.g., 'chrome.exe') to terminate when this profile is active.")

        ttk.Label(self.profile_settings_frame, text="Windows Services to Stop (when profile active):").pack(anchor="w", pady=(10, 2))
        services_frame = ttk.LabelFrame(self.profile_settings_frame, text="Requires Admin Privileges", padding=5)
        services_frame.pack(fill="x", pady=5)
        
        # Dynamically create checkboxes for services
        col = 0
        for service_name, display_name in WINDOWS_SERVICES.items():
            var = tk.BooleanVar()
            self.profile_stop_services_vars[service_name] = var
            chk = ttk.Checkbutton(services_frame, text=display_name, variable=var)
            chk.grid(row=col // 3, column=col % 3, sticky="w", padx=5, pady=2)
            Tooltip(chk, f"Stop the '{display_name}' Windows service when this profile is active. Requires Administrator privileges.")
            col += 1

        ttk.Button(self.profile_settings_frame, text="Save Profile Settings", command=self._save_current_profile_settings).pack(pady=10)
        
        self._populate_profile_listbox()
        if self.config["profiles"]:
            self.profile_listbox.selection_set(0)
            self._load_profile_settings() # Load settings for the first profile by default


        # --- Populate Automation Tab ---
        ttk.Label(automation_content_frame, text="Automation Rules", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        
        self.auto_battery_var = tk.BooleanVar(value=self.config["auto_profile_switching"].get("battery_level", True))
        auto_batt_check = ttk.Checkbutton(automation_content_frame, text="Enable Battery Level Based Profile Switching", variable=self.auto_battery_var)
        auto_batt_check.pack(anchor="w", pady=10)
        Tooltip(auto_batt_check, "Automatically switch profiles based on battery percentage and charging status.")

        # App Triggers
        app_trigger_frame = ttk.LabelFrame(automation_content_frame, text="Application Launch Triggers", padding=10)
        app_trigger_frame.pack(fill="x", pady=10)
        app_trigger_frame.columnconfigure(1, weight=1)
        
        ttk.Label(app_trigger_frame, text="App Name (e.g., steam.exe):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.new_app_trigger_name_var = tk.StringVar()
        new_app_entry = ttk.Entry(app_trigger_frame, textvariable=self.new_app_trigger_name_var)
        new_app_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        Tooltip(new_app_entry, "Enter the executable name of the application (e.g., 'chrome.exe').")
        
        ttk.Label(app_trigger_frame, text="Switch to Profile:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.new_app_trigger_profile_var = tk.StringVar()
        app_profile_combo = ttk.Combobox(app_trigger_frame, textvariable=self.new_app_trigger_profile_var, values=list(self.config["profiles"].keys()), state="readonly")
        app_profile_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        Tooltip(app_profile_combo, "Select the profile to activate when the specified application is detected running.")
        
        ttk.Button(app_trigger_frame, text="Add App Trigger", command=self._add_app_trigger).grid(row=2, column=0, columnspan=2, pady=5)
        
        self.app_triggers_listbox = tk.Listbox(app_trigger_frame, height=4, bg=FIELD_BG, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground="white", relief=tk.FLAT)
        self.app_triggers_listbox.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(app_trigger_frame, text="Remove Selected App Trigger", command=self._remove_app_trigger).grid(row=4, column=0, columnspan=2, pady=5)
        self._populate_app_triggers()

        # Network Triggers
        network_trigger_frame = ttk.LabelFrame(automation_content_frame, text="Network SSID Triggers", padding=10)
        network_trigger_frame.pack(fill="x", pady=10)
        network_trigger_frame.columnconfigure(1, weight=1)

        ttk.Label(network_trigger_frame, text="Wi-Fi SSID:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.new_network_trigger_ssid_var = tk.StringVar()
        new_net_entry = ttk.Entry(network_trigger_frame, textvariable=self.new_network_trigger_ssid_var)
        new_net_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        Tooltip(new_net_entry, "Enter the exact name of the Wi-Fi network (SSID).")
        
        ttk.Label(network_trigger_frame, text="Switch to Profile:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.new_network_trigger_profile_var = tk.StringVar()
        network_profile_combo = ttk.Combobox(network_trigger_frame, textvariable=self.new_network_trigger_profile_var, values=list(self.config["profiles"].keys()), state="readonly")
        network_profile_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        Tooltip(network_profile_combo, "Select the profile to activate when connected to the specified Wi-Fi network.")
        
        ttk.Button(network_trigger_frame, text="Add Network Trigger", command=self._add_network_trigger).grid(row=2, column=0, columnspan=2, pady=5)
        
        self.network_triggers_listbox = tk.Listbox(network_trigger_frame, height=4, bg=FIELD_BG, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground="white", relief=tk.FLAT)
        self.network_triggers_listbox.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(network_trigger_frame, text="Remove Selected Network Trigger", command=self._remove_network_trigger).grid(row=4, column=0, columnspan=2, pady=5)
        self._populate_network_triggers()

        # Time Triggers
        time_trigger_frame = ttk.LabelFrame(automation_content_frame, text="Time-Based Triggers", padding=10)
        time_trigger_frame.pack(fill="x", pady=10)
        time_trigger_frame.columnconfigure(1, weight=1)

        ttk.Label(time_trigger_frame, text="Start Time (HH:MM):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.new_time_trigger_start_var = tk.StringVar()
        new_time_start_entry = ttk.Entry(time_trigger_frame, textvariable=self.new_time_trigger_start_var, width=8)
        new_time_start_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        Tooltip(new_time_start_entry, "Enter the start time in 24-hour format (e.g., 08:00, 22:30).")
        
        ttk.Label(time_trigger_frame, text="End Time (HH:MM):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.new_time_trigger_end_var = tk.StringVar()
        new_time_end_entry = ttk.Entry(time_trigger_frame, textvariable=self.new_time_trigger_end_var, width=8)
        new_time_end_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        Tooltip(new_time_end_entry, "Enter the end time in 24-hour format (e.g., 17:00, 07:00).")

        ttk.Label(time_trigger_frame, text="Switch to Profile:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.new_time_trigger_profile_var = tk.StringVar()
        time_profile_combo = ttk.Combobox(time_trigger_frame, textvariable=self.new_time_trigger_profile_var, values=list(self.config["profiles"].keys()), state="readonly")
        time_profile_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        Tooltip(time_profile_combo, "Select the profile to activate within the specified time window.")
        
        ttk.Button(time_trigger_frame, text="Add Time Trigger", command=self._add_time_trigger).grid(row=3, column=0, columnspan=2, pady=5)
        
        self.time_triggers_listbox = tk.Listbox(time_trigger_frame, height=4, bg=FIELD_BG, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground="white", relief=tk.FLAT)
        self.time_triggers_listbox.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(time_trigger_frame, text="Remove Selected Time Trigger", command=self._remove_time_trigger).grid(row=5, column=0, columnspan=2, pady=5)
        self._populate_time_triggers()

        # --- Populate App Killer Tab ---
        ttk.Label(tabs["App Killer"], text="Application Killer & Monitor", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        
        process_monitor_frame = ttk.LabelFrame(tabs["App Killer"], text="Live Process Monitor", padding=10)
        process_monitor_frame.pack(fill="both", expand=True, pady=10)

        monitor_controls_frame = ttk.Frame(process_monitor_frame)
        monitor_controls_frame.pack(fill="x", pady=5)
        ttk.Label(monitor_controls_frame, text="Sort by:").pack(side="left", padx=5)
        self.process_sort_var = tk.StringVar(value="CPU")
        ttk.Radiobutton(monitor_controls_frame, text="CPU", variable=self.process_sort_var, value="CPU", command=self._update_process_list).pack(side="left", padx=5)
        ttk.Radiobutton(monitor_controls_frame, text="RAM", variable=self.process_sort_var, value="RAM", command=self._update_process_list).pack(side="left", padx=5)
        ttk.Button(monitor_controls_frame, text="Refresh Processes", command=self._update_process_list).pack(side="right", padx=5)

        self.process_list_text = scrolledtext.ScrolledText(process_monitor_frame, height=10, font=("Consolas", 9), bg="#1E1E1E", fg="#CCCCCC", relief=tk.FLAT)
        self.process_list_text.pack(fill="both", expand=True, pady=5)

        add_process_frame = ttk.Frame(process_monitor_frame)
        add_process_frame.pack(fill="x", pady=5)
        self.selected_process_to_add_var = tk.StringVar()
        ttk.Label(add_process_frame, text="Add to Kill List:").pack(side="left", padx=5)
        self.add_process_entry = ttk.Entry(add_process_frame, textvariable=self.selected_process_to_add_var)
        self.add_process_entry.pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(add_process_frame, text="Add to Current Profile's Kill List", command=self._add_selected_process_to_kill_list).pack(side="right", padx=5)
        
        self._update_process_list() # Initial population

        # --- Populate Analytics Tab ---
        ttk.Label(tabs["Analytics"], text="Battery Analytics", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        
        battery_stats_frame = ttk.LabelFrame(tabs["Analytics"], text="Current Battery Stats", padding=15)
        battery_stats_frame.pack(fill="x", pady=10)
        self.battery_stats_label = ttk.Label(battery_stats_frame, text="Loading...", justify="left")
        self.battery_stats_label.pack(anchor="w", fill="x")

        battery_history_frame = ttk.LabelFrame(tabs["Analytics"], text="Battery Level History (Last 24h)", padding=15)
        battery_history_frame.pack(fill="both", expand=True, pady=10)
        self.battery_history_text = scrolledtext.ScrolledText(battery_history_frame, state="disabled", font=("Consolas", 9), bg="#1E1E1E", fg="#CCCCCC", relief=tk.FLAT)
        self.battery_history_text.pack(fill="both", expand=True, pady=5)
        ttk.Button(battery_history_frame, text="Refresh History", command=self._update_battery_analytics).pack(pady=5, anchor="e")

        # --- Populate Log Viewer ---
        log_frame = tabs["Log Viewer"]
        ttk.Label(log_frame, text="Application Log", style="Header.TLabel").pack(anchor="w", pady=(0, 15))
        self.log_text = scrolledtext.ScrolledText(log_frame, state="disabled", font=("Consolas", 9), bg="#1E1E1E", fg="#CCCCCC", relief=tk.FLAT)
        self.log_text.pack(fill="both", expand=True, pady=5)
        ttk.Button(log_frame, text="Refresh Log", command=self._update_log_viewer).pack(anchor="e", pady=10)


        # --- Populate Advanced Tab ---
        ttk.Label(tabs["Advanced"], text="Advanced Configuration", style="Header.TLabel").pack(pady=(0, 20), anchor="w")
        
        config_mgmt_frame = ttk.LabelFrame(tabs["Advanced"], text="Configuration Management", padding=15)
        config_mgmt_frame.pack(fill="x", pady=10)
        
        export_btn = ttk.Button(config_mgmt_frame, text="Export Configuration", command=self._export_config)
        export_btn.pack(fill="x", pady=5)
        Tooltip(export_btn, "Save all profiles and settings to a JSON file for backup or transfer.")
        
        import_btn = ttk.Button(config_mgmt_frame, text="Import Configuration", command=self._import_config)
        import_btn.pack(fill="x", pady=5)
        Tooltip(import_btn, "Load profiles and settings from a JSON file. This will overwrite current settings.")
        
        notify_frame = ttk.LabelFrame(tabs["Advanced"], text="Notifications", padding=15)
        notify_frame.pack(fill="x", pady=10)
        self.show_notify_var = tk.BooleanVar(value=self.config['show_notifications'])
        
        notify_check = ttk.Checkbutton(notify_frame, text="Show Desktop Notifications", variable=self.show_notify_var, command=self._save_general_settings)
        notify_check.pack(anchor="w", pady=8)
        Tooltip(notify_check, "Toggle desktop notifications for application events.")


        # --- Bottom Buttons ---
        button_frame = ttk.Frame(self.settings_window, style="TFrame")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        ttk.Button(button_frame, text="Close", command=self.settings_window.destroy).pack(side="right", padx=5)

        self._update_dashboard()
        self._update_log_viewer()
        self._update_battery_analytics()
        self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.destroy)

    def _on_profile_selected_from_dashboard(self, event=None):
        # When a profile is selected from the dashboard combobox, update the listbox in the Profiles tab
        selected_profile = self.profile_selector_var.get()
        if selected_profile in self.config["profiles"]:
            idx = list(self.config["profiles"].keys()).index(selected_profile)
            self.profile_listbox.selection_clear(0, tk.END)
            self.profile_listbox.selection_set(idx)
            self.profile_listbox.see(idx)
            self._load_profile_settings()

    def _populate_profile_listbox(self):
        """Populates the listbox with profile names."""
        self.profile_listbox.delete(0, tk.END)
        for profile_name in self.config["profiles"].keys():
            self.profile_listbox.insert(tk.END, profile_name)

    def _load_profile_settings(self, event=None):
        """Loads settings of the selected profile into the GUI fields."""
        selected_indices = self.profile_listbox.curselection()
        if not selected_indices:
            # If no profile is selected (e.g., after deletion of the last one), clear fields
            self.current_profile_name_var.set("")
            self.profile_eco_thresh_var.set(0)
            self.profile_restore_thresh_var.set(0)
            self.profile_enable_smart_kill_var.set(False)
            self.profile_reduce_bright_var.set(False)
            self.profile_brightness_level_var.set(0)
            self.profile_disable_wifi_var.set(False)
            self.profile_disable_bt_var.set(False)
            self.profile_windows_power_plan_var.set("")
            self.profile_user_kill_apps_text.delete("1.0", tk.END)
            for var in self.profile_stop_services_vars.values():
                var.set(False)
            return
        
        profile_name = self.profile_listbox.get(selected_indices[0])
        self.current_profile_name_var.set(profile_name)
        profile_settings = self.config["profiles"].get(profile_name, {})

        self.profile_eco_thresh_var.set(profile_settings.get("eco_threshold", 40))
        self.profile_restore_thresh_var.set(profile_settings.get("restore_threshold", 80))
        self.profile_enable_smart_kill_var.set(profile_settings.get("enable_smart_kill", True))
        self.profile_reduce_bright_var.set(profile_settings.get("reduce_brightness", True))
        self.profile_brightness_level_var.set(profile_settings.get("brightness_level", 70))
        self.profile_disable_wifi_var.set(profile_settings.get("disable_wifi", False))
        self.profile_disable_bt_var.set(profile_settings.get("disable_bluetooth", False))
        self.profile_windows_power_plan_var.set(profile_settings.get("windows_power_plan", "Balanced"))

        self.profile_user_kill_apps_text.delete("1.0", tk.END)
        self.profile_user_kill_apps_text.insert(tk.END, "\n".join(profile_settings.get("user_kill_apps", [])))

        # Load service checkboxes
        stop_services_list = [s.get("service_name") for s in profile_settings.get("stop_services", [])]
        for service_name, var in self.profile_stop_services_vars.items():
            var.set(service_name in stop_services_list)

    def _save_current_profile_settings(self):
        """Saves settings from the GUI fields back to the active profile."""
        profile_name = self.current_profile_name_var.get()
        if not profile_name or profile_name not in self.config["profiles"]:
            messagebox.showerror("Error", "No profile selected or invalid profile name.", parent=self.settings_window)
            return

        try:
            profile_settings = self.config["profiles"][profile_name]
            profile_settings["eco_threshold"] = self.profile_eco_thresh_var.get()
            profile_settings["restore_threshold"] = self.profile_restore_thresh_var.get()
            profile_settings["enable_smart_kill"] = self.profile_enable_smart_kill_var.get()
            profile_settings["reduce_brightness"] = self.profile_reduce_bright_var.get()
            profile_settings["brightness_level"] = self.profile_brightness_level_var.get()
            profile_settings["disable_wifi"] = self.profile_disable_wifi_var.get()
            profile_settings["disable_bluetooth"] = self.profile_disable_bt_var.get()
            profile_settings["windows_power_plan"] = self.profile_windows_power_plan_var.get()
            
            apps_list = self.profile_user_kill_apps_text.get("1.0", tk.END).strip().split("\n")
            profile_settings["user_kill_apps"] = [app.strip() for app in apps_list if app.strip()]

            # Save service settings
            profile_settings["stop_services"] = []
            for service_name, var in self.profile_stop_services_vars.items():
                if var.get():
                    profile_settings["stop_services"].append({"service_name": service_name, "display_name": WINDOWS_SERVICES.get(service_name, service_name)})

            self.save_config()
            self.profile_selector['values'] = list(self.config["profiles"].keys()) # Update dashboard combobox
            self.update_tray_icon() # Update tray menu if profiles changed
            messagebox.showinfo("Success", f"Profile '{profile_name}' settings saved.", parent=self.settings_window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save profile settings: {e}", parent=self.settings_window)
            logging.error(f"Failed to save profile settings: {e}", exc_info=True)

    def _add_new_profile(self):
        """Adds a new profile based on a default template."""
        new_name = "New Profile"
        i = 1
        while new_name in self.config["profiles"]:
            new_name = f"New Profile {i}"
            i += 1
        
        default_profile_settings = {
            "eco_threshold": 40,
            "restore_threshold": 80,
            "enable_smart_kill": True,
            "user_kill_apps": [],
            "disable_wifi": False,
            "disable_bluetooth": False,
            "reduce_brightness": True,
            "brightness_level": 70,
            "windows_power_plan": "Balanced",
            "stop_services": []
        }
        self.config["profiles"][new_name] = default_profile_settings
        self.save_config()
        self._populate_profile_listbox()
        self.profile_listbox.selection_clear(0, tk.END)
        self.profile_listbox.selection_set(tk.END) # Select the new profile
        self._load_profile_settings()
        self.profile_selector['values'] = list(self.config["profiles"].keys())
        self.update_tray_icon()
        messagebox.showinfo("Success", f"Profile '{new_name}' added.", parent=self.settings_window)

    def _rename_profile(self):
        """Renames the selected profile."""
        selected_indices = self.profile_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a profile to rename.", parent=self.settings_window)
            return
        
        old_name = self.profile_listbox.get(selected_indices[0])
        
        # Simple input dialog
        dialog = tk.Toplevel(self.settings_window)
        dialog.title("Rename Profile")
        dialog.transient(self.settings_window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="New Profile Name:").pack(padx=10, pady=10)
        new_name_entry = ttk.Entry(dialog)
        new_name_entry.pack(padx=10, pady=5)
        new_name_entry.insert(0, old_name)
        new_name_entry.focus_set()

        def on_ok():
            new_name = new_name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Profile name cannot be empty.", parent=dialog)
                return
            if new_name in self.config["profiles"] and new_name != old_name:
                messagebox.showerror("Error", "Profile name already exists.", parent=dialog)
                return
            
            if old_name == self.config["active_profile"]:
                self.config["active_profile"] = new_name
            
            # Update app triggers
            for trigger in self.config["auto_profile_switching"]["app_triggers"]:
                if trigger["profile"] == old_name:
                    trigger["profile"] = new_name
            # Update network triggers
            for trigger in self.config["auto_profile_switching"]["network_triggers"]:
                if trigger["profile"] == old_name:
                    trigger["profile"] = new_name
            # Update time triggers
            for trigger in self.config["auto_profile_switching"]["time_triggers"]:
                if trigger["profile"] == old_name:
                    trigger["profile"] = new_name

            self.config["profiles"][new_name] = self.config["profiles"].pop(old_name)
            self.save_config()
            self._populate_profile_listbox()
            self.profile_listbox.selection_clear(0, tk.END)
            self.profile_listbox.selection_set(list(self.config["profiles"].keys()).index(new_name))
            self._load_profile_settings()
            self.profile_selector['values'] = list(self.config["profiles"].keys())
            self.update_tray_icon()
            self._populate_app_triggers() # Refresh automation tabs as well
            self._populate_network_triggers()
            self._populate_time_triggers()
            messagebox.showinfo("Success", f"Profile '{old_name}' renamed to '{new_name}'.", parent=self.settings_window)
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=on_ok).pack(side="left", expand=True, padx=5, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side="right", expand=True, padx=5, pady=10)
        self.settings_window.wait_window(dialog)


    def _delete_profile(self):
        """Deletes the selected profile."""
        selected_indices = self.profile_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a profile to delete.", parent=self.settings_window)
            return
        
        profile_name = self.profile_listbox.get(selected_indices[0])
        
        if profile_name == "Balanced" or len(self.config["profiles"]) == 1:
            messagebox.showerror("Error", "Cannot delete the last or default 'Balanced' profile.", parent=self.settings_window)
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete profile '{profile_name}'?", parent=self.settings_window):
            del self.config["profiles"][profile_name]
            if self.config["active_profile"] == profile_name:
                self.config["active_profile"] = "Balanced" # Fallback to Balanced if active profile is deleted
            self.save_config()
            self._populate_profile_listbox()
            self.profile_listbox.selection_set(0) # Select first profile after deletion
            self._load_profile_settings()
            self.profile_selector['values'] = list(self.config["profiles"].keys())
            self.update_tray_icon()
            messagebox.showinfo("Success", f"Profile '{profile_name}' deleted.", parent=self.settings_window)

    def _duplicate_profile(self):
        """Duplicates the selected profile."""
        selected_indices = self.profile_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a profile to duplicate.", parent=self.settings_window)
            return
        
        original_name = self.profile_listbox.get(selected_indices[0])
        new_name = f"{original_name} (Copy)"
        i = 1
        while new_name in self.config["profiles"]:
            new_name = f"{original_name} (Copy {i})"
            i += 1
        
        self.config["profiles"][new_name] = self.config["profiles"][original_name].copy()
        self.save_config()
        self._populate_profile_listbox()
        self.profile_listbox.selection_clear(0, tk.END)
        self.profile_listbox.selection_set(list(self.config["profiles"].keys()).index(new_name))
        self._load_profile_settings()
        self.profile_selector['values'] = list(self.config["profiles"].keys())
        self.update_tray_icon()
        messagebox.showinfo("Success", f"Profile '{original_name}' duplicated as '{new_name}'.", parent=self.settings_window)

    def _get_available_power_plans(self):
        """Gets a list of available Windows Power Plans."""
        plans = []
        try:
            result = subprocess.run(
                ["powercfg", "/list"],
                capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in result.stdout.splitlines():
                if "Power Scheme GUID:" in line:
                    parts = line.split("(")
                    if len(parts) > 1:
                        plan_name = parts[-1].replace(")", "").strip()
                        plans.append(plan_name)
        except Exception as e:
            logging.error(f"Error listing power plans: {e}", exc_info=True)
            plans = ["Balanced", "Power Saver", "High Performance"] # Fallback
        return plans

    def _save_general_settings(self):
        """Saves general settings like notifications."""
        self.config['show_notifications'] = self.show_notify_var.get()
        self.save_config()
        messagebox.showinfo("Success", "General settings saved.", parent=self.settings_window)

    def _add_app_trigger(self):
        """Adds a new application trigger."""
        app_name = self.new_app_trigger_name_var.get().strip()
        profile = self.new_app_trigger_profile_var.get().strip()
        if not app_name or not profile:
            messagebox.showwarning("Warning", "App name and profile cannot be empty.", parent=self.settings_window)
            return
        if profile not in self.config["profiles"]:
            messagebox.showerror("Error", "Selected profile does not exist.", parent=self.settings_window)
            return
        
        trigger = {"app_name": app_name.lower(), "profile": profile}
        if trigger not in self.config["auto_profile_switching"]["app_triggers"]:
            self.config["auto_profile_switching"]["app_triggers"].append(trigger)
            self.save_config()
            self._populate_app_triggers()
            messagebox.showinfo("Success", "App trigger added.", parent=self.settings_window)
            self.new_app_trigger_name_var.set("") # Clear input field
        else:
            messagebox.showwarning("Warning", "This app trigger already exists.", parent=self.settings_window)

    def _remove_app_trigger(self):
        """Removes the selected application trigger."""
        selected_indices = self.app_triggers_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select an app trigger to remove.", parent=self.settings_window)
            return
        
        idx = selected_indices[0]
        del self.config["auto_profile_switching"]["app_triggers"][idx]
        self.save_config()
        self._populate_app_triggers()
        messagebox.showinfo("Success", "App trigger removed.", parent=self.settings_window)

    def _populate_app_triggers(self):
        """Populates the app triggers listbox."""
        self.app_triggers_listbox.delete(0, tk.END)
        for trigger in self.config["auto_profile_switching"]["app_triggers"]:
            self.app_triggers_listbox.insert(tk.END, f"'{trigger['app_name']}' -> '{trigger['profile']}'")

    def _add_network_trigger(self):
        """Adds a new network trigger."""
        ssid = self.new_network_trigger_ssid_var.get().strip()
        profile = self.new_network_trigger_profile_var.get().strip()
        if not ssid or not profile:
            messagebox.showwarning("Warning", "SSID and profile cannot be empty.", parent=self.settings_window)
            return
        if profile not in self.config["profiles"]:
            messagebox.showerror("Error", "Selected profile does not exist.", parent=self.settings_window)
            return
        
        trigger = {"ssid": ssid, "profile": profile}
        if trigger not in self.config["auto_profile_switching"]["network_triggers"]:
            self.config["auto_profile_switching"]["network_triggers"].append(trigger)
            self.save_config()
            self._populate_network_triggers()
            messagebox.showinfo("Success", "Network trigger added.", parent=self.settings_window)
            self.new_network_trigger_ssid_var.set("") # Clear input field
        else:
            messagebox.showwarning("Warning", "This network trigger already exists.", parent=self.settings_window)

    def _remove_network_trigger(self):
        """Removes the selected network trigger."""
        selected_indices = self.network_triggers_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a network trigger to remove.", parent=self.settings_window)
            return
        
        idx = selected_indices[0]
        del self.config["auto_profile_switching"]["network_triggers"][idx]
        self.save_config()
        self._populate_network_triggers()
        messagebox.showinfo("Success", "Network trigger removed.", parent=self.settings_window)

    def _populate_network_triggers(self):
        """Populates the network triggers listbox."""
        self.network_triggers_listbox.delete(0, tk.END)
        for trigger in self.config["auto_profile_switching"]["network_triggers"]:
            self.network_triggers_listbox.insert(tk.END, f"'{trigger['ssid']}' -> '{trigger['profile']}'")

    def _add_time_trigger(self):
        """Adds a new time-based trigger."""
        start_time_str = self.new_time_trigger_start_var.get().strip()
        end_time_str = self.new_time_trigger_end_var.get().strip()
        profile = self.new_time_trigger_profile_var.get().strip()

        if not start_time_str or not end_time_str or not profile:
            messagebox.showwarning("Warning", "Start time, end time, and profile cannot be empty.", parent=self.settings_window)
            return
        if profile not in self.config["profiles"]:
            messagebox.showerror("Error", "Selected profile does not exist.", parent=self.settings_window)
            return
        
        try:
            # Validate time format
            datetime.strptime(start_time_str, "%H:%M")
            datetime.strptime(end_time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM (e.g., 22:00).", parent=self.settings_window)
            return

        trigger = {"start_time": start_time_str, "end_time": end_time_str, "profile": profile}
        if trigger not in self.config["auto_profile_switching"]["time_triggers"]:
            self.config["auto_profile_switching"]["time_triggers"].append(trigger)
            self.save_config()
            self._populate_time_triggers()
            messagebox.showinfo("Success", "Time trigger added.", parent=self.settings_window)
            self.new_time_trigger_start_var.set("") # Clear input field
            self.new_time_trigger_end_var.set("") # Clear input field
        else:
            messagebox.showwarning("Warning", "This time trigger already exists.", parent=self.settings_window)

    def _remove_time_trigger(self):
        """Removes the selected time-based trigger."""
        selected_indices = self.time_triggers_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a time trigger to remove.", parent=self.settings_window)
            return
        
        idx = selected_indices[0]
        del self.config["auto_profile_switching"]["time_triggers"][idx]
        self.save_config()
        self._populate_time_triggers()
        messagebox.showinfo("Success", "Time trigger removed.", parent=self.settings_window)

    def _populate_time_triggers(self):
        """Populates the time triggers listbox."""
        self.time_triggers_listbox.delete(0, tk.END)
        for trigger in self.config["auto_profile_switching"]["time_triggers"]:
            self.time_triggers_listbox.insert(tk.END, f"'{trigger['start_time']}-{trigger['end_time']}' -> '{trigger['profile']}'")

    def _update_process_list(self):
        """Updates the live process monitor list."""
        self.process_list_text.config(state="normal")
        self.process_list_text.delete("1.0", tk.END)
        
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                # Calculate CPU percent over a short interval for more accurate live data
                p.cpu_percent(interval=None) 
                processes.append(p)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Give a moment for CPU percents to be calculated after first call
        time.sleep(0.1) 
        
        # Get updated CPU percents
        processes_data = []
        for p in processes:
            try:
                cpu_percent = p.cpu_percent(interval=None) # Get latest CPU percent
                mem_info = p.memory_info()
                processes_data.append({
                    'pid': p.pid,
                    'name': p.name(),
                    'cpu_percent': cpu_percent,
                    'rss_mb': mem_info.rss / (1024 * 1024) # Resident Set Size in MB
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        sort_key = self.process_sort_var.get()
        if sort_key == "CPU":
            processes_data.sort(key=lambda x: x['cpu_percent'], reverse=True)
            header = f"{'PID':<8} {'CPU %':<8} {'RAM (MB)':<12} {'Process Name'}"
        else: # RAM
            processes_data.sort(key=lambda x: x['rss_mb'], reverse=True)
            header = f"{'PID':<8} {'RAM (MB)':<12} {'CPU %':<8} {'Process Name'}"
        
        self.process_list_text.insert(tk.END, header + "\n")
        self.process_list_text.insert(tk.END, "=" * len(header) + "\n")

        for p_data in processes_data[:50]: # Show top 50 processes
            if sort_key == "CPU":
                line = f"{p_data['pid']:<8} {p_data['cpu_percent']:.1f:<8} {p_data['rss_mb']:.1f:<12} {p_data['name']}"
            else:
                line = f"{p_data['pid']:<8} {p_data['rss_mb']:.1f:<12} {p_data['cpu_percent']:.1f:<8} {p_data['name']}"
            self.process_list_text.insert(tk.END, line + "\n")

        self.process_list_text.config(state="disabled")

    def _add_selected_process_to_kill_list(self):
        """Adds the process name from the entry box to the current profile's user_kill_apps list."""
        process_name = self.selected_process_to_add_var.get().strip()
        if not process_name:
            messagebox.showwarning("Warning", "Please enter a process name.", parent=self.settings_window)
            return
        
        profile_name = self.current_profile_name_var.get()
        if not profile_name or profile_name not in self.config["profiles"]:
            messagebox.showerror("Error", "Please select a profile in the 'Profiles' tab first.", parent=self.settings_window)
            return

        profile_settings = self.config["profiles"][profile_name]
        user_kill_apps = profile_settings.get("user_kill_apps", [])
        
        if process_name.lower() not in [app.lower() for app in user_kill_apps]:
            user_kill_apps.append(process_name)
            profile_settings["user_kill_apps"] = user_kill_apps
            self.save_config()
            self._load_profile_settings() # Refresh profile settings display
            messagebox.showinfo("Success", f"'{process_name}' added to '{profile_name}' kill list.", parent=self.settings_window)
            self.selected_process_to_add_var.set("") # Clear entry
        else:
            messagebox.showwarning("Warning", f"'{process_name}' is already in the kill list for '{profile_name}'.", parent=self.settings_window)


    def _export_config(self):
        """Exports the entire configuration to a JSON file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export PowerWhisper Configuration"
        )
        if file_path:
            try:
                # Create a backup before exporting
                with open(CONFIG_BACKUP_FILE, 'w') as backup_f:
                    json.dump(self.config, backup_f, indent=4)
                logging.info(f"Configuration backup created at {CONFIG_BACKUP_FILE}")

                with open(file_path, 'w') as f:
                    json.dump(self.config, f, indent=4)
                messagebox.showinfo("Export Complete", "Configuration exported successfully!", parent=self.settings_window)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export configuration: {e}", parent=self.settings_window)
                logging.error(f"Failed to export config: {e}", exc_info=True)

    def _import_config(self):
        """Imports configuration from a JSON file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Import PowerWhisper Configuration"
        )
        if file_path:
            if messagebox.askyesno("Confirm Import", "Importing will overwrite your current settings. Continue?", parent=self.settings_window):
                try:
                    # Create a backup before importing
                    with open(CONFIG_BACKUP_FILE, 'w') as backup_f:
                        json.dump(self.config, backup_f, indent=4)
                    logging.info(f"Configuration backup created at {CONFIG_BACKUP_FILE} before import.")

                    with open(file_path, 'r') as f:
                        imported_config = json.load(f)
                    
                    # Basic validation for imported config structure
                    if not isinstance(imported_config, dict) or "profiles" not in imported_config or "auto_profile_switching" not in imported_config:
                        messagebox.showerror("Import Error", "Invalid configuration file format. Missing 'profiles' or 'auto_profile_switching' keys.", parent=self.settings_window)
                        return

                    self.config = imported_config
                    self.save_config()
                    self.load_config() # Reload to ensure consistency and apply defaults for missing keys
                    
                    # Update all GUI elements
                    self._populate_profile_listbox()
                    if self.config["profiles"]:
                        self.profile_listbox.selection_set(0)
                        self._load_profile_settings()
                    self.profile_selector['values'] = list(self.config["profiles"].keys())
                    self.profile_selector_var.set(self.config["active_profile"])
                    self.auto_battery_var.set(self.config["auto_profile_switching"].get("battery_level", True))
                    self._populate_app_triggers()
                    self._populate_network_triggers()
                    self._populate_time_triggers()
                    self.show_notify_var.set(self.config.get("show_notifications", True))
                    self.update_tray_icon()
                    messagebox.showinfo("Import Complete", "Configuration imported successfully! Please review settings.", parent=self.settings_window)
                except (json.JSONDecodeError, IOError) as e:
                    messagebox.showerror("Import Error", f"Failed to import configuration: {e}", parent=self.settings_window)
                    logging.error(f"Failed to import config: {e}", exc_info=True)
                except Exception as e:
                    messagebox.showerror("Import Error", f"An unexpected error occurred during import: {e}", parent=self.settings_window)
                    logging.critical(f"Unexpected error during import: {e}", exc_info=True)


    def _update_dashboard(self):
        """Updates the dashboard tab with current system status."""
        if not (self.settings_window and self.settings_window.winfo_exists()):
            return
        try:
            battery = psutil.sensors_battery()
            mode_text = f"Active Profile: {self.active_profile_name}"
            admin_text = "Yes" if self.is_admin else "No (Limited Functionality)"
            
            status_text = f"  {mode_text}\n"
            if battery:
                plugged = "Charging" if battery.power_plugged else "On Battery"
                status_text += f"  Battery Level:      {int(battery.percent)}% ({plugged})\n"
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
                        status_text += f"  Time Remaining:     Calculating...\n"
                    else:
                        mins, secs = divmod(int(battery.secsleft), 60)
                        hours, mins = divmod(mins, 60)
                        status_text += f"  Time Remaining:     {hours:02d}h {mins:02d}m\n"
                else:
                    status_text += f"  Time Remaining:     Unlimited (Plugged In)\n"
            status_text += f"  Admin Rights:       {admin_text}\n"
            status_text += f"  Current Power Plan: {get_current_power_plan()}\n"
            status_text += f"  Current Wi-Fi SSID: {get_current_wifi_ssid() or 'Not Connected'}"
            
            self.status_label.config(text=status_text)
        except Exception as e:
            self.status_label.config(text="Could not read system status.")
            logging.error(f"Error updating GUI dashboard: {e}", exc_info=True)
        
        self.settings_window.after(POLL_INTERVAL_SECONDS * 1000, self._update_dashboard)

    def _update_battery_analytics(self):
        """Updates the battery analytics tab."""
        if not (self.settings_window and self.settings_window.winfo_exists()):
            return
        try:
            battery = psutil.sensors_battery()
            if battery:
                self.battery_stats_label.config(
                    text=f"  Current Level: {int(battery.percent)}%\n"
                         f"  Power Plugged: {'Yes' if battery.power_plugged else 'No'}\n"
                         f"  Time Remaining: {'Unlimited' if battery.secsleft == psutil.POWER_TIME_UNLIMITED else (f'{int(battery.secsleft // 3600):02d}h {int((battery.secsleft % 3600) // 60):02d}m' if battery.secsleft != psutil.POWER_TIME_UNKNOWN else 'Unknown')}\n"
                         f"  CPU Usage: {psutil.cpu_percent(interval=0.1)}%\n" # Short interval for live update
                         f"  RAM Usage: {psutil.virtual_memory().percent}%"
                )
            else:
                self.battery_stats_label.config(text=f"Battery information not available.\nCPU Usage: {psutil.cpu_percent(interval=0.1)}%\nRAM Usage: {psutil.virtual_memory().percent}%")

            self.battery_history_text.config(state="normal")
            self.battery_history_text.delete("1.0", tk.END)
            
            if not self.battery_history:
                self.battery_history_text.insert(tk.END, "No battery history recorded yet.")
            else:
                one_day_ago = datetime.now() - timedelta(hours=24)
                display_history = [e for e in self.battery_history if datetime.fromisoformat(e['timestamp']) >= one_day_ago]

                if not display_history:
                    self.battery_history_text.insert(tk.END, "No battery history in the last 24 hours.")
                else:
                    self.battery_history_text.insert(tk.END, "--- Battery Level Trend (Last 24h) ---\n")
                    min_p = min(e['percent'] for e in display_history)
                    max_p = max(e['percent'] for e in display_history)
                    
                    hourly_data = {}
                    for entry in display_history:
                        dt_obj = datetime.fromisoformat(entry['timestamp'])
                        hour_key = dt_obj.replace(minute=0, second=0, microsecond=0)
                        if hour_key not in hourly_data:
                            hourly_data[hour_key] = {'total_percent': 0, 'count': 0, 'profiles': set()}
                        hourly_data[hour_key]['total_percent'] += entry['percent']
                        hourly_data[hour_key]['count'] += 1
                        if entry.get('profile'):
                            hourly_data[hour_key]['profiles'].add(entry['profile'])

                    for dt_hour in sorted(hourly_data.keys()):
                        avg_percent = hourly_data[dt_hour]['total_percent'] / hourly_data[dt_hour]['count']
                        profile_info = f" ({', '.join(sorted(list(hourly_data[dt_hour]['profiles'])))})" if hourly_data[dt_hour]['profiles'] else ""
                        self.battery_history_text.insert(tk.END, f"{dt_hour.strftime('%Y-%m-%d %H:%M')} - {avg_percent:.0f}%{profile_info}\n")
                    self.battery_history_text.insert(tk.END, "----------------------------------------\n")
            
            self.battery_history_text.yview_moveto(1.0)
            self.battery_history_text.config(state="disabled")

        except Exception as e:
            self.battery_stats_label.config(text="Error loading analytics.")
            self.battery_history_text.config(state="normal")
            self.battery_history_text.delete("1.0", tk.END)
            self.battery_history_text.insert(tk.END, f"Error loading battery analytics: {e}")
            self.battery_history_text.config(state="disabled")
            logging.error(f"Error updating battery analytics: {e}", exc_info=True)
        
        self.settings_window.after(POLL_INTERVAL_SECONDS * 1000, self._update_battery_analytics)

    def _update_log_viewer(self):
        """Updates the log viewer tab."""
        if not (self.settings_window and self.settings_window.winfo_exists()):
            return
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        try:
            with open(LOG_FILE, 'r') as f:
                self.log_text.insert(tk.END, f.read())
        except Exception as e:
            self.log_text.insert(tk.END, f"Log file not created yet or inaccessible. Error: {e}")
        self.log_text.yview_moveto(1.0)
        self.log_text.config(state="disabled")

    # --- Background Tasks and Lifecycle ---
    def _monitor_battery_thread(self):
        """Monitors battery level and applies profiles based on battery and other triggers."""
        logging.info("Battery and automation monitoring thread started.")
        last_checked_ssid = None
        
        # Keep track of which apps were running in the previous cycle for app triggers
        last_running_apps = {p.info['name'].lower() for p in psutil.process_iter(['name'])}

        while not self.stop_event.is_set():
            try:
                battery = psutil.sensors_battery()
                current_percent = int(battery.percent) if battery and hasattr(battery, 'percent') else -1
                current_plugged = battery.power_plugged if battery and hasattr(battery, 'power_plugged') else False

                # Log battery history if percentage changed or every few intervals
                if current_percent != self.last_battery_percent or (len(self.battery_history) % 10 == 0):
                    self.battery_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "percent": current_percent,
                        "plugged": current_plugged,
                        "profile": self.active_profile_name
                    })
                    self.last_battery_percent = current_percent
                    self.save_battery_history()

                # Battery Level Based Switching
                if self.config["auto_profile_switching"].get("battery_level", True) and battery:
                    active_profile_settings = self.config["profiles"].get(self.active_profile_name, {})
                    eco_threshold = active_profile_settings.get("eco_threshold", 40)
                    restore_threshold = active_profile_settings.get("restore_threshold", 80)

                    if not current_plugged and current_percent <= eco_threshold and self.active_profile_name != "Max Battery": # Example: switch to Max Battery
                        logging.info(f"Battery at {current_percent}%, below {eco_threshold}%. Switching to 'Max Battery' profile.")
                        self.apply_profile("Max Battery")
                    elif current_plugged and current_percent >= restore_threshold and self.active_profile_name == "Max Battery": # Example: switch back to Balanced
                        logging.info(f"Battery at {current_percent}%, above {restore_threshold}% and charging. Switching to 'Balanced' profile.")
                        self.apply_profile("Balanced")
                
                # Application-Based Triggers
                current_running_apps = {p.info['name'].lower() for p in psutil.process_iter(['name'])}
                for trigger in self.config["auto_profile_switching"].get("app_triggers", []):
                    app_name = trigger["app_name"].lower()
                    target_profile = trigger["profile"]
                    
                    # Trigger if app just started and current profile is not target profile
                    if app_name in current_running_apps and app_name not in last_running_apps and self.active_profile_name != target_profile:
                        logging.info(f"Detected app '{app_name}' launched. Switching to '{target_profile}' profile.")
                        self.apply_profile(target_profile)
                last_running_apps = current_running_apps # Update for next cycle
                
                # Network-Based Triggers
                current_ssid = get_current_wifi_ssid()
                if current_ssid != last_checked_ssid: # Only check if SSID changed
                    for trigger in self.config["auto_profile_switching"].get("network_triggers", []):
                        ssid = trigger["ssid"]
                        target_profile = trigger["profile"]
                        if current_ssid == ssid and self.active_profile_name != target_profile:
                            logging.info(f"Connected to Wi-Fi '{ssid}'. Switching to '{target_profile}' profile.")
                            self.apply_profile(target_profile)
                    # If disconnected from all triggered SSIDs, revert to default? (Complex, for future)
                    last_checked_ssid = current_ssid

                # Time-Based Triggers
                current_time = datetime.now().strftime("%H:%M")
                for trigger in self.config["auto_profile_switching"].get("time_triggers", []):
                    start_time_str = trigger["start_time"]
                    end_time_str = trigger["end_time"]
                    target_profile = trigger["profile"]

                    # Convert times to comparable format (e.g., minutes from midnight)
                    start_minutes = int(start_time_str.split(':')[0]) * 60 + int(start_time_str.split(':')[1])
                    end_minutes = int(end_time_str.split(':')[0]) * 60 + int(end_time_str.split(':')[1])
                    current_minutes = int(current_time.split(':')[0]) * 60 + int(current_time.split(':')[1])

                    is_active_time_window = False
                    if start_minutes <= end_minutes: # Normal time window (e.g., 09:00 - 17:00)
                        is_active_time_window = start_minutes <= current_minutes < end_minutes
                    else: # Overnight time window (e.g., 22:00 - 07:00)
                        is_active_time_window = current_minutes >= start_minutes or current_minutes < end_minutes

                    if is_active_time_window and self.active_profile_name != target_profile:
                        logging.info(f"Time is {current_time}, within {start_time_str}-{end_time_str}. Switching to '{target_profile}' profile.")
                        self.apply_profile(target_profile)
                    # If outside time window and currently in that profile, switch back? (Complex, for future)

            except Exception as e:
                logging.error(f"Unhandled exception in automation thread: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL_SECONDS)
        logging.info("Battery and automation monitoring thread stopped.")

    def setup_hotkey(self):
        """Registers a global hotkey for quick profile toggling (e.g., between two specific profiles)."""
        try:
            # For simplicity, hotkey will toggle between "Balanced" and "Max Battery" for now
            # A more advanced hotkey could cycle through profiles or activate a specific one.
            keyboard.add_hotkey('ctrl+alt+p', self._hotkey_toggle_profile)
            logging.info("Global hotkey Ctrl+Alt+P registered.")
        except Exception as e:
            logging.error(f"Failed to register hotkey: {e}", exc_info=True)

    def _hotkey_toggle_profile(self):
        """Logic for the global hotkey."""
        if self.active_profile_name == "Balanced":
            self.apply_profile("Max Battery")
        else:
            self.apply_profile("Balanced")
        self.send_notification("Hotkey Triggered", f"Switched to '{self.active_profile_name}' profile.")

    def exit_app(self):
        """Handles application shutdown."""
        logging.info("Exit requested. Shutting down...")
        self.stop_event.set()
        if self.tray_icon: self.tray_icon.stop()
        self.root.quit()
        keyboard.remove_all_hotkeys()
        logging.info("Shutdown complete.")

    def run(self):
        """Starts the main application loop."""
        # Apply the initial active profile on startup
        self.apply_profile(self.active_profile_name) 
        self.setup_hotkey()
        self.setup_tray_icon()
        monitor_thread = threading.Thread(target=self._monitor_battery_thread, daemon=True)
        monitor_thread.start()
        self.tray_icon.run_detached()
        self.root.mainloop()

# --- Application Entry Point ---
if __name__ == "__main__":
    app = PowerWhisperApp()
    if not app.is_admin:
        messagebox.showwarning(
            f"{APP_NAME} - Permissions Warning",
            "PowerWhisper is not running as an administrator.\n\n"
            "Key features like toggling Wi-Fi/Bluetooth, killing processes, changing power plans, and stopping Windows services will not work correctly.\n\n"
            "For full functionality, please run as administrator."
        )
    try:
        app.run()
    except Exception as e:
        logging.critical(f"A fatal error occurred: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"A fatal error occurred: {e}\n\nPlease check {LOG_FILE} for details.")
