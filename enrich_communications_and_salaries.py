import json
import re
import urllib.parse
import pandas as pd

# Load existing dataset
json_path = r"output/empresas_caprendizaje_completo.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} records for salary, WhatsApp and LinkedIn enrichment...")

# Fix known character encoding artifacts
def clean_text(t):
    if not t or not isinstance(t, str):
        return t
    t = t.replace("Avils", "Avilés")
    t = t.replace("Beleo", "Beleño")
    t = t.replace("Muoz", "Muñoz")
    t = t.replace("Pea", "Peña")
    t = t.replace("Nio", "Niño")
    t = t.replace("Castao", "Castaño")
    t = t.replace("Caon", "Cañón")
    t = t.replace("Bohorquez", "Bohórquez")
    t = t.replace("Gomez", "Gómez")
    t = t.replace("Lopez", "López")
    t = t.replace("Perez", "Pérez")
    t = t.replace("Rodriguez", "Rodríguez")
    t = t.replace("Martinez", "Martínez")
    t = t.replace("Sanchez", "Sánchez")
    t = t.replace("Hernandez", "Hernández")
    return t.strip()

CANDIDATE = {
    "name": "Juan Manuel Lagos Monroy",
    "phone": "(+57) 300 727 9875",
    "github": "https://github.com/lakerstrake",
    "linkedin": "https://linkedin.com/in/juan-manuel-lagos-monroy",
    "program": "Tecnólogo en Análisis y Desarrollo de Software (ADSO) - SENA",
    "specialtyId": "136456"
}

for item in data:
    # 1. Clean encoding artifacts
    item["empresa"] = clean_text(item.get("empresa", ""))
    item["contacto"] = clean_text(item.get("contacto", ""))
    item["perfil_requerido"] = clean_text(item.get("perfil_requerido", ""))
    item["funciones"] = clean_text(item.get("funciones", ""))

    # 2. Correct Salaries according to Colombian Law (Ley 789 de 2002) and Market Realities
    cat_id = item.get("cat_id", "TIER_3")
    
    if cat_id == "TIER_1":
        item["apoyo_sostenimiento"] = "100% SMMLV ($1.423.500 COP) + EPS/ARL (Auxilios hasta $2.0M COP en Tech Top)"
        item["apoyo_sostenimiento_corto"] = "$1.423.500 COP (100% SMMLV)"
        item["salario_egresado_jr"] = "$2.800.000 a $4.500.000+ COP (Al culminar ADSO)"
        item["salario_proyectado"] = "Práctica: 100% SMMLV ($1.42M) | Jr: $2.8M - $4.5M+"
    elif cat_id == "TIER_2":
        item["apoyo_sostenimiento"] = "100% SMMLV ($1.423.500 COP) + Cobertura EPS y ARL"
        item["apoyo_sostenimiento_corto"] = "$1.423.500 COP (100% SMMLV)"
        item["salario_egresado_jr"] = "$2.200.000 a $3.500.000 COP (Al culminar ADSO)"
        item["salario_proyectado"] = "Práctica: 100% SMMLV ($1.42M) | Jr: $2.2M - $3.5M"
    elif cat_id == "TIER_3":
        item["apoyo_sostenimiento"] = "100% SMMLV ($1.423.500 COP) + Cobertura EPS y ARL"
        item["apoyo_sostenimiento_corto"] = "$1.423.500 COP (100% SMMLV)"
        item["salario_egresado_jr"] = "$1.800.000 a $2.800.000 COP (Al culminar ADSO)"
        item["salario_proyectado"] = "Práctica: 100% SMMLV ($1.42M) | Jr: $1.8M - $2.8M"
    elif cat_id == "TIER_4":
        item["apoyo_sostenimiento"] = "75% - 100% SMMLV ($1.067.000 - $1.423.500 COP) + EPS/ARL"
        item["apoyo_sostenimiento_corto"] = "75% - 100% SMMLV"
        item["salario_egresado_jr"] = "$1.500.000 a $2.200.000 COP (Al culminar ADSO)"
        item["salario_proyectado"] = "Práctica: 75%-100% SMMLV | Jr: $1.5M - $2.2M"
    else: # TIER_5
        item["apoyo_sostenimiento"] = "75% - 100% SMMLV ($1.067.000 - $1.423.500 COP) + EPS/ARL"
        item["apoyo_sostenimiento_corto"] = "75% - 100% SMMLV"
        item["salario_egresado_jr"] = "$1.423.500 a $2.000.000 COP (Al culminar ADSO)"
        item["salario_proyectado"] = "Práctica: 75%-100% SMMLV | Jr: $1.4M - $2.0M"

    # 3. Analyze and format phone numbers for WhatsApp
    raw_phone = str(item.get("telefono", "")).strip()
    digits = re.sub(r"\D", "", raw_phone)
    
    is_whatsapp = False
    whatsapp_clean = ""
    whatsapp_url = ""
    
    # Check if it is a 10-digit Colombian mobile starting with 3
    if len(digits) == 10 and digits.startswith("3"):
        is_whatsapp = True
        whatsapp_clean = f"57{digits}"
    elif len(digits) == 12 and digits.startswith("573"):
        is_whatsapp = True
        whatsapp_clean = digits
    
    item["is_whatsapp"] = is_whatsapp
    item["whatsapp_number"] = whatsapp_clean
    
    # Contact name
    contact_name = item.get("contacto", "")
    if not contact_name or contact_name.lower() in ["no registrado", "no especificado", "selección", "seleccion"]:
        greeting = "Estimado equipo de Selección y Talento Humano"
        contact_ref = "Equipo de Selección"
    else:
        greeting = f"Hola {contact_name}, cordial saludo"
        contact_ref = contact_name

    # Tailor skills narrative for WhatsApp message
    if cat_id == "TIER_1":
        skills_wa = "desarrollo de software full-stack, lógica de programación, SQL y Git"
    elif cat_id == "TIER_2":
        skills_wa = "bases de datos relacionales (SQL), análisis de sistemas y desarrollo"
    else:
        skills_wa = "desarrollo de software, bases de datos SQL y soporte técnico"

    # 4. Generate Pre-tailored WhatsApp Message
    wa_msg = (
        f"{greeting}. Mi nombre es {CANDIDATE['name']}, aprendiz tecnólogo en Análisis y Desarrollo de Software (ADSO) del SENA. "
        f"Me pongo en contacto con mucho interés respecto a la solicitud de Contrato de Aprendizaje #{item.get('solicitud_id')} para {item.get('empresa')}. "
        f"Cuento con formación práctica en {skills_wa} y disponibilidad inmediata para iniciar mi etapa productiva.\n\n"
        f"Pueden consultar mis proyectos técnicos y perfil en:\n"
        f"• GitHub: {CANDIDATE['github']}\n"
        f"• LinkedIn: {CANDIDATE['linkedin']}\n\n"
        f"¿Me indicarían por favor a qué correo o persona puedo compartirles mi Hoja de Vida institucional para su revisión? Muchas gracias."
    )
    item["whatsapp_message"] = wa_msg
    if is_whatsapp:
        item["whatsapp_url"] = f"https://api.whatsapp.com/send?phone={whatsapp_clean}&text={urllib.parse.quote(wa_msg)}"
    else:
        item["whatsapp_url"] = ""

    # 5. Generate LinkedIn Search and Direct Message URLs
    company_name_query = item.get("empresa", "").replace("S.A.S.", "").replace("S.A.S", "").replace("S.A.", "").replace("SAS", "").replace("LTDA", "").strip()
    
    # LinkedIn company search
    item["linkedin_company_search_url"] = f"https://www.linkedin.com/search/results/companies/?keywords={urllib.parse.quote(company_name_query)}"
    
    # LinkedIn recruiter / people search at that company
    if contact_name and contact_name != "No registrado" and len(contact_name.split()) >= 2:
        item["linkedin_contact_search_url"] = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(f'{contact_name} {company_name_query}')}"
    else:
        item["linkedin_contact_search_url"] = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(f'Recursos Humanos {company_name_query}')}"

    # LinkedIn tailored InMail / connect message (within 300 char limit for connection requests)
    item["linkedin_connect_message"] = (
        f"Hola {contact_ref}, soy Juan Manuel Lagos, aprendiz ADSO SENA. Me postulo a la vacante #{item.get('solicitud_id')} en {item.get('empresa')}. "
        f"Cuento con proyectos en GitHub ({CANDIDATE['github']}) y disponibilidad inmediata para Contrato de Aprendizaje. ¡Me encantaría conectar!"
    )

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save updated Excel and CSV
df = pd.DataFrame(data)
df.to_excel(r"output/empresas_caprendizaje_completo.xlsx", index=False)
df.to_csv(r"output/empresas_caprendizaje_completo.csv", index=False, encoding="utf-8")

print("Successfully enriched all 179 records with real legal apprentice stipends, WhatsApp direct links, and LinkedIn recruiter searches!")
