🇬🇧 [English](methodology.md) | 🇫🇷 [Français](methodology_FR.md) | 🇪🇸 Español

# Metodología de benchmarks

Este directorio hace seguimiento del rendimiento de ArcadeMatrix en distintas generaciones de hardware.

## Cómo medir
1. Activa `FPS_LOGGING=True` en `core/config.py` (o inyéctalo mediante variables de entorno).
2. Deja que el bucle de rotación se ejecute exactamente durante 5 minutos.
3. Haz la media de los FPS registrados en la consola.

## Métricas importantes
- **Carga de CPU**: nuestro objetivo es mantener la carga total de CPU por debajo del 40 % en un Pi Zero 2 para evitar thermal throttling.
- **Estabilidad de FPS**: el objetivo estándar es un 60 FPS sólido, o 50 FPS como mínimo.
