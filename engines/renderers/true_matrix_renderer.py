import random
from PIL import Image, ImageDraw, ImageFont
from .base_renderer import BaseRenderer
from core.theme import load_font

class TrueMatrixRenderer(BaseRenderer):
    def __init__(self, config):
        super().__init__(config)
        self.matrix_cols = [random.randint(-self.config.matrix_height, -10) for _ in range(0, self.config.matrix_width, 10)]
        self.matrix_img = None
        try:
            self.matrix_font = load_font('DotGothic16.ttf', 12)
        except:
            self.matrix_font = ImageFont.load_default()

    def render(self, img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor=1.0):
        # Draw background
        if self.matrix_img is None:
            self.matrix_img = Image.new('RGBA', img.size, (0,0,0,255))
            
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 40))
        self.matrix_img = Image.alpha_composite(self.matrix_img, overlay)
        draw = ImageDraw.Draw(self.matrix_img)
        draw.fontmode = '1'
        
        for i, y in enumerate(self.matrix_cols):
            if y > -20 and y < self.config.matrix_height:
                char = chr(random.randint(0x30A0, 0x30FF))
                draw.text((i * 10, y), char, font=self.matrix_font, fill=(180, 255, 180, 255))
                if random.random() < 0.2:
                     draw.text((i * 10, y), char, font=self.matrix_font, fill=(255, 255, 255, 255))
            
            self.matrix_cols[i] += random.randint(8, 12)
            
            if self.matrix_cols[i] > self.config.matrix_height:
                if random.random() < 0.1:
                    self.matrix_cols[i] = random.randint(-20, -10)
                    
        img.paste(self.matrix_img.convert('RGB'), (0,0))
        
        # Draw foreground text
        return super().render(img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor)
