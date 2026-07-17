import time
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging
import os
from core.theme import load_font, draw_styled_text, get_theme_colors
from engines.renderers import get_renderer

class DateEngine:
    def __init__(self, matrix_wrapper, config, fighter_engine=None):
        self.mw = matrix_wrapper
        self.config = config
        self.fighter_engine = fighter_engine

    def _get_date_string(self):
        now = datetime.now()
        fmt = self.config.date_format.replace("DD", "%d").replace("MM", "%m").replace("YYYY", "%Y")
        return now.strftime(fmt)

    def run(self, duration_sec):
        logging.info(f"Starting DateEngine for {duration_sec}s")
        start_time = time.time()
        
        canvas = self.mw.get_canvas()
        if not canvas:
            return
            
        # Size and scale logic
        is_bdf = self.config.date_font.lower().endswith('.bdf')
        if is_bdf:
            font_size = 16
            scale_factor = self.config.date_size
        else:
            font_size = self.config.date_size
            scale_factor = 1

        font = load_font(self.config.date_font, font_size)
        renderer = get_renderer(self.config.date_theme, self.config)
        prev_date_str = ""
            
        while time.time() - start_time < duration_sec:
            if getattr(self.config, 'reload_flag', False):
                break
            
            date_str = self._get_date_string()
            
            if renderer.animate(self.mw, prev_date_str, date_str, font, self.config.date_color_1, self.config.date_color_2, self.config.date_offset_x, self.config.date_offset_y, scale_factor):
                pass
                
            prev_date_str = date_str
            
            img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), color=(0, 0, 0))
            img = renderer.render(img, date_str, font, self.config.date_theme, self.config.date_color_1, self.config.date_color_2, self.config.date_offset_x, self.config.date_offset_y, scale_factor)
                
            if self.fighter_engine:
                img = self.fighter_engine.tick(img)
                
            canvas.SetImage(img)
            canvas = self.mw.swap_canvas(canvas)
            
            # Update faster if cyberpunk, matrix theme, or fighter engine is enabled
            fast_update = self.config.date_theme in [18, 21] or (self.fighter_engine and self.config.idle_sprite_count > 0)
            time.sleep(0.04 if fast_update else 1)
