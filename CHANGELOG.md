# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Professional repository documentation and polish
- LICENSE file (MIT)
- CONTRIBUTING.md guide
- SECURITY.md policy
- CODE_OF_CONDUCT.md
- GitHub issue and PR templates
- Python packaging configuration (setup.py)

## [2.5.0] - 2025-01-17

### Added
- **Plugin System**: Extensible architecture for custom image hosting services
  - Plugin development guide and API documentation
  - Sample plugin template
  - UI integration for plugin management
- **Async Upload Engine**: AsyncIO-based concurrent upload processing
  - 20-40% faster upload speeds
  - Lower memory overhead compared to ThreadPoolExecutor
  - Semaphore-controlled concurrency per service
- **Intelligent Thumbnail Caching**: LRU cache with file modification tracking
  - 50-90% faster re-loading of previously added files
  - Memory-only mode (default) or optional disk persistence
  - Cache hit rates typically 80%+ on re-adds
- **Upload History Tracking**: Automatic session persistence
  - JSON-based storage in `~/.connies_uploader/history/`
  - Track upload statistics, success rates, and errors
  - Access history via Tools menu
- **YAML Configuration System**: User-customizable settings
  - Network, threading, UI, and performance tuning
  - Hot-reload support (no restart required)
  - `config.example.yaml` template included
- **Comprehensive Test Suite**: 76 automated tests
  - 75-92% code coverage across core modules
  - `pytest` integration with coverage reporting
  - See `TESTING_GUIDE.md` for manual testing checklist

### Security
- **Path Validation**: Comprehensive security hardening
  - Prevents path traversal attacks (`../../etc/passwd`)
  - Blocks symlink exploits to system files
  - Validates all file inputs (CLI args, drag-drop, file dialogs)
  - Forbids access to system directories (Windows & Unix)
  - File type and size validation (max 100MB)

### Changed
- **Centralized Error Handling**: Standardized error framework
  - `ErrorHandler` class with severity levels (INFO/WARNING/ERROR/CRITICAL)
  - User notification queue for error display
  - Error statistics and monitoring
- **Configuration Management**: Extracted magic numbers to config
  - 15+ hard-coded values moved to centralized constants
  - Self-documenting code with inline comments
  - Easy tuning without modifying code logic
- **Memory Management**: Fixed memory leaks
  - Garbage collection triggers for large batches (>100 files)
  - Proper PIL image file handle cleanup
  - Cleared results and gallery data after upload completion

### Fixed
- Memory leaks in thumbnail generation and image references
- Silent failures now show user notifications
- Platform-specific imports (winreg) now conditional
- Unbounded memory growth in large file batches

### Performance
- Async/await upload engine (20-40% faster)
- LRU thumbnail caching (50-90% faster re-loads)
- Smart garbage collection for memory efficiency
- Queue-based UI updates to prevent blocking

## [2.0.0] - 2024-12-15

### Added
- **Multi-Service Support**: Upload to imx.to, pixhost.to, TurboImageHost, and vipr.im
- **CustomTkinter UI**: Modern, native-looking interface
  - Dark/Light theme support (follows system settings)
  - Drag-and-drop file support
  - Group management for organizing files
- **Template System**: Save and reuse upload configurations
- **Gallery Management**: Auto-create galleries on supported services
- **Retry Logic**: Exponential backoff for network failures
- **Desktop Notifications**: Error notifications for upload failures
- **Execution Log**: Detailed logging with filtering and export
- **Batch Processing**: Upload hundreds of images simultaneously
- **Live Progress Tracking**: Real-time upload status and progress bars
- **Result Management**: Copy URLs, open in browser, preview thumbnails

### Changed
- Complete UI rewrite using CustomTkinter framework
- Improved credential management using system keyring
- Enhanced HTTP client with HTTP/2 support (httpx)
- Better error handling and user feedback

### Deprecated
- Legacy Tkinter UI (v1.x)

## [1.0.0] - 2024-06-01

### Added
- Initial release
- Basic upload functionality for imx.to and pixhost.to
- Simple Tkinter-based GUI
- File selection and batch upload
- Basic progress tracking

---

## Version History Summary

- **v2.5.0**: Plugin system, async uploads, caching, security hardening, comprehensive testing
- **v2.0.0**: CustomTkinter UI, multi-service support, templates, gallery management
- **v1.0.0**: Initial release with basic functionality

---

## Upgrade Notes

### Upgrading to 2.5.0 from 2.0.x

No breaking changes. All new features are backward compatible.

**New Features to Try:**
1. Create a `config.yaml` from `config.example.yaml` to customize behavior
2. Check out the new upload history feature in Tools menu
3. Try developing a custom plugin (see `PLUGIN_DEVELOPMENT_GUIDE.md`)
4. Run the test suite: `pytest tests/ -v`

**Configuration Migration:**
- Old hard-coded settings are now customizable in `config.yaml`
- Default behavior unchanged if no config file is present

### Upgrading to 2.0.0 from 1.x

**Breaking Changes:**
- New UI framework (CustomTkinter vs Tkinter)
- Different file structure and module organization
- Updated dependencies (see `requirements.txt`)

**Migration Steps:**
1. Install new dependencies: `pip install -r requirements.txt`
2. Re-configure credentials in the new Settings dialog
3. Templates from v1.x are not compatible - recreate them

---

[Unreleased]: https://github.com/conniecombs/ConniesUploader-legacy/compare/v2.5.0...HEAD
[2.5.0]: https://github.com/conniecombs/ConniesUploader-legacy/compare/v2.0.0...v2.5.0
[2.0.0]: https://github.com/conniecombs/ConniesUploader-legacy/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/conniecombs/ConniesUploader-legacy/releases/tag/v1.0.0
