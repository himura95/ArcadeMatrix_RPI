🇬🇧 [English](README.md) | 🇫🇷 Français | 🇪🇸 [Español](README_ES.md)

# ArcadeMatrix MUGEN Sprite Extractor

Ce script Python (`mugen_extractor.py`) a été conçu sur mesure pour extraire, optimiser et convertir des personnages issus du moteur de jeu de combat **MUGEN**, afin de les rendre compatibles avec les `FighterEngine` d'ArcadeMatrix (versions ESP32 en C++ et Raspberry Pi en Python).

## À quoi sert-il ?

Les jeux de combat (MUGEN en particulier) gèrent les sprites avec des palettes de couleurs complexes (`.act`, `.sff`) et des scripts d'animation (`.air`) qui incluent des délais variables entre chaque frame, ainsi que des boîtes de collision.

De plus, la taille d'une matrice LED est très limitée (ex. 64x32). Les sprites MUGEN originaux sont souvent trop grands et n'ont pas toujours le même alignement d'une animation à l'autre (par exemple, un personnage qui saute aura une image plus grande qui s'étend vers le haut).

Le but de cet outil est de :
1. **Lire les formats MUGEN natifs** (`.sff` v1 et `.air`).
2. **Décoder la palette maître** (pour que les couleurs soient correctes).
3. **Sélectionner uniquement les animations nécessaires** pour ArcadeMatrix (`walk`, `attack`, `hit`, `win`, `special`, `super`, `fall`).
4. **Calculer une échelle uniforme** basée sur la hauteur standard du personnage (en position `stand` ou `walk`) afin qu'il tienne dans la hauteur de votre matrice LED (ex. 32 pixels).
5. **Générer un alignement parfait (Virtual Ground)** : l'outil calcule une bounding box globale afin de garantir que la ligne de sol (`ground_y`) et le centre du personnage (`origin_x`) restent parfaitement fixes d'une animation à l'autre. Cela évite que le personnage « tremble » ou change de taille lorsqu'il attaque !
6. **Convertir en `.fgt` (Fighter Format)** : le format `.fgt` est un format binaire optimisé créé spécifiquement pour ArcadeMatrix, stockant les pixels en RGB565 avec un code couleur de transparence, prêt à être lu ultra rapidement par l'ESP32 et le Raspberry Pi.

## Prérequis

Assurez-vous d'avoir Python 3 installé avec la bibliothèque d'images PIL (Pillow) :

```bash
pip install Pillow
```

## Structure du répertoire MUGEN

Le script attend que vous lui fournissiez un dossier source contenant plusieurs sous-dossiers, un par personnage. Chaque personnage doit contenir au minimum ses fichiers `.sff` et `.air`.

Exemple :
```text
/path/to/mugen_chars/
    ├── Ryu/
    │   ├── ryu.sff
    │   ├── ryu.air
    │   └── ryu.def
    ├── Ken/
    │   ├── ken.sff
    │   └── ken.air
    └── ChunLi/
```

## Comment l'utiliser

Exécutez le script avec des arguments en ligne de commande - inutile de modifier le moindre code :

```bash
python mugen_extractor.py --src /Chemin/Vers/Vos/Personnages/Mugen/chars --dest ./fighters_32
```

Options :
| Option | Défaut | Description |
|---|---|---|
| `--src` | *(obligatoire)* | Dossier contenant vos sous-dossiers de personnages MUGEN. |
| `--dest` | `./fighters_32` | Dossier de sortie pour les fichiers `.fgt` générés + `index.json`/`index.txt`. |
| `--mode` | `FULLSIZE` | `SCALED` redimensionne les personnages pour occuper exactement la hauteur du panneau (ESP32 standard, sans PSRAM) ; `FULLSIZE` conserve l'échelle 1:1 (recommandé sur RPi, qui n'a pas cette contrainte mémoire). |
| `--compress` | désactivé | Compresse les fichiers `.fgt` en gzip (`.fgt.gz`) pour économiser de l'espace disque. |

Pour cibler à la fois une matrice 32px et 64px, exécutez-le simplement deux fois avec des dossiers `--dest` différents :

```bash
python mugen_extractor.py --src /Chemin/Vers/Vos/Personnages/Mugen/chars --dest ./fighters_32
python mugen_extractor.py --src /Chemin/Vers/Vos/Personnages/Mugen/chars --dest ./fighters_64
```

### Processus d'extraction

Le script va créer (ou vider) les dossiers `fighters_32` et `fighters_64`. Pour chaque personnage, il créera un sous-dossier (ex. `fighters_32/Ryu/`) contenant :
- `walk.fgt`
- `attack.fgt`
- `hit.fgt`
- `win.fgt`
- *(et éventuellement `special1.fgt`, `super1.fgt`, `fall.fgt` s'ils sont trouvés)*

Il génère également deux fichiers d'index à la racine du dossier d'export :
- `index.json`
- `index.txt`

Ces fichiers d'index contiennent les métadonnées (Height, `ground_y`, `origin_x`, etc.) nécessaires aux moteurs de rendu ArcadeMatrix pour positionner correctement les combattants sur la matrice.

## Pourquoi les personnages ignoraient-ils auparavant la ligne de sol ?

Auparavant, chaque animation (`walk`, `attack`) était mise à l'échelle isolément en recadrant les pixels transparents. Résultat : une attaque haute rendait l'image d'attaque plus grande que l'image de marche, modifiant l'échelle et décalant le personnage vers le bas.

Avec cette version **v4**, le script effectue deux passes :
1. Il mesure les proportions maximales globales du personnage sur l'ensemble de ses animations combinées.
2. Il applique un ratio d'échelle strict basé uniquement sur son animation de marche/repos.
3. Il dessine toutes les frames sur un « Canvas » global à taille fixe (ex. 48x48), afin que l'axe des pieds du personnage tombe toujours sur le pixel exact `ground_y`. Les moteurs lisent cette valeur `ground_y` pour les aligner ensemble !

---
*Ce script est open source et conçu pour l'écosystème ArcadeMatrix.*
