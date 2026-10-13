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

Estado: compilación y verificaciones completas; carga y prueba física pendientes.

Fuentes `4105d7d3631dc1cb1ba07cac17a079039837f222`.
[Compilación USB](https://github.com/FelipeCris/Crisboard/actions/runs/38447300670).
[Resultados](five-rgb-presets-verification.json).

Frente al firmware Uniforme instalado cambian exactamente cinco bytes de cada
aplicación: cuatro en las dos posiciones Fn añadidas y uno en el límite de
presets admitidos (de tres a cinco). Todos los demás bytes de aplicación son
idénticos, incluidos los gráficos. No aumenta la flash ni la RAM estática.

| Mitad | Flash de aplicación | Flash libre | RAM estática | RAM restante antes de pila |
| --- | ---: | ---: | ---: | ---: |
| Izquierda | 25584 | 3088 | 1752 | 808 |
| Derecha | 25656 | 3016 | 1756 | 804 |

Tamaños en bytes. La EEPROM de presets pasa de 30 a 50 bytes. Las pruebas
nativas de las cinco ranuras, conservación de los tres registros y callbacks
RGB, las cuatro compilaciones AVR y las comparaciones de mapa/gráficos pasaron.
