"""Tests for EMU Black protocol decoder."""

import struct
import pytest

from src.data.emu_protocol import EMUProtocolDecoder
from src.data.models import VehicleState


class TestEMUProtocolDecoder:
    """Tests for EMUProtocolDecoder."""

    def test_initialization(self):
        """Decoder should initialize with default base ID."""
        decoder = EMUProtocolDecoder()
        assert decoder.base_id == 0x600

    def test_custom_base_id(self):
        """Decoder should accept custom base ID."""
        decoder = EMUProtocolDecoder(base_id=0x700)
        assert decoder.base_id == 0x700

    def test_ignores_unrelated_messages(self):
        """Should ignore CAN messages outside EMU range."""
        decoder = EMUProtocolDecoder(base_id=0x600)

        # Message outside range
        result = decoder.process_message(0x100, b"\x00" * 8)
        assert result is None

        result = decoder.process_message(0x700, b"\x00" * 8)
        assert result is None

    def test_accepts_valid_frame(self):
        """Should accept messages in valid range."""
        decoder = EMUProtocolDecoder(base_id=0x600)

        # Valid frame 0
        result = decoder.process_message(0x600, b"\x00" * 8)
        # Won't return state until all 8 frames received
        assert result is None

    def test_rejects_invalid_dlc(self):
        """Should reject messages with wrong data length."""
        decoder = EMUProtocolDecoder()

        # Too short
        result = decoder.process_message(0x600, b"\x00" * 4)
        assert result is None

    def test_full_frame_set_returns_state(self):
        """Complete set of 8 frames should return VehicleState."""
        decoder = EMUProtocolDecoder(base_id=0x600)

        # Send all 8 frames
        for i in range(8):
            result = decoder.process_message(0x600 + i, b"\x00" * 8)

        # Last frame should trigger state return
        assert isinstance(result, VehicleState)

    def test_frame_0_decoding(self):
        """Frame 0 should decode RPM, TPS, IAT, MAP correctly."""
        decoder = EMUProtocolDecoder()

        # RPM=3000, TPS=50%, IAT=25C, MAP=150kPa
        frame0 = struct.pack("<HBbHH", 3000, 100, 25, 1500, 0)

        # Send frame 0
        decoder.process_message(0x600, frame0)

        assert decoder._state.rpm == 3000
        assert decoder._state.tps == 50.0  # 100 * 0.5
        assert decoder._state.intake_temp == 25
        assert decoder._state.map_kpa == 150.0  # 1500 * 0.1

    def test_frame_2_decoding(self):
        """Frame 2 should decode speed, gear, ignition, battery."""
        decoder = EMUProtocolDecoder()

        # Speed=1200 (120km/h), Gear=4, Ign=28, Batt=138 (13.8V)
        frame2 = struct.pack("<HbbBxxx", 1200, 4, 28, 138)

        decoder.process_message(0x602, frame2)

        assert decoder._state.speed == 120.0  # 1200 * 0.1
        assert decoder._state.gear == 4
        assert decoder._state.ignition_angle == 28
        assert decoder._state.battery_voltage == 13.8

    def test_boost_calculation(self):
        """Boost should be calculated from MAP."""
        decoder = EMUProtocolDecoder()

        # MAP = 200 kPa = approx 1 bar boost
        frame0 = struct.pack("<HBbHH", 3000, 100, 25, 2000, 0)
        decoder.process_message(0x600, frame0)

        # boost = (MAP - 101.3) / 100
        expected_boost = (200.0 - 101.3) / 100.0
        assert abs(decoder._state.boost_pressure - expected_boost) < 0.01

    def test_reset(self):
        """Reset should clear accumulated frame data."""
        decoder = EMUProtocolDecoder()

        # Send some frames
        decoder.process_message(0x600, b"\x00" * 8)
        decoder.process_message(0x601, b"\x00" * 8)

        decoder.reset()

        # Internal frame data should be cleared
        assert len(decoder._frame_data) == 0


class TestEMUProtocolDecoderTiming:
    """Tests for timing-related functionality."""

    def test_is_receiving_false_initially(self):
        """is_receiving should be False before data received."""
        decoder = EMUProtocolDecoder()
        assert not decoder.is_receiving

    def test_is_receiving_true_after_complete_set(self):
        """is_receiving should be True after complete frame set."""
        decoder = EMUProtocolDecoder()

        # Send complete set
        for i in range(8):
            decoder.process_message(0x600 + i, b"\x00" * 8)

        assert decoder.is_receiving
