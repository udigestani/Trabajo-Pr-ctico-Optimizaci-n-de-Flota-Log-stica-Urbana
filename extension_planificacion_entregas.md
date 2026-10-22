## Extensión de Consigna (Cambio Controlado): Edición del Itinerario, Solicitudes Entrantes y Zonas Restringidas

La cátedra define el incremento 5 de la evolución del semestre. Los nuevos comportamientos deben incorporarse **conservando las reglas 1 a 13, el ejemplo de aceptación y todas las pruebas anteriores**.

### Nuevas Reglas de Negocio

14. **Edición del itinerario por posición relativa:** Además de agregar al final, el operador puede insertar una solicitud **inmediatamente después de una parada indicada**, quitar una parada intermedia o mover una parada para que quede antes que otra. Estas operaciones son las más frecuentes durante la planificación y no deben requerir desplazar ni reconstruir el resto de la secuencia. El itinerario nunca se consulta por número de posición: siempre se recorre desde la primera parada hacia la siguiente, que es también como se calculan los horarios (regla 6). La revalidación atómica de la regla 7 sigue vigente.

15. **Deshacer y rehacer cambios de planificación:** Mientras el viaje esté `PLANIFICADO`, el operador puede deshacer los cambios aceptados (agregar, insertar, quitar o mover), siempre comenzando por **el cambio más reciente**, y luego el anterior. Lo deshecho puede rehacerse en el orden inverso al que se deshizo. Realizar un cambio nuevo descarta la posibilidad de rehacer lo deshecho hasta ese momento. Los cambios rechazados por la regla 7 no cuentan como cambios. Al iniciar el viaje, el historial de cambios se descarta.

16. **Solicitudes entrantes del día:** Las solicitudes que se reciben durante la jornada no se planifican de inmediato: el operador las evalúa **en el mismo orden en que fueron recibidas**, tomando siempre la más antigua sin evaluar. Si una solicitud no puede incorporarse a ningún viaje planificado del día, se traslada a las pendientes del día siguiente, que se evaluarán **antes** que las recibidas ese nuevo día y conservando su orden original. Debe poder consultarse la próxima solicitud a evaluar sin retirarla.

17. **Tramos dirigidos:** La matriz de distancias se carga a partir de un listado de tramos, cada uno compuesto por origen, destino y distancia. El tramo de A a B es distinto del tramo de B a A. Un tramo no puede modificarse una vez cargado, y la distancia de un tramo debe poder obtenerse de forma inmediata a partir del par origen–destino, sin recorrer el listado (regla 3).

18. **Zonas restringidas:** Algunas ubicaciones pertenecen a una o más zonas de circulación (por ejemplo "microcentro", "carga pesada prohibida"). Cada tipo de transporte tiene habilitadas determinadas zonas. Un itinerario solo es factible si **todas** las zonas que atraviesan sus paradas están habilitadas para el transporte del viaje. Si no lo son, el rechazo debe informar exactamente qué zonas no habilitadas se visitarían, sin repeticiones aunque varias paradas compartan zona. Esta validación forma parte de la revalidación atómica de la regla 7.

### Requisitos de la Extensión

- La resolución de esta extensión debe emplear **al menos cuatro estructuras de datos de naturaleza distinta**, elegidas por ustedes según el comportamiento que exige cada regla. Para las estructuras que no son nativas de Python, utilicen las implementaciones desarrolladas en la cátedra.
- Actualizar el diagrama de responsabilidades y la sección de decisiones de diseño. Para cada regla nueva, justifiquen qué estructura eligieron y por qué es más adecuada que las alternativas (orden de acceso, unicidad, mutabilidad y costo de las operaciones frecuentes).
- Respondan además: ¿qué objeto es responsable de conservar el historial de cambios? ¿Cómo se garantiza que deshacer un cambio también respete la revalidación atómica?

### Pruebas mínimas esperadas

- Inserción después de una parada intermedia y movimiento de una parada: horarios recalculados correctamente.
- Inserción inviable por ventana: la secuencia queda intacta.
- Tres cambios, dos deshacer y un rehacer: secuencia y horarios esperados en cada paso.
- Un cambio nuevo luego de deshacer elimina la posibilidad de rehacer.
- Intento de deshacer luego de iniciar el viaje.
- Cuatro solicitudes entrantes con una no incorporable: pasa al día siguiente y se evalúa antes que las nuevas.
- Tramo A→B definido y B→A faltante: el cálculo se rechaza en el sentido faltante.
- Intento de modificar un tramo ya cargado.
- Itinerario con dos paradas en la misma zona no habilitada: el rechazo la informa una sola vez.
- El ejemplo de aceptación del enunciado sigue produciendo los mismos resultados.
