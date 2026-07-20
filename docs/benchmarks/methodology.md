🇬🇧 English | 🇫🇷 [Français](methodology_FR.md) | 🇪🇸 [Español](methodology_ES.md)

# Benchmark Methodology

This directory tracks the performance of ArcadeMatrix across different hardware generations.

## How to measure
1. Enable `FPS_LOGGING=True` in `core/config.py` (or inject it via env variables).
2. Let the rotation loop run for exactly 5 minutes.
3. Average the FPS logged to the console.

## Important Metrics
- **CPU Load**: We aim to keep total CPU load under 40% on a Pi Zero 2 to prevent thermal throttling.
- **FPS Stability**: The standard target is a solid 60 FPS, or 50 FPS minimum.
