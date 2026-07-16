#!/bin/bash
# ArcadeMatrix_RPi Auto-Installation Script (Non-Interactive)
# Recommended OS: Raspberry Pi OS Lite (32-bit or 64-bit)

echo "======================================"
echo "    ArcadeMatrix RPi Auto-Installer   "
echo "======================================"
echo "⚠️ WARNING for Raspberry Pi 5 users: "
echo "The hzeller rgb-led-matrix library does NOT support the Pi 5 natively"
echo "due to the new RP1 GPIO chip. You MUST use an active adapter board."
echo "Pi 3, Pi 4, and Zero 2 W are fully supported out of the box."
echo "======================================"

# 1. Stop existing service if installed
if systemctl list-unit-files | grep -q arcadematrix.service; then
    echo "Stopping existing ArcadeMatrix service..."
    sudo systemctl stop arcadematrix.service || true
    sudo systemctl disable arcadematrix.service 2>/dev/null || true
fi

# 2. Update and install dependencies
echo "Updating packages and installing system dependencies..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-dev python3-pil python3-flask python3-venv git build-essential curl cython3

# Check if we are in the project root
if [ ! -f "main.py" ]; then
    echo "main.py not found. It looks like you ran this script standalone."
    echo "Cloning the ArcadeMatrix_RPI repository..."
    git clone https://github.com/red77290/ArcadeMatrix_RPI.git
    cd ArcadeMatrix_RPI || { echo "Failed to enter directory"; exit 1; }
else
    echo "Found main.py, proceeding with local files..."
fi

CURRENT_DIR=$(pwd)

# 3. Setup Python Virtual Environment
echo "Setting up Python Virtual Environment..."
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 4. Configure Matrix Hardware (AUTO DEFAULTS)
echo ""
echo "--- MATRIX HARDWARE CONFIGURATION (AUTO) ---"
MAPPING="regular"
ROWS=32
COLS=64
CHAIN=1
PARALLEL=1

if [ ! -f "conf.ini" ]; then
    echo "conf.ini not found. Please ensure it is present in the repository."
else
    echo "conf.ini found. Preserving existing configuration."
fi


# 5. Install hzeller's rgbmatrix library
if [ ! -d "rpi-rgb-led-matrix" ]; then
    echo "Cloning hzeller's rpi-rgb-led-matrix library..."
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
fi

echo "Compiling rgbmatrix library via scikit-build-core (this might take a few minutes)..."
cd rpi-rgb-led-matrix
# The library uses modern CMake via pyproject.toml now
../venv/bin/pip install .
cd ..


# 6. Anti-Flicker Performance Tweaks (Disable Audio)
echo "Applying anti-flicker optimizations (Disabling Onboard Audio)..."

# Blacklist sound module
sudo bash -c "cat > /etc/modprobe.d/snd-blacklist.conf << EOF
blacklist snd_bcm2835
EOF"

# Disable audio in config.txt (handling both older OS and Bookworm paths)
CONFIG_TXT="/boot/config.txt"
if [ -f "/boot/firmware/config.txt" ]; then
    CONFIG_TXT="/boot/firmware/config.txt"
fi

if grep -q "dtparam=audio=on" "$CONFIG_TXT"; then
    sudo sed -i 's/dtparam=audio=on/dtparam=audio=off/g' "$CONFIG_TXT"
    echo "Disabled audio in $CONFIG_TXT"
elif ! grep -q "dtparam=audio=off" "$CONFIG_TXT"; then
    echo "dtparam=audio=off" | sudo tee -a "$CONFIG_TXT" > /dev/null
fi

# Disable HDMI audio loaded by vc4 driver which causes PWM conflicts
if grep -q "dtoverlay=vc4-kms-v3d$" "$CONFIG_TXT"; then
    sudo sed -i 's/dtoverlay=vc4-kms-v3d$/dtoverlay=vc4-kms-v3d,noaudio/g' "$CONFIG_TXT"
    echo "Disabled vc4 HDMI audio in $CONFIG_TXT"
fi

# Isolate CPU core 3 for perfect LED matrix timing
CMDLINE_TXT="/boot/cmdline.txt"
if [ -f "/boot/firmware/cmdline.txt" ]; then
    CMDLINE_TXT="/boot/firmware/cmdline.txt"
fi

if ! grep -q "isolcpus=" "$CMDLINE_TXT"; then
    sudo sed -i '1 s/$/ isolcpus=3/' "$CMDLINE_TXT"
    echo "Isolated CPU core 3 in $CMDLINE_TXT for LED matrix"
fi

# Disable triggerhappy service which is known to cause PWM flickering
sudo systemctl disable triggerhappy 2>/dev/null || true

# 7. Setup Systemd Service
echo "Setting up systemd service for auto-start..."
SERVICE_FILE="/etc/systemd/system/arcadematrix.service"

sudo bash -c "cat > $SERVICE_FILE << EOF
[Unit]
Description=ArcadeMatrix RPi Daemon
After=network.target

[Service]
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/main.py
WorkingDirectory=$CURRENT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root
# root is required to interact with GPIO for the LED Matrix

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable arcadematrix.service
sudo systemctl restart arcadematrix.service || echo "Warning: Could not start service (this is normal in chroot)"

IP_ADDR=$(hostname -I | awk '{print $1}')
echo "======================================"
echo "Installation Complete (Auto Mode)!"
echo "The service has been enabled. You can check its status with:"
echo "sudo systemctl status arcadematrix.service"
echo ""
if [ -n "$IP_ADDR" ]; then
    echo "You can access the Web UI at: http://$IP_ADDR:8080"
else
    echo "You can access the Web UI at: http://<raspberry-pi-ip>:8080"
fi
echo "======================================"
echo "⚠️ IMPORTANT: Audio has been disabled to prevent matrix flickering."
echo "Please REBOOT your Raspberry Pi now to apply the hardware changes!"
echo "Command: sudo reboot"
echo "======================================"
