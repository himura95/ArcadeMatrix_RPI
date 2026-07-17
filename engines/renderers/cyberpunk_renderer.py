import random
from PIL import ImageDraw
from .base_renderer import BaseRenderer

class CyberpunkRenderer(BaseRenderer):
    def __init__(self, config):
        super().__init__(config)
        self.drops = []
        self._init_drops()

    def _init_drops(self):
        num_drops = max(15, self.config.matrix_width // 3)
        min_len = max(5, self.config.matrix_height // 6)
        max_len = max(10, self.config.matrix_height // 3 + 5)
        
        for _ in range(num_drops):
            self.drops.append({
                'x': random.randint(0, self.config.matrix_width - 1),
                'y': random.randint(-self.config.matrix_height, 0),
                'speed': random.randint(1, max(3, self.config.matrix_height // 10)),
                'length': random.randint(min_len, max_len)
            })

    def render(self, img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor=1.0):
        # Draw background
        draw = ImageDraw.Draw(img)
        draw.fontmode = '1'
        min_len = max(5, self.config.matrix_height // 6)
        max_len = max(10, self.config.matrix_height // 3 + 5)
        
        for d in self.drops:
            d['y'] += d['speed']
            if d['y'] - d['length'] > self.config.matrix_height:
                d['x'] = random.randint(0, self.config.matrix_width - 1)
                d['y'] = random.randint(-20, 0)
                d['speed'] = random.randint(1, max(3, self.config.matrix_height // 10))
                d['length'] = random.randint(min_len, max_len)
            
            for j in range(d['length']):
                py = d['y'] - j
                if 0 <= py < self.config.matrix_height:
                    if j == 0:
                        draw.point((d['x'], py), fill=(255, 255, 255))
                    else:
                        g = max(0, 255 - (j * (255 // d['length'])))
                        draw.point((d['x'], py), fill=(0, g, 0))
                        
        # Draw foreground text
        return super().render(img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor)
