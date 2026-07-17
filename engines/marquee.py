import time
import logging
from PIL import Image, ImageOps

class MarqueeEngine:
    def __init__(self, matrix_wrapper, config):
        self.mw = matrix_wrapper
        self.config = config

    def run(self, count):
        image_path = getattr(self.config, 'image_path', None)
        if not image_path:
            logging.warning("MarqueeEngine: No image_path provided in config.")
            return

        logging.info(f"Starting MarqueeEngine to display {image_path}")

        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            logging.error(f"MarqueeEngine: Cannot open image {image_path}: {e}")
            return

        # Resize image to fit matrix while keeping aspect ratio (padding with black)
        if image.size != (self.config.matrix_width, self.config.matrix_height):
            image = ImageOps.pad(image, (self.config.matrix_width, self.config.matrix_height), color=(0, 0, 0), method=Image.Resampling.LANCZOS)

        canvas = self.mw.get_canvas()
        if not canvas:
            return

        canvas.SetImage(image)
        canvas = self.mw.swap_canvas(canvas)

        # Keep displaying until interrupted
        while True:
            if getattr(self.config, 'reload_flag', False):
                break
            time.sleep(0.1)
