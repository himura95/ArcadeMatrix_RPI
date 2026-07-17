#!/bin/bash
# install_recalbox_sync.sh
# Run this script from your Mac terminal to install the MQTT sync script on Recalbox

RECALBOX_IP="192.168.1.133"
RECALBOX_PASS="recalboxroot"
MQTT_BROKER="192.168.1.100" # Change this if your broker is on a different IP

echo "===================================================="
echo " ArcadeMatrix - Recalbox MQTT Sync Installer"
echo "===================================================="
echo "Creating the synchronization script locally..."

cat << 'EOF' > arcadematrix_sync.sh
#!/bin/bash
# ArcadeMatrix MQTT Sync Script for Recalbox
# Placed in /userdata/system/scripts/

ACTION=$1
ROM_PATH=$2
SYSTEM_NAME=$3

# Configuration (replaced during install)
BROKER="MQTT_BROKER_IP"
TOPIC="recalbox/system/playing"

# Extract game name from rom path
GAME_NAME=$(basename "$ROM_PATH" | sed 's/\.[^.]*$//')

# Check if mosquitto_pub is available (Recalbox usually has it)
if ! command -v mosquitto_pub &> /dev/null; then
    # Fallback to python raw MQTT if needed, but Recalbox 9+ includes mosquitto
    echo "mosquitto_pub not found!" > /tmp/arcadematrix_mqtt.log
fi

case $ACTION in
    gameStart)
        mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{\"status\": \"playing\", \"game\": \"$GAME_NAME\", \"system\": \"$SYSTEM_NAME\"}"
        ;;
    gameStop)
        mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{\"status\": \"stopped\"}"
        ;;
esac
EOF

# Replace the broker IP
sed -i '' "s/MQTT_BROKER_IP/$MQTT_BROKER/g" arcadematrix_sync.sh

echo "Uploading script to Recalbox at $RECALBOX_IP..."
echo "(You may be prompted for the Recalbox password: $RECALBOX_PASS)"

# Ensure the scripts directory exists and copy the file
ssh root@$RECALBOX_IP "mkdir -p /userdata/system/scripts/"
scp arcadematrix_sync.sh root@$RECALBOX_IP:/userdata/system/scripts/
ssh root@$RECALBOX_IP "chmod +x /userdata/system/scripts/arcadematrix_sync.sh"

echo "Cleaning up local files..."
rm arcadematrix_sync.sh

echo "===================================================="
echo " Installation Complete!"
echo " Recalbox will now publish MQTT messages to $MQTT_BROKER"
echo " on topic: recalbox/system/playing"
echo "===================================================="
