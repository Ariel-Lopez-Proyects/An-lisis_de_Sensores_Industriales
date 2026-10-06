from pathlib import Path
import pandas as pd

UMBRAL = 85

base = Path(__file__).parent
ruta_csv = base / "data" / "sensores_industriales.csv"
ruta_salida = base / "resultados" / "alertas.csv"

df = pd.read_csv(ruta_csv)

print("1) Registros y sensores")
print("Registros:", len(df))
print("Sensores distintos:", df["id_sensor"].nunique())

print("\n2) Temperatura promedio por planta")
promedios = df.groupby("planta")["temperatura_c"].mean().round(2)
print(promedios.to_string())

print("\n3) Temperatura maxima")
maxima = df["temperatura_c"].max()
filas_max = df[df["temperatura_c"] == maxima]
print("Temperatura maxima:", maxima, "C")
print(filas_max[["id_sensor", "fecha_hora", "planta"]].to_string(index=False))

print("\n4) Lecturas con alerta (> 85 C)")
alertas = df[df["temperatura_c"] > UMBRAL]
print("Total de alertas:", len(alertas))

print("\n5) Planta con mas alertas")
por_planta = alertas.groupby("planta").size()
mayor = por_planta.max()
print(por_planta.to_string())
print("Planta(s) con mas alertas:", ", ".join(por_planta[por_planta == mayor].index), "con", mayor)

ruta_salida.parent.mkdir(exist_ok=True)
alertas.to_csv(ruta_salida, index=False)
print("\n6) Alertas exportadas a", ruta_salida.relative_to(base))