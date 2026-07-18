from PIL import Image, ImageDraw, ImageFont
import math
from core.theme import draw_styled_text

class SlotMachineClock:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.last_minute = -1
        self.anim_frame = 0
        self.spinning = False
        self.spin_speed = 0
        self.target_time = ""
        self.current_time = "00:00"
        self.y_offset = 0.0

    def tick(self, img, time_str, font, color1, color2, offset_x=0, offset_y=0, scale_factor=1.0):
        draw = ImageDraw.Draw(img)
        draw.fontmode = '1'
        self.anim_frame += 1

        parts = time_str.split(':')
        now_min = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0

        if self.last_minute == -1:
            self.last_minute = now_min
            self.current_time = time_str
            self.target_time = time_str
        elif self.last_minute != now_min and not self.spinning:
            self.spinning = True
            self.spin_speed = 15.0
            self.target_time = time_str
        elif not self.spinning:
            self.current_time = time_str
            
        try:
            bbox = draw.textbbox((0, 0), "00:00", font=font)
            left, top = bbox[0], bbox[1]
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except:
            tw, th = 30, 10
            left, top = 0, 0
            
        tw *= scale_factor
        th *= scale_factor
        left *= scale_factor
        top *= scale_factor
            
        tx = (self.w - tw) // 2 - left + offset_x
        ty = (self.h - th) // 2 - top + offset_y
        
        # Draw slot machine frame
        draw.rectangle([tx - 4, ty - 2, tx + tw + 4, ty + th + 2], outline=(200, 150, 0))
        
        if self.spinning:
            self.y_offset += self.spin_speed
            self.spin_speed *= 0.95 # Slow down friction
            
            if self.spin_speed < 0.5:
                self.spinning = False
                self.current_time = self.target_time
                self.last_minute = now_min
                self.y_offset = 0
                
            # Draw spinning blur (fake numbers)
            blur_y = ty + (int(self.y_offset) % (th * 2))
            draw_styled_text(img, "88:88", (tx, blur_y - (th * 2)), font, 19, (100, 100, 100), (100, 100, 100), scale=scale_factor)
            draw_styled_text(img, "00:00", (tx, blur_y), font, 19, (50, 50, 50), (50, 50, 50), scale=scale_factor)
            
            # Mask out the overflow
            draw.rectangle([0, 0, self.w, ty - 3], fill=(0,0,0))
            draw.rectangle([0, ty + th + 3, self.w, self.h], fill=(0,0,0))
            
        else:
            # Static time
            draw_styled_text(img, self.current_time, (tx, ty), font, 19, color1, color2, scale=scale_factor)
            
            # Win effect when not spinning
            if self.anim_frame % 20 < 10:
                draw.rectangle([tx - 4, ty - 2, tx + tw + 4, ty + th + 2], outline=(255, 255, 0))
                
        # Draw some decorative slot machine lights
        light_color = (255, 0, 0) if (self.anim_frame // 5) % 2 == 0 else (0, 255, 0)
        draw.ellipse([tx - 12, ty + th//2 - 2, tx - 8, ty + th//2 + 2], fill=light_color)
        
        light_color2 = (0, 255, 0) if (self.anim_frame // 5) % 2 == 0 else (255, 0, 0)
        draw.ellipse([tx + tw + 8, ty + th//2 - 2, tx + tw + 12, ty + th//2 + 2], fill=light_color2)

        return img
