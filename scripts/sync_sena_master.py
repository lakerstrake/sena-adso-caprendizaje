import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import sys
import pandas as pd
import concurrent.futures
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
DATA_DIR = os.path.join(OUTPUT_DIR, "assets", "data")
JS_DIR = os.path.join(OUTPUT_DIR, "assets", "js")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(JS_DIR, exist_ok=True)

CANDIDATE = {
    "name": "Juan Manuel Lagos Monroy",
    "role": "Desarrollador Web Junior · Aprendiz ADSO SENA",
    "email": "jmlagos2003@gmail.com",
    "phone": "(+57) 300 727 9875",
    "phone_clean": "573007279875",
    "cv_url": "https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing",
    "cert_url": "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing",
    "github_url": "https://github.com/lakerstrake",
    "linkedin_url": "https://linkedin.com/in/juan-manuel-lagos-monroy"
}

def clean_text(text):
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text).replace('\xa0', ' ')).strip()

def clean_email(email_str):
    if not email_str:
        return ""
    cleaned = re.sub(r'(?i)imagen\s*de\s*perfil.*', '', str(email_str)).strip()
    m = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+)', cleaned)
    if m:
        return m.group(1).lower().rstrip('.')
    return clean_text(cleaned)

def extract_tags(text):
    if not text:
        return ["SQL", "Frontend / Web", "Git", "APIs REST"]
    keywords = [
        "python", "javascript", "typescript", "react", "angular", "vue", "node", "nodejs",
        "java", "c#", ".net", "php", "laravel", "sql", "mysql", "postgresql", "sql server", "oracle", "mongodb",
        "aws", "azure", "docker", "git", "github", "gitlab", "devops", "linux",
        "flutter", "kotlin", "swift", "android", "ios", "qa", "testing", "soporte",
        "html", "css", "bootstrap", "tailwind", "api", "rest", "power bi", "excel", "seguridad"
    ]
    text_lower = text.lower()
    found = []
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            found.append(kw.upper() if kw in ["sql", "qa", "api", "aws", "css", "html", "php"] else kw.capitalize())
    res = list(dict.fromkeys(found))
    return res if res else ["SQL", "Frontend / Web", "Git", "APIs REST"]

def extract_modality(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["remoto", "teletrabajo", "home office", "virtual"]):
        return "Remoto"
    elif any(k in text_lower for k in ["hibrid", "híbrid"]):
        return "Híbrido"
    elif "presencial" in text_lower:
        return "Presencial"
    return "Presencial / No especificado"

GENERIC_TERMS = [
    "seleccion", "selección", "talento", "humano", "rrhh", "recursos", "gestion", "gestión",
    "administracion", "administración", "recepcion", "recepción", "gerencia", "direccion",
    "dirección", "departamento", "dpto", "contratacion", "contratación", "sin registrar",
    "no registra", "sena", "aprendiz", "caprendizaje", "coordinacion", "coordinación",
    "jefe", "lider", "líder", "analista", "asistente", "auxiliar", "contacto"
]

def clean_contact_person(raw_contact, empresa):
    if not raw_contact:
        short_emp = re.sub(r'(?i)\s+(s\.?a\.?s\.?|s\.?a\.?|ltda\.?|e\.?u\.?|sucursal\s+colombia|colombia)$', '', empresa).strip()
        return {
            "type": "team",
            "name": f"equipo de desarrollo en {short_emp}",
            "saludo_email": f"Hola equipo de desarrollo en {short_emp},",
            "saludo_wa": f"Hola equipo de {short_emp}, un cordial saludo.",
            "saludo_li": f"Hola equipo de {short_emp},"
        }

    cleaned = re.sub(r'(?i)^(ing\.|lic\.|dr\.|dra\.|psic\.|sr\.|sra\.|abg\.)\s*', '', raw_contact).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    lower_c = cleaned.lower()

    if any(term in lower_c for term in GENERIC_TERMS) or len(cleaned) < 3:
        short_emp = re.sub(r'(?i)\s+(s\.?a\.?s\.?|s\.?a\.?|ltda\.?|e\.?u\.?|sucursal\s+colombia|colombia)$', '', empresa).strip()
        return {
            "type": "team",
            "name": f"equipo de desarrollo en {short_emp}",
            "saludo_email": f"Hola equipo de desarrollo en {short_emp},",
            "saludo_wa": f"Hola equipo de {short_emp}, un cordial saludo.",
            "saludo_li": f"Hola equipo de {short_emp},"
        }

    parts = cleaned.split()
    first_name = parts[0].capitalize()
    if len(parts) >= 2 and first_name.lower() in ["juan", "maría", "maria", "luis", "carlos", "ana", "jorge", "laura", "paula", "andrea", "claudia"]:
        first_name = f"{first_name} {parts[1].capitalize()}"

    return {
        "type": "person",
        "name": first_name,
        "saludo_email": f"Hola {first_name},",
        "saludo_wa": f"Hola {first_name}, un cordial saludo.",
        "saludo_li": f"Hola {first_name},"
    }

def extract_tech_match(funciones, perfil):
    combo = f"{funciones} {perfil}".lower()
    matches = []
    if any(k in combo for k in ["sql", "base de datos", "bases de datos", "mysql", "postgres", "consultas", "oracle"]):
        matches.append("diseño relacional, consultas complejas SQL y optimización de bases de datos")
    if any(k in combo for k in ["react", "frontend", "javascript", "web", "html", "css", "angular", "vue"]):
        matches.append("desarrollo web frontend moderno con JavaScript, React y consumo de APIs")
    if any(k in combo for k in ["backend", "node", "python", "java", "c#", ".net", "php", "api", "rest", "microservicios"]):
        matches.append("arquitectura backend robusta, creación de endpoints RESTful e integración de servicios")
    if any(k in combo for k in ["qa", "testing", "pruebas", "calidad"]):
        matches.append("aseguramiento de calidad (QA), diseño de planes de pruebas y verificación de software")
    if not matches:
        matches.append("desarrollo de software full-stack con React, Node.js, SQL y buenas prácticas de ingeniería")
    return " y ".join(matches)

def build_formal_email(empresa, contacto, funciones, perfil, solicitud_id=""):
    contacto_info = clean_contact_person(contacto, empresa)
    tech_match = extract_tech_match(funciones, perfil)

    return (
        f"{contacto_info['saludo_email']}\n\n"
        f"Me dirijo a ustedes con gran entusiasmo para postularme a la vacante de Contrato de Aprendizaje "
        f"en {empresa} (Solicitud SGVA #{solicitud_id}).\n\n"
        f"Soy aprendiz del programa Tecnólogo en Análisis y Desarrollo de Software (ADSO) en el SENA, con una sólida "
        f"base académica previa de 7 semestres de Ingeniería Mecatrónica y titulación como Técnico en Sistemas. Esta formación "
        f"multidisciplinaria me permite abordar el desarrollo de software con rigor algorítmico, capacidad analítica y enfoque "
        f"en resolución estructurada de problemas.\n\n"
        f"Revisando los requerimientos de la posición, puedo aportar valor inmediato en {tech_match}, aplicando metodologías "
        f"ágiles (Scrum), control de versiones Git y patrones de diseño limpios.\n\n"
        f"Tengo disponibilidad inmediata para iniciar la etapa productiva bajo la modalidad requerida.\n\n"
        f"Adjunto mi Hoja de Vida y enlaces directos para su consulta:\n"
        f"📄 Hoja de Vida (PDF Drive): {CANDIDATE['cv_url']}\n"
        f"🎓 Certificados Académicos (Drive): {CANDIDATE['cert_url']}\n"
        f"💻 Repositorios y Código (GitHub): {CANDIDATE['github_url']}\n"
        f"🔗 Perfil Profesional en LinkedIn: {CANDIDATE['linkedin_url']}\n\n"
        f"Agradezco de antemano su atención y quedo a su entera disposición para coordinar una breve entrevista técnica.\n\n"
        f"Cordialmente,\n\n"
        f"{CANDIDATE['name']}\n"
        f"{CANDIDATE['role']}\n"
        f"📱 {CANDIDATE['phone']} · ✉️ {CANDIDATE['email']}"
    )

def build_whatsapp_pitch(empresa, contacto, funciones="", solicitud_id=""):
    contacto_info = clean_contact_person(contacto, empresa)
    tech_match = extract_tech_match(funciones, "")

    return (
        f"{contacto_info['saludo_wa']} Mi nombre es {CANDIDATE['name']}, aprendiz del Tecnólogo en Análisis y Desarrollo de Software (ADSO) del SENA.\n\n"
        f"Me comunico con mucho interés tras ver la vacante de Contrato de Aprendizaje para *{empresa}* en Caprendizaje (Solicitud #{solicitud_id}). "
        f"Cuento con preparación práctica en *{tech_match}*, 7 semestres de Ingeniería Mecatrónica y disponibilidad inmediata para iniciar etapa productiva.\n\n"
        f"Comparto mi Hoja de Vida y proyectos de código:\n"
        f"📄 *Hoja de Vida:* {CANDIDATE['cv_url']}\n"
        f"🎓 *Certificados:* {CANDIDATE['cert_url']}\n"
        f"💻 *GitHub:* {CANDIDATE['github_url']}\n"
        f"🔗 *LinkedIn:* {CANDIDATE['linkedin_url']}\n\n"
        f"¿Me indicarían por favor con quién o a qué correo puedo coordinar una breve entrevista técnica? ¡Muchas gracias!"
    )

def build_linkedin_pitch(empresa, contacto, solicitud_id=""):
    contacto_info = clean_contact_person(contacto, empresa)
    nombre = contacto_info["name"] if contacto_info["type"] == "person" else f"equipo de {empresa}"
    return f"Hola {nombre}, soy Juan Manuel, aprendiz ADSO SENA (background Mecatrónica). Me postulo a la vacante en {empresa}. Proyectos en github.com/lakerstrake y CV listo. ¡Me encantaría conectar!"

def classify_tier_legacy(empresa_name, profile_text, functions_text):
    combo = f"{empresa_name} {profile_text} {functions_text}".lower()
    t1_kw = ["software", "desarrollo", "programador", "frontend", "backend", "full stack", "react", "java", "node", "python", "tecnolog", "sistemas de informacion", "ingenieria de software"]
    t2_kw = ["bases de datos", "sql", "analista de datos", "infraestructura", "servidores", "devops", "cloud", "seguridad informatica", "redes", "consultor ti"]
    t3_kw = ["soporte tecnico", "mesa de ayuda", "help desk", "mantenimiento de equipos", "hardware", "asistencia tecnica", "sistemas"]
    t4_kw = ["administrativo", "digitador", "archivo", "ofimatica", "secretaria", "call center", "operativo"]

    if any(k in combo for k in ["desarrollo de software", "software", "developer", "programacion", "fullstack", "frontend", "backend", "stefanini", "designer software", "arquitecsoft", "nalsani"]):
        return {
            "id": "TIER_1", "badge": "Tier 1 · Software & Tech", "color": "purple", "score": 95,
            "escalabilidad": 96, "escalabilidad_nivel": "Exponencial (Alta Demanda Global)",
            "techo_salarial": " - + COP (.0k - .5k USD)", "rating": 4.3, "fuente": "Glassdoor / Computrabajo"
        }
    elif any(k in combo for k in t2_kw):
        return {
            "id": "TIER_2", "badge": "Tier 2 · Sistemas & Datos", "color": "blue", "score": 80,
            "escalabilidad": 88, "escalabilidad_nivel": "Sólida & Constante",
            "techo_salarial": ".5M - .0M COP (.2k - .8k USD)", "rating": 4.0, "fuente": "Computrabajo / LinkedIn"
        }
    elif any(k in combo for k in t3_kw):
        return {
            "id": "TIER_3", "badge": "Tier 3 · Soporte TI & Redes", "color": "amber", "score": 65,
            "escalabilidad": 72, "escalabilidad_nivel": "Media (Transicional)",
            "techo_salarial": ".0M - .0M COP (.3k - .3k USD)", "rating": 3.8, "fuente": "Computrabajo"
        }
    elif any(k in combo for k in t4_kw):
        return {
            "id": "TIER_4", "badge": "Tier 4 · Operación General", "color": "gray", "score": 45,
            "escalabilidad": 50, "escalabilidad_nivel": "Básica",
            "techo_salarial": ".5M - .5M COP ( - .4k USD)", "rating": 3.5, "fuente": "Directorio Empresas"
        }
    else:
        return {
            "id": "TIER_5", "badge": "Tier 5 · Baja Afinidad ADSO", "color": "rose", "score": 30,
            "escalabilidad": 35, "escalabilidad_nivel": "Limitada",
            "techo_salarial": ".5M - .0M COP", "rating": 3.2, "fuente": "Directorio Empresas"
        }

def run_pipeline():
    print("=" * 70)
    print(" SGVA SENA - FULL LIVE SYNC & MULTI-AI ENRICHMENT")
    print("=" * 70)
    
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9"
    })

    print("[1/5] Autenticando en portal oficial SGVA...")
    r = session.get("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
    viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"] if soup.find("input", {"id": "__VIEWSTATEGENERATOR"}) else ""

    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventvalidation,
        "tbLoginUsuario": "1074808317",
        "__tbPasswordUsuario": "C26D398F",
        "ini_session_aprendiz": "Iniciar sesión"
    }
    session.post("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", data=payload, allow_redirects=False, timeout=20)

    print("[2/5] Consultando todas las solicitudes activas de ADSO a nivel nacional (dpto: 0)...")
    r_sol = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params={
        "especialidad": "136456",
        "dpto": 0,
        "ciudad": "0",
        "RSocial": ""
    }, timeout=20)
    
    sol_list = r_sol.json().get("aaData", [])
    print(f"[+] Total de vacantes activas encontradas en SGVA: {len(sol_list)}")

    solicitudes_resumen = []
    for item in sol_list:
        soup_btn = BeautifulSoup(item[0], "html.parser")
        btn = soup_btn.find(attrs={"data-id-solicitud": True})
        sol_id = btn["data-id-solicitud"] if btn else None
        solicitudes_resumen.append({
            "solicitud_id": sol_id,
            "empresa_resumen": clean_text(item[1]),
            "departamento_resumen": clean_text(item[2]),
            "ciudad_resumen": clean_text(item[3]),
            "vacantes_resumen": int(item[4]) if item[4] and str(item[4]).isdigit() else 1,
            "fecha_creacion_resumen": clean_text(item[5]),
            "fecha_cierre_resumen": clean_text(item[6])
        })

    print("[3/5] Extrayendo detalle completo de cada vacante en paralelo...")
    detalles_completos = []
    total = len(solicitudes_resumen)

    def fetch_detail(sol_info):
        s_id = sol_info["solicitud_id"]
        if not s_id:
            return None
        try:
            r_det = session.get(
                "https://caprendizaje.sena.edu.co/sgva/Solicitudes/ConsultarSolicitud",
                params={"solicitudID": s_id},
                timeout=25
            )
            r_det.encoding = 'utf-8'
            data = r_det.json().get("aaData", [])
            if data and len(data) > 0:
                d = data[0]
                empresa = clean_text(d[16]) if len(d) > 16 and d[16] else sol_info["empresa_resumen"]
                nit = clean_text(d[17]) if len(d) > 17 else ""
                perfil = clean_text(d[1]) if len(d) > 1 else ""
                funciones = clean_text(d[2]) if len(d) > 2 else ""
                dpto = clean_text(d[3]).title() if len(d) > 3 else sol_info["departamento_resumen"].title()
                ciudad = clean_text(d[4]).title() if len(d) > 4 else sol_info["ciudad_resumen"].title()
                direccion = clean_text(d[5]) if len(d) > 5 else ""
                telefono = clean_text(d[6]) if len(d) > 6 else ""
                contacto = clean_text(d[7]) if len(d) > 7 else ""
                email = clean_email(d[9]) if len(d) > 9 else ""
                
                vacantes = int(d[8]) if len(d) > 8 and str(d[8]).isdigit() else sol_info["vacantes_resumen"]
                aplicados = int(d[15]) if len(d) > 15 and str(d[15]).isdigit() else 0
                
                fecha_creacion = clean_text(d[10]) if len(d) > 10 else sol_info["fecha_creacion_resumen"]
                fecha_cierre = clean_text(d[12]) if len(d) > 12 else sol_info["fecha_cierre_resumen"]
                
                tier_info = classify_tier_legacy(empresa, perfil, funciones)
                tags = extract_tags(f"{perfil} {funciones}")
                modalidad = extract_modality(f"{perfil} {funciones}")

                is_wa = False
                wa_num = ""
                if telefono and len(re.sub(r'\D', '', telefono)) >= 10:
                    clean_digits = re.sub(r'\D', '', telefono)
                    if clean_digits.startswith("3"):
                        is_wa = True
                        wa_num = f"57{clean_digits}"

                wa_msg = build_whatsapp_pitch(empresa, contacto, funciones, s_id)
                email_msg = build_formal_email(empresa, contacto, funciones, perfil, s_id)
                li_msg = build_linkedin_pitch(empresa, contacto, s_id)

                return {
                    "solicitud_id": str(s_id),
                    "empresa": empresa.upper(),
                    "nit": str(nit).strip(),
                    "departamento": dpto,
                    "ciudad": ciudad,
                    "direccion": direccion,
                    "telefono": telefono,
                    "contacto": contacto,
                    "email": email,
                    "modalidad": modalidad,
                    "vacantes": vacantes,
                    "postulados": aplicados,
                    "competencia_ratio": round(aplicados / max(1, vacantes), 2),
                    "ranking_posicion": 0,
                    "puntaje_exito": tier_info["score"],
                    "cat_id": tier_info["id"],
                    "cat_badge": tier_info["badge"],
                    "cat_color": tier_info["color"],
                    "reputacion_rating": tier_info["rating"],
                    "reputacion_fuente": tier_info["fuente"],
                    "reputacion_nivel": "Excelente (Sector TI)" if tier_info["id"] == "TIER_1" else "Buena (Sector Productivo)",
                    "apoyo_sostenimiento": ".423.500 COP (100% SMMLV)",
                    "salario_egresado_jr": ".800.000 a .500.000+ COP (Al culminar ADSO)",
                    "escalabilidad_score": tier_info["escalabilidad"],
                    "escalabilidad_nivel": tier_info["escalabilidad_nivel"],
                    "techo_salarial_5anios": tier_info["techo_salarial"],
                    "stack_tags": tags,
                    "is_whatsapp": is_wa,
                    "whatsapp_number": wa_num,
                    "whatsapp_message": wa_msg,
                    "whatsapp_url": f"https://wa.me/{wa_num}?text={requests.utils.quote(wa_msg)}" if is_wa else "",
                    "linkedin_contact_search_url": f"https://www.linkedin.com/search/results/people/?keywords={requests.utils.quote(contacto + ' ' + empresa)}" if contacto else f"https://www.linkedin.com/search/results/companies/?keywords={requests.utils.quote(empresa)}",
                    "linkedin_connect_message": li_msg,
                    "correo_formal_completo": email_msg,
                    "curva_aprendizaje_titulo": "Desarrollo de Software Full-Stack & Arquitectura Cloud",
                    "curva_aprendizaje_detalle": "Dominio de frameworks modernos, bases de datos relacionales/NoSQL, control de versiones Git y metodologías ágiles.",
                    "perfil_requerido": perfil,
                    "funciones": funciones,
                    "fecha_cierre": fecha_cierre,
                    "facilidad_code": "MOD"
                }
        except Exception as e:
            print(f"[!] Error extrayendo {s_id}: {e}")
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_detail, sol): sol for sol in solicitudes_resumen}
        count = 0
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                detalles_completos.append(res)
            count += 1
            if count % 40 == 0 or count == total:
                print(f"  -> Progreso: {count}/{total} vacantes extraídas...")

    print(f"[+] Total vacantes procesadas con éxito: {len(detalles_completos)}")

    # Guardar base limpia
    json_path = os.path.join(DATA_DIR, "empresas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(detalles_completos, f, ensure_ascii=False, indent=2)

    print("[4/5] Aplicando pipelines de enriquecimiento (Multi-AI Consensus + Panorama Empresarial)...")
    
    # 1. Multi-AI Ranking
    os.system('python scripts/etl/multi_ai_ranking.py')
    # 2. Company Panorama
    os.system('python scripts/etl/company_panorama.py')

    # 3. Exportar CSV y Excel
    with open(json_path, "r", encoding="utf-8") as f:
        final_list = json.load(f)

    df = pd.DataFrame(final_list)
    cols = ["empresa", "departamento", "ciudad", "vacantes", "postulados", "competencia_ratio", "puntaje_exito", "cat_badge", "contacto", "email", "telefono", "nit", "solicitud_id", "fecha_cierre"]
    cols_exist = [c for c in cols if c in df.columns]
    df_sub = df[cols_exist]
    
    csv_path = os.path.join(DATA_DIR, "empresas.csv")
    xlsx_path = os.path.join(DATA_DIR, "empresas.xlsx")
    df_sub.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df_sub.to_excel(xlsx_path, index=False, engine="openpyxl")

    # 4. Actualizar data.js
    data_js_path = os.path.join(JS_DIR, "data.js")
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Live Master Dataset\n */\nwindow.RAW_DATA = ")
        json.dump(final_list, f, ensure_ascii=False)
        f.write(";\n")

    print(f"[5/5] Sincronización finalizada exitosamente. Total vacantes: {len(final_list)}")
    return len(final_list)

if __name__ == "__main__":
    run_pipeline()
