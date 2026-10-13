# Crisboard

Configuraciones personales de dos variantes del teclado Crisboard.

| Variante | Firmware | Controlador | Ubicación |
| --- | --- | --- | --- |
| Inalámbrica | ZMK | La matriz de compilación selecciona `nice_nano_v2` | `config/`, `build.yaml` |
| Cableada USB | QMK | ATmega32U4 / Caterina, verificados por lectura | `qmk/` |

## Cableado USB

En [`qmk/README.md`](qmk/README.md) están los fuentes históricos, el mapa
recuperado de las dos mitades y el procedimiento de programación. Las bases
recuperadas reproducen byte por byte los programas originales de ambas mitades.

La versión con `CYCLE_SPIRAL` desactivado y LTO activado se cargó el
13 de octubre de 2026 y se verificaron mediante lectura completa, conservando
el bootloader y los ajustes de cada mitad. El propietario confirmó que ambas
mitades, Fn/play-pause, colores, brillo, modos RGB y perrito funcionan como antes. La primera reconstrucción se descartó.

La copia de trabajo prepara ahora la [nueva distribución Fn](qmk/changes/2026-10-13-fn-rgb-media.md):
controles RGB a la izquierda y multimedia a la derecha. Colemak y QWERTY
se conservan íntegros. Esta revisión debe compilarse y cargarse por separado.

## Inalámbrico

La configuración ya existente utiliza ZMK:

- `config/west.yml` obtiene ZMK desde `zmkfirmware/zmk`, revisión `main`.
- `build.yaml` contiene `crisboard_left`, `crisboard_right` y `settings_reset`
  para `nice_nano_v2`.
- `config/boards/shields/Crisboard/crisboard.keymap` contiene las capas del
  inalámbrico. Es independiente del mapa QMK leído en el cableado.
- `Firmware Oled 34rgb stable.zip` conserva tres imágenes `.uf2`: izquierda,
  derecha y reinicio de ajustes.

La presencia de esos archivos identifica la configuración conservada, no
confirma qué imagen está actualmente instalada en las placas inalámbricas.

La configuración y el workflow ZMK se conservan sin cambios. No se ha
verificado una compilación actual: ambos siguen `main` y la configuración
es histórica. Además, `Kconfig.defconfig` repite `if SHIELD_CRISBOARD_LEFT`
en un segundo bloque que declara nombre/rol de la derecha; debe revisarse
antes de atribuirle un fallo o preparar una actualización.

## Organización recomendada

Mantener aquí las configuraciones personales y fijar las revisiones de QMK/ZMK
al preparar compilaciones reproducibles. Contribuir al repositorio oficial de
QMK sería un trabajo posterior de soporte de hardware y revisión comunitaria;
no hace falta para conservar o programar este teclado.
