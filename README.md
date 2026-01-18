# Connie's Uploader Ultimate v2.5

[![Tests](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/test.yml/badge.svg)](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/test.yml)
[![Build and Release](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/release.yml/badge.svg)](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/release.yml)
[![CodeQL](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/codeql.yml/badge.svg)](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/codeql.yml)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-2.5.0-brightgreen)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![Tests](https://img.shields.io/badge/tests-102%20passed-success)
![Coverage](https://img.shields.io/badge/coverage-75--92%25-brightgreen)

A powerful, user-friendly desktop application for batch uploading images to multiple hosting services with advanced features like thumbnail caching, async uploads, and session tracking.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Plugin System](#plugin-system)
- [Configuration](#configuration-guide)
- [Testing](#testing)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Features

### Core Functionality
- **Multi-Service Support**: Upload to imx.to, pixhost.to, TurboImageHost, and vipr.im
- **Batch Processing**: Upload hundreds of images simultaneously
- **Drag & Drop**: Intuitive interface with drag-and-drop support
- **Group Management**: Organize files into collapsible groups
- **Template System**: Save and reuse upload configurations

### Performance Optimizations (v2.5)
- **Intelligent Thumbnail Caching**: 50-90% faster re-loading with LRU cache
- **Async Upload Engine**: 20-40% faster uploads with asyncio-based concurrent processing
- **Memory Efficient**: Smart garbage collection for large batches (5000+ files)

### Advanced Features
- **Upload History**: Automatic session tracking with JSON persistence
- **Retry Logic**: Exponential backoff for network failures
- **Security**: Path validation preventing traversal attacks and system directory access
- **YAML Configuration**: User-customizable settings with hot-reload support
- **Gallery Support**: Auto-create galleries on supported services

### User Experience
- **Live Progress Tracking**: Real-time upload status and progress bars
- **Result Management**: Copy URLs, open in browser, preview thumbnails
- **Error Notifications**: Desktop notifications for failures
- **Execution Log**: Detailed logging with filtering and export
- **Dark/Light Theme**: Follows system appearance settings

### Plugin System (v2.5)
- **Extensible Architecture**: Add custom image hosting services without modifying core code
- **Simple API**: Implement just 4 methods to create a plugin
- **UI Integration**: Plugins automatically appear in service dropdown
- **Full Documentation**: See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md)

---

## Installation

### Requirements
- Python 3.9+
- Linux, Windows, or macOS

### Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
- `customtkinter` - Modern GUI framework
- `tkinterdnd2` - Drag-and-drop support
- `Pillow` - Image processing
- `httpx` - Modern HTTP client with HTTP/2 support
- `loguru` - Advanced logging
- `PyYAML` - Configuration management
- `pytest` - Testing framework

## Quick Start

### Basic Usage

```bash
python main.py
```

1. **Add Files**: Click "Add Files" or drag-and-drop images
2. **Select Service**: Choose upload service (imx.to, pixhost, etc.)
3. **Configure**: Set API key/credentials if needed
4. **Upload**: Click "Start Upload" and monitor progress

### Configuration

Create `config.yaml` in the project root to customize behavior:

```yaml
# Network Settings
network:
  timeout_seconds: 60.0
  retry_count: 3
  upload_timeout_seconds: 300.0

# UI Settings
ui:
  thumbnail_size: [40, 40]
  show_previews_default: true

# Threading (Concurrent Uploads)
threading:
  imx_threads: 5
  pixhost_threads: 3
  turbo_threads: 2
  vipr_threads: 1
```

See `config.example.yaml` for all available options.

## Project Structure

```
Version-2.5/
├── main.py                 # Application entry point
├── modules/
│   ├── api.py             # Service-specific upload implementations
│   ├── async_upload_manager.py  # Async concurrent upload engine
│   ├── config_loader.py   # YAML configuration management
│   ├── thumbnail_cache.py # LRU thumbnail caching
│   ├── upload_history.py  # Session tracking & persistence
│   ├── path_validator.py  # Security validation
│   ├── error_handler.py   # Error handling & notifications
│   ├── app_state.py       # Application state management
│   └── ...
├── tests/                 # Pytest unit tests (102 tests, 75-92% coverage)
├── config.yaml            # User configuration (optional)
└── TESTING_GUIDE.md       # Manual testing checklist
```

## Testing

### Run Automated Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_thumbnail_cache.py -v
```

**Test Coverage:**
- `config_loader.py`: 92%
- `upload_history.py`: 87%
- `path_validator.py`: 85%
- `thumbnail_cache.py`: 75%

### Manual Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive manual testing checklist.

## Building from Source

### Build Executable

Use the provided build script to create standalone executables:

```bash
# Install build dependencies
pip install pyinstaller

# Build for current platform
python build.py

# Clean build and rebuild
python build.py --clean

# Build in debug mode
python build.py --debug
```

**Output:**
- Executable in `dist/` directory
- Release package: `ConniesUploader-{Platform}.{zip,tar.gz}`

### Platform-Specific Notes

**Windows:**
- Produces `.exe` in `dist/`
- Release package: `ConniesUploader-Windows.zip`

**Linux:**
- Produces binary in `dist/`
- Release package: `ConniesUploader-Linux.tar.gz`
- May require: `sudo apt install python3-tk`

**macOS:**
- Produces `.app` bundle in `dist/`
- Release package: `ConniesUploader-macOS.tar.gz`

### CI/CD

Automated builds run on every release tag:

```bash
# Create and push a version tag
git tag -a v2.5.0 -m "Release version 2.5.0"
git push origin v2.5.0
```

This triggers:
- ✅ Automated tests on all platforms (Python 3.9-3.12)
- ✅ Build executables for Windows, Linux, macOS
- ✅ Create GitHub release with binaries
- ✅ Publish to PyPI (optional)

See [.github/workflows/](.github/workflows/) for CI/CD configuration.

## Architecture

### Key Components

**Upload Pipeline:**
```
User Input → Path Validation → Group Organization →
Thumbnail Generation (with cache) → Upload Coordinator →
Async Upload Manager → Service API → Result Processing →
Upload History
```

**State Management:**
- `AppState`: Centralized application state
- `UploadCoordinator`: Upload workflow orchestration
- `AsyncUploadManager`: Concurrent upload execution
- `ThumbnailCache`: LRU cache for performance
- `UploadHistory`: Session persistence

### Performance Features

1. **Thumbnail Caching**
   - LRU cache with file modification time tracking
   - Memory-only mode (default) or disk persistence
   - Cache hit rates typically 80%+ on re-adds

2. **Async Uploads**
   - AsyncIO-based concurrent processing
   - Semaphore-controlled concurrency per service
   - Lower memory overhead vs ThreadPoolExecutor
   - Automatic retry with exponential backoff

3. **Memory Management**
   - Garbage collection triggered after 100+ files
   - Queue-based UI updates to prevent blocking
   - Efficient thumbnail handling

## Security

- **Path Validation**: Prevents traversal attacks (`../../etc/passwd`)
- **System Directory Protection**: Blocks access to `/etc`, `/sys`, `/root`, etc.
- **Null Byte Injection Prevention**: Rejects malicious file paths
- **File Type Validation**: Only allows image extensions
- **Size Limits**: Prevents loading files >100MB into memory
- **Credential Storage**: Uses system keyring for sensitive data

## Configuration Guide

### Network Settings

```yaml
network:
  timeout_seconds: 60.0           # Standard request timeout
  retry_count: 3                  # Retries on network failure
  upload_timeout_seconds: 300.0   # Extended timeout for large files
  chunk_size: 8192                # Upload chunk size (bytes)
  http2_enabled: true             # Enable HTTP/2 support
```

### Performance Tuning

```yaml
threading:
  imx_threads: 5        # Concurrent uploads for IMX.to
  pixhost_threads: 3    # Concurrent uploads for Pixhost
  turbo_threads: 2      # TurboImageHost (keep lower)
  vipr_threads: 1       # Vipr.im (keep at 1)

performance:
  ui_queue_batch_size: 20           # UI updates per cycle
  progress_queue_batch_size: 50     # Progress updates per cycle
  gc_threshold_files: 100           # GC trigger threshold
```

### UI Customization

```yaml
ui:
  update_interval_ms: 20            # UI refresh rate
  thumbnail_size: [40, 40]          # Thumbnail dimensions
  show_previews_default: true       # Show previews on load
  recursion_limit: 3000             # Python recursion limit
```

## Upload History

Upload sessions are automatically tracked in `~/.connies_uploader/history/`:

```json
{
  "session_id": "20251230_143022",
  "service": "imx.to",
  "total_files": 50,
  "successful": 48,
  "failed": 2,
  "status": "completed",
  "records": [...]
}
```

Access history via Tools menu or programmatically.

## Troubleshooting

### Common Issues

**Import errors:**
```bash
pip install -r requirements.txt
```

**Upload timeouts:**
- Increase `upload_timeout_seconds` in config.yaml
- Reduce concurrent thread count for the service

**Memory usage high:**
- Lower `gc_threshold_files` to trigger GC more frequently
- Reduce `thumbnail_workers` count
- Disable thumbnail previews for large batches

**Cache not working:**
- Check `~/.connies_uploader/cache/` permissions
- Verify file modification times are stable
- Review cache statistics in Tools menu

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v
```

### Code Style

- Follow PEP 8
- Use type hints where practical
- Document public APIs with docstrings
- Keep functions focused and testable

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

**Quick Start:**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Make changes with tests
4. Run test suite: `pytest tests/ -v`
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

See also:
- [Code of Conduct](CODE_OF_CONDUCT.md) (if you have community guidelines)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ℹ️ License and copyright notice required

## Credits

**Version 2.5 Improvements:**
- Async upload engine
- Thumbnail caching system
- Upload history tracking
- YAML configuration
- Comprehensive test suite
- Security hardening

**Original Author:** Connie Combs

## Support

### Getting Help

For issues, feature requests, or questions:
- **Bug Reports**: [Open an issue](https://github.com/conniecombs/ConniesUploader-legacy/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/conniecombs/ConniesUploader-legacy/issues/new?template=feature_request.md)
- **Security Issues**: See [SECURITY.md](SECURITY.md)
- **General Questions**: [GitHub Discussions](https://github.com/conniecombs/ConniesUploader-legacy/discussions)

### Documentation

- **Configuration**: See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) and [config.example.yaml](config.example.yaml)
- **Testing**: See [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Plugin Development**: See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md)
- **Security**: See [SECURITY.md](SECURITY.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md)

## Changelog

### v2.5 (Current)
- ✨ Added async/await upload engine (20-40% faster)
- ✨ Implemented LRU thumbnail caching (50-90% faster re-loads)
- ✨ Added upload history tracking with JSON persistence
- ✨ Implemented YAML-based configuration system
- 🔒 Enhanced security with path validation
- 🧪 Added comprehensive test suite (102 tests, 75-92% coverage)
- 📊 Improved error handling and notifications
- 🎨 Memory optimization for large batches

### v2.0
- Initial CustomTkinter implementation
- Multi-service upload support
- Template system
- Gallery management
