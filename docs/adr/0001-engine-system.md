🇬🇧 English | 🇫🇷 [Français](0001-engine-system_FR.md) | 🇪🇸 [Español](0001-engine-system_ES.md)

# ADR 0001: Engine System Architecture

## Status
Accepted

## Context
As the ArcadeMatrix project grew beyond just displaying a clock, we needed a way to manage multiple distinct features (Clock, Date, Weather, GIFs, Fighting Sprites) without creating a massive, monolithic main loop.

## Decision
We decided to adopt an **Engine System**. Each major feature is encapsulated into its own class (e.g., `ClockEngine`, `WeatherEngine`, `FighterEngine`).
- The `RotationEngine` handles the scheduling and invokes each engine's `run(duration)` method.
- Engines are self-contained with respect to their business logic (e.g., fetching weather API data).

## Consequences
- **Pros**: Easy to add new features by simply creating a new Engine. The main loop remains clean.
- **Cons**: Requires standardizing the interface (`run(duration)`) and handling interruptions (like WebUI updates or MQTT commands) gracefully within each engine's loop.
