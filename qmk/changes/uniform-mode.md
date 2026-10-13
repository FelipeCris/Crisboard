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

Estado: preparado; compilación AVR, medición de memoria y carga pendientes.
