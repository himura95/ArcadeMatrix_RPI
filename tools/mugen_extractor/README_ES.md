🇬🇧 [English](README.md) | 🇫🇷 [Français](README_FR.md) | 🇪🇸 Español

# ArcadeMatrix MUGEN Sprite Extractor

Este script de Python (`mugen_extractor.py`) está diseñado a medida para extraer, optimizar y convertir personajes del motor de juegos de lucha **MUGEN** para hacerlos compatibles con los `FighterEngine` de ArcadeMatrix (tanto en la versión ESP32 C++ como en la versión Raspberry Pi Python).

## ¿Para qué sirve?

Los juegos de lucha (MUGEN en particular) gestionan sprites con paletas de colores complejas (`.act`, `.sff`) y scripts de animación (`.air`) que incluyen retrasos variables entre cada frame, así como cajas de colisión.

Además, el tamaño de una matriz LED es muy limitado (p. ej. 64x32). Los sprites originales de MUGEN suelen ser demasiado grandes y no siempre tienen la misma alineación de una animación a otra (por ejemplo, un personaje saltando tendrá una imagen más grande que se expande hacia arriba).

El objetivo de esta herramienta es:
1. **Leer los formatos nativos de MUGEN** (`.sff` v1 y `.air`).
2. **Decodificar la paleta maestra** (para que los colores sean correctos).
3. **Seleccionar solo las animaciones necesarias** para ArcadeMatrix (`walk`, `attack`, `hit`, `win`, `special`, `super`, `fall`).
4. **Calcular una escala uniforme** basada en la altura estándar del personaje (en posición `stand` o `walk`) para que encaje dentro de la altura de tu matriz LED (p. ej. 32 píxeles).
5. **Generar una alineación perfecta (Virtual Ground)**: la herramienta calcula una bounding box global para garantizar que la línea de suelo (`ground_y`) y el centro del personaje (`origin_x`) permanezcan perfectamente fijos de una animación a otra. ¡Esto evita que el personaje «tiemble» o cambie de tamaño al atacar!
6. **Convertir a `.fgt` (Fighter Format)**: el formato `.fgt` es un formato binario optimizado creado específicamente para ArcadeMatrix, que almacena píxeles en RGB565 con un código de color transparente, listo para ser leído a máxima velocidad por el ESP32 y la Raspberry Pi.

## Requisitos previos

Asegúrate de tener Python 3 instalado junto con la biblioteca de imágenes PIL (Pillow):

```bash
pip install Pillow
```

## Estructura del directorio MUGEN

El script espera que proporciones una carpeta fuente que contenga varias subcarpetas, una por personaje. Cada personaje debe contener al menos sus archivos `.sff` y `.air`.

Ejemplo:
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

## Cómo usarlo

Ejecuta el script con argumentos de línea de comandos - no hace falta editar ningún código:

```bash
python mugen_extractor.py --src /Ruta/A/Tus/Personajes/Mugen/chars --dest ./fighters_32
```

Opciones:
| Opción | Por defecto | Descripción |
|---|---|---|
| `--src` | *(obligatorio)* | Carpeta que contiene tus subcarpetas de personajes MUGEN. |
| `--dest` | `./fighters_32` | Carpeta de salida para los archivos `.fgt` generados + `index.json`/`index.txt`. |
| `--mode` | `FULLSIZE` | `SCALED` redimensiona los personajes para ajustarse exactamente a la altura del panel (ESP32 estándar, sin PSRAM); `FULLSIZE` mantiene la escala 1:1 (recomendado en RPi, que no tiene esa limitación de memoria). |
| `--compress` | desactivado | Comprime los archivos `.fgt` de salida en gzip (`.fgt.gz`) para ahorrar espacio en disco. |

Para generar tanto una matriz de 32px como de 64px, simplemente ejecútalo dos veces con carpetas `--dest` diferentes:

```bash
python mugen_extractor.py --src /Ruta/A/Tus/Personajes/Mugen/chars --dest ./fighters_32
python mugen_extractor.py --src /Ruta/A/Tus/Personajes/Mugen/chars --dest ./fighters_64
```

### Proceso de extracción

El script creará (o vaciará) las carpetas `fighters_32` y `fighters_64`. Para cada personaje, creará una subcarpeta (p. ej. `fighters_32/Ryu/`) que contendrá:
- `walk.fgt`
- `attack.fgt`
- `hit.fgt`
- `win.fgt`
- *(y opcionalmente `special1.fgt`, `super1.fgt`, `fall.fgt` si se encuentran)*

También genera dos archivos de índice en la raíz de la carpeta de exportación:
- `index.json`
- `index.txt`

Estos archivos de índice contienen los metadatos (Height, `ground_y`, `origin_x`, etc.) necesarios para que los motores de renderizado de ArcadeMatrix posicionen correctamente a los luchadores en la matriz.

## ¿Por qué antes los personajes ignoraban la línea de suelo?

Anteriormente, cada animación (`walk`, `attack`) se escalaba de forma aislada recortando los píxeles transparentes. Como resultado, un ataque alto hacía que la imagen de ataque fuera más grande que la imagen de caminar, cambiando la escala y desplazando al personaje hacia abajo.

Con esta versión **v4**, el script realiza dos pasadas:
1. Mide las proporciones máximas globales del personaje a lo largo de todas sus animaciones combinadas.
2. Aplica una relación de escala estricta basada únicamente en su animación de caminar/reposo.
3. Dibuja todos los frames sobre un «Canvas» global de tamaño fijo (p. ej. 48x48), para que el eje de los pies del personaje siempre caiga en el píxel exacto `ground_y`. ¡Los motores leen ese valor `ground_y` para alinearlos entre sí!

---
*Este script es open source y está diseñado para el ecosistema ArcadeMatrix.*
