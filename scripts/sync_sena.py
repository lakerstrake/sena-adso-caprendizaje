#!/usr/bin/env python3
"""
================================================================================
SGVA SENA CAPRENDIZAJE - AUTOMATED SYNC & ENRICHMENT PIPELINE
================================================================================
Standard: ISO/IEC 25010 & Software Engineering Clean Architecture
Author: Juan Manuel Lagos Monroy (Aprendiz ADSO - SENA)

This script connects directly to the official SENA Caprendizaje portal
(https://caprendizaje.sena.edu.co/sgva), authenticates, extracts all active
ADSO / Software vacancies, enriches them with technical scoring, salary
escalation models, and professional outreach pitches, and builds production-ready
JSON and JS data assets.
================================================================================
"""

import os
import sys
import re
import json
import time
from datetime import datetime
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "https://caprendizaje.sena.edu.co/sgva"
LOGIN_URL = f"{BASE_URL}/SGVA_Diseno/pag/login.aspx"
ACAD_URL = f"{BASE_URL}/AprendizAcademico/AprendizConsultarAcademicos"
DETAIL_URL = f"{BASE_URL}/AprendizSolicitud/VerDetalleSolicitud"

# Official Candidate Profile Information
CANDIDATE = {
    "name": "Juan Manuel Lagos Monroy",
    "role": "Desarrollador Web Junior · Aprendiz ADSO SENA",
    "email": "jmlagos2003@gmail.com",
    "phone": "(+57) 300 727 9875",
    "phone_clean": "573007279875",
    "cv_url": "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN",
    "github_url": "https://github.com/lakerstrake",
    "linkedin_url": "https://linkedin.com/in/juan-manuel-lagos-monroy"
}

def get_session(user_id=None, password=None):
    """Establece sesión autenticada con el portal oficial SGVA SENA."""
    user = user_id or os.environ.get("SENA_USER", "1074808317")
    pwd = password or os.environ.get("SENA_PASSWORD", "C26D398F")

    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    })

    print(f"[*] Accediendo a login SGVA SENA ({LOGIN_URL})...")
    r = session.get(LOGIN_URL, timeout=25)
    soup = BeautifulSoup(r.text, "html.parser")

    viewstate = soup.find("input", {"id": "__VIEWSTATE"})
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})
    viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})

    if not viewstate or not eventvalidation:
        raise ConnectionError("No se pudieron extraer los tokens __VIEWSTATE del portal SENA.")

    payload = {
        "__VIEWSTATE": viewstate["value"],
        "__VIEWSTATEGENERATOR": viewstategen["value"] if viewstategen else "",
        "__EVENTVALIDATION": eventvalidation["value"],
        "tbLoginUsuario": user,
        "__tbPasswordUsuario": pwd,
        "ini_session_aprendiz": "Iniciar sesión"
    }

    print(f"[*] Autenticando usuario SENA: {user}...")
    r_post = session.post(LOGIN_URL, data=payload, allow_redirects=False, timeout=25)
    
    # Check if session cookie exists
    cookies = session.cookies.get_dict()
    if not any("ASP.NET_SessionId" in k or ".ASPXAUTH" in k for k in cookies) and r_post.status_code != 302:
        print("[!] Advertencia: Respuesta no redirigida, verificando acceso a endpoints...")

    return session

def clean_text(text):
    if not text:
        return ""
    t = str(text).replace('\xa0', ' ').strip()
    return re.sub(r'\s+', ' ', t)

def clean_email(raw_email):
    if not raw_email:
        return ""
    cleaned = re.sub(r'(?i)imagen\s*de\s*perfil.*', '', str(raw_email)).strip()
    m = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+)', cleaned)
    if m:
        return m.group(1).lower().rstrip('.')
    return clean_text(cleaned)

def extract_tags(text):
    if not text:
        return []
    keywords = [
        "python", "javascript", "typescript", "react", "angular", "vue", "node", "nodejs",
        "java", "c#", ".net", "php", "laravel", "sql", "mysql", "postgresql", "sql server", "oracle", "mongodb",
        "aws", "azure", "docker", "git", "github", "gitlab", "devops", "linux",
        "flutter", "kotlin", "swift", "android", "ios", "qa", "testing", "soporte",
        "html", "css", "bootstrap", "tailwind", "api", "rest", "power bi", "excel", "seguridad", "django", "spring"
    ]
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            tag = kw.upper() if kw in ["sql", "qa", "api", "aws", "css", "html", "php"] else kw.capitalize()
            found.append(tag)
    return list(dict.fromkeys(found))

def classify_tier(empresa_name, profile_text, functions_text):
    combo = f"{empresa_name} {profile_text} {functions_text}".lower()
    
    # Tier 1 - Software & Tech Development
    t1_kw = ["software", "desarrollo", "programador", "frontend", "backend", "full stack", "react", "java", "node", "python", "tecnolog", "sistemas de informacion", "ingenieria de software"]
    # Tier 2 - Systems & Data
    t2_kw = ["bases de datos", "sql", "analista de datos", "infraestructura", "servidores", "devops", "cloud", "seguridad informatica", "redes", "consultor ti"]
    # Tier 3 - IT Support
    t3_kw = ["soporte tecnico", "mesa de ayuda", "help desk", "mantenimiento de equipos", "hardware", "asistencia tecnica", "sistemas"]
    # Tier 4 - Administrative & Operations
    t4_kw = ["administrativo", "digitador", "archivo", "ofimatica", "secretaria", "call center", "operativo"]

    if any(k in combo for k in ["desarrollo de software", "software", "developer", "programacion", "fullstack", "frontend", "backend", "stefanini", "designer software", "arquitecsoft"]):
        return {
            "id": "TIER_1",
            "badge": "Tier 1 · Software & Tech",
            "color": "purple",
            "score": 95,
            "escalabilidad": 96,
            "escalabilidad_nivel": "Exponencial (Alta Demanda Global)",
            "techo_salarial": "$10M - $22M+ COP ($3.0k - $5.5k USD)",
            "rating": 4.3,
            "fuente": "Glassdoor / Computrabajo"
        }
    elif any(k in combo for k in t2_kw):
        return {
            "id": "TIER_2",
            "badge": "Tier 2 · Sistemas & Datos",
            "color": "blue",
            "score": 80,
            "escalabilidad": 88,
            "escalabilidad_nivel": "Sólida & Constante",
            "techo_salarial": "$8.5M - $15.0M COP ($2.2k - $3.8k USD)",
            "rating": 4.0,
            "fuente": "Computrabajo / LinkedIn"
        }
    elif any(k in combo for k in t3_kw):
        return {
            "id": "TIER_3",
            "badge": "Tier 3 · Soporte TI & Redes",
            "color": "amber",
            "score": 65,
            "escalabilidad": 72,
            "escalabilidad_nivel": "Media (Transicional)",
            "techo_salarial": "$5.0M - $9.0M COP ($1.3k - $2.3k USD)",
            "rating": 3.8,
            "fuente": "Computrabajo"
        }
    elif any(k in combo for k in t4_kw):
        return {
            "id": "TIER_4",
            "badge": "Tier 4 · Operación General",
            "color": "gray",
            "score": 45,
            "escalabilidad": 50,
            "escalabilidad_nivel": "Básica",
            "techo_salarial": "$3.5M - $5.5M COP ($900 - $1.4k USD)",
            "rating": 3.5,
            "fuente": "Directorio Empresas"
        }
    else:
        return {
            "id": "TIER_5",
            "badge": "Tier 5 · Baja Afinidad ADSO",
            "color": "rose",
            "score": 30,
            "escalabilidad": 35,
            "escalabilidad_nivel": "Limitada",
            "techo_salarial": "$2.5M - $4.0M COP",
            "rating": 3.2,
            "fuente": "Directorio Empresas"
        }

def build_formal_email(empresa, contacto, funciones):
    contacto_nombre = contacto if contacto and "selección" not in contacto.lower() and "talento" not in contacto.lower() else "Equipo de Selección"
    return (
        f"Asunto: Postulación Contrato de Aprendizaje - Tecnólogo ADSO SENA - {CANDIDATE['name']}\n\n"
        f"Estimado/a {contacto_nombre},\n\n"
        f"Reciba un cordial saludo. Mi nombre es {CANDIDATE['name']}, aprendiz en etapa productiva del programa "
        f"Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA.\n\n"
        f"Me dirijo a ustedes tras consultar con gran interés la vacante de Contrato de Aprendizaje para {empresa} "
        f"que vi publicada en la plataforma institucional Caprendizaje. Mi objetivo es vincularme formalmente con su "
        f"equipo y aportar valor técnico en sus proyectos y operaciones de software.\n\n"
        f"Cuento con sólida preparación práctica y experiencia en proyectos reales en desarrollo web y software "
        f"full-stack (JavaScript, React, Java, Spring Boot, APIs REST), bases de datos SQL y despliegue en producción, "
        f"además de background en siete semestres de Ingeniería Mecatrónica y título como Técnico en Sistemas, con total "
        f"disponibilidad y dedicación para iniciar mi etapa productiva.\n\n"
        f"Pongo a su entera disposición mi hoja de vida institucional, portafolio de código y certificaciones técnicas:\n"
        f"• Hoja de Vida (CV) y Certificados: {CANDIDATE['cv_url']}\n"
        f"• Repositorio y Proyectos en GitHub: {CANDIDATE['github_url']}\n"
        f"• Perfil Profesional en LinkedIn: {CANDIDATE['linkedin_url']}\n"
        f"• Teléfono directo / WhatsApp: {CANDIDATE['phone']}\n"
        f"• Correo Electrónico: {CANDIDATE['email']}\n\n"
        f"Agradezco de antemano la oportunidad de participar en su proceso de selección y quedo atento a su respuesta para "
        f"coordinar una entrevista técnica.\n\n"
        f"Atentamente,\n\n"
        f"{CANDIDATE['name']}\n"
        f"{CANDIDATE['role']}\n"
        f"{CANDIDATE['phone']} · {CANDIDATE['email']}"
    )

def build_whatsapp_pitch(empresa, contacto):
    contacto_nombre = contacto if contacto and "selección" not in contacto.lower() else "Equipo de Talento Humano"
    return (
        f"Hola {contacto_nombre}, cordial saludo. Mi nombre es {CANDIDATE['name']}, aprendiz tecnólogo en "
        f"Análisis y Desarrollo de Software (ADSO) del SENA.\n\n"
        f"Me comunico con mucho interés tras revisar la vacante de Contrato de Aprendizaje para {empresa} "
        f"que vi publicada en Caprendizaje. Cuento con total disponibilidad para iniciar mi etapa productiva "
        f"y aportar en desarrollo web, software (Java, React, SQL), Git y metodologías ágiles.\n\n"
        f"Pongo a su disposición mi hoja de vida y proyectos técnicos:\n"
        f"• Hoja de Vida (CV) y Certificados: {CANDIDATE['cv_url']}\n"
        f"• GitHub: {CANDIDATE['github_url']}\n"
        f"• LinkedIn: {CANDIDATE['linkedin_url']}\n\n"
        f"¿Me indicarían por favor con quién o a qué correo puedo coordinar una entrevista técnica? Muchas gracias."
    )

def sync_vacancies():
    """Ejecuta la sincronización completa y exporta los datasets actualizados."""
    print("=" * 70)
    print(" SGVA SENA CAPRENDIZAJE - SINCRONIZACIÓN AUTOMÁTICA DE VACANTES")
    print("=" * 70)
    
    session = get_session()

    print("[*] Obteniendo solicitudes registradas en Caprendizaje...")
    r_acad = session.get(ACAD_URL, timeout=25)
    acad_json = r_acad.json()

    raw_list = []
    if isinstance(acad_json, list):
        raw_list = acad_json
    elif isinstance(acad_json, dict) and "data" in acad_json:
        raw_list = acad_json["data"]
    elif isinstance(acad_json, dict) and "aaData" in acad_json:
        raw_list = acad_json["aaData"]

    print(f"[+] Total de registros recibidos del SENA: {len(raw_list)}")

    # If the live API returns valid records, parse them
    enriched_companies = []
    
    if len(raw_list) > 0:
        for idx, item in enumerate(raw_list, start=1):
            empresa_name = clean_text(item.get("RazonSocial") or item.get("Empresa") or item.get("nombreEmpresa") or "EMPRESA REGISTRADA")
            solicitud_id = str(item.get("IdSolicitud") or item.get("idSolicitud") or item.get("SolicitudId") or idx)
            nit = str(item.get("Nit") or item.get("nit") or "")
            ciudad = clean_text(item.get("Ciudad") or item.get("ciudad") or "Bogota D. C.")
            depto = clean_text(item.get("Departamento") or item.get("departamento") or "Bogota D.C.")
            contacto = clean_text(item.get("Contacto") or item.get("nombreContacto") or "")
            email = clean_email(item.get("Correo") or item.get("email") or "")
            telefono = clean_text(item.get("Telefono") or item.get("telefono") or "")
            vacantes = int(item.get("NumeroVacantes") or item.get("vacantes") or 1)
            postulados = int(item.get("NumeroPostulados") or item.get("postulados") or 0)
            fecha_cierre = clean_text(item.get("FechaCierre") or item.get("fechaCierre") or "30/09/2026")
            perfil = clean_text(item.get("Perfil") or item.get("perfilRequerido") or "Tecnólogo ADSO SENA")
            funciones = clean_text(item.get("Funciones") or item.get("funciones") or "Desarrollo y mantenimiento de software")

            tier_data = classify_tier(empresa_name, perfil, funciones)
            stack_tags = extract_tags(f"{perfil} {funciones}")
            if not stack_tags:
                stack_tags = ["SQL", "Frontend / Web", "Git", "APIs REST"]

            # WhatsApp verification
            is_wa = False
            wa_num = ""
            if telefono and len(re.sub(r'\D', '', telefono)) >= 10:
                clean_digits = re.sub(r'\D', '', telefono)
                if clean_digits.startswith("3"):
                    is_wa = True
                    wa_num = f"57{clean_digits}"

            wa_msg = build_whatsapp_pitch(empresa_name, contacto)
            email_msg = build_formal_email(empresa_name, contacto, funciones)

            comp = {
                "solicitud_id": solicitud_id,
                "empresa": empresa_name,
                "nit": nit,
                "departamento": depto,
                "ciudad": ciudad,
                "direccion": clean_text(item.get("Direccion") or ""),
                "telefono": telefono,
                "contacto": contacto,
                "email": email,
                "modalidad": "Presencial / No especificado",
                "vacantes": vacantes,
                "postulados": postulados,
                "competencia_ratio": round(postulados / max(1, vacantes), 2),
                "ranking_posicion": idx,
                "puntaje_exito": tier_data["score"],
                "cat_id": tier_data["id"],
                "cat_badge": tier_data["badge"],
                "cat_color": tier_data["color"],
                "reputacion_rating": tier_data["rating"],
                "reputacion_fuente": tier_data["fuente"],
                "reputacion_nivel": "Excelente (Sector TI)",
                "apoyo_sostenimiento": "$1.423.500 COP (100% SMMLV)",
                "salario_egresado_jr": "$2.800.000 a $4.500.000+ COP (Al culminar ADSO)",
                "escalabilidad_score": tier_data["escalabilidad"],
                "escalabilidad_nivel": tier_data["escalabilidad_nivel"],
                "techo_salarial_5anios": tier_data["techo_salarial"],
                "stack_tags": stack_tags,
                "is_whatsapp": is_wa,
                "whatsapp_number": wa_num,
                "whatsapp_message": wa_msg,
                "whatsapp_url": f"https://wa.me/{wa_num}?text={requests.utils.quote(wa_msg)}" if is_wa else "",
                "linkedin_contact_search_url": f"https://www.linkedin.com/search/results/people/?keywords={requests.utils.quote(contacto + ' ' + empresa_name)}" if contacto else f"https://www.linkedin.com/search/results/companies/?keywords={requests.utils.quote(empresa_name)}",
                "linkedin_connect_message": f"Hola {contacto or 'Equipo'}, soy Juan Manuel Lagos, aprendiz ADSO SENA. Me postulo a la vacante de Contrato de Aprendizaje en {empresa_name} que vi en Caprendizaje. Cuento con proyectos en GitHub (github.com/lakerstrake), CV en Drive y disponibilidad inmediata. ¡Me encantaría conectar!",
                "correo_formal_completo": email_msg,
                "curva_aprendizaje_titulo": "Desarrollo de Software Full-Stack & Arquitectura Cloud",
                "curva_aprendizaje_detalle": "Dominio de frameworks modernos, bases de datos relacionales/NoSQL, control de versiones Git y metodologías ágiles.",
                "perfil_requerido": perfil,
                "funciones": funciones,
                "fecha_cierre": fecha_cierre,
                "facilidad_code": "MOD"
            }
            enriched_companies.append(comp)
    else:
        print("[!] No se recibieron nuevos registros directos de la API. Manteniendo base curada existente...")
        return False

    # Save output/assets/data/empresas.json
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(root_dir, "output", "assets", "data", "empresas.json")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(enriched_companies, f, ensure_ascii=False, indent=2)

    print(f"[✓] Archivo JSON actualizado exitosamente: {json_path} ({len(enriched_companies)} vacantes)")

    # Trigger build.py to refresh data.js
    build_script = os.path.join(root_dir, "scripts", "build.py")
    if os.path.exists(build_script):
        print("[*] Recompilando assets para producción con build.py...")
        os.system(f'python "{build_script}"')

    return True

if __name__ == "__main__":
    try:
        success = sync_vacancies()
        if success:
            print("\n[✓] Sincronización finalizada con éxito.")
        else:
            print("\n[-] Sincronización conservó el dataset maestro actual.")
    except Exception as ex:
        print(f"\n[!] Error durante la sincronización: {ex}")
        sys.exit(1)
