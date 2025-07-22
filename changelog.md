# Changelog

All notable changes to PowerWhisper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Scheduler-based profile switching
- Cloud sync of configurations
- Auto-detection of heavy apps by CPU/RAM usage
- GUI theming and animations
- Native Windows toast notifications
- Multiple power profiles

## [1.0.0] - 2025-01-XX

### Added
- 🔋 **Core Features**
  - Automatic eco mode activation based on battery threshold
  - Manual eco mode toggle via system tray and global hotkey (Ctrl+Alt+P)
  - Battery level monitoring with 30-second polling intervals
  - Persistent JSON-based configuration system

- 🖥️ **System Control**
  - Display brightness reduction via WMI
  - Wi-Fi adapter control using Windows netsh commands
  - Bluetooth adapter control via PowerShell
  - Selective process termination for power saving

- 🎯 **User Interface**
  - Complete Tkinter-based GUI with settings panel
  - System tray integration using pystray
  - Real-time battery information display
  - Interactive configuration management

- 🔔 **Notifications & Logging**
  - Cross-platform notifications using plyer
  - Comprehensive logging to powerwhisper.log
  - Error handling and admin privilege awareness
  - Detailed operation tracking

- ⚙️ **Configuration Options**
  - Customizable battery thresholds (eco and restore)
  - Toggleable feature controls (Wi-Fi, Bluetooth, brightness)
  - User-defined application kill list
  - Auto eco mode and notification settings

- 🔧 **Technical Features**
  - Global hotkey support via keyboard library
  - Thread-safe battery monitoring
  - Administrator privilege detection
  - PyInstaller compatibility for standalone executable

### Technical Details
- **Dependencies**: psutil, pystray, Pillow, plyer, keyboard, tkinter
- **Platform**: Windows 10/11, Python 3.10+
- **Architecture**: x64 support
- **Installation**: Python script or standalone executable

### Documentation
- Complete README.md with installation and usage instructions
- Comprehensive troubleshooting guide
- Feature overview table
- System requirements documentation

---

## Version History Notes

### Semantic Versioning
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in backward-compatible manner  
- **PATCH**: Backward-compatible bug fixes

### Release Types
- 🎉 **Major Release**: Significant new features, possible breaking changes
- ✨ **Minor Release**: New features, enhancements, backward-compatible
- 🐛 **Patch Release**: Bug fixes, small improvements
- 🔒 **Security Release**: Security fixes and improvements

### Change Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Any bug fixes
- **Security**: Vulnerability fixes

---

## Future Roadmap

### v1.1.0 (Planned)
- **Enhanced UI**: Dark mode theme support
- **Improved Performance**: Optimized battery polling
- **New Features**: Custom notification sounds
- **Bug Fixes**: GUI stability improvements

### v1.2.0 (Planned)
- **Power Profiles**: Multiple preset configurations
- **Advanced Scheduling**: Time-based power management
- **Statistics**: Power usage tracking and reporting

### v2.0.0 (Future)
- **Complete Rewrite**: Modern UI framework
- **Cloud Integration**: Configuration synchronization
- **Plugin System**: Extensible architecture
- **Mobile Companion**: Android/iOS monitoring app

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- How to report bugs
- How to suggest features  
- Development setup
- Pull request process

## Acknowledgments

Thanks to all contributors who help make PowerWhisper better:
- Bug reporters and testers
- Feature contributors
- Documentation improvements
- Community feedback