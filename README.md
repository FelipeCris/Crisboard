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

La copia de trabajo contiene la [nueva distribución Fn](qmk/changes/2026-10-13-fn-rgb-media.md):
controles RGB a la izquierda y multimedia a la derecha. Colemak y QWERTY
se conservan íntegros. Esta revisión se compiló y cargó en ambas mitades;
la lectura completa confirma que solo cambiaron 24 bytes del mapa por mitad.
El propietario confirmó que Fn funciona como pidió y que Colemak/QWERTY se conservaron.

## Inalámbrico

La configuración ya existente utiliza ZMK:

- `config/west.yml` fija ZMK `c7fdce8` y Zephyr 3.0 `3861c95`, compatibles
  con las lecturas del teclado nice!nano v2.
- `build.yaml` contiene `crisboard_left`, `crisboard_right` y `settings_reset`
  para `nice_nano_v2`.
- `config/boards/shields/Crisboard/crisboard.keymap` contiene las capas del
  inalámbrico. Es independiente del mapa QMK leído en el cableado.
- `Firmware Oled 34rgb stable.zip` conserva tres imágenes `.uf2`: izquierda,
  derecha y reinicio de ajustes.

El mapa central leído de la placa coincide con las 204 asignaciones del
repositorio. El ZIP antiguo tiene dos teclas de puntuación intercambiadas y
carece de las correcciones USB/HID identificadas en lo instalado.

Esta rama prepara el porcentaje de batería local en ambas pantallas,
conservando el símbolo USB, mapas, RGB, Bluetooth y reposo. La compilación
compatible aplica únicamente la mejora oficial del widget de porcentaje.
Las cuatro compilaciones y verificaciones pasaron: la base derecha coincide
con todos los bytes de aplicación leídos; la izquierda solo difiere en
cuatro bytes del orden de dos conjuntos internos de dependencias con los
mismos miembros. Todos los demás bytes coinciden. Carga y prueba física
del porcentaje pendientes. [Resultados](zmk/verification/battery-percentage.json).

`Kconfig.defconfig` conserva su segundo bloque que repite
`if SHIELD_CRISBOARD_LEFT`; ese detalle histórico no se modifica como parte
del cambio de porcentaje.

## Organización recomendada

Mantener aquí las configuraciones personales y fijar las revisiones de QMK/ZMK
al preparar compilaciones reproducibles. Contribuir al repositorio oficial de
QMK sería un trabajo posterior de soporte de hardware y revisión comunitaria;
no hace falta para conservar o programar este teclado.
