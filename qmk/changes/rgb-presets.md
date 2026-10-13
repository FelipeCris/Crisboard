# Tres presets RGB guardables desde el teclado

Rama `feature/rgb-presets`, basada en el PR #1 ya fusionado. Estado:
compilación y verificaciones completas; ambas mitades cargadas el 13 de
octubre de 2026. La lectura completa de cada flash coincide con su imagen
prevista; se conservaron los 4096 bytes de bootloader y los 1024 bytes de EEPROM
de cada mitad. El propietario confirmó que los tres presets se guardan y cargan, sobreviven
a la reconexión USB y que indicadores, multimedia, escritura y perrito
siguen funcionando como antes.

Fuentes compilados: `4f9f83c6db5dcc1c17b7652df10688713a15539d`.
[Compilación QMK USB](https://github.com/FelipeCris/Crisboard/actions/runs/38433183294).
[Resultados verificados](rgb-presets-verification.json).

## Uso

| Preset | Colemak | QWERTY, misma posición física |
| --- | --- | --- |
| 1 | Fn + J | Fn + Y |
| 2 | Fn + L | Fn + U |
| 3 | Fn + U | Fn + I |

- Un toque carga el preset al soltar la tecla.
- Mantener Fn y la tecla durante dos segundos guarda la configuración actual.
  Se guarda una sola vez por pulsación; soltar después no vuelve a cargarla.
- Antes de guardar, ajustar normalmente color, saturación, brillo, efecto y
  velocidad. También se conserva si RGB estaba encendido o apagado.
- Una ranura vacía o inválida no altera la iluminación.
- Las tablas Colemak y QWERTY no cambian; solo se reasignan tres posiciones Fn.

Se guarda la configuración RGB base leída por las API de QMK, sin copiar los
colores finales de los LED ni las variables usadas para pintar indicadores.
Por eso guardar con Fn pulsado no captura sus indicadores temporales. La
lógica original de Fn y de los bordes de color inverso permanece idéntica;
se vuelve a calcular sobre el color base recuperado. OLED y perrito permanecen
sin cambios.

## Persistencia

Las tres ranuras ocupan 30 bytes, direcciones EEPROM 64–93. Cada registro de
10 bytes contiene firma, versión, HSV, efecto, velocidad, encendido y CRC-8.
La zona estaba vacía en ambos respaldos de la versión instalada. Se reserva
fuera de los ajustes nativos de QMK (0–34) y de los cuatro bytes de usuario
que ya forman parte de ese espacio.

Guardar modifica solo la ranura elegida. No se escribe si sus datos ya son
idénticos. La firma se invalida primero y se confirma al final: un guardado
interrumpido puede dejar esa ranura inválida, pero no carga un registro parcial
ni altera otras ranuras. El CRC, la versión y los límites del efecto se validan
antes de aplicar un preset.

Cargar actualiza la configuración RGB nativa y la persiste igual que los
controles RGB normales; las tres ranuras no se sobrescriben al cargar.
Al desconectar se conservan tanto los presets como la última configuración
cargada. Los presets se guardan en la mitad maestra: el USB habitual sigue
en la izquierda. No se replica el almacenamiento personalizado entre mitades.

No se inicializan ni borran las ranuras al arrancar. La carga del firmware
conservó EEPROM y bootloader, verificados por lectura completa.
Si en el futuro se activa VIA, se cambian los efectos compilados o se cambia
QMK, debe revisarse esta distribución de EEPROM, los códigos y su versión.

## Verificación

Las pruebas nativas compilan y ejecutan el módulo C real con EEPROM acotada y
API QMK simulada: guardado mientras Fn está activo, tres ranuras independientes,
RGB apagado, toques y pulsaciones largas, soltar Fn primero, temporizador con
desbordamiento, datos corruptos y cortes en cada escritura de un guardado.

La compilación AVR conserva QMK 0.18.0 y AVR GCC 8.5.0. Reproduce y verifica
las dos aplicaciones originales antes de compilar la revisión de cada mitad.
Compara los 420 bytes del mapa esperado, los 1344 bytes de fuente OLED y los
864 bytes del perrito. El guard de fuentes exige que las capas base y la lógica
original de indicadores, OLED y perrito sigan intactas.

Las pruebas nativas del módulo C real y las cuatro compilaciones AVR pasaron.
Las bases completas reproducen los respaldos originales; las dos aplicaciones
nuevas contienen el mapa esperado y todos los gráficos originales. Frente al
firmware Fn anterior cambian exactamente las tres posiciones de presets, sin
alterar ninguna posición de Colemak o QWERTY.

| Mitad | Flash de aplicación | Flash libre | RAM estática | RAM restante antes de pila |
| --- | ---: | ---: | ---: | ---: |
| Izquierda | 25544 | 3128 | 1752 | 808 |
| Derecha | 25614 | 3058 | 1756 | 804 |

Tamaños en bytes: el aumento es de 542 bytes de flash y 6 bytes de RAM estática
por mitad respecto a la distribución Fn instalada y probada en Windows y macOS.
Los 30 bytes de presets se almacenan en EEPROM, una memoria distinta. La RAM
restante no incluye el consumo dinámico de la pila; la prueba de uso de esta
función fue confirmada por el propietario el 13 de octubre de 2026.
