# ⚡ PowerWhisper v2.0 - Advanced Intelligent Battery Saver & System Optimizer

**PowerWhisper v2** is a comprehensive Python-based Windows utility that intelligently manages your laptop's power consumption through customizable profiles, smart automation, and real-time system monitoring. This major update introduces **profile-based power management**, **advanced automation triggers**, and a **professional dark-themed GUI**.

Perfect for power users, developers, gamers, and professionals who demand **granular control** over their system's power behavior without the limitations of OEM bloatware.

---

## 🆕 What's New in v2.0

### 🎯 **Profile-Based Power Management**
- **Multiple Power Profiles**: Create unlimited custom profiles (Balanced, Max Battery, Gaming, Work, etc.)
- **Per-Profile Settings**: Each profile has independent brightness, Wi-Fi, Bluetooth, app killing, and Windows power plan settings
- **Smart Profile Switching**: Automatic or manual profile activation
- **Profile Import/Export**: Backup and share your configurations

### 🤖 **Advanced Automation Engine**
- **Battery Level Triggers**: Auto-switch profiles based on battery percentage and charging state
- **Application Launch Triggers**: Automatically activate profiles when specific apps are detected (e.g., Gaming profile when Steam launches)
- **Network-Based Triggers**: Switch profiles based on Wi-Fi SSID (e.g., Work profile at office, Power Saver at home)
- **Time-Based Triggers**: Schedule profile activation during specific time windows (e.g., Quiet Hours profile at night)

### 🎨 **Professional GUI Overhaul**
- **Modern Dark Theme**: Professional dark UI with accent colors and proper contrast
- **Tabbed Interface**: Dashboard, Profiles, Automation, App Killer, Analytics, Log Viewer, and Advanced tabs
- **Scrollable Content**: Handle large amounts of data with smooth scrolling
- **Interactive Tooltips**: Hover help for all settings and controls
- **Live Process Monitor**: Real-time CPU and RAM monitoring with sorting options

### 📊 **Analytics & Monitoring**
- **Battery History Tracking**: 24-hour battery level trend analysis
- **System Dashboard**: Live battery stats, CPU/RAM usage, and system status
- **Comprehensive Logging**: Detailed log viewer with real-time updates
- **Smart Notifications**: Non-intrusive desktop notifications for all actions

### 🛠️ **Enhanced System Control**
- **Windows Services Management**: Start/stop system services per profile (Print Spooler, Superfetch, etc.)
- **Improved Brightness Control**: More reliable screen brightness management
- **Better Error Handling**: Graceful failure handling with user-friendly error messages
- **Configuration Validation**: Automatic config file validation and repair

---

## 📦 Core Features

| Feature | Description | Admin Required |
|---------|-------------|----------------|
| 🔋 **Profile-Based Power Management** | Create unlimited custom power profiles with independent settings | Partial |
| 🤖 **Smart Automation** | Auto-switch profiles based on battery, apps, network, or time | No |
| 🖥️ **Brightness Control** | Adjustable screen brightness per profile | Yes* |
| 📶 **Wi-Fi Management** | Disable/enable Wi-Fi adapter per profile | Yes |
| 📡 **Bluetooth Control** | Toggle Bluetooth via PowerShell per profile | Yes |
| ⚡ **Windows Power Plans** | Set High Performance, Balanced, or Power Saver per profile | Yes |
| 🗂️ **Windows Services** | Start/stop system services (Spooler, Superfetch, etc.) per profile | Yes |
| ❌ **Smart App Killer** | Terminate resource-heavy apps with predefined + custom lists | Partial |
| 🔔 **Desktop Notifications** | Non-intrusive alerts for all power management actions | No |
| ⌨️ **Global Hotkey** | Ctrl+Alt+P for instant profile switching | No |
| 📊 **System Analytics** | Battery history, CPU/RAM monitoring, live process list | No |
| 🎨 **Professional GUI** | Modern dark-themed interface with tabbed navigation | No |
| 💾 **Configuration Management** | Import/export settings, automatic backup/restore | No |

*Some systems may allow brightness control without admin rights

---

## 🔧 Installation & Setup

### Prerequisites
- **Windows 10/11** (x64 recommended)
- **Python 3.10+** (if running from source)
- **Administrator privileges** (recommended for full functionality)

### Method 1: Download Executable (Recommended)
1. Download the latest `PowerWhisper-v2.exe` from [Releases](https://github.com/yourusername/powerwhisper/releases)
2. Run as Administrator for full functionality
3. The app will automatically create configuration files in the same directory

### Method 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/powerwhisper.git
cd powerwhisper

# Install dependencies
pip install psutil pystray pillow plyer keyboard

# Run the application
python Powersage-v2.py
```

### Method 3: Build Your Own Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico Powersage-v2.py

# Find executable in dist/ folder
```

---

## 🚀 Quick Start Guide

### 1. **First Launch**
- Run PowerWhisper (preferably as Administrator)
- The app starts with a default "Balanced" profile
- Look for the ⚡ icon in your system tray

### 2. **Access Settings**
- Right-click the tray icon → **Settings**
- Or use the global hotkey: **Ctrl+Alt+P**

### 3. **Create Your First Profile**
- Go to **Profiles** tab
- Click **Add New** to create a custom profile
- Configure settings like brightness, Wi-Fi control, apps to kill
- Click **Save Profile Settings**

### 4. **Set Up Automation** (Optional)
- Go to **Automation** tab
- Enable **Battery Level Based Profile Switching**
- Add application triggers (e.g., Steam → Gaming profile)
- Add network triggers (e.g., Office Wi-Fi → Work profile)
- Add time triggers (e.g., 10 PM → Quiet Hours profile)

### 5. **Monitor & Analyze**
- **Dashboard**: View live system status
- **App Killer**: Monitor processes and add apps to kill lists
- **Analytics**: Track battery usage patterns
- **Log Viewer**: Troubleshoot issues

---

## 🎛️ Profile Configuration Guide

### Default Profiles Included:

#### 🔄 **Balanced** (Default)
- Eco Threshold: 40%
- Restore Threshold: 80%
- Smart Kill: Enabled
- Brightness: 70%
- Power Plan: Balanced

#### 🔋 **Max Battery** (Power Saver)
- Eco Threshold: 99% (always active)
- Disables Wi-Fi and Bluetooth
- Brightness: 20%
- Kills additional apps
- Power Plan: Power Saver
- Stops non-essential Windows services

#### 🎮 **Gaming** (Performance)
- Eco Threshold: 0% (never activates eco mode)
- Smart Kill: Disabled
- Brightness: 100%
- Power Plan: High Performance
- No service restrictions

### Creating Custom Profiles:
1. **Navigate**: Profiles tab → Add New
2. **Configure Thresholds**: Set when the profile activates/deactivates
3. **Power Settings**: Choose brightness level, Windows power plan
4. **Network Control**: Enable/disable Wi-Fi and Bluetooth
5. **App Management**: Enable smart kill + add custom apps to terminate
6. **Service Control**: Select Windows services to stop when profile is active
7. **Save**: Apply settings to the profile

---

## 🤖 Automation System

### 🔋 **Battery Level Automation**
Automatically switches profiles based on battery percentage and charging status:
```
Battery ≤ 40% + Unplugged → Max Battery Profile
Battery ≥ 80% + Plugged In → Balanced Profile
```

### 📱 **Application Triggers**
Launch specific profiles when target applications are detected:
```
Steam.exe detected → Gaming Profile
Teams.exe detected → Work Profile
OBS.exe detected → Streaming Profile
```

### 🌐 **Network Triggers**
Switch profiles based on connected Wi-Fi network:
```
"Office-WiFi" → Work Profile
"Home-5G" → Balanced Profile
"Cafe-Guest" → Max Battery Profile
```

### ⏰ **Time-Based Triggers**
Activate profiles during specific time windows:
```
22:00-07:00 → Quiet Hours Profile
09:00-17:00 → Work Profile (weekdays)
```

---

## 🎯 Smart App Killer

### Built-in Smart Kill List:
PowerWhisper includes a curated list of common resource-heavy applications:

**Communication & Social:**
- Discord, Teams, Slack, Zoom

**Game Launchers & Overlays:**
- Steam, Epic Games, Battle.net, Origin, Riot Client

**Media Players:**
- Spotify, iTunes, Windows Music

**Cloud Sync & Updaters:**
- OneDrive, Adobe Creative Cloud, Update services

**System Apps:**
- Cortana, Your Phone, Game Bar, GeForce Overlay

### Custom App Management:
- **Add via Process Monitor**: View live processes, click to add to kill list
- **Manual Entry**: Type executable names directly
- **Per-Profile Customization**: Different apps killed for different profiles

---

## ⚙️ Windows Services Control

Control system services to maximize battery life:

| Service | Description | Impact |
|---------|-------------|---------|
| **Print Spooler** | Printing service | Medium battery savings |
| **Superfetch/SysMain** | Memory pre-loading | High battery/RAM savings |
| **Windows Search** | File indexing | Medium CPU/battery savings |
| **Themes** | Visual themes | Low battery savings |
| **Xbox Services** | Gaming-related services | Medium battery savings |
| **Delivery Optimization** | Windows Update optimization | Medium network/battery savings |

> ⚠️ **Caution**: Only disable services you understand. PowerWhisper attempts to restore services when switching profiles.

---

## 📊 Analytics & Monitoring

### **Real-Time Dashboard**
- Current battery level and charging status
- Active profile information
- Administrator rights status
- Current Windows power plan
- Connected Wi-Fi network

### **Battery History Tracking**
- 24-hour battery level trends
- Profile activation history
- Charging pattern analysis
- Export data for external analysis

### **Live Process Monitor**
- Real-time CPU and RAM usage by process
- Sort by CPU or memory consumption
- Quick-add processes to kill lists
- Identify resource-heavy applications

### **System Logs**
- Comprehensive activity logging
- Error tracking and debugging
- Export logs for support
- Real-time log viewer in GUI

---

## ⌨️ Keyboard Shortcuts & Hotkeys

| Shortcut | Action |
|----------|--------|
| **Ctrl+Alt+P** | Toggle between Balanced and Max Battery profiles |
| **Mouse Wheel** | Scroll in any scrollable GUI section |

> 💡 **Tip**: Global hotkeys work from any application. Customize the key combination in the source code if needed.

---

## 🔒 Security & Privacy

- **Local-Only Operation**: No data sent to external servers
- **Configuration Encryption**: None (JSON plaintext for user editability)
- **Process Access**: Only reads process names, no sensitive data harvesting
- **Network Access**: None required (works completely offline)
- **File System Access**: Limited to app directory for config and logs

---

## 🛠️ Advanced Configuration

### **Configuration Files**
- `powerwhisper_config.json` - Main configuration
- `powerwhisper_config_backup.json` - Automatic backup
- `powerwhisper_battery_history.json` - Battery analytics data
- `powerwhisper.log` - Application logs

### **Manual Configuration Editing**
While the GUI provides full functionality, you can manually edit `powerwhisper_config.json`:

```json
{
    "active_profile": "Balanced",
    "profiles": {
        "Custom Work": {
            "eco_threshold": 50,
            "restore_threshold": 85,
            "enable_smart_kill": true,
            "user_kill_apps": ["chrome.exe", "slack.exe"],
            "disable_wifi": false,
            "disable_bluetooth": true,
            "reduce_brightness": true,
            "brightness_level": 60,
            "windows_power_plan": "Balanced",
            "stop_services": [
                {"service_name": "Spooler", "display_name": "Print Spooler"}
            ]
        }
    },
    "auto_profile_switching": {
        "battery_level": true,
        "app_triggers": [
            {"app_name": "steam.exe", "profile": "Gaming"}
        ],
        "network_triggers": [
            {"ssid": "Office-WiFi", "profile": "Work"}
        ],
        "time_triggers": [
            {"start_time": "22:00", "end_time": "07:00", "profile": "Quiet Hours"}
        ]
    },
    "show_notifications": true
}
```

### **Command Line Arguments**
Currently, PowerWhisper v2 runs entirely through GUI. Future versions may include CLI support.

---

## 🚨 Troubleshooting Guide

### **Common Issues**

#### **🔐 Permission Errors**
**Problem**: "Access Denied" when toggling Wi-Fi/Bluetooth or killing processes
**Solution**: 
- Run PowerWhisper as Administrator
- Use Task Scheduler for startup with "highest privileges"
- Check Windows UAC settings

#### **⚡ Tray Icon Missing**
**Problem**: Can't find PowerWhisper in system tray
**Solution**:
- Check Windows notification area overflow
- Ensure app isn't crashed (check Task Manager)
- Restart application as Administrator

#### **🔆 Brightness Not Changing**
**Problem**: Screen brightness doesn't adjust
**Solution**:
- Run as Administrator
- Check if your display driver supports WMI brightness control
- Some external monitors don't support software brightness control
- Try manually: `powershell "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 50)"`

#### **📱 App Automation Not Working**
**Problem**: Profiles don't switch when launching specific apps
**Solution**:
- Ensure automation is enabled in the Automation tab
- Check that app names exactly match process names (case-insensitive)
- Verify the target profile exists
- Check logs for automation events

#### **🌐 Network Triggers Not Activating**
**Problem**: Profiles don't switch when connecting to specific Wi-Fi networks
**Solution**:
- Ensure SSID name exactly matches (case-sensitive)
- Check that Wi-Fi is actually connected (not just scanning)
- Verify network trigger is properly configured
- Test with `netsh wlan show interfaces` to see current SSID

#### **📁 Configuration Lost After Update**
**Problem**: Settings reset after updating PowerWhisper
**Solution**:
- Check for `powerwhisper_config_backup.json` in the app directory
- Use Import Configuration feature to restore from backup
- Keep regular exports of your configuration

### **Diagnostic Commands**

Run these PowerShell commands to diagnose system-level issues:

```powershell
# Check available power plans
powercfg /list

# Check current power plan
powercfg /getactivescheme

# Check Wi-Fi interfaces
netsh wlan show interfaces

# Check Bluetooth devices
Get-PnpDevice -Class Bluetooth

# Check Windows services status
Get-Service | Where-Object {$_.Name -in @("Spooler", "SysMain", "WSearch")}

# Test WMI brightness control
(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 75)
```

---

## 🏃‍♂️ Adding to Windows Startup

### **Method 1: Task Scheduler (Recommended)**
1. Open **Task Scheduler** as Administrator
2. **Create Task** (not Basic Task)
3. **General Tab**:
   - Name: `PowerWhisper`
   - ✅ **Run with highest privileges**
   - Run whether user is logged on or not
4. **Triggers Tab**:
   - New → **At log on** → Specific user
5. **Actions Tab**:
   - New → **Start a program** → Browse to `PowerWhisper.exe`
6. **Settings Tab**:
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
7. **Save** and test with **Run**

### **Method 2: Registry Startup (Basic)**
```cmd
# Add to registry (run as Administrator)
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "PowerWhisper" /t REG_SZ /d "C:\Path\To\PowerWhisper.exe"
```

### **Method 3: Startup Folder (Limited)**
1. Press `Win+R` → type `shell:startup`
2. Copy PowerWhisper shortcut to the opened folder
3. ⚠️ **Note**: Limited functionality without admin rights

---

## 📋 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10 build 1903+ or Windows 11
- **Architecture**: x64 (recommended) or x86
- **RAM**: 50MB+ available
- **Storage**: 10MB for application + logs
- **Python**: 3.10+ (if running from source)

### **Recommended Environment**
- **Administrator privileges** for full feature access
- **Modern laptop** with WMI-compatible brightness control
- **Wi-Fi adapter** for network-based automation
- **Bluetooth adapter** for Bluetooth management features

### **Dependencies (Auto-Installed)**
```bash
psutil>=5.9.0      # System and process utilities
pystray>=0.19.4    # System tray integration
Pillow>=9.5.0      # Image processing for tray icons
plyer>=2.1.0       # Cross-platform notifications
keyboard>=0.13.5   # Global hotkey support
```

---

## 🎮 Usage Examples

### **Example 1: Gaming Setup**
Create a "Gaming" profile that:
- Never activates eco mode (threshold: 0%)
- Disables smart app killing
- Sets brightness to 100%
- Uses "High Performance" power plan
- Automatically activates when Steam launches

### **Example 2: Office Work**
Create a "Work" profile that:
- Activates at 60% battery
- Keeps Wi-Fi enabled but disables Bluetooth
- Kills personal apps (Spotify, Discord)
- Stops Print Spooler and Xbox services
- Automatically activates on office Wi-Fi

### **Example 3: Travel Mode**
Create a "Travel" profile that:
- Activates at 70% battery
- Disables both Wi-Fi and Bluetooth
- Aggressive app killing (browsers, media players)
- Brightness at 30%
- Stops all non-essential services

### **Example 4: Presentation Mode**
Create a "Presentation" profile that:
- Never dims screen (brightness: 100%)
- Disables all notifications
- Kills communication apps
- Activates during business hours (09:00-17:00)

---

## 🔍 Process Kill Lists

### **Smart Kill List (Built-in)**
PowerWhisper includes an intelligent kill list of common resource-heavy applications:

**Communication**: Discord, Teams, Slack, Zoom  
**Gaming**: Steam, Epic Games, Battle.net, Origin, Riot Client, GOG Galaxy  
**Media**: Spotify, iTunes, Windows Music  
**Cloud Sync**: OneDrive, Adobe Creative Cloud  
**System**: Cortana, Your Phone, Game Bar, GeForce Experience  

### **Custom Kill Lists**
Add your own applications per profile:
- Navigate to **Profiles** tab
- Select your profile
- Add executable names in "Additional Apps to Kill"
- Or use **App Killer** tab to select from running processes

### **Kill List Best Practices**
- ✅ **Safe to Kill**: Media players, chat apps, game launchers
- ⚠️ **Use Caution**: Browsers with important work, IDEs with unsaved code
- ❌ **Never Kill**: System processes, antivirus, drivers

---

## 📈 Advanced Automation Logic

### **Battery Level Automation Algorithm**
```python
if not battery.power_plugged and battery.percent <= eco_threshold:
    activate_profile("Max Battery")  # Or configured eco profile
elif battery.power_plugged and battery.percent >= restore_threshold:
    restore_to_previous_profile()
```

### **Application Detection Logic**
```python
current_apps = get_running_processes()
for trigger in app_triggers:
    if trigger.app_name in current_apps and trigger.app_name not in previous_apps:
        activate_profile(trigger.profile)
```

### **Network Detection Logic**
```python
current_ssid = get_wifi_ssid()
if current_ssid != previous_ssid:
    for trigger in network_triggers:
        if current_ssid == trigger.ssid:
            activate_profile(trigger.profile)
```

### **Time-Based Logic**
```python
current_time = datetime.now().time()
for trigger in time_triggers:
    if is_within_time_window(current_time, trigger.start_time, trigger.end_time):
        if current_profile != trigger.profile:
            activate_profile(trigger.profile)
```

---

## 🔧 API Reference (For Developers)

### **Core Classes**

#### **PowerWhisperApp**
Main application class handling GUI, configuration, and system integration.

**Key Methods:**
- `apply_profile(profile_name)` - Activates a specific profile
- `set_brightness(level)` - Sets screen brightness (0-100)
- `toggle_network_adapter(adapter, enable)` - Controls network adapters
- `toggle_bluetooth(enable)` - Controls Bluetooth state
- `kill_processes(process_list)` - Terminates specified processes
- `set_power_plan(plan_name)` - Changes Windows power plan

#### **Configuration Structure**
```python
{
    "active_profile": str,
    "profiles": {
        profile_name: {
            "eco_threshold": int,
            "restore_threshold": int,
            "enable_smart_kill": bool,
            "user_kill_apps": [str],
            "disable_wifi": bool,
            "disable_bluetooth": bool,
            "reduce_brightness": bool,
            "brightness_level": int,
            "windows_power_plan": str,
            "stop_services": [{"service_name": str, "display_name": str}]
        }
    },
    "auto_profile_switching": {
        "battery_level": bool,
        "app_triggers": [{"app_name": str, "profile": str}],
        "network_triggers": [{"ssid": str, "profile": str}],
        "time_triggers": [{"start_time": str, "end_time": str, "profile": str}]
    },
    "show_notifications": bool
}
```

---

## 🐛 Known Issues & Limitations

### **Current Limitations**
- **Brightness Control**: Some external monitors don't support software brightness adjustment
- **Service Restoration**: Service restoration between profiles may not be 100% reliable
- **Network Detection**: Requires active Wi-Fi connection (doesn't detect Ethernet)
- **Time Triggers**: No timezone awareness (uses system local time)
- **App Detection**: Only detects running processes, not windowed/minimized state

### **Future Improvements**
- **Multi-Monitor Brightness**: Individual brightness control per monitor
- **Smart Service Tracking**: Remember original service states for better restoration
- **Ethernet Detection**: Support for wired network triggers
- **Process Window State**: Detect focused/background application states
- **Cloud Sync**: Optional cloud backup of configurations
- **Scheduled Profiles**: Recurring time-based profiles (weekdays, weekends)

---

## 🆘 Getting Help

### **Log Analysis**
1. Navigate to **Log Viewer** tab in settings
2. Look for ERROR or WARNING entries
3. Check timestamps around when issues occurred
4. Export logs using **Advanced** → **Export Configuration**

### **Support Channels**
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/powerwhisper/issues)
- **Discussions**: [Community support and tips](https://github.com/yourusername/powerwhisper/discussions)
- **Wiki**: [Extended documentation and guides](https://github.com/yourusername/powerwhisper/wiki)

### **Before Reporting Issues**
1. ✅ Run as Administrator
2. ✅ Check the **Log Viewer** tab for error messages
3. ✅ Try with default profiles first
4. ✅ Export your configuration for sharing (remove sensitive SSIDs)
5. ✅ Include your Windows version and hardware details

---

## 🔄 Migration from v1.x

### **Automatic Migration**
PowerWhisper v2 automatically detects v1 configurations and creates equivalent profiles. Your settings will be preserved.

### **New Features to Explore**
- **Multiple Profiles**: Create specialized profiles for different scenarios
- **App Triggers**: Set up automatic Gaming mode when launching games
- **Network Automation**: Configure work and home profiles
- **Service Management**: Fine-tune Windows services for maximum battery life
- **Analytics**: Review your battery usage patterns

### **Breaking Changes**
- Configuration file format updated (automatic migration included)
- Hotkey now toggles between Balanced and Max Battery (was simple eco mode toggle)
- Some advanced features require recreation in the new profile system

---

## 💡 Pro Tips & Best Practices

### **Profile Strategy**
- **Create profiles for different scenarios**: Work, Gaming, Travel, Presentation
- **Use descriptive names**: "Conference Call Mode" vs "Profile 3"
- **Test profiles manually** before enabling automation
- **Regular exports**: Backup configurations before major changes

### **Automation Setup**
- **Start simple**: Enable battery-level automation first
- **Test app triggers**: Launch target apps to verify profile switching
- **Network trigger accuracy**: Use exact SSID names (check in Windows Wi-Fi settings)
- **Time trigger overlap**: Avoid conflicting time windows between profiles

### **Performance Optimization**
- **Review kill lists regularly**: Remove apps you no longer use
- **Monitor service impact**: Use Task Manager to verify service stopping benefits
- **Battery history analysis**: Use analytics to identify the most effective settings
- **Gradual brightness reduction**: Don't jump from 100% to 20% immediately

### **Troubleshooting Workflow**
1. **Check Dashboard**: Verify current profile and system status
2. **Review Logs**: Look for recent error messages or warnings
3. **Test Manual Switching**: Try activating profiles manually first
4. **Verify Admin Rights**: Ensure elevated privileges for system-level features
5. **Reset to Defaults**: Import a fresh configuration if issues persist

---

## 📄 License

```
MIT License

Copyright (c) 2025 PowerWhisper Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

PowerWhisper is an open-source project welcoming contributions!

### **How to Contribute**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### **Contribution Guidelines**
- **Code Style**: Follow PEP 8 Python style guidelines
- **Documentation**: Update README and add docstrings for new functions
- **Testing**: Test on different Windows versions and hardware configurations
- **Error Handling**: Include comprehensive error handling and logging
- **Backward Compatibility**: Maintain compatibility with existing configurations

### **Areas for Contribution**
- 🎨 **UI/UX Improvements**: Better icons, animations, themes
- 🔧 **Hardware Support**: Support for more brightness control methods
- 📱 **Mobile Integration**: Android/iOS companion apps
- 🌐 **Network Features**: Ethernet detection, VPN awareness
- 📊 **Analytics**: Advanced battery life predictions and optimization
- 🔒 **Security**: Configuration encryption and secure storage
- 🌍 **Localization**: Multi-language support

---

## 🙏 Acknowledgments

- **psutil**: Cross-platform system and process utilities
- **pystray**: System tray integration library
- **Pillow**: Python Imaging Library for icon creation
- **plyer**: Platform-native notification support
- **keyboard**: Global hotkey functionality
- **Windows API**: Native system control capabilities

### **Community**
Special thanks to all beta testers, contributors, and users who provided feedback to make PowerWhisper v2 possible!

---

## 📞 Contact & Links

- **📂 GitHub Repository**: [https://github.com/yourusername/powerwhisper](https://github.com/yourusername/powerwhisper)
- **📋 Issue Tracker**: [Report Bugs & Request Features](https://github.com/yourusername/powerwhisper/issues)
- **💬 Discussions**: [Community Support](https://github.com/yourusername/powerwhisper/discussions)
- **📖 Documentation**: [Extended Guides & Tutorials](https://github.com/yourusername/powerwhisper/wiki)
- **🏷️ Releases**: [Download Latest Version](https://github.com/yourusername/powerwhisper/releases)

---

**PowerWhisper v2** - Take control of your laptop's power consumption with intelligence and precision! ⚡