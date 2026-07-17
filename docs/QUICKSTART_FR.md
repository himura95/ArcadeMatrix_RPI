# Guide de Démarrage Rapide

Ce guide vous aidera à installer et configurer ArcadeMatrix sur votre Raspberry Pi.

## 1. Installation (Recommandée)

Nous fournissons une image pré-compilée prête à l'emploi.

1. Flashez le fichier `ArcadeMatrix_Release.img` sur votre carte SD avec **Raspberry Pi Imager**.
2. Une fois terminé, réinsérez la carte SD dans votre PC/Mac. Une clé USB de 8Go nommée **DATA** va apparaître.
3. Ouvrez le fichier `conf.ini` situé sur ce lecteur **DATA** pour y insérer vos identifiants Wi-Fi (`SSID` et `PASS`) et la taille de votre matrice.
4. Insérez la carte SD dans le Raspberry Pi et allumez-le. L'adresse IP s'affichera sur la matrice !

## 2. Configuration Web

Une fois le Pi allumé, ouvrez un navigateur sur votre téléphone ou PC et allez sur :
`http://<IP_DU_RASPBERRY>:8080`

Ici vous pourrez configurer :
- Les couleurs, polices et thèmes de l'horloge et de la date.
- Les fonctionnalités activées dans la boucle de rotation.
- La luminosité et le mode nuit.

## 3. Ajout de Contenu (GIFs, Sprites, Polices)

Pour ajouter vos propres médias, **branchez simplement votre carte SD sur votre PC/Mac**.
Le lecteur **DATA** apparaîtra comme une clé USB classique (format exFAT) :

- **GIFs** : Déposez-les dans le dossier `gifs/`.
- **Sprites MUGEN** : Utilisez notre extracteur pour générer des `.fgt` et placez-les dans `fighters_32/` ou `fighters_64/`.
- **Polices** : Déposez des polices `.ttf` ou `.bdf` dans le dossier `fonts/`.

*(L'ajout de médias se fait exclusivement en branchant la carte SD sur un ordinateur ou via SSH/SFTP. Si vous utilisez SSH, assurez-vous que la partition DATA est bien montée au préalable. Il n'y a pas d'upload via l'interface Web).*

## 4. Connexion Matérielle

Nous recommandons d'utiliser un HAT ou Bonnet RGB Matrix Adafruit branché sur un Raspberry Pi Zero 2 W ou Pi 4. Assurez-vous que le connecteur HUB75 est correctement branché à votre panneau LED.
