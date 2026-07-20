🇬🇧 [English](methodology.md) | 🇫🇷 Français | 🇪🇸 [Español](methodology_ES.md)

# Méthodologie de benchmark

Ce répertoire suit les performances d'ArcadeMatrix sur différentes générations de matériel.

## Comment mesurer
1. Activez `FPS_LOGGING=True` dans `core/config.py` (ou injectez-le via des variables d'environnement).
2. Laissez tourner la boucle de rotation pendant exactement 5 minutes.
3. Faites la moyenne des FPS journalisés dans la console.

## Métriques importantes
- **Charge CPU** : nous visons à maintenir la charge CPU totale sous 40 % sur un Pi Zero 2 afin d'éviter le thermal throttling.
- **Stabilité des FPS** : l'objectif standard est un 60 FPS solide, ou 50 FPS minimum.
