import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "output", "assets", "data", "empresas.json")
DATA_JS   = os.path.join(ROOT, "output", "assets", "js", "data.js")

CANDIDATE_STACK = {
    "languages": ["javascript", "java", "python", "sql", "html", "css", "c#", "typescript", "php"],
    "frameworks": ["react", "node", "spring", "spring boot", "angular", "vue", ".net", "express"],
    "databases":  ["sql", "mysql", "postgresql", "mongodb", "oracle", "sql server"],
    "tools":      ["git", "github", "docker", "api", "rest", "scrum", "agil", "jira", "linux"],
    "domains":    ["software", "web", "frontend", "backend", "full stack", "bases de datos", "qa",
                   "testing", "soporte", "mantenimiento", "sistemas", "aplicaciones"]
}

TECH_KEYWORDS = [
    "software", "desarrollo", "programador", "programacion", "developer", "frontend", "backend",
    "full stack", "fullstack", "react", "node", "java", "python", "sql", "bases de datos",
    "sistemas de informacion", "ingenieria", "tecnolog", "it ", "tech", "cloud", "api", "qa"
]

NON_TECH_KEYWORDS = [
    "oleaginosa", "palma", "porki", "cerdo", "ganad", "agricol", "agro", "avicol", "frigorifico",
    "carnes", "alimentos", "restaurante", "hotel", "campestre", "confeccion", "distribuidora",
    "comercializadora de pollo", "drogeria", "panaderia", "farmacia", "calzado"
]

def score_fit_ai(emp):
    funciones = (emp.get("funciones", "") + " " + emp.get("perfil_requerido", "")).lower()
    empresa = emp.get("empresa", "").lower()
    tags = [t.lower() for t in (emp.get("stack_tags") or [])]
    combo = f"{empresa} {funciones} {' '.join(tags)}"

    score = 40

    # Sector check
    if emp.get("cat_id") == "TIER_1":
        score += 35
    elif emp.get("cat_id") == "TIER_2":
        score += 25
    elif emp.get("cat_id") == "TIER_3":
        score += 15
    elif emp.get("cat_id") == "TIER_4":
        score += 5

    # Tech keyword matches
    tech_hits = sum(1 for kw in TECH_KEYWORDS if kw in combo)
    score += min(20, tech_hits * 3)

    # Penalize non-tech sectors
    if any(nk in combo for nk in NON_TECH_KEYWORDS):
        score -= 30

    return min(100, max(20, score))

def score_growth_ai(emp):
    cat_id = emp.get("cat_id", "TIER_4")
    if cat_id == "TIER_1": base = 95
    elif cat_id == "TIER_2": base = 85
    elif cat_id == "TIER_3": base = 70
    elif cat_id == "TIER_4": base = 50
    else: base = 35

    empresa = emp.get("empresa", "").upper()
    if any(k in empresa for k in ["SOFTWARE", "TECH", "SISTEMAS", "SOLUCIONES", "TECNOLOGIA", "NALSANI", "STEFANINI", "WASI", "TELEMATICA", "CLARO", "ARQUITECSOFT", "MVM", "ARTURO CALLE"]):
        base += 5

    return min(100, max(20, base))

def score_recruiter_ai(emp):
    score = 50
    if emp.get("contacto") and len(emp.get("contacto")) > 3:
        score += 25
    if emp.get("email", "").strip() and "@" in emp.get("email", ""):
        score += 20
    if emp.get("is_whatsapp", False) or emp.get("whatsapp_number", ""):
        score += 10
    return min(100, max(20, score))

def score_urgency_ai(emp):
    score = 65
    postulados = int(emp.get("postulados", 0) or 0)
    vacantes   = int(emp.get("vacantes", 1)   or 1)
    ratio = postulados / max(vacantes, 1)

    if ratio == 0:     score += 25
    elif ratio <= 1.0: score += 15
    elif ratio <= 2.0: score += 5
    elif ratio <= 4.0: score -= 5
    else:              score -= 20

    return min(100, max(20, score))

def score_competence_ai(emp):
    score = 65
    funciones = (emp.get("funciones", "") + " " + emp.get("perfil_requerido", "")).lower()
    
    if any(k in funciones for k in ["react", "node", "sql", "javascript", "python", "desarrollo"]):
        score += 20
    if any(k in funciones for k in ["mecanica", "electronica", "iot", "automatizacion"]):
        score += 15
    return min(100, max(20, score))

WEIGHTS = {
    "fit":       0.35,  # Real alignment with Software / Tech
    "growth":    0.25,  # Real career value
    "recruiter": 0.20,  # Real contactibility
    "urgency":   0.10,  # Competition ratio
    "competence":0.10   # Differentiator
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
    if score >= 88: return {"tier": "S", "label": "Prioridad Máxima - Postula HOY", "color": "#10b981"}
    if score >= 76: return {"tier": "A", "label": "Alta Probabilidad de Éxito",     "color": "#0284c7"}
    if score >= 62: return {"tier": "B", "label": "Buena Oportunidad Técnica",     "color": "#7c3aed"}
    if score >= 48: return {"tier": "C", "label": "Opción Secundaria",             "color": "#d97706"}
    return              {"tier": "D", "label": "Baja Afinidad ADSO",               "color": "#64748b"}

def main():
    print("=" * 70)
    print("  MULTI-AI RANKING CALIBRATION v3.1 (High Tech Credibility)")
    print("=" * 70)

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    for i, emp in enumerate(companies):
        res = compute_multi_ai_score(emp)
        tier = get_tier(res["puntaje_exito"])

        emp["puntaje_exito"]             = res["puntaje_exito"]
        emp["ai_scores"]                 = res["ai_scores"]
        emp["ai_consensus_confidence"]   = res["ai_consensus_confidence"]
        emp["ai_tier"]                   = tier["tier"]
        emp["ai_tier_label"]             = tier["label"]
        emp["ai_tier_color"]             = tier["color"]

    # Re-ranking: Sort by puntaje_exito desc, then vacantes desc, then postulados asc
    companies.sort(key=lambda x: (-x["puntaje_exito"], -int(x.get("vacantes",1) or 1), int(x.get("postulados",0) or 0)))
    for i, emp in enumerate(companies):
        emp["ranking_posicion"] = i + 1

    tiers = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    for emp in companies:
        tiers[emp.get("ai_tier", "D")] += 1

    print(f"\n[DISTRIBUCIÓN] Tier S={tiers['S']} | Tier A={tiers['A']} | Tier B={tiers['B']} | Tier C={tiers['C']} | Tier D={tiers['D']}")
    print(f"\nTop 15 vacantes:")
    for emp in companies[:15]:
        print(f"  #{emp['ranking_posicion']:02d} [{emp['puntaje_exito']}pts - Tier {emp['ai_tier']}] {emp['empresa']} ({emp['ciudad']}) | Cat: {emp.get('cat_badge','')}")

    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Multi-AI Ranked Dataset\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False)
        f.write(";\n")

    print("\n[OK] Dataset actualizado con ranking tech de alta fidelidad.")

if __name__ == "__main__":
    main()
