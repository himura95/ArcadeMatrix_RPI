# tools/

🇬🇧 English | 🇫🇷 [Français](README_FR.md) | 🇪🇸 [Español](README_ES.md)

PC/manual-side utilities for ArcadeMatrix_RPi. These are not part of the Flask app/API - you run
them yourself, separately, either on your own computer or by pasting them onto your Recalbox.

## `mugen_extractor/`

Converts MUGEN fighting-game character files (`.sff`/`.air`) into the `.fgt` binary sprite format
used by both this project's `engines/fighter.py` **and** the ESP32 sibling project's
`FighterEngine` (C++) - it's the same tool, kept identical in both repos since there's no shared
package mechanism between the two independent codebases. See `mugen_extractor/README.md` for full
usage.

## `recalbox_setup_mqtt.sh`

A standalone shell script you copy onto your Recalbox and run **directly on the device over SSH**
(not from your PC) to install the "now playing" MQTT daemon:

1. `ssh root@<recalbox-ip>` (password: `recalboxroot`)
2. Edit the `MQTT_BROKER` variable at the top of this script to your Raspberry Pi's IP (the one
   running ArcadeMatrix_RPi and the LED matrix).
3. Copy/paste the script onto the Recalbox (e.g. `scp tools/recalbox_setup_mqtt.sh root@<recalbox-ip>:/tmp/` then `ssh root@<recalbox-ip> "sh /tmp/recalbox_setup_mqtt.sh"`).
4. Reboot the Recalbox when prompted.

What it installs:
- A small Python daemon (`/recalbox/share/arcadematrix_daemon.py`) that polls
  `/tmp/es_state.inf` (EmulationStation's live state file) every 100ms, debounces rapid
  navigation (150ms), and publishes `{"status": "playing"|"browsing", "game": "<rom basename>",
  "system": "<SystemId>"}` over MQTT on `recalbox/system/playing` via `mosquitto_pub` - this is
  what `main.py`'s `_on_mqtt_message()` and `core/dmd_cache.py` consume to show a live marquee.
- A launcher script (`/recalbox/share/userscripts/arcadematrix_launcher(permanent).sh`) that
  EmulationStation calls on startup to keep the daemon running across reboots.

**Note for users who also have an ESP32 ArcadeMatrix device**: this exact daemon/wire-protocol was
ported to a friendlier, cross-platform (Windows/macOS/Linux) installer in the ESP32 project's
`ArcadeMatrix/tools/recalbox_daemon/` (`install.sh`/`install.ps1`, run from your PC instead of
manually over SSH). Either installer publishes the same MQTT format, so **one install serves both
an RPi and an ESP32 device simultaneously** if both subscribe to the same broker. If you only run
this RPi project, this script is all you need; the other repo's installer is just a more automated
way to deploy the same thing (worth adopting even here, if you'd rather not SSH in by hand -
`ArcadeMatrix/tools/recalbox_daemon/install.sh` works against a Recalbox regardless of which
project's frontend it's paired with).

**Normally this happens automatically via the web UI's SSH install feature** (`core/ssh_installer.py`,
triggered from the Settings page) - this script is the manual fallback for when you'd rather not
give the app your Recalbox's SSH credentials, or need to inspect/customize exactly what gets
installed before running it.
