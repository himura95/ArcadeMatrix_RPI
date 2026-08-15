🇬🇧 [English](README.md) | 🇫🇷 [Français](README_FR.md) | 🇪🇸 Español

# tools/

Utilidades del lado del PC/manuales para ArcadeMatrix_RPi. No forman parte de la aplicación
Flask/API - las ejecutas tú mismo, por separado, ya sea en tu propio ordenador o copiándolas a tu
Recalbox.

## `mugen_extractor/`

Convierte los archivos de personajes de MUGEN (`.sff`/`.air`) al formato binario de sprite `.fgt`
usado tanto por `engines/fighter.py` de este proyecto **como** por el `FighterEngine` (C++) del
proyecto hermano ESP32 - es la misma herramienta, mantenida idéntica en ambos repositorios ya que
no existe un mecanismo de paquetes compartido entre estas dos bases de código independientes. Ver
`mugen_extractor/README_ES.md` para el uso completo.

## `recalbox_setup_mqtt.sh`

Un script de shell independiente que copias en tu Recalbox y ejecutas **directamente en el
dispositivo por SSH** (no desde tu PC) para instalar el daemon MQTT de "reproduciendo ahora":

1. `ssh root@<ip-recalbox>` (contraseña: `recalboxroot`)
2. Edita la variable `MQTT_BROKER` al inicio de este script con la IP de tu Raspberry Pi (el que
   ejecuta ArcadeMatrix_RPi y la matriz LED).
3. Copia/pega el script en la Recalbox (ej.: `scp tools/recalbox_setup_mqtt.sh root@<ip-recalbox>:/tmp/` y luego `ssh root@<ip-recalbox> "sh /tmp/recalbox_setup_mqtt.sh"`).
4. Reinicia la Recalbox cuando se te indique.

Lo que instala:
- Un pequeño daemon en Python (`/recalbox/share/arcadematrix_daemon.py`) que consulta
  `/tmp/es_state.inf` (el archivo de estado en vivo de EmulationStation) cada 100ms, filtra los
  cambios rápidos de navegación (150ms), y publica `{"status": "playing"|"browsing", "game":
  "<nombre base de la rom>", "system": "<SystemId>"}` vía MQTT en el topic
  `recalbox/system/playing` mediante `mosquitto_pub` - esto es lo que consumen `_on_mqtt_message()`
  de `main.py` y `core/dmd_cache.py` para mostrar un marquee en vivo.
- Un script de lanzamiento (`/recalbox/share/userscripts/arcadematrix_launcher(permanent).sh`) que
  EmulationStation invoca al arrancar para mantener el daemon activo tras cada reinicio.

**Nota para usuarios que también tienen un dispositivo ESP32 ArcadeMatrix**: este mismo daemon/
protocolo de comunicación fue trasladado a un instalador multiplataforma más amigable
(Windows/macOS/Linux) en `ArcadeMatrix/tools/recalbox_daemon/` del proyecto ESP32
(`install.sh`/`install.ps1`, para ejecutar desde tu PC en lugar de hacer SSH manual). Ambos
instaladores publican el mismo formato MQTT, así que **una sola instalación puede servir a la vez
a un dispositivo RPi y a un dispositivo ESP32** si ambos están suscritos al mismo broker. Si solo
usas este proyecto RPi, este script es todo lo que necesitas; el instalador del otro repositorio es
solo una forma más automatizada de desplegar lo mismo (vale la pena adoptarlo incluso aquí si
prefieres evitar el SSH manual - `ArcadeMatrix/tools/recalbox_daemon/install.sh` funciona contra
una Recalbox sin importar con qué proyecto frontend esté emparejada).

**Normalmente esto ocurre automáticamente mediante la función de instalación SSH de la interfaz
web** (`core/ssh_installer.py`, activada desde la página de Ajustes) - este script es el recurso
manual para quienes prefieren no dar sus credenciales SSH de Recalbox a la aplicación, o necesitan
inspeccionar/personalizar exactamente lo que se instala antes de ejecutarlo.
