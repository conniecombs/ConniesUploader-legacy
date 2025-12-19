# modules/config.py
import sys
import re
from loguru import logger
import os

# --- Version ---
APP_VERSION = "2.1.0"
USER_AGENT = f"ConniesUploader/{APP_VERSION}"

# --- Constants ---
IMX_URL = "https://api.imx.to/v1/upload.php"
PIX_URL = "https://api.pixhost.to/images"
PIX_COVERS_URL = "https://api.pixhost.to/covers"
PIX_GALLERIES_URL = "https://api.pixhost.to/galleries"
IMX_LOGIN_URL = "https://imx.to/login.php"
IMX_DASHBOARD_URL = "https://imx.to/user/dashboard"
IMX_GALLERY_ADD_URL = "https://imx.to/user/gallery/add"
IMX_GALLERY_EDIT_URL = "https://imx.to/user/gallery/edit"

# TURBO Constants
TURBO_HOME_URL = "https://www.turboimagehost.com/"
TURBO_LOGIN_URL = "https://www.turboimagehost.com/login.tu"

# VIPR Constants
VIPR_HOME_URL = "https://vipr.im/"
VIPR_LOGIN_URL = "https://vipr.im/"
VIPR_AJAX_URL = "https://vipr.im/"

SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
SETTINGS_FILE = "user_settings.json"
CRASH_LOG_FILE = "crash_log.log"
UI_THUMB_SIZE = (40, 40)

# Keyring Services
KEYRING_SERVICE_API = "ImageUploader:imx_api_key"
KEYRING_SERVICE_USER = "ImageUploader:imx_username"
KEYRING_SERVICE_PASS = "ImageUploader:imx_password"
KEYRING_SERVICE_VIPR_USER = "ImageUploader:vipr_username"
KEYRING_SERVICE_VIPR_PASS = "ImageUploader:vipr_password"

# --- Logging Setup ---
logger.remove()
# Only log to stderr if it exists (fixes EXE crash)
if sys.stderr:
    logger.add(sys.stderr, level="INFO")
logger.add(CRASH_LOG_FILE, rotation="1 MB", retention="10 days", level="DEBUG", backtrace=True, diagnose=True)

def natural_sort_key(s: str):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)