import json
import pandas as pd
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Tech firms and software indicators
software_firms = [
    "NTT DATA", "WIRELESS", "SOFT", "DATA", "TECH", "SYSTEM", "DIGITAL", "SOLUCION", 
    "ABAI", "INTEXUS", "ARBITRIUM", "GLOBAL", "TELECOM", "INFORMATIC", "LOGICA", "SQA",
    "STEFANINI", "GEOCOM", "DESIGNER", "MVM", "ARQUITECSOFT"
]

def classify_human_friendly(item):
    empresa = item.get("empresa", "").upper()
    perfil = item.get("perfil_requerido", "").lower()
    funciones = item.get("funciones", "").lower()
    full_text = f"{empresa} {perfil} {funciones}"
    
    vacantes = int(item.get("vacantes", 1))
    postulados = int(item.get("postulados", 0))
    ratio = float(item.get("competencia_ratio", 0))
    techs = item.get("tecnologias", [])
    
    # Check if software dev
    is_software_house = any(sf in empresa for sf in software_firms)
    has_dev_terms = any(k in full_text for k in ["desarroll", "programaci", "software", "aplicacion", "web", "backend", "frontend", "codigo", "react", "java", "python", "c#", ".net", "php"])
    has_db_terms = any(k in full_text for k in ["base de datos", "bases de datos", "sql", "oracle", "postgresql", "automatiz", "inventario", "reporte", "sistemas internos"])
    has_support_terms = any(k in full_text for k in ["soporte", "mantenimiento", "impresor", "help desk", "redes", "ofimatica", "hardware", "usuario"])
    
    # 1. Enfoque del Cargo (Clasificación Principal)
    if is_software_house or (has_dev_terms and not ('soporte a impresoras' in full_text)):
        enfoque_id = "DESARROLLO_SOFTWARE"
        enfoque_titulo = "Desarrollo de Software Puro"
        enfoque_subtitulo = "Programación, web, apps y código"
        enfoque_badge = "💻 Desarrollo de Software"
        enfoque_color = "purple"
        que_haras = "Estarás programando directamente en proyectos de software, creando funcionalidades, consumiendo APIs y trabajando en equipos ágiles."
        por_que_sirve = "Es el cargo con MAYOR proyección salarial ($3.5M - $6M+ COP post-etapa). Te formarás como desarrollador profesional."
        estrellas = 5
    elif has_db_terms or "sistemas" in full_text or vacantes >= 3:
        enfoque_id = "DATOS_SISTEMAS"
        enfoque_titulo = "Sistemas y Bases de Datos"
        enfoque_subtitulo = "Bases de datos SQL, automatización y ERP"
        enfoque_badge = "🗄️ Datos y Sistemas"
        enfoque_color = "blue"
        que_haras = "Manejo de bases de datos relacionales (SQL/Oracle), desarrollo de herramientas internas, reportes analíticos y optimización de procesos corporativos."
        por_que_sirve = "Muy alta estabilidad en grandes empresas y bancos. Excelente para especializarse en Backend, Datos o Administración de Sistemas."
        estrellas = 4
    elif has_support_terms or "soporte" in full_text:
        enfoque_id = "SOPORTE_TI"
        enfoque_titulo = "Soporte Técnico y Redes"
        enfoque_subtitulo = "Infraestructura, helpdesk y equipos"
        enfoque_badge = "🛠️ Soporte Técnico"
        enfoque_color = "amber"
        que_haras = "Soporte a usuarios, mantenimiento preventivo de computadores, configuración de redes y atención de incidentes técnicos de TI."
        por_que_sirve = "Bueno para iniciar y entender la infraestructura de una empresa, aunque involucra poco o nada de programación."
        estrellas = 3
    else:
        enfoque_id = "OPERATIVO_GENERAL"
        enfoque_titulo = "Apoyo Operativo General"
        enfoque_subtitulo = "Labores asignadas por jefatura"
        enfoque_badge = "📋 Apoyo General"
        enfoque_color = "gray"
        que_haras = "Funciones administrativas u operativas generales definidas por el jefe inmediato en la empresa."
        por_que_sirve = "Te permite cumplir la etapa práctica del SENA, pero no está enfocado en programación."
        estrellas = 2
        
    # 2. Facilidad de Entrada (Nivel de Competencia)
    if postulados == 0:
        facilidad_id = "SIN_RIVALES"
        facilidad_titulo = "★ Sin Rivales (0 Postulados)"
        facilidad_badge = "🟢 Vacante Libre (0 Rivales)"
        facilidad_desc = "CERO candidatos postulados. Si aplicas hoy, tienes la máxima probabilidad de ser llamado de inmediato."
        probabilidad = "Máxima (99%)"
    elif ratio <= 1.0:
        facilidad_id = "MUY_FACIL"
        facilidad_titulo = "Baja Competencia (≤ 1 por cupo)"
        facilidad_badge = "🟢 Muy Alta Entrada"
        facilidad_desc = "Hay igual o más vacantes que candidatos. Probabilidad de ingreso excelente."
        probabilidad = "Muy Alta (90%)"
    elif ratio <= 2.0:
        facilidad_id = "FACIL"
        facilidad_titulo = "Competencia Moderada (1 a 2 por cupo)"
        facilidad_badge = "🔵 Buena Oportunidad"
        facilidad_desc = "Pocos candidatos por cupo. Tu perfil técnico del SENA destacará con facilidad."
        probabilidad = "Alta (75%)"
    elif ratio <= 5.0:
        facilidad_id = "MEDIA"
        facilidad_titulo = "Competencia Media (3 a 5 por cupo)"
        facilidad_badge = "🟡 Competencia Estándar"
        facilidad_desc = "Varios candidatos postulados. Se recomienda enviar correo directo formal con portafolio."
        probabilidad = "Media (50%)"
    else:
        facilidad_id = "ALTA_COMPETENCIA"
        facilidad_titulo = "Alta Competencia (> 5 por cupo)"
        facilidad_badge = "🔴 Muy Demandada"
        facilidad_desc = "Muchos aprendices compitiendo por este cupo. Necesitas destacar con tu portafolio de GitHub."
        probabilidad = "Competida (20-30%)"

    return {
        "enfoque_id": enfoque_id,
        "enfoque_titulo": enfoque_titulo,
        "enfoque_subtitulo": enfoque_subtitulo,
        "enfoque_badge": enfoque_badge,
        "enfoque_color": enfoque_color,
        "que_haras": que_haras,
        "por_que_sirve": por_que_sirve,
        "estrellas": estrellas,
        "facilidad_id": facilidad_id,
        "facilidad_titulo": facilidad_titulo,
        "facilidad_badge": facilidad_badge,
        "facilidad_desc": facilidad_desc,
        "probabilidad": probabilidad
    }

for item in data:
    c = classify_human_friendly(item)
    item["enfoque_id"] = c["enfoque_id"]
    item["enfoque_titulo"] = c["enfoque_titulo"]
    item["enfoque_subtitulo"] = c["enfoque_subtitulo"]
    item["enfoque_badge"] = c["enfoque_badge"]
    item["enfoque_color"] = c["enfoque_color"]
    item["que_haras"] = c["que_haras"]
    item["por_que_sirve"] = c["por_que_sirve"]
    item["estrellas"] = c["estrellas"]
    item["facilidad_id"] = c["facilidad_id"]
    item["facilidad_titulo"] = c["facilidad_titulo"]
    item["facilidad_badge"] = c["facilidad_badge"]
    item["facilidad_desc"] = c["facilidad_desc"]
    item["probabilidad"] = c["probabilidad"]

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

df = pd.DataFrame(data)
df.to_excel(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.xlsx", index=False)
df.to_csv(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.csv", index=False, encoding="utf-8-sig")

from collections import Counter
print("=== CONTEO DE CLASIFICACIONES CLARAS ===")
print("ENFOQUES:")
for k, v in Counter(d['enfoque_titulo'] for d in data).items():
    print(f"  • {k}: {v} empresas")

print("\nFACILIDAD DE ENTRADA:")
for k, v in Counter(d['facilidad_titulo'] for d in data).items():
    print(f"  • {k}: {v} empresas")
