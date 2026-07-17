import paramiko
import logging
import socket
import json

def install_sync_script(target_ip, matrix_ip):
    """
    Connects via SSH to Recalbox or Batocera and installs the event sync script.
    Returns (success_bool, message)
    """
    port = 22
    username = "root"
    passwords = [
        ("Recalbox", "recalboxroot", "/recalbox/share/userscripts"),
        ("Batocera", "linux", "/userdata/system/scripts")
    ]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connected = False
    system_name = None
    target_dir = None
    
    for sys_name, pwd, t_dir in passwords:
        try:
            logging.info(f"Trying to connect to {target_ip} as {sys_name}...")
            ssh.connect(target_ip, port=port, username=username, password=pwd, timeout=5)
            connected = True
            system_name = sys_name
            target_dir = t_dir
            break
        except paramiko.AuthenticationException:
            logging.warning(f"Authentication failed for {sys_name} password.")
        except socket.timeout:
            return False, f"Timeout connecting to {target_ip}. Make sure the IP is correct and the system is turned on."
        except Exception as e:
            logging.warning(f"Connection error: {e}")
            
    if not connected:
        return False, "Failed to authenticate. Is it Recalbox (pwd: recalboxroot) or Batocera (pwd: linux)?"
        
    try:
        # Create the script content
        script_content = f"""#!/bin/bash
# ArcadeMatrix Auto-Sync Script for {system_name}
# Automatically installed by ArcadeMatrix Web UI

BROKER="{matrix_ip}"
TOPIC="recalbox/system/playing"
ACTION=""
STATEFILE=""

# Parse arguments (Recalbox style)
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -action) ACTION="$2"; shift ;;
        -statefile) STATEFILE="$2"; shift ;;
    esac
    shift
done

# Fallback for Batocera
if [ -z "$ACTION" ]; then
    ACTION=$1
    ROM_PATH=$2
    SYSTEM_NAME=$3
fi

if [[ "$ACTION" == "rungame" || "$ACTION" == "gameStart" || "$ACTION" == "GamelistBrowsing" || "$ACTION" == "gameSelected" ]]; then
    
    # Read statefile for Recalbox
    if [ -n "$STATEFILE" ] && [ -f "$STATEFILE" ]; then
        ROM_PATH=$(grep -i '^rom=' "$STATEFILE" | cut -d'=' -f2- | tr -d '\\r')
        SYSTEM_NAME=$(grep -i '^system=' "$STATEFILE" | cut -d'=' -f2- | tr -d '\\r')
    fi
    
    if [ -z "$ROM_PATH" ]; then
        exit 0
    fi
    
    ROM_DIR=$(dirname "$ROM_PATH")
    GAME_BASENAME=$(basename "$ROM_PATH" | sed 's/\\.[^.]*$//')
    
    # Search for marquee image
    MARQUEE_PATH=""
    for ext in png jpg gif; do
        if [ -f "$ROM_DIR/images/${{GAME_BASENAME}}-marquee.$ext" ]; then
            MARQUEE_PATH="$ROM_DIR/images/${{GAME_BASENAME}}-marquee.$ext"
            break
        elif [ -f "$ROM_DIR/images/${{GAME_BASENAME}}-wheel.$ext" ]; then
            MARQUEE_PATH="$ROM_DIR/images/${{GAME_BASENAME}}-wheel.$ext"
            break
        elif [ -f "$ROM_DIR/images/${{GAME_BASENAME}}-image.$ext" ]; then
            MARQUEE_PATH="$ROM_DIR/images/${{GAME_BASENAME}}-image.$ext"
            break
        elif [ -f "$ROM_DIR/downloaded_images/${{GAME_BASENAME}}-marquee.$ext" ]; then
            MARQUEE_PATH="$ROM_DIR/downloaded_images/${{GAME_BASENAME}}-marquee.$ext"
            break
        fi
    done
    
    if [ -n "$MARQUEE_PATH" ]; then
        # Send image via HTTP to ArcadeMatrix
        curl -s -X POST -F "image=@$MARQUEE_PATH" http://$BROKER:8080/api/marquee > /dev/null &
    else
        # Fallback to Text via MQTT
        STATUS="playing"
        if [[ "$ACTION" == "GamelistBrowsing" || "$ACTION" == "gameSelected" ]]; then
            STATUS="browsing"
        fi
        mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{{\\"status\\": \\"$STATUS\\", \\"game\\": \\"$GAME_BASENAME\\", \\"system\\": \\"$SYSTEM_NAME\\"}}" &
    fi

elif [[ "$ACTION" == "quitgame" || "$ACTION" == "gameStop" ]]; then
    mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{{\\"status\\": \\"stopped\\"}}" &
fi
"""
        
        script_path = f"{target_dir}/arcadematrix_mqtt.sh"
        
        logging.info(f"Creating directory {target_dir}...")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {target_dir}")
        stdout.read()
        
        logging.info(f"Uploading script to {script_path}...")
        sftp = ssh.open_sftp()
        with sftp.file(script_path, "w") as f:
            f.write(script_content)
        sftp.close()
        
        logging.info("Making script executable...")
        ssh.exec_command(f"chmod +x {script_path}")
        
        return True, f"Successfully installed on {system_name}!"
        
    except Exception as e:
        logging.error(f"Error during installation: {e}")
        return False, f"Installation error: {str(e)}"
    finally:
        ssh.close()
