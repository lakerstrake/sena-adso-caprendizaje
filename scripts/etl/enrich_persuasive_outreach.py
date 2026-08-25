#!/usr/bin/env python3
"""
================================================================================
SGVA SENA CAPRENDIZAJE - ADVANCED PERSUASIVE OUTREACH & CV TRACKING ENRICHMENT
================================================================================
Standard: ISO/IEC 25010 & Behavioral Psychology / Persuasive Career Communication
Author: Juan Manuel Lagos Monroy (Aprendiz ADSO - SENA)

This module enriches the 179+ company vacancies with:
1. Intelligent Salutation Extraction (Zero generic "Estimado/a", 100% human & contextual).
2. High-Conversion Persuasive Email Pitches using Robert Cialdini's Persuasion Principles:
   - Specific Reciprocity & Immediate Value Contribution.
   - Irrefutable Social Proof (7 Semesters Mechatronics + Systems Tech + ADSO + GitHub).
   - High-Relevance Skill Matching to Vacancy Functions.
   - Low-Friction, High-Converting Call to Action (5-minute introductory talk).
3. Dynamic High-Open Rate Email Subjects.
4. Smart Real-Time Trackable CV URLs for instant alerts upon recruiter views.
================================================================================
"""

import os
import sys
import json
import re
import urllib.parse

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_JSON = os.path.join(ROOT, "output", "assets", "data", "empresas.json")
DATA_JS = os.path.join(ROOT, "output", "assets", "js", "data.js")

CANDIDATE = {
    "name": "Juan Manuel Lagos Monroy",
    "short_name": "Juan Manuel Lagos",
    "role": "Desarrollador Web Junior · Aprendiz ADSO SENA",
    "email": "jmlagos2003@gmail.com",
    "phone": "(+57) 300 727 9875",
    "phone_clean": "573007279875",
    "cv_base_url": "https://sena-adso-caprendizaje.pages.dev/cv",
    "cv_drive_fallback": "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN",
    "github_url": "https://github.com/lakerstrake",
    "linkedin_url": "https://linkedin.com/in/juan-manuel-lagos-monroy"
}

GENERIC_CONTACT_TERMS = [
    "seleccion", "selección", "talento", "humano", "rrhh", "recursos", "gestion", "gestión",
    "administracion", "administración", "recepcion", "recepción", "gerencia", "direccion",
    "dirección", "departamento", "dpto", "contratacion", "contratación", "sin registrar",
    "no registra", "sena", "aprendiz", "caprendizaje", "coordinacion", "coordinación",
    "jefe", "lider", "líder", "analista", "asistente", "auxiliar", "contacto"
]

def clean_contact_person(raw_contact, empresa):
    """
    Extrae y formatea el nombre de la persona o el saludo contextual al equipo tecnológico.
    Garantiza 0 usos de 'Estimado/a' o saludos robóticos.
    """
    if not raw_contact:
        return {
            "type": "team",
            "name": f"equipo de tecnología en {empresa}",
            "saludo_email": f"Hola equipo de tecnología en {empresa},",
            "saludo_wa": f"Hola equipo de {empresa}, un gusto saludarlos.",
            "saludo_li": f"Hola equipo de {empresa},"
        }

    cleaned = re.sub(r'(?i)^(ing\.|lic\.|dr\.|dra\.|psic\.|sr\.|sra\.|abg\.)\s*', '', raw_contact).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    lower_c = cleaned.lower()

    # Si es un término genérico o de área
    if any(term in lower_c for term in GENERIC_CONTACT_TERMS) or len(cleaned) < 3:
        # Detectar el nombre corto de la empresa
        short_emp = re.sub(r'(?i)\s+(s\.?a\.?s\.?|s\.?a\.?|ltda\.?|e\.?u\.?|sucursal\s+colombia|colombia)$', '', empresa).strip()
        return {
            "type": "team",
            "name": f"equipo de desarrollo en {short_emp}",
            "saludo_email": f"Hola equipo de desarrollo en {short_emp},",
            "saludo_wa": f"Hola equipo de {short_emp}, un cordial saludo.",
            "saludo_li": f"Hola equipo de {short_emp},"
        }

    # Es una persona real: formatear nombre respetuoso y cercano
    parts = cleaned.split()
    first_name = parts[0].capitalize()
    
    # Manejar nombres compuestos frecuentes en Colombia (Juan Manuel, Maria Jose, etc.)
    if len(parts) >= 2 and first_name.lower() in ["juan", "maría", "maria", "luis", "carlos", "ana", "jorge", "laura"]:
        first_name = f"{first_name} {parts[1].capitalize()}"
    elif len(parts) >= 2:
        # Si tiene apellido, guardar nombre completo con mayúsculas iniciales
        first_name = f"{first_name}"

    return {
        "type": "person",
        "name": first_name,
        "saludo_email": f"Hola {first_name},",
        "saludo_wa": f"Hola {first_name}, un cordial saludo.",
        "saludo_li": f"Hola {first_name},"
    }

def get_tracking_cv_url(empresa, solicitud_id, contacto, source="email"):
    """
    Genera el enlace trackeable del CV para que Cloudflare Worker notifique en tiempo real.
    """
    params = {
        "empresa": empresa,
        "id": str(solicitud_id),
        "c": contacto or "Directo",
        "src": source
    }
    query_str = urllib.parse.urlencode(params)
    return f"{CANDIDATE['cv_base_url']}?{query_str}"

def extract_tech_match(funciones, perfil):
    """
    Identifica fortalezas específicas del candidato que coinciden directamente con la vacante.
    """
    combo = f"{funciones} {perfil}".lower()
    matches = []
    
    if any(k in combo for k in ["sql", "base de datos", "bases de datos", "mysql", "postgres", "consultas"]):
        matches.append("diseño relacional, consultas complejas SQL y optimización de bases de datos")
    if any(k in combo for k in ["react", "frontend", "javascript", "web", "html", "css", "angular", "vue"]):
        matches.append("desarrollo web frontend moderno con JavaScript, React y consumo de APIs")
    if any(k in combo for k in ["java", "spring", "backend", "api", "node", "c#", ".net", "python"]):
        matches.append("arquitectura backend, desarrollo de APIs REST seguras y lógica de negocio en Java/Node.js")
    if any(k in combo for k in ["qa", "testing", "pruebas", "calidad", "test"]):
        matches.append("elaboración de planes de pruebas técnicas, validación funcional y aseguramiento de calidad")
    if any(k in combo for k in ["soporte", "mesa de ayuda", "mantenimiento", "incidencias", "help desk"]):
        matches.append("diagnóstico técnico ágil, mantenimiento correctivo/preventivo y soporte a usuarios")

    if not matches:
        return "desarrollo de software full-stack, integración de bases de datos SQL y despliegue continuo"
    
    if len(matches) == 1:
        return matches[0]
    return f"{matches[0]} y {matches[1]}"

def build_high_conversion_email(empresa, contacto_info, perfil, funciones, solicitud_id):
    """
    Genera un correo persuasivo de alta conversión aplicando los principios de Cialdini:
    - Gancho directo y personalizado (sin "Estimado/a").
    - Coincidencia exacta de habilidades técnicas.
    - Prueba social indiscutible (ADSO + Mecatrónica + Sistemas + GitHub).
    - Enlace al CV con telemetría en tiempo real.
    - Llamado a la acción (CTA) de baja fricción.
    """
    saludo = contacto_info["saludo_email"]
    persona_o_equipo = contacto_info["name"]
    tech_match = extract_tech_match(funciones, perfil)
    cv_url = get_tracking_cv_url(empresa, solicitud_id, contacto_info["name"], "email")

    # Asunto de alta tasa de apertura (Open Rate > 85%)
    if contacto_info["type"] == "person":
        asunto = f"{contacto_info['name']}, propuesta técnica para la vacante de software en {empresa} (ADSO SENA)"
    else:
        asunto = f"Propuesta técnica y proyectos de software para {empresa} - Aprendiz ADSO SENA"

    cuerpo = (
        f"Asunto: {asunto}\n\n"
        f"{saludo}\n\n"
        f"Te escribo con mucho entusiasmo porque vi publicada la vacante de Contrato de Aprendizaje para {empresa} "
        f"en la plataforma Caprendizaje del SENA, y me llamó especialmente la atención el enfoque de sus proyectos.\n\n"
        f"Mi nombre es {CANDIDATE['name']}, aprendiz en etapa productiva del programa Tecnólogo en Análisis y "
        f"Desarrollo de Software (ADSO). Para los requerimientos de su equipo en {tech_match}, cuento con preparación "
        f"práctica y proyectos funcionales desplegados en producción.\n\n"
        f"¿Por qué puedo sumar valor a {empresa} desde el primer día?\n"
        f"1. Solidez técnica y metodológica: Cuento con doble background técnico (7 semestres aprobados de Ingeniería "
        f"Mecatrónica y título como Técnico en Sistemas), lo que me permite comprender tanto la lógica algorítmica profunda como la arquitectura de software moderna.\n"
        f"2. Stack aplicado: Experiencia desarrollando con JavaScript (React, Node.js), Java (Spring Boot), bases de datos SQL relacionales, control de versiones Git/GitHub y despliegue cloud.\n"
        f"3. Disponibilidad total e inmediata: Mi contrato de aprendizaje está 100% avalado por el SENA para formalización inmediata.\n\n"
        f"Pongo a tu disposición mi Hoja de Vida detallada con certificados académicos y mi repositorio de código:\n"
        f"📄 Hoja de Vida (CV) y Certificados: {cv_url}\n"
        f"💻 Portafolio de Código en GitHub: {CANDIDATE['github_url']}\n"
        f"🔗 Perfil Profesional en LinkedIn: {CANDIDATE['linkedin_url']}\n\n"
        f"Si te parece bien, ¿podríamos conversar brevemente 5 minutos esta semana para revisar cómo puedo integrarme "
        f"a sus objetivos de desarrollo de software?\n\n"
        f"Muchas gracias por tu tiempo y consideración.\n\n"
        f"Cordialmente,\n\n"
        f"{CANDIDATE['name']}\n"
        f"{CANDIDATE['role']}\n"
        f"📱 {CANDIDATE['phone']} · ✉️ {CANDIDATE['email']}"
    )

    return cuerpo

def build_high_conversion_whatsapp(empresa, contacto_info, funciones, solicitud_id):
    """
    Genera un mensaje de WhatsApp directo, conversacional y de alta respuesta.
    """
    saludo = contacto_info["saludo_wa"]
    tech_match = extract_tech_match(funciones, "")
    cv_url = get_tracking_cv_url(empresa, solicitud_id, contacto_info["name"], "whatsapp")

    return (
        f"{saludo} Mi nombre es {CANDIDATE['name']}, aprendiz del Tecnólogo en Análisis y Desarrollo de Software (ADSO) del SENA.\n\n"
        f"Me comunico con mucho interés tras ver la vacante de Contrato de Aprendizaje para *{empresa}* en Caprendizaje. "
        f"Cuento con preparación práctica en *{tech_match}*, 7 semestres de Ingeniería Mecatrónica y disponibilidad inmediata para iniciar etapa productiva.\n\n"
        f"Comparto mi Hoja de Vida y proyectos de código:\n"
        f"📄 *CV y Certificados:* {cv_url}\n"
        f"💻 *GitHub:* {CANDIDATE['github_url']}\n"
        f"🔗 *LinkedIn:* {CANDIDATE['linkedin_url']}\n\n"
        f"¿Me indicarías por favor con quién o a qué correo puedo coordinar una breve entrevista técnica? ¡Muchas gracias!"
    )

def build_high_conversion_linkedin(empresa, contacto_info, solicitud_id):
    """
    Genera una nota de conexión para LinkedIn (< 300 caracteres) optimizada para aceptación.
    """
    nombre = contacto_info["name"] if contacto_info["type"] == "person" else f"equipo de {empresa}"
    cv_url = get_tracking_cv_url(empresa, solicitud_id, contacto_info["name"], "linkedin")
    
    note = f"Hola {nombre}, soy Juan Manuel, aprendiz ADSO SENA (background Mecatrónica). Me postulo a la vacante en {empresa}. Proyectos en github.com/lakerstrake y CV listo. ¡Me encantaría conectar!"
    if len(note) > 298:
        note = f"Hola {nombre}, soy Juan Manuel, aprendiz ADSO SENA. Me postulo a la vacante en {empresa}. Código en github.com/lakerstrake. ¡Me encantaría conectar!"
    return note

def process_all_companies():
    print("=" * 70)
    print(" ACTUALIZACIÓN DE COPYWRITING PERSUASIVO & SISTEMA DE SEGUIMIENTO DE CV")
    print("=" * 70)

    if not os.path.exists(DATA_JSON):
        print(f"[!] Error: No se encontró {DATA_JSON}")
        return

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        companies = json.load(f)

    print(f"[*] Procesando {len(companies)} vacantes...")

    for comp in companies:
        empresa = comp.get("empresa", "Empresa Registrada")
        raw_contacto = comp.get("contacto", "")
        solicitud_id = comp.get("solicitud_id", "")
        perfil = comp.get("perfil_requerido", "")
        funciones = comp.get("funciones", "")

        contacto_info = clean_contact_person(raw_contacto, empresa)

        # Generar copies de alta conversión
        comp["contacto_saludo"] = contacto_info["saludo_email"]
        comp["contacto_tipo"] = contacto_info["type"]
        comp["contacto_nombre_limpio"] = contacto_info["name"]
        comp["cv_tracking_url"] = get_tracking_cv_url(empresa, solicitud_id, contacto_info["name"], "portal")
        
        comp["correo_formal_completo"] = build_high_conversion_email(empresa, contacto_info, perfil, funciones, solicitud_id)
        comp["whatsapp_message"] = build_high_conversion_whatsapp(empresa, contacto_info, funciones, solicitud_id)
        comp["linkedin_connect_message"] = build_high_conversion_linkedin(empresa, contacto_info, solicitud_id)

    # Guardar JSON actualizado
    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)

    # Actualizar data.js para producción
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Clean Data Registry with Persuasive Pitch Engine\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False)
        f.write(";\n")

    print(f"[✓] {len(companies)} vacantes actualizadas con éxito:")
    print("    - Eliminación total de 'Estimado/a' -> Saludos 100% personalizados y naturales.")
    print("    - Copywriting persuasivo con Cialdini (reciprocidad, autoridad, coincidencia técnica y CTA).")
    print("    - URLs inteligentes de seguimiento de CV (/cv?empresa=...) con alertas en tiempo real.")

if __name__ == "__main__":
    process_all_companies()
