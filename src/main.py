#!/usr/bin/env python3
"""
RoboDash - Racing Dashboard for Toyota Supra Mk4

Entry point for the dashboard application.

Usage:
    python -m src.main [options]

Options:
    --mock          Use mock data source (no CAN hardware required)
    --sound         Enable synthesized engine sound (mock mode only)
    --config PATH   Path to configuration file
    --windowed      Run in windowed mode instead of fullscreen
    --debug         Enable debug logging

Reference implementation based on:
    https://github.com/valtsu23/DIY-Emu-Black-Dash

Copyright (c) 2025 Robotechy
"""

import argparse
import logging
import sys
from pathlib import Path

from .core.app import DashboardApp
from .core.config import Config


def setup_logging(debug: bool = False) -> None:
    """
    Configure application logging.

    Args:
        debug: Enable debug level logging.
    """
    level = logging.DEBUG if debug else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from Qt
    logging.getLogger("PyQt5").setLevel(logging.WARNING)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="RoboDash - Racing Dashboard for Toyota Supra Mk4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m src.main                  # Run with auto-detected data source
    python -m src.main --mock           # Run with simulated data
    python -m src.main --mock --sound   # Run with simulated data and engine sound
    python -m src.main --windowed       # Run in windowed mode
    python -m src.main --debug          # Enable debug logging

Reference: https://github.com/valtsu23/DIY-Emu-Black-Dash
        """,
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use mock data source (simulated vehicle data)",
    )

    parser.add_argument(
        "--sound",
        action="store_true",
        help="Enable synthesized engine sound (mock mode only)",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to configuration file (default: config/default.yaml)",
    )

    parser.add_argument(
        "--windowed",
        action="store_true",
        help="Run in windowed mode instead of fullscreen",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument("--version", action="version", version="RoboDash 1.0.0")

    return parser.parse_args()


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success).
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    logger.info("=" * 50)
    logger.info("RoboDash Starting")
    logger.info("=" * 50)

    # Load configuration
    config = Config.load(args.config)

    # Override fullscreen if windowed flag set
    if args.windowed:
        config.display.fullscreen = False
        config.display.frameless = False

    logger.info(f"Configuration loaded: {config.app_name} v{config.app_version}")
    logger.info(f"Display: {config.display.width}x{config.display.height}")
    logger.info(f"CAN: {'enabled' if config.can.enabled else 'disabled'}")
    logger.info(f"Mock mode: {args.mock}")
    logger.info(f"Engine sound: {args.sound}")

    # Create and run application
    try:
        app = DashboardApp(config, use_mock=args.mock, enable_sound=args.sound)
        exit_code = app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        exit_code = 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        exit_code = 1
    finally:
        logger.info("RoboDash exiting")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
