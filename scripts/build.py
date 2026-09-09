"""
SGVA SENA ADSO - Production Build & Data Pipeline
Normaliza el dataset de empresas, valida el esquema y compila los modulos de assets.

La validacion es bloqueante: si el dataset llega corrupto, el build falla en CI
antes de publicar en lugar de mostrar cifras rotas en produccion.
"""

import os
import re
import sys
import json

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")
DATA_DIR = os.path.join(OUTPUT, "assets", "data")
JS_DIR = os.path.join(OUTPUT, "assets", "js")

# Campos sin los cuales una vacante no se puede renderizar.
REQUIRED_FIELDS = ("solicitud_id", "empresa", "cat_id", "ranking_posicion")

# Campos monetarios: deben abrir con simbolo de moneda o una formula conocida.
# Un prefijo perdido ('.423.500' en lugar de '$1.423.500') se detiene aqui.
MONEY_FIELDS = ("apoyo_sostenimiento", "salario_egresado_jr", "techo_salarial_5anios")
MONEY_OK = re.compile(r'^\s*(\$|Desde|Hasta|A convenir|No especificado)', re.IGNORECASE)


def validate(companies):
    """Devuelve la lista de problemas detectados en el dataset."""
    problems = []
    seen_ids = set()

    for idx, row in enumerate(companies):
        label = row.get("empresa") or f"registro #{idx}"

        for field in REQUIRED_FIELDS:
            if not row.get(field):
                problems.append(f"{label}: falta el campo obligatorio '{field}'")

        sid = row.get("solicitud_id")
        if sid in seen_ids:
            problems.append(f"{label}: solicitud_id duplicado '{sid}'")
        seen_ids.add(sid)

        for field in MONEY_FIELDS:
            value = row.get(field)
            if isinstance(value, str) and value.strip() and not MONEY_OK.match(value):
                problems.append(f"{label}: '{field}' con formato monetario invalido -> {value!r}")

        email = row.get("email")
        if email and "@" not in email:
            problems.append(f"{label}: email invalido -> {email!r}")

    return problems


def build_data_pipeline():
    json_path = os.path.join(DATA_DIR, "empresas.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    problems = validate(companies)
    if problems:
        print(f"[X] Validacion fallida: {len(problems)} problema(s) en el dataset.")
        for p in problems[:25]:
            print(f"    - {p}")
        if len(problems) > 25:
            print(f"    ... y {len(problems) - 25} mas")
        return 1

    # Sort strictly by ranking position
    companies.sort(key=lambda x: x.get("ranking_posicion", 999))

    data_js_path = os.path.join(JS_DIR, "data.js")
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Clean Data Registry\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    tiers = {}
    for row in companies:
        tiers[row["cat_id"]] = tiers.get(row["cat_id"], 0) + 1

    print(f"[OK] Validacion superada: {len(companies)} registros sin incidencias.")
    print(f"[OK] Distribucion por tier: {tiers}")
    print(f"[OK] data.js compilado ({os.path.getsize(data_js_path) // 1024} KB).")
    return 0


if __name__ == "__main__":
    sys.exit(build_data_pipeline())
