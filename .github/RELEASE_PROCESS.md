# Release Process

This document describes the automated release process for Connie's Uploader.

## Overview

The project uses GitHub Actions for continuous integration and deployment:

- **Tests**: Run automatically on all PRs and pushes to main/develop
- **Builds**: Created automatically when version tags are pushed
- **Releases**: Published to GitHub Releases and optionally PyPI

## Automated Workflows

### 1. Test Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Actions:**
- Runs tests on Python 3.8-3.12
- Tests on Windows, Linux, and macOS
- Generates code coverage reports
- Runs linting (flake8, black, mypy)
- Uploads coverage to Codecov

**Badge:** ![Tests](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/test.yml/badge.svg)

### 2. Release Workflow (`release.yml`)

**Triggers:**
- Push of version tags (`v*.*.*`)
- Manual workflow dispatch

**Actions:**
1. Run full test suite
2. Build executables for:
   - Windows (`.exe`)
   - Linux (binary)
   - macOS (`.app`)
3. Create release packages (`.zip` / `.tar.gz`)
4. Create GitHub Release with binaries
5. Publish to PyPI (if configured)

**Badge:** ![Build and Release](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/release.yml/badge.svg)

### 3. CodeQL Workflow (`codeql.yml`)

**Triggers:**
- Push to `main`
- Pull requests to `main`
- Weekly on Mondays

**Actions:**
- Security analysis with CodeQL
- Identifies security vulnerabilities
- Checks code quality issues

**Badge:** ![CodeQL](https://github.com/conniecombs/ConniesUploader-legacy/actions/workflows/codeql.yml/badge.svg)

## Creating a Release

### Prerequisites

1. All tests passing on main branch
2. CHANGELOG.md updated with new version
3. Version number updated in:
   - `setup.py` (line 12)
   - `README.md` (title and badges)
   - Any other version references

### Release Steps

#### 1. Update Version Numbers

```bash
# Edit these files to update version to X.Y.Z:
# - setup.py (version="X.Y.Z")
# - README.md (title and version badge)

git add setup.py README.md
git commit -m "chore: Bump version to vX.Y.Z"
```

#### 2. Update CHANGELOG.md

```bash
# Add release notes for vX.Y.Z to CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: Update CHANGELOG for vX.Y.Z"
```

#### 3. Push Changes

```bash
git push origin main
```

#### 4. Create and Push Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push tag to trigger release workflow
git push origin vX.Y.Z
```

#### 5. Monitor Build

1. Go to **Actions** tab on GitHub
2. Watch the "Build and Release" workflow
3. Verify all builds complete successfully

#### 6. Verify Release

1. Check **Releases** page
2. Verify all platform binaries are attached
3. Test download and run on each platform (if possible)

### Post-Release

1. Announce release in Discussions/social media
2. Update documentation links if needed
3. Start work on next version

## Manual Release Build

If you need to build locally without triggering CI:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build executable
python build.py

# Test executable
./dist/ConniesUploader  # Linux/macOS
dist\ConniesUploader.exe  # Windows
```

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (x.Y.0): New features, backward compatible
- **PATCH** (x.y.Z): Bug fixes, backward compatible

Examples:
- `v2.5.0` → `v2.5.1`: Bug fix release
- `v2.5.0` → `v2.6.0`: New feature release
- `v2.5.0` → `v3.0.0`: Breaking changes

## PyPI Publishing

### First Time Setup

1. Create PyPI account: https://pypi.org/account/register/
2. Generate API token: https://pypi.org/manage/account/token/
3. Add token as GitHub secret: `PYPI_API_TOKEN`

### Automated Publishing

When a release tag is pushed, the workflow will:
1. Build Python package (`sdist` and `wheel`)
2. Validate package with `twine`
3. Upload to PyPI

Users can then install via:
```bash
pip install connies-uploader
```

### Manual Publishing

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Troubleshooting

### Build Fails on Specific Platform

- Check platform-specific dependencies in `requirements.txt`
- Review PyInstaller hidden imports in `build.py`
- Test locally on that platform if possible

### Tests Fail in CI but Pass Locally

- Ensure all test dependencies in `requirements.txt`
- Check for platform-specific test assumptions
- Review test isolation (avoid global state)

### Release Not Created

- Verify tag format matches `v*.*.*`
- Check workflow permissions in repository settings
- Review workflow logs in Actions tab

### PyPI Upload Fails

- Verify `PYPI_API_TOKEN` secret is set
- Check version number not already published
- Ensure package metadata is valid

## Rollback Procedure

If a release needs to be rolled back:

1. **Delete GitHub Release**
   - Go to Releases page
   - Delete the problematic release

2. **Delete Git Tag**
   ```bash
   git tag -d vX.Y.Z
   git push --delete origin vX.Y.Z
   ```

3. **Revert Changes** (if needed)
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

4. **Notify Users**
   - Create issue explaining the rollback
   - Update any external announcements

## Best Practices

1. **Test Before Release**
   - Run full test suite locally
   - Test on multiple platforms if possible
   - Review all changes since last release

2. **Clear Release Notes**
   - Highlight breaking changes
   - List new features prominently
   - Include migration instructions if needed

3. **Version Consistency**
   - Update all version references
   - Keep CHANGELOG.md current
   - Tag commits properly

4. **Communication**
   - Announce releases in Discussions
   - Update README if features changed
   - Respond to release-related issues quickly

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/)
