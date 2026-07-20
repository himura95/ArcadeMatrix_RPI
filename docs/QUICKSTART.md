🇬🇧 English | 🇫🇷 [Français](QUICKSTART_FR.md) | 🇪🇸 [Español](QUICKSTART_ES.md)

# Quickstart Guide

This guide will help you install and configure ArcadeMatrix on your Raspberry Pi.

## 1. Installation (Recommended)

We provide a ready-to-use pre-compiled image.

1. Flash the `ArcadeMatrix_Release.img` file to your SD card using **Raspberry Pi Imager**.
2. Once finished, reinsert the SD card into your PC/Mac. An 8GB USB drive named **DATA** will appear.
3. Open the `conf.ini` file located on this **DATA** drive to insert your Wi-Fi credentials (`SSID` and `PASS`) and your matrix size.
4. Insert the SD card into the Raspberry Pi and turn it on. The IP address will be displayed on the matrix!

## 2. Web Configuration

Once the Pi is powered on, open a browser on your phone or PC and go to:
`http://<RASPBERRY_IP>:8080`

Here you can configure:
- Clock & Date colors, fonts, and themes.
- Enabled features in the rotation loop.
- Brightness and night mode settings.

## 3. Adding Content (GIFs, Sprites, Fonts)

To add your own media, **simply plug your SD card into your PC/Mac**.
The **DATA** drive will appear as a standard USB flash drive (exFAT format):

- **GIFs**: Drop them in the `gifs/` folder.
- **MUGEN Sprites**: Use our extractor to generate `.fgt` files and place them in `fighters_32/` or `fighters_64/`.
- **Fonts**: Drop `.ttf` or `.bdf` fonts in the `fonts/` folder.

*(Adding media is done exclusively by plugging the SD card into a computer or via SSH/SFTP. If using SSH, ensure the DATA partition is properly mounted first. There is no web upload feature).*

## 4. Hardware Connection

We recommend using an Adafruit RGB Matrix HAT or Bonnet connected to a Raspberry Pi Zero 2 W or Pi 4. Ensure the HUB75 connector is properly plugged into your LED panel.
