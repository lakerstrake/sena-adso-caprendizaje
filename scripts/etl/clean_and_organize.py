import os
import shutil
import json

ROOT = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje"
OUTPUT = os.path.join(ROOT, "output")
DOCS = os.path.join(ROOT, "docs")
SCRIPTS = os.path.join(ROOT, "scripts")
ETL_DIR = os.path.join(SCRIPTS, "etl")
SCREENSHOTS_DIR = os.path.join(DOCS, "screenshots")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(ETL_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT, "assets", "data"), exist_ok=True)

# 1. Clean up loose files in output/
for item in os.listdir(OUTPUT):
    item_path = os.path.join(OUTPUT, item)
    if os.path.isfile(item_path):
        if item.endswith(".png"):
            # Move relevant screenshots to docs/screenshots, delete test artifacts
            if item.startswith("0") or "preview" in item:
                shutil.move(item_path, os.path.join(SCREENSHOTS_DIR, item))
            else:
                os.remove(item_path)
        elif item in ["README.md", "LICENSE", "wrangler.toml", ".gitignore"]:
            os.remove(item_path)
        elif item.startswith("empresas_caprendizaje_completo."):
            # Move to output/assets/data with clean names
            ext = item.split(".")[-1]
            dest_name = f"empresas.{ext}"
            shutil.move(item_path, os.path.join(OUTPUT, "assets", "data", dest_name))

# 2. Organize scripts/etl/
keep_in_scripts = ["build.py", "test_viewport.py"]
for f in os.listdir(SCRIPTS):
    f_path = os.path.join(SCRIPTS, f)
    if os.path.isfile(f_path) and f not in keep_in_scripts:
        shutil.move(f_path, os.path.join(ETL_DIR, f))

# 3. Clean JSON data schema
data_path = os.path.join(OUTPUT, "assets", "data", "empresas.json")
with open(data_path, "r", encoding="utf-8") as f:
    raw_list = json.load(f)

clean_list = []
for it in raw_list:
    clean_item = {
        "solicitud_id": str(it.get("solicitud_id", "")),
        "empresa": it.get("empresa", "").strip(),
        "nit": str(it.get("nit", "")).strip(),
        "departamento": it.get("departamento", "").strip(),
        "ciudad": it.get("ciudad", "").strip(),
        "direccion": it.get("direccion", "").strip(),
        "telefono": str(it.get("telefono", "")).strip(),
        "contacto": it.get("contacto", "").strip(),
        "email": it.get("email", "").strip(),
        "modalidad": it.get("modalidad", "Presencial / Híbrido").strip(),
        "vacantes": int(it.get("vacantes", 1)),
        "postulados": int(it.get("postulados", 0)),
        "competencia_ratio": float(it.get("competencia_ratio", 0.0)),
        "ranking_posicion": int(it.get("ranking_posicion", 999)),
        "puntaje_exito": int(it.get("puntaje_exito", 70)),
        "cat_id": it.get("cat_id", "TIER_3"),
        "cat_badge": it.get("cat_badge", "Tier 3 · Soporte TI"),
        "cat_color": it.get("cat_color", "amber"),
        "reputacion_rating": float(it.get("reputacion_rating", 3.8)),
        "reputacion_fuente": it.get("reputacion_fuente", "Directorio Empresarial"),
        "reputacion_nivel": it.get("reputacion_nivel", "Validada"),
        "apoyo_sostenimiento": "$1.423.500 COP (100% SMMLV)",
        "salario_egresado_jr": it.get("salario_egresado_jr", "$2.8M - $4.5M COP"),
        "escalabilidad_score": int(it.get("escalabilidad_score", 75)),
        "escalabilidad_nivel": it.get("escalabilidad_nivel", "Media"),
        "techo_salarial_5anios": it.get("techo_salarial_5anios", "$10M - $22M+ COP"),
        "stack_tags": it.get("stack_tags", ["SQL", "Frontend / Web"]),
        "is_whatsapp": bool(it.get("is_whatsapp", False)),
        "whatsapp_number": str(it.get("whatsapp_number", "")),
        "whatsapp_message": it.get("whatsapp_message", ""),
        "whatsapp_url": it.get("whatsapp_url", ""),
        "linkedin_contact_search_url": it.get("linkedin_contact_search_url", ""),
        "linkedin_connect_message": it.get("linkedin_connect_message", ""),
        "correo_formal_completo": it.get("correo_formal_completo", ""),
        "curva_aprendizaje_titulo": it.get("curva_aprendizaje_titulo", "Desarrollo de Software"),
        "curva_aprendizaje_detalle": it.get("curva_aprendizaje_detalle", ""),
        "perfil_requerido": it.get("perfil_requerido", "").strip(),
        "funciones": it.get("funciones", "").strip(),
        "fecha_cierre": it.get("fecha_cierre", "30/09/2026"),
        "facilidad_code": it.get("facilidad_code", "MOD"),
        "finanzas_5anios": it.get("finanzas_5anios", {
            "practica_6m": "$8.541.000 COP",
            "anio_1": "$45.000.000 COP",
            "acumulado_3a": "$185.000.000 COP",
            "acumulado_5a": "$450.000.000 a $720.000.000+ COP",
            "diferencial_vs_pyme": "+$320.000.000 COP adicionales"
        }),
        "hitos_carrera": it.get("hitos_carrera", []),
        "preguntas_entrevista": it.get("preguntas_entrevista", [])
    }
    clean_list.append(clean_item)

# Sort by ranking
clean_list.sort(key=lambda x: x["ranking_posicion"])

# Write clean empresas.json
with open(data_path, "w", encoding="utf-8") as f:
    json.dump(clean_list, f, ensure_ascii=False, indent=2)

# Write clean assets/js/data.js
data_js_path = os.path.join(OUTPUT, "assets", "js", "data.js")
with open(data_js_path, "w", encoding="utf-8") as f:
    f.write("/**\n * SGVA SENA ADSO - Clean Data Registry\n */\nwindow.RAW_DATA = ")
    json.dump(clean_list, f, ensure_ascii=False)
    f.write(";\n")

print(f"Successfully normalized and structured {len(clean_list)} company records into clean architecture!")
