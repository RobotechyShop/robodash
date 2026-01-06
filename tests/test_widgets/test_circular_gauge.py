"""Tests for circular gauge widget."""

import pytest

from src.widgets.circular_gauge import CircularGauge, Tachometer


class TestCircularGauge:
    """Tests for CircularGauge widget."""

    def test_initialization(self, qtbot):
        """Gauge should initialize with default values."""
        gauge = CircularGauge()
        qtbot.addWidget(gauge)

        assert gauge.value == 0.0
        assert gauge.min_value == 0.0
        assert gauge.max_value == 100.0

    def test_set_value(self, qtbot):
        """Value should be settable."""
        gauge = CircularGauge()
        qtbot.addWidget(gauge)

        gauge.value = 50.0
        assert gauge.value == 50.0

    def test_value_clamping(self, qtbot):
        """Values should be clamped to range."""
        gauge = CircularGauge()
        gauge.set_range(0, 100)
        qtbot.addWidget(gauge)

        gauge.value = 150
        assert gauge.value == 100

        gauge.value = -50
        assert gauge.value == 0

    def test_value_changed_signal(self, qtbot):
        """Signal should emit when value changes."""
        gauge = CircularGauge()
        qtbot.addWidget(gauge)

        with qtbot.waitSignal(gauge.value_changed, timeout=1000):
            gauge.value = 75

    def test_value_percent(self, qtbot):
        """value_percent should calculate correctly."""
        gauge = CircularGauge()
        gauge.set_range(0, 100)
        qtbot.addWidget(gauge)

        gauge.value = 50
        assert gauge.value_percent == 0.5

        gauge.value = 25
        assert gauge.value_percent == 0.25

    def test_add_zones(self, qtbot):
        """Zones should be addable."""
        gauge = CircularGauge()
        qtbot.addWidget(gauge)

        gauge.add_zone(0, 50, "#00FF00")
        gauge.add_zone(50, 75, "#FFFF00")
        gauge.add_zone(75, 100, "#FF0000")

        assert len(gauge._zones) == 3

    def test_clear_zones(self, qtbot):
        """Zones should be clearable."""
        gauge = CircularGauge()
        gauge.add_zone(0, 50, "#00FF00")
        qtbot.addWidget(gauge)

        gauge.clear_zones()
        assert len(gauge._zones) == 0

    def test_render_without_crash(self, qtbot):
        """Gauge should render without exceptions."""
        gauge = CircularGauge()
        gauge.set_range(0, 8000)
        gauge.value = 4000
        gauge.add_zone(0, 6000, "#00FF00")
        qtbot.addWidget(gauge)

        gauge.resize(200, 200)
        gauge.show()
        gauge.repaint()  # Force paint event

    @pytest.mark.screenshot
    def test_gauge_screenshot(self, qtbot, capture_screenshot):
        """Capture gauge screenshot for visual verification."""
        gauge = CircularGauge()
        gauge.set_range(0, 8000)
        gauge.add_zone(0, 6000, "#9EFF11")
        gauge.add_zone(6000, 7000, "#FFAA00")
        gauge.add_zone(7000, 8000, "#FF0000")
        gauge.value = 5500
        gauge.resize(200, 200)
        qtbot.addWidget(gauge)
        gauge.show()

        path = capture_screenshot(gauge, "circular_gauge_5500rpm")
        assert path.exists()


class TestTachometer:
    """Tests for Tachometer widget."""

    def test_initialization(self, qtbot):
        """Tachometer should have RPM-appropriate defaults."""
        tacho = Tachometer()
        qtbot.addWidget(tacho)

        assert tacho.min_value == 0
        assert tacho.max_value == 8000

    def test_has_default_zones(self, qtbot):
        """Tachometer should have default color zones."""
        tacho = Tachometer()
        qtbot.addWidget(tacho)

        assert len(tacho._zones) == 3

    def test_set_redline(self, qtbot):
        """set_redline should update zones."""
        tacho = Tachometer()
        qtbot.addWidget(tacho)

        tacho.set_redline(7500)

        # Should have reconfigured zones
        assert len(tacho._zones) == 3

    @pytest.mark.screenshot
    def test_tachometer_redline_screenshot(self, qtbot, capture_screenshot):
        """Capture tachometer at redline."""
        tacho = Tachometer()
        tacho.value = 7100
        tacho.resize(200, 200)
        qtbot.addWidget(tacho)
        tacho.show()

        path = capture_screenshot(tacho, "tachometer_redline")
        assert path.exists()
