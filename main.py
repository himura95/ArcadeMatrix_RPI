import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    with open("crash.log", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
sys.excepthook = handle_exception

import time
import logging
import threading
import os
import subprocess
import socket
from PIL import Image, ImageDraw, ImageFont
from core.config import Config
from core.matrix import MatrixWrapper
from core.rotation import RotationManager
from api.server import run_server, set_app_instance

# Optional: paho-mqtt for Batocera integration
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

class ArcadeMatrixApp:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.config = Config()
        self.mw = MatrixWrapper(self.config)
        self.rotation_manager = RotationManager(self.mw, self.config)
        self.mqtt_client = None

    def _on_mqtt_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        logging.info(f"MQTT Message received on {msg.topic}: {payload}")
        
        import json
        try:
            data = json.loads(payload)
            if data.get("status") == "playing":
                game_name = data.get("game", "Unknown Game")
                sys_name = data.get("system", "")
                
                text = f"Playing {game_name}"
                if sys_name:
                    text += f" [{sys_name}]"
                
                # Interrupt current rotation and scroll the game name
                self.config.message_payload = {
                    'text': text,
                    'color': 0xFFFF, # White
                    'size': 2,
                    'direction': 'rtl',
                    'speed': 30,
                    'timeoutSeconds': 30
                }
                self.config.force_engine = 'message'
                self.config.reload_flag = True
        except Exception as e:
            logging.error(f"Failed to parse MQTT json: {e}")

    def _setup_mqtt(self):
        if not MQTT_AVAILABLE or not self.config.mqtt_enabled:
            return
            
        logging.info(f"Connecting to MQTT broker at {self.config.mqtt_broker}:{self.config.mqtt_port}")
        try:
            # Handle newer paho-mqtt versions without warnings
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=self.config.mqtt_device)
        except AttributeError:
            self.mqtt_client = mqtt.Client(client_id=self.config.mqtt_device)
        
        if self.config.mqtt_user and self.config.mqtt_pass:
            self.mqtt_client.username_pw_set(self.config.mqtt_user, self.config.mqtt_pass)
            
        self.mqtt_client.on_message = self._on_mqtt_message
        
        try:
            self.mqtt_client.connect(self.config.mqtt_broker, self.config.mqtt_port, 60)
            if self.config.mqtt_topic_bato:
                self.mqtt_client.subscribe(self.config.mqtt_topic_bato)
            if self.config.mqtt_topic_recal:
                self.mqtt_client.subscribe(self.config.mqtt_topic_recal)
            self.mqtt_client.loop_start()
            logging.info("MQTT connected and subscribed.")
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}")

    def _setup_wifi(self):
        if self.config.wifi_ssid and not self.config.wifi_configured:
            logging.info(f"Attempting to configure Wi-Fi for SSID: {self.config.wifi_ssid}")
            try:
                # Set country code BEFORE unblocking to satisfy hardware regulations
                subprocess.run('sudo raspi-config nonint do_wifi_country FR', shell=True)
                subprocess.run('sudo rfkill unblock wifi', shell=True)
                
                # Give the Wi-Fi adapter a few seconds to turn on and scan
                import time
                time.sleep(2)
                
                # Create a pure NetworkManager profile to avoid any nmcli scan race conditions
                safe_ssid = self.config.wifi_ssid.replace(" ", "_").replace("/", "_")
                nm_content = f"""[connection]
id={safe_ssid}
type=wifi
autoconnect=true

[wifi]
mode=infrastructure
ssid={self.config.wifi_ssid}

[wifi-security]
key-mgmt=wpa-psk
psk={self.config.wifi_pass}

[ipv4]
method=auto

[ipv6]
addr-gen-mode=default
method=auto
"""
                profile_path = f"/etc/NetworkManager/system-connections/{safe_ssid}.nmconnection"
                with open(profile_path, "w") as f:
                    f.write(nm_content)
                
                os.chmod(profile_path, 0o600)
                
                # Reload NetworkManager and force activation
                subprocess.run('sudo nmcli connection reload', shell=True)
                time.sleep(1)
                subprocess.run(f'sudo nmcli connection up "{safe_ssid}"', shell=True)
                
                logging.info("Wi-Fi profile generated and activated successfully.")
                self.config.wifi_configured = True
                self.config.save()
            except Exception as e:
                logging.error(f"Exception during Wi-Fi setup: {e}")

    def _get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def _show_ip(self):
        ip_addr = self._get_ip()
        logging.info(f"Local IP Address: {ip_addr}")
        try:
            img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), "black")
            draw = ImageDraw.Draw(img)
            draw.fontmode = '1'
            # Try to load a small font, fallback to default
            try:
                font = ImageFont.truetype("fonts/PressStart2P.ttf", 6)
            except:
                font = ImageFont.load_default()
            
            draw.text((2, 2), "IP Address:", font=font, fill=(0, 255, 0))
            draw.text((2, 14), ip_addr, font=font, fill=(255, 255, 255))
            
            self.mw.set_image(img)
            time.sleep(5)
        except Exception as e:
            logging.error(f"Failed to display IP: {e}")

    def run(self):
        # 0. Setup Wi-Fi if needed
        self._setup_wifi()

        # 0.5 Show IP on Matrix
        self._show_ip()

        # 1. Start Web Server in a separate thread
        set_app_instance(self)
        web_thread = threading.Thread(target=run_server, args=(8080,), daemon=True)
        web_thread.start()

        # 2. Setup MQTT
        self._setup_mqtt()

        # 3. Start Main Rotation Loop (blocking)
        try:
            self.rotation_manager.start_loop()
        except KeyboardInterrupt:
            logging.info("Exiting ArcadeMatrix RPi...")
        finally:
            self.mw.clear()
            if self.mqtt_client:
                self.mqtt_client.loop_stop()

if __name__ == "__main__":
    app = ArcadeMatrixApp()
    app.run()
