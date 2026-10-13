# Crisboard cableado: fuentes históricos y mapa instalado

El Crisboard cableado utiliza QMK sobre ATmega32U4. Se leyeron ambas mitades
mediante Caterina, sin escribir en el teclado. Cada flash se leyó dos veces y
las dos copias coincidieron. El mapa de teclas y el bootloader son idénticos
entre mitades; el programa compilado y la EEPROM difieren.

## Contenido

- `legacy/crisboard/`: copia sin cambios de los diez archivos de la carpeta
  histórica del propietario. No es una reconstrucción del programa instalado.
- `legacy/source-manifest.json`: SHA256 de cada archivo histórico copiado.
- `recovered/keymap-only.c`: tabla de teclas reconstruida de la flash real.
  No incluye las implementaciones instaladas de OLED, RGB o transporte split.
- `recovered/keymap.json`: códigos numéricos originales, matriz y posiciones
  físicas de las tres capas.
- `tools/decode_keymap.py`: decodificador de los dos respaldos verificados.

Los binarios de respaldo y la EEPROM se conservaron localmente. Sus huellas:

| Mitad | SHA256 de flash completa, 32768 bytes |
| --- | --- |
| Izquierda | `069eae24b773643071d7ad368c4b63536e603040775edea4b1e86a19c22b935d` |
| Derecha | `32347d004cb6d5b779809a92848d4117994e7b0a412bd19088aaed46d8d6c90f` |

No se identificó la versión exacta de QMK en el binario. La tabla usa los
valores históricos de keycodes documentados en
[`quantum_keycodes.h` de QMK 0.18.0](https://github.com/qmk/qmk_firmware/blob/0.18.0/quantum/quantum_keycodes.h).
Esa referencia permite decodificarla; **no prueba que se compilara con 0.18.0**.
La disposición matriz→teclas se tomó del `LAYOUT` en `legacy/crisboard/crisboard.h`.

## Lo comprobado del mapa instalado

Las capas son Colemak (0), QWERTY (1) y Lower/Fn (2). La tabla común ocupa
420 bytes en `0x047e..0x0621`. Contiene 68 switches físicos y dos posiciones
sin switch por capa.

El mapa no coincide exactamente con `Estable.zip`, `Estable2.zip`,
`Final Entrega.zip` ni con el `keymap.c` histórico suelto. Por eso se conservan
separados los fuentes encontrados y la tabla recuperada.

Mantener Fn entra en Lower. Las dos teclas interiores de la segunda fila
seleccionan QWERTY (izquierda) y Colemak (derecha) mediante `DF(layer)`.
Esto cambia la capa base de la sesión; no la guarda en EEPROM.

Las etiquetas de puntuación en C son posiciones USB/HID, no una distribución
de idioma. Los caracteres resultantes dependen de la distribución de Windows.

## Cómo se programa el cableado

1. Se edita `keymap.c` para las teclas/capas, `config.h` para pines y opciones,
   y el código de OLED/RGB cuando corresponde.
2. Se compila con QMK para obtener un `.hex` de aplicación. Debe elegirse una
   revisión de QMK y una herramienta de compilación concretas.
3. Con un firmware ya validado, QMK Toolbox permite seleccionar ATmega32U4 y
   programar por Caterina tras pulsar RESET. Se trata cada mitad por separado.

**Estos fuentes todavía no constituyen un firmware actualizado y validado.**
Antes de compilar con QMK actual hay que portar las definiciones antiguas,
integrar el mapa recuperado y verificar RGB, OLED, pines y rol de cada mitad.
No se ha compilado ni programado ningún firmware nuevo en esta recuperación.

En particular, los fuentes históricos declaran `MASTER_RIGHT`, mientras la
conexión habitual observada fue por la izquierda. Esto no basta para deducir
cómo se compiló cada programa instalado.

El ATmega32U4 tiene 32768 bytes de flash; Caterina ocupa los últimos 4096.
En las imágenes leídas quedan 486 bytes (izquierda) y 408 (derecha) de `0xff`
al final del área de aplicación. Es una observación del binario, no un informe
de tamaño del enlazador; hay poco margen y habrá que medir cada compilación.

Documentación: [compilación QMK](https://docs.qmk.fm/newbs_building_firmware),
[Caterina](https://docs.qmk.fm/flashing#caterina),
[capas](https://docs.qmk.fm/feature_layers).

## Mejoras que conviene evaluar

Consultado el 13 de octubre de 2026. Son opciones de QMK actual, no funciones
que se hayan incorporado al teclado durante esta recuperación:

- [Layer Lock](https://docs.qmk.fm/features/layer_lock): mantener Fn activo
  sin sostener la tecla. Sería útil para F1–F12 y ajustes RGB prolongados.
- [Repeat Key](https://docs.qmk.fm/features/repeat_key): repetir la última
  tecla o combinación; puede resultar cómodo al escribir en Colemak.
- [Caps Word](https://docs.qmk.fm/features/caps_word): escribir una palabra
  en mayúsculas y salir automáticamente al terminarla. No es necesariamente
  una novedad posterior a este firmware, cuya versión exacta desconocemos.
- [Chordal Hold y Flow Tap](https://docs.qmk.fm/tap_hold): evaluar solo si
  se decide convertir letras en modificadores al mantenerlas. El mapa actual
  utiliza modificadores dedicados.

Primero conviene portar y medir. Por ejemplo, los fuentes históricos incluyen
`config_common.h`, `RGB_DI_PIN` y un callback RGB que devuelve `void`; QMK
ha cambiado esas interfaces. Véanse los cambios de
[noviembre de 2022](https://docs.qmk.fm/ChangeLog/20221126) y
[mayo de 2023](https://docs.qmk.fm/ChangeLog/20230528).
La guía oficial para AVR recomienda evaluar `LTO_ENABLE = yes` para reducir
el tamaño: [optimización de flash](https://docs.qmk.fm/squeezing_avr).
No se ha medido cuánto ahorraría en este teclado.

## Reproducir la recuperación del mapa

Con Python 3 y el respaldo local de cualquiera de las dos mitades:

```text
python qmk/tools/decode_keymap.py RUTA_A_FIRMWARE.bin --json-out mapa.json --c-out keymap-only.c
```

El programa rechaza imágenes con otra huella. Solo lee archivos y genera
los resultados solicitados; no accede al teclado.

Los encabezados de licencia de los fuentes históricos se preservan. El
decodificador y el mapa recuperado se publican como GPL-2.0-or-later, en
concordancia con esos fuentes. Esto no cambia la licencia del resto del repo.
