"""
Value smoothing utilities for RoboDash.

Provides algorithms to smooth noisy sensor data for more stable
gauge displays without introducing noticeable lag.

Available smoothers:
- ExponentialMovingAverage: Simple EMA with configurable alpha
- ValueSmoother: Multi-channel smoother for VehicleState
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from ..data.models import VehicleState


class ExponentialMovingAverage:
    """
    Exponential Moving Average filter.

    EMA provides smooth output while responding quickly to changes.
    Lower alpha = more smoothing (slower response).
    Higher alpha = less smoothing (faster response).

    Formula: output = alpha * input + (1 - alpha) * previous_output

    Usage:
        ema = ExponentialMovingAverage(alpha=0.3)
        smoothed = ema.update(noisy_value)
    """

    def __init__(self, alpha: float = 0.3, initial_value: Optional[float] = None):
        """
        Initialize EMA filter.

        Args:
            alpha: Smoothing factor (0.0 to 1.0). Default 0.3.
                   - 0.1: Heavy smoothing, slow response
                   - 0.3: Moderate smoothing (recommended)
                   - 0.5: Light smoothing, fast response
                   - 1.0: No smoothing
            initial_value: Starting value. If None, uses first input.
        """
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be between 0 (exclusive) and 1 (inclusive)")

        self._alpha = alpha
        self._value = initial_value
        self._initialized = initial_value is not None

    @property
    def value(self) -> Optional[float]:
        """Get current smoothed value."""
        return self._value

    @property
    def alpha(self) -> float:
        """Get smoothing factor."""
        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Set smoothing factor."""
        if not 0.0 < value <= 1.0:
            raise ValueError("alpha must be between 0 (exclusive) and 1 (inclusive)")
        self._alpha = value

    def update(self, value: float) -> float:
        """
        Update filter with new input value.

        Args:
            value: New input value.

        Returns:
            Smoothed output value.
        """
        if not self._initialized:
            self._value = value
            self._initialized = True
        else:
            assert self._value is not None  # Guaranteed since _initialized is True
            self._value = self._alpha * value + (1 - self._alpha) * self._value

        assert self._value is not None  # Type narrowing for return
        return self._value

    def reset(self, value: Optional[float] = None) -> None:
        """
        Reset filter state.

        Args:
            value: Optional new initial value.
        """
        self._value = value
        self._initialized = value is not None


@dataclass
class SmootherConfig:
    """Configuration for a single value smoother."""

    alpha: float = 0.3
    enabled: bool = True


@dataclass
class ValueSmoother:
    """
    Multi-channel value smoother for vehicle telemetry.

    Maintains separate EMA filters for each telemetry channel,
    allowing different smoothing levels per value type.

    Usage:
        smoother = ValueSmoother()
        smoother.configure("rpm", alpha=0.5)  # Fast response for RPM
        smoother.configure("oil_temp", alpha=0.1)  # Heavy smoothing for temp

        smoothed_rpm = smoother.update("rpm", raw_rpm)
    """

    # Default alpha values per channel type
    # Lower alpha = more smoothing (slower response, easier to read)
    DEFAULT_ALPHAS: Dict[str, float] = field(
        default_factory=lambda: {
            # Readable response (heavily smoothed for easy reading)
            "rpm": 0.08,
            "speed": 0.05,  # Very smooth for readability
            "tps": 0.3,
            "boost_pressure": 0.2,
            # Medium response
            "afr": 0.15,
            "oil_pressure": 0.15,
            "battery_voltage": 0.15,
            "fuel_level": 0.1,
            # Slow response (temperatures change slowly anyway)
            "coolant_temp": 0.1,
            "oil_temp": 0.1,
            "intake_temp": 0.1,
            "egt1": 0.1,
            "egt2": 0.1,
        }
    )

    def __post_init__(self):
        """Initialize internal state."""
        self._filters: Dict[str, ExponentialMovingAverage] = {}
        self._configs: Dict[str, SmootherConfig] = {}

    def configure(
        self, channel: str, alpha: Optional[float] = None, enabled: bool = True
    ) -> None:
        """
        Configure smoothing for a channel.

        Args:
            channel: Channel name (e.g., "rpm", "coolant_temp").
            alpha: Smoothing factor. If None, uses default for channel.
            enabled: Whether smoothing is enabled for this channel.
        """
        if alpha is None:
            alpha = self.DEFAULT_ALPHAS.get(channel, 0.3)

        self._configs[channel] = SmootherConfig(alpha=alpha, enabled=enabled)

        # Update existing filter if present
        if channel in self._filters:
            self._filters[channel].alpha = alpha

    def update(self, channel: str, value: float) -> float:
        """
        Update a channel with a new value.

        Args:
            channel: Channel name.
            value: New raw value.

        Returns:
            Smoothed value (or raw if smoothing disabled).
        """
        config = self._configs.get(channel)

        # If not configured, use defaults
        if config is None:
            self.configure(channel)
            config = self._configs[channel]

        # Return raw if disabled
        if not config.enabled:
            return value

        # Get or create filter
        if channel not in self._filters:
            self._filters[channel] = ExponentialMovingAverage(
                alpha=config.alpha, initial_value=value
            )
            return value

        return self._filters[channel].update(value)

    def get(self, channel: str) -> Optional[float]:
        """
        Get current smoothed value for a channel.

        Args:
            channel: Channel name.

        Returns:
            Current smoothed value, or None if not initialized.
        """
        if channel in self._filters:
            return self._filters[channel].value
        return None

    def reset(self, channel: Optional[str] = None) -> None:
        """
        Reset filter state.

        Args:
            channel: Channel to reset. If None, resets all channels.
        """
        if channel is None:
            self._filters.clear()
        elif channel in self._filters:
            del self._filters[channel]

    def smooth_state(self, state: "VehicleState") -> "VehicleState":
        """
        Apply smoothing to all values in a VehicleState.

        Args:
            state: Raw vehicle state.

        Returns:
            New VehicleState with smoothed values.
        """
        from ..data.models import VehicleState

        return VehicleState(
            rpm=int(self.update("rpm", state.rpm)),
            speed=self.update("speed", state.speed),
            gear=state.gear,  # Don't smooth discrete values
            boost_pressure=self.update("boost_pressure", state.boost_pressure),
            map_kpa=self.update("map_kpa", state.map_kpa),
            oil_pressure=self.update("oil_pressure", state.oil_pressure),
            fuel_pressure=self.update("fuel_pressure", state.fuel_pressure),
            coolant_temp=self.update("coolant_temp", state.coolant_temp),
            oil_temp=self.update("oil_temp", state.oil_temp),
            intake_temp=self.update("intake_temp", state.intake_temp),
            egt1=self.update("egt1", state.egt1),
            egt2=self.update("egt2", state.egt2),
            afr=self.update("afr", state.afr),
            lambda_value=self.update("lambda_value", state.lambda_value),
            lambda_target=state.lambda_target,  # Target doesn't need smoothing
            tps=self.update("tps", state.tps),
            injector_duty=self.update("injector_duty", state.injector_duty),
            ignition_angle=self.update("ignition_angle", state.ignition_angle),
            battery_voltage=self.update("battery_voltage", state.battery_voltage),
            fuel_level=self.update("fuel_level", state.fuel_level),
            flags=state.flags,
            warnings=state.warnings,
            timestamp=state.timestamp,
        )
