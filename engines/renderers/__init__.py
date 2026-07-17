from .base_renderer import BaseRenderer
from .flip_renderer import FlipRenderer
from .cyberpunk_renderer import CyberpunkRenderer
from .true_matrix_renderer import TrueMatrixRenderer

def get_renderer(theme_id, config):
    if theme_id == 18:
        return CyberpunkRenderer(config)
    elif theme_id == 19:
        return FlipRenderer(config)
    elif theme_id == 21:
        return TrueMatrixRenderer(config)
    else:
        return BaseRenderer(config)
