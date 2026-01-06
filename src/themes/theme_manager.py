"""
Theme management for RoboDash.

Handles loading, applying, and switching between themes.
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

from .robotechy_dark import DEFAULT_THEME, RobotechyDarkTheme

logger = logging.getLogger(__name__)


# Type alias for theme classes
Theme = RobotechyDarkTheme


@dataclass
class ThemeManager:
    """
    Manages application theming.

    Handles:
    - Theme registration and selection
    - Stylesheet application
    - Font loading
    - Runtime theme switching
    """

    def __init__(self):
        """Initialize theme manager."""
        self._themes: Dict[str, Theme] = {
            "robotechy_dark": DEFAULT_THEME,
        }
        self._current_theme_name: str = "robotechy_dark"
        self._current_theme: Theme = DEFAULT_THEME
        self._fonts_loaded: bool = False

    @property
    def current_theme(self) -> Theme:
        """Get the currently active theme."""
        return self._current_theme

    @property
    def current_theme_name(self) -> str:
        """Get the name of the current theme."""
        return self._current_theme_name

    def register_theme(self, name: str, theme: Theme) -> None:
        """
        Register a new theme.

        Args:
            name: Unique theme identifier.
            theme: Theme instance.
        """
        self._themes[name] = theme
        logger.info(f"Registered theme: {name}")

    def set_theme(self, name: str) -> bool:
        """
        Switch to a different theme.

        Args:
            name: Name of theme to activate.

        Returns:
            True if theme was changed, False if theme not found.
        """
        if name not in self._themes:
            logger.warning(f"Theme not found: {name}")
            return False

        self._current_theme = self._themes[name]
        self._current_theme_name = name
        logger.info(f"Theme changed to: {name}")

        # Apply to application if available
        app = QApplication.instance()
        if app:
            self.apply_to_application(app)

        return True

    def apply_to_application(self, app: QApplication) -> None:
        """
        Apply current theme to a QApplication.

        Args:
            app: QApplication instance.
        """
        # Load fonts first
        if not self._fonts_loaded:
            self._load_fonts()

        # Apply stylesheet
        stylesheet = self._current_theme.to_stylesheet()
        app.setStyleSheet(stylesheet)

        # Set default font
        font = QFont("Roboto", 12)
        font.setStyleHint(QFont.SansSerif)
        app.setFont(font)

        logger.info(f"Applied theme to application: {self._current_theme_name}")

    def _load_fonts(self) -> None:
        """Load custom fonts for the application."""
        from ..core.constants import FONTS_DIR

        # Try to load Roboto font if available
        roboto_path = FONTS_DIR / "Roboto-Regular.ttf"

        if roboto_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(roboto_path))
            if font_id >= 0:
                logger.info("Loaded font: Roboto")
            else:
                logger.warning(f"Failed to load font: {roboto_path}")

        # Also try bold variant
        roboto_bold_path = FONTS_DIR / "Roboto-Bold.ttf"
        if roboto_bold_path.exists():
            QFontDatabase.addApplicationFont(str(roboto_bold_path))

        self._fonts_loaded = True

    def get_available_themes(self) -> list:
        """
        Get list of available theme names.

        Returns:
            List of theme names.
        """
        return list(self._themes.keys())

    # =========================================================================
    # Color Convenience Methods
    # =========================================================================

    def get_background_color(self) -> str:
        """Get current theme's background color."""
        return self._current_theme.BACKGROUND

    def get_accent_color(self) -> str:
        """Get current theme's accent color (Robotechy green)."""
        return self._current_theme.ROBOTECHY_GREEN

    def get_text_color(self, variant: str = "primary") -> str:
        """
        Get text color for specified variant.

        Args:
            variant: "primary", "secondary", "disabled", or "accent"
        """
        colors = {
            "primary": self._current_theme.TEXT_PRIMARY,
            "secondary": self._current_theme.TEXT_SECONDARY,
            "disabled": self._current_theme.TEXT_DISABLED,
            "accent": self._current_theme.TEXT_ACCENT,
        }
        return colors.get(variant, self._current_theme.TEXT_PRIMARY)

    def get_status_color(self, status: str) -> str:
        """
        Get color for status type.

        Args:
            status: "normal", "warning", "critical", or "info"
        """
        colors = {
            "normal": self._current_theme.NORMAL,
            "warning": self._current_theme.WARNING,
            "critical": self._current_theme.CRITICAL,
            "info": self._current_theme.INFO,
        }
        return colors.get(status, self._current_theme.NORMAL)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance.

    Creates the instance if it doesn't exist.

    Returns:
        ThemeManager singleton.
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_current_theme() -> Theme:
    """
    Get the currently active theme.

    Convenience function for quick theme access.

    Returns:
        Current Theme instance.
    """
    return get_theme_manager().current_theme
