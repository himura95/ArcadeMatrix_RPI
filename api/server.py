import os
import threading
from flask import Flask, jsonify, request, send_from_directory
from core.config import Config
import logging

app = Flask(__name__, static_folder='www')
config = Config()
app_instance = None
_marquee_timer = None
_marquee_lock = threading.Lock()

def _apply_marquee():
    """Called after debounce period - triggers the actual display."""
    config.force_engine = 'marquee'
    config.reload_flag = True

def set_app_instance(instance):
    global app_instance, config
    app_instance = instance
    config = instance.config

# Routes that can change system state (reboot/shutdown/network/remote code install) - these are
# protected by an opt-in token (see Config.api_auth_enabled) since they are the highest-impact
# endpoints if the API were ever exposed beyond a trusted LAN.
_SENSITIVE_ROUTES = {'/api/wifi', '/api/mqtt/install', '/api/system/reboot', '/api/system/shutdown'}

@app.before_request
def _check_api_auth():
    if not config.api_auth_enabled:
        return None
    if request.path not in _SENSITIVE_ROUTES:
        return None
    supplied = request.headers.get('X-API-Token', '')
    if not supplied or supplied != config.api_token:
        return jsonify({'status': 'error', 'message': 'Missing or invalid X-API-Token header'}), 401
    return None

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/fonts', methods=['GET'])
def api_fonts():
    try:
        # Use os.getcwd() because Cython obfuscation breaks __file__ paths
        base_dir = os.getcwd()
        fonts_dir = os.path.join(base_dir, "fonts")
        fonts = [f for f in os.listdir(fonts_dir) if f.lower().endswith(('.ttf', '.otf', '.bdf'))]
    except Exception as e:
        logging.error(f"Failed to list fonts: {e}")
        fonts = []
    return jsonify(fonts)

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    global config
    if request.method == 'GET':
        return jsonify({
            'brightness_limit': config.matrix_brightness,
            'color_depth': 24, # Dummy
            'rotation': ",".join(config.idle_rotation),
            'clock_offset_x': config.time_offset_x,
            'clock_offset_y': config.time_offset_y,
            'date_offset_x': config.date_offset_x,
            'date_offset_y': config.date_offset_y,
            'weather_offset_x': config.weather_offset_x,
            'weather_offset_y': config.weather_offset_y,
            'clock_size': config.time_size,
            'clock_font': config.time_font,
            'clock_theme': config.time_theme,
            'clock_color_1': config.clock_color_1,
            'clock_color_2': config.clock_color_2,
            'format_24h': config.time_24h,
            'date_size': config.date_size,
            'date_font': config.date_font,
            'date_theme': config.date_theme,
            'date_format': config.date_format,
            'date_color_1': config.date_color_1,
            'date_color_2': config.date_color_2,
            'night_mode_enabled': config.standby_enabled,
            'turn_off_at': config.standby_turn_off,
            'wake_up_at': config.standby_wake_up,
            'matrix_brightness_night': config.matrix_brightness_night,
            'matrix_power': getattr(config, 'matrix_power', True),
            "matrix_brightness": config.matrix_brightness,
            "matrix_slowdown": config.matrix_slowdown,
            "matrix_rows": config.matrix_rows,
            "matrix_cols": config.matrix_cols,
            "matrix_chain": config.matrix_chain,
            "matrix_parallel": config.matrix_parallel,
            "matrix_mapping": config.matrix_mapping,
            "matrix_rgb_sequence": config.matrix_rgb_sequence,
            "matrix_pwm_bits": config.matrix_pwm_bits,
            "matrix_pwm_lsb_nanoseconds": config.matrix_pwm_lsb_nanoseconds,
            "mqtt_enabled": config.mqtt_enabled,
            'mqtt_broker': config.mqtt_broker,
            'mqtt_port': config.mqtt_port,
            'mqtt_user': config.mqtt_user,
            'clock_duration_sec': config.idle_clock_dur,
            'date_duration_sec': config.idle_date_dur,
            'weather_duration_sec': config.idle_weather_dur,
            'gifs_count': config.idle_gifs_count,
            'sprite_count': config.idle_sprite_count,
            'fighter_interval_sec': getattr(config, 'idle_fighter_interval', 10),
            'weather_api_key': config.weather_api,
            'weather_city': config.weather_city,
            'wifi_ssid': config.wifi_ssid,
            'wifi_pass': config.wifi_pass,
            'mqtt_user': config.mqtt_user,
            'mqtt_pass': config.mqtt_pass,
        })
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
        if 'brightness_limit' in data:
            config.matrix_brightness = int(data['brightness_limit'])
            if app_instance and app_instance.mw and app_instance.mw.matrix:
                app_instance.mw.matrix.brightness = config.matrix_brightness
                
        needs_restart = False
        if 'matrix_slowdown' in data:
            config.matrix_slowdown = int(data['matrix_slowdown'])
            needs_restart = True
        if 'matrix_rows' in data: 
            config.matrix_rows = int(data['matrix_rows'])
            needs_restart = True
        if 'matrix_cols' in data: 
            config.matrix_cols = int(data['matrix_cols'])
            needs_restart = True
        if 'matrix_chain' in data: 
            config.matrix_chain = int(data['matrix_chain'])
            needs_restart = True
        if 'matrix_parallel' in data: 
            config.matrix_parallel = int(data['matrix_parallel'])
            needs_restart = True
        if 'matrix_mapping' in data: 
            config.matrix_mapping = str(data['matrix_mapping'])
            needs_restart = True
        if 'matrix_rgb_sequence' in data:
            config.matrix_rgb_sequence = str(data['matrix_rgb_sequence'])
            needs_restart = True
        if 'matrix_pwm_bits' in data:
            config.matrix_pwm_bits = int(data['matrix_pwm_bits'])
            needs_restart = True
        if 'matrix_pwm_lsb_nanoseconds' in data:
            config.matrix_pwm_lsb_nanoseconds = int(data['matrix_pwm_lsb_nanoseconds'])
            needs_restart = True
            
        if 'rotation' in data:
            config.idle_rotation = [x.strip() for x in data['rotation'].split(',') if x.strip()]
        
        # TIME
        if 'clock_offset_x' in data: config.time_offset_x = int(data['clock_offset_x'])
        if 'clock_offset_y' in data: config.time_offset_y = int(data['clock_offset_y'])
        if 'clock_size' in data: config.time_size = int(data['clock_size'])
        if 'clock_font' in data: 
            val = str(data['clock_font'])
            if not val.isdigit():
                config.time_font = val
        if 'clock_theme' in data: config.time_theme = int(data['clock_theme'])
        if 'clock_color_1' in data: config.clock_color_1 = str(data['clock_color_1'])
        if 'clock_color_2' in data: config.clock_color_2 = str(data['clock_color_2'])
        if 'format_24h' in data: config.time_24h = bool(data['format_24h'])
        
        if 'timezone_iana' in data:
            tz_iana = data['timezone_iana']
            if tz_iana:
                import subprocess
                # Never interpolate user input into a shell string - pass as an argv list instead.
                subprocess.Popen(['sudo', 'timedatectl', 'set-timezone', str(tz_iana)], shell=False)

        # DATE
        if 'date_offset_x' in data: config.date_offset_x = int(data['date_offset_x'])
        if 'date_offset_y' in data: config.date_offset_y = int(data['date_offset_y'])
        if 'date_size' in data: config.date_size = int(data['date_size'])
        if 'date_font' in data: 
            val = str(data['date_font'])
            if not val.isdigit():
                config.date_font = val
        if 'date_theme' in data: config.date_theme = int(data['date_theme'])
        if 'date_format' in data: config.date_format = str(data['date_format'])
        if 'date_color_1' in data: config.date_color_1 = str(data['date_color_1'])
        if 'date_color_2' in data: config.date_color_2 = str(data['date_color_2'])
        
        # WEATHER
        if 'weather_offset_x' in data: config.weather_offset_x = int(data['weather_offset_x'])
        if 'weather_offset_y' in data: config.weather_offset_y = int(data['weather_offset_y'])
        if 'weather_api_key' in data: config.weather_api = data['weather_api_key']
        if 'weather_city' in data: config.weather_city = data['weather_city']
        
        # STANDBY
        if 'night_mode_enabled' in data: config.standby_enabled = bool(data['night_mode_enabled'])
        if 'turn_off_at' in data: config.standby_turn_off = data['turn_off_at']
        if 'wake_up_at' in data: config.standby_wake_up = data['wake_up_at']
        if 'matrix_brightness_night' in data: config.matrix_brightness_night = int(data['matrix_brightness_night'])
        
        # MQTT
        if 'mqtt_enable' in data: config.mqtt_enabled = bool(data['mqtt_enable'])
        if 'mqtt_broker' in data: config.mqtt_broker = data['mqtt_broker']
        if 'mqtt_port' in data: config.mqtt_port = int(data['mqtt_port'])
        if 'mqtt_user' in data: config.mqtt_user = data['mqtt_user']
        if 'mqtt_pass' in data: config.mqtt_pass = data['mqtt_pass']
        
        # DURATIONS
        if 'clock_duration_sec' in data: config.idle_clock_dur = int(data['clock_duration_sec'])
        if 'date_duration_sec' in data: config.idle_date_dur = int(data['date_duration_sec'])
        if 'weather_duration_sec' in data: config.idle_weather_dur = int(data['weather_duration_sec'])
        if 'gifs_count' in data: config.idle_gifs_count = int(data['gifs_count'])
        if 'sprite_count' in data: config.idle_sprite_count = int(data['sprite_count'])
        if 'fighter_interval_sec' in data: config.idle_fighter_interval = int(data['fighter_interval_sec'])
        
        config.save()
        config.reload_flag = True
        
        if needs_restart:
            # Run the restart command in background so we can return the response
            import subprocess
            subprocess.Popen("sleep 1 && sudo systemctl restart arcadematrix", shell=True)
            
        return jsonify({'status': 'success'})

@app.route('/api/playlists', methods=['GET'])
def api_playlists():
    # Return subdirectories in gifs/ folder
    try:
        res = {}
        if os.path.exists("gifs"):
            for d in os.listdir("gifs"):
                path = os.path.join("gifs", d)
                if os.path.isdir(path):
                    gifs_in_folder = [f for f in os.listdir(path) if f.lower().endswith('.gif')]
                    res[d] = {'path': path, 'count': len(gifs_in_folder)}
    except:
        res = {}
    return jsonify(res)

@app.route('/api/playlists/selected', methods=['GET'])
def api_playlists_selected():
    return jsonify({'playlists': config.selected_gifs})

@app.route('/api/playlists/save', methods=['POST'])
def api_playlists_save():
    data = request.json
    if data and 'playlists' in data:
        config.selected_gifs = data['playlists']
        config.save()
        config.force_engine = 'gifs'
        config.reload_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/sprites/playlists', methods=['GET'])
def api_sprites_playlists():
    return jsonify({})

@app.route('/api/sprites/playlists/selected', methods=['GET'])
def api_sprites_playlists_selected():
    return jsonify({'playlists': []})

@app.route('/api/sprites/playlists/save', methods=['POST'])
def api_sprites_playlists_save():
    return jsonify({'status': 'success'})

@app.route('/api/message', methods=['POST'])
def api_message():
    data = request.json
    config.message_payload = data
    config.force_engine = 'message'
    config.reload_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/clock', methods=['POST'])
def api_clock():
    data = request.json
    if 'clock_theme' in data:
        config.time_theme = int(data['clock_theme'])
        config.save()
        config.reload_flag = True
    return jsonify({'status': 'success'})

@app.route('/api/system_info', methods=['GET'])
def api_system_info():
    import psutil
    try:
        cpu_load = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Temp (Raspberry Pi specific)
        temp = 0.0
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
        except:
            pass
            
        return jsonify({
            'cpu_load': cpu_load,
            'ram_used_mb': ram.used // (1024*1024),
            'ram_total_mb': ram.total // (1024*1024),
            'ram_percent': ram.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_percent': disk.percent,
            'temperature_c': round(temp, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/wifi', methods=['POST'])
def api_wifi():
    data = request.json
    if not data or 'ssid' not in data or 'password' not in data:
        return jsonify({'status': 'error', 'message': 'Missing ssid or password'}), 400
        
    config.wifi_ssid = data['ssid']
    config.wifi_pass = data['password']
    config.wifi_configured = False # Set to false to trigger nmcli
    config.save()
    
    # Try connecting immediately.
    # IMPORTANT: never build this as a shell string (shell=True) - the SSID/password
    # come directly from user input and could otherwise be used for command injection.
    import subprocess
    cmd = ['sudo', 'nmcli', 'dev', 'wifi', 'connect', config.wifi_ssid, 'password', config.wifi_pass]
    result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    
    if result.returncode == 0:
        config.wifi_configured = True
        config.save()
        return jsonify({'status': 'success', 'message': 'Connected to Wi-Fi successfully!'})
    else:
        return jsonify({'status': 'error', 'message': f'Failed to connect: {result.stderr}'}), 500

@app.route('/api/marquee', methods=['POST'])
def api_marquee():
    global _marquee_timer
    if 'image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400

    try:
        from PIL import Image
        image = Image.open(file.stream).convert('RGB')
    except Exception as e:
        return jsonify({"status": "error", "message": f"Invalid image: {e}"}), 400

    # Store image in memory immediately, but debounce the display trigger
    config.image_obj = image
    config.image_path = None

    with _marquee_lock:
        if _marquee_timer is not None:
            _marquee_timer.cancel()
        _marquee_timer = threading.Timer(0.15, _apply_marquee)
        _marquee_timer.start()

    return jsonify({"status": "success", "message": "Marquee image received and displayed"})

@app.route('/api/mqtt/install', methods=['POST'])
def api_mqtt_install():
    data = request.json
    target_ip = data.get('ip')
    if not target_ip:
        return jsonify({'status': 'error', 'message': 'No IP provided'}), 400
        
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        matrix_ip = s.getsockname()[0]
    except Exception:
        matrix_ip = '127.0.0.1'
    finally:
        s.close()
        
    try:
        import core.ssh_installer as ssh_installer
        success, message = ssh_installer.install_sync_script(target_ip, matrix_ip)
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'status': 'error', 'message': message}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/reboot', methods=['POST'])
def api_reboot():
    import subprocess
    subprocess.Popen("sleep 1 && sudo reboot", shell=True)
    return jsonify({'status': 'success', 'message': 'Rebooting system...'})

@app.route('/api/system/shutdown', methods=['POST'])
def api_shutdown():
    import subprocess
    subprocess.Popen("sleep 1 && sudo shutdown now", shell=True)
    return jsonify({'status': 'success', 'message': 'Shutting down system...'})

@app.route('/api/system/power', methods=['POST'])
def api_power():
    data = request.json
    if data and 'state' in data:
        config.matrix_power = bool(data['state'])
        if not config.matrix_power:
            if app_instance and app_instance.mw:
                app_instance.mw.clear()
        config.reload_flag = True
    return jsonify({'status': 'success', 'matrix_power': config.matrix_power})

def run_server(port=8080):
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server(8080)
