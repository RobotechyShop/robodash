"""
Digital display widgets for large numeric readouts.

Provides clean, high-visibility numeric displays for:
- Speed
- Gear indicator
- Other large numeric values
"""

from typing import Optional

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtWidgets import QWidget

from .base_widget import BaseWidget, get_custom_font


class DigitalDisplay(BaseWidget):
    """
    Large numeric display widget.

    Renders a large, bold numeric value with optional label and unit.
    Designed for high visibility at a glance.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize digital display."""
        super().__init__(parent)

        # Display settings
        self._font_size_ratio: float = 0.6  # Relative to widget height
        self._show_unit: bool = True
        self._show_label: bool = True
        self._center_value: bool = True

        # Minimum size
        self.setMinimumSize(100, 60)

    def paintEvent(self, event) -> None:
        """Paint the digital display."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = self.rect()

        # Draw solid background
        painter.fillRect(rect, QColor("#0A0A0A"))

        # Reserve space for label and unit
        label_space = 25 if self._show_label and self._label else 0
        unit_space = 30 if self._show_unit and self._unit_label else 0

        # Calculate remaining space for value
        value_area_height = rect.height() - label_space - unit_space

        # Font sizes - scale to available space
        label_font_size = 14
        unit_font_size = 18
        value_font_size = min(
            180, max(30, int(value_area_height * self._font_size_ratio))
        )

        # Get value color
        value_color = self.get_value_color()

        # Get custom font
        font_name = get_custom_font()

        # Draw label (top)
        if self._show_label and self._label:
            label_font = QFont(font_name, label_font_size)
            painter.setFont(label_font)
            painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            label_rect = QRect(rect.left(), rect.top() + 2, rect.width(), label_space)
            painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, self._label)

        # Draw main value in center
        value_font = QFont(font_name, value_font_size)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(value_color)

        value_text = self.get_formatted_value()

        # Value occupies middle section
        value_rect = QRect(
            rect.left(), rect.top() + label_space, rect.width(), value_area_height
        )
        painter.drawText(value_rect, Qt.AlignCenter, value_text)

        # Draw unit at bottom
        if self._show_unit and self._unit_label:
            unit_font = QFont(font_name, unit_font_size)
            painter.setFont(unit_font)
            painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            unit_rect = QRect(
                rect.left(), rect.bottom() - unit_space, rect.width(), unit_space
            )
            painter.drawText(
                unit_rect, Qt.AlignHCenter | Qt.AlignVCenter, self._unit_label
            )

        painter.end()

    def set_font_size_ratio(self, ratio: float) -> None:
        """Set the font size as ratio of widget height."""
        self._font_size_ratio = max(0.2, min(0.9, ratio))
        self.update()

    def set_show_unit(self, show: bool) -> None:
        """Toggle unit display."""
        self._show_unit = show
        self.update()

    def set_show_label(self, show: bool) -> None:
        """Toggle label display."""
        self._show_label = show
        self.update()


class SpeedDisplay(DigitalDisplay):
    """
    Speed display optimized for vehicle speed.

    Large, centered speed value with unit indicator.
    Uses white text for maximum visibility.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize speed display."""
        super().__init__(parent)

        self.set_label("Speed")
        self.set_unit("mph")
        self.set_range(0, 200)
        self.set_format("{:.0f}")
        self._font_size_ratio = 1.0  # Maximum size for best visibility

    def get_value_color(self) -> QColor:
        """Speed always uses white for maximum visibility."""
        return QColor("#FFFFFF")


class GearIndicator(BaseWidget):
    """
    Gear indicator display.

    Shows current gear (N, R, 1-6) in a large, prominent display.
    Uses different colors for neutral, reverse, and forward gears.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize gear indicator."""
        super().__init__(parent)

        self._gear: int = 0  # 0=N, -1=R, 1-6=forward
        self._font_size_ratio: float = 0.7

        self.setMinimumSize(80, 80)

    @property
    def gear(self) -> int:
        """Get current gear."""
        return self._gear

    @gear.setter
    def gear(self, value: int) -> None:
        """Set gear value."""
        if value != self._gear:
            self._gear = value
            self.update()

    def get_gear_text(self) -> str:
        """Get display text for current gear."""
        if self._gear == 0:
            return "N"
        elif self._gear == -1:
            return "R"
        else:
            return str(self._gear)

    def get_gear_color(self) -> QColor:
        """Get color based on current gear."""
        if self._gear == 0:
            # Neutral - secondary color
            return QColor(self.theme.TEXT_SECONDARY)
        elif self._gear == -1:
            # Reverse - warning color
            return QColor(self.theme.WARNING)
        else:
            # Forward gear - accent color
            return QColor(self.theme.ROBOTECHY_GREEN)

    def paintEvent(self, event) -> None:
        """Paint the gear indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = self.rect()

        # Draw solid background
        painter.fillRect(rect, QColor("#0A0A0A"))

        # Get custom font
        font_name = get_custom_font()

        # Reserve space for label
        label_space = 30

        # Draw label at top
        label_font = QFont(font_name, 16)
        painter.setFont(label_font)
        painter.setPen(QColor(self.theme.TEXT_SECONDARY))

        label_rect = QRect(rect.left(), rect.top() + 5, rect.width(), label_space)
        painter.drawText(label_rect, Qt.AlignHCenter | Qt.AlignTop, "GEAR")

        # Draw gear - large, centered in remaining space
        gear_area_height = rect.height() - label_space
        gear_font_size = min(150, int(gear_area_height * 0.7))
        gear_font = QFont(font_name, gear_font_size)
        gear_font.setBold(True)
        painter.setFont(gear_font)
        painter.setPen(self.get_gear_color())

        gear_rect = QRect(
            rect.left(), rect.top() + label_space, rect.width(), gear_area_height
        )
        painter.drawText(gear_rect, Qt.AlignCenter, self.get_gear_text())

        painter.end()
