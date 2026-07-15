import time
import requests
import logging
import os
from PIL import Image, ImageDraw, ImageFont

class WeatherEngine:
    def __init__(self, matrix_wrapper, config, fighter_engine=None):
        self.mw = matrix_wrapper
        self.config = config
        self.fighter_engine = fighter_engine
        self.last_fetch_time = 0
        self.cache_duration = 600  # 10 minutes cache
        self.weather_data = None
        self.font = ImageFont.load_default()
        
    def _fetch_weather(self):
        if not self.config.weather_api or not self.config.weather_city:
            logging.warning("Weather API key or city not configured.")
            return False
            
        current_time = time.time()
        if self.weather_data and (current_time - self.last_fetch_time < self.cache_duration):
            return True
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.config.weather_city}&appid={self.config.weather_api}&units=metric"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                temp = int(round(data['main']['temp']))
                icon = data['weather'][0]['icon']
                
                self.weather_data = {
                    'temp': f"{temp}°C",
                    'icon': icon
                }
                self.last_fetch_time = current_time
                logging.info(f"Weather updated: {self.weather_data['temp']}, {self.weather_data['icon']}")
                return True
            else:
                logging.error(f"Weather API error: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Failed to fetch weather: {e}")
            return False

    def run(self, duration_sec):
        logging.info(f"Starting WeatherEngine for {duration_sec}s")
        if not self._fetch_weather():
            time.sleep(2)
            return

        start_time = time.time()
        canvas = self.mw.get_canvas()
        if not canvas:
            return
            
        # load icon if available
        icon_path = f"weather_icons/{self.weather_data['icon']}.png"
        
        # Download icon if it doesn't exist
        if not os.path.exists(icon_path):
            os.makedirs("weather_icons", exist_ok=True)
            url = f"http://openweathermap.org/img/wn/{self.weather_data['icon']}@2x.png"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                logging.error(f"Failed to download weather icon: {e}")

        icon_img = None
        if os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path).convert('RGBA')
                # scale icon according to matrix height (leave some padding)
                icon_size = self.config.matrix_height - 4
                icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            except Exception as e:
                logging.error(f"Could not load weather icon {icon_path}: {e}")

        # Choose a nice font
        try:
            # Scale font size based on matrix height
            font_size = 14 if self.config.matrix_height <= 32 else 24
            font = ImageFont.truetype("fonts/PressStart2P.ttf", font_size)
        except:
            font = self.font

        while time.time() - start_time < duration_sec:
            if getattr(self.config, 'reload_flag', False):
                break
            img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.fontmode = '1'
            
            temp_str = self.weather_data['temp']
            try:
                bbox = self.font.getbbox(temp_str)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                try:
                    text_width, text_height = draw.textsize(temp_str, font=self.font)
                except:
                    text_width, text_height = 30, 10
            
            if icon_img:
                icon_x = self.config.weather_offset_x + 2
                icon_y = (self.config.matrix_height - icon_img.height) // 2 + self.config.weather_offset_y
                img.paste(icon_img, (icon_x, icon_y), icon_img)
                
                text_x = icon_x + icon_img.width + 4
                text_y = (self.config.matrix_height - text_height) // 2 + self.config.weather_offset_y
            else:
                # No icon, center text
                text_x = (self.config.matrix_width - text_width) // 2 + self.config.weather_offset_x
                text_y = (self.config.matrix_height - text_height) // 2 + self.config.weather_offset_y
                
            draw.text((text_x, text_y), temp_str, font=self.font, fill=(255, 255, 255))
            
            if self.fighter_engine:
                img = self.fighter_engine.tick(img)
            
            canvas.SetImage(img)
            canvas = self.mw.swap_canvas(canvas)
            # Update faster if fighter engine is enabled
            fast_update = self.fighter_engine and self.config.idle_sprite_count > 0
            time.sleep(0.04 if fast_update else 1)
