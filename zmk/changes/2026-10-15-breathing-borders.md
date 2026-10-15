# Bordes fijos y centro con respiración

Se añade un sexto modo a Fn + Tab, después de Bordes inversos. En Colemak,
los mismos 17 LED de borde por mitad mantienen el tono opuesto y un brillo
fijo. El centro respira con el periodo y la velocidad de la respiración
nativa, entre cero y el brillo elegido. En QWERTY respira todo el teclado
uniformemente. Los cinco modos instalados conservan sus números y su
renderizado. No se cambia la respiración nativa.

El modo nuevo tiene el identificador 5 y funciona con los cinco presets
existentes, sin ampliar su registro de ocho bytes ni cambiar su CRC o versión.
No cambia ninguna asignación, voltaje, Bluetooth, pines ni tiempo de reposo.

## Investigación del RGB aparentemente bloqueado

Después de cargar la revisión de cinco modos, el usuario observó solo X/K
encendidas y ausencia de efectos. Más tarde indicó que cargar presets
existentes recuperó el funcionamiento, sin otra carga de firmware. La
restauración solicitada se quedó esperando RESET y terminó sin escribir
ninguna placa. No se borraron ajustes ni emparejamientos.

En el código instalado se identifica esta ruta:

1. Tras 30 segundos de inactividad, `rgb_underglow_auto_state()` llama a
   `zmk_rgb_underglow_off()`, que cambia `state.on` y programa su guardado.
2. Ese apagado temporal puede persistirse como `on=false`, también si un
   guardado anterior estaba pendiente al entrar en reposo.
3. Al reiniciar se carga `on=false` y no arranca el temporizador RGB.
4. Cambiar de efecto solo cambia el número de modo. Un preset encendido
   llama a `zmk_rgb_underglow_on()` y vuelve a arrancar el temporizador.

Esto explica un bloqueo recuperable con un preset. Es una causa probable
del caso observado: no se leyó su estado NVS durante el fallo y no permite
atribuir con certeza los dos LED residuales a esta ruta. CURRENT.UF2 no
expone los ajustes NVS. El usuario prefirió omitir la reproducción física.

La corrección conserva `state.on` como elección del usuario y representa
la suspensión por inactividad con una bandera en RAM. Suspender limpia
los LED y detiene el temporizador, sin guardar un apagado temporal. Al
despertar se respeta el apagado explícito. Una tarea RGB ya encolada no
puede volver a encender los LED mientras están suspendidos. Cargar un
preset encendido sigue despertando el RGB.

La corrección respeta un `on=false` que ya estuviera guardado. Si arranca
apagado al actualizar, Fn + Esc o un preset encendido permite activarlo
una vez; los reposos siguientes ya no persistirán ese apagado temporal.

## Validación

[Compilación y pruebas aprobadas](https://github.com/FelipeCris/Crisboard/actions/runs/38686721021), fuente `f05d90d66fd797d286f306a4b9bbb2fffb7f984e`. La prueba del código C real reproduce la ruta de apagado persistido de la base y verifica su corrección. El ensayo de arranque ejecuta las
funciones C reales de la base instalada y de la corrección: reposo,
guardado diferido, reinicio, cambio de modo, carga de preset y apagado
explícito. El renderizado de los cinco modos instalados se compara byte
por byte y el sexto se contrasta con un cálculo HSV independiente.

La base de compilación debe reproducir exactamente ambos UF2 instalados
de `33dfebf65ee3ffa68ee063685bca3a2b4473ced9`. Se comparan configuración,
devicetree y las 204 asignaciones enlazadas. Ambas mitades cargadas y verificadas por lectura; prueba funcional pendiente.

El incremento medido es de 224 bytes de flash por mitad, sin aumento de RAM
estática respecto a los cinco modos instalados. Las imágenes solo incluyen
aplicación; no se cargan ajustes ni bootloader.
