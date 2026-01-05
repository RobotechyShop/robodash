"""
Base layout class for dashboard screens.

Provides common functionality for all dashboard layouts including:
- Data binding to VehicleState
- Widget management
- Theme integration
"""

from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.sip import wrappertype

from ..data.models import VehicleState
from ..themes import get_current_theme


# Combined metaclass to resolve QWidget + ABC conflict
class QWidgetABCMeta(wrappertype, ABCMeta):
    """Metaclass combining PyQt5's wrappertype with ABCMeta."""
    pass


class BaseLayout(QWidget, metaclass=QWidgetABCMeta):
    """
    Abstract base class for dashboard layouts.

    Subclasses must implement:
    - _setup_ui(): Create and arrange widgets
    - update_from_state(): Update widgets from VehicleState
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize base layout.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._theme = get_current_theme()
        self._widgets: Dict[str, QWidget] = {}
        self._last_state: Optional[VehicleState] = None

        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)

        # Call subclass setup
        self._setup_ui()

    @abstractmethod
    def _setup_ui(self) -> None:
        """
        Set up the layout UI.

        Subclasses must implement this to create and arrange widgets.
        """
        pass

    @abstractmethod
    def update_from_state(self, state: VehicleState) -> None:
        """
        Update all widgets from a vehicle state.

        Args:
            state: Current vehicle telemetry state.
        """
        pass

    def register_widget(self, name: str, widget: QWidget) -> None:
        """
        Register a widget for easy access.

        Args:
            name: Widget identifier.
            widget: Widget instance.
        """
        self._widgets[name] = widget

    def get_widget(self, name: str) -> Optional[QWidget]:
        """
        Get a registered widget by name.

        Args:
            name: Widget identifier.

        Returns:
            Widget instance or None if not found.
        """
        return self._widgets.get(name)

    @property
    def theme(self):
        """Get current theme."""
        return self._theme

    def refresh_theme(self) -> None:
        """Refresh theme for all widgets."""
        self._theme = get_current_theme()
        for widget in self._widgets.values():
            if hasattr(widget, 'refresh_theme'):
                widget.refresh_theme()

    def show_connection_warning(self) -> None:
        """Show a visual indication that connection is lost."""
        # Override in subclass for specific behavior
        pass

    def hide_connection_warning(self) -> None:
        """Hide connection warning."""
        # Override in subclass
        pass

    @property
    def layout_name(self) -> str:
        """Get layout identifier name."""
        return self.__class__.__name__.lower().replace("layout", "")
