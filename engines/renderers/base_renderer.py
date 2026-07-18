class BaseRenderer:
    def __init__(self, config):
        self.config = config

    def render(self, img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor=1.0):
        """
        Renders the static text onto the image, centered by default.
        """
        from PIL import ImageDraw
        from core.theme import draw_styled_text
        
        draw = ImageDraw.Draw(img)
        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        except AttributeError:
            try:
                w, h = font.getsize(text)
                left, top, right, bottom = 0, 0, w, h
            except Exception:
                left, top, right, bottom = 0, 0, 30, 10
        
        text_width = (right - left) * scale_factor
        text_height = (bottom - top) * scale_factor
        
        x = (self.config.matrix_width - text_width) // 2 - left + offset_x
        y = (self.config.matrix_height - text_height) // 2 - top + offset_y
        
        draw_styled_text(img, text, (x, y), font, theme_id, color1, color2, scale=scale_factor)
        return img

    def animate(self, mw, prev_text, current_text, font, color1, color2, offset_x, offset_y, scale_factor=1.0):
        """
        Optional. Performs an animation directly on the MatrixWrapper canvas.
        Returns a list of frames if an animation was performed, empty list otherwise.
        """
        return []
