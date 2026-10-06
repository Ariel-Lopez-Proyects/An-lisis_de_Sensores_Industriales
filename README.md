# Análisis de sensores industriales

Proyecto de la clase de Manejo Masivo de Datos. La idea es analizar las lecturas
de temperatura y vibración de los sensores de cuatro plantas industriales y
detectar cuándo hubo alertas por temperatura alta.

## Sobre los datos

El archivo `data/sensores_industriales.csv` tiene 100,000 mediciones.
**Los datos son simulados**, no vienen de máquinas reales.

Cada fila tiene:

- `id_registro`: número de la medición
- `fecha_hora`: cuándo se tomó la lectura
- `id_sensor`: qué sensor la tomó
- `planta`: en qué planta está el sensor
- `temperatura_c`: temperatura en °C
- `vibracion_mm_s`: vibración en mm/s

Una lectura cuenta como alerta cuando la temperatura es mayor a 85 °C. Ese
umbral es una regla didáctica del ejercicio.

## Qué hace el programa

`analisis.py` lee el CSV y muestra en pantalla:

- cuántos registros y sensores distintos hay
- la temperatura promedio de cada planta
- la temperatura máxima, con su sensor y fecha (si hay empate, muestra todos)
- cuántas lecturas son alertas
- qué planta tiene más alertas (también muestra empates)

Además guarda todas las alertas en `resultados/alertas.csv`.

## Cómo instalarlo y correrlo

```bash
git clone <url-del-repositorio>
cd <carpeta-del-repositorio>

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python analisis.py
```

El único paquete externo es pandas (con numpy, que viene con él).
Las versiones exactas están en `requirements.txt`.

## Estructura

```
.
├── analisis.py
├── data/
│   └── sensores_industriales.csv
├── resultados/
│   └── alertas.csv
├── requirements.txt
└── README.md
```