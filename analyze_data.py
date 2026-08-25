import json
import pandas as pd
from collections import Counter

with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

print(f"=== REPORTE GENERAL DE EXTRACCIÓN ===")
print(f"Total de ofertas extraídas: {len(df)}")
print(f"Total de empresas únicas: {df['empresa'].nunique()}")
print(f"Total de vacantes disponibles: {df['vacantes'].sum()}")
print(f"Total de postulaciones acumuladas: {df['postulados'].sum()}")

print("\n--- DISTRIBUCIÓN POR DEPARTAMENTO ---")
print(df['departamento'].value_counts().head(10))

print("\n--- DISTRIBUCIÓN POR CIUDAD (TOP 10) ---")
print(df['ciudad'].str.strip().value_counts().head(10))

print("\n--- OFERTAS CON MÁS VACANTES (TOP 5) ---")
print(df.sort_values(by="vacantes", ascending=False)[["empresa", "ciudad", "vacantes", "postulados", "competencia_ratio", "score_oportunidad"]].head(5).to_string(index=False))

print("\n--- MEJORES OPORTUNIDADES (TOP 10 POR SCORE Y MENOR COMPETENCIA) ---")
print(df.sort_values(by=["score_oportunidad", "competencia_ratio"], ascending=[False, True])[["empresa", "ciudad", "vacantes", "postulados", "competencia_ratio", "score_oportunidad", "tecnologias_str"]].head(10).to_string(index=False))

# Tech stats
all_techs = []
for item in data:
    all_techs.extend(item.get("tecnologias", []))
tech_counts = Counter(all_techs)
print("\n--- TECNOLOGÍAS MÁS DEMANDADAS ---")
for t, c in tech_counts.most_common(15):
    print(f"  {t}: {c} menciones")
