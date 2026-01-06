"""
Application lifecycle management for RoboDash.

Handles:
- QApplication setup and configuration
- Window management
- Data source initialization
- Splash screen coordination
"""

import logging
import sys
from typing import Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFontDatabase, QIcon, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from ..data import CANDataSource, DataSource, MockDataSource
from ..data.can_source import is_can_available
from ..layouts import RaceLayout, SplashScreen
from ..themes import get_theme_manager
from ..utils import ValueSmoother
from .config import Config
from .constants import FONTS_DIR, ROBOTECHY_LOGO_PATH, SCREEN_HEIGHT, SCREEN_WIDTH

logger = logging.getLogger(__name__)


def load_custom_fonts() -> str:
    """
    Load custom fonts from assets/fonts directory.

    Returns:
        Name of loaded custom font, or "Roboto" as fallback.
    """
    # Try to load Japanese Robot font
    japanese_robot = FONTS_DIR / "Japanese Robot.ttf"
    if japanese_robot.exists():
        font_id = QFontDatabase.addApplicationFont(str(japanese_robot))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                logger.info(f"Loaded custom font: {families[0]}")
                return families[0]

    # Try alternative name
    japanese_robot_alt = FONTS_DIR / "JapaneseRobot.ttf"
    if japanese_robot_alt.exists():
        font_id = QFontDatabase.addApplicationFont(str(japanese_robot_alt))
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                logger.info(f"Loaded custom font: {families[0]}")
                return families[0]

    logger.info("Using default Roboto font")
    return "Roboto"


class DashboardWindow(QMainWindow):
    """
    Main dashboard window.

    Manages the central layout widget and handles data updates
    from the configured data source.
    """

    def __init__(
        self, config: Config, data_source: DataSource, parent: Optional[QWidget] = None
    ):
        """
        Initialize dashboard window.

        Args:
            config: Application configuration.
            data_source: Data source for vehicle telemetry.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self.config = config
        self.data_source = data_source
        self.smoother = ValueSmoother()

        # Window setup
        self.setWindowTitle("RoboDash")
        self.setFixedSize(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set window icon (for taskbar)
        if ROBOTECHY_LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(ROBOTECHY_LOGO_PATH)))

        if config.display.frameless:
            self.setWindowFlags(Qt.FramelessWindowHint)

        # Set solid black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(10, 10, 10))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)
        self.setStyleSheet("background-color: #0A0A0A;")

        # Create layout
        self.layout = RaceLayout(self)
        self.setCentralWidget(self.layout)

        # Connect data source
        self.data_source.data_updated.connect(self._on_data_updated)
        self.data_source.connection_changed.connect(self._on_connection_changed)

        logger.info("DashboardWindow initialized")

    def _on_data_updated(self, state) -> None:
        """
        Handle incoming vehicle state updates.

        Args:
            state: New VehicleState from data source.
        """
        # Apply smoothing
        smoothed = self.smoother.smooth_state(state)

        # Update layout
        self.layout.update_from_state(smoothed)

    def _on_connection_changed(self, connected: bool) -> None:
        """
        Handle connection status changes.

        Args:
            connected: New connection status.
        """
        if connected:
            self.layout.hide_connection_warning()
            logger.info("Data source connected")
        else:
            self.layout.show_connection_warning()
            logger.warning("Data source disconnected")

    def start_data(self) -> None:
        """Start data acquisition."""
        self.data_source.start()

    def stop_data(self) -> None:
        """Stop data acquisition."""
        self.data_source.stop()

    def closeEvent(self, event) -> None:
        """Handle window close."""
        logger.info("Closing dashboard window")
        self.stop_data()
        self.layout.cleanup()
        event.accept()

    def keyPressEvent(self, event) -> None:
        """
        Handle key presses (development only).

        Note: In vehicle operation there is no keyboard.
        These shortcuts are for development/testing only.
        """
        # Development shortcuts only
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        else:
            super().keyPressEvent(event)


class DashboardApp:
    """
    Main application controller.

    Coordinates splash screen, window creation, and data source
    initialization.
    """

    def __init__(
        self, config: Config, use_mock: bool = False, enable_sound: bool = False
    ):
        """
        Initialize application.

        Args:
            config: Application configuration.
            use_mock: Force use of mock data source.
            enable_sound: Enable synthesized engine sound (mock mode only).
        """
        self.config = config
        self.use_mock = use_mock
        self.enable_sound = enable_sound

        self.app: Optional[QApplication] = None
        self.splash: Optional[SplashScreen] = None
        self.window: Optional[DashboardWindow] = None
        self.data_source: Optional[DataSource] = None

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code.
        """
        # Create QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("RoboDash")
        self.app.setApplicationVersion(self.config.app_version)

        # Load custom fonts
        custom_font = load_custom_fonts()
        self.app.setProperty("custom_font", custom_font)

        # Set application icon (for taskbar/dock)
        if ROBOTECHY_LOGO_PATH.exists():
            self.app.setWindowIcon(QIcon(str(ROBOTECHY_LOGO_PATH)))

        # Apply theme
        theme_manager = get_theme_manager()
        theme_manager.apply_to_application(self.app)

        # Show splash screen
        self.splash = SplashScreen(self.config.splash_duration_ms)
        self.splash.finished.connect(self._on_splash_finished)
        self.splash.set_status("Initializing...")

        # Initialize data source during splash
        QTimer.singleShot(100, self._init_data_source)

        # Start splash
        self.splash.start()

        # Run event loop
        return self.app.exec_()

    def _init_data_source(self) -> None:
        """Initialize the data source."""
        self.splash.set_status("Connecting to ECU...")

        if self.use_mock:
            logger.info("Using mock data source (forced)")
            self.data_source = MockDataSource(
                update_rate_hz=self.config.update_rate_hz,
                enable_sound=self.enable_sound,
            )
            if self.enable_sound:
                self.splash.set_status("Simulation mode (with sound)")
        elif self.config.can.enabled and is_can_available():
            try:
                logger.info("Attempting CAN connection...")
                self.data_source = CANDataSource(
                    channel=self.config.can.channel,
                    bitrate=self.config.can.bitrate,
                    base_id=self.config.can.base_id,
                )
                self.splash.set_status("CAN bus connected")
            except Exception as e:
                logger.warning(f"CAN init failed: {e}, falling back to mock")
                self.splash.set_status("Using simulation mode")
                self.data_source = MockDataSource(
                    update_rate_hz=self.config.update_rate_hz,
                    enable_sound=self.enable_sound,
                )
        else:
            logger.info("CAN not available, using mock data source")
            self.splash.set_status("Simulation mode")
            self.data_source = MockDataSource(
                update_rate_hz=self.config.update_rate_hz,
                enable_sound=self.enable_sound,
            )

    def _on_splash_finished(self) -> None:
        """Handle splash screen completion."""
        logger.info("Splash finished, showing main window")

        # Hide splash
        self.splash.hide()

        # Create main window
        self.window = DashboardWindow(self.config, self.data_source)

        # Position on second display if available (HDMI at x=1920)
        screens = self.app.screens()
        if len(screens) > 1:
            # Find the non-primary screen (likely HDMI)
            for screen in screens:
                if screen != self.app.primaryScreen():
                    self.window.move(screen.geometry().topLeft())
                    logger.info(f"Moved window to screen: {screen.name()}")
                    break

        # Show window
        if self.config.display.fullscreen:
            self.window.showFullScreen()
        else:
            self.window.show()

        # Start data acquisition
        self.window.start_data()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.window:
            self.window.close()
        if self.data_source:
            self.data_source.stop()
