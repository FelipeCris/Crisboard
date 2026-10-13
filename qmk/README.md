# Crisboard USB: recuperación y distribución Fn

## Estado del teclado

La rama `feature/rgb-presets` contiene [tres presets guardables desde el teclado](changes/rgb-presets.md),
compilados y cargados en ambas mitades, con lectura completa verificada.
EEPROM y bootloader se conservaron. El propietario confirmó los tres
presets, su persistencia al reconectar y el funcionamiento del resto del teclado. Solo añade tres teclas Fn y el módulo
aislado de persistencia; los indicadores Fn, bordes inversos, OLED, perrito
y las tablas Colemak/QWERTY se conservan.

Esta función añade 542 bytes de flash y 6 bytes de RAM estática por mitad,
además de 30 bytes de EEPROM para las tres ranuras. Quedan 3128/3058 bytes
de flash libres en izquierda/derecha. Las pruebas nativas del módulo C y las
verificaciones AVR pasaron en la [compilación de presets](https://github.com/FelipeCris/Crisboard/actions/runs/38433183294).

La nueva distribución Fn se cargó en ambas mitades el 13 de octubre de 2026.
Se verificaron los 32768 bytes de cada flash y se conservaron EEPROM y bootloader.
Solo cambian 24 bytes de las 14 posiciones Fn; Colemak y QWERTY y todos los bytes
fuera de la tabla de teclas son idénticos a la versión anterior.
El propietario confirmó que esta distribución Fn funciona como la solicitó.

### Instalación previa de las dos opciones de tamaño

El 13 de octubre de 2026 se cargaron las versiones que solo desactivan
CYCLE_SPIRAL y activan LTO en ambas mitades. Antes de escribir se verificó
el programa original de cada mitad y se respaldaron su flash y EEPROM.
La lectura completa posterior coincide exactamente con cada imagen prevista;
los bootloaders y los 1024 bytes de ajustes de cada mitad se conservaron.
El propietario confirmó la prueba de uso: escritura con ambas mitades,
Fn/play-pause, colores inversos de los bordes, brillo, modos RGB y perrito
funcionan como antes, con CYCLE_SPIRAL eliminado.

Durante la prueba se reportó un fallo momentáneo de Play/Pause. El monitor
de teclas multimedia de Windows registró sus pulsaciones y liberaciones; el
propietario confirmó después que volvió a funcionar sin otra carga ni cambios
de mapa. La causa del fallo momentáneo no se ha determinado.

La primera reconstrucción, que alteró comportamiento RGB, queda descartada.
Antes de esta carga se habían restaurado y verificado ambos originales y sus
ajustes; el propietario confirmó bordes inversos, play/pause y brillo.

## Fuentes conservados

- `legacy/crisboard/`: los diez archivos de la primera carpeta encontrada,
  preservados byte por byte y con su manifiesto SHA256. Difieren del instalado.
- `snapshots/2023-06/crisboard/`: copia sin modificar del archivo aportado
  `Crisboard 2023 jun.rar`; el manifiesto conserva el SHA256 del RAR y de cada
  archivo extraído. No contiene binarios ni la versión de QMK del propietario.
- `keyboards/crisboard/`: copia de ese RAR con CYCLE_SPIRAL desactivado,
  `LTO_ENABLE = yes`, la distribución Fn aprobada y el módulo de presets
  (dos archivos adicionales). Tres posiciones Fn ahora seleccionan presets.
- `recovered/keymap-only.c` y `keymap.json`: tabla leída de los dos programas
  originales, con códigos numéricos y posiciones físicas.
- `recovered/june-2023-comparison.json`: evidencia y límites de la comparación.

El RAR coincide con los 420 bytes del mapa de ambas mitades: 210 posiciones,
68 switches y dos huecos por capa. Coinciden también los 1344 bytes de la
fuente OLED, los 864 bytes del perrito, los rangos RGB de bordes/Fn y los
principales descriptores USB.

Frente a la primera carpeta, el RAR declara MASTER_LEFT, brillo OLED y RGB
máximo 255, textos Clmk/Base/Lower y los rangos simétricos de color inverso.
El respaldo izquierdo carece del bloque de apagado OLED por WPM que sí
aparece en el derecho y en el RAR. Esta diferencia se conserva al recuperar
la base de cada mitad; no se aplica como nueva función al izquierdo.

## Compilación y límites

Se usa como referencia compatible QMK 0.18.0, commit
`0a3f7e48690bb2b7b008300a54554979a55be19a`. No se ha identificado todavía
la revisión exacta del checkout original del propietario.

El workflow `QMK USB` fija las acciones por commit, verifica los paquetes de
compilador y registra herramientas/dependencias en el artefacto. La referencia
para AVR GCC 8.5 es el
[paquete histórico de MSYS2 mantenido por fauxpark](https://github.com/msys2/MINGW-packages/blob/6561e2269487ec2f86935be588af48275b4c215e/mingw-w64-avr-gcc/PKGBUILD).

`tools/verify_two_options.py` exige los diez archivos originales y los dos
del módulo de presets, con las opciones de tamaño y la integración aprobada.
Rechaza cambios en Colemak/QWERTY, otras teclas Fn, indicadores RGB, brillo,
fuente OLED y animación del perrito. `tools/preset_mapping.py` extiende la
distribución anterior de `tools/fn_mapping.py` con solo las tres posiciones
elegidas y genera la tabla completa para verificar el binario compilado.

`tools/reconstruct_baseline.py` recupera la diferencia OLED del izquierdo y
exige SHA256 idéntico del área completa de aplicación original (28672 bytes,
completando el final con 0xff). La comprobación se ejecuta antes de compilar
la optimización de cada mitad. Los dos hashes originales son:

- Izquierda: `01f934c4a40a9653e146a1cb1c0652e5a50bdb072af15a3f960c276f8daee1e5`.
- Derecha: `a9d131153a88eada4022603b994662ae9a67eafd35e4bf1d4b0ce5ac990e7abb`.

El verificador del `.hex` comprueba registros/checksums, límite de Caterina
`0x7000`, símbolo keymaps y coincidencia de los 420 bytes del mapa real.
**Compilar correctamente no basta para afirmar equivalencia con el instalado.**
No cargar un resultado que no haya superado la comparación completa de su base.

La comparación completa pasó con AVR GCC 8.5.0: las dos bases reproducen
exactamente los 28672 bytes de aplicación de sus respectivos respaldos.
[Compilación verificada](https://github.com/FelipeCris/Crisboard/actions/runs/38362814984),
fuentes `275b0fec6170437e83958c9cc11c238cf5b69c4a`.

| Mitad | Original | Solo espiral/LTO | Libre | Ahorro |
| --- | ---: | ---: | ---: | ---: |
| Izquierda | 28186 | 25002 | 3670 | 3184 |
| Derecha | 28264 | 25072 | 3600 | 3192 |

Tamaños en bytes de aplicación. La comparación incluye también mapa y todos
los fotogramas/fuente OLED en los binarios optimizados. La instalación física
es un paso separado que exige verificar la imagen anterior y leer lo escrito.

Desde un checkout QMK en la revisión fijada y con el toolchain preparado:

```text
bash qmk/tools/build_usb.sh RUTA_QMK RUTA_RESULTADOS
```

El script produce resultados separados para izquierda/derecha, base/optimizado,
con sus ELF, HEX, registros, tamaños y verificaciones. Los respaldos originales
y la EEPROM permanecen locales y no se suben al repositorio.

## Mapa instalado

La [nueva distribución Fn](changes/2026-10-13-fn-rgb-media.md) está compilada
y cargada en ambas mitades, con lectura completa verificada. Colemak y QWERTY
se conservan idénticos. El propietario confirmó que las nuevas funciones Fn y ambas capas base funcionan como pidió.

Colemak (0), QWERTY (1) y Lower/Fn (2). Mantener Fn activa Lower. Las dos
teclas interiores de la segunda fila seleccionan QWERTY (izquierda) y Colemak
(derecha) mediante DF(layer), para la sesión. El idioma de Windows determina
los caracteres de puntuación; los códigos son posiciones USB/HID.

Para repetir únicamente la extracción del mapa de uno de los backups conocidos:

```text
python qmk/tools/decode_keymap.py FIRMWARE.bin --json-out mapa.json --c-out keymap-only.c
```

## Programación

ATmega32U4, 16 MHz, Caterina/AVR109, USB por la izquierda. Cada mitad se
programa por separado después de RESET y con su resultado verificado.
Conservar el bootloader de 4096 bytes, respaldar los ajustes y verificar lo
escrito por lectura completa. El firmware original de cada mitad y sus ajustes
pueden restaurarse exactamente desde los respaldos locales ya verificados.

La configuración ZMK del inalámbrico y su workflow se conservan independientes.
Los encabezados de licencia históricos se mantienen; los scripts de recuperación
son GPL-2.0-or-later.
