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

Estado: código preparado; compilación e instalación de esta revisión pendientes.
La versión previamente instalada conserva el mapa original y las dos opciones
de tamaño. No se modifican los fuentes históricos ni los respaldos.
