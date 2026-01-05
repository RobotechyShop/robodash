#!/bin/bash
# =============================================================================
# RoboDash Headless Test Runner
#
# Runs pytest in a virtual framebuffer for CI/CD or headless environments.
# This is required for Qt widget tests on systems without a display.
#
# Usage:
#   ./scripts/run_tests_headless.sh [pytest args]
#
# Examples:
#   ./scripts/run_tests_headless.sh
#   ./scripts/run_tests_headless.sh -v -m screenshot
#   ./scripts/run_tests_headless.sh tests/test_widgets/ --cov=src
# =============================================================================

set -e

# Check for Xvfb
if ! command -v Xvfb &> /dev/null; then
    echo "Xvfb not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y xvfb
    else
        echo "Error: Please install Xvfb manually"
        exit 1
    fi
fi

# Start Xvfb on display :99
export DISPLAY=:99
Xvfb :99 -screen 0 1920x360x24 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 1

# Verify Xvfb is running
if ! kill -0 $XVFB_PID 2>/dev/null; then
    echo "Error: Failed to start Xvfb"
    exit 1
fi

echo "Xvfb started on display $DISPLAY (PID: $XVFB_PID)"
echo "Running tests..."
echo "=============================================="

# Run pytest with any passed arguments
python -m pytest tests/ "$@"
TEST_EXIT_CODE=$?

echo "=============================================="
echo "Tests complete (exit code: $TEST_EXIT_CODE)"

# Cleanup Xvfb
kill $XVFB_PID 2>/dev/null || true
echo "Xvfb stopped"

exit $TEST_EXIT_CODE
