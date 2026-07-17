#!/bin/bash
# ==============================================================================
# ArcadeMatrix - Recalbox MQTT Installer (A EXÉCUTER SUR LA RECALBOX DIRECTEMENT)
# ==============================================================================

# Mets ici l'adresse IP de ton Raspberry Pi (celui avec la matrice LED)
MQTT_BROKER="192.168.1.169"

TARGET_DIR="/recalbox/share/userscripts"
TARGET_FILE="$TARGET_DIR/arcadematrix_mqtt.sh"

echo "Configuration du hook MQTT pour ArcadeMatrix..."

# Création du répertoire de scripts d'EmulationStation si manquant
mkdir -p "$TARGET_DIR"

# Création du script d'événements
cat << 'EOF' > "$TARGET_FILE"
#!/bin/bash
# Script d'événement automatique EmulationStation (Format Recalbox)

echo "----------------------------------------" >> /recalbox/share/userscripts/mqtt_debug.log
echo "$(date) - Script called with args: $@" >> /recalbox/share/userscripts/mqtt_debug.log

ACTION=""
STATEFILE=""

# Parse les arguments de Recalbox (-action rungame -statefile /tmp/...)
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -action) ACTION="$2"; shift ;;
        -statefile) STATEFILE="$2"; shift ;;
    esac
    shift
done

BROKER="MQTT_BROKER_IP_PLACEHOLDER"
TOPIC="recalbox/system/playing"

if [[ "$ACTION" == "rungame" || "$ACTION" == "gameStart" ]]; then
    # Essayer de lire le statefile de Recalbox
    if [ -f "$STATEFILE" ]; then
        ROM_PATH=$(grep -i '^rom=' "$STATEFILE" | cut -d'=' -f2- | tr -d '\r')
        SYSTEM_NAME=$(grep -i '^system=' "$STATEFILE" | cut -d'=' -f2- | tr -d '\r')
    else
        ROM_PATH=$2 # Fallback Batocera
        SYSTEM_NAME=$3
    fi
    
    GAME_NAME=$(basename "$ROM_PATH" | sed 's/\.[^.]*$//')
    mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{\"status\": \"playing\", \"game\": \"$GAME_NAME\", \"system\": \"$SYSTEM_NAME\"}"

elif [[ "$ACTION" == "quitgame" || "$ACTION" == "gameStop" ]]; then
    mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{\"status\": \"stopped\"}"
fi
EOF

# Remplacement de l'IP dans le script final (syntaxe Linux standard pour Buildroot)
sed -i "s/MQTT_BROKER_IP_PLACEHOLDER/$MQTT_BROKER/g" "$TARGET_FILE"

# Rendre le script exécutable pour EmulationStation
chmod +x "$TARGET_FILE"

echo "=============================================================================="
echo "SUCCÈS ! Le hook MQTT a été installé ici : $TARGET_FILE"
echo "Chaque lancement/arrêt de jeu notifiera ArcadeMatrix ($MQTT_BROKER)."
echo "=============================================================================="
