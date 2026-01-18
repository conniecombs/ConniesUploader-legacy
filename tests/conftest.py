"""
Pytest configuration and fixtures for test suite.
Configures environment for headless testing of GUI application.
"""
import os
import sys
import pytest

# Set environment variables before any GUI imports
os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':99')
os.environ['MPLBACKEND'] = 'Agg'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Prevent GUI initialization during imports
os.environ['CONNIES_UPLOADER_TESTING'] = '1'


@pytest.fixture(scope='session', autouse=True)
def configure_test_environment():
    """Configure environment for headless testing."""
    # Set testing mode
    os.environ['CONNIES_UPLOADER_TESTING'] = '1'

    # Ensure modules directory is in path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    yield

    # Cleanup after all tests
    os.environ.pop('CONNIES_UPLOADER_TESTING', None)


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset state between tests."""
    yield
    # Add any cleanup needed between tests


def pytest_configure(config):
    """Pytest configuration hook."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI (may skip in headless environments)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle GUI tests appropriately."""
    # Check if running in headless environment
    is_headless = os.environ.get('CI') or not os.environ.get('DISPLAY')

    if is_headless:
        skip_gui = pytest.mark.skip(reason="GUI test - skipped in headless environment")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)
