🇬🇧 [English](0005-backend-abstraction.md) | 🇫🇷 [Français](0005-backend-abstraction_FR.md) | 🇪🇸 Español

# ADR-0005: abstracción del backend (borrador)

## Status
Proposed (Future Phase)

## Context
ArcadeMatrix actualmente tiene dos codebases distintas: una versión ESP32 en C++ y una versión Raspberry Pi en Python. Aunque comparten la misma filosofía, están fuertemente acopladas a sus respectivas bibliotecas de hardware (`FastLED`/`PxMatrix` vs `hzeller/rpi-rgb-led-matrix`). 
Si queremos desarrollar o depurar la interfaz en un PC estándar sin una matriz LED física (p. ej. usando SDL o Pygame), o si queremos unificar la lógica de renderizado en todas las plataformas, necesitamos una capa de abstracción del backend.

## Proposed Decision
Introducir una interfaz `HardwareBackend`. La capa `Renderer` producirá framebuffers estándar o comandos genéricos de dibujo (como `draw_pixel`, `draw_rect`), que luego consumirá el backend activo:
1. `RPiBackend`: traduce framebuffers a arrays de `hzeller`.
2. `ESP32Backend`: traduce comandos a `FastLED`.
3. `SDLBackend`: traduce framebuffers a una ventana en pantalla para desarrollo de escritorio.

## Consequences
- **Pros**: permite desarrollo de escritorio sin hardware físico. Prepara la arquitectura para cualquier futura tecnología de pantalla.
- **Cons**: añade otra capa de indirección, que debe perfilarse cuidadosamente en el ESP32 para evitar caídas de FPS.
