"""
Abstract base class for data sources.

This defines the interface that all data sources (CAN, mock, etc.)
must implement, enabling hot-swapping between real and simulated data.
"""

from abc import ABCMeta, abstractmethod
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.sip import wrappertype

from .models import VehicleState


# Combined metaclass to resolve QObject + ABC conflict
class QObjectABCMeta(wrappertype, ABCMeta):
    """Metaclass combining PyQt5's wrappertype with ABCMeta."""
    pass


class DataSource(QObject, metaclass=QObjectABCMeta):
    """
    Abstract interface for vehicle data sources.

    Subclasses must implement start(), stop(), and is_connected().
    Data is emitted via the data_updated signal.

    Signals:
        data_updated: Emitted when new vehicle state is available.
        connection_changed: Emitted when connection status changes.
        error_occurred: Emitted when an error occurs.
    """

    # Signal emitted when new data is available
    data_updated = pyqtSignal(object)  # Emits VehicleState

    # Signal for connection status changes
    connection_changed = pyqtSignal(bool)

    # Signal for errors
    error_occurred = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize the data source.

        Args:
            parent: Optional parent QObject for memory management.
        """
        super().__init__(parent)
        self._connected = False
        self._last_state: Optional[VehicleState] = None

    @property
    def connected(self) -> bool:
        """Get current connection status."""
        return self._connected

    @property
    def last_state(self) -> Optional[VehicleState]:
        """Get the most recently received vehicle state."""
        return self._last_state

    @abstractmethod
    def start(self) -> None:
        """
        Begin data acquisition.

        This should initialize any hardware connections and start
        receiving data. Implementations should emit connection_changed(True)
        on successful start, or error_occurred on failure.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop data acquisition and cleanup resources.

        This should cleanly shut down any hardware connections and
        background threads. Emit connection_changed(False) when stopped.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if data source is actively receiving data.

        Returns:
            True if connected and receiving data, False otherwise.
        """
        pass

    def _emit_state(self, state: VehicleState) -> None:
        """
        Helper to emit a new vehicle state.

        This updates the internal state cache and emits the signal.

        Args:
            state: The new vehicle state to emit.
        """
        self._last_state = state
        self.data_updated.emit(state)

    def _set_connected(self, connected: bool) -> None:
        """
        Helper to update connection status.

        Args:
            connected: New connection status.
        """
        if connected != self._connected:
            self._connected = connected
            self.connection_changed.emit(connected)
