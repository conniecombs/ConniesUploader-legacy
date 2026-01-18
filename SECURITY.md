# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.5.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Security Features

### Current Security Implementations (v2.5.0)

#### Path Validation
- **Path Traversal Prevention**: Blocks attempts to access files outside allowed directories
- **Symlink Protection**: Validates symlink targets to prevent exploitation
- **System Directory Protection**: Forbids access to sensitive system directories
  - Unix: `/etc`, `/sys`, `/proc`, `/root`, `/boot`
  - Windows: `C:\Windows`, `C:\System32`, system root
- **Null Byte Injection Prevention**: Rejects malicious file paths
- **File Type Validation**: Restricts to image file extensions only
- **Size Limits**: Prevents loading files >100MB into memory

#### Credential Management
- **System Keyring**: Credentials stored using OS keyring (Keychain/Credential Manager)
- **No Plain Text Storage**: API keys and passwords never stored in plain text
- **Memory Protection**: Credentials cleared from memory when no longer needed

#### Network Security
- **HTTP/2 Support**: Modern, secure protocol support via httpx
- **TLS/SSL Verification**: Certificate validation for all HTTPS connections
- **Timeout Protection**: Prevents resource exhaustion from hanging connections
- **Retry Limits**: Bounded retry attempts to prevent infinite loops

#### Input Validation
- **User Input Sanitization**: All user inputs validated and sanitized
- **HTML Escaping**: Gallery names and user text properly escaped
- **URL Validation**: Upload service URLs validated before use
- **Configuration Validation**: YAML config files validated on load

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

### 1. Do NOT Open a Public Issue

Please do not report security vulnerabilities through public GitHub issues.

### 2. Report Privately

Send a detailed report to the project maintainers privately:

- **Preferred**: Use GitHub Security Advisories (see "Security" tab)
- **Alternative**: Email the maintainer directly (check profile for contact info)

### 3. Include in Your Report

Please include as much of the following information as possible:

- **Type of vulnerability** (e.g., XSS, SQL injection, path traversal)
- **Affected versions** (specify exact version numbers)
- **Steps to reproduce** (detailed, step-by-step instructions)
- **Proof of concept** (code, screenshots, or video if applicable)
- **Impact assessment** (what an attacker could achieve)
- **Suggested fix** (if you have one)
- **Your name/handle** (for credit in security advisory)

### 4. What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Status Updates**: Regular updates on fix progress
- **Disclosure Timeline**: Coordinated disclosure after fix is released

### 5. Coordinated Disclosure

We follow a coordinated disclosure process:

1. Vulnerability is reported privately
2. We confirm and investigate the issue
3. We develop and test a fix
4. We release a security patch
5. Public disclosure (with credit to reporter) after users have time to update

**Typical Timeline**: 30-90 days from report to public disclosure

## Security Best Practices for Users

### Installation

```bash
# Always install from official sources
pip install -r requirements.txt

# Verify integrity of downloaded files
sha256sum main.py
```

### Configuration

```yaml
# In config.yaml - Use secure defaults

network:
  timeout_seconds: 60.0      # Prevent infinite hangs
  retry_count: 3             # Limit retry attempts
  upload_timeout_seconds: 300.0

# Never commit config.yaml with credentials
```

### Credential Storage

```python
# DO: Use system keyring (automatic in v2.5)
# Application stores credentials securely

# DON'T: Store API keys in code or config files
# DON'T: Share config files containing credentials
# DON'T: Commit credentials to version control
```

### File Handling

```python
# The application validates all file paths, but you should:
# - Only add files from trusted sources
# - Avoid uploading sensitive/private images
# - Review file lists before uploading
# - Use the clear list feature to remove unwanted files
```

### Plugin Security

If using the plugin system:

```python
# Only install plugins from trusted sources
# Review plugin code before installation
# Plugins have full access to upload functionality
# Report malicious plugins immediately
```

### Network Security

```bash
# Application uses HTTPS for all uploads
# Verify certificate warnings - NEVER ignore them
# Use trusted networks for uploading sensitive content
# Consider using a VPN for additional privacy
```

## Known Security Considerations

### API Key Exposure

**Risk**: API keys grant access to your image hosting accounts

**Mitigation**:
- Keys stored in system keyring, not in plain text
- Never log or display full API keys
- Keys cleared from memory after use

**User Action**:
- Rotate API keys regularly
- Use account-specific keys with minimal permissions
- Don't share configuration files

### Upload Content Privacy

**Risk**: Uploaded images are publicly accessible on hosting services

**Mitigation**:
- Application warns about public uploads
- No automatic sharing of upload links
- Upload history stored locally only

**User Action**:
- Review images before uploading
- Understand hosting service privacy policies
- Delete uploads from services when no longer needed

### Path Traversal (FIXED in v2.5.0)

**Risk**: Malicious file paths could access system files

**Status**: ✅ **FIXED** - Comprehensive path validation implemented

**Protection**:
- All file paths validated before access
- Symlinks checked and validated
- System directories blocked
- See `modules/path_validator.py`

### Dependency Vulnerabilities

**Risk**: Third-party packages may have security issues

**Mitigation**:
- Regular dependency updates
- Security audit of dependencies
- Minimal dependency footprint

**User Action**:
```bash
# Keep dependencies updated
pip install --upgrade -r requirements.txt

# Check for known vulnerabilities
pip-audit
```

## Security Checklist for Contributors

Before submitting code that handles:

- [ ] **User Input**: Validate and sanitize all inputs
- [ ] **File Paths**: Use PathValidator for all file operations
- [ ] **Network Requests**: Use https, validate certificates, set timeouts
- [ ] **Credentials**: Never log, display, or store in plain text
- [ ] **Error Messages**: Don't leak sensitive information in errors
- [ ] **Dependencies**: Only add well-maintained, security-audited packages
- [ ] **Tests**: Include security test cases
- [ ] **Documentation**: Document security implications

## Security Update Process

### For Maintainers

1. Vulnerability reported via GitHub Security Advisory
2. Create private fork to develop fix
3. Write tests to prevent regression
4. Prepare security advisory draft
5. Release patch version (e.g., 2.5.1)
6. Publish security advisory
7. Notify users via GitHub Releases

### For Users

When a security update is released:

1. **Update Immediately**: `git pull && pip install -r requirements.txt`
2. **Review CHANGELOG**: Read security advisory details
3. **Check Your Usage**: Verify if you were affected
4. **Update API Keys**: If credential-related issue, rotate keys
5. **Scan for Compromise**: Review upload history for suspicious activity

## Responsible Disclosure Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

*No reports yet - be the first!*

## Contact

- **Security Email**: [Use GitHub Security Advisory]
- **General Issues**: GitHub Issues (for non-security bugs)
- **Project Maintainer**: See GitHub profile

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Last Updated**: 2025-01-17
**Policy Version**: 1.0
