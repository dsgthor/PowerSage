# Contributing to PowerWhisper

Thank you for your interest in contributing to PowerWhisper! This document outlines the guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Check existing issues** to avoid duplicates
2. **Use the search function** to see if your issue has been addressed
3. **Provide detailed information** including:
   - Windows version and architecture
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Relevant log excerpts from `powerwhisper.log`

### Suggesting Features

We welcome feature suggestions! Please:

1. **Check the roadmap** in README.md first
2. **Open a feature request issue** with:
   - Clear description of the feature
   - Use case and benefits
   - Potential implementation approach (if you have ideas)

### Code Contributions

#### Prerequisites

- Python 3.10 or newer
- Git knowledge
- Basic understanding of Windows APIs and system administration

#### Development Setup

1. **Fork the repository**
   ```bash
   git fork https://github.com/yourusername/powerwhisper.git
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/powerwhisper.git
   cd powerwhisper
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install psutil pystray pillow plyer keyboard
   pip install pyinstaller  # For building executables
   ```

5. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Code Guidelines

**Code Style:**
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise

**Testing:**
- Test on both Windows 10 and 11 if possible
- Test with and without administrator privileges
- Verify GUI functionality doesn't break
- Test system tray integration

**Logging:**
- Add appropriate logging for new features
- Use the existing logging setup
- Log both successful operations and errors

#### Pull Request Process

1. **Update documentation** if needed
2. **Test thoroughly** on your local machine
3. **Write clear commit messages**
   ```
   Add feature: Describe what you added
   
   - Detailed explanation of changes
   - Any breaking changes
   - Testing performed
   ```

4. **Submit pull request** with:
   - Clear title and description
   - Reference any related issues
   - Screenshots if UI changes are involved
   - Testing notes

## 🧪 Testing Guidelines

### Manual Testing Checklist

Before submitting, please test:

- [ ] GUI opens without errors
- [ ] System tray icon appears and functions
- [ ] Battery monitoring works correctly
- [ ] Eco mode activation/deactivation
- [ ] Settings persistence (JSON config)
- [ ] Admin privilege handling
- [ ] Notification system
- [ ] Process termination feature
- [ ] Wi-Fi and Bluetooth controls (with admin rights)
- [ ] Brightness adjustment
- [ ] Global hotkey (Ctrl+Alt+P)

### Test Scenarios

1. **Low Battery Scenario**
   - Set eco threshold to current battery % + 5%
   - Verify eco mode triggers automatically
   - Check all enabled features activate

2. **Charging Scenario**
   - Plug in charger during eco mode
   - Verify settings restore automatically

3. **Manual Toggle**
   - Use tray menu to toggle eco mode
   - Use hotkey to toggle eco mode
   - Verify GUI reflects status changes

## 📝 Documentation

When contributing:

- Update README.md for new features
- Add inline code comments for complex logic
- Update this CONTRIBUTING.md if process changes
- Consider adding examples for new features

## 🐛 Bug Report Template

When reporting bugs, please include:

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 11]
- Python Version: [e.g. 3.12]
- PowerWhisper Version: [e.g. commit hash]
- Admin Rights: [Yes/No]

**Logs**
Relevant excerpts from powerwhisper.log
```

## ✨ Feature Request Template

```markdown
**Feature Description**
Clear description of the feature you'd like.

**Use Case**
Why would this feature be useful?

**Proposed Solution**
How do you envision this working?

**Alternatives Considered**
Any alternative solutions you've considered?

**Additional Context**
Any other context or screenshots about the feature.
```

## 🔧 Development Notes

### Architecture Overview

- **Main Thread**: GUI and system tray
- **Background Thread**: Battery monitoring
- **Event System**: Threading-safe communication
- **Configuration**: JSON-based persistence
- **Logging**: Centralized via Python logging module

### Key Files Structure

- `powerwhisper_complete5.py` - Main application
- `powerwhisper_config.json` - User settings (auto-generated)
- `powerwhisper.log` - Runtime logs

### Windows APIs Used

- **WMI**: Brightness control
- **netsh**: Wi-Fi management
- **PowerShell**: Bluetooth control
- **psutil**: System and process information

## 📞 Getting Help

- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: All contributions are reviewed before merging

## 🙏 Recognition

All contributors will be recognized in the project. Thank you for helping make PowerWhisper better!