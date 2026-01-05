"""
Mock data source for development and testing.

Generates realistic simulated vehicle data without requiring
actual CAN bus hardware. Useful for:
- UI development on desktop
- Automated testing
- Demonstrations

The simulation models a realistic driving experience with
acceleration, gear changes, and fluctuating temperatures.

Optional: Includes synthesized engine sound that varies with RPM.
"""

import math
import random
import logging
from typing import Optional

from PyQt5.QtCore import QTimer, QObject

from .base import DataSource
from .models import VehicleState, EngineFlags, WarningFlags
from ..utils.engine_sound import create_engine_sound, EngineSoundSynthesizer

logger = logging.getLogger(__name__)


class MockDataSource(DataSource):
    """
    Simulated vehicle data source for development.

    Generates realistic driving data including:
    - RPM cycling with gear changes
    - Speed based on gear and RPM
    - Fluctuating temperatures
    - Boost pressure simulation
    - Occasional warning conditions (configurable)
    """

    # Gear ratios (approximate for 2JZ-GTE)
    GEAR_RATIOS = {
        1: 3.827,
        2: 2.360,
        3: 1.685,
        4: 1.312,
        5: 1.000,
        6: 0.793,
    }
    FINAL_DRIVE = 3.538
    TIRE_CIRCUMFERENCE = 2.0  # meters (approximate for 275/35R18)

    # RPM limits
    IDLE_RPM = 850
    REDLINE_RPM = 7200
    REV_LIMIT_RPM = 7500

    # Shift points
    UPSHIFT_RPM = 6800
    DOWNSHIFT_RPM = 2500

    def __init__(
        self,
        parent: Optional[QObject] = None,
        update_rate_hz: int = 30,
        enable_warnings: bool = False,
        enable_sound: bool = False,
        sound_volume: float = 0.5
    ):
        """
        Initialize mock data source.

        Args:
            parent: Optional parent QObject.
            update_rate_hz: Data update frequency (default 30 Hz).
            enable_warnings: If True, randomly trigger warning conditions.
            enable_sound: If True, play synthesized engine sounds.
            sound_volume: Volume for engine sound (0.0 to 1.0).
        """
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._generate_data)
        self._update_interval = 1000 // update_rate_hz
        self._enable_warnings = enable_warnings

        # Engine sound synthesis
        self._engine_sound: Optional[EngineSoundSynthesizer] = None
        if enable_sound:
            self._engine_sound = create_engine_sound(sound_volume)
            if self._engine_sound:
                logger.info("Engine sound enabled")
            else:
                logger.warning("Engine sound requested but audio not available")

        # Simulation state
        self._time = 0.0
        self._gear = 1
        self._rpm = self.IDLE_RPM
        self._throttle = 0.0
        self._accelerating = True
        self._cruise_mode = False
        self._cruise_speed = 0.0

        # Temperature simulation (start cold)
        self._coolant_temp = 20.0
        self._oil_temp = 20.0
        self._engine_running_time = 0.0

        # Fuel simulation (start with random amount)
        self._fuel_level = 75.0 + random.uniform(-20, 20)  # 55-95%

        logger.info("MockDataSource initialized")

    def start(self) -> None:
        """Begin generating simulated data."""
        logger.info("MockDataSource starting")
        self._timer.start(self._update_interval)
        self._set_connected(True)

        # Start engine sound if enabled
        if self._engine_sound:
            self._engine_sound.start()

    def stop(self) -> None:
        """Stop generating data."""
        logger.info("MockDataSource stopping")
        self._timer.stop()
        self._set_connected(False)

        # Stop engine sound
        if self._engine_sound:
            self._engine_sound.stop()

    def is_connected(self) -> bool:
        """Check if simulation is running."""
        return self._timer.isActive()

    def _generate_data(self) -> None:
        """Generate a frame of simulated data."""
        dt = self._update_interval / 1000.0
        self._time += dt
        self._engine_running_time += dt

        # Update throttle and RPM
        self._update_throttle(dt)
        self._update_rpm(dt)

        # Update engine sound with current RPM
        if self._engine_sound:
            self._engine_sound.set_rpm(self._rpm)

        # Auto gear changes
        self._check_gear_change()

        # Calculate dependent values
        speed = self._calculate_speed()
        boost = self._calculate_boost()

        # Update temperatures (slow warm-up)
        self._update_temperatures(dt)

        # Update fuel level (slow consumption)
        self._update_fuel(dt)

        # Build state
        state = VehicleState(
            rpm=int(self._rpm),
            speed=speed,
            gear=self._gear,
            boost_pressure=boost,
            map_kpa=101.3 + (boost * 100),
            coolant_temp=self._coolant_temp,
            oil_temp=self._oil_temp,
            intake_temp=25 + random.uniform(-2, 2),
            oil_pressure=self._calculate_oil_pressure(),
            fuel_pressure=3.0 + random.uniform(-0.1, 0.1),
            afr=self._calculate_afr(),
            lambda_value=self._calculate_afr() / 14.7,
            lambda_target=0.85 if self._throttle > 80 else 1.0,
            tps=self._throttle,
            injector_duty=self._calculate_injector_duty(),
            ignition_angle=self._calculate_ignition(),
            battery_voltage=13.8 + random.uniform(-0.3, 0.3),
            fuel_level=self._fuel_level,
            flags=self._get_engine_flags(),
            warnings=self._get_warnings(),
        )

        self._emit_state(state)

    def _update_throttle(self, dt: float) -> None:
        """Simulate throttle input patterns with more variation."""
        # Vary throttle to create realistic driving
        cycle = math.sin(self._time * 0.3) * 0.5 + 0.5  # 0-1 cycle

        # Occasionally trigger heavy braking/slowdown
        if random.random() < 0.002:  # ~0.2% chance per frame
            self._accelerating = False
            self._throttle = 0  # Full lift

        if self._accelerating:
            # Gradual throttle increase
            target = 70 + cycle * 30  # 70-100%
            self._throttle = min(100, self._throttle + 150 * dt)
            if self._throttle >= target and random.random() < 0.015:
                self._accelerating = False
        else:
            # Lift off - sometimes more aggressive
            if self._throttle > 50:
                # Quick lift
                self._throttle = max(0, self._throttle - 300 * dt)
            else:
                # Gradual coast
                target = 10 + cycle * 20  # 10-30%
                self._throttle = max(0, self._throttle - 150 * dt)

            # More likely to accelerate again if speed/rpm is low
            resume_chance = 0.03 if self._rpm < 3000 else 0.02
            if self._throttle <= 15 and random.random() < resume_chance:
                self._accelerating = True

    def _update_rpm(self, dt: float) -> None:
        """Update RPM based on throttle."""
        if self._throttle > 50:
            # Accelerating
            rpm_change = (self._throttle - 30) * 15 * dt
            self._rpm = min(self.REV_LIMIT_RPM, self._rpm + rpm_change)
        elif self._throttle > 10:
            # Light throttle - maintain with some variation
            target = self.IDLE_RPM + (self._throttle / 10) * 2000
            self._rpm += (target - self._rpm) * dt * 2
        else:
            # Decel / engine braking
            rpm_change = 800 * dt
            self._rpm = max(self.IDLE_RPM, self._rpm - rpm_change)

        # Add some noise
        self._rpm += random.uniform(-20, 20)

    def _check_gear_change(self) -> None:
        """Check if gear change is needed and execute."""
        if self._rpm >= self.UPSHIFT_RPM and self._gear < 6:
            self._shift_up()
        elif self._rpm <= self.DOWNSHIFT_RPM and self._gear > 1 and self._throttle < 30:
            self._shift_down()

    def _shift_up(self) -> None:
        """Upshift gear."""
        if self._gear < 6:
            old_gear = self._gear
            self._gear += 1
            # RPM drop on upshift
            ratio_change = (
                self.GEAR_RATIOS[old_gear] / self.GEAR_RATIOS[self._gear]
            )
            self._rpm *= (1 / ratio_change)

            # Play gear change sound
            if self._engine_sound:
                self._engine_sound.play_gear_change(upshift=True)

            logger.debug(f"Upshift {old_gear} -> {self._gear}, RPM: {self._rpm:.0f}")

    def _shift_down(self) -> None:
        """Downshift gear."""
        if self._gear > 1:
            old_gear = self._gear
            self._gear -= 1
            # RPM rise on downshift
            ratio_change = (
                self.GEAR_RATIOS[old_gear] / self.GEAR_RATIOS[self._gear]
            )
            self._rpm *= (1 / ratio_change)
            self._rpm = min(self._rpm, self.REDLINE_RPM)

            # Play gear change sound
            if self._engine_sound:
                self._engine_sound.play_gear_change(upshift=False)

            logger.debug(f"Downshift {old_gear} -> {self._gear}, RPM: {self._rpm:.0f}")

    def _calculate_speed(self) -> float:
        """Calculate vehicle speed from RPM and gear (km/h)."""
        if self._gear <= 0:
            return 0.0

        ratio = self.GEAR_RATIOS.get(self._gear, 1.0)
        # Speed = (RPM * tire_circumference * 60) / (gear_ratio * final_drive * 1000)
        speed_mps = (
            self._rpm * self.TIRE_CIRCUMFERENCE
        ) / (ratio * self.FINAL_DRIVE * 60)
        speed_kph = speed_mps * 3.6

        return max(0, speed_kph)

    def _calculate_boost(self) -> float:
        """Calculate boost pressure based on RPM and throttle."""
        if self._rpm < 2500 or self._throttle < 50:
            # Vacuum at low RPM/throttle
            return -0.5 + random.uniform(-0.1, 0.1)

        # Boost builds with RPM and throttle
        rpm_factor = min(1.0, (self._rpm - 2500) / 4000)
        throttle_factor = (self._throttle - 50) / 50

        boost = 1.8 * rpm_factor * throttle_factor
        boost += random.uniform(-0.05, 0.05)

        return round(boost, 2)

    def _update_temperatures(self, dt: float) -> None:
        """Update coolant and oil temperatures with warning capability."""
        # Base target temps after warm-up
        base_coolant = 88
        base_oil = 95

        # Add heat based on throttle and RPM
        load_factor = (self._throttle / 100) * (self._rpm / self.REDLINE_RPM)

        # At sustained high load, temps can reach warning levels
        if self._gear >= 5 and self._rpm > 6000 and self._throttle > 80:
            # High load in top gears - temps rise more
            coolant_target = base_coolant + 25 + load_factor * 15  # Can reach 115+
            oil_target = base_oil + 35 + load_factor * 20  # Can reach 130+
        else:
            coolant_target = base_coolant + load_factor * 15
            oil_target = base_oil + load_factor * 20

        # Warm-up rate (slower when cold, faster when hot and cooling)
        if self._engine_running_time < 60:
            rate = 0.5
        elif self._coolant_temp > coolant_target:
            rate = 0.15  # Cooling rate
        else:
            rate = 0.2  # Heating rate

        # Move toward target
        self._coolant_temp += (coolant_target - self._coolant_temp) * rate * dt
        self._oil_temp += (oil_target - self._oil_temp) * rate * dt

        # Add noise
        self._coolant_temp += random.uniform(-0.3, 0.3)
        self._oil_temp += random.uniform(-0.3, 0.3)

        # Clamp to reasonable values
        self._coolant_temp = max(20, min(130, self._coolant_temp))
        self._oil_temp = max(20, min(150, self._oil_temp))

    def _update_fuel(self, dt: float) -> None:
        """Simulate fuel consumption."""
        # Fuel consumption based on RPM and throttle
        load_factor = (self._throttle / 100) * (self._rpm / self.REDLINE_RPM)
        # Base consumption + load-based consumption (per minute, scaled to dt)
        consumption = (0.1 + load_factor * 0.5) * dt / 60.0
        self._fuel_level = max(5, self._fuel_level - consumption)

    def _calculate_oil_pressure(self) -> float:
        """Calculate oil pressure based on RPM."""
        # Oil pressure increases with RPM
        base = 1.0 + (self._rpm / 1000) * 0.8
        return base + random.uniform(-0.2, 0.2)

    def _calculate_afr(self) -> float:
        """Calculate air-fuel ratio based on load."""
        if self._throttle > 80:
            # Rich under boost
            return 11.5 + random.uniform(-0.3, 0.3)
        elif self._throttle > 30:
            # Slightly rich at part throttle
            return 13.5 + random.uniform(-0.3, 0.3)
        else:
            # Stoich at cruise/idle
            return 14.7 + random.uniform(-0.2, 0.2)

    def _calculate_injector_duty(self) -> float:
        """Calculate injector duty cycle."""
        base = (self._rpm / self.REDLINE_RPM) * 50
        load_factor = self._throttle / 100
        duty = base + (load_factor * 40)
        return min(95, duty + random.uniform(-2, 2))

    def _calculate_ignition(self) -> float:
        """Calculate ignition timing."""
        # Base timing varies with RPM and load
        base = 35 - (self._throttle / 100) * 20
        rpm_advance = min(10, (self._rpm - self.IDLE_RPM) / 500)
        return base + rpm_advance + random.uniform(-1, 1)

    def _get_engine_flags(self) -> EngineFlags:
        """Get current engine status flags."""
        flags = EngineFlags.NONE

        if self._rpm < 1000:
            flags |= EngineFlags.IDLE
        if self._rpm >= self.UPSHIFT_RPM and self._throttle > 90:
            # Simulate shift light / gear cut
            flags |= EngineFlags.GEARCUT

        return flags

    def _get_warnings(self) -> WarningFlags:
        """Get warning flags (occasional if enabled)."""
        if not self._enable_warnings:
            return WarningFlags.NONE

        warnings = WarningFlags.NONE

        # Randomly trigger warnings (rare)
        if random.random() < 0.001:
            warnings |= WarningFlags.KNOCKING

        return warnings

    def set_gear(self, gear: int) -> None:
        """Manually set gear (for testing)."""
        self._gear = max(0, min(6, gear))

    def set_rpm(self, rpm: int) -> None:
        """Manually set RPM (for testing)."""
        self._rpm = max(0, min(self.REV_LIMIT_RPM, rpm))
