import time
import logging
import datetime
from engines.clock import ClockEngine
from engines.date import DateEngine
from engines.weather import WeatherEngine
from engines.gif import GifEngine
from engines.fighter import FighterEngine
from engines.network import NetworkEngine


def is_night_time(now, off_str, wake_str):
    """Pure helper (no hardware/config dependency, easy to unit test): returns True if `now`
    (a datetime.time) falls within the [off_str, wake_str) standby/night window, where both
    strings are "HH:MM" formatted. Handles overnight windows that wrap past midnight (e.g.
    off_str="23:00", wake_str="07:00") by treating them as off_time > wake_time.
    Fails safe (returns False, i.e. "not night") if either string is malformed/unparseable,
    so a config typo never accidentally forces the display into permanent standby.
    """
    try:
        off_time = datetime.datetime.strptime(off_str, "%H:%M").time()
        wake_time = datetime.datetime.strptime(wake_str, "%H:%M").time()
    except (ValueError, TypeError):
        return False

    if off_time > wake_time:
        return now >= off_time or now < wake_time
    else:
        return now >= off_time and now < wake_time


class RotationManager:
    def __init__(self, matrix_wrapper, config):
        self.mw = matrix_wrapper
        self.config = config
        self.fighter_engine = FighterEngine(config)
        self.engines = {
            'clock': ClockEngine(matrix_wrapper, config, self.fighter_engine),
            'date': DateEngine(matrix_wrapper, config, self.fighter_engine),
            'weather': WeatherEngine(matrix_wrapper, config, self.fighter_engine),
            'network': NetworkEngine(matrix_wrapper, config, self.fighter_engine),
            'gifs': GifEngine(matrix_wrapper, config),
            'message': __import__('engines.message', fromlist=['MessageEngine']).MessageEngine(matrix_wrapper, config),
            'marquee': __import__('engines.marquee', fromlist=['MarqueeEngine']).MarqueeEngine(matrix_wrapper, config)
        }

    def start_loop(self):
        logging.info("Starting idle rotation loop...")
        while True:
            # Check manual power state first
            if not getattr(self.config, 'matrix_power', True):
                self.mw.clear()
                time.sleep(1)
                continue
                
            # Check standby (night mode)
            is_night = False
            if self.config.standby_enabled:
                now = datetime.datetime.now().time()
                is_night = is_night_time(now, self.config.standby_turn_off, self.config.standby_wake_up)
                    
            if is_night:
                if getattr(self.config, 'matrix_brightness_night', 10) == 0:
                    self.mw.clear()
                    time.sleep(5)
                    continue
                else:
                    if self.mw.matrix:
                        self.mw.matrix.brightness = self.config.matrix_brightness_night
            else:
                if self.mw.matrix and getattr(self.config, 'matrix_brightness', 50) != self.mw.matrix.brightness:
                    self.mw.matrix.brightness = self.config.matrix_brightness

            rotation_list = self.config.idle_rotation
            if getattr(self.config, 'mqtt_enabled', False):
                rotation_list = ['waiting']
            elif not rotation_list:
                logging.warning("No rotation configured. Defaulting to clock.")
                rotation_list = ['clock']
                
            for engine_name in rotation_list:
                # Check power state mid-rotation
                if not getattr(self.config, 'matrix_power', True):
                    break
                    
                # Intercept forced jump
                if getattr(self.config, 'force_engine', None):
                    engine_name = self.config.force_engine
                    self.config.force_engine = None
                    self.config.reload_flag = False
                    
                if getattr(self.config, 'reload_flag', False):
                    self.config.reload_flag = False
                    # Completely recreate engines so internal state (e.g. animated clocks) resets
                    self.engines = {
                        'clock': ClockEngine(self.mw, self.config, self.fighter_engine),
                        'date': DateEngine(self.mw, self.config, self.fighter_engine),
                        'weather': WeatherEngine(self.mw, self.config, self.fighter_engine),
                        'network': NetworkEngine(self.mw, self.config, self.fighter_engine),
                        'gifs': GifEngine(self.mw, self.config),
                        'message': __import__('engines.message', fromlist=['MessageEngine']).MessageEngine(self.mw, self.config),
                        'marquee': __import__('engines.marquee', fromlist=['MarqueeEngine']).MarqueeEngine(self.mw, self.config)
                    }
                    break
                    
                engine_name = engine_name.strip()
                if engine_name not in self.engines and engine_name != 'waiting':
                    logging.warning(f"Unknown engine: {engine_name}")
                    continue
                
                # Run the engine for its configured duration or count
                is_single = (len(rotation_list) == 1)
                
                if engine_name == 'waiting':
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), "black")
                    draw = ImageDraw.Draw(img)
                    draw.text((4, self.config.matrix_height // 2 - 8), "Waiting for", fill=(128, 128, 128))
                    draw.text((14, self.config.matrix_height // 2 + 2), "Marquee...", fill=(128, 128, 128))
                    self.mw.set_image(img)
                    time.sleep(2)
                    continue
                    
                engine = self.engines[engine_name]
                
                if engine_name == 'clock':
                    engine.run(86400 if is_single else self.config.idle_clock_dur)
                elif engine_name == 'date':
                    engine.run(86400 if is_single else self.config.idle_date_dur)
                elif engine_name == 'weather':
                    engine.run(86400 if is_single else self.config.idle_weather_dur)
                elif engine_name == 'network':
                    engine.run(86400 if is_single else 10)
                elif engine_name == 'gifs':
                    engine.run(self.config.idle_gifs_count)
                elif engine_name == 'message':
                    engine.run()
                elif engine_name == 'marquee':
                    engine.run(1)
                    
                # Small pause between engines for smooth transition
                if not is_single:
                    self.mw.clear()
                    time.sleep(0.5)
