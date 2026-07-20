🇬🇧 English | 🇫🇷 [Français](0005-backend-abstraction_FR.md) | 🇪🇸 [Español](0005-backend-abstraction_ES.md)

# ADR-0005: Backend Abstraction (Draft)

## Status
Proposed (Future Phase)

## Context
ArcadeMatrix currently has two distinct codebases: an ESP32 C++ version and a Python Raspberry Pi version. While they share the same philosophy, they are tightly coupled to their respective hardware libraries (`FastLED`/`PxMatrix` vs `hzeller/rpi-rgb-led-matrix`). 
If we want to develop or debug the interface on a standard PC without a physical LED matrix (e.g., using SDL or Pygame), or if we want to unify the rendering logic across all platforms, we need a backend abstraction layer.

## Proposed Decision
Introduce a `HardwareBackend` interface. The `Renderer` layer will output standard framebuffers or generic draw commands (like `draw_pixel`, `draw_rect`), which are then consumed by the active backend:
1. `RPiBackend`: Translates framebuffers to `hzeller` arrays.
2. `ESP32Backend`: Translates commands to `FastLED`.
3. `SDLBackend`: Translates framebuffers to an on-screen window for desktop development.

## Consequences
- **Pros**: Enables desktop-based development without physical hardware. Prepares the architecture for any future display technology.
- **Cons**: Adds another layer of indirection, which must be carefully profiled on the ESP32 to prevent FPS drops.
