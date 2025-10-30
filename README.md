# robodash

[![License](https://img.shields.io/badge/License-Educational-blue.svg)](LICENSE)

A custom racing car dashboard project for a Toyota Supra Mk4, designed as part of an NEA coursework. This repository contains 3D models, research documents, and design specifications for a Raspberry Pi-powered dashboard using the Corsair Xenon screen.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Project Overview](#project-overview)
- [Client Profile](#client-profile)
- [Research and Development](#research-and-development)
- [Design Specifications](#design-specifications)
- [Contributing](#contributing)
- [Bibliography](#bibliography)
- [License](#license)

## Description

This project focuses on designing and prototyping a modern, customizable dashboard for a time attack Toyota Supra Mk4. The dashboard integrates a Corsair Xenon touchscreen display controlled by a Raspberry Pi, providing real-time data visualization for racing applications. The design emphasizes safety, ergonomics, and compliance with FIA regulations.

Key components:
- **Hardware**: Raspberry Pi, Corsair Xenon 7" touchscreen
- **Software**: Custom interface for displaying speed, lap times, temperatures, and warnings
- **Materials**: PETG-CF 3D printed enclosure with carbon fiber accents
- **Regulations**: Compliant with FIA time attack series standards

## Features

- **Customizable Display**: Touchscreen interface showing essential racing metrics
- **3D Printed Enclosure**: Lightweight, durable design using PETG-CF filament
- **Raspberry Pi Integration**: Runs custom software for data visualization
- **FIA Compliant**: Meets safety and regulatory requirements for time attack racing
- **Modular Design**: Easy to modify and upgrade components

## Project Structure

```
robodash/
├── 3d-model/
│   ├── README.md
│   └── robodash.f3d          # Fusion 360 design file
└── README.md                 # This file
```

## Installation

### Prerequisites
- Fusion 360 (for viewing/editing 3D models)
- Raspberry Pi (for hardware prototyping)
- 3D Printer (for enclosure manufacturing)
- Corsair Xenon touchscreen (optional for full setup)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/robodash.git
   cd robodash
   ```

2. Open the 3D model in Fusion 360:
   - Navigate to `3d-model/robodash.f3d`

3. For hardware setup:
   - Connect Raspberry Pi to Corsair Xenon screen
   - Install required software (Python, GPIO libraries)

## Usage

### Viewing the Design
- Open `3d-model/robodash.f3d` in Fusion 360 to view the dashboard enclosure design.

### Prototyping
1. Print the enclosure using PETG-CF filament on a 3D printer.
2. Mount the Corsair Xenon screen in the enclosure.
3. Connect to Raspberry Pi and run custom interface software.

## Project Overview

This NEA coursework project involves the design and development of a custom dashboard for a racing car. It includes phases such as ethnographic research, secondary product analysis, co-designing, and prototyping. The goal is to create a functional, safe, and aesthetically pleasing dashboard that meets the client's needs and regulatory standards.

### Project Sections
- Ethnographic Research: Studying user interactions and controls
- Secondary Product Analysis: Evaluating existing dashboard solutions
- Secondary Research with Materials: Selecting appropriate materials
- Mood Board of Examples: Visual inspiration and design ideas
- Co-Designing: Collaborative design with client
- Design Brief and Specification: Detailed requirements and specs

## Client Profile

- **Client**: Racing enthusiast with Toyota Supra time attack experience
- **Needs**: Custom dashboard for Toyota Supra time attack racing
- **Requirements**: Minimalist design, real-time data display, FIA compliance

## Research and Development

### Key Research Areas
- Ethnographic research on racing controls
- Secondary product analysis of existing dashboards
- Material research (PETG-CF, Carbon Fiber, PLA)
- Co-designing with client feedback
- Site visit to assess installation constraints

### Development Phases
1. **Research**: Client interviews, market analysis, material testing
2. **Design**: CAD modeling, prototyping, iteration
3. **Testing**: Vibration testing, usability evaluation
4. **Finalization**: Production of complete dashboard

### Client Interview Summary
- General: Involved in racing since early 20s, time attack experience
- Problems: Discomfort from roll cage, wiring issues, non-functional gauges
- Usability: Quick access important for safety, customizable features desired
- Preferences: Minimalist design, high-end aesthetics, ease of modification

## Design Specifications

### Dimensions
- Screen: 372mm x 120mm x 22mm (14.65" x 4.72" x 0.86")
- Enclosure: Slightly larger than screen for cable management

### Materials
- Primary: PETG-CF filament (strength, lightweight)
- Alternative: Carbon fiber for accents
- Prototyping: PLA

### Performance Requirements
- Vibration resistant for track use
- Touchscreen responsive in daylight
- Customizable widget system
- Real-time data display (speed, temps, lap times)

### Safety & Regulations
- FIA Appendix J compliance
- External master cut-off switch
- Visible warning indicators
- Non-obstructive design

### Specification Criteria
- Product Function: Seamless dashboard with customizable data display
- Client/User: Racing enthusiast requiring functional, safe interface
- Environment and Sustainability: Prioritize quality over sustainability for one-off product
- Properties of Materials: 3D printed PETG-CF with carbon fiber options
- Dimensional Constraints: Fit within screen dimensions and cockpit space
- Cost: Approximately £250 for materials and components
- Manufacturing and Quality: 3D printing with iterative prototyping
- Aesthetics: High-end Lamborghini-inspired design
- Time Constraints: Complete by April, product by late February

## Contributing

This is an educational project. Contributions are welcome for:
- 3D model improvements
- Software development
- Documentation enhancements

Please open an issue or submit a pull request.

## Bibliography

### Books
- Norris, D. (2016) *Raspberry Pi Electronics Projects for the Evil Genius*. New York: McGraw-Hill Education.
- Radovici, A. and Culic, I. (2021) *Getting Started with Secure Embedded Systems*. Berkeley: Apress.
- Deng, J. (2021) *Build Your Own Linux System For Raspberry Pi*. Berkeley: Apress.
- Carlsen, J. (2020) *Python: Embedded Systems for Beginners*. Scotts Valley: CreateSpace Independent Publishing Platform.
- McCarthy, S. (2017) *The Raspberry Pi 3 Project Book*. Indianapolis: Que.

### Websites
- Corsair. (2023) *CORSAIR XENEON EDGE Touchscreen: Everything you need to know*. Available at: https://www.corsair.com/us/en/Categories/Products/Gaming-Peripherals/Streaming-Gear/Xenon-Series/p/CP-9010075-WW (Accessed: 30 October 2025).
- Federation Internationale de l'Automobile. (n.d.) Available at: https://www.fia.com/ (Accessed: 30 October 2025).
- webtechy. (n.d.) *(49) webtechy - YouTube*. Available at: https://www.youtube.com/@webtechy (Accessed: 30 October 2025).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Note: This is for educational purposes as part of coursework.

