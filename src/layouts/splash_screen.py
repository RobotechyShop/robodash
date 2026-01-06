"""
Splash screen with Robotechy branding.

Displays the Robotechy R logo during application startup
while initializing CAN communication and loading resources.
"""

from typing import Optional

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QWidget,
)

from ..core.constants import ROBOTECHY_LOGO_PATH, SCREEN_HEIGHT, SCREEN_WIDTH
from ..themes import get_current_theme


class SplashScreen(QWidget):
    """
    Splash screen displayed during application startup.

    Shows:
    - Robotechy R logo (centered)
    - Application name
    - Loading status text
    - Progress indication

    Emits `finished` signal when splash duration completes.
    """

    # Signal emitted when splash is complete
    finished = pyqtSignal()

    def __init__(self, duration_ms: int = 2500, parent: Optional[QWidget] = None):
        """
        Initialize splash screen.

        Args:
            duration_ms: How long to display splash (milliseconds).
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._duration = duration_ms
        self._theme = get_current_theme()
        self._status_text = "Initializing..."
        self._logo_pixmap: Optional[QPixmap] = None

        # Timer for auto-close
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_fade_out)

        # Set up window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Opacity effect for fade transitions
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Fade animations
        self._fade_in_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in_anim.setDuration(400)
        self._fade_in_anim.setStartValue(0.0)
        self._fade_in_anim.setEndValue(1.0)
        self._fade_in_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._fade_out_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out_anim.setDuration(500)
        self._fade_out_anim.setStartValue(1.0)
        self._fade_out_anim.setEndValue(0.0)
        self._fade_out_anim.setEasingCurve(QEasingCurve.InCubic)
        self._fade_out_anim.finished.connect(self._on_fade_out_complete)

        # Load logo
        self._load_logo()

    def _load_logo(self) -> None:
        """Load the Robotechy logo."""
        logo_path = ROBOTECHY_LOGO_PATH

        if logo_path.exists():
            self._logo_pixmap = QPixmap(str(logo_path))
            # Scale to appropriate size (about 1/3 of screen height)
            target_height = SCREEN_HEIGHT * 0.5
            self._logo_pixmap = self._logo_pixmap.scaledToHeight(
                int(target_height), Qt.SmoothTransformation
            )
        else:
            # Create placeholder if logo not found
            self._logo_pixmap = None

    def set_status(self, text: str) -> None:
        """
        Update the status text.

        Args:
            text: Status message to display.
        """
        self._status_text = text
        self.update()

    def start(self) -> None:
        """Start the splash screen with fade in."""
        self.show()
        self._fade_in_anim.start()
        self._timer.start(self._duration)

    def _start_fade_out(self) -> None:
        """Begin fade out transition."""
        self._fade_out_anim.start()

    def _on_fade_out_complete(self) -> None:
        """Handle completion of fade out."""
        self.finished.emit()

    def skip(self) -> None:
        """Skip the splash screen with quick fade."""
        self._timer.stop()
        # Quick fade out
        self._fade_out_anim.setDuration(200)
        self._fade_out_anim.start()

    def paintEvent(self, event) -> None:
        """Paint the splash screen - just the Robotechy R logo centered."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = self.rect()

        # Draw background
        painter.fillRect(rect, QColor(self._theme.BACKGROUND))

        center_x = rect.center().x()
        center_y = rect.center().y()

        # Draw logo only - centered
        if self._logo_pixmap:
            logo_x = center_x - self._logo_pixmap.width() // 2
            logo_y = center_y - self._logo_pixmap.height() // 2
            painter.drawPixmap(logo_x, logo_y, self._logo_pixmap)
        else:
            # Draw placeholder "R" if no logo
            self._draw_placeholder_logo(painter, center_x, center_y)

        painter.end()

    def _draw_placeholder_logo(
        self, painter: QPainter, center_x: int, center_y: int
    ) -> None:
        """Draw a placeholder R with shadow if logo file not found."""
        # Try to use custom font if available
        app = QApplication.instance()
        custom_font = app.property("custom_font") if app else None
        font_name = custom_font if custom_font else "Roboto"

        # Large stylized R
        font = QFont(font_name, 180)
        font.setBold(True)
        painter.setFont(font)

        text_rect = self.rect()
        text_rect.moveCenter(self.rect().center())
        text_rect.moveTop(center_y - 120)

        # Draw white shadow (offset slightly)
        shadow_rect = text_rect.translated(4, 4)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(shadow_rect, Qt.AlignHCenter | Qt.AlignTop, "R")

        # Draw green R on top
        painter.setPen(QColor(self._theme.ROBOTECHY_GREEN))
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, "R")

    def keyPressEvent(self, event) -> None:
        """
        Handle key press to skip splash (development only).

        Note: In vehicle operation there is no keyboard.
        Splash auto-completes after duration.
        """
        if event.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Escape):
            self.skip()

    # Note: Touch/mouse skip disabled for vehicle use
    # The splash provides time for CAN initialization
