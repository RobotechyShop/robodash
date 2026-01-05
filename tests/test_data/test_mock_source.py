"""Tests for mock data source."""

import pytest
from PyQt5.QtCore import QSignalSpy

from src.data.mock_source import MockDataSource
from src.data.models import VehicleState


class TestMockDataSource:
    """Tests for MockDataSource."""

    def test_initialization(self):
        """MockDataSource should initialize without errors."""
        source = MockDataSource(update_rate_hz=30)
        assert source is not None
        assert not source.is_connected()

    def test_start_stop(self, qtbot):
        """Source should start and stop correctly."""
        source = MockDataSource(update_rate_hz=30)

        source.start()
        assert source.is_connected()

        source.stop()
        assert not source.is_connected()

    def test_emits_data(self, qtbot):
        """Source should emit data_updated signal with VehicleState."""
        source = MockDataSource(update_rate_hz=30)

        with qtbot.waitSignal(source.data_updated, timeout=500) as blocker:
            source.start()

        # Check we received a VehicleState
        assert len(blocker.args) == 1
        state = blocker.args[0]
        assert isinstance(state, VehicleState)

        source.stop()

    def test_data_has_reasonable_values(self, qtbot):
        """Emitted data should have reasonable values."""
        source = MockDataSource(update_rate_hz=30)

        with qtbot.waitSignal(source.data_updated, timeout=500) as blocker:
            source.start()

        state = blocker.args[0]

        # Check ranges
        assert 0 <= state.rpm <= 8000
        assert 0 <= state.speed <= 400  # km/h
        assert 0 <= state.gear <= 6
        assert -1.0 <= state.boost_pressure <= 3.0
        assert 0 <= state.coolant_temp <= 150
        assert 10 <= state.battery_voltage <= 16

        source.stop()

    def test_gear_changes(self, qtbot):
        """Simulation should produce gear changes."""
        source = MockDataSource(update_rate_hz=60)

        gears_seen = set()

        def on_data(state):
            gears_seen.add(state.gear)

        source.data_updated.connect(on_data)
        source.start()

        # Wait for some data
        qtbot.wait(2000)

        source.stop()

        # Should see multiple gears in 2 seconds of simulation
        assert len(gears_seen) >= 2

    def test_manual_gear_set(self):
        """Manual gear setting should work."""
        source = MockDataSource()

        source.set_gear(4)
        assert source._gear == 4

        source.set_gear(0)  # Neutral
        assert source._gear == 0

    def test_manual_rpm_set(self):
        """Manual RPM setting should work."""
        source = MockDataSource()

        source.set_rpm(5000)
        assert source._rpm == 5000

        # Should clamp to limits
        source.set_rpm(10000)
        assert source._rpm <= 7500  # REV_LIMIT


class TestMockDataSourceConnection:
    """Test connection status behavior."""

    def test_connection_signal_on_start(self, qtbot):
        """Should emit connection_changed(True) on start."""
        source = MockDataSource()

        with qtbot.waitSignal(source.connection_changed, timeout=500) as blocker:
            source.start()

        assert blocker.args[0] is True
        source.stop()

    def test_connection_signal_on_stop(self, qtbot):
        """Should emit connection_changed(False) on stop."""
        source = MockDataSource()
        source.start()

        with qtbot.waitSignal(source.connection_changed, timeout=500) as blocker:
            source.stop()

        assert blocker.args[0] is False
