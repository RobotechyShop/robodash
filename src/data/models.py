"""
Data models for vehicle telemetry.

Reference: https://github.com/designer2k2/EMUcan
ECU: ECUMaster EMU Black
"""

from dataclasses import dataclass, field
from enum import IntFlag
from typing import Optional
import time


class EngineFlags(IntFlag):
    """
    Engine status flags from EMU Black.

    These flags indicate the current operating state of the engine
    and any active control interventions.
    """
    NONE = 0x00
    GEARCUT = 0x01           # Gear cut active (flat shift)
    ALS = 0x02               # Anti-lag system active
    LAUNCH_CONTROL = 0x04    # Launch control active
    IDLE = 0x08              # Engine at idle
    TABLE_SET = 0x10         # Alternative table set active
    TC_INTERVENTION = 0x20   # Traction control intervening
    PIT_LIMITER = 0x40       # Pit lane limiter active
    BRAKE_SWITCH = 0x80      # Brake pedal pressed


class WarningFlags(IntFlag):
    """
    Warning/error flags from EMU Black.

    These flags indicate sensor failures or alarm conditions
    that require driver attention.
    """
    NONE = 0x0000
    CLT_SENSOR = 0x0001      # Coolant temp sensor fault
    IAT_SENSOR = 0x0002      # Intake air temp sensor fault
    MAP_SENSOR = 0x0004      # Manifold pressure sensor fault
    WBO_SENSOR = 0x0008      # Wideband O2 sensor fault
    EGT1_SENSOR = 0x0010     # Exhaust gas temp 1 sensor fault
    EGT2_SENSOR = 0x0020     # Exhaust gas temp 2 sensor fault
    EGT_ALARM = 0x0040       # EGT over threshold
    KNOCKING = 0x0080        # Knock detected
    FUEL_PRESSURE = 0x0100   # Fuel pressure warning
    OIL_PRESSURE = 0x0200    # Oil pressure warning
    BATTERY_LOW = 0x0400     # Low battery voltage


@dataclass
class VehicleState:
    """
    Complete vehicle state snapshot.

    All values are stored in SI/metric units internally:
    - Speed: km/h
    - Temperature: Celsius
    - Pressure: bar (boost) or kPa (manifold)

    Unit conversion happens at the display layer.
    """

    # ==========================================================================
    # Core Engine Data
    # ==========================================================================
    rpm: int = 0
    speed: float = 0.0          # km/h (internal)
    gear: int = 0               # 0 = Neutral, -1 = Reverse, 1-6 = Forward

    # ==========================================================================
    # Pressures
    # ==========================================================================
    boost_pressure: float = 0.0     # bar (relative to atmosphere)
    map_kpa: float = 101.3          # Manifold Absolute Pressure (kPa)
    oil_pressure: float = 0.0       # bar
    fuel_pressure: float = 0.0      # bar

    # ==========================================================================
    # Temperatures
    # ==========================================================================
    coolant_temp: float = 0.0       # Celsius
    oil_temp: float = 0.0           # Celsius
    intake_temp: float = 0.0        # Celsius (IAT)
    egt1: float = 0.0               # Exhaust Gas Temp 1 (Celsius)
    egt2: float = 0.0               # Exhaust Gas Temp 2 (Celsius)

    # ==========================================================================
    # Fueling / Air-Fuel Ratio
    # ==========================================================================
    afr: float = 14.7               # Air-Fuel Ratio
    lambda_value: float = 1.0       # Lambda (AFR / 14.7)
    lambda_target: float = 1.0      # Target lambda
    tps: float = 0.0                # Throttle Position (0-100%)
    injector_duty: float = 0.0      # Injector duty cycle (0-100%)
    ignition_angle: float = 0.0     # Ignition timing (degrees BTDC)

    # ==========================================================================
    # Electrical
    # ==========================================================================
    battery_voltage: float = 12.0   # Volts

    # ==========================================================================
    # Fuel
    # ==========================================================================
    fuel_level: float = 100.0       # Fuel level percentage (0-100%)

    # ==========================================================================
    # Status Flags
    # ==========================================================================
    flags: EngineFlags = field(default_factory=lambda: EngineFlags.NONE)
    warnings: WarningFlags = field(default_factory=lambda: WarningFlags.NONE)

    # ==========================================================================
    # Timing
    # ==========================================================================
    timestamp: float = field(default_factory=time.time)

    # ==========================================================================
    # Computed Properties
    # ==========================================================================

    @property
    def gear_display(self) -> str:
        """Get displayable gear string."""
        if self.gear == 0:
            return "N"
        elif self.gear == -1:
            return "R"
        else:
            return str(self.gear)

    @property
    def is_at_redline(self) -> bool:
        """Check if RPM is at or above redline (7200 default)."""
        return self.rpm >= 7200

    @property
    def is_overheating(self) -> bool:
        """Check if coolant temp is critical (115°C default)."""
        return self.coolant_temp >= 115

    @property
    def has_warnings(self) -> bool:
        """Check if any warning flags are set."""
        return self.warnings != WarningFlags.NONE

    @property
    def has_sensor_faults(self) -> bool:
        """Check if any sensor fault flags are set."""
        sensor_faults = (
            WarningFlags.CLT_SENSOR |
            WarningFlags.IAT_SENSOR |
            WarningFlags.MAP_SENSOR |
            WarningFlags.WBO_SENSOR |
            WarningFlags.EGT1_SENSOR |
            WarningFlags.EGT2_SENSOR
        )
        return bool(self.warnings & sensor_faults)

    def copy(self) -> "VehicleState":
        """Create a shallow copy of this state."""
        return VehicleState(
            rpm=self.rpm,
            speed=self.speed,
            gear=self.gear,
            boost_pressure=self.boost_pressure,
            map_kpa=self.map_kpa,
            oil_pressure=self.oil_pressure,
            fuel_pressure=self.fuel_pressure,
            coolant_temp=self.coolant_temp,
            oil_temp=self.oil_temp,
            intake_temp=self.intake_temp,
            egt1=self.egt1,
            egt2=self.egt2,
            afr=self.afr,
            lambda_value=self.lambda_value,
            lambda_target=self.lambda_target,
            tps=self.tps,
            injector_duty=self.injector_duty,
            ignition_angle=self.ignition_angle,
            battery_voltage=self.battery_voltage,
            fuel_level=self.fuel_level,
            flags=self.flags,
            warnings=self.warnings,
            timestamp=self.timestamp,
        )
