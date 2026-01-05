"""
Race layout for primary dashboard display.

Optimized for 1920x720 ultrawide display with key racing metrics
prominently displayed. Inspired by the clean, minimalist design
with large central speed display and organized metric boxes.

Layout (1920x720):
┌─────────────────────────────────────────────────────────────────────────────┐
│  [GEAR]  │                    [SPEED]                    │    [Metrics]    │
│    3     │                     142                       │   Oil Pres      │
│          │                     mph                       │   Oil Temp      │
│  [Boost] │                                               │   Coolant       │
│  1.2 bar │    [RPM: 5432]                               │   AFR           │
│          │ ═══════════════════════════════════════════  │   Battery       │
│ Connected│ [            RPM Bar                       ] │   Fuel          │
└─────────────────────────────────────────────────────────────────────────────┘
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QFrame, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt

from .base_layout import BaseLayout
from ..data.models import VehicleState
from ..widgets import (
    DigitalDisplay, GearIndicator, SpeedDisplay,
    RPMBar, MetricBox, FuelBar
)
from ..core.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class RaceLayout(BaseLayout):
    """
    Primary race dashboard layout.

    Optimized for quick glance readability at speed with:
    - Large gear indicator (left)
    - Central speed display (prominent)
    - RPM display near bar
    - Secondary metrics panel (right)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize race layout."""
        super().__init__(parent)
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)

    def _setup_ui(self) -> None:
        """Set up the race layout UI."""
        # Ensure solid background
        self.setStyleSheet("background-color: #0A0A0A;")

        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # -- Left Panel: Gear + Boost + Status --
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)

        # -- Center Panel: Speed + RPM bar --
        center_panel = self._create_center_panel()
        main_layout.addWidget(center_panel, stretch=2)

        # -- Right Panel: Metrics (wider) --
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)

    def _create_left_panel(self) -> QWidget:
        """Create left panel with gear and status."""
        panel = QFrame()
        panel.setFixedWidth(280)  # Wider left panel
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Gear indicator - takes most of the space
        self._gear_indicator = GearIndicator()
        self._gear_indicator.setMinimumHeight(450)
        layout.addWidget(self._gear_indicator, stretch=4)
        self.register_widget("gear", self._gear_indicator)

        # Connection status at bottom of left panel
        self._status_label = QLabel("Connected")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(
            f"color: {self.theme.ROBOTECHY_GREEN}; font-size: 14px; padding: 10px;"
        )
        layout.addWidget(self._status_label)
        self.register_widget("status", self._status_label)

        return panel

    def _create_center_panel(self) -> QWidget:
        """Create center panel with speed prominently displayed and RPM bar."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Speed display - very large and centered
        self._speed_display = SpeedDisplay()
        self._speed_display.setMinimumHeight(350)
        self._speed_display._font_size_ratio = 0.8  # Make speed much bigger
        layout.addWidget(self._speed_display, stretch=2)
        self.register_widget("speed", self._speed_display)

        # RPM value - smaller, above the bar
        rpm_row = QHBoxLayout()
        rpm_row.addStretch()

        self._rpm_display = DigitalDisplay()
        self._rpm_display.set_label("RPM")
        self._rpm_display.set_range(0, 8000)
        self._rpm_display.set_format("{:.0f}")
        self._rpm_display.set_font_size_ratio(0.8)  # Bigger font
        self._rpm_display.set_show_unit(False)
        self._rpm_display.setFixedWidth(280)  # Wider for bigger digits
        self._rpm_display.setFixedHeight(90)  # Taller for bigger digits
        rpm_row.addWidget(self._rpm_display)
        self.register_widget("rpm_display", self._rpm_display)

        rpm_row.addStretch()
        layout.addLayout(rpm_row)

        # RPM bar - 50% taller
        self._rpm_bar = RPMBar()
        self._rpm_bar.setMinimumHeight(375)  # 50% taller
        layout.addWidget(self._rpm_bar, stretch=1)
        self.register_widget("rpm_bar", self._rpm_bar)

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create right panel with secondary metrics (wider)."""
        panel = QFrame()
        panel.setFixedWidth(600)  # 50% wider panel
        layout = QGridLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # Oil Pressure
        self._oil_pressure = MetricBox("Oil Pressure")
        self._oil_pressure.set_range(0, 10)
        self._oil_pressure.set_decimals(1)
        self._oil_pressure.set_unit("bar")
        self._oil_pressure.set_thresholds(warning_low=1.0)
        layout.addWidget(self._oil_pressure, 0, 0)
        self.register_widget("oil_pressure", self._oil_pressure)

        # Oil Temp
        self._oil_temp = MetricBox("Oil Temp")
        self._oil_temp.set_range(0, 160)
        self._oil_temp.set_decimals(0)
        self._oil_temp.set_unit("°C")
        self._oil_temp.set_thresholds(warning=120, critical=140)
        layout.addWidget(self._oil_temp, 0, 1)
        self.register_widget("oil_temp", self._oil_temp)

        # Coolant Temp
        self._coolant_temp = MetricBox("Coolant Temp")
        self._coolant_temp.set_range(0, 140)
        self._coolant_temp.set_decimals(0)
        self._coolant_temp.set_unit("°C")
        self._coolant_temp.set_thresholds(warning=105, critical=115)
        layout.addWidget(self._coolant_temp, 1, 0)
        self.register_widget("coolant_temp", self._coolant_temp)

        # AFR
        self._afr = MetricBox("AFR")
        self._afr.set_range(10, 20)
        self._afr.set_decimals(1)
        self._afr.set_unit("")
        layout.addWidget(self._afr, 1, 1)
        self.register_widget("afr", self._afr)

        # Battery
        self._battery = MetricBox("Battery")
        self._battery.set_range(10, 16)
        self._battery.set_decimals(1)
        self._battery.set_unit("V")
        self._battery.set_thresholds(warning=15.0, warning_low=12.0)
        layout.addWidget(self._battery, 2, 0)
        self.register_widget("battery", self._battery)

        # Boost gauge (moved from left panel)
        self._boost_box = MetricBox("Boost")
        self._boost_box.set_range(-1.0, 2.5)
        self._boost_box.set_decimals(2)
        self._boost_box.set_unit("bar")
        self._boost_box.set_thresholds(warning=2.0)
        layout.addWidget(self._boost_box, 2, 1)
        self.register_widget("boost", self._boost_box)

        # Fuel Level - with visual bar (at bottom, spans both columns)
        self._fuel_level = FuelBar()
        self._fuel_level.setMinimumHeight(80)
        layout.addWidget(self._fuel_level, 3, 0, 1, 2)  # Row 3, span both columns
        self.register_widget("fuel_level", self._fuel_level)

        return panel

    def update_from_state(self, state: VehicleState) -> None:
        """
        Update all widgets from vehicle state.

        Args:
            state: Current vehicle telemetry.
        """
        self._last_state = state

        # Core displays
        self._gear_indicator.gear = state.gear
        self._rpm_display.value = state.rpm
        self._rpm_bar.value = state.rpm
        self._speed_display.value = state.speed * 0.621371  # km/h to mph

        # Pressures
        self._boost_box.value = state.boost_pressure
        self._oil_pressure.value = state.oil_pressure

        # Temperatures
        self._oil_temp.value = state.oil_temp
        self._coolant_temp.value = state.coolant_temp

        # Fueling
        self._afr.value = state.afr
        self._fuel_level.value = state.fuel_level

        # Electrical
        self._battery.value = state.battery_voltage

    def show_connection_warning(self) -> None:
        """Show disconnection warning."""
        self._status_label.setText("Disconnected")
        self._status_label.setStyleSheet(
            f"color: {self.theme.CRITICAL}; font-size: 14px; padding: 10px;"
        )

    def hide_connection_warning(self) -> None:
        """Hide disconnection warning."""
        self._status_label.setText("Connected")
        self._status_label.setStyleSheet(
            f"color: {self.theme.ROBOTECHY_GREEN}; font-size: 14px; padding: 10px;"
        )

    def cleanup(self) -> None:
        """Clean up resources."""
        pass  # No warning indicators to stop anymore
