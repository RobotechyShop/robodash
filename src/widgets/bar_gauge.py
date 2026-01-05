"""
Bar gauge widgets for linear indicator displays.

Provides:
- BarGauge: Generic bar indicator
- HorizontalBar: Horizontal fill bar
- RPMBar: Horizontal RPM bar with shift zones
"""

from typing import Optional, List, Tuple

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient, QFont

from .base_widget import BaseWidget


class BarGauge(BaseWidget):
    """
    Base bar gauge widget.

    Displays value as a filled bar with optional zones and labels.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize bar gauge."""
        super().__init__(parent)

        # Orientation
        self._horizontal: bool = True

        # Visual settings
        self._bar_height: int = 20
        self._show_label: bool = True
        self._show_value: bool = True
        self._show_ticks: bool = False

        # Zones: list of (start_pct, end_pct, color)
        self._zones: List[Tuple[float, float, str]] = []

        # Default to single color
        self._fill_color: str = self.theme.ROBOTECHY_GREEN
        self._background_color: str = self.theme.GAUGE_ARC

        self.setMinimumSize(200, 40)

    def set_horizontal(self, horizontal: bool) -> None:
        """Set bar orientation."""
        self._horizontal = horizontal
        self.update()

    def add_zone(self, start_pct: float, end_pct: float, color: str) -> None:
        """
        Add a colored zone.

        Args:
            start_pct: Zone start (0.0 to 1.0).
            end_pct: Zone end (0.0 to 1.0).
            color: Hex color string.
        """
        self._zones.append((start_pct, end_pct, color))
        self.update()

    def clear_zones(self) -> None:
        """Remove all zones."""
        self._zones.clear()
        self.update()

    def set_fill_color(self, color: str) -> None:
        """Set the fill color (used when no zones defined)."""
        self._fill_color = color
        self.update()

    def _get_fill_color_at(self, percent: float) -> str:
        """Get fill color at given percentage."""
        for start, end, color in self._zones:
            if start <= percent <= end:
                return color
        return self._fill_color

    def paintEvent(self, event) -> None:
        """Paint the bar gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        if self._horizontal:
            self._draw_horizontal(painter, rect)
        else:
            self._draw_vertical(painter, rect)

        painter.end()

    def _draw_horizontal(self, painter: QPainter, rect: QRect) -> None:
        """Draw horizontal bar."""
        # Calculate bar area
        label_height = 16 if self._show_label else 0
        value_width = 60 if self._show_value else 0

        bar_rect = QRect(
            rect.left(),
            rect.top() + label_height,
            rect.width() - value_width - 5,
            self._bar_height
        )

        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self._background_color)))
        painter.drawRoundedRect(bar_rect, 3, 3)

        # Draw fill
        fill_width = int(bar_rect.width() * self.value_percent)
        if fill_width > 0:
            fill_rect = QRect(
                bar_rect.left(),
                bar_rect.top(),
                fill_width,
                bar_rect.height()
            )

            # Use zones or single color
            if self._zones:
                self._draw_zoned_fill(painter, bar_rect, fill_rect)
            else:
                painter.setBrush(QBrush(QColor(self.get_value_color_hex())))
                painter.drawRoundedRect(fill_rect, 3, 3)

        # Draw label
        if self._show_label and self._label:
            font = QFont("Roboto", 10)
            painter.setFont(font)
            painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            label_rect = QRect(rect.left(), rect.top(), rect.width(), label_height)
            painter.drawText(label_rect, Qt.AlignLeft | Qt.AlignVCenter, self._label)

        # Draw value
        if self._show_value:
            font = QFont("Roboto", 12)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.get_value_color())

            value_rect = QRect(
                rect.right() - value_width,
                bar_rect.top(),
                value_width,
                bar_rect.height()
            )
            painter.drawText(
                value_rect,
                Qt.AlignRight | Qt.AlignVCenter,
                self.get_display_text()
            )

    def _draw_vertical(self, painter: QPainter, rect: QRect) -> None:
        """Draw vertical bar."""
        # Calculate bar area
        label_height = 16 if self._show_label else 0
        value_height = 20 if self._show_value else 0

        bar_rect = QRect(
            rect.left() + (rect.width() - self._bar_height) // 2,
            rect.top() + label_height,
            self._bar_height,
            rect.height() - label_height - value_height - 5
        )

        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self._background_color)))
        painter.drawRoundedRect(bar_rect, 3, 3)

        # Draw fill (from bottom)
        fill_height = int(bar_rect.height() * self.value_percent)
        if fill_height > 0:
            fill_rect = QRect(
                bar_rect.left(),
                bar_rect.bottom() - fill_height,
                bar_rect.width(),
                fill_height
            )
            painter.setBrush(QBrush(QColor(self.get_value_color_hex())))
            painter.drawRoundedRect(fill_rect, 3, 3)

        # Draw label
        if self._show_label and self._label:
            font = QFont("Roboto", 9)
            painter.setFont(font)
            painter.setPen(QColor(self.theme.TEXT_SECONDARY))

            label_rect = QRect(rect.left(), rect.top(), rect.width(), label_height)
            painter.drawText(label_rect, Qt.AlignCenter, self._label)

        # Draw value
        if self._show_value:
            font = QFont("Roboto", 10)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.get_value_color())

            value_rect = QRect(
                rect.left(),
                rect.bottom() - value_height,
                rect.width(),
                value_height
            )
            painter.drawText(value_rect, Qt.AlignCenter, self.get_formatted_value())

    def _draw_zoned_fill(
        self,
        painter: QPainter,
        bar_rect: QRect,
        fill_rect: QRect
    ) -> None:
        """Draw fill with colored zones."""
        # Create gradient based on zones
        gradient = QLinearGradient(bar_rect.left(), 0, bar_rect.right(), 0)

        for start_pct, end_pct, color in self._zones:
            gradient.setColorAt(start_pct, QColor(color))
            gradient.setColorAt(end_pct, QColor(color))

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(fill_rect, 3, 3)


class HorizontalBar(BarGauge):
    """Simple horizontal bar gauge."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize horizontal bar."""
        super().__init__(parent)
        self.set_horizontal(True)


class RPMBar(BarGauge):
    """
    Horizontal RPM bar with shift zones.

    Wide bar display optimized for the ultrawide screen format.
    Features curved arc design that sweeps upward.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize RPM bar."""
        super().__init__(parent)

        self.set_horizontal(True)
        self.set_range(0, 8000)
        self.set_label("RPM")
        self._show_value = False  # Value shown elsewhere
        self._bar_height = 180  # Much taller for 720p

        # More granular: 80 segments = 100 RPM each
        self._segment_count = 80

        # Add RPM zones
        self.add_zone(0.0, 0.75, self.theme.RPM_ZONE_NORMAL)
        self.add_zone(0.75, 0.85, self.theme.RPM_ZONE_WARNING)
        self.add_zone(0.85, 1.0, self.theme.RPM_ZONE_REDLINE)

        self.set_thresholds(warning=6800, critical=7200)

        self.setMinimumSize(400, 50)

    def paintEvent(self, event) -> None:
        """Custom paint for curved RPM bar - bars grow taller as RPM increases."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Draw solid background first
        painter.fillRect(rect, QColor("#0A0A0A"))

        padding = 10
        bar_width = rect.width() - padding * 2

        # Min and max bar heights (bars grow taller toward redline)
        min_bar_height = 60
        max_bar_height = self._bar_height - 30

        active_segments = int(self._segment_count * self.value_percent)
        segment_width = bar_width / self._segment_count
        segment_gap = 4  # Visible gap between bars

        # Draw segments - each bar gets progressively taller
        for i in range(self._segment_count):
            # Bar height increases with position (taller toward high RPM)
            progress = i / (self._segment_count - 1)
            bar_height = min_bar_height + (max_bar_height - min_bar_height) * progress

            seg_x = padding + i * segment_width + segment_gap / 2
            seg_y = rect.bottom() - bar_height - 15  # Aligned to bottom
            seg_w = segment_width - segment_gap
            seg_h = bar_height

            seg_rect = QRectF(seg_x, seg_y, seg_w, seg_h)

            # Determine segment color based on position
            seg_pct = (i + 0.5) / self._segment_count

            if i < active_segments:
                # Active segment - color based on zone
                if seg_pct > 0.90:
                    color = self.theme.RPM_ZONE_REDLINE
                elif seg_pct > 0.85:
                    color = "#FF5500"  # Orange transition
                elif seg_pct > 0.75:
                    color = self.theme.RPM_ZONE_WARNING
                else:
                    color = self.theme.RPM_ZONE_NORMAL
                painter.setPen(Qt.NoPen)
            else:
                # Inactive segment - darker
                color = "#222222"
                painter.setPen(Qt.NoPen)

            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(seg_rect, 2, 2)

        # Draw RPM markers below
        painter.setPen(QColor(self.theme.TEXT_SECONDARY))
        font = QFont("Roboto", 12)
        painter.setFont(font)

        marker_y = rect.bottom() - 18
        for rpm in range(0, 9000, 1000):
            x = padding + (rpm / 8000) * bar_width
            painter.drawText(
                QRectF(x - 20, marker_y, 40, 18),
                Qt.AlignCenter,
                str(rpm // 1000)
            )

        painter.end()


class FuelBar(BaseWidget):
    """
    Horizontal fuel gauge bar showing 0-100% with sliding fill.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize fuel bar."""
        super().__init__(parent)

        self.set_range(0, 100)
        self.set_label("FUEL")
        self.set_unit("%")
        self.set_thresholds(warning_low=20)

        self.setMinimumSize(300, 60)

    def paintEvent(self, event) -> None:
        """Paint the fuel bar gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Draw solid background
        painter.fillRect(rect, QColor("#0A0A0A"))

        padding = 10
        label_height = 25
        label_margin = 10  # Margin under FUEL text
        value_width = 80  # Wider to fit "100%"

        # Label at top
        painter.setPen(QColor(self.theme.TEXT_SECONDARY))
        font = QFont("Roboto", 14)
        painter.setFont(font)
        painter.drawText(
            QRectF(padding, 5, 100, label_height),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._label
        )

        # Bar area (with margin under label)
        bar_rect = QRectF(
            padding,
            label_height + label_margin,
            rect.width() - padding * 2 - value_width - 10,
            rect.height() - label_height - label_margin - 10
        )

        # Draw bar background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#222222")))
        painter.drawRoundedRect(bar_rect, 4, 4)

        # Draw fill based on percentage
        fill_width = bar_rect.width() * self.value_percent
        if fill_width > 0:
            fill_rect = QRectF(
                bar_rect.left(),
                bar_rect.top(),
                fill_width,
                bar_rect.height()
            )

            # Color based on level (configurable: 10% red, 25% amber)
            if self._value <= 10:
                color = self.theme.CRITICAL
            elif self._value <= 25:
                color = self.theme.WARNING
            else:
                color = self.theme.ROBOTECHY_GREEN

            painter.setBrush(QBrush(QColor(color)))
            painter.drawRoundedRect(fill_rect, 4, 4)

        # Draw percentage value on right
        value_font = QFont("Roboto", 22)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(self.get_value_color())

        value_rect = QRectF(
            rect.width() - value_width - padding,
            label_height + label_margin,
            value_width,
            rect.height() - label_height - label_margin - 10
        )
        painter.drawText(
            value_rect,
            Qt.AlignRight | Qt.AlignVCenter,
            f"{int(self._value)}%"
        )

        painter.end()
