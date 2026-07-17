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
            # Recalbox Daemon
            daemon_code = f"""import subprocess
import time
import os
import xml.etree.ElementTree as ET

BROKER = "{matrix_ip}"
TOPIC = "recalbox/system/playing"

def parse_statefile():
    game = None
    system = None
    if os.path.exists("/tmp/statefile"):
        with open("/tmp/statefile", "r") as f:
            for line in f:
                if line.lower().startswith("game=") or line.lower().startswith("rom="):
                    game = line.split("=", 1)[1].strip()
                elif line.lower().startswith("system="):
                    system = line.split("=", 1)[1].strip()
    return game, system

def find_image(rom_path, system):
    if not rom_path: return None
    rom_dir = os.path.dirname(rom_path)
    gamelist_path = os.path.join(rom_dir, "gamelist.xml")
    if os.path.exists(gamelist_path):
        try:
            tree = ET.parse(gamelist_path)
            root = tree.getroot()
            rom_basename = os.path.basename(rom_path)
            for game in root.findall('game'):
                path_node = game.find('path')
                if path_node is not None and path_node.text and path_node.text.endswith(rom_basename):
                    image_node = game.find('image')
                    if image_node is not None and image_node.text:
                        img_rel = image_node.text
                        if img_rel.startswith("./"): img_rel = img_rel[2:]
                        img_abs = os.path.join(rom_dir, img_rel)
                        if os.path.exists(img_abs): return img_abs
        except Exception:
            pass
            
    # Fallback search
    game_base = os.path.splitext(os.path.basename(rom_path))[0]
    for ext in ['png', 'jpg', 'gif']:
        for pre in ["images/", "downloaded_images/", "media/marquees/", "media/images/", "media/wheels/", ""]:
            for suf in ["-marquee", "-wheel", "-image", "-thumb", ""]:
                p = os.path.join(rom_dir, f"{{pre}}{{game_base}}{{suf}}.{{ext}}")
                if os.path.exists(p): return p
    return None

def main():
    time.sleep(5)
    cmd = ["mosquitto_sub", "-h", "127.0.0.1", "-t", "/Recalbox/EmulationStation/Event"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    except Exception:
        return
        
    for line in iter(proc.stdout.readline, ''):
        event = line.strip().lower()
        if event in ["gamelistbrowsing", "rungame"]:
            time.sleep(0.1)
            rom_path, system = parse_statefile()
            if not rom_path: continue
            
            img = find_image(rom_path, system)
            status = "playing" if event == "rungame" else "browsing"
            gbase = os.path.splitext(os.path.basename(rom_path))[0]
            
            if img:
                subprocess.Popen(["curl", "-s", "-X", "POST", "-F", f"image=@{{img}}", f"http://{{BROKER}}:8080/api/marquee"])
            else:
                msg = '{{"status": "' + status + '", "game": "' + gbase + '", "system": "' + system + '"}}'
                subprocess.Popen(["mosquitto_pub", "-h", BROKER, "-t", TOPIC, "-m", msg])
                
        elif event in ["quitgame"]:
            subprocess.Popen(["mosquitto_pub", "-h", BROKER, "-t", TOPIC, "-m", '{{"status": "stopped"}}'])

if __name__ == "__main__":
    main()
"""
            launcher_code = """#!/bin/sh
python3 /recalbox/share/userscripts/arcadematrix_daemon.py &
"""
            logging.info(f"Creating directory {target_dir}...")
            ssh.exec_command(f"mkdir -p {target_dir}")
            
            sftp = ssh.open_sftp()
            
            daemon_path = f"{target_dir}/arcadematrix_daemon.py"
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
