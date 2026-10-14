# Primera etapa: controles inalámbricos y acceso a Fn

Esta revisión parte de master `47a51bd`, que incluye el voltaje confirmado
en las dos pantallas. Conserva la revisión ZMK/Zephyr y sus parches de batería.

| Posición física en Colemak, manteniendo Fn | Acción |
| --- | --- |
| W | Perfil Bluetooth 1 (`BT_SEL 0`) |
| F | Perfil Bluetooth 2 (`BT_SEL 1`) |
| P | Perfil Bluetooth 3 (`BT_SEL 2`) |
| G | Borrar el emparejamiento del perfil seleccionado (`BT_CLR`) |
| D | Alternar salida preferida USB/Bluetooth (`OUT_TOG`) |

Las posiciones son las mismas en QWERTY: W/E/R/T/G respectivamente.
Los antiguos controles inalámbricos de Fn + Q/A/R/S/T en Colemak vuelven
a la letra de la capa activa. Fn + D pasa de borrar el perfil a alternar salida.
No se borra ningún emparejamiento al actualizar: borrar requiere pulsar Fn + G.

Las capas quedan ordenadas Colemak (0), QWERTY (1), Fn (2), para que QWERTY
no oculte Fn. Fn queda en la segunda tecla de la fila inferior izquierda y
Win en la tercera en ambas capas, como en QMK. Los selectores interiores
siguen QMK: Fn + tecla interior superior izquierda selecciona QWERTY;
la derecha selecciona Colemak.

Las letras y puntuación de las capas base se conservan. El resto de Fn,
incluidos los controles RGB nativos, permanece como en el ZMK instalado.
La paridad multimedia, controles RGB QMK, efectos/indicadores por tecla,
cinco presets y pantalla/perrito corresponden a etapas posteriores.

## Verificación y prueba

El workflow compila ambas mitades, con la aplicación de voltaje instalada
como base y la nueva distribución. Comprueba los 204 bindings enlazados
en la central, conserva todas las opciones compiladas y compara el
devicetree fuera del mapa. La base debe reproducir exactamente los UF2
de voltaje verificados en las placas. No se genera ni carga settings_reset.

Después de cargar y verificar por lectura:

1. Probar escritura en ambas mitades y voltaje en las dos pantallas.
2. Probar Fn + W/F/P y comprobar el perfil activo en el OLED. No requieren
   borrar ni volver a vincular equipos ya guardados.
3. Probar Fn + D: seleccionar Bluetooth para escribir en un equipo vinculado
   con USB conectado; pulsar de nuevo para volver a USB.
4. Cambiar a QWERTY con el selector izquierdo y comprobar Fn en la misma
   tecla física. Probar sus atajos W/E/R/T/G equivalentes. Volver a Colemak
   con el selector derecho y comprobar que las letras se conservan.
5. No pulsar Fn + G durante la prueba normal. Su función está comprobada
   en el binding compilado; probarla borraría el perfil seleccionado.

La [compilación de a40b38d](https://github.com/FelipeCris/Crisboard/actions/runs/38625007608)
pasó para ambas mitades, incluidas las cuatro compilaciones y la prueba del
código de batería. Las bases reproducen exactamente los UF2 de voltaje
instalados y la central contiene las 204 asignaciones esperadas. Las opciones
compiladas son idénticas y, fuera del mapa, solo se intercambian los dos IDs
de phandle generados de Bluetooth y salida. Todas las propiedades y referencias
de hardware se conservan. El tamaño asignado de flash y RAM no aumenta.

La aplicación de la derecha es idéntica a la instalada: esta etapa requiere
cargar únicamente la izquierda. El UF2 nuevo de la izquierda tiene SHA-256
`0228fb6268c8f7b17a6d5e0874c5ae38118020509b115b9cf00fe0c7c7b488ac`.
[Resultados](../verification/wireless-shortcuts.json).

Estado: compilado y verificado; instalación izquierda y prueba física pendientes.
