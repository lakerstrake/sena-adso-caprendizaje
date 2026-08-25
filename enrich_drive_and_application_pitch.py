import json
import pandas as pd
import urllib.parse

json_path = r"output/empresas_caprendizaje_completo.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Updating {len(data)} records: removing specialty codes & raw application IDs, adding CV link and email jmlagos2003@gmail.com...")

CANDIDATE_NAME = "Juan Manuel Lagos Monroy"
CANDIDATE_PHONE = "(+57) 300 727 9875"
CANDIDATE_EMAIL = "jmlagos2003@gmail.com"
CANDIDATE_GITHUB = "https://github.com/lakerstrake"
CANDIDATE_LINKEDIN = "https://linkedin.com/in/juan-manuel-lagos-monroy"
CANDIDATE_CV_DRIVE = "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN"
CANDIDATE_PROGRAM = "Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA"

for item in data:
    empresa = item.get("empresa", "")
    contacto = item.get("contacto", "")
    cat_id = item.get("cat_id", "TIER_3")
    is_wa = item.get("is_whatsapp", False)
    wa_num = item.get("whatsapp_number", "")
    
    contact_name = contacto if contacto and contacto != "No registrado" else "Equipo de Selección y Gestión Humana"

    if cat_id == "TIER_1":
        skills_pitch = "desarrollo web y software full-stack (JavaScript, React, Java, Spring Boot, APIs REST), bases de datos SQL y despliegue en producción"
    elif cat_id == "TIER_2":
        skills_pitch = "diseño y administración de bases de datos relacionales (SQL), desarrollo de software, reportería y sistemas corporativos"
    elif cat_id == "TIER_3":
        skills_pitch = "soporte técnico especializado de aplicaciones, administración de sistemas, bases de datos SQL y diagnóstico"
    else:
        skills_pitch = "desarrollo de software, bases de datos relacionales (SQL), herramientas ofimáticas avanzadas y soporte técnico"

    # Natural, ultra-professional Formal Email without specialty codes or raw application numbers
    email_body = f"""Asunto: Postulación Contrato de Aprendizaje - Tecnólogo ADSO SENA - {CANDIDATE_NAME}

Estimado/a {contact_name},

Reciba un cordial saludo. Mi nombre es {CANDIDATE_NAME}, aprendiz en etapa productiva del programa {CANDIDATE_PROGRAM}.

Me dirijo a ustedes tras consultar con gran interés la vacante de Contrato de Aprendizaje para {empresa} que vi publicada en la plataforma institucional Caprendizaje. Mi objetivo es vincularme formalmente con su equipo y aportar valor técnico en sus proyectos y operaciones de software.

Cuento con sólida preparación práctica y experiencia en proyectos reales en {skills_pitch}, además de background en siete semestres de Ingeniería Mecatrónica y título como Técnico en Sistemas, con total disponibilidad y dedicación para iniciar mi etapa productiva.

Pongo a su entera disposición mi hoja de vida institucional, portafolio de código y certificaciones técnicas:
• Hoja de Vida (CV) y Certificados: {CANDIDATE_CV_DRIVE}
• Repositorio y Proyectos en GitHub: {CANDIDATE_GITHUB}
• Perfil Profesional en LinkedIn: {CANDIDATE_LINKEDIN}
• Teléfono directo / WhatsApp: {CANDIDATE_PHONE}
• Correo Electrónico: {CANDIDATE_EMAIL}

Agradezco de antemano la oportunidad de participar en su proceso de selección y quedo atento a su respuesta para coordinar una entrevista técnica.

Atentamente,

{CANDIDATE_NAME}
Desarrollador Web Junior · Aprendiz ADSO SENA
{CANDIDATE_PHONE} · {CANDIDATE_EMAIL}"""

    item["correo_formal_completo"] = email_body

    # Natural WhatsApp Message without application ID numbers or specialty codes
    wa_msg = f"""Hola {contact_name}, cordial saludo. Mi nombre es {CANDIDATE_NAME}, aprendiz tecnólogo en Análisis y Desarrollo de Software (ADSO) del SENA.

Me comunico con mucho interés tras revisar la vacante de Contrato de Aprendizaje para {empresa} que vi publicada en Caprendizaje. Cuento con total disponibilidad para iniciar mi etapa productiva y aportar en desarrollo web, software (Java, React, SQL), Git y metodologías ágiles.

Pongo a su disposición mi hoja de vida y proyectos técnicos:
• Hoja de Vida (CV) y Certificados: {CANDIDATE_CV_DRIVE}
• GitHub: {CANDIDATE_GITHUB}
• LinkedIn: {CANDIDATE_LINKEDIN}

¿Me indicarían por favor con quién o a qué correo puedo coordinar una entrevista técnica? Muchas gracias."""

    item["whatsapp_message"] = wa_msg
    if is_wa and wa_num:
        item["whatsapp_url"] = f"https://api.whatsapp.com/send?phone={wa_num}&text={urllib.parse.quote(wa_msg)}"

    # Natural LinkedIn Message
    linkedin_msg = f"Hola {contact_name}, soy Juan Manuel Lagos, aprendiz ADSO SENA. Me postulo a la vacante de Contrato de Aprendizaje en {empresa} que vi en Caprendizaje. Cuento con proyectos en GitHub (github.com/lakerstrake), CV en Drive y disponibilidad inmediata. ¡Me encantaría conectar!"
    item["linkedin_connect_message"] = linkedin_msg

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save updated Excel and CSV
df = pd.DataFrame(data)
df.to_excel(r"output/empresas_caprendizaje_completo.xlsx", index=False)
df.to_csv(r"output/empresas_caprendizaje_completo.csv", index=False, encoding="utf-8")

print("Successfully updated master JSON, Excel, and CSV datasets without specialty codes or IDs, and with CV links!")
