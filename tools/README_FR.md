🇬🇧 [English](README.md) | 🇫🇷 Français | 🇪🇸 [Español](README_ES.md)

# tools/

Utilitaires côté PC/manuels pour ArcadeMatrix_RPi. Ils ne font pas partie de l'application
Flask/API - vous les exécutez vous-même, séparément, soit sur votre propre ordinateur, soit en les
copiant sur votre Recalbox.

## `mugen_extractor/`

Convertit les fichiers de personnages MUGEN (`.sff`/`.air`) au format binaire de sprite `.fgt`
utilisé à la fois par `engines/fighter.py` de ce projet **et** par le `FighterEngine` (C++) du
projet frère ESP32 - c'est le même outil, conservé identique dans les deux dépôts puisqu'il n'y a
pas de mécanisme de package partagé entre ces deux bases de code indépendantes. Voir
`mugen_extractor/README_FR.md` pour l'utilisation complète.

## `recalbox_setup_mqtt.sh`

Un script shell autonome que vous copiez sur votre Recalbox et exécutez **directement sur
l'appareil via SSH** (pas depuis votre PC) pour installer le daemon MQTT "en cours de lecture" :

1. `ssh root@<ip-recalbox>` (mot de passe : `recalboxroot`)
2. Modifiez la variable `MQTT_BROKER` en haut de ce script avec l'IP de votre Raspberry Pi (celui
   qui fait tourner ArcadeMatrix_RPi et la matrice LED).
3. Copiez/collez le script sur la Recalbox (ex : `scp tools/recalbox_setup_mqtt.sh root@<ip-recalbox>:/tmp/` puis `ssh root@<ip-recalbox> "sh /tmp/recalbox_setup_mqtt.sh"`).
4. Redémarrez la Recalbox quand demandé.

Ce qu'il installe :
- Un petit daemon Python (`/recalbox/share/arcadematrix_daemon.py`) qui interroge
  `/tmp/es_state.inf` (le fichier d'état en direct d'EmulationStation) toutes les 100ms, filtre les
  changements rapides de navigation (150ms), et publie `{"status": "playing"|"browsing", "game":
  "<nom de base de la rom>", "system": "<SystemId>"}` via MQTT sur le topic
  `recalbox/system/playing` via `mosquitto_pub` - c'est ce que consomment `_on_mqtt_message()` de
  `main.py` et `core/dmd_cache.py` pour afficher un marquee en direct.
- Un script de lancement (`/recalbox/share/userscripts/arcadematrix_launcher(permanent).sh`)
  qu'EmulationStation appelle au démarrage pour garder le daemon actif après chaque redémarrage.

**Note pour les utilisateurs qui ont aussi un appareil ESP32 ArcadeMatrix** : ce même daemon/format
de communication a été porté vers un installeur multiplateforme plus convivial (Windows/macOS/Linux)
dans `ArcadeMatrix/tools/recalbox_daemon/` du projet ESP32 (`install.sh`/`install.ps1`, à lancer
depuis votre PC au lieu de faire du SSH manuel). Les deux installeurs publient le même format MQTT,
donc **une seule installation peut servir à la fois un appareil RPi et un appareil ESP32
simultanément** si les deux sont abonnés au même broker. Si vous n'utilisez que ce projet RPi, ce
script suffit ; l'installeur de l'autre dépôt n'est qu'une façon plus automatisée de déployer la
même chose (ça vaut le coup de l'adopter même ici si vous préférez éviter le SSH manuel -
`ArcadeMatrix/tools/recalbox_daemon/install.sh` fonctionne contre une Recalbox quel que soit le
projet frontend avec lequel elle est associée).

**Normalement cela se fait automatiquement via la fonctionnalité d'installation SSH de l'interface
web** (`core/ssh_installer.py`, déclenchée depuis la page Réglages) - ce script est le recours
manuel pour ceux qui préfèrent ne pas donner leurs identifiants SSH Recalbox à l'application, ou qui
ont besoin d'inspecter/personnaliser exactement ce qui est installé avant de l'exécuter.
