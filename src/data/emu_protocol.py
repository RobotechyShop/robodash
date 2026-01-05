"""
ECUMaster EMU Black CAN protocol decoder.

This module decodes the CAN stream from ECUMaster EMU Black ECU.
The EMU Black sends 8 CAN frames (IDs BASE through BASE+7) containing
all engine telemetry data.

Reference: https://github.com/designer2k2/EMUcan
Protocol: EMU Black CAN Stream Format v2.154+

CAN Configuration:
- Bitrate: 500 kbps
- Base ID: 0x600 (configurable in ECU software)
- Frame count: 8 frames (0x600 - 0x607)
- DLC: 8 bytes per frame
"""

import struct
import logging
from typing import Optional, Dict, Any
import time

from .models import VehicleState, EngineFlags, WarningFlags

logger = logging.getLogger(__name__)


class EMUProtocolDecoder:
    """
    Decodes CAN messages from ECUMaster EMU Black.

    The decoder accumulates data from all 8 CAN frames and produces
    a complete VehicleState when a full set has been received.

    Usage:
        decoder = EMUProtocolDecoder(base_id=0x600)
        for msg in can_bus:
            state = decoder.process_message(msg.arbitration_id, msg.data)
            if state:
                # Full state available
                update_display(state)
    """

    # Frame offsets from base ID
    FRAME_COUNT = 8

    def __init__(self, base_id: int = 0x600):
        """
        Initialize the decoder.

        Args:
            base_id: CAN base ID for EMU stream (default 0x600).
        """
        self.base_id = base_id
        self._frame_data: Dict[int, bytes] = {}
        self._last_complete_time = 0.0
        self._state = VehicleState()

    def process_message(
        self,
        arbitration_id: int,
        data: bytes
    ) -> Optional[VehicleState]:
        """
        Process a CAN message and return VehicleState if complete.

        Args:
            arbitration_id: CAN message ID.
            data: CAN message data (8 bytes).

        Returns:
            VehicleState if a complete set of frames received, else None.
        """
        # Check if this message belongs to our EMU stream
        if not self._is_emu_frame(arbitration_id):
            return None

        if len(data) != 8:
            logger.warning(f"Invalid DLC {len(data)} for frame {arbitration_id:#x}")
            return None

        # Store frame data
        frame_index = arbitration_id - self.base_id
        self._frame_data[frame_index] = data

        # Decode this frame
        self._decode_frame(frame_index, data)

        # Check if we have all frames
        if len(self._frame_data) >= self.FRAME_COUNT:
            self._frame_data.clear()
            self._state.timestamp = time.time()
            self._last_complete_time = self._state.timestamp
            return self._state.copy()

        return None

    def _is_emu_frame(self, arbitration_id: int) -> bool:
        """Check if CAN ID belongs to EMU stream."""
        return self.base_id <= arbitration_id < self.base_id + self.FRAME_COUNT

    def _decode_frame(self, frame_index: int, data: bytes) -> None:
        """
        Decode a single CAN frame and update state.

        Frame layout based on EMUcan library and EMU Black documentation.
        """
        if frame_index == 0:
            self._decode_frame_0(data)
        elif frame_index == 1:
            self._decode_frame_1(data)
        elif frame_index == 2:
            self._decode_frame_2(data)
        elif frame_index == 3:
            self._decode_frame_3(data)
        elif frame_index == 4:
            self._decode_frame_4(data)
        elif frame_index == 5:
            self._decode_frame_5(data)
        elif frame_index == 6:
            self._decode_frame_6(data)
        elif frame_index == 7:
            self._decode_frame_7(data)

    def _decode_frame_0(self, data: bytes) -> None:
        """
        Frame 0: RPM, TPS, IAT, MAP

        Byte 0-1: RPM (uint16, little-endian)
        Byte 2: TPS (uint8, 0.5% per bit)
        Byte 3: IAT (int8, Celsius)
        Byte 4-5: MAP (uint16, 0.1 kPa per bit)
        Byte 6-7: Reserved
        """
        self._state.rpm = struct.unpack_from("<H", data, 0)[0]
        self._state.tps = data[2] * 0.5
        self._state.intake_temp = struct.unpack_from("<b", data, 3)[0]
        self._state.map_kpa = struct.unpack_from("<H", data, 4)[0] * 0.1

        # Calculate boost from MAP (relative to 101.3 kPa atmosphere)
        self._state.boost_pressure = (self._state.map_kpa - 101.3) / 100.0

    def _decode_frame_1(self, data: bytes) -> None:
        """
        Frame 1: Injector PW, Lambda target, Lambda, Fuel pressure

        Byte 0-1: Injector pulse width (uint16, 0.01ms per bit)
        Byte 2: Lambda target (uint8, value/100 + 0.5)
        Byte 3: Reserved
        Byte 4-5: Lambda (uint16, value/10000)
        Byte 6-7: Fuel pressure (uint16, 0.01 bar per bit)
        """
        inj_pw = struct.unpack_from("<H", data, 0)[0] * 0.01  # ms
        self._state.lambda_target = data[2] / 100.0 + 0.5
        self._state.lambda_value = struct.unpack_from("<H", data, 4)[0] / 10000.0
        self._state.fuel_pressure = struct.unpack_from("<H", data, 6)[0] * 0.01

        # Calculate AFR from lambda (stoich = 14.7)
        if self._state.lambda_value > 0:
            self._state.afr = self._state.lambda_value * 14.7

        # Calculate injector duty (assuming max 8333 Hz at 7500 RPM)
        if self._state.rpm > 0:
            cycle_time = 120000.0 / self._state.rpm  # ms per cycle (4-stroke)
            self._state.injector_duty = min(100.0, (inj_pw / cycle_time) * 100.0)

    def _decode_frame_2(self, data: bytes) -> None:
        """
        Frame 2: VSS (Vehicle Speed), Gear, Ignition angle

        Byte 0-1: Vehicle speed (uint16, 0.1 km/h per bit)
        Byte 2: Gear (int8, 0=N, -1=R, 1-6=forward)
        Byte 3: Ignition angle (int8, degrees BTDC, signed)
        Byte 4: Battery voltage (uint8, 0.1V per bit)
        Byte 5-7: Reserved
        """
        self._state.speed = struct.unpack_from("<H", data, 0)[0] * 0.1
        self._state.gear = struct.unpack_from("<b", data, 2)[0]
        self._state.ignition_angle = struct.unpack_from("<b", data, 3)[0]
        self._state.battery_voltage = data[4] * 0.1

    def _decode_frame_3(self, data: bytes) -> None:
        """
        Frame 3: Temperatures (CLT, Oil temp)

        Byte 0-1: Coolant temp (int16, 0.1°C per bit)
        Byte 2-3: Oil temp (int16, 0.1°C per bit)
        Byte 4-7: Reserved
        """
        self._state.coolant_temp = struct.unpack_from("<h", data, 0)[0] * 0.1
        self._state.oil_temp = struct.unpack_from("<h", data, 2)[0] * 0.1

    def _decode_frame_4(self, data: bytes) -> None:
        """
        Frame 4: Oil pressure, EGT1, EGT2

        Byte 0-1: Oil pressure (uint16, 0.01 bar per bit)
        Byte 2-3: EGT1 (uint16, Celsius)
        Byte 4-5: EGT2 (uint16, Celsius)
        Byte 6-7: Reserved
        """
        self._state.oil_pressure = struct.unpack_from("<H", data, 0)[0] * 0.01
        self._state.egt1 = struct.unpack_from("<H", data, 2)[0]
        self._state.egt2 = struct.unpack_from("<H", data, 4)[0]

    def _decode_frame_5(self, data: bytes) -> None:
        """
        Frame 5: Engine flags, Warning flags

        Byte 0: Engine flags (EngineFlags bitfield)
        Byte 1-2: Warning flags (WarningFlags bitfield)
        Byte 3-7: Reserved
        """
        self._state.flags = EngineFlags(data[0])
        self._state.warnings = WarningFlags(struct.unpack_from("<H", data, 1)[0])

    def _decode_frame_6(self, data: bytes) -> None:
        """
        Frame 6: Additional data (DBW, boost target, etc.)

        Byte 0: DBW position (uint8, 0.5% per bit)
        Byte 1: Boost target (uint8, 0.01 bar per bit, signed offset)
        Byte 2-7: Reserved/Custom
        """
        # DBW (Drive By Wire) position if equipped
        # dbw_position = data[0] * 0.5
        pass

    def _decode_frame_7(self, data: bytes) -> None:
        """
        Frame 7: Reserved/Custom data

        This frame is available for custom CAN messages configured
        in the EMU Black software.
        """
        pass

    def reset(self) -> None:
        """Reset decoder state, clearing accumulated frame data."""
        self._frame_data.clear()
        self._state = VehicleState()

    @property
    def time_since_last_complete(self) -> float:
        """Get seconds since last complete state was received."""
        if self._last_complete_time == 0:
            return float('inf')
        return time.time() - self._last_complete_time

    @property
    def is_receiving(self) -> bool:
        """Check if decoder is actively receiving data (within 1 second)."""
        return self.time_since_last_complete < 1.0
