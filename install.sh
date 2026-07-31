#!/bin/bash
# ArcadeMatrix_RPi Rust Installer
set -e

echo "======================================"
echo "    ArcadeMatrix RPi Installer (Rust) "
echo "======================================"

# Stop existing service if running
if systemctl list-unit-files | grep -q arcadematrix.service; then
    echo "Stopping existing ArcadeMatrix service..."
    sudo systemctl stop arcadematrix.service || true
fi

# Install system dependencies
sudo apt-get update
sudo apt-get install -y curl mosquitto mosquitto-clients

# Configure Mosquitto MQTT Broker
sudo bash -c 'echo -e "listener 1883 0.0.0.0\nallow_anonymous true" > /etc/mosquitto/conf.d/arcadematrix.conf'
sudo systemctl restart mosquitto || true

CURRENT_DIR=$(pwd)

# Install Rust toolchain if cargo is not found
if ! command -v cargo &> /dev/null; then
    echo "Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

echo "Building ArcadeMatrix native binary..."
cargo build --release

sudo cp target/release/arcadematrix /usr/local/bin/arcadematrix
sudo chmod +x /usr/local/bin/arcadematrix

# Setup Systemd Service
echo "Setting up systemd service..."
SERVICE_FILE="/etc/systemd/system/arcadematrix.service"

sudo bash -c "cat > $SERVICE_FILE << EOF
[Unit]
Description=ArcadeMatrix RPi Daemon (Rust)
After=network.target

[Service]
ExecStart=/usr/local/bin/arcadematrix
WorkingDirectory=$CURRENT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable arcadematrix.service
sudo systemctl restart arcadematrix.service || true

echo "======================================"
echo "ArcadeMatrix RPi Rust Installation Complete!"
echo "Web UI accessible at: http://<raspberry-pi-ip>:8080"
echo "======================================"
