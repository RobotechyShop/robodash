"""
Configuration management for RoboDash.

Handles loading, saving, and runtime access to user preferences
and application settings.
"""

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .constants import (
    CAN_BITRATE,
    CAN_CHANNEL,
    CAN_TIMEOUT_MS,
    DEFAULT_CONFIG_PATH,
    EMU_BASE_ID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TARGET_FPS,
    GaugeDefaults,
    Layouts,
    Units,
)

logger = logging.getLogger(__name__)


@dataclass
class GaugeConfig:
    """Configuration for a single gauge."""

    min: float
    max: float
    warning: Optional[float] = None
    critical: Optional[float] = None
    warning_low: Optional[float] = None
    zones: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DisplayConfig:
    """Display settings."""

    width: int = SCREEN_WIDTH
    height: int = SCREEN_HEIGHT
    fullscreen: bool = True
    frameless: bool = True
    orientation: int = 0


@dataclass
class CANConfig:
    """CAN bus settings."""

    enabled: bool = True
    channel: str = CAN_CHANNEL
    bitrate: int = CAN_BITRATE
    base_id: int = EMU_BASE_ID
    timeout_ms: int = CAN_TIMEOUT_MS


@dataclass
class UnitsConfig:
    """Unit preferences."""

    speed: str = Units.SPEED_MPH  # UK default
    temperature: str = Units.TEMP_CELSIUS
    pressure: str = Units.PRESSURE_BAR


@dataclass
class Config:
    """
    Main application configuration.

    Handles loading from YAML files and provides defaults for all settings.
    """

    # Application
    app_name: str = "RoboDash"
    app_version: str = "1.0.0"
    update_rate_hz: int = TARGET_FPS

    # Display
    display: DisplayConfig = field(default_factory=DisplayConfig)

    # CAN
    can: CANConfig = field(default_factory=CANConfig)

    # Units
    units: UnitsConfig = field(default_factory=UnitsConfig)

    # Layout
    current_layout: str = Layouts.RACE

    # Theme
    theme: str = "robotechy_dark"

    # Gauge configurations
    gauges: Dict[str, GaugeConfig] = field(default_factory=dict)

    # Splash screen
    splash_duration_ms: int = 2500

    def __post_init__(self):
        """Initialize default gauge configurations if not provided."""
        if not self.gauges:
            self.gauges = self._default_gauges()

    @staticmethod
    def _default_gauges() -> Dict[str, GaugeConfig]:
        """Create default gauge configurations."""
        return {
            "rpm": GaugeConfig(
                min=GaugeDefaults.RPM_MIN,
                max=GaugeDefaults.RPM_MAX,
                warning=GaugeDefaults.RPM_SHIFT_LIGHT,
                critical=GaugeDefaults.RPM_REDLINE,
                zones=[
                    {"start": 0, "end": 6000, "color": "#9EFF11"},
                    {"start": 6000, "end": 6800, "color": "#FFAA00"},
                    {"start": 6800, "end": 8000, "color": "#FF0000"},
                ],
            ),
            "speed": GaugeConfig(
                min=GaugeDefaults.SPEED_MIN,
                max=GaugeDefaults.SPEED_MAX_MPH,  # Adjusted per unit selection
            ),
            "boost": GaugeConfig(
                min=GaugeDefaults.BOOST_MIN,
                max=GaugeDefaults.BOOST_MAX,
                warning=GaugeDefaults.BOOST_WARNING,
            ),
            "coolant_temp": GaugeConfig(
                min=GaugeDefaults.COOLANT_MIN,
                max=GaugeDefaults.COOLANT_MAX,
                warning=GaugeDefaults.COOLANT_WARNING,
                critical=GaugeDefaults.COOLANT_CRITICAL,
            ),
            "oil_temp": GaugeConfig(
                min=GaugeDefaults.OIL_TEMP_MIN,
                max=GaugeDefaults.OIL_TEMP_MAX,
                warning=GaugeDefaults.OIL_TEMP_WARNING,
                critical=GaugeDefaults.OIL_TEMP_CRITICAL,
            ),
            "oil_pressure": GaugeConfig(
                min=GaugeDefaults.OIL_PRESSURE_MIN,
                max=GaugeDefaults.OIL_PRESSURE_MAX,
                warning_low=GaugeDefaults.OIL_PRESSURE_WARNING_LOW,
            ),
            "afr": GaugeConfig(
                min=GaugeDefaults.AFR_MIN,
                max=GaugeDefaults.AFR_MAX,
            ),
            "battery": GaugeConfig(
                min=GaugeDefaults.BATTERY_MIN,
                max=GaugeDefaults.BATTERY_MAX,
                warning_low=GaugeDefaults.BATTERY_WARNING_LOW,
                warning=GaugeDefaults.BATTERY_WARNING_HIGH,
            ),
        }

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """
        Load configuration from a YAML file.

        Args:
            path: Path to config file. Uses default if not specified.

        Returns:
            Config instance with loaded settings.
        """
        config_path = path or DEFAULT_CONFIG_PATH

        if not config_path.exists():
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return cls()

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            return cls._from_dict(data)

        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return cls()

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary (parsed YAML)."""
        config = cls()

        # Application settings
        if "app" in data:
            app = data["app"]
            config.app_name = app.get("name", config.app_name)
            config.app_version = app.get("version", config.app_version)
            config.update_rate_hz = app.get("update_rate_hz", config.update_rate_hz)

        # Display settings
        if "display" in data:
            d = data["display"]
            config.display = DisplayConfig(
                width=d.get("width", SCREEN_WIDTH),
                height=d.get("height", SCREEN_HEIGHT),
                fullscreen=d.get("fullscreen", True),
                frameless=d.get("frameless", True),
                orientation=d.get("orientation", 0),
            )

        # CAN settings
        if "can" in data:
            c = data["can"]
            config.can = CANConfig(
                enabled=c.get("enabled", True),
                channel=c.get("channel", CAN_CHANNEL),
                bitrate=c.get("bitrate", CAN_BITRATE),
                base_id=c.get("base_id", EMU_BASE_ID),
                timeout_ms=c.get("timeout_ms", CAN_TIMEOUT_MS),
            )

        # Unit preferences
        if "units" in data:
            u = data["units"]
            config.units = UnitsConfig(
                speed=u.get("speed", Units.SPEED_MPH),
                temperature=u.get("temperature", Units.TEMP_CELSIUS),
                pressure=u.get("pressure", Units.PRESSURE_BAR),
            )

        # Layout
        if "layout" in data:
            config.current_layout = data["layout"].get("current", Layouts.RACE)

        # Theme
        if "theme" in data:
            config.theme = data["theme"].get("current", "robotechy_dark")

        # Splash
        if "splash" in data:
            config.splash_duration_ms = data["splash"].get("duration_ms", 2500)

        # Gauge configurations
        if "gauges" in data:
            for name, gauge_data in data["gauges"].items():
                if name in config.gauges:
                    config.gauges[name] = GaugeConfig(
                        min=gauge_data.get("min", config.gauges[name].min),
                        max=gauge_data.get("max", config.gauges[name].max),
                        warning=gauge_data.get("warning"),
                        critical=gauge_data.get("critical"),
                        warning_low=gauge_data.get("warning_low"),
                        zones=gauge_data.get("zones", []),
                    )

        return config

    def save(self, path: Optional[Path] = None) -> None:
        """
        Save configuration to a YAML file.

        Args:
            path: Path to save config. Uses default if not specified.
        """
        config_path = path or DEFAULT_CONFIG_PATH

        data = {
            "app": {
                "name": self.app_name,
                "version": self.app_version,
                "update_rate_hz": self.update_rate_hz,
            },
            "display": asdict(self.display),
            "can": asdict(self.can),
            "units": asdict(self.units),
            "layout": {"current": self.current_layout},
            "theme": {"current": self.theme},
            "splash": {"duration_ms": self.splash_duration_ms},
            "gauges": {name: asdict(gauge) for name, gauge in self.gauges.items()},
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration saved to {config_path}")
