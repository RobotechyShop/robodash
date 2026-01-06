"""
Warning indicator widgets for status and alert displays.

Provides visual indicators for:
- Engine warnings
- Sensor faults
- Status indicators
"""

from typing import Optional

from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from .base_widget import BaseWidget


class WarningIndicator(BaseWidget):
    """
    Warning/status indicator widget.

    Displays an icon or text indicator that can be:
    - Off (inactive)
    - On (active, steady)
    - Flashing (active, blinking)
    """

    def __init__(self, label: str = "", parent: Optional[QWidget] = None):
        """
        Initialize warning indicator.

        Args:
            label: Short label text (e.g., "OIL", "TEMP").
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._label = label
        self._active: bool = False
        self._flashing: bool = False
        self._flash_state: bool = True

        # Colors
        self._color_active = self.theme.WARNING
        self._color_inactive = self.theme.SURFACE_ELEVATED
        self._color_critical = self.theme.CRITICAL

        # Flash timer
        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._toggle_flash)
        self._flash_interval: int = 300  # ms

        # Size
        self._indicator_size: int = 40
        self.setMinimumSize(50, 50)

    @property
    def active(self) -> bool:
        """Get active state."""
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        """Set active state."""
        if value != self._active:
            self._active = value
            self.update()

    def set_active(self, active: bool, flash: bool = False) -> None:
        """
        Set indicator active state.

        Args:
            active: Whether indicator is active.
            flash: Whether to flash when active.
        """
        self._active = active
        self._flashing = flash and active

        if self._flashing and not self._flash_timer.isActive():
            self._flash_timer.start(self._flash_interval)
        elif not self._flashing and self._flash_timer.isActive():
            self._flash_timer.stop()
            self._flash_state = True

        self.update()

    def set_color(self, color: str) -> None:
        """Set active color."""
        self._color_active = color
        self.update()

    def set_critical(self) -> None:
        """Set to critical (red) color."""
        self._color_active = self._color_critical
        self.update()

    def _toggle_flash(self) -> None:
        """Toggle flash state."""
        self._flash_state = not self._flash_state
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the warning indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = self.rect()
        center = rect.center()

        # Determine current display color
        if self._active:
            if self._flashing and not self._flash_state:
                color = QColor(self._color_inactive)
            else:
                color = QColor(self._color_active)
        else:
            color = QColor(self._color_inactive)

        # Draw indicator circle/box
        indicator_rect = QRectF(
            center.x() - self._indicator_size / 2,
            center.y() - self._indicator_size / 2 - 5,
            self._indicator_size,
            self._indicator_size,
        )

        # Glow effect for active state
        if self._active and (not self._flashing or self._flash_state):
            glow_color = QColor(color)
            glow_color.setAlpha(60)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(indicator_rect.adjusted(-5, -5, 5, 5))

        # Main indicator
        painter.setPen(QPen(QColor(self.theme.BORDER), 2))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(indicator_rect)

        # Draw label
        if self._label:
            font = QFont("Roboto", 9)
            font.setBold(True)
            painter.setFont(font)

            if self._active and (not self._flashing or self._flash_state):
                # Dark text on bright background
                painter.setPen(QColor(self.theme.BACKGROUND))
            else:
                painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            painter.drawText(indicator_rect, int(Qt.AlignCenter), self._label)

        painter.end()

    def stop(self) -> None:
        """Stop flash timer."""
        self._flash_timer.stop()


class StatusLED(WarningIndicator):
    """Simple LED-style status indicator."""

    def __init__(self, label: str = "", parent: Optional[QWidget] = None):
        """Initialize status LED."""
        super().__init__(label, parent)

        self._indicator_size = 16
        self.setMinimumSize(24, 24)
        self.setMaximumSize(32, 32)

    def paintEvent(self, event) -> None:
        """Paint small LED indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()

        # Determine color
        if self._active:
            if self._flashing and not self._flash_state:
                color = QColor(self._color_inactive)
            else:
                color = QColor(self._color_active)
        else:
            color = QColor(self._color_inactive)

        # Draw LED
        led_rect = QRectF(
            center.x() - self._indicator_size / 2,
            center.y() - self._indicator_size / 2,
            self._indicator_size,
            self._indicator_size,
        )

        painter.setPen(QPen(QColor(self.theme.BORDER), 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(led_rect)

        # Highlight
        if self._active:
            highlight = QColor(255, 255, 255, 80)
            painter.setBrush(QBrush(highlight))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(led_rect.adjusted(3, 2, -6, -8))

        painter.end()


class WarningPanel(QWidget):
    """
    Panel containing multiple warning indicators.

    Groups related warnings together in a compact display.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize warning panel."""
        super().__init__(parent)

        from PyQt5.QtWidgets import QHBoxLayout

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        self._indicators = {}

    def add_indicator(self, name: str, label: str) -> WarningIndicator:
        """
        Add a warning indicator.

        Args:
            name: Internal identifier.
            label: Display label.

        Returns:
            The created indicator.
        """
        indicator = WarningIndicator(label, self)
        self._indicators[name] = indicator
        self._layout.addWidget(indicator)
        return indicator

    def set_warning(self, name: str, active: bool, flash: bool = False) -> None:
        """
        Set warning state for an indicator.

        Args:
            name: Indicator name.
            active: Whether warning is active.
            flash: Whether to flash.
        """
        if name in self._indicators:
            self._indicators[name].set_active(active, flash)

    def clear_all(self) -> None:
        """Clear all warnings."""
        for indicator in self._indicators.values():
            indicator.set_active(False)

    def stop_all(self) -> None:
        """Stop all flash timers."""
        for indicator in self._indicators.values():
            indicator.stop()
