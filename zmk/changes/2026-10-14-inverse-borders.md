# Modo Bordes inversos en ZMK

Se añade un quinto modo, seleccionado con Fn + Tab después de Solid, Breathe,
Spectrum y Swirl. Conserva esos cuatro modos, sus identificadores 0–3 y sus
presets. El nuevo modo usa el identificador 4 y se guarda/carga con los cinco
presets J/L/U/Y/Ñ igual que los anteriores.

En Colemak, el nuevo modo muestra el color base en las teclas interiores y
el tono opuesto en los bordes. El tono se desplaza 180°; la saturación y el
brillo se conservan. Es el equivalente en grados al desplazamiento QMK de
127 sobre su escala 0–254. Al seleccionar QWERTY, este modo queda uniforme,
igual que el comportamiento de los bordes del QMK. Fn no cambia la base.

Se usan los mismos índices LED que el QMK, convertidos al índice local de
cada mitad: 0–6, 17–20, 23–24, 27–28 y 32–33; son 17 de los 34 LED por mitad.
El patrón es estático y sigue el color/brillo elegidos desde el teclado.

La central comunica el cambio de base por el comportamiento RGB global
existente. Al reconectar la derecha, envía de nuevo la base cuando está
descubierta la característica que recibe comportamientos. No hay sondeo,
temporizadores adicionales ni cambios en los parámetros de radio.

El registro de presets mantiene sus ocho bytes, versión, CRC y campos. Solo
amplía de cuatro a cinco el número de efectos válidos. El estado de capa se
comunica aparte y no se guarda dentro del preset. El estado RGB nativo mantiene
su estructura y sus límites de brillo. Se conservan el mapa completo, los
atajos Bluetooth, el voltaje, los pines y los tiempos de reposo.

## Validación

La compilación compara el firmware instalado contra el nuevo para ambas
mitades. La base debe reproducir exactamente los UF2 validados en la fase Fn.
Configuración compilada y devicetree deben ser idénticos, y las 204 asignaciones
enlazadas de la central deben coincidir en las dos variantes.

Las pruebas ejecutan el código C real de renderizado: comparan todos los bytes
de los cuatro efectos anteriores y su avance de animación; comprueban el
patrón de los 34 LED, el tono opuesto, QWERTY uniforme y los límites de brillo.
También prueban el módulo real de sincronización de base, su aislamiento de
Fn y la repetición al reconectar después del descubrimiento de características.
Se mantienen las pruebas de batería, presets, persistencia y entrega a ambas mitades.

Estado: [compilación y verificaciones aprobadas](https://github.com/FelipeCris/Crisboard/actions/runs/38683595731), fuente `33dfebf65ee3ffa68ee063685bca3a2b4473ced9`. Carga y prueba física pendientes.

## Prueba física

El enlazador mide +364 bytes de flash y +16 bytes de RAM en la central;
en la derecha, +176 bytes de flash y la misma RAM que antes.

1. Con Colemak activo, recorrer Fn + Tab. Los cuatro modos anteriores deben
   mantenerse y el quinto debe mostrar bordes opuestos en ambas mitades.
2. Cambiar tono, saturación y brillo. Solo el nuevo modo debe tener ese patrón.
3. Cambiar a QWERTY y volver: con el nuevo modo activo debe alternar uniforme /
   bordes inversos, incluso si se reinicia la derecha entre cambios de base.
4. Recuperar los cinco presets existentes antes de reemplazar cualquiera.
5. Guardar el nuevo modo en una ranura elegida y comprobar carga y persistencia.
6. Comprobar escritura, multimedia, Bluetooth, voltaje y reposo.

Para volver al firmware anterior, seleccionar primero uno de los modos 0–3.
El firmware anterior ignora los presets guardados con el modo nuevo; los
registros de los cuatro modos que ya existían siguen siendo compatibles.
No cargar `settings_reset` ni borrar emparejamientos para esta actualización.
