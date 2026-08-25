import json
import pandas as pd
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

top_tech_firms = [
    "DESIGNER SOFTWARE", "STEFANINI", "SOFTWARE QUALITY ASSURANCE", "SQA", "GREEN SQA", "MVM INGENIERIA",
    "GEOCOM SOFTWARE", "CALL PROCESSING TECHNOLOGIES", "CALLTECH", "ARQUITECSOFT", "NTT DATA",
    "VC@SOFT", "ABAI COLOMBIA", "INTEXUS", "GLOBAL MVM", "WIRELESS & MOBILE", "LOGICA DIGITAL",
    "TELECOM", "ARBITRIUM", "SOLUCIONES TECNOLOGICAS", "INFORMATICA", "LOPEZ QUINTERO"
]

corporate_firms = [
    "BANCAMIA", "BANCO", "OLEAGINOSAS SAN MARCOS", "TENARIS", "TUBOCARIBE", "RETPLAS",
    "KAESER COMPRESORES", "ZIPPOL", "CEMENTOS", "CLINICA", "HOSPITAL", "SALUD", "SEGUROS", "ASISTE MAS"
]

def calculate_success_metrics(item):
    empresa = item.get("empresa", "").upper()
    nit = item.get("nit", "")
    perfil = item.get("perfil_requerido", "").lower()
    funciones = item.get("funciones", "").lower()
    full_text = f"{empresa} {perfil} {funciones}"
    
    vacantes = int(item.get("vacantes", 1))
    postulados = int(item.get("postulados", 0))
    ratio = float(item.get("competencia_ratio", 0))
    techs = item.get("tecnologias", [])
    
    # 1. Tech & Coding Score (Max 40 pts)
    tech_score = 10
    # Specific tech keywords
    tech_hits = sum(1 for t in ["python", "java", "sql", "oracle", "c#", ".net", "php", "javascript", "react", "git", "linux", "api", "base de datos", "bases de datos"] if t in full_text)
    tech_score += min(15, tech_hits * 5)
    
    if any(k in full_text for k in ["desarrollo", "programaci", "software", "aplicacion", "web", "backend", "frontend", "codigo"]):
        tech_score += 15
    elif any(k in full_text for k in ["base de datos", "bases de datos", "automatiz", "sistema"]):
        tech_score += 10
    elif any(k in full_text for k in ["soporte", "mantenimiento", "redes"]):
        tech_score += 5
        
    tech_score = min(40, tech_score)

    # 2. Company Environment & Prestige (Max 25 pts)
    is_pure_tech = any(tf in empresa for tf in top_tech_firms)
    is_corp = any(cf in empresa for cf in corporate_firms)
    
    if is_pure_tech:
        company_score = 25
    elif is_corp:
        company_score = 22
    elif vacantes >= 5:
        company_score = 20
    elif "software" in full_text or "tecnolog" in empresa:
        company_score = 16
    elif vacantes >= 2:
        company_score = 12
    else:
        company_score = 8
        
    company_score = min(25, company_score)

    # 3. Probability & Competition (Max 20 pts)
    if postulados == 0:
        comp_score = 20
    elif ratio <= 1.0:
        comp_score = 18
    elif ratio <= 2.0:
        comp_score = 15
    elif ratio <= 4.0:
        comp_score = 10
    elif ratio <= 8.0:
        comp_score = 5
    else:
        comp_score = 1

    # 4. Employability & Junior Salary Potential (Max 15 pts)
    if is_pure_tech:
        salary_score = 15
        salario_proyectado = "$3.500.000 a $6.000.000+ COP"
    elif is_corp or tech_score >= 30:
        salary_score = 12
        salario_proyectado = "$2.800.000 a $4.500.000 COP"
    elif tech_score >= 18:
        salary_score = 8
        salario_proyectado = "$2.000.000 a $2.800.000 COP"
    else:
        salary_score = 4
        salario_proyectado = "Salario Básico / Mínimo"

    # TOTAL SUCCESS SCORE (0 - 100)
    total_score = tech_score + company_score + comp_score + salary_score
    total_score = min(100, max(15, total_score))

    # CATEGORÍA DE ÉXITO
    if total_score >= 82:
        cat_id = "CAT_EXCEPCIONAL"
        cat_titulo = "💎 Éxito Excepcional (Top Tech)"
        cat_badge = "💎 Éxito Excepcional"
        cat_color = "purple"
        cat_nivel = 1
        diagnostico_corto = "Máxima prioridad: Aprenderás desarrollo de software real, metodologías ágiles y proyectos de alto valor."
    elif total_score >= 68:
        cat_id = "CAT_ALTO_EXITO"
        cat_titulo = "🚀 Alto Éxito (Corporativo & Datos)"
        cat_badge = "🚀 Alto Éxito"
        cat_color = "blue"
        cat_nivel = 2
        diagnostico_corto = "Muy recomendada: Excelente balance entre sistemas corporativos, bases de datos SQL y baja competencia."
    elif total_score >= 54:
        cat_id = "CAT_MODERADO"
        cat_titulo = "⚖️ Éxito Moderado (Soporte TI / Básico)"
        cat_badge = "⚖️ Éxito Moderado"
        cat_color = "amber"
        cat_nivel = 3
        diagnostico_corto = "Opción válida: Enfoque en soporte de sistemas, infraestructura o desarrollo básico."
    elif total_score >= 40:
        cat_id = "CAT_MENOR_PROYECCION"
        cat_titulo = "⚠️ Menor Proyección (Poco Código)"
        cat_badge = "⚠️ Menor Proyección"
        cat_color = "orange"
        cat_nivel = 4
        diagnostico_corto = "Menor relevancia para ADSO: Labores de soporte a usuarios o hardware con poca programación."
    else:
        cat_id = "CAT_NO_RECOMENDADA"
        cat_titulo = "🔻 No Recomendada (Sin Código / Saturada)"
        cat_badge = "🔻 No Recomendada"
        cat_color = "rose"
        cat_nivel = 5
        diagnostico_corto = "No recomendada: Muy alta saturación de postulados o labores puramente administrativas sin desarrollo."

    return {
        "puntaje_exito": total_score,
        "cat_id": cat_id,
        "cat_titulo": cat_titulo,
        "cat_badge": cat_badge,
        "cat_color": cat_color,
        "cat_nivel": cat_nivel,
        "salario_proyectado": salario_proyectado,
        "diagnostico_corto": diagnostico_corto,
        "tech_score": tech_score,
        "company_score": company_score,
        "comp_score": comp_score
    }

for item in data:
    res = calculate_success_metrics(item)
    item["puntaje_exito"] = res["puntaje_exito"]
    item["cat_id"] = res["cat_id"]
    item["cat_titulo"] = res["cat_titulo"]
    item["cat_badge"] = res["cat_badge"]
    item["cat_color"] = res["cat_color"]
    item["cat_nivel"] = res["cat_nivel"]
    item["salario_proyectado"] = res["salario_proyectado"]
    item["diagnostico_corto"] = res["diagnostico_corto"]

# STRICT SORTING: From Best (#1) to Worst (#179)
data.sort(key=lambda x: (-x["puntaje_exito"], x["competencia_ratio"], -x["vacantes"], x["empresa"]))

# Assign definitive ranking
for idx, item in enumerate(data):
    item["ranking_posicion"] = idx + 1
    item["ranking_badge"] = f"#{idx + 1}"

# Save JSON
with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save Excel and CSV
df = pd.DataFrame(data)
cols = [
    "ranking_posicion", "empresa", "cat_titulo", "puntaje_exito", "salario_proyectado",
    "departamento", "ciudad", "vacantes", "postulados", "competencia_ratio",
    "enfoque_titulo", "facilidad_titulo", "tecnologias_str", "contacto", "email",
    "telefono", "direccion", "nit", "solicitud_id", "fecha_creacion", "fecha_cierre",
    "diagnostico_corto", "perfil_requerido", "funciones"
]
df_out = df[[c for c in cols if c in df.columns]]
df_out.to_excel(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.xlsx", index=False)
df_out.to_csv(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.csv", index=False, encoding="utf-8-sig")

print("=== DISTRIBUCIÓN DE CATEGORÍAS DE ÉXITO ===")
from collections import Counter
for cat, count in Counter(d['cat_titulo'] for d in data).items():
    print(f"  • {cat}: {count} empresas")

print("\n--- TOP 15 MEJORES EMPRESAS (DEL MEJOR AL PEOR) ---")
for d in data[:15]:
    print(f"#{d['ranking_posicion']} [{d['puntaje_exito']}/100] {d['empresa']} ({d['ciudad']}) - {d['cat_badge']} (Vac: {d['vacantes']} | Post: {d['postulados']} | Ratio: {d['competencia_ratio']})")

print("\n--- TOP 5 PEORES / MENOS RECOMENDADAS ---")
for d in data[-5:]:
    print(f"#{d['ranking_posicion']} [{d['puntaje_exito']}/100] {d['empresa']} ({d['ciudad']}) - {d['cat_badge']} (Vac: {d['vacantes']} | Post: {d['postulados']} | Ratio: {d['competencia_ratio']})")
