#!/bin/bash
#
# RoboDash CAN Interface Setup Script
#
# This script configures the MCP2515 CAN controller on Raspberry Pi
# for communication with ECUMaster EMU Black at 500 kbps.
#
# Usage:
#   sudo ./setup_can.sh [options]
#
# Options:
#   -b, --bitrate    CAN bitrate (default: 500000)
#   -c, --channel    CAN channel (default: can0)
#   -t, --test       Run loopback test
#   -p, --persistent Make configuration persistent
#   -h, --help       Show this help
#

set -e

# Default values
BITRATE=500000
CHANNEL="can0"
TEST_MODE=false
PERSISTENT=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Help message
show_help() {
    echo "RoboDash CAN Interface Setup Script"
    echo ""
    echo "Usage: sudo $0 [options]"
    echo ""
    echo "Options:"
    echo "  -b, --bitrate RATE   CAN bitrate in bps (default: 500000)"
    echo "  -c, --channel NAME   CAN channel name (default: can0)"
    echo "  -t, --test           Run loopback test after setup"
    echo "  -p, --persistent     Make configuration persistent across reboots"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo $0                    # Setup can0 at 500 kbps"
    echo "  sudo $0 -b 250000          # Setup can0 at 250 kbps"
    echo "  sudo $0 -t                 # Setup and run loopback test"
    echo "  sudo $0 -p                 # Setup and make persistent"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--bitrate)
            BITRATE="$2"
            shift 2
            ;;
        -c|--channel)
            CHANNEL="$2"
            shift 2
            ;;
        -t|--test)
            TEST_MODE=true
            shift
            ;;
        -p|--persistent)
            PERSISTENT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    error "This script must be run as root (sudo)"
fi

# Check if can-utils is installed
if ! command -v candump &> /dev/null; then
    info "Installing can-utils..."
    apt-get update
    apt-get install -y can-utils
fi

# Check for kernel module
info "Checking CAN kernel modules..."
if ! lsmod | grep -q "mcp251x"; then
    warn "MCP251x module not loaded"

    # Check if dtoverlay is configured
    if ! grep -q "mcp2515" /boot/firmware/config.txt 2>/dev/null && \
       ! grep -q "mcp2515" /boot/config.txt 2>/dev/null; then
        error "MCP2515 dtoverlay not configured in /boot/firmware/config.txt

Add the following to /boot/firmware/config.txt:
    dtparam=spi=on
    dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25,spimaxfrequency=1000000

Then reboot and run this script again."
    fi

    warn "dtoverlay configured but module not loaded. Try rebooting."
fi

# Bring down interface if already up
if ip link show "$CHANNEL" &> /dev/null; then
    info "Bringing down existing $CHANNEL interface..."
    ip link set "$CHANNEL" down 2>/dev/null || true
fi

# Configure CAN interface
info "Configuring $CHANNEL at $BITRATE bps..."
ip link set "$CHANNEL" type can bitrate "$BITRATE"

# Bring up interface
info "Bringing up $CHANNEL..."
ip link set "$CHANNEL" up

# Verify
if ip link show "$CHANNEL" | grep -q "UP"; then
    info "$CHANNEL is UP and configured at $BITRATE bps"
else
    error "Failed to bring up $CHANNEL"
fi

# Show interface status
echo ""
ip -details link show "$CHANNEL"

# Make persistent if requested
if $PERSISTENT; then
    info "Making configuration persistent..."

    NETIF_FILE="/etc/network/interfaces.d/$CHANNEL"

    cat > "$NETIF_FILE" << EOF
# CAN interface for RoboDash
# Auto-configured by setup_can.sh
auto $CHANNEL
iface $CHANNEL inet manual
    pre-up /sbin/ip link set $CHANNEL type can bitrate $BITRATE
    up /sbin/ip link set $CHANNEL up
    down /sbin/ip link set $CHANNEL down
EOF

    info "Configuration saved to $NETIF_FILE"
    info "$CHANNEL will start automatically on boot"
fi

# Run loopback test if requested
if $TEST_MODE; then
    info "Running loopback test..."

    # Set loopback mode
    ip link set "$CHANNEL" down
    ip link set "$CHANNEL" type can bitrate "$BITRATE" loopback on
    ip link set "$CHANNEL" up

    # Start candump in background
    timeout 5 candump "$CHANNEL" &
    DUMP_PID=$!

    sleep 1

    # Send test message
    info "Sending test message: 123#DEADBEEF"
    cansend "$CHANNEL" 123#DEADBEEF

    sleep 2

    # Kill candump
    kill $DUMP_PID 2>/dev/null || true

    # Restore normal mode
    ip link set "$CHANNEL" down
    ip link set "$CHANNEL" type can bitrate "$BITRATE" loopback off
    ip link set "$CHANNEL" up

    info "Loopback test complete. If you saw the test message above, CAN is working."
fi

echo ""
info "Setup complete!"
echo ""
echo "To monitor CAN traffic:"
echo "    candump $CHANNEL"
echo ""
echo "To send a test message:"
echo "    cansend $CHANNEL 123#DEADBEEF"
echo ""
echo "To run RoboDash:"
echo "    python -m src.main"
