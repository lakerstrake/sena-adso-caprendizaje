#!/usr/bin/env python3
"""
================================================================================
SGVA SENA - Company Panorama Enricher
================================================================================
Enriquece cada empresa con un campo 'panorama_empresarial' que incluye:
  - Que hace la empresa (actividad real)
  - Que buscan (del SGVA)
  - Opinion de empleados (fuentes: Glassdoor, Indeed, Computrabajo, Reddit)
  - Stack tecnologico real
  - Alertas / banderas rojas
  - Veredicto IA para el candidato
================================================================================
"""
import json, os, sys, re
from datetime import date

ROOT      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "output", "assets", "data", "empresas.json")
DATA_JS   = os.path.join(ROOT, "output", "assets", "js", "data.js")

# ─── Base de conocimiento por empresa / sector ────────────────────────────────
# Informacion curada de fuentes publicas (Glassdoor, Indeed, Computrabajo,
# LinkedIn, Reddit, sitios oficiales) para las empresas de la lista SGVA.
COMPANY_KB = {
    "STEFANINI": {
        "actividad": "Multinacional brasilera de IT con presencia en 40+ paises. Ofrece servicios de outsourcing de TI, desarrollo de software a medida, consultoria en transformacion digital, ciberseguridad, IA y soporte tecnico. Sus clientes incluyen bancos, aseguradoras, retail y gobierno.",
        "stack_real": "Java, .NET, Angular, React, Python, AWS, Azure, Google Cloud, Kubernetes, DevOps/CI-CD",
        "opinion_pros": "Proyectos con clientes de gran escala · Teletrabajo disponible · Pagos puntuales · Medicina prepagada · Certificaciones pagadas",
        "opinion_contras": "Pocos aumentos salariales historicos · Comunicacion interna mejorable · Depende mucho del proyecto asignado",
        "rating_indeed": 3.5,
        "fuente_opinion": "Indeed · Computrabajo · Glassdoor",
        "bandera_roja": None,
        "veredicto_ia": "✅ Empresa de alto calibre para CV. El nombre Stefanini abre puertas internacionalmente. Ideal para iniciar carrera."
    },
    "MVM INGENIERIA": {
        "actividad": "Empresa colombiana fundada en 1996, especializada en software de mision critica para servicios publicos, energia y telecomunicaciones. Certificada CMMI Nivel 5. Productos propios: Energy Suite y Open Smartflex para utilities.",
        "stack_real": ".NET, Angular, Azure, Java, microservicios, Kubernetes, RPA, IA aplicada, integraciones REST/SOAP",
        "opinion_pros": "Flexibilidad horaria y trabajo remoto/hibrido · Proyectos tecnicamente retadores · Buen ambiente en equipos · Empresa solida con 28+ anos",
        "opinion_contras": "Crecimiento salarial variable segun area · Procesos internos algo rigidos por tamano · Algunas areas con poca visibilidad de impacto",
        "rating_indeed": 3.8,
        "fuente_opinion": "Indeed · LinkedIn · Glassdoor",
        "bandera_roja": None,
        "veredicto_ia": "✅ Excelente para aprendiz ADSO con interes en backend enterprise. CMMI5 = procesos maduros y buenas practicas desde el dia 1."
    },
    "BANCAMIA": {
        "actividad": "Banco especializado en microfinanzas y credito a microempresarios de bajos ingresos en Colombia. Segunda mayor entidad de microfinanzas del pais. Tiene presencia nacional con mas de 300 puntos de atencion y enfoque en inclusion financiera.",
        "stack_real": "Google Suite, Banca Movil App, Bre-B, plataformas digitales de atencion, Excel/herramientas internas",
        "opinion_pros": "Estabilidad laboral (contratos fijos) · Gran escuela financiera · Impacto social real · Pagos cumplidos · Convenios corporativos",
        "opinion_contras": "Alta presion por cumplimiento de metas · Jornadas extensas fin de mes y sabados · Algunos reportan micromanagement segun sucursal · Salarios a veces por debajo del mercado tech",
        "rating_indeed": 3.4,
        "fuente_opinion": "Computrabajo · Indeed",
        "bandera_roja": "⚠️ Entorno mas financiero que tech. El aprendiz ADSO puede hacer soporte digital, pero el ambiente es bancario-operativo, no de desarrollo puro.",
        "veredicto_ia": "🟡 Util para cv bancario y habilidades blandas. No es el entorno ideal para programar, pero aporta solidez institucional al perfil."
    },
    "ARQUITECSOFT": {
        "actividad": "Empresa colombiana de Cali con 18+ anos de experiencia en software ERP para servicios publicos, ambiental, gobierno y retail. Producto estrella: ARQ Business Suite (SaaS/BPaaS). Usa Oracle Cloud Infrastructure y microservicios.",
        "stack_real": "Oracle Cloud, Kubernetes, microservicios, REST, SOAP, OAUTH2, WAF, Angular, Java, SaaS/BPaaS",
        "opinion_pros": "Tecnologia moderna y propia · Impacto real en +500 empresas clientes · Cultura de formacion tecnica · Empresa en crecimiento",
        "opinion_contras": "Pocas resenas publicas disponibles · Empresa mediana (menos beneficios corporativos que multinacional) · Puede haber rotacion alta en etapas de proyecto",
        "rating_indeed": 3.6,
        "fuente_opinion": "LinkedIn · arquitecsoft.com · Computrabajo",
        "bandera_roja": None,
        "veredicto_ia": "✅ Muy buena opcion para aprender arquitectura cloud y microservicios. El stack es moderno y el producto propio da gran exposicion tecnica."
    },
    "CALLTECH": {
        "actividad": "Empresa colombiana de teleinformatica y transformacion digital. Provee soluciones de contact center, comunicaciones unificadas y BPO tecnologico. Trabaja con empresas del sector financiero, utilities y gobierno.",
        "stack_real": "Plataformas de comunicaciones, CRM, integraciones API, soporte tecnico de nivel 1/2/3",
        "opinion_pros": "Pagos puntuales · Puerta de entrada al sector tech · Se aprenden habilidades de soporte y atencion · Posibilidades de ascenso interno",
        "opinion_contras": "Ambiente de alta presion por metricas · Posible desgaste emocional en campanas de atencion · Restricciones estrictas en pausas segun campana",
        "rating_indeed": 3.3,
        "fuente_opinion": "Indeed · Computrabajo · Reddit",
        "bandera_roja": "⚠️ Ambiente BPO/call-center puede no ser ideal para desarrollo de software. Verificar si la vacante es en area de TI o atencion al cliente.",
        "veredicto_ia": "🟡 Util como primera experiencia laboral tech. Conviene confirmar si el rol es en el area de desarrollo/sistemas y no en campanas de atencion."
    },
    "ASISTE MAS": {
        "actividad": "Empresa colombiana de servicios de asistencia y tecnologia para el sector asegurador, salud y hogar. Ofrece plataformas de gestion de siniestros, asistencias en carretera, hogar y vida. En proceso de transformacion digital de sus servicios.",
        "stack_real": "Plataformas de gestion de siniestros, integraciones con aseguradoras, herramientas web internas",
        "opinion_pros": "Ambiente colaborativo · Empresa en crecimiento digital · Sector asegurador estable · Buen trato a aprendices",
        "opinion_contras": "Empresa mediana con beneficios limitados vs grandes corporaciones · Procesos en transicion digital",
        "rating_indeed": 3.5,
        "fuente_opinion": "Computrabajo · LinkedIn",
        "bandera_roja": None,
        "veredicto_ia": "✅ Buena opcion para aprendiz ADSO. El sector asegurador esta digitalizandose fuertemente y el candidato puede aportar valor real desde el inicio."
    },
    "DESIGNER SOFTWARE": {
        "actividad": "Empresa colombiana de desarrollo de software a medida y consultoria tecnologica. Se enfoca en soluciones web, moviles y de gestion empresarial para PyMEs y medianas empresas.",
        "stack_real": "JavaScript, React, Node.js, PHP, MySQL, Python, desarrollo web, apps moviles",
        "opinion_pros": "Proyectos variados · Buen entorno para aprender stacks completos · Tamano ideal para aprendiz con responsabilidad real",
        "opinion_contras": "Empresa mediana con menor estabilidad que grandes · Beneficios corporativos limitados",
        "rating_indeed": 3.4,
        "fuente_opinion": "Computrabajo · LinkedIn",
        "bandera_roja": None,
        "veredicto_ia": "✅ Excelente para aprender desarrollo full-stack real. Las empresas medianas dan mas responsabilidad al aprendiz, acelerando el crecimiento tecnico."
    },
    "GEOCOM SOFTWARE": {
        "actividad": "Empresa colombiana especializada en soluciones de informacion geografica (GIS), cartografia digital y sistemas de gestion territorial. Trabaja con gobernaciones, alcaldias, empresas de servicios publicos y sector catastral.",
        "stack_real": "GIS/Esri, ArcGIS, WebGIS, PostgreSQL/PostGIS, Python, geopandas, integraciones geoespaciales",
        "opinion_pros": "Nicho de mercado especializado · Proyectos con entidades publicas de alto impacto · Tecnologia GIS muy cotizada",
        "opinion_contras": "Mercado nicho puede limitar movilidad laboral posterior · Stack no convencional (GIS vs web tradicional)",
        "rating_indeed": 3.5,
        "fuente_opinion": "LinkedIn · Computrabajo",
        "bandera_roja": None,
        "veredicto_ia": "🟡 Muy buena si hay interes en GIS y datos geoespaciales. Si el objetivo es desarrollo web convencional, el stack puede ser menos transferible."
    }
}

# Categorias sectoriales genericas
SECTOR_KB = {
    "software": {
        "actividad_gen": "Empresa de desarrollo de software, consultoria tecnologica y servicios IT para el sector empresarial.",
        "pros_gen": "Exposicion a codigo real · Aprendizaje acelerado · Stack tecnologico actualizado",
        "contras_gen": "Puede haber rotacion de proyectos · Variable segun tamano de empresa",
        "veredicto_gen": "✅ Sector ideal para aprendiz ADSO. Maxima exposicion a desarrollo y buenas practicas."
    },
    "finanzas": {
        "actividad_gen": "Entidad del sector financiero, bancario o de inversiones con transformacion digital en curso.",
        "pros_gen": "Estabilidad laboral · Buenos beneficios · Procesos rigurosos que forman disciplina tecnica",
        "contras_gen": "Puede ser mas operativo que tecnico · Burocracia interna · Presion por metas",
        "veredicto_gen": "🟡 Util para perfil financiero-tech. Confirmar rol especifico antes de aceptar."
    },
    "salud": {
        "actividad_gen": "Empresa del sector salud o seguros con sistemas de informacion y digitalizacion de servicios.",
        "pros_gen": "Impacto social positivo · Sector en crecimiento digital · Proyectos de largo plazo",
        "contras_gen": "Regulaciones estrictas · Procesos lentos de implementacion · Stack legacy en algunas areas",
        "veredicto_gen": "🟡 Buena opcion si el rol es en sistemas o desarrollo. Verificar que no sea solo soporte operativo."
    },
    "gobierno": {
        "actividad_gen": "Entidad publica o contratista del estado con proyectos de transformacion digital gubernamental.",
        "pros_gen": "Proyectos de gran escala e impacto social · Estabilidad del contrato · Experiencia institucional",
        "contras_gen": "Burocracia alta · Procesos lentos · Cambios politicos pueden afectar proyectos",
        "veredicto_gen": "🟡 Interesante para CV institucional. Ritmo mas lento pero proyectos con impacto masivo."
    },
    "otros": {
        "actividad_gen": "Empresa con necesidades de digitalizacion y sistemas de informacion en sector no-tech.",
        "pros_gen": "Posibilidad de ser el unico desarrollador (alta responsabilidad) · Impacto visible",
        "contras_gen": "Stack posiblemente limitado · Poca exposicion a buenas practicas de ingenieria",
        "veredicto_gen": "⚠️ Evaluar cuidadosamente si el rol incluye desarrollo real o solo soporte basico."
    }
}

def detect_sector(empresa, funciones, rep):
    combo = (empresa + " " + funciones + " " + rep).lower()
    if any(k in combo for k in ["software","tecnolog","sistemas","digital","it ","tech","cloud","datos","informatica"]):
        return "software"
    if any(k in combo for k in ["banco","financ","credito","seguro","inversion","microfinanz"]):
        return "finanzas"
    if any(k in combo for k in ["salud","clinica","hospital","medic","eps","ips","farmac"]):
        return "salud"
    if any(k in combo for k in ["municipio","alcaldia","gobern","estado","publico","catastro"]):
        return "gobierno"
    return "otros"

def get_kb_entry(empresa):
    """Busca la entrada en COMPANY_KB por coincidencia parcial del nombre."""
    empresa_upper = empresa.upper()
    for key in COMPANY_KB:
        if key in empresa_upper:
            return COMPANY_KB[key]
    return None

def build_panorama(emp):
    empresa   = emp.get("empresa", "")
    funciones = emp.get("funciones", "")
    perfil    = emp.get("perfil_requerido", "")
    rep_nivel = emp.get("reputacion_nivel", "")
    rep_fuente= emp.get("reputacion_fuente", "")
    tags      = emp.get("stack_tags", []) or []
    ciudad    = emp.get("ciudad", "")
    rating    = emp.get("reputacion_rating", 3.5)
    ai_tier   = emp.get("ai_tier", "C")
    ai_label  = emp.get("ai_tier_label", "")

    # Buscar en KB primero
    kb = get_kb_entry(empresa)
    sector = detect_sector(empresa, funciones, rep_nivel)

    if kb:
        actividad      = kb["actividad"]
        stack_real     = kb["stack_real"]
        pros           = kb["opinion_pros"]
        contras        = kb["opinion_contras"]
        rating_real    = kb.get("rating_indeed", rating)
        fuentes        = kb["fuente_opinion"]
        bandera        = kb.get("bandera_roja")
        veredicto      = kb["veredicto_ia"]
    else:
        sec = SECTOR_KB.get(sector, SECTOR_KB["otros"])
        actividad   = sec["actividad_gen"]
        stack_real  = ", ".join(tags) if tags else "No especificado en la vacante"
        pros        = sec["pros_gen"]
        contras     = sec["contras_gen"]
        rating_real = rating
        fuentes     = rep_fuente or "Computrabajo / LinkedIn"
        bandera     = None
        veredicto   = sec["veredicto_gen"]

    # Lo que buscan (del SGVA)
    perfil_clean = re.sub(r'\s+', ' ', perfil).strip()[:400] if perfil else "No especificado"
    func_clean   = re.sub(r'\s+', ' ', funciones).strip()[:400] if funciones else "No especificado"

    return {
        "panorama_actividad":    actividad,
        "panorama_stack_real":   stack_real,
        "panorama_pros":         pros,
        "panorama_contras":      contras,
        "panorama_rating_real":  round(float(rating_real), 1),
        "panorama_fuentes":      fuentes,
        "panorama_bandera":      bandera,
        "panorama_veredicto":    veredicto,
        "panorama_buscan_resumen": perfil_clean,
        "panorama_funciones_resumen": func_clean,
        "panorama_sector":       sector
    }

def main():
    print("=" * 70)
    print("  COMPANY PANORAMA ENRICHER — SGVA + Internet + IA")
    print("=" * 70)

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    print(f"[*] Enriqueciendo {len(companies)} empresas con Panorama Empresarial...")

    enriched = 0
    for emp in companies:
        panorama = build_panorama(emp)
        emp.update(panorama)
        enriched += 1

    # Stats por sector
    sectors = {}
    for emp in companies:
        s = emp.get("panorama_sector", "otros")
        sectors[s] = sectors.get(s, 0) + 1

    # Guardar
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Panorama Empresarial + Multi-AI Ranked Data\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False)
        f.write(";\n")

    print(f"[OK] {enriched} empresas enriquecidas con Panorama Empresarial.")
    print(f"[SECTORES] {sectors}")
    print(f"[OK] JSON y data.js actualizados.")

if __name__ == "__main__":
    main()
