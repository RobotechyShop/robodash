"""
Shift light indicator widget.

Visual indicator that activates progressively as RPM approaches
the shift point, with flash at redline.
"""

from typing import Optional

from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QWidget

from .base_widget import BaseWidget


class ShiftLight(BaseWidget):
    """
    Progressive shift light indicator.

    Displays a row of LED-style indicators that light up progressively
    as RPM increases. Flashes when at redline.

    Layout (horizontal):
    [G][G][G][Y][Y][R][R][R]
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize shift light."""
        super().__init__(parent)

        # Configuration
        self._led_count: int = 12
        self._horizontal: bool = True
        self._led_spacing: int = 4
        self._led_size: int = 20

        # RPM thresholds
        self._activation_rpm: int = 5000  # Start lighting
        self._shift_rpm: int = 6800  # Yellow zone
        self._redline_rpm: int = 7200  # Red zone / flash
        self._max_rpm: int = 8000

        # Flash state
        self._flash_active: bool = False
        self._flash_state: bool = False
        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._toggle_flash)
        self._flash_interval: int = 50  # ms

        # Colors
        self._color_off = self.theme.SHIFT_LIGHT_OFF
        self._color_green = self.theme.SHIFT_LIGHT_GREEN
        self._color_yellow = self.theme.SHIFT_LIGHT_YELLOW
        self._color_red = self.theme.SHIFT_LIGHT_RED
        self._color_flash = self.theme.SHIFT_LIGHT_FLASH

        self.setMinimumSize(200, 30)

    def set_rpm_thresholds(
        self, activation: int, shift: int, redline: int, max_rpm: int = 8000
    ) -> None:
        """
        Set RPM thresholds for shift light behavior.

        Args:
            activation: RPM when first LED lights.
            shift: RPM when yellow LEDs start.
            redline: RPM when red LEDs and flash start.
            max_rpm: Maximum RPM scale.
        """
        self._activation_rpm = activation
        self._shift_rpm = shift
        self._redline_rpm = redline
        self._max_rpm = max_rpm
        self.update()

    def set_led_count(self, count: int) -> None:
        """Set number of LEDs."""
        self._led_count = max(4, min(20, count))
        self.update()

    def set_horizontal(self, horizontal: bool) -> None:
        """Set orientation."""
        self._horizontal = horizontal
        self.update()

    @property
    def rpm(self) -> int:
        """Get current RPM."""
        return int(self._value)

    @rpm.setter
    def rpm(self, value: int) -> None:
        """Set current RPM."""
        self.value = float(value)
        self._update_flash_state()

    def _update_flash_state(self) -> None:
        """Update flash state based on RPM."""
        should_flash = self._value >= self._redline_rpm

        if should_flash and not self._flash_active:
            self._flash_active = True
            self._flash_timer.start(self._flash_interval)
        elif not should_flash and self._flash_active:
            self._flash_active = False
            self._flash_timer.stop()
            self._flash_state = False
            self.update()

    def _toggle_flash(self) -> None:
        """Toggle flash state."""
        self._flash_state = not self._flash_state
        self.update()

    def _get_active_led_count(self) -> int:
        """Calculate how many LEDs should be lit."""
        if self._value < self._activation_rpm:
            return 0

        # Linear interpolation from activation to max
        rpm_range = self._max_rpm - self._activation_rpm
        rpm_progress = self._value - self._activation_rpm

        return int((rpm_progress / rpm_range) * self._led_count)

    def _get_led_color(self, index: int, is_active: bool) -> QColor:
        """
        Get color for LED at given index.

        Args:
            index: LED index (0-based).
            is_active: Whether LED is currently lit.

        Returns:
            QColor for the LED.
        """
        if not is_active:
            return QColor(self._color_off)

        # Flash override at redline
        if self._flash_active and self._flash_state:
            return QColor(self._color_flash)

        # Calculate which zone this LED is in
        led_rpm = self._activation_rpm + (
            (index / self._led_count) * (self._max_rpm - self._activation_rpm)
        )

        if led_rpm >= self._redline_rpm:
            return QColor(self._color_red)
        elif led_rpm >= self._shift_rpm:
            return QColor(self._color_yellow)
        else:
            return QColor(self._color_green)

    def paintEvent(self, event) -> None:
        """Paint the shift light."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        active_count = self._get_active_led_count()

        if self._horizontal:
            self._draw_horizontal(painter, rect, active_count)
        else:
            self._draw_vertical(painter, rect, active_count)

        painter.end()

    def _draw_horizontal(self, painter: QPainter, rect, active_count: int) -> None:
        """Draw horizontal shift light bar."""
        # Calculate LED dimensions
        total_width = (
            self._led_count * self._led_size + (self._led_count - 1) * self._led_spacing
        )
        start_x = rect.center().x() - total_width / 2
        center_y = rect.center().y()

        for i in range(self._led_count):
            x = start_x + i * (self._led_size + self._led_spacing)
            is_active = i < active_count

            led_rect = QRectF(
                x, center_y - self._led_size / 2, self._led_size, self._led_size
            )

            # Draw LED
            color = self._get_led_color(i, is_active)

            # Outer glow for active LEDs
            if is_active:
                glow_color = QColor(color)
                glow_color.setAlpha(80)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(glow_color))
                painter.drawEllipse(led_rect.adjusted(-3, -3, 3, 3))

            # Main LED
            painter.setPen(QPen(QColor(self.theme.BORDER), 1))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(led_rect)

            # Highlight for active LEDs
            if is_active:
                highlight = QColor(255, 255, 255, 100)
                painter.setBrush(QBrush(highlight))
                painter.setPen(Qt.NoPen)
                highlight_rect = QRectF(
                    led_rect.left() + led_rect.width() * 0.2,
                    led_rect.top() + led_rect.height() * 0.15,
                    led_rect.width() * 0.3,
                    led_rect.height() * 0.25,
                )
                painter.drawEllipse(highlight_rect)

    def _draw_vertical(self, painter: QPainter, rect, active_count: int) -> None:
        """Draw vertical shift light bar."""
        total_height = (
            self._led_count * self._led_size + (self._led_count - 1) * self._led_spacing
        )
        center_x = rect.center().x()
        start_y = rect.center().y() + total_height / 2  # Start from bottom

        for i in range(self._led_count):
            y = start_y - i * (self._led_size + self._led_spacing) - self._led_size
            is_active = i < active_count

            led_rect = QRectF(
                center_x - self._led_size / 2, y, self._led_size, self._led_size
            )

            color = self._get_led_color(i, is_active)

            painter.setPen(QPen(QColor(self.theme.BORDER), 1))
            painter.setBrush(QBrush(color))
            painter.drawEllipse(led_rect)

    def stop(self) -> None:
        """Stop flash timer (call when widget is destroyed)."""
        self._flash_timer.stop()
