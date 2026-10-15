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

La versión instalada contiene [tres presets RGB guardables](qmk/changes/rgb-presets.md)
con Fn + J/L/U en Colemak. Guardan la configuración base, sin capturar las
indicaciones temporales de Fn. La compilación y las pruebas del módulo C pasaron;
ambas mitades están cargadas y verificadas por lectura completa.
El propietario confirmó que los tres presets funcionan, se conservan al
reconectar y el resto del teclado sigue funcionando como antes. Añade 542 bytes de flash y 6 bytes
de RAM estática por mitad, con 30 bytes de EEPROM para los tres presets.
Colemak y QWERTY se conservan intactos.

La copia de trabajo añade un [modo RGB Uniforme](qmk/changes/uniform-mode.md),
seleccionable con Fn + Tab y guardable en los mismos presets. En ese modo,
Colemak ilumina también los bordes con el color base; los modos anteriores
conservan el color inverso. Esta ampliación está compilada y cargada en ambas mitades,
con lectura completa verificada. El propietario confirmó Uniforme, los modos
anteriores y la conservación de sus presets. Añade 40/42 bytes de flash en izquierda/derecha, sin aumentar RAM estática
ni EEPROM.

La rama `feature/rgb-presets` amplía ahora a [cinco presets](qmk/changes/five-rgb-presets.md):
añade Fn + Y y Fn + Ñ en Colemak como ranuras 4 y 5 (O/P en QWERTY).
Los tres guardados anteriores conservan sus direcciones y datos. Esta ampliación
está cargada en ambas mitades, con lectura completa verificada y EEPROM y
bootloader conservados. El propietario confirmó que Y y Ñ ya guardan, sin
otra carga ni cambios de firmware durante el diagnóstico. La persistencia de
las dos ranuras nuevas tras reconectar queda pendiente de confirmación.
Añade 20 bytes de EEPROM,
hasta 50 en total, sin aumentar flash ni RAM estática. Solo cambian cinco bytes
del programa por mitad: las dos teclas Fn y el límite de ranuras.

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

El mapa original leído de la placa coincide con las 204 asignaciones guardadas
en `zmk/verified-keymap.json`. El ZIP antiguo tiene dos teclas de puntuación intercambiadas y
carece de las correcciones USB/HID identificadas en lo instalado.

La primera revisión muestra el porcentaje de batería local en ambas pantallas,
conservando el símbolo USB, mapas, RGB, Bluetooth y reposo. La compilación
compatible aplica únicamente la mejora oficial del widget de porcentaje.
Las cuatro compilaciones y verificaciones pasaron: la base derecha coincide
con todos los bytes de aplicación leídos; la izquierda solo difiere en
cuatro bytes del orden de dos conjuntos internos de dependencias con los
mismos miembros. Todos los demás bytes coinciden. El 13 de octubre de 2026
se cargaron ambas mitades y una lectura posterior a RESET verificó todos
los bytes del programa nuevo y las zonas legibles fuera de las páginas
de carga. Los archivos excluyen ajustes y bootloader; estas zonas no
son legibles mediante CURRENT.UF2. La prueba funcional del propietario
sigue pendiente. [Resultados](zmk/verification/battery-percentage.json).

La revisión actual muestra voltaje en ambas pantallas, por ejemplo
`4.08 V`, manteniendo el porcentaje del servicio Bluetooth. Se obtiene el
voltaje ya guardado por el sensor durante la lectura existente; no se añade
otra conversión ADC ni cambia su intervalo. El texto se actualiza también
cuando cambia el voltaje y el porcentaje estimado permanece igual. Antes de
la primera lectura válida aparece `--.-- V`; un fallo conserva la última
lectura válida. El formato usa enteros y no requiere soporte printf de coma
flotante. Las compilaciones comparan la versión de porcentaje instalada y
la variante de voltaje, incluida configuración, devicetree y mapa real.
Las cuatro compilaciones y las pruebas del código C pasaron para la fuente
`f4965f2`. Las dos bases reproducen todos los bytes de las aplicaciones de
porcentaje leídas después de su instalación. La única opción compilada
distinta es `SHOW_VOLTAGE`; el devicetree y las 204 asignaciones del mapa
central coinciden. El enlazador mide +124 bytes de flash en la izquierda,
+116 en la derecha y +16 bytes de RAM por mitad. El 14 de octubre de 2026
se cargaron ambas mitades. Una lectura posterior a RESET verificó
todos los bytes del programa nuevo y las zonas legibles fuera de las
páginas de carga. Los UF2 excluyen ajustes y bootloader; CURRENT.UF2
no expone esas zonas. El propietario confirmó voltaje en ambas
pantallas e indica que las dos mitades funcionan. No se registró una
confirmación separada de Fn y RGB. [Resultados](zmk/verification/battery-voltage.json).

nice!nano v2 mide su alimentación VDDH. Al usar batería sirve para observar
la descarga; con USB, el circuito de carga puede elevar esa alimentación
respecto a los bornes de batería. Se conserva el símbolo de alimentación
USB y no se aplica una compensación supuesta. Véanse el
[esquema oficial](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/)
y el [sensor de esta revisión ZMK](https://github.com/zmkfirmware/zmk/blob/c7fdce863ac2f03bc70495f9904b127f2d99d85c/app/drivers/sensor/battery/battery_nrf_vddh.c).

`Kconfig.defconfig` conserva su segundo bloque que repite
`if SHIELD_CRISBOARD_LEFT`; ese detalle histórico no se modifica como parte
de los cambios de visualización de batería.

## Organización recomendada

La [primera etapa de migración del mapa inalámbrico](zmk/changes/2026-10-14-wireless-shortcuts.md)
reubica los tres perfiles Bluetooth, borrar perfil y USB/Bluetooth en las
posiciones acordadas de Fn. Corrige la prioridad de Fn en QWERTY y unifica
su posición con Colemak/QMK. El resto de la migración se hará por etapas.
La compilación y sus verificaciones pasaron para ambas mitades; la aplicación
de la derecha era idéntica a la instalada y en esa etapa solo se cargó la izquierda.
La izquierda está cargada y verificada por lectura; el propietario confirmó
la prueba funcional de esta etapa. Esta revisión conserva el voltaje.

La [revisión que completa el mapa Fn de QMK](zmk/changes/2026-10-14-qmk-fn.md)
añade las teclas multimedia, los controles RGB en sus posiciones QMK y cinco
presets guardables desde el teclado. El indicador muestra siempre el perfil
Bluetooth seleccionado y la preferencia USB/Bluetooth, diferenciándolos de
la salida efectiva. Las cuatro compilaciones y las pruebas de presets, batería y
mapa real pasaron para `b47294b`. Ambas mitades se cargaron y verificaron por
lectura. El usuario confirmó la prueba funcional.
[Resultados](zmk/verification/qmk-fn.json). Esta fase conserva los cuatro
efectos nativos ZMK; los efectos QMK, colores por tecla y perrito quedan para
etapas posteriores.

Mantener aquí las configuraciones personales y fijar las revisiones de QMK/ZMK
al preparar compilaciones reproducibles. Contribuir al repositorio oficial de
QMK sería un trabajo posterior de soporte de hardware y revisión comunitaria;
no hace falta para conservar o programar este teclado.

## Modo Bordes inversos en ZMK

La [fase de bordes inversos](zmk/changes/2026-10-14-inverse-borders.md) añade un
quinto modo en Fn + Tab, con las mismas 17 posiciones LED de borde por mitad
que QMK. En Colemak desplaza el tono del borde 180° y conserva saturación y
brillo; en QWERTY se muestra uniforme. Los cuatro modos anteriores y sus
presets conservan sus identificadores. El nuevo modo también se guarda y
recupera desde los cinco presets. No cambia el mapa, Bluetooth ni voltaje.
Estado: cuatro compilaciones y verificaciones aprobadas; carga y prueba física pendientes.
[Resultados](zmk/verification/inverse-borders.json).
