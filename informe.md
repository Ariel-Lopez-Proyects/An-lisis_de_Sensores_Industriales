# Informe: Aplicación al caso de Big Data

**Caso:** sistema de sensores de temperatura en plantas industriales
**Integrantes:** [COMPLETAR: nombres]
**Nota:** los datos del CSV son **simulados**. Una lectura mayor a 85 °C es una "alerta del ejercicio"; por sí sola no demuestra que una máquina vaya a fallar.

---

## 5. Las 5 V aplicadas al proyecto

El CSV contiene lecturas con las columnas `id_registro`, `fecha_hora`, `id_sensor`, `planta`, `temperatura_c` y `vibracion_mm_s`. Cuando una V requiere características que el archivo no tiene (datos en tiempo real, formatos distintos, errores reales de sensores), el ejemplo se marca como parte de la **futura ampliación** del sistema.

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación futura? |
|---|---|---|---|
| **Volumen** | Cada sensor genera lecturas continuamente y la cantidad total crece con el número de sensores y la frecuencia de medición. | El CSV analizado tiene [COMPLETAR: total de registros según la salida de `analisis.py`, aprox. 100,000] lecturas de 40 sensores (10 en cada una de las 4 plantas). Si miles de sensores midieran cada segundo, se generarían millones de lecturas por día. | **CSV actual:** el volumen de 100,000 registros. **Ampliación futura:** los millones de lecturas diarias. |
| **Velocidad** | Los sensores producen datos de forma continua y algunas decisiones (por ejemplo, una alerta) dependen de reaccionar en segundos. | Recibir una lectura mayor a 85 °C y notificar al personal de mantenimiento pocos segundos después. | **Ampliación futura.** El CSV es un archivo ya almacenado: solo conserva la fecha de cada lectura, pero no demuestra que los datos lleguen en tiempo real. |
| **Variedad** | Una planta real genera datos de distintos tipos, no solo tablas de temperatura. | Mensajes JSON de los sensores, fotografías de las máquinas y reportes de mantenimiento en texto libre. | **Ampliación futura.** El CSV actual tiene un solo formato estructurado. |
| **Veracidad** | Los sensores pueden descalibrarse, fallar o enviar valores incorrectos, lo que afecta la confianza en los datos. | Un sensor descalibrado que reporta 95 °C cuando la máquina está a 70 °C generaría falsas alertas. | **Ampliación futura.** Los datos del CSV son simulados, por lo que no reflejan errores reales de sensores. En `alertas.csv` (6,954 filas) no hay valores vacíos ni filas duplicadas, y las temperaturas van de 85.01 a 104.99 °C, un rango acotado propio de datos simulados. |
| **Valor** | Los datos solo sirven si ayudan a tomar mejores decisiones de mantenimiento y operación. | Identificar la planta con más alertas (Planta_3, con 1,777 de las 6,954 alertas) para priorizar inspecciones. | **CSV actual**, como ejercicio de análisis. El valor real (reducir paros no planeados) correspondería a la ampliación futura con datos reales. |

---

## 6. Tipos de datos y procesamiento tradicional

### Clasificación

| Elemento | Tipo | Justificación |
|---|---|---|
| El CSV de sensores | **Estructurado** | Tiene filas y columnas fijas con un esquema definido (id_registro, fecha_hora, id_sensor, planta, temperatura_c, vibracion_mm_s). |
| Un mensaje JSON enviado por un sensor | **Semiestructurado** | Tiene etiquetas y campos (clave-valor), pero su estructura puede variar entre mensajes y no sigue una tabla rígida. |
| Una fotografía de una máquina | **No estructurado** | Es una imagen (píxeles) sin esquema tabular; para extraer información se requiere procesamiento de imágenes. |
| El texto libre de un reporte de mantenimiento | **No estructurado** | Es lenguaje natural sin campos definidos; extraer información requiere interpretar el texto. |

### ¿Por qué 100,000 registros no convierten automáticamente al archivo en Big Data?

Big Data no se define solo por el número de filas, sino por las características del problema (volumen, velocidad, variedad, etc.) y por si las herramientas tradicionales dejan de ser suficientes. Un archivo de 100,000 filas con pocas columnas ocupa unos pocos megabytes, cabe en la memoria de una laptop y un programa de Python lo procesa en segundos. Además, es un solo formato, estructurado y estático, sin llegada continua de datos. Por eso el procesamiento tradicional (un script sobre un archivo en una sola computadora) es suficiente.

### Limitaciones al aumentar la escala

- **Memoria:** cargar el archivo completo dejaría de ser posible cuando supere la RAM disponible.
- **Almacenamiento y procesamiento en una sola máquina:** el disco y la CPU se vuelven un límite, y los tiempos de ejecución crecen.
- **Tolerancia a fallos:** si el equipo falla a mitad del proceso, se pierde el avance y no hay copias distribuidas.
- **Tiempo de respuesta:** leer todo el archivo para cada consulta no sirve cuando se necesitan resultados en segundos.
- **Variedad:** un esquema de tabla no sirve para JSON, imágenes ni texto libre.
- **Concurrencia:** varios usuarios o procesos leyendo y escribiendo el mismo archivo generan conflictos.

---

## 7. Batch y Streaming

### Tipo de procesamiento realizado

`analisis.py` realiza **procesamiento por lotes (batch)**. Lee un archivo que ya está guardado completo, lo procesa de una sola vez y entrega resultados al final. No necesita responder mientras los datos llegan, y el resultado no pierde valor por tardar unos segundos o minutos.

### Alerta pocos segundos después de una lectura mayor a 85 °C

Usaría **procesamiento en flujo (streaming)**. Cada lectura se procesa en cuanto llega: los sensores publican sus mediciones a un sistema de mensajería (por ejemplo, Apache Kafka) y un motor de procesamiento de flujos (por ejemplo, Spark Structured Streaming o Apache Flink) evalúa la regla `temperatura > 85` evento por evento y dispara una notificación. Aquí el resultado se necesita en segundos; con batch, la alerta llegaría tarde, cuando ya se hubiera procesado el archivo.

### Resumen al terminar el día

Usaría **batch programado**. Al cierre del día ya se tienen todas las lecturas, no importa si el cálculo tarda unos minutos, y se pueden procesar grandes volúmenes de una vez con mayor eficiencia (promedios por planta, máximos, conteo de alertas).

### Relación con el tiempo

| Resultado | Tiempo en que se necesita | Enfoque |
|---|---|---|
| Alerta por temperatura alta | Segundos | Streaming |
| Resumen diario | Una vez al día (horas) | Batch |
| Análisis del CSV de esta práctica | No es urgente, los datos ya existen | Batch |

---

## 8. Lambda y Kappa

### Escenario A: Arquitectura Lambda

**Justificación:** la empresa quiere combinar dos rutas, una por lotes que recalcula el historial y otra rápida para las mediciones recientes. Eso es exactamente la arquitectura Lambda: una capa *batch* (resultados precisos sobre todo el historial), una capa *de velocidad* (resultados inmediatos sobre datos recientes) y una capa de servicio que une ambas vistas.

```
                       +----------------------------+     +-------------------+
                  +--> |  Almacén de datos crudos   | --> |    Capa batch     |--+
                  |    |  (historial completo)      |     | (recalcula todo)  |  |
+----------+   +--+---+ +----------------------------+     +-------------------+  |   +------------------+   +-----------+
| Sensores | ->| Ingesta |                                                         +-->|  Capa de servicio | ->| Consultas |
+----------+   +--+---+ +----------------------------+     +-------------------+  |   | (une las vistas)  |   | y alertas |
                  |    |    Capa de velocidad       |     | Vista en tiempo   |  |   +------------------+   +-----------+
                  +--> |  (mediciones recientes)    | --> |      real         |--+
                       +----------------------------+     +-------------------+
```

### Escenario B: Arquitectura Kappa

**Justificación:** la empresa quiere una sola lógica de procesamiento de eventos y conservar las mediciones para reprocesarlas cuando haga falta. Kappa elimina la ruta batch separada: todo se trata como un flujo de eventos guardados en un registro (log) inmutable. Si cambia la lógica, se vuelve a reproducir (replay) el log desde el inicio con el nuevo código, sin mantener dos sistemas distintos.

```
+----------+     +--------------------------+     +------------------------------+     +--------------------+     +-----------+
| Sensores | --> | Registro de eventos      | --> | Procesamiento de flujos      | --> | Vistas / resultados| --> | Consultas |
+----------+     | (log inmutable, retiene  |     | (una sola lógica)            |     +--------------------+     | y alertas |
                 |  todas las mediciones)   |     +------------------------------+                                +-----------+
                 +--------------------------+                    ^
                              |                                  |
                              +---- Reprocesamiento (replay) ----+
```

### Comparación breve

| | Lambda | Kappa |
|---|---|---|
| Rutas de procesamiento | Dos (batch y velocidad) | Una (flujo) |
| Lógica de cálculo | Duplicada en dos sistemas | Una sola |
| Reprocesar historial | Con la capa batch | Reproduciendo el log |
| Complejidad de mantenimiento | Mayor | Menor |

---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Descriptiva: ¿qué pasó?

Hallazgos reales obtenidos con `analisis.py`:

1. **Planta con más alertas:** hubo **6,954 lecturas mayores a 85 °C** y la planta con más alertas fue **Planta_3, con 1,777**. Le siguen Planta_1 (1,737), Planta_4 (1,732) y Planta_2 (1,708). La diferencia entre plantas es pequeña (69 alertas entre la primera y la última).
2. **Temperatura máxima, con empate:** la temperatura máxima fue **104.99 °C** y la alcanzaron **cuatro lecturas**:
   - Sensor S023, Planta_3, 01/09/26 22:23 (registro 53743)
   - Sensor S019, Planta_2, 02/09/26 13:11 (registro 89259)
   - Sensor S014, Planta_2, 02/09/26 15:23 (registro 94534)
   - Sensor S030, Planta_3, 02/09/26 16:02 (registro 96110)

Otros datos del análisis: la temperatura promedio de cada planta es [COMPLETAR: copiar de la salida de `analisis.py`].

### Predictiva: ¿qué podría pasar?

**Pregunta:** ¿qué máquinas tienen mayor probabilidad de presentar una falla en los próximos días si su temperatura supera repetidamente los 85 °C?

**Datos adicionales necesarios:**
- Historial de fallas y de mantenimiento de cada máquina (para saber qué ocurrió después de las alertas).
- Identificador de la máquina asociada a cada sensor (el CSV registra sensor y planta, no la máquina).
- Otras variables de operación: carga de trabajo, horas de uso, antigüedad y temperatura ambiente. El CSV ya incluye la vibración (`vibracion_mm_s`), que también podría usarse como variable del modelo.
- Un periodo de tiempo largo con datos reales, no simulados.

Con esos datos se podría entrenar un modelo que estime la probabilidad de falla. Con solo las lecturas de temperatura del CSV no es posible afirmar que una máquina fallará.

### Prescriptiva: ¿qué hacer?

**Acción propuesta:** programar una **inspección preventiva** empezando por los sensores con más alertas (S027 con 211, S009 con 197 y S022 con 195) y por la Planta_3, que concentra más alertas (1,777). Como la diferencia entre plantas es pequeña, la priorización por sensor es más útil que por planta.

**Información que se revisaría antes de decidir:**
- Si las alertas son consistentes en el tiempo o se deben a un sensor descalibrado (falsa alarma).
- El historial de mantenimiento y fallas de esa máquina.
- La criticidad de la máquina para la producción.
- El costo de detener la máquina para inspeccionarla frente al costo de una falla no planeada.
- La disponibilidad del personal técnico y las refacciones.

Recordatorio: una lectura por encima del umbral es solo una alerta del ejercicio. Sirve para priorizar la revisión, no demuestra que la máquina vaya a fallar.
