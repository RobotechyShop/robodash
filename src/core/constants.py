"""
Application-wide constants for RoboDash.

Reference: https://github.com/valtsu23/DIY-Emu-Black-Dash
ECU Protocol: https://github.com/designer2k2/EMUcan
"""

# =============================================================================
# Display Configuration
# =============================================================================

# Dashboard display resolution (attached ultrawide)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 720

# Target refresh rate
TARGET_FPS = 30
UPDATE_INTERVAL_MS = 1000 // TARGET_FPS  # ~33ms

# =============================================================================
# CAN Bus Configuration (ECUMaster EMU Black)
# =============================================================================

# Default CAN interface
CAN_CHANNEL = "can0"
CAN_BITRATE = 500000  # 500 kbps

# EMU Black CAN stream base ID (configurable in ECU)
# Messages are sent on IDs: BASE_ID through BASE_ID + 7
EMU_BASE_ID = 0x600

# CAN message timeout before showing connection warning
CAN_TIMEOUT_MS = 1000

# =============================================================================
# Robotechy Brand Colors
# =============================================================================

class Colors:
    """Robotechy dark theme color palette."""

    # Backgrounds
    BACKGROUND = "#0A0A0A"
    SURFACE = "#1A1A1A"
    SURFACE_ELEVATED = "#242424"

    # Borders
    BORDER = "#333333"
    BORDER_LIGHT = "#444444"

    # Text
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#888888"
    TEXT_DISABLED = "#555555"

    # Brand
    ROBOTECHY_GREEN = "#9EFF11"  # Official Robotechy luminous green
    ACCENT = ROBOTECHY_GREEN

    # Status colors
    NORMAL = ROBOTECHY_GREEN
    WARNING = "#FFAA00"
    CRITICAL = "#FF0000"
    INFO = "#00AAFF"

    # Gauge specific
    GAUGE_BACKGROUND = "#1A1A1A"
    GAUGE_ARC = "#333333"
    GAUGE_NEEDLE = "#FFFFFF"

    # RPM zones
    RPM_NORMAL = ROBOTECHY_GREEN
    RPM_WARNING = "#FFAA00"
    RPM_REDLINE = "#FF0000"

# =============================================================================
# Gauge Defaults
# =============================================================================

class GaugeDefaults:
    """Default gauge ranges and thresholds."""

    # RPM
    RPM_MIN = 0
    RPM_MAX = 8000
    RPM_REDLINE = 7200
    RPM_SHIFT_LIGHT = 6800

    # Speed (stored internally as km/h)
    SPEED_MIN = 0
    SPEED_MAX_KMH = 320
    SPEED_MAX_MPH = 200

    # Boost pressure (bar)
    BOOST_MIN = -1.0  # Vacuum
    BOOST_MAX = 2.5
    BOOST_WARNING = 2.0

    # Coolant temperature (Celsius)
    COOLANT_MIN = 0
    COOLANT_MAX = 140
    COOLANT_WARNING = 105
    COOLANT_CRITICAL = 115

    # Oil temperature (Celsius)
    OIL_TEMP_MIN = 0
    OIL_TEMP_MAX = 160
    OIL_TEMP_WARNING = 120
    OIL_TEMP_CRITICAL = 140

    # Oil pressure (bar)
    OIL_PRESSURE_MIN = 0
    OIL_PRESSURE_MAX = 10
    OIL_PRESSURE_WARNING_LOW = 1.0

    # AFR
    AFR_MIN = 10.0
    AFR_MAX = 20.0
    AFR_STOICH = 14.7

    # Battery voltage
    BATTERY_MIN = 10.0
    BATTERY_MAX = 16.0
    BATTERY_WARNING_LOW = 12.0
    BATTERY_WARNING_HIGH = 15.0

# =============================================================================
# Unit Systems
# =============================================================================

class Units:
    """Unit system identifiers."""

    # Speed
    SPEED_MPH = "mph"
    SPEED_KMH = "km/h"

    # Temperature
    TEMP_CELSIUS = "c"
    TEMP_FAHRENHEIT = "f"

    # Pressure
    PRESSURE_BAR = "bar"
    PRESSURE_PSI = "psi"
    PRESSURE_KPA = "kpa"

# =============================================================================
# Layout Identifiers
# =============================================================================

class Layouts:
    """Available dashboard layout identifiers."""

    RACE = "race"
    STREET = "street"
    DIAGNOSTIC = "diagnostic"

# =============================================================================
# Application Paths
# =============================================================================

import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Asset directories
ASSETS_DIR = PROJECT_ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
FONTS_DIR = ASSETS_DIR / "fonts"

# Configuration directory
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default.yaml"

# Logo path
ROBOTECHY_LOGO_PATH = ICONS_DIR / "robotechy_r.png"
