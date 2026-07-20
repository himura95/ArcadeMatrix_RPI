🇬🇧 [English](0005-backend-abstraction.md) | 🇫🇷 Français | 🇪🇸 [Español](0005-backend-abstraction_ES.md)

# ADR-0005 : abstraction du backend (brouillon)

## Status
Proposed (Future Phase)

## Context
ArcadeMatrix possède actuellement deux codebases distinctes : une version ESP32 en C++ et une version Raspberry Pi en Python. Bien qu'elles partagent la même philosophie, elles sont fortement couplées à leurs bibliothèques matérielles respectives (`FastLED`/`PxMatrix` vs `hzeller/rpi-rgb-led-matrix`). 
Si nous voulons développer ou déboguer l'interface sur un PC standard sans matrice LED physique (p. ex. avec SDL ou Pygame), ou si nous voulons unifier la logique de rendu sur toutes les plateformes, nous avons besoin d'une couche d'abstraction du backend.

## Proposed Decision
Introduire une interface `HardwareBackend`. La couche `Renderer` produira des framebuffers standard ou des commandes de dessin génériques (comme `draw_pixel`, `draw_rect`), qui seront ensuite consommées par le backend actif :
1. `RPiBackend` : traduit les framebuffers en tableaux `hzeller`.
2. `ESP32Backend` : traduit les commandes pour `FastLED`.
3. `SDLBackend` : traduit les framebuffers en une fenêtre à l'écran pour le développement desktop.

## Consequences
- **Pros** : permet un développement desktop sans matériel physique. Prépare l'architecture à toute technologie d'affichage future.
- **Cons** : ajoute une couche supplémentaire d'indirection, qui devra être profilée avec soin sur l'ESP32 pour éviter des baisses de FPS.
