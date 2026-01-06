"""
Pytest configuration and shared fixtures for RoboDash tests.

Provides:
- QApplication fixture for Qt widget testing
- Mock data fixtures
- Screenshot helpers
"""

import os
import sys
from pathlib import Path

import pytest

# Set Qt to offscreen mode for headless testing
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# pytest-qt provides qapp and qtbot fixtures automatically
# We just need to ensure QT_QPA_PLATFORM is set (done above)


@pytest.fixture
def sample_vehicle_state():
    """Create a sample VehicleState for testing."""
    from src.data.models import EngineFlags, VehicleState

    return VehicleState(
        rpm=5500,
        speed=120.0,  # km/h
        gear=4,
        boost_pressure=1.2,
        map_kpa=220.0,
        oil_pressure=4.5,
        fuel_pressure=3.0,
        coolant_temp=88.0,
        oil_temp=95.0,
        intake_temp=35.0,
        afr=14.2,
        lambda_value=0.97,
        lambda_target=1.0,
        tps=75.0,
        injector_duty=55.0,
        ignition_angle=28.0,
        battery_voltage=13.8,
        flags=EngineFlags.NONE,
    )


@pytest.fixture
def warning_vehicle_state():
    """Create a VehicleState with warning conditions."""
    from src.data.models import VehicleState, WarningFlags

    return VehicleState(
        rpm=6900,
        speed=180.0,
        gear=5,
        boost_pressure=1.9,
        oil_pressure=0.8,  # Low!
        coolant_temp=112.0,  # High!
        oil_temp=135.0,  # High!
        afr=11.5,
        battery_voltage=13.5,
        warnings=WarningFlags.OIL_PRESSURE | WarningFlags.EGT_ALARM,
    )


@pytest.fixture
def mock_data_source():
    """Create a mock data source for testing."""
    from src.data.mock_source import MockDataSource

    source = MockDataSource(update_rate_hz=30)
    yield source
    source.stop()


@pytest.fixture
def default_config():
    """Create a default configuration for testing."""
    from src.core.config import Config

    return Config()


@pytest.fixture
def screenshot_dir(tmp_path):
    """Get/create directory for test screenshots."""
    screenshots = Path(__file__).parent / "screenshots"
    screenshots.mkdir(exist_ok=True)
    return screenshots


def save_widget_screenshot(widget, path: Path, name: str) -> Path:
    """
    Save a screenshot of a widget.

    Args:
        widget: Qt widget to capture.
        path: Directory to save to.
        name: Base filename (without extension).

    Returns:
        Path to saved screenshot.
    """
    # Ensure widget is shown and painted
    widget.show()
    widget.repaint()

    # Capture
    pixmap = widget.grab()

    # Save
    filepath = path / f"{name}.png"
    pixmap.save(str(filepath))

    return filepath


@pytest.fixture
def capture_screenshot(screenshot_dir):
    """Fixture that provides screenshot capture function."""

    def _capture(widget, name: str) -> Path:
        return save_widget_screenshot(widget, screenshot_dir, name)

    return _capture
