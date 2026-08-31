import json
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "output", "assets", "data", "empresas.json")

with open(DATA_JSON, "r", encoding="utf-8") as f:
    companies = json.load(f)

print(f"Total empresas analizadas: {len(companies)}\n")
print(f"{'#':<3} | {'Tier':<8} | {'Score':<5} | {'Empresa':<40} | {'Actividad / Sector':<35} | {'Funciones':<40}")
print("-" * 140)

for idx, c in enumerate(companies[:30], 1):
    emp = c.get("empresa", "")[:38]
    tier = c.get("cat_id", "")
    score = c.get("puntaje_exito", 0)
    sector = c.get("panorama_sector", "") or c.get("cat_badge", "")
    funciones = (c.get("funciones", "") or "")[:38].replace("\n", " ")
    print(f"{idx:<3} | {tier:<8} | {score:<5} | {emp:<40} | {sector:<35} | {funciones:<40}")

print("\n--- DISTRIBUCIÓN POR TIER ACTUAL ---")
from collections import Counter
tiers = Counter(c.get("cat_id") for c in companies)
for t, cnt in tiers.most_common():
    print(f"  {t}: {cnt} empresas")
