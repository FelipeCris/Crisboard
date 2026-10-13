# Crisboard USB: recuperaci?n y dos opciones de tama?o

## Estado del teclado

El 13 de octubre de 2026 se restauraron el programa y los ajustes originales
de ambas mitades despu?s de una reconstrucci?n que alter? comportamiento RGB.
Se verificaron por lectura completa; el propietario confirm? que volvieron
los bordes de color inverso, play/pause y el brillo anterior. Esa reconstrucci?n
queda descartada. El teclado no tiene todav?a aplicados LTO ni la eliminaci?n
de CYCLE_SPIRAL.

## Fuentes conservados

- `legacy/crisboard/`: los diez archivos de la primera carpeta encontrada,
  preservados byte por byte y con su manifiesto SHA256. Difieren del instalado.
- `snapshots/2023-06/crisboard/`: copia sin modificar del archivo aportado
  `Crisboard 2023 jun.rar`; el manifiesto conserva el SHA256 del RAR y de cada
  archivo extra?do. No contiene binarios ni la versi?n de QMK del propietario.
- `keyboards/crisboard/`: copia de ese RAR con solo CYCLE_SPIRAL desactivado
  en `config.h` y `LTO_ENABLE = yes` en `rules.mk`.
- `recovered/keymap-only.c` y `keymap.json`: tabla le?da de los dos programas
  originales, con c?digos num?ricos y posiciones f?sicas.
- `recovered/june-2023-comparison.json`: evidencia y l?mites de la comparaci?n.

El RAR coincide con los 420 bytes del mapa de ambas mitades: 210 posiciones,
68 switches y dos huecos por capa. Coinciden tambi?n los 1344 bytes de la
fuente OLED, los 864 bytes del perrito, los rangos RGB de bordes/Fn y los
principales descriptores USB.

Frente a la primera carpeta, el RAR declara MASTER_LEFT, brillo OLED y RGB
m?ximo 255, textos Clmk/Base/Lower y los rangos sim?tricos de color inverso.
El respaldo izquierdo carece del bloque de apagado OLED por WPM que s?
aparece en el derecho y en el RAR. Esta diferencia se conserva al recuperar
la base de cada mitad; no se aplica como nueva funci?n al izquierdo.

## Compilaci?n y l?mites

Se usa como referencia compatible QMK 0.18.0, commit
`0a3f7e48690bb2b7b008300a54554979a55be19a`. No se ha identificado todav?a
la revisi?n exacta del checkout original del propietario.

El workflow `QMK USB` fija las acciones por commit, verifica los paquetes de
compilador y registra herramientas/dependencias en el artefacto. La referencia
para AVR GCC 8.5 es el
[paquete hist?rico de MSYS2 mantenido por fauxpark](https://github.com/msys2/MINGW-packages/blob/6561e2269487ec2f86935be588af48275b4c215e/mingw-w64-avr-gcc/PKGBUILD).

`tools/verify_two_options.py` exige que la copia de trabajo conserve los diez
archivos y solo contenga las dos diferencias solicitadas. Rechaza cambios en
mapa, indicadores RGB, brillo, fuente OLED y animaci?n del perrito.

`tools/reconstruct_baseline.py` recupera la diferencia OLED del izquierdo y
exige SHA256 id?ntico del ?rea completa de aplicaci?n original (28672 bytes,
completando el final con 0xff). La comprobaci?n se ejecuta antes de compilar
la optimizaci?n de cada mitad. Los dos hashes originales son:

- Izquierda: `01f934c4a40a9653e146a1cb1c0652e5a50bdb072af15a3f960c276f8daee1e5`.
- Derecha: `a9d131153a88eada4022603b994662ae9a67eafd35e4bf1d4b0ce5ac990e7abb`.

El verificador del `.hex` comprueba registros/checksums, l?mite de Caterina
`0x7000`, s?mbolo keymaps y coincidencia de los 420 bytes del mapa real.
**Compilar correctamente no basta para afirmar equivalencia con el instalado.**
No cargar un resultado que no haya superado la comparaci?n completa de su base.

La comparaci?n completa pas? con AVR GCC 8.5.0: las dos bases reproducen
exactamente los 28672 bytes de aplicaci?n de sus respectivos respaldos.
[Compilaci?n verificada](https://github.com/FelipeCris/Crisboard/actions/runs/38362814984),
fuentes `275b0fec6170437e83958c9cc11c238cf5b69c4a`.

| Mitad | Original | Solo espiral/LTO | Libre | Ahorro |
| --- | ---: | ---: | ---: | ---: |
| Izquierda | 28186 | 25002 | 3670 | 3184 |
| Derecha | 28264 | 25072 | 3600 | 3192 |

Tama?os en bytes de aplicaci?n. La comparaci?n incluye tambi?n mapa y todos
los fotogramas/fuente OLED en los binarios optimizados. La instalaci?n f?sica
es un paso separado que exige verificar la imagen anterior y leer lo escrito.

Desde un checkout QMK en la revisi?n fijada y con el toolchain preparado:

```text
bash qmk/tools/build_usb.sh RUTA_QMK RUTA_RESULTADOS
```

El script produce resultados separados para izquierda/derecha, base/optimizado,
con sus ELF, HEX, registros, tama?os y verificaciones. Los respaldos originales
y la EEPROM permanecen locales y no se suben al repositorio.

## Mapa instalado

Colemak (0), QWERTY (1) y Lower/Fn (2). Mantener Fn activa Lower. Las dos
teclas interiores de la segunda fila seleccionan QWERTY (izquierda) y Colemak
(derecha) mediante DF(layer), para la sesi?n. El idioma de Windows determina
los caracteres de puntuaci?n; los c?digos son posiciones USB/HID.

Para repetir ?nicamente la extracci?n del mapa de uno de los backups conocidos:

```text
python qmk/tools/decode_keymap.py FIRMWARE.bin --json-out mapa.json --c-out keymap-only.c
```

## Programaci?n

ATmega32U4, 16 MHz, Caterina/AVR109, USB por la izquierda. Cada mitad se
programa por separado despu?s de RESET y con su resultado verificado.
Conservar el bootloader de 4096 bytes, respaldar los ajustes y verificar lo
escrito por lectura completa. El firmware original de cada mitad y sus ajustes
pueden restaurarse exactamente desde los respaldos locales ya verificados.

La configuraci?n ZMK del inal?mbrico y su workflow se conservan independientes.
Los encabezados de licencia hist?ricos se mantienen; los scripts de recuperaci?n
son GPL-2.0-or-later.
