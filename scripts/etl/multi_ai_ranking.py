#!/usr/bin/env python3
"""
================================================================================
SGVA SENA - MULTI-AI RANKING ENGINE v2.0
================================================================================
Simula 5 perspectivas de IA especializadas para re-calcular el puntaje de exito
de cada empresa con base en datos objetivos y criterios de ingenieria social.

Modelos simulados:
  [M1] RecruiterAI   - Probabilidad de respuesta del reclutador al correo
  [M2] FitAI         - Alineacion tecnica candidato <-> vacante
  [M3] GrowthAI      - Potencial de crecimiento profesional real a 5 anios
  [M4] UrgencyAI     - Urgencia de cierre y ventana de oportunidad
  [M5] CompetenceAI  - Ventaja competitiva del candidato sobre otros postulantes

Score final = promedio ponderado de los 5 modelos (pesos calibrados).
================================================================================
"""

import json
import os
import re
from datetime import datetime, date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "output", "assets", "data", "empresas.json")
DATA_JS   = os.path.join(ROOT, "output", "assets", "js", "data.js")

# ─── Perfil del candidato ─────────────────────────────────────────────────────
CANDIDATE_STACK = {
    "languages": ["javascript", "java", "python", "sql", "html", "css", "c#"],
    "frameworks": ["react", "node", "spring", "spring boot", "angular", "vue", ".net"],
    "databases":  ["sql", "mysql", "postgresql", "mongodb", "oracle"],
    "tools":      ["git", "github", "docker", "api", "rest", "scrum", "agil", "jira"],
    "domains":    ["web", "frontend", "backend", "full stack", "bases de datos", "qa",
                   "testing", "soporte", "mantenimiento", "erp", "sistemas"]
}

# Palabras clave high-signal que indican SENA / aprendiz muy buscado
HIGH_SIGNAL_KEYWORDS = [
    "sena", "aprendiz", "adso", "analisis y desarrollo", "tecnologia",
    "logica", "programacion basica", "junior", "practica"
]

# Sectores con alta absorcion de aprendices SENA tech
TECH_SECTORS = ["software", "tecnologia", "sistemas", "desarrollo", "digital",
                "datos", "informatica", "it ", "tech", "cloud", "ia", "inteligencia"]

# ─── M1: RecruiterAI ─────────────────────────────────────────────────────────
def score_recruiter_ai(emp):
    """
    Probabilidad de que el reclutador abra, lea y responda el correo.
    Factores: contacto nominal, canal disponible, tamano empresa, urgencia.
    """
    score = 50  # base

    # Contacto nominal (tiene nombre real, no solo 'Recursos Humanos')
    tipo = emp.get("contacto_tipo", "")
    if tipo == "person":
        score += 20  # nombre real = respuesta +2x segun psicologia social

    # Tiene email directo
    if emp.get("email", "").strip():
        score += 15

    # Tiene WhatsApp
    if emp.get("is_whatsapp", False) or emp.get("whatsapp_number", ""):
        score += 8

    # Empresa pequena/mediana = decision mas rapida
    empresa = emp.get("empresa", "").upper()
    rep = emp.get("reputacion_fuente", "").lower()
    if any(k in rep for k in ["multinacional", "enterprise", "banco"]):
        score -= 8  # mas burocracia
    elif any(k in rep for k in ["startup", "pyme", "boutique", "consultora"]):
        score += 5

    # Soft companies responden mejor a correos tecnicos
    if any(k in rep for k in ["software", "tech", "digital", "sistemas"]):
        score += 7

    return min(100, max(0, score))

# ─── M2: FitAI ───────────────────────────────────────────────────────────────
def score_fit_ai(emp):
    """
    Alineacion entre el stack del candidato y los requerimientos de la vacante.
    Penaliza vacantes en sectores no-tech donde el aprendiz no encaja.
    """
    funciones = (emp.get("funciones", "") + " " + emp.get("perfil_requerido", "")).lower()
    tags = [t.lower() for t in (emp.get("stack_tags") or [])]
    combo = funciones + " " + " ".join(tags)

    hits = 0
    total_checked = 0

    for skill_list in CANDIDATE_STACK.values():
        for skill in skill_list:
            total_checked += 1
            if skill in combo:
                hits += 1

    raw_fit = min(100, (hits / max(total_checked, 1)) * 280)  # escala realista: 5/35 matches = buen fit

    # Bonus si requiere explicitamente ADSO/SENA
    if any(k in combo for k in HIGH_SIGNAL_KEYWORDS):
        raw_fit = min(100, raw_fit + 20)

    # Penalizacion por sector no-tech
    empresa_lower = emp.get("empresa", "").lower()
    rep_lower = emp.get("reputacion_fuente", "").lower()
    non_tech_flags = ["oleaginosa", "agricola", "ganaderia", "alimentos", "campestre",
                      "hotel", "construccion", "manufactura", "textil", "mineria"]
    if any(k in empresa_lower or k in rep_lower for k in non_tech_flags):
        raw_fit = max(10, raw_fit - 25)

    return min(100, max(0, round(raw_fit)))

# ─── M3: GrowthAI ────────────────────────────────────────────────────────────
def score_growth_ai(emp):
    """
    Potencial de crecimiento profesional real: escalabilidad, sector, stack futuro.
    """
    esc = emp.get("escalabilidad_score", 50)
    if isinstance(esc, str):
        try: esc = float(re.sub(r"[^0-9.]", "", esc))
        except: esc = 50

    nivel = emp.get("escalabilidad_nivel", "").lower()
    rep   = (emp.get("reputacion_fuente", "") + " " + emp.get("reputacion_nivel", "")).lower()

    score = float(esc) * 0.6  # base desde escalabilidad_score

    # Sector tech global = futuro garantizado
    if any(k in nivel for k in ["exponencial", "alto", "global"]):
        score += 20
    elif any(k in nivel for k in ["medio", "moderado"]):
        score += 8

    # Empresa reconocida = red de contactos y marca en CV
    if any(k in rep for k in ["multinacional", "enterprise", "banco", "grupo", "ntt", "stefanini"]):
        score += 12
    elif any(k in rep for k in ["startup", "boutique", "scale-up"]):
        score += 6

    # Salario egresado como indicador de mercado
    sal = emp.get("salario_egresado_jr", "").lower()
    if "5.000" in sal or "6.000" in sal or "7.000" in sal or "8.000" in sal:
        score += 8
    elif "4.000" in sal or "4.500" in sal:
        score += 4

    return min(100, max(0, round(score)))

# ─── M4: UrgencyAI ───────────────────────────────────────────────────────────
def score_urgency_ai(emp):
    """
    Urgencia de la oportunidad: fecha de cierre, postulados vs vacantes, ventana activa.
    """
    score = 55  # base neutral

    # Dias restantes hasta cierre
    fecha_str = emp.get("fecha_cierre", "")
    try:
        day, month, year = fecha_str.split("/")
        cierre = date(int(year), int(month), int(day))
        hoy    = date.today()
        dias   = (cierre - hoy).days

        if dias < 0:
            score -= 40   # ya cerro
        elif dias <= 5:
            score -= 15   # critico, puede que no vean tu correo
        elif dias <= 15:
            score += 25   # ventana perfecta - urgencia alta
        elif dias <= 30:
            score += 15   # buena ventana
        elif dias <= 60:
            score += 5
        else:
            score -= 5    # poca urgencia para el reclutador
    except:
        pass

    # Ratio postulados/vacantes - competencia
    try:
        postulados = int(emp.get("postulados", 0) or 0)
        vacantes   = int(emp.get("vacantes", 1)   or 1)
        ratio = postulados / max(vacantes, 1)

        if ratio <= 1.0:   score += 20  # pocas personas, alta chance
        elif ratio <= 2.0: score += 12
        elif ratio <= 4.0: score += 4
        elif ratio <= 8.0: score -= 8
        else:              score -= 18  # muy competido
    except:
        pass

    return min(100, max(0, score))

# ─── M5: CompetenceAI ────────────────────────────────────────────────────────
def score_competence_ai(emp):
    """
    Ventaja competitiva del candidato vs tipico postulante a esta vacante.
    Considera: facilidad de acceso, stack match exclusivo, doble formacion, GitHub.
    """
    facilidad = emp.get("facilidad_code", "MED")
    score_map  = {"HIGH": 90, "MOD": 72, "MED": 55, "LOW": 38, "ZERO": 15}
    score = score_map.get(facilidad, 55)

    # Doble formacion = ventaja diferencial vs competidores puros ADSO
    funciones = (emp.get("funciones", "") + " " + emp.get("perfil_requerido", "")).lower()

    if any(k in funciones for k in ["mecanica", "electronica", "iot", "automatizacion",
                                     "robotica", "industria", "manufactura", "control"]):
        score += 15  # background mecatronica = diferenciador total

    if any(k in funciones for k in ["react", "node", "spring", "angular", "aws", "cloud"]):
        score += 12  # stack moderno exacto al candidato

    # GitHub en el correo ya enviado = prueba social irrefutable
    score += 8  # base por portafolio publico verificable

    # Penalizar si requiere experiencia laboral formal
    if any(k in funciones for k in ["experiencia minima", "1 año", "2 años", "senior",
                                     "lider", "arquitecto"]):
        score -= 20

    return min(100, max(0, score))

# ─── Consenso de los 5 modelos ────────────────────────────────────────────────
WEIGHTS = {
    "recruiter": 0.20,   # quien responde es lo que importa primero
    "fit":       0.30,   # match tecnico es el filtro principal
    "growth":    0.18,   # donde me conviene estar en 5 anios
    "urgency":   0.15,   # ventana de tiempo real
    "competence":0.17    # mi ventaja vs otros candidatos
}

def compute_multi_ai_score(emp):
    m1 = score_recruiter_ai(emp)
    m2 = score_fit_ai(emp)
    m3 = score_growth_ai(emp)
    m4 = score_urgency_ai(emp)
    m5 = score_competence_ai(emp)

    final = (
        m1 * WEIGHTS["recruiter"] +
        m2 * WEIGHTS["fit"] +
        m3 * WEIGHTS["growth"] +
        m4 * WEIGHTS["urgency"] +
        m5 * WEIGHTS["competence"]
    )

    consensus = round(final)

    # Nivel de confianza del consenso (cuanto de acuerdo estan los modelos)
    scores = [m1, m2, m3, m4, m5]
    mean   = sum(scores) / len(scores)
    stddev = (sum((s - mean)**2 for s in scores) / len(scores)) ** 0.5
    confidence = "Alta" if stddev < 12 else ("Media" if stddev < 22 else "Baja")

    return {
        "puntaje_exito": consensus,
        "ai_scores": {
            "M1_RecruiterAI":  m1,
            "M2_FitAI":        m2,
            "M3_GrowthAI":     m3,
            "M4_UrgencyAI":    m4,
            "M5_CompetenceAI": m5
        },
        "ai_consensus_confidence": confidence
    }

def get_tier(score):
    if score >= 85: return {"tier": "S", "label": "Prioritario - Postula HOY", "color": "#f59e0b"}
    if score >= 72: return {"tier": "A", "label": "Alta Probabilidad",          "color": "#10b981"}
    if score >= 58: return {"tier": "B", "label": "Buena Oportunidad",          "color": "#3b82f6"}
    if score >= 44: return {"tier": "C", "label": "Posible",                    "color": "#8b5cf6"}
    return              {"tier": "D", "label": "Baja Prioridad",               "color": "#6b7280"}

def main():
    print("=" * 70)
    print("  MULTI-AI RANKING ENGINE v2.0 - 5 IAs en Consenso")
    print("  [M1] RecruiterAI [M2] FitAI [M3] GrowthAI [M4] UrgencyAI [M5] CompetenceAI")
    print("=" * 70)

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    print(f"[*] Analizando {len(companies)} vacantes con 5 modelos IA...")

    for i, emp in enumerate(companies):
        result = compute_multi_ai_score(emp)
        tier   = get_tier(result["puntaje_exito"])

        emp["puntaje_exito"]             = result["puntaje_exito"]
        emp["ai_scores"]                 = result["ai_scores"]
        emp["ai_consensus_confidence"]   = result["ai_consensus_confidence"]
        emp["ai_tier"]                   = tier["tier"]
        emp["ai_tier_label"]             = tier["label"]
        emp["ai_tier_color"]             = tier["color"]

    # Re-ranking por nuevo puntaje
    companies.sort(key=lambda x: x["puntaje_exito"], reverse=True)
    for i, emp in enumerate(companies):
        emp["ranking_posicion"] = i + 1

    # Estadisticas
    tiers = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    for emp in companies:
        tiers[emp.get("ai_tier", "D")] += 1

    print(f"\n[RESULTADOS] Top 20 vacantes por consenso multi-IA:")
    print(f"{'Pos':>3} {'Score':>5} {'Tier':>4} {'Conf':>5} | {'M1':>3} {'M2':>3} {'M3':>3} {'M4':>3} {'M5':>3} | Empresa")
    print("-" * 100)
    for emp in companies[:20]:
        ai = emp.get("ai_scores", {})
        print(
            f"{emp['ranking_posicion']:>3} "
            f"{emp['puntaje_exito']:>5} "
            f"  {emp.get('ai_tier','?'):>1}   "
            f"{emp.get('ai_consensus_confidence','?')[:4]:>4} "
            f"| {ai.get('M1_RecruiterAI',0):>3} "
            f"{ai.get('M2_FitAI',0):>3} "
            f"{ai.get('M3_GrowthAI',0):>3} "
            f"{ai.get('M4_UrgencyAI',0):>3} "
            f"{ai.get('M5_CompetenceAI',0):>3} "
            f"| {emp['empresa'][:55]}"
        )

    print(f"\n[DISTRIBUCION] Tier S={tiers['S']} A={tiers['A']} B={tiers['B']} C={tiers['C']} D={tiers['D']}")
    print(f"[*] Vacantes prioritarias (Tier S+A): {tiers['S']+tiers['A']}")

    # Guardar JSON
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    # Guardar data.js
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Multi-AI Ranked Data Registry\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False)
        f.write(";\n")

    print(f"\n[OK] JSON y data.js actualizados con rankings Multi-AI.")

if __name__ == "__main__":
    main()


