import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import sys
from datetime import datetime
import pandas as pd
import concurrent.futures
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set stdout encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def get_authenticated_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })

    print("[1/5] Accediendo a la página de login SGVA SENA...")
    r = session.get("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx")
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

    print("[2/5] Autenticando con credenciales...")
    session.post(
        "https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx",
        data=payload,
        allow_redirects=False
    )
    return session

def clean_text(text):
    if text is None:
        return ""
    text = str(text).strip()
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

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
        return []
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
    return list(dict.fromkeys(found))

def extract_modality(text):
    text_lower = text.lower()
    if "remoto" in text_lower or "teletrabajo" in text_lower or "home office" in text_lower or "virtual" in text_lower:
        return "Remoto"
    elif "hibrid" in text_lower or "híbrid" in text_lower:
        return "Híbrido"
    elif "presencial" in text_lower:
        return "Presencial"
    return "Presencial / No especificado"

def fetch_all_data():
    session = get_authenticated_session()

    print("[3/5] Consultando perfil académico y lista general de solicitudes...")
    r_acad = session.get("https://caprendizaje.sena.edu.co/sgva/AprendizAcademico/AprendizConsultarAcademicos")
    acad_data = r_acad.json()
    last_acad = acad_data["aaData"][-1]
    especialidad_id = last_acad[7]
    programa_nombre = clean_text(last_acad[8])

    print(f"-> Programa: {programa_nombre} (ID Especialidad: {especialidad_id})")

    params_all = {
        "especialidad": especialidad_id,
        "dpto": 0,
        "ciudad": "0",
        "RSocial": ""
    }
    r_sol = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params=params_all)
    sol_list = r_sol.json().get("aaData", [])
    print(f"-> Encontradas {len(sol_list)} solicitudes para procesar.")

    solicitudes_resumen = []
    for item in sol_list:
        soup = BeautifulSoup(item[0], "html.parser")
        btn = soup.find(attrs={"data-id-solicitud": True})
        sol_id = btn["data-id-solicitud"] if btn else None

        solicitudes_resumen.append({
            "solicitud_id": sol_id,
            "empresa_resumen": clean_text(item[1]),
            "departamento_resumen": clean_text(item[2]),
            "ciudad_resumen": clean_text(item[3]),
            "vacantes_resumen": int(item[4]) if item[4] and str(item[4]).isdigit() else 1,
            "fecha_creacion_resumen": clean_text(item[5]),
            "fecha_cierre_resumen": clean_text(item[6]),
        })

    print("[4/5] Extrayendo información detallada y verificada de cada empresa ('ConsultarSolicitud')...")

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
                fecha_solicitud = clean_text(d[11]) if len(d) > 11 else ""
                fecha_cierre = clean_text(d[12]) if len(d) > 12 else sol_info["fecha_cierre_resumen"]
                estado = clean_text(d[13]) if len(d) > 13 else "Requerido"
                
                # Competitiveness index: aplicados / vacantes
                ratio_competitividad = round(aplicados / vacantes, 2) if vacantes > 0 else float(aplicados)

                # Extract technologies and modality
                combined_desc = f"{perfil} {funciones}"
                tecnologias = extract_tags(combined_desc)
                modalidad = extract_modality(combined_desc)

                # Opportunity Rating
                if aplicados == 0:
                    score = min(100, 90 + vacantes * 2)
                elif ratio_competitividad <= 1:
                    score = 85
                elif ratio_competitividad <= 2:
                    score = 75
                elif ratio_competitividad <= 4:
                    score = 60
                elif ratio_competitividad <= 8:
                    score = 40
                else:
                    score = max(10, 30 - int(ratio_competitividad))

                return {
                    "solicitud_id": s_id,
                    "empresa": empresa.upper(),
                    "nit": nit,
                    "departamento": dpto,
                    "ciudad": ciudad,
                    "direccion": direccion,
                    "telefono": telefono,
                    "contacto": contacto,
                    "email": email,
                    "vacantes": vacantes,
                    "postulados": aplicados,
                    "competencia_ratio": ratio_competitividad,
                    "score_oportunidad": score,
                    "modalidad": modalidad,
                    "tecnologias": tecnologias,
                    "tecnologias_str": ", ".join(tecnologias),
                    "fecha_creacion": fecha_creacion,
                    "fecha_solicitud": fecha_solicitud,
                    "fecha_cierre": fecha_cierre,
                    "estado": estado,
                    "perfil_requerido": perfil,
                    "funciones": funciones,
                    "programa_especialidad": clean_text(d[0]) if len(d) > 0 else programa_nombre,
                }
        except Exception as e:
            print(f"Error extrayendo solicitud {s_id}: {e}")
            return None

    # ThreadPoolExecutor for fast scraping
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_detail, sol): sol for sol in solicitudes_resumen}
        count = 0
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                detalles_completos.append(res)
            count += 1
            if count % 35 == 0 or count == total:
                print(f"  -> Progreso: {count}/{total} solicitudes extraídas y verificadas...")

    # Sort by Opportunity Score (Highest first) and fewest applicants per vacancy
    detalles_completos.sort(key=lambda x: (-x["score_oportunidad"], x["competencia_ratio"], -(x["vacantes"] or 0)))

    print(f"\n[5/5] Exportando {len(detalles_completos)} registros verificados a JSON, Excel y CSV...")

    output_dir = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. JSON
    json_path = os.path.join(output_dir, "empresas_caprendizaje_completo.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(detalles_completos, f, indent=2, ensure_ascii=False)
    print(f"[OK] Guardado JSON: {json_path}")

    # 2. DataFrame & Excel
    df = pd.DataFrame(detalles_completos)
    
    col_order = [
        "empresa", "departamento", "ciudad", "vacantes", "postulados", "competencia_ratio",
        "score_oportunidad", "modalidad", "tecnologias_str", "contacto", "email", "telefono",
        "direccion", "nit", "solicitud_id", "fecha_creacion", "fecha_cierre", "estado",
        "perfil_requerido", "funciones", "programa_especialidad"
    ]
    df_excel = df[[c for c in col_order if c in df.columns]]
    
    excel_path = os.path.join(output_dir, "empresas_caprendizaje_completo.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_excel.to_excel(writer, sheet_name="Empresas y Ofertas ADSO", index=False)
        worksheet = writer.sheets["Empresas y Ofertas ADSO"]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)

    print(f"[OK] Guardado Excel: {excel_path}")

    # 3. CSV
    csv_path = os.path.join(output_dir, "empresas_caprendizaje_completo.csv")
    df_excel.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Guardado CSV: {csv_path}")

    print("\n[OK] Extracción y verificación completada exitosamente!")
    return detalles_completos

if __name__ == "__main__":
    fetch_all_data()
