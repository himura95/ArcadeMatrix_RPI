# Guía de Inicio Rápido

Esta guía le ayudará a instalar y configurar ArcadeMatrix en su Raspberry Pi.

## 1. Instalación (Recomendada)

Proporcionamos una imagen precompilada lista para usar.

1. Grabe el archivo `ArcadeMatrix_Release.img` en su tarjeta SD usando **Raspberry Pi Imager**.
2. Una vez terminado, vuelva a insertar la tarjeta SD en su PC/Mac. Aparecerá una unidad USB de 8GB llamada **DATA**.
3. Abra el archivo `conf.ini` ubicado en esta unidad **DATA** para introducir sus credenciales de Wi-Fi (`SSID` y `PASS`) y el tamaño de su matriz.
4. Inserte la tarjeta SD en la Raspberry Pi y enciéndala. ¡La dirección IP se mostrará en la matriz!

## 2. Configuración Web

Una vez que la Pi esté encendida, abra un navegador en su teléfono o PC y vaya a:
`http://<IP_DE_RASPBERRY>:8080`

Aquí podrá configurar:
- Colores, fuentes y temas del reloj y la fecha.
- Funciones habilitadas en el bucle de rotación.
- Brillo y modo nocturno.

## 3. Añadir Contenido (GIFs, Sprites, Fuentes)

Para añadir sus propios medios, **simplemente conecte su tarjeta SD a su PC/Mac**.
La unidad **DATA** aparecerá como una memoria USB estándar (formato exFAT):

- **GIFs**: Déjelos en la carpeta `gifs/`.
- **Sprites MUGEN**: Use nuestro extractor para generar archivos `.fgt` y colóquelos en `fighters_32/` o `fighters_64/`.
- **Fuentes**: Deje las fuentes `.ttf` o `.bdf` en la carpeta `fonts/`.

*(La adición de medios se hace exclusivamente conectando la tarjeta SD a un ordenador o por SSH/SFTP. Si usa SSH, asegúrese de montar primero la partición DATA. No hay función de carga vía web).*

## 4. Conexión de Hardware

Recomendamos utilizar un Adafruit RGB Matrix HAT o Bonnet conectado a una Raspberry Pi Zero 2 W o Pi 4. Asegúrese de que el conector HUB75 esté correctamente enchufado a su panel LED.
