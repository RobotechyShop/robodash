"""
Unit conversion utilities for RoboDash.

Handles conversion between metric and imperial units for:
- Speed: km/h <-> mph
- Temperature: Celsius <-> Fahrenheit
- Pressure: bar <-> psi <-> kPa

All internal values are stored in SI/metric units. Conversion
happens at the display layer based on user preferences.
"""

from dataclasses import dataclass
from typing import Union

from ..core.constants import Units


@dataclass
class ConvertedValues:
    """Container for converted display values."""

    speed: float
    speed_unit: str
    coolant_temp: float
    oil_temp: float
    intake_temp: float
    temp_unit: str
    boost_pressure: float
    oil_pressure: float
    fuel_pressure: float
    pressure_unit: str


class UnitConverter:
    """
    Converts values between unit systems.

    Usage:
        converter = UnitConverter(speed="mph", temperature="c", pressure="bar")
        display_speed = converter.convert_speed(100.0)  # 100 km/h -> 62.14 mph
    """

    # Conversion factors
    KMH_TO_MPH = 0.621371
    MPH_TO_KMH = 1.60934

    BAR_TO_PSI = 14.5038
    PSI_TO_BAR = 0.0689476
    BAR_TO_KPA = 100.0
    KPA_TO_BAR = 0.01

    def __init__(
        self,
        speed: str = Units.SPEED_MPH,
        temperature: str = Units.TEMP_CELSIUS,
        pressure: str = Units.PRESSURE_BAR,
    ):
        """
        Initialize converter with unit preferences.

        Args:
            speed: Speed unit ("mph" or "km/h").
            temperature: Temperature unit ("c" or "f").
            pressure: Pressure unit ("bar", "psi", or "kpa").
        """
        self.speed_unit = speed
        self.temp_unit = temperature
        self.pressure_unit = pressure

    # =========================================================================
    # Speed Conversion
    # =========================================================================

    def convert_speed(self, kmh: float) -> float:
        """
        Convert speed from km/h to display unit.

        Args:
            kmh: Speed in kilometers per hour.

        Returns:
            Speed in configured display unit.
        """
        if self.speed_unit == Units.SPEED_MPH:
            return kmh * self.KMH_TO_MPH
        return kmh  # km/h

    def speed_to_internal(self, value: float) -> float:
        """
        Convert speed from display unit to internal km/h.

        Args:
            value: Speed in display unit.

        Returns:
            Speed in km/h.
        """
        if self.speed_unit == Units.SPEED_MPH:
            return value * self.MPH_TO_KMH
        return value

    def get_speed_unit_label(self) -> str:
        """Get display label for speed unit."""
        return "mph" if self.speed_unit == Units.SPEED_MPH else "km/h"

    def get_speed_max(self) -> float:
        """Get appropriate max speed for current unit."""
        return 200.0 if self.speed_unit == Units.SPEED_MPH else 320.0

    # =========================================================================
    # Temperature Conversion
    # =========================================================================

    def convert_temperature(self, celsius: float) -> float:
        """
        Convert temperature from Celsius to display unit.

        Args:
            celsius: Temperature in Celsius.

        Returns:
            Temperature in configured display unit.
        """
        if self.temp_unit == Units.TEMP_FAHRENHEIT:
            return (celsius * 9 / 5) + 32
        return celsius

    def temperature_to_internal(self, value: float) -> float:
        """
        Convert temperature from display unit to internal Celsius.

        Args:
            value: Temperature in display unit.

        Returns:
            Temperature in Celsius.
        """
        if self.temp_unit == Units.TEMP_FAHRENHEIT:
            return (value - 32) * 5 / 9
        return value

    def get_temp_unit_label(self) -> str:
        """Get display label for temperature unit."""
        return "°F" if self.temp_unit == Units.TEMP_FAHRENHEIT else "°C"

    # =========================================================================
    # Pressure Conversion
    # =========================================================================

    def convert_pressure(self, bar: float) -> float:
        """
        Convert pressure from bar to display unit.

        Args:
            bar: Pressure in bar.

        Returns:
            Pressure in configured display unit.
        """
        if self.pressure_unit == Units.PRESSURE_PSI:
            return bar * self.BAR_TO_PSI
        elif self.pressure_unit == Units.PRESSURE_KPA:
            return bar * self.BAR_TO_KPA
        return bar

    def pressure_to_internal(self, value: float) -> float:
        """
        Convert pressure from display unit to internal bar.

        Args:
            value: Pressure in display unit.

        Returns:
            Pressure in bar.
        """
        if self.pressure_unit == Units.PRESSURE_PSI:
            return value * self.PSI_TO_BAR
        elif self.pressure_unit == Units.PRESSURE_KPA:
            return value * self.KPA_TO_BAR
        return value

    def get_pressure_unit_label(self) -> str:
        """Get display label for pressure unit."""
        if self.pressure_unit == Units.PRESSURE_PSI:
            return "psi"
        elif self.pressure_unit == Units.PRESSURE_KPA:
            return "kPa"
        return "bar"

    # =========================================================================
    # Batch Conversion
    # =========================================================================

    def convert_vehicle_state(self, state: "VehicleState") -> ConvertedValues:
        """
        Convert all relevant values from a VehicleState.

        Args:
            state: Vehicle state with internal units.

        Returns:
            ConvertedValues with all values in display units.
        """
        return ConvertedValues(
            speed=self.convert_speed(state.speed),
            speed_unit=self.get_speed_unit_label(),
            coolant_temp=self.convert_temperature(state.coolant_temp),
            oil_temp=self.convert_temperature(state.oil_temp),
            intake_temp=self.convert_temperature(state.intake_temp),
            temp_unit=self.get_temp_unit_label(),
            boost_pressure=self.convert_pressure(state.boost_pressure),
            oil_pressure=self.convert_pressure(state.oil_pressure),
            fuel_pressure=self.convert_pressure(state.fuel_pressure),
            pressure_unit=self.get_pressure_unit_label(),
        )

    # =========================================================================
    # Threshold Conversion
    # =========================================================================

    def convert_speed_threshold(self, kmh: float) -> float:
        """Convert speed threshold for gauge configuration."""
        return self.convert_speed(kmh)

    def convert_temp_threshold(self, celsius: float) -> float:
        """Convert temperature threshold for gauge configuration."""
        return self.convert_temperature(celsius)

    def convert_pressure_threshold(self, bar: float) -> float:
        """Convert pressure threshold for gauge configuration."""
        return self.convert_pressure(bar)


# Type alias for VehicleState import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data.models import VehicleState
