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
        if system_name == "Batocera":
            script_content = f"""#!/bin/sh
# ArcadeMatrix Auto-Sync Script for Batocera

BROKER="{matrix_ip}"
TOPIC="recalbox/system/playing"
ACTION=$1
ROM_PATH=$2
SYSTEM_NAME=$3

if [ "$ACTION" = "gameStart" ] || [ "$ACTION" = "gameSelected" ]; then
    GAME_BASENAME=$(basename "$ROM_PATH" | sed 's/\\.[^.]*$//')
    ROM_DIR=$(dirname "$ROM_PATH")
    
    MARQUEE_PATH=""
    for ext in png jpg gif; do
        for prefix in "images/" "downloaded_images/" "media/marquees/" "media/images/" "media/wheels/" ""; do
            for suffix in "-marquee" "-wheel" "-image" "-thumb" ""; do
                if [ -f "$ROM_DIR/$prefix${{GAME_BASENAME}}$suffix.$ext" ]; then
                    MARQUEE_PATH="$ROM_DIR/$prefix${{GAME_BASENAME}}$suffix.$ext"
                    break 3
                fi
            done
        done
    done
    
    if [ -n "$MARQUEE_PATH" ]; then
        curl -s -X POST -F "image=@$MARQUEE_PATH" http://$BROKER:8080/api/marquee > /dev/null &
    else
        STATUS="playing"
        if [ "$ACTION" = "gameSelected" ]; then STATUS="browsing"; fi
        mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{{\\"status\\": \\"$STATUS\\", \\"game\\": \\"$GAME_BASENAME\\", \\"system\\": \\"$SYSTEM_NAME\\"}}" &
    fi
elif [ "$ACTION" = "gameStop" ]; then
    mosquitto_pub -h "$BROKER" -t "$TOPIC" -m "{{\\"status\\": \\"stopped\\"}}" &
fi
"""
            script_path = f"{target_dir}/arcadematrix_mqtt.sh"
            
            logging.info(f"Creating directory {target_dir}...")
            ssh.exec_command(f"mkdir -p {target_dir}")
            
            logging.info(f"Uploading script to {script_path}...")
            sftp = ssh.open_sftp()
            with sftp.file(script_path, "w") as f:
                f.write(script_content)
            sftp.close()
            ssh.exec_command(f"chmod +x {script_path}")
            
        else:
            # Recalbox Daemon — ultra-lightweight, zero image processing
            daemon_code = f"""import subprocess
import time
import os

BROKER = "{matrix_ip}"
TOPIC = "recalbox/system/playing"

def parse_statefile():
    game = None
    system = None
    image = None
    state = "browsing"
    try:
        with open("/tmp/es_state.inf", "r") as f:
            for line in f:
                if line.startswith("GamePath="):
                    game = line.split("=", 1)[1].strip()
                elif line.startswith("SystemId="):
                    system = line.split("=", 1)[1].strip()
                elif line.startswith("ImagePath="):
                    image = line.split("=", 1)[1].strip()
                elif line.startswith("State="):
                    state = line.split("=", 1)[1].strip()
    except Exception:
        pass
    return game, system, image, state

def main():
    import socket
    import sys
    # Single instance lock: guarantee only one daemon runs at a time
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock_socket.bind(("127.0.0.1", 49132))
    except socket.error:
        print("Another daemon is already running, exiting...")
        sys.exit(1)
        
    print("Daemon started (v5 - lightweight)!", flush=True)
    time.sleep(5)
    last_game = None
    last_sent = None
    pending_since = 0
    curl_proc = None

    while True:
        try:
            rom_path, system, img, state = parse_statefile()
            if not rom_path:
                time.sleep(0.1)
                continue

            if rom_path != last_game:
                last_game = rom_path
                pending_since = time.time()

            elapsed = time.time() - pending_since
            if elapsed >= 0.15 and rom_path != last_sent:
                last_sent = rom_path
                gbase = os.path.splitext(os.path.basename(rom_path))[0]

                # Instantly send the game name via MQTT
                msg = '{{"status": "' + state + '", "game": "' + gbase + '", "system": "' + str(system) + '"}}'
                try:
                    subprocess.run(["mosquitto_pub", "-h", BROKER, "-t", TOPIC, "-m", msg], timeout=2, check=False)
                except subprocess.TimeoutExpired:
                    pass
        except Exception as e:
            print("Error: " + str(e), flush=True)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
"""
            launcher_code = """#!/bin/sh
# Only act on boot/startup (or manual run) to prevent spawning duplicates on every game launch
if [ -z "$1" ] || [ "$1" = "-action" -a "$2" = "start" ]; then
    # Kill any existing daemon to prevent ghost clones
    pkill -f arcadematrix_daemon.py || true
    # Start the fresh daemon
    python3 /recalbox/share/arcadematrix_daemon.py > /recalbox/share/userscripts/daemon.log 2>&1 &
fi
"""
            logging.info(f"Creating directory {target_dir}...")
            ssh.exec_command(f"mkdir -p {target_dir}")
            
            # Nuclear cleanup: remove ALL old scripts and kill ghost processes
            logging.info("Cleaning up ALL legacy scripts...")
            ssh.exec_command(f"cd {target_dir} && for f in *.sh; do case \"$f\" in 'arcadematrix_launcher(permanent).sh') ;; *) rm -f \"$f\" ;; esac; done")
            ssh.exec_command(f"rm -f {target_dir}/arcadematrix_daemon.py")
            ssh.exec_command("pkill -f recalbox_mqtt_status || true")
            ssh.exec_command("pkill -f arcadematrix_mqtt || true")
            ssh.exec_command("pkill -f arcadematrix_daemon.py || true")
            
            sftp = ssh.open_sftp()
            
            daemon_path = "/recalbox/share/arcadematrix_daemon.py"
            with sftp.file(daemon_path, "w") as f:
                f.write(daemon_code)
                
            launcher_path = f"{target_dir}/arcadematrix_launcher(permanent).sh"
            with sftp.file(launcher_path, "w") as f:
                f.write(launcher_code)
                
            sftp.close()
            ssh.exec_command(f"chmod +x {launcher_path}")
            # Also clean up the old one-shot script if it exists
            ssh.exec_command(f"rm -f {target_dir}/arcadematrix_mqtt.sh")
        
        logging.info("Rebooting target system...")
        ssh.exec_command("sleep 1 && reboot")
        
        return True, f"Successfully installed! {system_name} is now rebooting..."
        
    except Exception as e:
        logging.error(f"Error during installation: {e}")
        return False, f"Installation error: {str(e)}"
    finally:
        ssh.close()
