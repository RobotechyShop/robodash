# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RoboDash is a custom racing car dashboard for a Toyota Supra Mk4, designed as an NEA coursework project. The system integrates:
- **Hardware**: Raspberry Pi 4 + Corsair Xenon 7" touchscreen (372mm x 120mm x 22mm)
- **Enclosure**: 3D printed PETG-CF with carbon fiber accents
- **Purpose**: Real-time racing data visualization (speed, lap times, temperatures, warnings)
- **Compliance**: FIA time attack series regulations (Appendix J)

## Repository Structure

```
robodash/
├── 3d-model/
│   ├── robodash.f3d                    # Fusion 360 source file
│   ├── Robodash Left Top.stl           # Exported STL parts
│   ├── Robodash Left Bottom.stl
│   ├── Robodash Right Top.stl
│   └── Robodash Right Bottom.stl
└── README.md                            # Comprehensive project documentation
```

## Current State

This repository currently contains only 3D design files. **No software has been implemented yet.**

Future software development will need to:
1. Interface with Raspberry Pi GPIO for sensor inputs
2. Display customizable widgets for racing metrics
3. Provide touchscreen controls for configuration
4. Implement safety warnings and FIA-compliant indicators

## Hardware Specifications

### Display
- Corsair Xeneon touchscreen: 372mm x 120mm x 22mm
- Must be responsive in bright daylight conditions
- Touchscreen interface for real-time configuration

### Enclosure Materials
- **Production**: PETG-CF filament (strength + lightweight)
- **Prototyping**: PLA
- **Accents**: Carbon fiber components

### Mounting & Safety
- Must withstand track vibration
- Non-obstructive installation in cockpit
- External master cut-off switch required (FIA)
- Visible warning indicators mandatory

## Design Constraints

- **Dimensional**: Fit Corsair Xenon screen + allow cable management
- **Budget**: ~£250 for materials and components
- **Regulations**: FIA Appendix J compliance for time attack racing
- **Aesthetics**: Lamborghini-inspired high-end minimalist design
- **Manufacturing**: 3D printing with iterative prototyping

## Client Requirements

The client is a racing enthusiast requiring:
- **Minimalist design** with quick access to essential data
- **Customizable features** (widgets, layouts)
- **Real-time data display**: speed, temperatures, lap times
- **Safety-first approach** with non-distracting interface
- **Easy modification** for future upgrades

## 3D Model Editing

To modify the enclosure design:
1. Open `3d-model/robodash.f3d` in Fusion 360
2. Export updated STL files for 3D printing
3. Test fit with physical Corsair Xenon screen dimensions

## Future Development Areas

When implementing software:
- Use Python for Raspberry Pi GPIO interfacing
- Consider libraries: RPi.GPIO, pygame/tkinter for UI
- Implement data acquisition from OBD-II/CAN bus
- Design modular widget system for customization
- Ensure real-time performance for safety-critical warnings
