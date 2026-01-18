"""Setup configuration for Connie's Uploader."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="connies-uploader",
    version="2.5.0",
    author="Connie Combs",
    author_email="",
    description="A modern, multi-service image uploader with plugin support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/conniecombs/ConniesUploader-legacy",
    project_urls={
        "Bug Tracker": "https://github.com/conniecombs/ConniesUploader-legacy/issues",
        "Documentation": "https://github.com/conniecombs/ConniesUploader-legacy#readme",
        "Source Code": "https://github.com/conniecombs/ConniesUploader-legacy",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    py_modules=["main"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.9",
    install_requires=[
        "customtkinter>=5.0.0",
        "tkinterdnd2>=0.3.0",
        "Pillow>=9.0.0",
        "httpx[http2]>=0.24.0",
        "requests-toolbelt>=0.10.0",
        "beautifulsoup4>=4.11.0",
        "keyring>=23.0.0",
        "loguru>=0.6.0",
        "pyperclip>=1.8.0",
        "tenacity>=8.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "build": [
            "pyinstaller>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "connies-uploader=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ico", "*.yaml", "*.md"],
    },
    keywords=[
        "image uploader",
        "image hosting",
        "imx.to",
        "pixhost",
        "turboimagehost",
        "vipr.im",
        "file upload",
        "batch upload",
        "image management",
    ],
    license="MIT",
    zip_safe=False,
)
