# ArcadeMatrix Music Sender

Cet outil capture les informations de lecture depuis les lecteurs audio sur Windows et les expose via HTTP pour affichage sur la matrice LED ArcadeMatrix_RPI.

## Fonctionnalités

- **Support des lecteurs natifs** : Détecte les titres en cours de lecture depuis VLC, Spotify Desktop, Foobar2000 et autres lecteurs audio natifs en utilisant pycaw
- **Support des lecteurs web** : Fonctionne avec les lecteurs web comme Deezer, Spotify Web, YouTube Music via l'extension navigateur
- **API HTTP** : Expose les informations de lecture via `GET /nowplaying` et accepte les mises à jour via `POST /nowplaying`
- **Windows uniquement** : Utilise des API spécifiques à Windows (pycaw)

## Installation

1. Installer les dépendances Python :
   ```
   pip install -r requirements.txt
   ```

2. Lancer l'outil :
   ```
   python music_sender.py --port 8085
   ```

3. Pour le support des lecteurs web, installez l'extension navigateur dans Chrome/Firefox

## Utilisation

### Options en ligne de commande
- `--port` ou `-p`: Port d'écoute (par défaut : 8085)

### Points de terminaison API
- `GET /nowplaying`: Retourne les informations du titre en cours sous forme JSON
- `POST /nowplaying`: Accepte les données de lecture depuis l'extension navigateur
- `GET /health`: Retourne l'état du serveur

## Configuration

1. Exécutez l'outil sur votre PC Windows
2. Configurez le RPI pour se connecter à l'IP et port de votre PC (par défaut : `http://192.168.1.100:8085`)
3. Pour les lecteurs web, installez l'extension navigateur et configurez-la avec l'IP de votre PC

## Fichiers

```
tools/music_sender/
├── music_sender.py        # Script principal Python
├── requirements.txt       # Dépendances Python
├── start_sender.bat       # Script de démarrage Windows
├── README.md              # Ce fichier
└── extension/             # Fichiers de l'extension navigateur
    ├── manifest.json      # Manifest de l'extension
    ├── background.js      # Script d'arrière-plan
    ├── popup.html         # Popup de configuration
    └── popup.js           # Logique du popup
```

## Dépendances

- Python 3.x
- Système Windows (pycaw ne fonctionne que sur Windows)
- Bibliothèque pycaw (`pip install pycaw`)
- Bibliothèque comtypes (`pip install comtypes`)

## Extension Navigateur

L'extension navigateur supporte :
- Spotify Web Player
- Deezer Web Player  
- YouTube Music

Installez l'extension dans Chrome/Firefox et configurez-la avec l'IP de votre PC pour envoyer les informations de lecture à l'outil music_sender.

## Dépannage

### Erreur "pycaw not available"
Cet outil nécessite Windows et pycaw pour détecter les lecteurs natifs. Si vous êtes sur un système non-Windows, seul le support des lecteurs web fonctionnera.

### Problèmes de connexion
1. Assurez-vous que le PC exécutant `music_sender.py` est accessible depuis votre RPI
2. Vérifiez que le port (par défaut 8085) est ouvert et non bloqué par un pare-feu
3. Vérifiez l'adresse IP dans la configuration de l'extension navigateur

### Détection des lecteurs web
Si la détection des lecteurs web ne fonctionne pas :
1. Assurez-vous d'avoir installé l'extension navigateur
2. Vérifiez que l'extension a les permissions nécessaires pour accéder aux onglets
3. Vérifiez que l'IP dans le popup de l'extension est correcte
4. Testez la connexion depuis le popup de l'extension