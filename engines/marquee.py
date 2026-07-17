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

        # Fast resizing while maintaining aspect ratio (thumbnail is highly optimized)
        if image.size != (self.config.matrix_width, self.config.matrix_height):
            bg = Image.new('RGB', (self.config.matrix_width, self.config.matrix_height), (0, 0, 0))
            image.thumbnail((self.config.matrix_width, self.config.matrix_height), Image.Resampling.BICUBIC)
            offset = ((self.config.matrix_width - image.width) // 2, (self.config.matrix_height - image.height) // 2)
            bg.paste(image, offset)
            image = bg

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
