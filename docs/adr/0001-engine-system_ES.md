🇬🇧 [English](0001-engine-system.md) | 🇫🇷 [Français](0001-engine-system_FR.md) | 🇪🇸 Español

# ADR 0001: arquitectura del sistema de Engines

## Status
Accepted

## Context
A medida que el proyecto ArcadeMatrix creció más allá de mostrar solo un reloj, necesitábamos una forma de gestionar múltiples funciones distintas (Clock, Date, Weather, GIFs, Fighting Sprites) sin crear un bucle principal masivo y monolítico.

## Decision
Decidimos adoptar un **Engine System**. Cada función principal queda encapsulada en su propia clase (p. ej. `ClockEngine`, `WeatherEngine`, `FighterEngine`).
- El `RotationEngine` se encarga de la planificación e invoca el método `run(duration)` de cada engine.
- Los engines son autocontenidos respecto a su lógica de negocio (p. ej. recuperar datos de la API de weather).

## Consequences
- **Pros**: es fácil añadir nuevas funciones creando simplemente un nuevo Engine. El bucle principal se mantiene limpio.
- **Cons**: requiere estandarizar la interfaz (`run(duration)`) y gestionar con elegancia las interrupciones (como actualizaciones de la WebUI o comandos MQTT) dentro del bucle de cada engine.
