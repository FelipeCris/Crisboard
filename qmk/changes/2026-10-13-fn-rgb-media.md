# Cambios de Fn: RGB a la izquierda y multimedia a la derecha

Esta revisión modifica exclusivamente la capa Lower/Fn. Colemak y QWERTY
conservan los 140 códigos de sus tablas originales. Se mantienen LTO activado,
CYCLE_SPIRAL desactivado, indicadores RGB, brillo máximo, OLED y perrito.

Las posiciones se identifican por la función o tecla que tenían antes en Fn:

| Posición anterior | Nueva función con Fn | Código QMK |
| --- | --- | --- |
| Caps, izquierda | Brillo RGB − | `RGB_VAD` |
| Q, izquierda | Brillo RGB + | `RGB_VAI` |
| Tab, izquierda | Siguiente modo RGB | `RGB_MODE_FORWARD` |
| A, izquierda | Tono RGB + | `RGB_HUI` |
| Shift izquierdo | Saturación RGB − | `RGB_SAD` |
| `KC_NONUS_BACKSLASH`, junto a Shift | Saturación RGB + | `RGB_SAI` |
| ↑, antiguo modo RGB | Volumen + | `KC_VOLU` |
| ↓, antigua saturación + | Volumen − | `KC_VOLD` |
| →, antiguo tono + | Canción siguiente | `KC_MNXT` |
| ←, antiguo brillo + | Canción anterior | `KC_MPRV` |
| Espacio de la derecha | Play/Pause | `KC_MPLY` |
| Enter, pulgar de la derecha | Mute | `KC_MUTE` |
| Antiguo Mute, L en Colemak / U en QWERTY | Letra de la capa base activa | `KC_TRNS` |
| Antiguo Play/Pause, U en Colemak / I en QWERTY | Letra de la capa base activa | `KC_TRNS` |

`tools/fn_mapping.py` enumera las 14 posiciones y sus valores de QMK 0.18.0.
La compilación compara los 420 bytes del mapa completo con el resultado
esperado, incluidos Colemak y QWERTY sin cambios. Las bases originales siguen
verificándose byte por byte contra sus respaldos antes de compilar cada mitad.

Estado: compilación completada y ambas mitades cargadas el 13 de octubre de
2026. La lectura completa confirma las imágenes previstas; EEPROM y bootloader
se conservaron. En cada programa cambiaron únicamente 24 bytes de la tabla de
teclas; todo el programa fuera de esa tabla es idéntico a la versión anterior.
El propietario confirmó que los controles Fn funcionan como los solicitó
y que Colemak y QWERTY se conservaron.

[Verificación de compilación y carga](2026-10-13-fn-rgb-media-verification.json).
[Compilación QMK USB](https://github.com/FelipeCris/Crisboard/actions/runs/38424635539),
fuentes `ecdcc049787e7795e112281a623402e573ebc633`.
Los fuentes históricos y respaldos se conservan.
