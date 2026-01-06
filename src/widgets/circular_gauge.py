"""
Circular gauge widgets for analog-style displays.

Provides:
- CircularGauge: Generic circular gauge
- Tachometer: RPM-optimized gauge with shift zones
"""

import math
from typing import List, Optional, Tuple

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
)
from PyQt5.QtWidgets import QWidget

from .base_widget import BaseWidget


class CircularGauge(BaseWidget):
    """
    Circular analog gauge widget.

    Features:
    - Configurable arc range
    - Colored zones
    - Tick marks and labels
    - Animated needle
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize circular gauge."""
        super().__init__(parent)

        # Arc configuration (degrees, 0 = 3 o'clock, CCW positive)
        self._start_angle: float = 225  # Start at 7:30 position
        self._end_angle: float = -45  # End at 4:30 position
        self._span_angle: float = self._start_angle - self._end_angle

        # Visual settings
        self._arc_width: float = 15
        self._needle_width: float = 4
        self._show_ticks: bool = True
        self._show_labels: bool = True
        self._show_value: bool = True

        # Colored zones: list of (start_value, end_value, color)
        self._zones: List[Tuple[float, float, str]] = []

        # Tick configuration
        self._major_tick_interval: float = 1000
        self._minor_tick_interval: float = 500
        self._label_interval: float = 1000
        self._label_format: str = "{:.0f}"

        self.setMinimumSize(150, 150)

    def set_arc_angles(self, start: float, end: float) -> None:
        """
        Set the arc start and end angles.

        Args:
            start: Start angle in degrees (0 = 3 o'clock).
            end: End angle in degrees.
        """
        self._start_angle = start
        self._end_angle = end
        self._span_angle = start - end
        self.update()

    def add_zone(self, start_value: float, end_value: float, color: str) -> None:
        """
        Add a colored zone to the gauge.

        Args:
            start_value: Zone start value.
            end_value: Zone end value.
            color: Hex color string.
        """
        self._zones.append((start_value, end_value, color))
        self.update()

    def clear_zones(self) -> None:
        """Remove all colored zones."""
        self._zones.clear()
        self.update()

    def set_tick_intervals(
        self,
        major: float,
        minor: Optional[float] = None,
        labels: Optional[float] = None,
    ) -> None:
        """
        Set tick mark intervals.

        Args:
            major: Major tick interval.
            minor: Minor tick interval (default: major/2).
            labels: Label interval (default: major).
        """
        self._major_tick_interval = major
        self._minor_tick_interval = minor or major / 2
        self._label_interval = labels or major
        self.update()

    def _value_to_angle(self, value: float) -> float:
        """Convert value to angle in degrees."""
        percent = (value - self._min_value) / self.value_range
        return self._start_angle - (percent * self._span_angle)

    def paintEvent(self, event) -> None:
        """Paint the circular gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate dimensions
        rect = self.rect()
        size = min(rect.width(), rect.height())
        center = QPointF(rect.center())

        # Outer radius with padding
        padding = 10
        outer_radius = (size / 2) - padding
        inner_radius = outer_radius - self._arc_width

        # Draw background arc
        self._draw_background_arc(painter, center, outer_radius, inner_radius)

        # Draw zones
        self._draw_zones(painter, center, outer_radius, inner_radius)

        # Draw tick marks
        if self._show_ticks:
            self._draw_ticks(painter, center, outer_radius)

        # Draw labels
        if self._show_labels:
            self._draw_labels(painter, center, outer_radius)

        # Draw needle
        self._draw_needle(painter, center, inner_radius * 0.95)

        # Draw center cap
        self._draw_center_cap(painter, center)

        # Draw value text
        if self._show_value:
            self._draw_value(painter, center, inner_radius)

        painter.end()

    def _draw_background_arc(
        self, painter: QPainter, center: QPointF, outer_r: float, inner_r: float
    ) -> None:
        """Draw the background arc."""
        pen = QPen(QColor(self.theme.GAUGE_ARC), self._arc_width)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)

        arc_rect = QRectF(
            center.x() - outer_r + self._arc_width / 2,
            center.y() - outer_r + self._arc_width / 2,
            (outer_r - self._arc_width / 2) * 2,
            (outer_r - self._arc_width / 2) * 2,
        )

        # Qt uses 16ths of a degree
        painter.drawArc(arc_rect, int(self._end_angle * 16), int(self._span_angle * 16))

    def _draw_zones(
        self, painter: QPainter, center: QPointF, outer_r: float, inner_r: float
    ) -> None:
        """Draw colored zones."""
        for start_val, end_val, color in self._zones:
            start_angle = self._value_to_angle(start_val)
            end_angle = self._value_to_angle(end_val)
            span = start_angle - end_angle

            pen = QPen(QColor(color), self._arc_width)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)

            arc_rect = QRectF(
                center.x() - outer_r + self._arc_width / 2,
                center.y() - outer_r + self._arc_width / 2,
                (outer_r - self._arc_width / 2) * 2,
                (outer_r - self._arc_width / 2) * 2,
            )

            painter.drawArc(arc_rect, int(end_angle * 16), int(span * 16))

    def _draw_ticks(self, painter: QPainter, center: QPointF, radius: float) -> None:
        """Draw tick marks."""
        pen_major = QPen(QColor(self.theme.TEXT_PRIMARY), 2)
        pen_minor = QPen(QColor(self.theme.TEXT_SECONDARY), 1)

        tick_outer = radius - self._arc_width - 2
        tick_inner_major = tick_outer - 12
        tick_inner_minor = tick_outer - 6

        value = self._min_value
        while value <= self._max_value:
            angle = math.radians(self._value_to_angle(value))

            # Determine if major or minor tick
            is_major = abs(value % self._major_tick_interval) < 0.001

            if is_major:
                painter.setPen(pen_major)
                inner = tick_inner_major
            else:
                painter.setPen(pen_minor)
                inner = tick_inner_minor

            # Calculate tick positions
            cos_a = math.cos(angle)
            sin_a = -math.sin(angle)  # Negative for Qt coordinate system

            x1 = center.x() + inner * cos_a
            y1 = center.y() + inner * sin_a
            x2 = center.x() + tick_outer * cos_a
            y2 = center.y() + tick_outer * sin_a

            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            value += self._minor_tick_interval

    def _draw_labels(self, painter: QPainter, center: QPointF, radius: float) -> None:
        """Draw value labels."""
        font = QFont("Roboto", 10)
        painter.setFont(font)
        painter.setPen(QColor(self.theme.TEXT_SECONDARY))

        label_radius = radius - self._arc_width - 22

        value = self._min_value
        while value <= self._max_value:
            if abs(value % self._label_interval) < 0.001:
                angle = math.radians(self._value_to_angle(value))

                x = center.x() + label_radius * math.cos(angle)
                y = center.y() - label_radius * math.sin(angle)

                # Format label (divide by 1000 for RPM)
                if self._max_value >= 1000:
                    label_text = f"{int(value / 1000)}"
                else:
                    label_text = self._label_format.format(value)

                # Center text on position
                text_rect = QRectF(x - 15, y - 8, 30, 16)
                painter.drawText(text_rect, int(Qt.AlignCenter), label_text)

            value += self._label_interval

    def _draw_needle(self, painter: QPainter, center: QPointF, length: float) -> None:
        """Draw the gauge needle."""
        angle = math.radians(self._value_to_angle(self._value))

        # Needle tip
        tip_x = center.x() + length * math.cos(angle)
        tip_y = center.y() - length * math.sin(angle)

        # Needle base (slightly behind center)
        base_length = 15
        base_x = center.x() - base_length * math.cos(angle)
        base_y = center.y() + base_length * math.sin(angle)

        # Draw needle
        pen = QPen(QColor(self.theme.GAUGE_NEEDLE), self._needle_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(base_x, base_y), QPointF(tip_x, tip_y))

    def _draw_center_cap(self, painter: QPainter, center: QPointF) -> None:
        """Draw center cap over needle pivot."""
        cap_radius = 8

        # Outer cap
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self.theme.SURFACE_ELEVATED)))
        painter.drawEllipse(center, cap_radius, cap_radius)

        # Inner highlight
        painter.setBrush(QBrush(QColor(self.theme.ROBOTECHY_GREEN)))
        painter.drawEllipse(center, cap_radius - 3, cap_radius - 3)

    def _draw_value(self, painter: QPainter, center: QPointF, radius: float) -> None:
        """Draw current value text."""
        font = QFont("Roboto", 14)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(self.get_value_color())

        # Position below center
        text_rect = QRectF(center.x() - 50, center.y() + radius * 0.3, 100, 30)
        painter.drawText(text_rect, int(Qt.AlignCenter), self.get_formatted_value())


class Tachometer(CircularGauge):
    """
    RPM tachometer with shift zones.

    Pre-configured for typical automotive RPM display with
    green/yellow/red zones.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize tachometer."""
        super().__init__(parent)

        # Configure for RPM
        self.set_range(0, 8000)
        self.set_tick_intervals(1000, 500, 1000)
        self.set_format("{:.0f}")
        self.set_label("RPM")

        # Add default zones
        self.add_zone(0, 6000, self.theme.RPM_ZONE_NORMAL)
        self.add_zone(6000, 6800, self.theme.RPM_ZONE_WARNING)
        self.add_zone(6800, 8000, self.theme.RPM_ZONE_REDLINE)

        # Set thresholds
        self.set_thresholds(warning=6800, critical=7200)

    def set_redline(self, rpm: int) -> None:
        """
        Set the redline RPM.

        Args:
            rpm: Redline RPM value.
        """
        self.clear_zones()
        shift_point = int(rpm * 0.85)
        warning_start = int(rpm * 0.75)

        self.add_zone(0, warning_start, self.theme.RPM_ZONE_NORMAL)
        self.add_zone(warning_start, shift_point, self.theme.RPM_ZONE_WARNING)
        self.add_zone(shift_point, self._max_value, self.theme.RPM_ZONE_REDLINE)

        self.set_thresholds(warning=shift_point, critical=rpm)
