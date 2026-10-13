# Cinco presets RGB: J, L, U, Y y Ñ en Colemak

La ampliación añade Fn + Y y Fn + Ñ como presets 4 y 5. Los tres anteriores
mantienen sus códigos, direcciones y datos guardados. Las tablas Colemak y
QWERTY normales se conservan; frente al firmware Uniforme instalado solo
se reasignan esas dos posiciones de Fn.

| Preset | Colemak | QWERTY, misma posición física |
| --- | --- | --- |
| 1 | Fn + J | Fn + Y |
| 2 | Fn + L | Fn + U |
| 3 | Fn + U | Fn + I |
| 4 | Fn + Y | Fn + O |
| 5 | Fn + Ñ | Fn + P |

Toque para cargar al soltar; mantener Fn y la tecla dos segundos para guardar.
Las dos ranuras nuevas empiezan vacías y pulsarlas no cambia la iluminación
hasta que se guarden. Cada preset puede usar cualquiera de los seis modos RGB,
incluido Uniforme o sólido con bordes inversos; el preset recuerda modo, HSV,
velocidad y encendido, sin capturar los indicadores temporales de Fn.

Los cinco registros ocupan 50 bytes de EEPROM (64–113). Los primeros tres
siguen en 64–93; solo se amplía con 94–113, una zona vacía en los respaldos.
El registro de diez bytes y su CRC no cambian. No hay inicializaciones ni
migraciones al arrancar. Las nuevas ranuras tampoco se escriben al cargar
firmware: se llenan únicamente cuando el usuario las guarda desde el teclado.

Las pruebas nativas ejecutan el módulo C real con cinco ranuras, guardan
Uniforme en la cuarta y verifican que escribir las dos nuevas no cambia
ningún byte de los tres registros anteriores. Se mantienen las pruebas de
interrupciones, corrupción, tiempos, límites y callbacks RGB completos.

Estado: preparado; compilación, medición de memoria y carga pendientes.
