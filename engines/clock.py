import time
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import logging
from core.theme import load_font, draw_styled_text, get_theme_colors
from engines.clocks.pong_clock import PongClock
from engines.clocks.tetris_clock import TetrisClock
from engines.clocks.word_clock import WordClock
from engines.clocks.binary_clock import BinaryClock
from engines.clocks.pacman_clock import PacManClock
from engines.clocks.versus_clock import VersusClock
from engines.clocks.slot_machine_clock import SlotMachineClock
from engines.renderers import get_renderer

class ClockEngine:
    def __init__(self, matrix_wrapper, config, fighter_engine=None):
        self.mw = matrix_wrapper
        self.config = config
        self.fighter_engine = fighter_engine
        self.drops = []
        self._init_drops()
        
        self.pong_clock = PongClock(config.matrix_width, config.matrix_height)
        self.tetris_clock = TetrisClock(config.matrix_width, config.matrix_height)
        self.word_clock = WordClock(config.matrix_width, config.matrix_height)
        self.binary_clock = BinaryClock(config.matrix_width, config.matrix_height)
        self.pacman_clock = PacManClock(config.matrix_width, config.matrix_height)
        self.versus_clock = VersusClock(config.matrix_width, config.matrix_height)
        self.slot_clock = SlotMachineClock(config.matrix_width, config.matrix_height)

    def _init_drops(self):
        # Background resources are now managed by renderers (CyberpunkRenderer, TrueMatrixRenderer)
        pass

    def _get_time_string(self):
        now = datetime.now()
        if self.config.time_24h:
            return now.strftime("%H:%M:%S")
        else:
            return now.strftime("%I:%M:%S %p")

    def run(self, duration_sec):
        logging.info(f"Starting ClockEngine for {duration_sec}s")
        start_time = time.time()
        
        canvas = self.mw.get_canvas()
        if not canvas:
            return
            
        # Size and scale logic
        is_bdf = self.config.time_font.lower().endswith('.bdf')
        if is_bdf:
            font_size = 16  # BDF ignores this, but we pass something safe
            scale_factor = self.config.time_size
        else:
            font_size = self.config.time_size
            scale_factor = 1

        font = load_font(self.config.time_font, font_size)
        renderer = get_renderer(self.config.time_theme, self.config)
        prev_time_str = ""
            
        while time.time() - start_time < duration_sec:
            if getattr(self.config, 'reload_flag', False):
                break
            
            time_str = self._get_time_string()
            
            anim_frames = renderer.animate(self.mw, prev_time_str, time_str, font, self.config.clock_color_1, self.config.clock_color_2, self.config.time_offset_x, self.config.time_offset_y, scale_factor)
            if anim_frames:
                for anim_img in anim_frames:
                    if self.fighter_engine:
                        anim_img = self.fighter_engine.tick(anim_img)
                    canvas.SetImage(anim_img)
                    canvas = self.mw.swap_canvas(canvas)
                    time.sleep(0.02)
                
            prev_time_str = time_str
            
            img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), color=(0, 0, 0))
            
            if self.config.time_theme == 22:
                # Pong Clock
                img = self.pong_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, scale_factor=scale_factor)
            elif self.config.time_theme == 23 or self.config.time_theme == 29:
                # Tetris Drop Clock (23=Multicolor, 29=Gameboy)
                is_gb = (self.config.time_theme == 29)
                img = self.tetris_clock.tick(img, time_str, font, self.config.time_offset_x, self.config.time_offset_y, is_gameboy=is_gb, scale_factor=scale_factor)
            elif self.config.time_theme == 24:
                # Word Clock
                img = self.word_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, scale_factor=scale_factor)
            elif self.config.time_theme == 25:
                # Binary Clock
                img = self.binary_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, scale_factor=scale_factor)
            elif self.config.time_theme == 26:
                # Pac-Man Clock
                img = self.pacman_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, scale_factor=scale_factor)
            elif self.config.time_theme == 27:
                # Versus Health Bar Clock
                img = self.versus_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, scale_factor=scale_factor)
            elif self.config.time_theme == 28:
                # Slot Machine Clock
                img = self.slot_clock.tick(img, time_str, font, self.config.clock_color_1, self.config.clock_color_2, self.config.time_offset_x, self.config.time_offset_y, scale_factor=scale_factor)
            elif self.config.time_theme >= 0 and self.config.time_theme <= 21:
                # Delegate text drawing and backgrounds to the generic renderer
                img = renderer.render(img, time_str, font, self.config.time_theme, self.config.clock_color_1, self.config.clock_color_2, self.config.time_offset_x, self.config.time_offset_y, scale_factor=scale_factor)
                
            if self.fighter_engine:
                img = self.fighter_engine.tick(img)
                
            canvas.SetImage(img)
            canvas = self.mw.swap_canvas(canvas)
            
            # Update faster if cyberpunk, matrix theme, pong, tetris, pacman, slots, or gameboy tetris is enabled
            fast_update = self.config.time_theme in [18, 21, 22, 23, 26, 28, 29] or (self.fighter_engine and self.config.idle_sprite_count > 0)
            time.sleep(0.04 if fast_update else 1)
