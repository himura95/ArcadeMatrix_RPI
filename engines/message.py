import time
import logging
from PIL import Image, ImageDraw, ImageFont

class MessageEngine:
    def __init__(self, matrix_wrapper, config):
        self.mw = matrix_wrapper
        self.config = config

    def rgb565_to_rgb(self, rgb565):
        r = (rgb565 >> 8) & 0xF8
        g = (rgb565 >> 3) & 0xFC
        b = (rgb565 << 3) & 0xF8
        return (r, g, b)

    def run(self, max_duration=None):
        payload = getattr(self.config, 'message_payload', None)
        if not payload:
            return

        text = payload.get('text', '')
        if not text:
            return

        color_565 = payload.get('color', 0xFFFF)
        color = self.rgb565_to_rgb(color_565)
        size = payload.get('size', 2)
        direction = payload.get('direction', 'rtl')
        speed = payload.get('speed', 30)
        timeout = payload.get('timeoutSeconds', 30)

        # Map sizes to actual font sizes
        # 1 = small (10), 2 = medium (20), 3 = large (30)
        font_size = 10 * size
        try:
            # Try to load a nice font
            font = ImageFont.truetype("fonts/DotGothic16.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Measure text using getbbox
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        matrix_w = self.mw.matrix.width
        matrix_h = self.mw.matrix.height

        # Start positions depending on direction
        if direction == 'rtl':
            x = matrix_w
            y = (matrix_h - text_h) // 2
        elif direction == 'ltr':
            x = -text_w
            y = (matrix_h - text_h) // 2
        elif direction == 'ttb':
            x = (matrix_w - text_w) // 2
            y = -text_h
        elif direction == 'btt':
            x = (matrix_w - text_w) // 2
            y = matrix_h
        else:
            x, y = 0, 0

        # Calculate step based on speed (10 = fast, 100 = slow)
        # speed parameter from UI is 10 to 100
        # If speed is 10, wait 0.01s. If speed is 100, wait 0.1s.
        sleep_time = speed / 1000.0
        step = 1

        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                break

            canvas = self.mw.matrix.CreateFrameCanvas()
            img = Image.new('RGB', (matrix_w, matrix_h), (0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Draw text considering bbox offset
            draw.text((int(x) - bbox[0], int(y) - bbox[1]), text, font=font, fill=color)

            canvas.SetImage(img)
            self.mw.swap_canvas(canvas)

            # Move text
            if direction == 'rtl':
                x -= step
                if x < -text_w: break
            elif direction == 'ltr':
                x += step
                if x > matrix_w: break
            elif direction == 'ttb':
                y += step
                if y > matrix_h: break
            elif direction == 'btt':
                y -= step
                if y < -text_h: break

            time.sleep(sleep_time)

            if getattr(self.config, 'reload_flag', False):
                break
