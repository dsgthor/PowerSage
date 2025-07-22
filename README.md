# ⚡ PowerWhisper - Intelligent Battery Saver and System Optimizer for Windows

**PowerWhisper** is a Python-based, self-contained Windows utility that monitors your battery level and system state, automatically applying power-saving settings when thresholds are met. It provides an intuitive GUI, system tray integration, and fully customizable features including Wi-Fi/Bluetooth control, process termination, brightness management, and notification delivery.

Designed for laptops, this tool is ideal for power users, developers, and minimalists who want **granular control over power-saving behaviors** without bloatware or OEM limitations.

---

## 📦 Features Overview

| Feature                      | Description |
|-----------------------------|-------------|
| 🔋 Auto Eco Mode             | Activates power-saving actions automatically below a battery threshold |
| ⚡ Manual Toggle             | Instantly enable or disable Eco Mode using tray menu or hotkey |
| 🖥️ Brightness Reduction      | Lowers screen brightness to conserve power |
| 📶 WiFi Control              | Disables Wi-Fi in Eco Mode (optional) |
| 📡 Bluetooth Control         | Disables Bluetooth via PowerShell (optional) |
| ❌ Process Killer            | Terminates selected apps/processes in Eco Mode |
| 💾 Persistent Settings       | JSON-based configuration saved and loaded automatically |
| 🔧 GUI Settings Panel        | Fully interactive settings editor using Tkinter |
| 🧠 System Tray Integration   | Pystray-based tray icon for background control |
| 🔔 Notifications             | Uses `plyer` for non-intrusive battery alerts |
| 🧩 Global Hotkey             | Ctrl + Alt + P toggles Eco Mode from anywhere |
| 📃 Logging                   | Detailed logging to `powerwhisper.log` for all actions and errors |
| 🔐 Admin Awareness           | Gracefully handles lack of privileges and logs warnings |

---

## 💻 System Requirements

- **Operating System**: Windows 10 or 11
- **Python Version**: 3.10 or newer (tested on 3.12)
- **Architecture**: x64 (if using compiled `.exe`)
- **Privileges**: Some features require administrator privileges

---

## 🛠️ Dependencies

Installed automatically via pip:

- `psutil` – Battery, process, and system metrics
- `pystray` – System tray icon support
- `Pillow` – Required for icon rendering in pystray
- `plyer` – Cross-platform notification system
- `keyboard` – Global hotkey support
- `tkinter` – GUI (comes with Python but must be present)

> Ensure all dependencies are available in your Python environment.

---

## 🔧 Installation & Usage

### Option 1: Run via Python (Development)

1. Clone or download the project:
   ```bash
   git clone https://github.com/yourusername/powerwhisper.git
   cd powerwhisper
   ```

2. Install dependencies:
   ```bash
   pip install psutil pystray pillow plyer keyboard
   ```

3. Run the app:
   ```bash
   python powerwhisper_complete5.py
   ```

---

### Option 2: Run as `.exe` (No Python Required)

1. Install [PyInstaller](https://pyinstaller.org/):
   ```bash
   pip install pyinstaller
   ```

2. Build the standalone app:
   ```bash
   py -m PyInstaller --noconfirm --onefile --windowed powerwhisper_complete5.py
   ```

3. Find the built app in:
   ```
   dist/powerwhisper_complete5.exe
   ```

Double-click the `.exe` or add it to Windows startup (see below).

---

## 🚀 Add to Windows Startup

### ✅ Recommended: Task Scheduler (with Admin Rights)

1. Open **Task Scheduler**
2. Click **Create Task** (not Basic Task)
3. Set:
   * Name: `PowerWhisper`
   * Run with highest privileges: ✅
   * Trigger: At log on
   * Action: Start program → your `.exe` file
4. Save and test by right-click → **Run**

This ensures Eco Mode can fully control WiFi/Bluetooth and kill processes.

---

## ⚙️ GUI Features

Launch the GUI by:
* Right-clicking the tray icon → `Settings`
* Or automatically on startup if you added `self.show_gui()` in code

### GUI Panels:
* **Battery Info Panel**: Shows battery % and charging state
* **Threshold Settings**: Set Eco and Restore thresholds (percent)
* **Feature Toggles**:
  * Auto Eco Mode
  * Reduce Brightness
  * Disable Wi-Fi
  * Disable Bluetooth
  * Show Notifications
* **App Killer List**: Modify process names to be killed in Eco Mode
* **Buttons**:
  * Save Settings
  * Manually Trigger Eco Mode
  * Kill Heavy Apps Now

---

## 🔐 Admin Privilege Behavior

Some system actions require elevation:

| Feature                       | Requires Admin?           | Fallback                |
| ----------------------------- | ------------------------- | ----------------------- |
| Wi-Fi toggle (netsh)          | ✅ Yes                     | Skipped, warning logged |
| Bluetooth toggle (PowerShell) | ✅ Yes                     | Skipped, warning logged |
| Kill other processes          | ✅ Yes (unless user-owned) | Logs AccessDenied       |
| Brightness control            | ❌ Usually works (via WMI) | -                       |

---

## 🔁 Automatic Behavior Logic

1. A background thread polls the battery every 30 seconds.
2. If:
   * `battery.percent <= eco_threshold`
   * AND `not plugged in`
   * → Trigger Eco Mode
3. If:
   * `battery.percent >= restore_threshold`
   * OR `plugged in`
   * → Restore settings (undo Eco Mode)
4. GUI updates reflect live status.
5. All events are logged in `powerwhisper.log`.

---

## 🔑 Hotkey Support

* Global hotkey: **Ctrl + Alt + P**
* Toggles Eco Mode instantly, from any application

Note: May conflict with other software. Change key combo in the script if needed.

---

## 🧠 Configuration File

### Location:
* Created in the working directory:
  ```
  powerwhisper_config.json
  ```

### Example:
```json
{
  "eco_threshold": 35,
  "restore_threshold": 80,
  "kill_apps": ["chrome.exe", "spotify.exe", "teams.exe"],
  "disable_wifi": true,
  "disable_bluetooth": true,
  "reduce_brightness": true,
  "auto_eco_mode": true,
  "show_notifications": true
}
```

### Notes:
* Edits can be made via GUI or manually
* Reloaded at every startup

---

## 📜 Logging

All operational logs and errors are stored in:
```
powerwhisper.log
```

Logged actions include:
* Eco Mode activation/restoration
* Kill attempts (with success or permission failure)
* Wi-Fi and Bluetooth toggle results
* GUI interactions
* Notification delivery failures
* Uncaught exceptions (e.g., GUI crashes)

---

## 🧪 Troubleshooting

| Problem                           | Solution                                                          |
| --------------------------------- | ----------------------------------------------------------------- |
| GUI crashes when opened           | Ensure `Tk()` root is created, don't pass widget to `ttk.Style()` |
| Tray icon missing                 | Check system tray overflow / run as GUI app                       |
| Wi-Fi or Bluetooth doesn't toggle | Ensure `.exe` is run **as administrator**                         |
| App doesn't start at login        | Use **Task Scheduler**, not `shell:startup` if admin needed       |
| Brightness not changing           | Some machines block WMI; test manually                            |
| Hotkey not working                | Conflicting app may override it; edit `keyboard.add_hotkey()`     |

---

## ❓ FAQ

**Q:** Can I change the polling frequency?  
**A:** Yes, modify the `time.sleep()` in the `monitor_battery` thread (default: 30 sec).

**Q:** Can I add sound or haptics?  
**A:** You can integrate sound via `winsound` or system APIs — it's not included by default.

**Q:** Is the app open source?  
**A:** Yes. MIT Licensed. Modify, extend, or repackage freely.

---

## 📃 License

MIT License.  
You may use, modify, and distribute this software freely. Attribution is appreciated but not required.

---

## 👨‍💻 Author

**PowerWhisper** was created as a lightweight alternative to bloated OEM power tools, with direct control over system behavior via Python and Windows APIs.

Contributions, forks, and feature requests are welcome.

---

## 📎 Project Structure

```
powerwhisper_complete5.py         # Main app script
powerwhisper_config.json          # Auto-generated config
powerwhisper.log                  # Runtime logs
dist/                             # Output folder after PyInstaller build
```

---

## 🧩 Future Improvements (Roadmap)

* Scheduler-based profile switching
* Cloud sync of configs
* Auto-detection of heavy apps by CPU/RAM
* GUI theming and animations
* Windows toast notifications (native)