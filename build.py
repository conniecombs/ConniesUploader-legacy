#!/usr/bin/env python3
"""
Build script for creating standalone executables using PyInstaller.

Usage:
    python build.py              # Build for current platform
    python build.py --clean      # Clean build artifacts first
    python build.py --debug      # Build with debug mode enabled
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_artifacts():
    """Remove existing build artifacts."""
    print("Cleaning build artifacts...")
    artifacts = ["build", "dist", "__pycache__"]
    for artifact in artifacts:
        if os.path.exists(artifact):
            print(f"  Removing {artifact}/")
            shutil.rmtree(artifact)

    # Remove .spec files
    for spec_file in Path(".").glob("*.spec"):
        print(f"  Removing {spec_file}")
        spec_file.unlink()

    print("Clean complete.\n")


def build_executable(debug=False):
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")

    # Determine platform-specific settings
    current_os = platform.system()
    separator = ";" if current_os == "Windows" else ":"

    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=ConniesUploader",
        "--onefile",
        "--windowed",
        f"--icon=logo.ico",
        f"--add-data=logo.ico{separator}.",
        f"--add-data=config.example.yaml{separator}.",
        f"--add-data=plugins{separator}plugins",
    ]

    # Add hidden imports for dependencies
    hidden_imports = [
        "customtkinter",
        "tkinterdnd2",
        "PIL",
        "httpx",
        "keyring",
        "loguru",
        "yaml",
        "tenacity",
        "pyperclip",
    ]

    for module in hidden_imports:
        cmd.append(f"--hidden-import={module}")

    # Debug mode settings
    if debug:
        cmd.extend(["--debug=all", "--console"])
        print("  Debug mode enabled")

    # Add main file
    cmd.append("main.py")

    print(f"  Platform: {current_os}")
    print(f"  Command: {' '.join(cmd)}\n")

    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✓ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error:")
        print(e.stderr)
        return False


def create_release_package():
    """Package the built executable with documentation."""
    print("\nCreating release package...")

    current_os = platform.system()
    release_dir = Path("release")
    dist_dir = Path("dist")

    # Create release directory
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    # Copy executable
    if current_os == "Windows":
        exe_name = "ConniesUploader.exe"
    elif current_os == "Darwin":  # macOS
        exe_name = "ConniesUploader.app"
    else:  # Linux
        exe_name = "ConniesUploader"

    exe_path = dist_dir / exe_name
    if exe_path.exists():
        print(f"  Copying {exe_name}")
        if exe_path.is_dir():
            shutil.copytree(exe_path, release_dir / exe_name)
        else:
            shutil.copy2(exe_path, release_dir)
    else:
        print(f"  Warning: {exe_name} not found in dist/")
        return False

    # Copy documentation
    docs = [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "CONFIG_GUIDE.md",
        "PLUGIN_DEVELOPMENT_GUIDE.md",
        "config.example.yaml",
    ]

    for doc in docs:
        if os.path.exists(doc):
            print(f"  Copying {doc}")
            shutil.copy2(doc, release_dir)

    # Create archive
    archive_name = f"ConniesUploader-{current_os}"
    print(f"\n  Creating archive: {archive_name}")

    if current_os == "Windows":
        # Create ZIP on Windows
        shutil.make_archive(archive_name, "zip", release_dir)
        print(f"✓ Package created: {archive_name}.zip")
    else:
        # Create tar.gz on Unix-like systems
        shutil.make_archive(archive_name, "gztar", release_dir)
        print(f"✓ Package created: {archive_name}.tar.gz")

    return True


def main():
    """Main build script entry point."""
    parser = argparse.ArgumentParser(description="Build ConniesUploader executable")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts first")
    parser.add_argument("--debug", action="store_true", help="Build in debug mode")
    parser.add_argument("--no-package", action="store_true", help="Skip creating release package")

    args = parser.parse_args()

    print("=" * 60)
    print("ConniesUploader Build Script")
    print("=" * 60)
    print()

    # Clean if requested
    if args.clean:
        clean_build_artifacts()

    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Build executable
    if not build_executable(debug=args.debug):
        print("\n✗ Build failed!")
        sys.exit(1)

    # Create release package
    if not args.no_package and not args.debug:
        if not create_release_package():
            print("\n✗ Packaging failed!")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print("\nOutputs:")
    print(f"  Executable: dist/ConniesUploader")
    if not args.no_package and not args.debug:
        print(f"  Package: ConniesUploader-{platform.system()}.{{zip,tar.gz}}")
    print()


if __name__ == "__main__":
    main()
