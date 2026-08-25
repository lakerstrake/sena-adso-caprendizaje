import json
import pandas as pd
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Deep evaluation of each company for an ADSO apprentice
# We will score:
# 1. Tech & Coding Relevance (40 pts)
# 2. Company Prestige & Tech Environment (25 pts)
# 3. Competition & Probability of Entry (20 pts)
# 4. Compensation/Post-Stage Employability Potential (15 pts)

tech_firms_names = [
    "NTT DATA", "WIRELESS", "SOFT", "DATA", "TECH", "SYSTEM", "DIGITAL", "SOLUCION", 
    "ABAI", "INTEXUS", "ARBITRIUM", "GLOBAL", "TELECOM", "INFORMATIC", "LOGICA"
]

def analyze_company_for_adso(item):
    empresa = item.get("empresa", "").upper()
    nit = item.get("nit", "")
    perfil = item.get("perfil_requerido", "").lower()
    funciones = item.get("funciones", "").lower()
    full_text = f"{empresa} {perfil} {funciones}"
    
    vacantes = int(item.get("vacantes", 1))
    postulados = int(item.get("postulados", 0))
    ratio = float(item.get("competencia_ratio", 0))
    techs = item.get("tecnologias", [])
    
    # 1. Tech score (0 - 40)
    tech_score = 15
    if any(k in full_text for k in ["desarroll", "programaci", "software", "aplicacion", "web", "backend", "frontend"]):
        tech_score += 15
    if any(k in full_text for k in ["python", "java", "sql", "react", "c#", ".net", "php", "javascript", "base de datos", "api"]):
        tech_score += 10
        
    # 2. Company Environment (0 - 25)
    env_score = 10
    is_pure_tech = any(t in empresa for t in tech_firms_names)
    if is_pure_tech:
        env_score = 25
    elif any(k in full_text for k in ["sistemas", "ti", "tecnolog", "transformacion digital"]):
        env_score = 18
    elif vacantes >= 5: # Large corporate intake
        env_score = 20
        
    # 3. Probability & Competition (0 - 20)
    if postulados == 0:
        prob_score = 20
    elif ratio <= 1.0:
        prob_score = 18
    elif ratio <= 2.0:
        prob_score = 15
    elif ratio <= 5.0:
        prob_score = 10
    elif ratio <= 10.0:
        prob_score = 5
    else:
        prob_score = 2
        
    # 4. Employability & Growth (0 - 15)
    emp_score = 8
    if is_pure_tech or len(techs) >= 2:
        emp_score = 15
    elif len(funciones) > 100 or len(perfil) > 100:
        emp_score = 12
        
    total_career_index = tech_score + env_score + prob_score + emp_score
    total_career_index = min(100, max(20, total_career_index))
    
    # Tier classification
    if is_pure_tech or (tech_score >= 35 and env_score >= 18):
        tier = "Tier S: Empresa Tech / Desarrollo Avanzado"
        tier_tag = "TIER_S"
        veredicto = "EXCELENTE: Proyecto enfocado en software, equipo técnico especializado y máxima valorización en tu hoja de vida como Desarrollador."
    elif tech_score >= 25 or "desarrollo" in full_text or "base de datos" in full_text or vacantes >= 3:
        tier = "Tier A: Corporativo / Automatización y Datos"
        tier_tag = "TIER_A"
        veredicto = "MUY RECOMENDADA: Departamento de TI consolidado, desarrollo interno, bases de datos y alta estabilidad corporativa."
    elif "soporte" in full_text or any(k in full_text for k in ["mantenimiento", "redes", "ofimatica"]):
        tier = "Tier B: Soporte TI & Operaciones"
        tier_tag = "TIER_B"
        veredicto = "BUENA: Enfoque en infraestructura, soporte y mantenimiento técnico de aplicaciones."
    else:
        tier = "Tier C: Operativo / Asignación General"
        tier_tag = "TIER_C"
        veredicto = "REGULAR: Funciones generales asignadas por jefatura. Menos especializada en código puro."

    # Recommendation category
    if postulados == 0 and tier_tag in ["TIER_S", "TIER_A"]:
        recomendacion = "🔥 ORO PURO: Alta relevancia técnica + CERO competencia actual."
    elif is_pure_tech and ratio <= 3.0:
        recomendacion = "🚀 TOP TECH: Consultora/Empresa de Software con excelente ratio de entrada."
    elif ratio <= 1.0 and tier_tag in ["TIER_S", "TIER_A"]:
        recomendacion = "⭐ ALTA PRIORIDAD: Excelente balance técnico y muy baja competencia."
    elif is_pure_tech:
        recomendacion = "💼 PRESTIGIO TECH: Empresa de clase mundial en tecnología."
    elif postulados == 0:
        recomendacion = "🎯 ENTRADA SEGURA: Sin candidatos postulados."
    else:
        recomendacion = "📌 OPCIÓN VÁLIDA: Aplicar según ubicación y perfil."
        
    return {
        "career_index": total_career_index,
        "tier": tier,
        "tier_tag": tier_tag,
        "is_pure_tech": is_pure_tech,
        "veredicto": veredicto,
        "recomendacion": recomendacion
    }

for item in data:
    analysis = analyze_company_for_adso(item)
    item["career_index"] = analysis["career_index"]
    item["tier"] = analysis["tier"]
    item["tier_tag"] = analysis["tier_tag"]
    item["is_pure_tech"] = analysis["is_pure_tech"]
    item["veredicto"] = analysis["veredicto"]
    item["recomendacion"] = analysis["recomendacion"]

# Sort by career index descending, then lowest ratio, then most vacancies
data.sort(key=lambda x: (-x["career_index"], -x["score_oportunidad"], x["competencia_ratio"]))

# Save updated dataset
with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save to Excel and CSV
df = pd.DataFrame(data)
col_order = [
    "empresa", "tier", "career_index", "recomendacion", "departamento", "ciudad", 
    "vacantes", "postulados", "competencia_ratio", "score_oportunidad", "tecnologias_str", 
    "contacto", "email", "telefono", "direccion", "nit", "solicitud_id", 
    "fecha_creacion", "fecha_cierre", "perfil_requerido", "funciones", "veredicto"
]
df_excel = df[[c for c in col_order if c in df.columns]]
df_excel.to_excel(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.xlsx", index=False)
df_excel.to_csv(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.csv", index=False, encoding="utf-8-sig")

print("=== REPORTE DE ANÁLISIS ESTRATÉGICO ADSO ===")
print(f"Total empresas evaluadas: {len(data)}")
print("\n--- TOP 15 EMPRESAS RECOMENDADAS PARA EL ÉXITO ADSO ---")
for i, item in enumerate(data[:15]):
    print(f"#{i+1} [{item['tier_tag']}] {item['empresa']} ({item['ciudad']})")
    print(f"   Career Index: {item['career_index']}/100 | Score: {item['score_oportunidad']} | Vac: {item['vacantes']} | Post: {item['postulados']} (Ratio: {item['competencia_ratio']})")
    print(f"   Recomendación: {item['recomendacion']}")
    print(f"   Contacto: {item['contacto']} | Email: {item['email']} | Tel: {item['telefono']}")
    print()
