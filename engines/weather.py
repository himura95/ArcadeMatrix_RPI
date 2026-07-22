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
        self.cache_duration = 1800  # 30 minutes cache for forecasts
        self.forecasts = []
        self.font = ImageFont.load_default()
        
    def _fetch_weather(self):
        if not self.config.weather_api or not self.config.weather_city:
            logging.warning("Weather API key or city not configured.")
            return False
            
        current_time = time.time()
        if self.forecasts and (current_time - self.last_fetch_time < self.cache_duration):
            return True
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.config.weather_city}&appid={self.config.weather_api}&units=metric"
            if getattr(self.config, 'weather_lang', ''):
                url += f"&lang={self.config.weather_lang}"
                
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Parse 3 days:
                # data['list'] contains 3-hour forecasts.
                # We want: Current (index 0), Tomorrow (~24h later -> index 8), Day After (~48h later -> index 16)
                self.forecasts = []
                
                lang = getattr(self.config, 'weather_lang', 'en').lower()
                if not lang:
                    lang = 'en'
                    
                if lang == "fr":
                    days = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]
                    labels = ["AUJ.", "DEMN", "DAY3"]
                elif lang == "es":
                    days = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
                    labels = ["HOY", "MANA", "DAY3"]
                else:
                    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                    labels = ["TODAY", "TMRW", "DAY3"]
                
                import datetime
                now_dt = datetime.datetime.now()
                
                for idx, label in zip([0, 8, 16], labels):
                    if idx < len(data['list']):
                        item = data['list'][idx]
                        temp = int(round(item['main']['temp']))
                        icon = item['weather'][0]['icon']
                        
                        if label == "DAY3":
                            day_idx = (now_dt.weekday() + 2) % 7
                            label = days[day_idx]
                            
                        self.forecasts.append({
                            'temp': f"{temp}°C",
                            'icon': icon,
                            'label': label
                        })
                        
                self.last_fetch_time = current_time
                logging.info(f"Weather forecast updated: {len(self.forecasts)} days fetched.")
                return True
            else:
                logging.error(f"Weather API error: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Failed to fetch weather: {e}")
            return False

    def _get_icon(self, icon_name, icon_size):
        icon_path = f"weather_icons/{icon_name}.png"
        
        if not os.path.exists(icon_path):
            os.makedirs("weather_icons", exist_ok=True)
            url = f"http://openweathermap.org/img/wn/{icon_name}@2x.png"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                logging.error(f"Failed to download weather icon: {e}")
                return None

        if os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path).convert('RGBA')
                bbox = icon_img.getbbox()
                if bbox:
                    icon_img = icon_img.crop(bbox)
                icon_img = icon_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                return icon_img
            except Exception as e:
                logging.error(f"Could not load weather icon {icon_path}: {e}")
        return None

    def run(self, duration_sec):
        logging.info(f"Starting WeatherEngine for {duration_sec}s")
        if not self._fetch_weather() or not self.forecasts:
            time.sleep(2)
            return

        start_time = time.time()
        canvas = self.mw.get_canvas()
        if not canvas:
            return
            
        # Layout metrics
        mw = self.config.matrix_width
        mh = self.config.matrix_height
        icon_size = mh - 4
        
        # Load fonts
        try:
            # Main font for temp
            temp_font_size = 14 if mh <= 32 else 24
            temp_font = ImageFont.truetype("fonts/PressStart2P.ttf", temp_font_size)
            
            # Smaller font for day label (AUJ, DEM)
            label_font_size = 8 if mh <= 32 else 12
            label_font = ImageFont.truetype("fonts/PressStart2P.ttf", label_font_size)
        except:
            temp_font = self.font
            label_font = self.font

        # Pre-render the panorama (Slide 1, Slide 2, Slide 3, and Slide 1 again for wrap-around)
        num_slides = len(self.forecasts)
        panorama_w = mw * (num_slides + 1)
        panorama = Image.new('RGB', (panorama_w, mh), color=(0, 0, 0))
        draw_pan = ImageDraw.Draw(panorama)
        
        slides_to_draw = self.forecasts + [self.forecasts[0]]
        
        for i, forecast in enumerate(slides_to_draw):
            base_x = i * mw
            
            icon_img = self._get_icon(forecast['icon'], icon_size)
            
            if icon_img:
                icon_x = base_x + self.config.weather_offset_x + 2
                icon_y = (mh - icon_img.height) // 2 + self.config.weather_offset_y
                panorama.paste(icon_img, (icon_x, icon_y), icon_img)
                text_x = icon_x + icon_img.width + 2
            else:
                text_x = base_x + self.config.weather_offset_x + 2
                
            # Draw label (AUJ)
            label_str = forecast['label']
            try:
                label_h = label_font.getbbox(label_str)[3] - label_font.getbbox(label_str)[1]
            except:
                label_h = 8
                
            draw_pan.text((text_x, 2 + self.config.weather_offset_y), label_str, font=label_font, fill=(180, 180, 255))
            
            # Draw Temp
            temp_str = forecast['temp']
            draw_pan.text((text_x, 2 + label_h + 4 + self.config.weather_offset_y), temp_str, font=temp_font, fill=(255, 255, 255))

        # Animation timing
        slide_duration = 5.0
        transition_duration = 1.0
        cycle_time = (slide_duration + transition_duration) * num_slides

        while time.time() - start_time < duration_sec:
            if getattr(self.config, 'reload_flag', False):
                break
                
            t = (time.time() - start_time) % cycle_time
            
            # Determine scroll x
            slide_idx = int(t / (slide_duration + transition_duration))
            local_t = t % (slide_duration + transition_duration)
            
            if local_t < slide_duration:
                # Static
                x_scroll = slide_idx * mw
                fast_update = False
            else:
                # Transitioning to next slide
                progress = (local_t - slide_duration) / transition_duration
                # smooth easing (ease in-out)
                ease = progress * progress * (3 - 2 * progress)
                x_scroll = int((slide_idx + ease) * mw)
                fast_update = True
                
            # Force fast update if fighters are present
            if self.fighter_engine and self.config.idle_sprite_count > 0:
                fast_update = True
                
            # Crop view from panorama
            view = panorama.crop((x_scroll, 0, x_scroll + mw, mh))
            img = Image.new('RGB', (mw, mh))
            img.paste(view, (0, 0))
            
            if self.fighter_engine:
                img = self.fighter_engine.tick(img)
            
            canvas.SetImage(img)
            canvas = self.mw.swap_canvas(canvas)
            
            time.sleep(0.04 if fast_update else 0.5)
