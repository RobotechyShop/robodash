"""Tests for race layout."""

import pytest

from src.data.models import VehicleState
from src.layouts.race_layout import RaceLayout


class TestRaceLayout:
    """Tests for RaceLayout."""

    def test_initialization(self, qtbot):
        """Layout should initialize without errors."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        assert layout is not None

    def test_has_required_widgets(self, qtbot):
        """Layout should have all required widgets registered."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        # Core widgets
        assert layout.get_widget("gear") is not None
        assert layout.get_widget("rpm_display") is not None
        assert layout.get_widget("rpm_bar") is not None
        assert layout.get_widget("speed") is not None
        assert layout.get_widget("shift_light") is not None

        # Metric boxes
        assert layout.get_widget("boost") is not None
        assert layout.get_widget("oil_pressure") is not None
        assert layout.get_widget("oil_temp") is not None
        assert layout.get_widget("coolant_temp") is not None
        assert layout.get_widget("afr") is not None
        assert layout.get_widget("battery") is not None

        # Warnings
        assert layout.get_widget("warn_oil") is not None
        assert layout.get_widget("warn_temp") is not None

    def test_update_from_state(self, qtbot, sample_vehicle_state):
        """Layout should update from VehicleState."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        # Should not raise
        layout.update_from_state(sample_vehicle_state)

        # Check some values propagated
        gear_widget = layout.get_widget("gear")
        assert gear_widget.gear == sample_vehicle_state.gear

    def test_warning_indicators(self, qtbot, warning_vehicle_state):
        """Warning indicators should activate on warning conditions."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        layout.update_from_state(warning_vehicle_state)

        # Oil pressure warning should be active (0.8 bar is low)
        warn_oil = layout.get_widget("warn_oil")
        assert warn_oil.active

        # Temp warning should be active (112°C coolant is high)
        warn_temp = layout.get_widget("warn_temp")
        assert warn_temp.active

    def test_connection_warning(self, qtbot):
        """Connection warning should show/hide."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        layout.show_connection_warning()
        status = layout.get_widget("status")
        assert "Disconnected" in status.text()

        layout.hide_connection_warning()
        assert "Connected" in status.text()

    def test_correct_dimensions(self, qtbot):
        """Layout should have correct dimensions for screen."""
        from src.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH

        layout = RaceLayout()
        qtbot.addWidget(layout)

        assert layout.width() == SCREEN_WIDTH
        assert layout.height() == SCREEN_HEIGHT

    @pytest.mark.screenshot
    def test_layout_screenshot_normal(
        self, qtbot, sample_vehicle_state, capture_screenshot
    ):
        """Capture screenshot of layout in normal state."""
        layout = RaceLayout()
        layout.resize(1920, 360)
        qtbot.addWidget(layout)
        layout.show()

        layout.update_from_state(sample_vehicle_state)
        qtbot.wait(100)  # Allow paint

        path = capture_screenshot(layout, "race_layout_normal")
        assert path.exists()

    @pytest.mark.screenshot
    def test_layout_screenshot_warning(
        self, qtbot, warning_vehicle_state, capture_screenshot
    ):
        """Capture screenshot with warning conditions."""
        layout = RaceLayout()
        layout.resize(1920, 360)
        qtbot.addWidget(layout)
        layout.show()

        layout.update_from_state(warning_vehicle_state)
        qtbot.wait(100)

        path = capture_screenshot(layout, "race_layout_warnings")
        assert path.exists()

    @pytest.mark.screenshot
    def test_layout_screenshot_redline(self, qtbot, capture_screenshot):
        """Capture screenshot at redline RPM."""
        layout = RaceLayout()
        layout.resize(1920, 360)
        qtbot.addWidget(layout)
        layout.show()

        state = VehicleState(
            rpm=7200,
            speed=250.0,
            gear=6,
            boost_pressure=1.8,
            coolant_temp=92,
            oil_temp=105,
            oil_pressure=5.0,
            afr=11.2,
            battery_voltage=14.0,
        )
        layout.update_from_state(state)
        qtbot.wait(100)

        path = capture_screenshot(layout, "race_layout_redline")
        assert path.exists()

    def test_cleanup(self, qtbot):
        """Cleanup should stop all timers."""
        layout = RaceLayout()
        qtbot.addWidget(layout)

        # Should not raise
        layout.cleanup()
