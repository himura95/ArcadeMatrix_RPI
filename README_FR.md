# ArcadeMatrix RPi 🍓👾

Un portage basé sur Python du projet **ArcadeMatrix**, spécialement conçu pour fonctionner sur un **Raspberry Pi** connecté à une matrice LED RGB (HUB75) via le HAT d'Adafruit ou le matériel Joy-IT.

Ce projet reproduit les superbes fonctionnalités de la version ESP32 tout en supprimant complètement ses limitations matérielles.

---

## 🌟 Fonctionnalités (Exclusivités RPi vs ESP32)

* **Polices chargeables dynamiquement (`.ttf`)** : Fini les polices codées en dur ! Déposez n'importe quelle police `.ttf` ou `.otf` directement dans le dossier `fonts/`, et l'interface Web la listera automatiquement pour l'utiliser sur l'horloge ou la date.
* **Tailles et décalages d'horloge/date illimités** : Vous n'êtes plus limité aux tailles 1, 2 ou 3. Vous pouvez définir n'importe quelle taille et positionner le texte librement sur des panneaux matriciels massifs (ex: 256x64).
* **Sélection massive d'horloges** : Profitez d'une variété d'horloges animées comprenant les classiques Arcade, Binaire, Cyberpunk, Flip, Mots, et les toutes nouvelles horloges **Pac-Man**, **Tetris**, **SlotMachine** (Machine à sous) et **Versus (Mugen)** !
* **Véritable pluie numérique Matrix (Katakana)** : Un effet de pluie numérique Matrix entièrement personnalisé, fluide et authentique (`DotGothic16`) avec des Katakana qui tombent et du texte en espace négatif (LEDs éteintes) qui perfore la pluie.
* **Dégradés lisses personnalisés** : En plus des thèmes classiques d'éditeurs (Nintendo, Capcom, Sega...), vous pouvez maintenant choisir un thème **Couleur / Dégradé personnalisé** et choisir deux couleurs pour générer un dégradé dynamique.
* **Listes de lecture d'images dynamiques (GIF/PNG/JPG)** : Lisez de vrais fichiers `.gif` et `.png` de manière dynamique directement depuis le système de fichiers, sans problèmes de fragmentation de la carte SD.
* **Puissance de Python** : L'intégralité du moteur, de l'API et de l'interface utilisateur est gérée par Python (`Pillow` pour le dessin, `Flask` pour l'API), ce qui permet des modifications beaucoup plus rapides.

---

## 🚀 Matériel Requis

1. **Raspberry Pi**: Tout modèle jusqu'au Pi 4 (Zero 2 W, Pi 3, Pi 4).
   *(⚠️ **Avertissement Pi 5** : La librairie hzeller rgb-led-matrix ne supporte PAS le Pi 5 nativement via GPIO à cause de sa puce RP1. Vous devez utiliser un adaptateur actif pour le Pi 5 ! Les Pi 4 ou Zero 2W sont fortement recommandés).*
2. **Matrice LED RGB**: Panneaux HUB75 (ex: 64x64, 128x32, 256x64).
3. **Adafruit RGB Matrix HAT** (ou Joy-IT, ou câblage manuel).
4. **Carte MicroSD** (16 Go ou plus recommandé pour l'image précompilée).

---

## 💾 Installation & Configuration

### Option 1 : Image Précompilée (Recommandée pour les testeurs)
Nous fournissons un fichier `.img` précompilé et entièrement automatisé (`ArcadeMatrix_Release.img`).
1. Flashez le `.img` sur votre carte SD avec **Raspberry Pi Imager**.
2. Une fois fait, insérez la carte SD dans votre PC/Mac. Vous verrez apparaître une grosse clé USB de **8 Go nommée DATA** !
3. Ouvrez le fichier `conf.ini` situé sur ce lecteur DATA pour configurer la taille de votre Matrice et vos identifiants **Wi-Fi** (`SSID` et `PASS`).
4. Mettez la carte SD dans votre Raspberry Pi et allumez-le.
5. La matrice s'allumera immédiatement et **affichera son adresse IP** pendant 5 secondes. Utilisez cette IP pour accéder à l'interface Web !

### Option 2 : Installation Manuelle
Si vous préférez l'installer manuellement sur un **Raspberry Pi OS Lite (64-bit)** fraîchement installé :
Une fois connecté à votre Raspberry Pi via SSH :

```bash
curl -sSL https://raw.githubusercontent.com/red77290/ArcadeMatrix_RPI/main/install.sh | bash
```

Le script va automatiquement :
1. Installer Python 3, Flask, Pillow et `build-essential`.
2. Télécharger et compiler le pilote `hzeller/rpi-rgb-led-matrix`.
3. Désactiver l'audio intégré pour éviter les scintillements (flicker) de la matrice.
4. Configurer `systemd` pour démarrer automatiquement ArcadeMatrix au démarrage.

---

## 🎨 Gestion des Médias

L'image précompilée dispose d'une **partition DATA de 8 Go** formatée en exFAT. Cela signifie que vous pouvez brancher votre carte SD directement sur votre PC ou Mac pour glisser-déposer vos fichiers sans avoir besoin de SSH ou FTP !

### Sprites & GIFs
* **`/fighters_32/`** ou **`/fighters_64/`** : Mettez vos sprites `.fgt` ici (Voir section Sprites MUGEN plus bas).
* **`/gifs/`** : Placez vos boucles `.gif` dans des dossiers à l'intérieur.
L'Interface Web scannera automatiquement ces dossiers et vous permettra de cocher ceux que vous voulez lire !

### Polices (Fonts)
* **`/fonts/`** : Placez vos fichiers `.ttf`, `.otf`, ou `.bdf` ici.
Par défaut, le projet est livré avec `PressStart2P.ttf`, `VT323.ttf`, et `DotGothic16.ttf`.

---

## 🕸️ Interface Web (Web UI)
Naviguez vers `http://<IP_DE_VOTRE_PI>:8080/` pour accéder au panneau de contrôle.

L'interface est exactement la même que la version ESP32, offrant les contrôles du tableau de bord, la sélection des listes de lecture, la configuration de l'horloge et les paramètres MQTT, avec des contrôles supplémentaires pour les **Dégradés** et les **Tailles illimitées**.

---

## 🔧 Configuration de la Matrice
Si vous avez une matrice plus grande que 64x64 ou 128x32, ou si vous utilisez un HAT non-Adafruit, vous devrez peut-être modifier les arguments `hzeller` dans `core/matrix.py`. Par défaut, ils sont définis sur `--led-gpio-mapping=adafruit-hat` et `128x32`.

Vous pouvez également modifier la luminosité de la matrice de manière dynamique via les paramètres de l'interface Web.
- Activez les modes Veille/Nuit.

---

## 📂 Gestion des médias avancés (Sprites MUGEN)

### Ajouter des GIFs
Déposez simplement vos fichiers `.gif` standards dans le dossier `gifs/` :
```text
ArcadeMatrix_RPi/
└── gifs/
    ├── mario_run.gif
    ├── sonic_wait.gif
    └── ...
```

### Ajouter des Sprites MUGEN
Afin d'obtenir une performance parfaite à 60fps et des alignements exacts de "sol virtuel" (virtual ground) sur des rosters de personnages massifs, le moteur Fighter utilise des fichiers `.fgt` pré-traités accompagnés d'un manifeste `index.txt`.

**Vous ne pouvez pas simplement déposer des images brutes dans les dossiers fighters !**
Vous DEVEZ utiliser l'outil `mugen_extractor.py` fourni dans le dossier `tools/mugen_extractor/` pour traiter vos personnages MUGEN. 

L'extracteur lira les fichiers `.sff` et `.air` de MUGEN, calculera les boîtes de collision (bounding boxes) parfaites pour éviter les tremblements d'animation, et exportera des fichiers `.fgt` optimisés directement dans vos dossiers `fighters_32/` et `fighters_64/`.

Veuillez consulter `tools/mugen_extractor/README_FR.md` pour les instructions complètes sur l'ajout de nouveaux personnages MUGEN !

---

## ⚙️ Configuration Avancée (conf.ini)

Si vous préférez configurer la matrice manuellement plutôt que via l'interface Web, vous pouvez éditer le fichier `conf.ini` situé sur la partition **DATA** de votre carte SD.
C'est particulièrement utile pour renseigner vos identifiants Wi-Fi avant le premier démarrage.

### 🌐 [WIFI]
| Paramètre | Défaut | Description |
|---|---|---|
| `SSID` | `YourNetworkName` | Le nom de votre réseau Wi-Fi. |
| `PASS` | `YourNetworkPassword` | Le mot de passe de votre réseau. |
| `CONFIGURED` | `false` | Mettez sur `false` pour forcer le Raspberry Pi à se connecter au prochain démarrage. Remis automatiquement à `true` en cas de succès. |

### 🎛️ [MATRIX]
| Paramètre | Défaut | Description |
|---|---|---|
| `ROWS` / `COLS` | `32` / `64` | Les dimensions en pixels d'un seul panneau LED. |
| `HARDWARE_MAPPING` | `adafruit-hat` | Type de câblage utilisé. (`adafruit-hat`, `adafruit-hat-pwm`, `regular-pi1`, `regular`). |
| `CHAIN` / `PARALLEL` | `1` / `1` | `CHAIN` pour chainer horizontalement. `PARALLEL` pour empiler verticalement sur plusieurs ports HUB75. |
| `SLOWDOWN` | `2` | Ralentissement matériel (1 à 4). Augmentez si votre matrice clignote ou glitch (surtout Pi 3/4). |
| `BRIGHTNESS` | `100` | Luminosité globale de la matrice (1 à 100). |
| `RGB_SEQUENCE` | `RGB` | Ordre des couleurs. Modifiez en `RBG` ou `BGR` si vos couleurs sont inversées. |

### ⏰ [TIME] & [DATE]
| Paramètre | Défaut | Description |
|---|---|---|
| `FORMAT_24H` | `true` | `true` pour le format 24h, `false` pour le format AM/PM (12h). |
| `CLOCK_FONT` | `DotGothic16.ttf`| Nom du fichier `.ttf` ou `.bdf` situé dans `/fonts/`. |
| `CLOCK_SIZE` | `16` | Taille de la police (facteur d'échelle) pour l'horloge. |
| `THEME` | `0` | L'identifiant numérique du thème d'horloge (ex: 19 pour Flip, 21 pour True Matrix). |
| `CLOCK_COLOR_1` | `#ffffff` | Couleur hexadécimale primaire. Utilisée pour les dégradés si le thème est Custom (20). |
| `CLOCK_COLOR_2` | `#ffffff` | Couleur hexadécimale secondaire. |

*(La section `[DATE]` contient des paramètres identiques pour configurer l'affichage de la date).*

### 🔄 [IDLE]
| Paramètre | Défaut | Description |
|---|---|---|
| `ROTATION` | `all` | Dicte la règle de rotation (`clock`, `gifs`, `sprites`, ou `all`). |
| `CLOCK_DURATION_SEC`| `10` | Temps d'affichage de l'horloge/date pendant la boucle. |
| `GIF_DURATION_SEC` | `10` | Temps d'affichage d'un seul GIF avant de passer au suivant. |
| `SELECTED_GIFS` | *(vide)* | Liste séparée par des virgules pour boucler certains médias. Laissez vide pour tout jouer. |
| `SELECTED_SPRITES` | *(vide)* | Liste séparée par des virgules pour boucler certains sprites. Laissez vide pour tout jouer. |

### 🌙 [STANDBY]
| Paramètre | Défaut | Description |
|---|---|---|
| `NIGHT_MODE_ENABLED`| `false` | Si `true`, la matrice s'éteindra et se rallumera automatiquement. |
| `TURN_OFF_AT` | `23:00` | Heure formatée en HH:MM pour la mise en veille. |
| `WAKE_UP_AT` | `07:00` | Heure formatée en HH:MM pour le réveil. |

## 📜 Licence
Ce projet est open-source. Profitez de votre horloge d'arcade rétro ultime !
