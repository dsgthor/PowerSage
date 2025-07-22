# Security Policy

## 🔒 Reporting Security Vulnerabilities

We take the security of PowerWhisper seriously. If you discover a security vulnerability, please help us address it responsibly.

### ⚠️ Please DO NOT:
- Report security vulnerabilities through public GitHub issues
- Share vulnerability details publicly before we've had a chance to address them

### ✅ Please DO:
1. **Email us privately** at [your-security-email@domain.com] with:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes (if you have them)

2. **Allow reasonable time** for us to investigate and address the issue

3. **Work with us** to verify the fix before public disclosure

## 🛡️ Security Considerations

### Administrator Privileges
PowerWhisper requests administrator privileges for certain features:
- **Wi-Fi control** (via `netsh` commands)
- **Bluetooth control** (via PowerShell)
- **Process termination** (for processes not owned by current user)

**Important**: Only run PowerWhisper from trusted sources. Administrator access allows system-level modifications.

### Data Handling
- **Configuration data**: Stored locally in `powerwhisper_config.json`
- **Logs**: Stored locally in `powerwhisper.log`
- **No data transmission**: PowerWhisper does not send data to external servers
- **No personal data collection**: Only system metrics (battery, processes) are accessed

### Code Security
- **Open source**: All code is visible and auditable
- **No external dependencies**: Minimal third-party library usage
- **Windows API usage**: Direct Windows API calls for system control

### System Modifications
PowerWhisper can modify these system settings:
- Display brightness (via WMI)
- Wi-Fi adapter state (via netsh)
- Bluetooth adapter state (via PowerShell)
- Running processes (termination)
- Windows power plan settings

## 🔍 Security Best Practices

### For Users:
1. **Download from official sources** only
2. **Review code** before building from source
3. **Run with minimum necessary privileges** when possible
4. **Monitor logs** for unexpected behavior
5. **Keep Python and dependencies updated**

### For Developers:
1. **Validate all user inputs** in GUI and configuration
2. **Handle privilege escalation gracefully**
3. **Log security-relevant events**
4. **Use secure coding practices** for system API calls
5. **Test with different privilege levels**

## 🔧 Secure Configuration

### Recommended Settings:
- **Limit app killer list** to only necessary processes
- **Use specific process names** rather than wildcards
- **Review configuration file** periodically
- **Enable notifications** to stay informed of eco mode changes

### File Permissions:
- Ensure `powerwhisper_config.json` is not world-writable
- Protect `powerwhisper.log` from unauthorized access
- Store executable in protected directory

## 📋 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | ✅ Yes             |
| < Latest| ❌ No              |

We only provide security updates for the latest version. Please keep PowerWhisper updated.

## 🚨 Known Security Limitations

1. **Process Termination**: May forcefully close applications without saving data
2. **Wi-Fi/Bluetooth Control**: Requires elevated privileges
3. **System Resource Access**: Has access to system power and process information
4. **Global Hotkeys**: May conflict with other applications

## 🔄 Security Update Process

1. **Assessment**: We assess reported vulnerabilities within 48 hours
2. **Development**: Security fixes are prioritized over feature development
3. **Testing**: Thorough testing on multiple Windows versions
4. **Release**: Security updates are released as soon as possible
5. **Notification**: Users are notified through GitHub releases

## 📞 Contact

For security-related inquiries:
- **Security issues**: [your-security-email@domain.com]
- **General questions**: GitHub Issues (for non-security topics only)

## 🙏 Responsible Disclosure

We appreciate security researchers who:
- Report vulnerabilities privately first
- Allow reasonable time for fixes
- Provide clear reproduction steps
- Work with us to verify solutions

Contributors who responsibly disclose security issues will be acknowledged in our security advisories (unless they prefer to remain anonymous).

---

**Last updated**: [Date]
**Next review**: [Date + 6 months]