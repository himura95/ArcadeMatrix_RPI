# Developer Guide

Welcome to the ArcadeMatrix development guide. This document explains how to extend the existing project, specifically how to add a new Clock/Date renderer.

## Extending the Project

ArcadeMatrix uses an **Engine System** for fetching data and managing loops, and a **Rendering Pipeline** for drawing to the hardware matrix.

If you want to create a new visual display for the time or date, you need to create a **Renderer**.

### Step-by-Step: Adding a New Clock Renderer

1. **Create the File**:
   Create a file `engines/renderers/my_custom_renderer.py`.

2. **Subclass BaseRenderer**:
   ```python
   from .base_renderer import BaseRenderer
   from core.theme import draw_styled_text

   class MyCustomRenderer(BaseRenderer):
       def __init__(self, config):
           super().__init__(config)
           # Initialize any persistent state here

       def render(self, img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor=1.0):
           # Draw your background or custom effects
           # ...
           # Draw the text on top
           return super().render(img, text, font, theme_id, color1, color2, offset_x, offset_y, scale_factor)
   ```

3. **Register the Renderer**:
   Open `engines/renderers/__init__.py` and add your renderer to the `get_renderer` factory based on a new theme ID.

4. **Update Configuration**:
   Update `core/config.py` and `api/server.py` if your theme requires new unique variables.
   Add your new theme ID to the Web UI frontend so users can select it.

## Testing

To run the integration tests on the API, use:
```bash
python3 -m pytest tests/
```
Ensure you have 100% coverage on new API routes!
