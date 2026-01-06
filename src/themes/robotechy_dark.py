"""
Robotechy Dark Theme for RoboDash.

Official Robotechy branding with luminous green (#9EFF11) accents
on a dark background optimized for visibility in racing conditions.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class RobotechyDarkTheme:
    """
    Robotechy Dark racing theme.

    Color palette designed for high visibility and readability
    in bright daylight and low-light racing conditions.
    """

    # =========================================================================
    # Brand Colors
    # =========================================================================

    # Official Robotechy luminous green
    ROBOTECHY_GREEN: str = "#9EFF11"

    # =========================================================================
    # Backgrounds
    # =========================================================================

    BACKGROUND: str = "#0A0A0A"  # Main background
    SURFACE: str = "#1A1A1A"  # Card/widget background
    SURFACE_ELEVATED: str = "#242424"  # Elevated surfaces
    SURFACE_HOVER: str = "#2A2A2A"  # Hover state

    # =========================================================================
    # Borders
    # =========================================================================

    BORDER: str = "#333333"  # Standard borders
    BORDER_LIGHT: str = "#444444"  # Light borders
    BORDER_ACCENT: str = "#9EFF11"  # Accent borders

    # =========================================================================
    # Text Colors
    # =========================================================================

    TEXT_PRIMARY: str = "#FFFFFF"  # Primary text
    TEXT_SECONDARY: str = "#888888"  # Secondary/label text
    TEXT_DISABLED: str = "#555555"  # Disabled text
    TEXT_ACCENT: str = "#9EFF11"  # Accent text

    # =========================================================================
    # Status Colors
    # =========================================================================

    NORMAL: str = "#9EFF11"  # Normal/good values
    WARNING: str = "#FFAA00"  # Warning values
    CRITICAL: str = "#FF0000"  # Critical/danger values
    INFO: str = "#00AAFF"  # Informational

    # =========================================================================
    # Gauge Colors
    # =========================================================================

    GAUGE_BACKGROUND: str = "#1A1A1A"  # Gauge face background
    GAUGE_ARC: str = "#333333"  # Unlit gauge arc
    GAUGE_NEEDLE: str = "#FFFFFF"  # Needle color
    GAUGE_NEEDLE_SHADOW: str = "#000000"  # Needle shadow

    # RPM Zone colors
    RPM_ZONE_NORMAL: str = "#9EFF11"  # Normal RPM range
    RPM_ZONE_WARNING: str = "#FFAA00"  # Near shift point
    RPM_ZONE_REDLINE: str = "#FF0000"  # Redline zone

    # Boost gauge colors
    BOOST_VACUUM: str = "#00AAFF"  # Vacuum (negative boost)
    BOOST_ATMOSPHERE: str = "#888888"  # Atmospheric
    BOOST_POSITIVE: str = "#9EFF11"  # Positive boost

    # =========================================================================
    # Widget Colors
    # =========================================================================

    BOX_BACKGROUND: str = "#1A1A1A"  # Metric box background
    BOX_BORDER: str = "#333333"  # Metric box border
    BOX_LABEL: str = "#888888"  # Metric box label
    BOX_VALUE: str = "#FFFFFF"  # Metric box value

    # =========================================================================
    # Shift Light Colors
    # =========================================================================

    SHIFT_LIGHT_OFF: str = "#333333"  # LED off
    SHIFT_LIGHT_GREEN: str = "#9EFF11"  # Green segment
    SHIFT_LIGHT_YELLOW: str = "#FFAA00"  # Yellow segment
    SHIFT_LIGHT_RED: str = "#FF0000"  # Red segment
    SHIFT_LIGHT_FLASH: str = "#FFFFFF"  # Flash color at redline

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def get_rpm_zone_colors(self) -> List[Tuple[float, float, str]]:
        """
        Get RPM zone color definitions.

        Returns:
            List of (start_pct, end_pct, color) tuples.
        """
        return [
            (0.0, 0.75, self.RPM_ZONE_NORMAL),  # 0-75%: Green
            (0.75, 0.85, self.RPM_ZONE_WARNING),  # 75-85%: Yellow
            (0.85, 1.0, self.RPM_ZONE_REDLINE),  # 85-100%: Red
        ]

    def get_boost_colors(self) -> Dict[str, str]:
        """Get boost pressure color mapping."""
        return {
            "vacuum": self.BOOST_VACUUM,
            "atmosphere": self.BOOST_ATMOSPHERE,
            "boost": self.BOOST_POSITIVE,
        }

    def get_temperature_color(
        self, value: float, warning: float, critical: float
    ) -> str:
        """
        Get color for temperature value.

        Args:
            value: Current temperature.
            warning: Warning threshold.
            critical: Critical threshold.

        Returns:
            Hex color string.
        """
        if value >= critical:
            return self.CRITICAL
        elif value >= warning:
            return self.WARNING
        return self.NORMAL

    def get_pressure_color(
        self, value: float, warning_low: float = None, warning_high: float = None
    ) -> str:
        """
        Get color for pressure value.

        Args:
            value: Current pressure.
            warning_low: Low threshold (critical if below).
            warning_high: High threshold (warning if above).

        Returns:
            Hex color string.
        """
        if warning_low is not None and value < warning_low:
            return self.CRITICAL
        if warning_high is not None and value > warning_high:
            return self.WARNING
        return self.NORMAL

    def to_stylesheet(self) -> str:
        """
        Generate Qt stylesheet for this theme.

        Returns:
            Qt stylesheet string.
        """
        return f"""
            /* Main Window */
            QMainWindow {{
                background-color: {self.BACKGROUND};
            }}

            QWidget {{
                background-color: transparent;
                color: {self.TEXT_PRIMARY};
                font-family: "Roboto", "Arial", sans-serif;
            }}

            /* Labels */
            QLabel {{
                color: {self.TEXT_PRIMARY};
            }}

            QLabel[class="secondary"] {{
                color: {self.TEXT_SECONDARY};
            }}

            QLabel[class="accent"] {{
                color: {self.TEXT_ACCENT};
            }}

            /* Frames */
            QFrame {{
                background-color: {self.SURFACE};
                border: 1px solid {self.BORDER};
                border-radius: 4px;
            }}

            QFrame[class="metric-box"] {{
                background-color: {self.BOX_BACKGROUND};
                border: 1px solid {self.BOX_BORDER};
            }}

            /* Buttons (for menu/settings if needed) */
            QPushButton {{
                background-color: {self.SURFACE};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}

            QPushButton:hover {{
                background-color: {self.SURFACE_HOVER};
                border-color: {self.BORDER_ACCENT};
            }}

            QPushButton:pressed {{
                background-color: {self.SURFACE_ELEVATED};
            }}
        """


# Create a default instance
DEFAULT_THEME = RobotechyDarkTheme()
