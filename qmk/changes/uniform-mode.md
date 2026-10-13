# Modo RGB Uniforme seleccionable

Se añade un sexto modo RGB, Uniforme: todas las teclas comparten el color base,
incluidos los bordes en Colemak. Los cinco modos anteriores conservan sus
indicadores y su inversión de bordes. Fn conserva sus indicadores temporales.

Seleccionar con Fn + Tab, ajustar tono/saturación/brillo y guardar en uno de
los tres presets mediante Fn + J/L/U durante dos segundos. Un toque lo carga.
El modo Uniforme no necesita teclas adicionales ni otro formato de presets.

El modo reutiliza el renderizador sólido de QMK, incluyendo sus límites y
gestión de las dos mitades. Se añade al final de la enumeración y las aserciones
de compilación comprueban los seis números, de modo que los cinco modos
existentes y los presets ya guardados mantienen sus identificadores.

El único cambio de los indicadores es omitir el repintado de bordes Colemak
cuando el modo seleccionado es Uniforme. El código de Fn, brillo máximo,
OLED, perrito, mapas completos y las tres ranuras de diez bytes se conservan.

Las pruebas nativas ejecutan los callbacks RGB reales, extraídos de los
fuentes de trabajo y del archivo histórico, para comparar los 68 LED en todos
los modos anteriores, ambas mitades, las dos capas base y con/sin Fn. También
comprueban Uniforme con/sin Fn y su guardado/carga por el módulo C real.

Estado: compilación AVR y verificaciones completas; ambas mitades cargadas
el 13 de octubre de 2026. La lectura completa de cada flash coincide con su
imagen prevista; EEPROM, presets y bootloader se conservaron.
El propietario confirmó Uniforme, los modos anteriores y la conservación de
sus presets. La ampliación posterior a cinco ranuras se documenta en
[Cinco presets RGB](five-rgb-presets.md).

Fuentes `fe546ad12c69cca40d2e1faefa4f2fa32b84b69e`.
[Compilación USB](https://github.com/FelipeCris/Crisboard/actions/runs/38438373255).
[Resultados](uniform-mode-verification.json).

| Mitad | Flash de aplicación | Flash libre | Aumento de flash | RAM estática |
| --- | ---: | ---: | ---: | ---: |
| Izquierda | 25584 | 3088 | 40 | 1752 |
| Derecha | 25656 | 3016 | 42 | 1756 |

Tamaños en bytes respecto al firmware de tres presets instalado. No aumenta
la RAM estática ni la EEPROM: los tres presets siguen ocupando 30 bytes.
Pasaron las pruebas de callbacks/presets reales, las cuatro compilaciones AVR,
la reproducción exacta de ambas bases, el mapa completo y todos los gráficos.
