"""
Base widget class for all RoboDash dashboard components.

Provides common functionality for:
- Value management with min/max clamping
- Warning/critical thresholds
- Color state based on value
- Update optimization
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal
from PyQt5.QtGui import QColor

from ..themes import get_current_theme


class BaseWidget(QWidget):
    """
    Abstract base class for all dashboard widgets.

    Provides:
    - Value property with change detection
    - Min/max range with clamping
    - Warning and critical thresholds
    - Automatic color selection based on value state
    """

    # Signal emitted when value changes
    value_changed = pyqtSignal(float)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize base widget.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Value state
        self._value: float = 0.0
        self._min_value: float = 0.0
        self._max_value: float = 100.0
        self._previous_value: float = 0.0

        # Thresholds
        self._warning_threshold: Optional[float] = None
        self._critical_threshold: Optional[float] = None
        self._warning_low_threshold: Optional[float] = None

        # Display formatting
        self._format_string: str = "{:.0f}"
        self._unit_label: str = ""
        self._label: str = ""

        # Performance optimization
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        # Cache theme reference
        self._theme = get_current_theme()

    # =========================================================================
    # Value Property
    # =========================================================================

    @pyqtProperty(float)
    def value(self) -> float:
        """Get current value."""
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        """
        Set value with clamping and change detection.

        Args:
            val: New value to set.
        """
        # Clamp to range
        clamped = max(self._min_value, min(self._max_value, val))

        # Only update if changed
        if clamped != self._value:
            self._previous_value = self._value
            self._value = clamped
            self.value_changed.emit(clamped)
            self.update()  # Schedule repaint

    # =========================================================================
    # Range Configuration
    # =========================================================================

    def set_range(self, min_val: float, max_val: float) -> None:
        """
        Set the value range.

        Args:
            min_val: Minimum value.
            max_val: Maximum value.
        """
        self._min_value = min_val
        self._max_value = max_val

        # Re-clamp current value
        self._value = max(min_val, min(max_val, self._value))
        self.update()

    @property
    def min_value(self) -> float:
        """Get minimum value."""
        return self._min_value

    @property
    def max_value(self) -> float:
        """Get maximum value."""
        return self._max_value

    @property
    def value_range(self) -> float:
        """Get the range (max - min)."""
        return self._max_value - self._min_value

    @property
    def value_percent(self) -> float:
        """Get value as percentage of range (0.0 to 1.0)."""
        if self.value_range == 0:
            return 0.0
        return (self._value - self._min_value) / self.value_range

    # =========================================================================
    # Threshold Configuration
    # =========================================================================

    def set_thresholds(
        self,
        warning: Optional[float] = None,
        critical: Optional[float] = None,
        warning_low: Optional[float] = None
    ) -> None:
        """
        Set warning and critical thresholds.

        Args:
            warning: Warning threshold (high).
            critical: Critical threshold (high).
            warning_low: Warning threshold (low).
        """
        self._warning_threshold = warning
        self._critical_threshold = critical
        self._warning_low_threshold = warning_low
        self.update()

    # =========================================================================
    # Value State
    # =========================================================================

    def get_value_state(self) -> str:
        """
        Get current value state based on thresholds.

        Returns:
            "normal", "warning", or "critical"
        """
        # Check critical first (highest priority)
        if self._critical_threshold is not None:
            if self._value >= self._critical_threshold:
                return "critical"

        # Check warning thresholds
        if self._warning_threshold is not None:
            if self._value >= self._warning_threshold:
                return "warning"

        if self._warning_low_threshold is not None:
            if self._value <= self._warning_low_threshold:
                return "warning"

        return "normal"

    def get_value_color(self) -> QColor:
        """
        Get color based on current value state.

        Returns:
            QColor for the current state.
        """
        state = self.get_value_state()

        if state == "critical":
            return QColor(self._theme.CRITICAL)
        elif state == "warning":
            return QColor(self._theme.WARNING)
        else:
            return QColor(self._theme.NORMAL)

    def get_value_color_hex(self) -> str:
        """
        Get hex color string based on current value state.

        Returns:
            Hex color string (e.g., "#9EFF11").
        """
        state = self.get_value_state()

        if state == "critical":
            return self._theme.CRITICAL
        elif state == "warning":
            return self._theme.WARNING
        else:
            return self._theme.NORMAL

    # =========================================================================
    # Display Formatting
    # =========================================================================

    def set_format(self, format_string: str) -> None:
        """
        Set the format string for value display.

        Args:
            format_string: Python format string (e.g., "{:.1f}").
        """
        self._format_string = format_string
        self.update()

    def set_unit(self, unit: str) -> None:
        """
        Set the unit label.

        Args:
            unit: Unit string (e.g., "mph", "°C").
        """
        self._unit_label = unit
        self.update()

    def set_label(self, label: str) -> None:
        """
        Set the widget label.

        Args:
            label: Label string (e.g., "Speed", "Oil Temp").
        """
        self._label = label
        self.update()

    def get_formatted_value(self) -> str:
        """
        Get the value formatted as a string.

        Returns:
            Formatted value string.
        """
        return self._format_string.format(self._value)

    def get_display_text(self) -> str:
        """
        Get full display text with unit.

        Returns:
            Value with unit (e.g., "120 mph").
        """
        if self._unit_label:
            return f"{self.get_formatted_value()} {self._unit_label}"
        return self.get_formatted_value()

    # =========================================================================
    # Theme Access
    # =========================================================================

    @property
    def theme(self):
        """Get current theme."""
        return self._theme

    def refresh_theme(self) -> None:
        """Refresh theme reference and repaint."""
        self._theme = get_current_theme()
        self.update()
