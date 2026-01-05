"""
Metric box widget for compact labeled value displays.

Used for secondary metrics like temperatures, pressures, and voltages.
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont

from .base_widget import BaseWidget


class MetricBox(BaseWidget):
    """
    Compact labeled value display widget.

    Shows a label, value, and optional unit in a bordered box.
    Designed for secondary metrics that need to be visible but
    not dominant.

    Layout:
    ┌─────────────┐
    │ Label       │
    │   45.0 psi  │
    └─────────────┘
    """

    def __init__(
        self,
        label: str = "",
        parent: Optional[QWidget] = None
    ):
        """
        Initialize metric box.

        Args:
            label: Display label for this metric.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._label = label
        self._decimals: int = 1
        self._show_border: bool = True
        self._compact: bool = False

        # Padding
        self._padding: int = 8

        self.setMinimumSize(120, 80)

    def set_decimals(self, decimals: int) -> None:
        """Set number of decimal places."""
        self._decimals = decimals
        self._format_string = f"{{:.{decimals}f}}"
        self.update()

    def set_compact(self, compact: bool) -> None:
        """Enable compact mode (smaller text, less padding)."""
        self._compact = compact
        self.update()

    def set_show_border(self, show: bool) -> None:
        """Toggle border visibility."""
        self._show_border = show
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the metric box."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        padding = self._padding if not self._compact else 4

        # Always draw solid background first
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#0A0A0A")))
        painter.drawRect(rect)

        # Draw background and border
        painter.setPen(QPen(QColor(self.theme.BOX_BORDER), 1))
        painter.setBrush(QBrush(QColor(self.theme.BOX_BACKGROUND)))
        painter.drawRoundedRect(
            rect.adjusted(1, 1, -1, -1),
            4, 4
        )

        # Calculate text areas
        inner_rect = rect.adjusted(padding, padding, -padding, -padding)

        label_height = inner_rect.height() * 0.3 if not self._compact else inner_rect.height() * 0.25
        value_height = inner_rect.height() - label_height

        # Font sizes - larger for readability
        label_font_size = 14 if not self._compact else 10
        value_font_size = int(value_height * 0.6) if not self._compact else int(value_height * 0.5)
        value_font_size = max(value_font_size, 18)  # Minimum readable size

        # Draw label
        label_font = QFont("Roboto", label_font_size)
        painter.setFont(label_font)
        painter.setPen(QColor(self.theme.BOX_LABEL))

        label_rect = QRectF(
            inner_rect.left(),
            inner_rect.top(),
            inner_rect.width(),
            label_height
        )
        painter.drawText(label_rect, Qt.AlignLeft | Qt.AlignTop, self._label)

        # Draw value
        value_font = QFont("Roboto", value_font_size)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(self.get_value_color())

        value_text = self.get_formatted_value()

        value_rect = QRectF(
            inner_rect.left(),
            inner_rect.top() + label_height,
            inner_rect.width(),
            value_height * 0.7
        )
        painter.drawText(value_rect, Qt.AlignLeft | Qt.AlignVCenter, value_text)

        # Draw unit
        if self._unit_label:
            unit_font = QFont("Roboto", label_font_size)
            painter.setFont(unit_font)
            painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            unit_rect = QRectF(
                inner_rect.left(),
                inner_rect.bottom() - label_height,
                inner_rect.width(),
                label_height
            )
            painter.drawText(unit_rect, Qt.AlignLeft | Qt.AlignBottom, self._unit_label)

        painter.end()


class TemperatureBox(MetricBox):
    """Pre-configured metric box for temperatures."""

    def __init__(
        self,
        label: str = "Temperature",
        parent: Optional[QWidget] = None
    ):
        """Initialize temperature box."""
        super().__init__(label, parent)

        self.set_range(0, 150)
        self.set_decimals(0)
        self.set_unit("°C")


class PressureBox(MetricBox):
    """Pre-configured metric box for pressures."""

    def __init__(
        self,
        label: str = "Pressure",
        parent: Optional[QWidget] = None
    ):
        """Initialize pressure box."""
        super().__init__(label, parent)

        self.set_range(0, 10)
        self.set_decimals(1)
        self.set_unit("bar")


class VoltageBox(MetricBox):
    """Pre-configured metric box for voltage."""

    def __init__(
        self,
        label: str = "Battery",
        parent: Optional[QWidget] = None
    ):
        """Initialize voltage box."""
        super().__init__(label, parent)

        self.set_range(10, 16)
        self.set_decimals(1)
        self.set_unit("V")
        self.set_thresholds(warning=15.0, warning_low=12.0)
