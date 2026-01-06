"""
Real CAN bus data source for ECUMaster EMU Black.

This module handles communication with the vehicle's ECU via CAN bus
using the python-can library and MCP2515 controller.

Hardware setup:
- MCP2515 CAN controller connected via SPI
- CAN bus at 500 kbps
- EMU Black streaming at base ID 0x600

Reference: https://python-can.readthedocs.io/
"""

import logging
import threading
from typing import Optional

from PyQt5.QtCore import QObject, QTimer

from .base import DataSource
from .emu_protocol import EMUProtocolDecoder

logger = logging.getLogger(__name__)

# Try to import python-can, handle gracefully if not available
try:
    import can

    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False
    logger.warning("python-can not installed. CAN data source unavailable.")


class CANDataSource(DataSource):
    """
    CAN bus data source for ECUMaster EMU Black.

    Connects to a SocketCAN interface (e.g., can0) and decodes
    the EMU Black CAN stream into VehicleState updates.

    Usage:
        source = CANDataSource(channel='can0', base_id=0x600)
        source.data_updated.connect(on_data)
        source.start()
    """

    def __init__(
        self,
        parent: Optional[QObject] = None,
        channel: str = "can0",
        bitrate: int = 500000,
        base_id: int = 0x600,
        timeout_ms: int = 1000,
    ):
        """
        Initialize CAN data source.

        Args:
            parent: Optional parent QObject.
            channel: CAN interface name (default 'can0').
            bitrate: CAN bus bitrate (default 500000).
            base_id: EMU Black CAN stream base ID (default 0x600).
            timeout_ms: Connection timeout in milliseconds.
        """
        super().__init__(parent)

        if not CAN_AVAILABLE:
            raise RuntimeError(
                "python-can library not installed. "
                "Install with: pip install python-can"
            )

        self._channel = channel
        self._bitrate = bitrate
        self._base_id = base_id
        self._timeout_ms = timeout_ms

        self._bus: Optional["can.Bus"] = None
        self._decoder = EMUProtocolDecoder(base_id)
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Timeout checker
        self._timeout_timer = QTimer(self)
        self._timeout_timer.timeout.connect(self._check_timeout)

        logger.info(
            f"CANDataSource initialized: channel={channel}, "
            f"bitrate={bitrate}, base_id={base_id:#x}"
        )

    def start(self) -> None:
        """
        Begin CAN data acquisition.

        Initializes the CAN interface and starts a background thread
        to read messages.
        """
        if self._running:
            logger.warning("CANDataSource already running")
            return

        try:
            # Initialize CAN bus
            self._bus = can.interface.Bus(
                interface="socketcan",
                channel=self._channel,
                bitrate=self._bitrate,
            )

            self._running = True
            self._decoder.reset()

            # Start reader thread
            self._thread = threading.Thread(
                target=self._read_loop, daemon=True, name="CAN-Reader"
            )
            self._thread.start()

            # Start timeout checker
            self._timeout_timer.start(100)  # Check every 100ms

            self._set_connected(True)
            logger.info(f"CANDataSource started on {self._channel}")

        except can.CanError as e:
            error_msg = f"Failed to initialize CAN bus: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self._set_connected(False)

    def stop(self) -> None:
        """Stop CAN data acquisition and cleanup."""
        logger.info("CANDataSource stopping")

        self._running = False
        self._timeout_timer.stop()

        # Wait for reader thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        # Close CAN bus
        if self._bus:
            try:
                self._bus.shutdown()
            except Exception as e:
                logger.warning(f"Error shutting down CAN bus: {e}")
            self._bus = None

        self._set_connected(False)
        logger.info("CANDataSource stopped")

    def is_connected(self) -> bool:
        """Check if CAN bus is active and receiving data."""
        return self._running and self._decoder.is_receiving

    def _read_loop(self) -> None:
        """
        Background thread loop for reading CAN messages.

        Runs continuously until stop() is called.
        """
        logger.debug("CAN reader thread started")

        while self._running and self._bus:
            try:
                # Read with timeout to allow clean shutdown
                msg = self._bus.recv(timeout=0.1)

                if msg is None:
                    continue

                # Process message through decoder
                state = self._decoder.process_message(
                    msg.arbitration_id, bytes(msg.data)
                )

                if state:
                    # Full state received, emit from main thread
                    self._emit_state(state)

            except can.CanError as e:
                if self._running:
                    logger.error(f"CAN read error: {e}")
                    self.error_occurred.emit(str(e))

            except Exception as e:
                if self._running:
                    logger.exception(f"Unexpected error in CAN reader: {e}")

        logger.debug("CAN reader thread exiting")

    def _check_timeout(self) -> None:
        """Check for CAN communication timeout."""
        if not self._decoder.is_receiving and self._connected:
            logger.warning("CAN communication timeout")
            self._set_connected(False)
        elif self._decoder.is_receiving and not self._connected:
            self._set_connected(True)

    @property
    def channel(self) -> str:
        """Get CAN channel name."""
        return self._channel

    @property
    def base_id(self) -> int:
        """Get EMU Black base CAN ID."""
        return self._base_id


def is_can_available() -> bool:
    """Check if CAN bus support is available."""
    return CAN_AVAILABLE


def get_available_interfaces() -> list:
    """
    Get list of available CAN interfaces.

    Returns:
        List of interface names (e.g., ['can0', 'can1']).
    """
    if not CAN_AVAILABLE:
        return []

    interfaces = []

    try:
        # Check for socketcan interfaces on Linux
        import os

        if os.path.exists("/sys/class/net"):
            for iface in os.listdir("/sys/class/net"):
                if iface.startswith("can") or iface.startswith("vcan"):
                    interfaces.append(iface)
    except Exception as e:
        logger.warning(f"Error detecting CAN interfaces: {e}")

    return sorted(interfaces)
