# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RoboDash is a PyQt5-based racing dashboard for a Toyota Supra Mk4 time attack car, designed as an NEA coursework project. The system integrates:
- **Hardware**: Raspberry Pi 4 + Corsair Xeneon Edge display (1920x360)
- **ECU**: ECUMaster EMU Black (CAN bus interface)
- **Enclosure**: 3D printed PETG-CF with carbon fiber accents
- **Purpose**: Real-time telemetry visualization (RPM, speed, boost, temperatures, warnings)
- **Compliance**: FIA time attack series regulations (Appendix J)

Reference implementation based on: https://github.com/valtsu23/DIY-Emu-Black-Dash

## Repository Structure

```
robodash/
├── src/                          # Application source code
│   ├── main.py                   # Entry point
│   ├── core/                     # App lifecycle, config, constants
│   ├── data/                     # Data sources (CAN, mock, protocol decoder)
│   ├── widgets/                  # UI components (gauges, displays)
│   ├── layouts/                  # Dashboard layouts (race, splash)
│   ├── themes/                   # Theming (Robotechy dark theme)
│   └── utils/                    # Utilities (unit conversion, smoothing)
├── tests/                        # pytest test suite
├── config/                       # YAML configuration files
├── assets/                       # Fonts, icons, images
├── scripts/                      # Setup and utility scripts
├── docs/                         # Documentation (AsciiDoc)
├── 3d-model/                     # 3D printable enclosure files
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── pyproject.toml                # Project metadata
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run with mock data (development)
python -m src.main --mock --windowed

# Run with mock data and engine sound
python -m src.main --mock --sound --windowed

# Run with real CAN data (on Pi)
python -m src.main

# Enable debug logging
python -m src.main --mock --debug
```

## Development Commands

```bash
# Run tests
make test
pytest tests/ -v

# Run tests headless (CI/server)
./scripts/run_tests_headless.sh

# Lint and format
make lint
make format

# Type checking
mypy src/
```

## Key Configuration

Configuration is in `config/default.yaml`:
- **Units**: mph/kmh, °C/°F, bar/psi (default: UK units)
- **CAN settings**: channel, bitrate, base ID
- **Gauge thresholds**: warning/critical levels for RPM, temps, pressures
- **Display**: resolution, fullscreen, update rate

## Architecture Notes

- **Data Flow**: ECU → MCP2515 CAN → python-can → DataSource → PyQt5 widgets
- **Threading**: CAN reception runs in background thread, signals to main thread
- **Updates**: 30 FPS default, smoothed with EMA filtering
- **Design**: Passive display only - no driver interaction while moving

## Theme Colors

- **Robotechy Green**: `#9EFF11` (primary accent)
- **Background**: `#0A0A0A`
- **Warning**: `#FFAA00` (amber)
- **Critical**: `#FF0000` (red)

## Useful Links

### Hardware Documentation
- [ECUMaster EMU Black Manual](https://www.ecumaster.com/files/Manuals/EMU-Black_manual.pdf)
- [MCP2515 CAN Controller Datasheet](https://www.microchip.com/en-us/product/MCP2515)
- [Raspberry Pi CAN Bus Setup Guide](https://forums.raspberrypi.com/viewtopic.php?t=141052)

### Software References
- [DIY-Emu-Black-Dash (Reference Implementation)](https://github.com/valtsu23/DIY-Emu-Black-Dash)
- [EMUcan Arduino Library (Protocol Reference)](https://github.com/designer2k2/EMUcan)
- [python-can Documentation](https://python-can.readthedocs.io/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython-5/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)

### Similar Projects
- [Phantom Dashboard (Kivy)](https://github.com/sfuphantom/phantom-dashboard)
- [nervecenter/Dash](https://github.com/nervecenter/Dash)
- [AnalogGaugeWidgetPyQt](https://github.com/StefanHol/AnalogGaugeWidgetPyQt)

### Regulations
- [FIA Technical Regulations](https://www.fia.com/regulation/category/110)

## Critical Files

When modifying the dashboard, these are the key files:

| File | Purpose |
|------|---------|
| `src/data/emu_protocol.py` | EMU Black CAN protocol decoder |
| `src/layouts/race_layout.py` | Main dashboard layout composition |
| `src/widgets/circular_gauge.py` | Core tachometer widget |
| `src/core/config.py` | Configuration management |
| `src/data/mock_source.py` | Simulation with engine sound |
| `config/default.yaml` | All configurable parameters |

## 3D Model Editing

To modify the enclosure design:
1. Open `3d-model/robodash.f3d` in Fusion 360
2. Export updated STL files for 3D printing
3. Test fit with physical Corsair Xeneon Edge dimensions

See `docs/BUILD.adoc` for assembly instructions.
