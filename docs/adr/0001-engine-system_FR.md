🇬🇧 [English](0001-engine-system.md) | 🇫🇷 Français | 🇪🇸 [Español](0001-engine-system_ES.md)

# ADR 0001 : architecture du système d'Engines

## Status
Accepted

## Context
À mesure que le projet ArcadeMatrix a dépassé le simple affichage d'une horloge, nous avions besoin d'un moyen de gérer plusieurs fonctionnalités distinctes (Clock, Date, Weather, GIFs, Fighting Sprites) sans créer une boucle principale massive et monolithique.

## Decision
Nous avons décidé d'adopter un **Engine System**. Chaque fonctionnalité majeure est encapsulée dans sa propre classe (p. ex. `ClockEngine`, `WeatherEngine`, `FighterEngine`).
- Le `RotationEngine` gère l'ordonnancement et invoque la méthode `run(duration)` de chaque engine.
- Les engines sont autonomes concernant leur logique métier (p. ex. la récupération de données depuis l'API météo).

## Consequences
- **Pros** : facile d'ajouter de nouvelles fonctionnalités en créant simplement un nouvel Engine. La boucle principale reste propre.
- **Cons** : nécessite de standardiser l'interface (`run(duration)`) et de gérer proprement les interruptions (comme les mises à jour WebUI ou les commandes MQTT) à l'intérieur de la boucle de chaque engine.
