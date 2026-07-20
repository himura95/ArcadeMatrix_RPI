🇬🇧 [English](0004-rendering-responsibilities.md) | 🇫🇷 Français | 🇪🇸 [Español](0004-rendering-responsibilities_ES.md)

# ADR-0004 : séparation des responsabilités de rendu

## Status
Accepted

## Context
À mesure que nous ajoutions davantage de styles visuels (Flip Clock, True Matrix, Cyberpunk), nos `ClockEngine` et `DateEngine` se sont alourdis de logique de dessin. La logique métier (calcul de l'heure, gestion des durées de rotation) se retrouvait fortement mélangée à la logique de rendu (dessin de rectangles qui rétrécissent, calcul de bounding boxes, parsing de matrices de pixels). 
Cette structure monolithique rendait les engines difficiles à tester, pénibles à lire et empêchait de réutiliser les animations (comme l'animation Flip) pour d'autres types de texte.

## Decision
Nous avons mis en place une séparation stricte des responsabilités via un **Rendering Pipeline** :
`Data -> Engine -> Animation -> Renderer -> Matrix`

### 1. Pourquoi les Engines ne dessinent plus
Les Engines (p. ex. `ClockEngine`) sont uniquement responsables de la gestion d'état et de la logique métier. Ils savent *quelle* heure il est, *quel* format elle doit avoir et *quand* il est temps de passer à la rotation suivante. Ils ne savent pas ce qu'est un pixel. Cet isolement les rend testables à 100 % à l'aide de mocks Python standard, sans avoir besoin d'un écran physique.

### 2. Pourquoi les Renderers ne connaissent pas la logique métier
Les Renderers (p. ex. `CyberpunkRenderer`) sont de simples tuyaux. Ils prennent des chaînes brutes, des coordonnées et des thèmes, puis renvoient une image rendue (ou manipulent le canvas matériel pour des animations complexes frame par frame). Un `FlipRenderer` ne se soucie pas de savoir s'il anime une Clock ou une Date ; il se contente de retourner les caractères.

### 3. Animations réutilisables et mise à l'échelle des polices
Parce que le rendu est isolé, nous pouvons implémenter des effets globaux. Par exemple, le « Font Scaling » (pour l'agrandissement net des polices BDF) est désormais de la responsabilité de la couche de rendu. Toutes les horloges spécialisées et tous les renderers bénéficient de ce facteur d'échelle sans alourdir la logique des engines.

## Consequences
- **Pros**: 
  - Réduction massive de la duplication de code.
  - Composants hautement testables.
  - Extrêmement facile d'ajouter de nouveaux thèmes ou animations.
- **Cons**: 
  - Léger surcoût lié au passage des paramètres de configuration dans le pipeline.
