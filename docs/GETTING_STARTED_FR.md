🇬🇧 [English](GETTING_STARTED.md) | 🇫🇷 Français | 🇪🇸 [Español](GETTING_STARTED_ES.md)

# Premiers pas (app Raspberry Pi, configuration du workspace développeur)

Ce guide s'adresse aux développeurs qui mettent en place un **environnement de développement local** sur leur propre machine
(Mac/Linux/Windows) pour travailler sur la codebase ArcadeMatrix_RPi — par opposition à `QUICKSTART_FR.md`,
qui vise les utilisateurs finaux flashant une image préconstruite sur un Raspberry Pi. Pour l'architecture et
les conventions de contribution (Engines vs. Renderers), voir `DEVELOPER_FR.md` et `../CONTRIBUTING_FR.md`.

## 1. Créer un environnement virtuel

```bash
git clone <this-repo-url>
cd ArcadeMatrix_RPi
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## 2. Installer les dépendances

```bash
pip install -r requirements.txt
pip install pytest                # not in requirements.txt (runtime deps only) - needed for tests
```

**Point matériel important :** `requirements.txt` **n'inclut pas** `rgbmatrix` — il s'agit du binding Python de [hzeller's `rpi-rgb-led-matrix`](https://github.com/hzeller/rpi-rgb-led-matrix), une extension C++ compilée qui ne se construit/ne s'exécute que sur un vrai Raspberry Pi (elle parle directement aux broches GPIO). Cela signifie :
- `python3 main.py` **ne peut pas fonctionner de bout en bout sur une machine de dev classique** — `core/matrix.py` importe `rgbmatrix` sans condition au chargement du module, donc cela échouera immédiatement hors Pi.
- Vous pouvez quand même développer et tester tout ce qui n'a pas besoin de dessiner sur un panneau physique : l'API Flask (`api/server.py`), le parsing de configuration (`core/config.py`), la logique de rotation (`core/rotation.py`) et la majeure partie de la logique métier des Engines — voir la section tests ci-dessous, qui mocke déjà entièrement la couche matrice.
- Si vous voulez un aperçu visuel en direct sur votre machine de dev sans Pi, regardez [`RGBMatrixEmulator`](https://github.com/ty-porter/RGBMatrixEmulator) (un package drop-in, compatible API, qui rend dans une fenêtre Pygame ou dans le navigateur au lieu du vrai GPIO). Il n'est **pas actuellement câblé dans ce projet** — `core/matrix.py` devrait échanger conditionnellement son `from rgbmatrix import ...` — mais c'est un shim compatible bien connu si vous voulez expérimenter localement.

## 3. Lancer réellement l'application

L'exécution complète de l'application nécessite un Raspberry Pi avec la matrice câblée conformément à
`ARCHITECTURE_FR.md` / aux instructions du fabricant du HAT, et `rgbmatrix` compilé/installé
(`../install.sh` à la racine du dépôt automatise cela, y compris la configuration du service systemd). Sur le Pi :

```bash
sudo python3 main.py
```

(root/`sudo` est requis — `rgbmatrix` a besoin d'un accès direct au GPIO/DMA.)

Pour une installation totalement clé en main, `../install.sh` configure une unité systemd `arcadematrix.service` afin que l'application
démarre au boot et redémarre après un crash — vérifiez son statut/logs avec :

```bash
sudo systemctl status arcadematrix.service
sudo journalctl -u arcadematrix.service -f      # live-tail systemd's own logs
```

## 4. Où sont les logs

Indépendamment de systemd, l'application écrit aussi son propre fichier de logs rotatif à côté de `main.py` :

```bash
tail -f arcadematrix.log            # rotates at 5MB, keeps 3 backups (see main.py)
```

Un `crash.log` séparé est écrit (et écrasé) si le processus meurt à cause d'une exception non interceptée
(voir le handler `sys.excepthook` au début de `main.py`) — regardez ce fichier en priorité après n'importe quel crash.

## 5. Exécuter la suite de tests

C'est la manière principale de valider les changements sans matériel réel — la suite existante mocke déjà la matrice
(`MockMatrix`/`MockMatrixWrapper` dans `tests/conftest.py`) afin qu'elle s'exécute de façon identique sur votre machine de dev ou en CI :

```bash
python3 -m pytest tests/ -v
```

Voir la section « Testing Your Code » de `DEVELOPER_FR.md` pour les attentes du projet en matière de couverture
(100 % sur les routes API) et `../CONTRIBUTING_FR.md` pour savoir ce qui compte comme Engine vs. Renderer lors de l'ajout de nouveaux tests.

## 6. Construire une image de release (optionnel, pour les maintainers)

Si vous devez produire une image Raspberry Pi OS complète et flashable (comme celle liée depuis
`QUICKSTART_FR.md`), voir `../scripts/build_image.sh` (macOS/Linux, nécessite Docker) — il télécharge
Raspberry Pi OS Lite, injecte ce dépôt, compile le Python en bytecode pour masquer les sources et
crée la partition FAT32/exFAT `DATA` sur laquelle les utilisateurs finaux déposent leurs GIFs/fonts/sprites. C'est un
processus de 10 à 15 minutes et ce n'est pas nécessaire pour le développement quotidien de fonctionnalités — uniquement pour couper un nouvel artefact de release.

## Dépannage

- **`ModuleNotFoundError: No module named 'rgbmatrix'`** lors de l'exécution de `python3 main.py` hors Pi :
  c'est attendu, voir §2 ci-dessus — utilisez `pytest` pour le développement local à la place.
- **`ImportError` pour `paho.mqtt`** : la prise en charge MQTT est optionnelle (flag `MQTT_AVAILABLE` dans `main.py`) ;
  installez `paho-mqtt` (déjà dans `requirements.txt`) si vous devez tester localement l'intégration Batocera/Recalbox.
- **Les tests échouent avec des erreurs d'import `rgbmatrix`** : assurez-vous de tester via `api/server.py`
  et les fixtures fournies (`tests/conftest.py`) plutôt qu'en important directement `core.matrix` dans
  un nouveau test — les tests existants sont structurés précisément pour éviter de toucher à ce module.
