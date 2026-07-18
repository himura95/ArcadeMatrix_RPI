import time
from PIL import Image, ImageDraw
from .base_renderer import BaseRenderer
from core.theme import draw_styled_text

class FlipRenderer(BaseRenderer):
    def __init__(self, config):
        super().__init__(config)
        self.prev_digits = None

    def _get_layout(self, text, font, scale_factor):
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        max_char_w = 0
        max_char_h = 0
        for char in "0123456789AMP ":
            try:
                left, top, right, bottom = draw.textbbox((0, 0), char, font=font)
                w = (right - left) * scale_factor
                h = (bottom - top) * scale_factor
                max_char_w = max(max_char_w, w)
                max_char_h = max(max_char_h, h)
            except Exception:
                max_char_w = max(max_char_w, 6 * scale_factor)
                max_char_h = max(max_char_h, 10 * scale_factor)
                
        if max_char_w == 0: max_char_w = 6 * scale_factor
        if max_char_h == 0: max_char_h = 10 * scale_factor
        
        panel_w = max(4, int(max_char_w + 2))
        panel_h = max(8, int(max_char_h + 4))
        spacing = 2
        
        total_w = 0
        for char in text:
            if char in [':', '/', '.', '-']:
                total_w += 2 + spacing
            else:
                total_w += panel_w + spacing
                
        if len(text) > 0:
            total_w -= spacing
            
        return panel_w, panel_h, spacing, total_w

    def _draw_static_frame(self, img, text, font, color1, color2, offset_x, offset_y, scale_factor=1.0):
        draw = ImageDraw.Draw(img)
        draw.fontmode = '1'
        
        panel_w, panel_h, spacing, total_w = self._get_layout(text, font, scale_factor)
        start_x = (self.config.matrix_width - total_w) // 2 + offset_x
        y_pos = (self.config.matrix_height - panel_h) // 2 + offset_y
        
        cx = start_x
        time_chars = list(text)
        
        for i, char in enumerate(time_chars):
            if char in [':', '/', '.', '-']:
                draw.rectangle([cx, y_pos + panel_h//3, cx + 1, y_pos + panel_h//3 + 1], fill=(255, 255, 255))
                draw.rectangle([cx, y_pos + 2*panel_h//3, cx + 1, y_pos + 2*panel_h//3 + 1], fill=(255, 255, 255))
                cx += 2 + spacing
                continue
                
            draw.rectangle([cx, y_pos, cx + panel_w - 1, y_pos + panel_h - 1], fill=(255, 255, 255))
            draw_styled_text(img, char, (cx + 1, y_pos + 1), font, 19, (0,0,0), (0,0,0), scale=scale_factor)
            mid_y = y_pos + panel_h // 2
            draw.line([(cx, mid_y), (cx + panel_w - 1, mid_y)], fill=(0, 0, 0), width=1)
            cx += panel_w + spacing
            
        return img

    def render(self, img, text, font, color1, color2, offset_x, offset_y, scale_factor=1.0):
        # We assume prev_digits exists, animation should have happened already
        return self._draw_static_frame(img, text, font, color1, color2, offset_x, offset_y, scale_factor)

    def animate(self, mw, prev_text, current_text, font, color1, color2, offset_x, offset_y, scale_factor=1.0):
        if self.prev_digits is None:
            self.prev_digits = [""] * len(current_text)
            
        time_chars = list(current_text)
        changed = [False] * len(time_chars)
        is_flipping = False
        
        for i in range(len(time_chars)):
            if i >= len(self.prev_digits) or time_chars[i] != self.prev_digits[i]:
                changed[i] = True
                is_flipping = True
                
        frames = []
        if is_flipping:
            panel_w, panel_h, spacing, total_w = self._get_layout(current_text, font, scale_factor)
            start_x = (self.config.matrix_width - total_w) // 2 + offset_x
            y_pos = (self.config.matrix_height - panel_h) // 2 + offset_y

            # 8 frames of animation
            for flip_frame in range(1, 9):
                anim_img = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), color=(0, 0, 0))
                anim_draw = ImageDraw.Draw(anim_img)
                anim_draw.fontmode = '1'
                
                cx = start_x
                for i, char in enumerate(time_chars):
                    if char in [':', '/', '.', '-']:
                        anim_draw.rectangle([cx, y_pos + panel_h//3, cx + 1, y_pos + panel_h//3 + 1], fill=(255, 255, 255))
                        anim_draw.rectangle([cx, y_pos + 2*panel_h//3, cx + 1, y_pos + 2*panel_h//3 + 1], fill=(255, 255, 255))
                        cx += 2 + spacing
                        continue
                        
                    is_flipping_panel = changed[i]
                    if is_flipping_panel:
                        shrink = flip_frame
                        if shrink > 4: shrink = 8 - flip_frame
                        shrink_px = int((shrink / 4.0) * (panel_h / 2))
                        
                        top_y = y_pos + shrink_px
                        bottom_y = max(top_y, y_pos + panel_h - shrink_px - 1)
                        anim_draw.rectangle([cx, top_y, cx + panel_w - 1, bottom_y], fill=(255, 255, 255))
                        mid_y = y_pos + panel_h // 2
                        anim_draw.line([(cx, mid_y), (cx + panel_w - 1, mid_y)], fill=(0, 0, 0), width=1)
                    else:
                        anim_draw.rectangle([cx, y_pos, cx + panel_w - 1, y_pos + panel_h - 1], fill=(255, 255, 255))
                        draw_styled_text(anim_img, char, (cx + 1, y_pos + 1), font, 19, (0,0,0), (0,0,0), scale=scale_factor)
                        mid_y = y_pos + panel_h // 2
                        anim_draw.line([(cx, mid_y), (cx + panel_w - 1, mid_y)], fill=(0, 0, 0), width=1)
                        
                    cx += panel_w + spacing
                    
                frames.append(anim_img)
                
        self.prev_digits = time_chars.copy()
        return frames
