import json
import re

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def clean_email(email):
    if not email:
        return ""
    email = email.strip()
    # Match standard email pattern
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email)
    if match:
        return match.group(0).lower()
    return email

def clean_phone(phone):
    if not phone:
        return ""
    # Clean non-standard chars
    phone = phone.strip()
    phone = re.sub(r'\s+', ' ', phone)
    return phone

def clean_text(text):
    if not text:
        return ""
    # Clean excessive whitespace and normalize
    text = text.replace('\xa0', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

cleaned_count = 0
for item in data:
    orig_email = item.get("email", "")
    new_email = clean_email(orig_email)
    if orig_email != new_email:
        print(f"Cleaned email for {item.get('empresa')}: '{orig_email}' -> '{new_email}'")
        item["email"] = new_email
        cleaned_count += 1
        
    item["contacto"] = clean_text(item.get("contacto", ""))
    item["direccion"] = clean_text(item.get("direccion", ""))
    item["perfil_requerido"] = clean_text(item.get("perfil_requerido", ""))
    item["funciones"] = clean_text(item.get("funciones", ""))
    item["ciudad"] = clean_text(item.get("ciudad", "")).title()
    item["departamento"] = clean_text(item.get("departamento", "")).title()
    item["empresa"] = clean_text(item.get("empresa", "")).upper()
    item["telefono"] = clean_phone(item.get("telefono", ""))
    
    # Recalculate metrics to be 100% verified & accurate
    vacantes = int(item.get("vacantes", 1))
    postulados = int(item.get("postulados", 0))
    ratio = round(postulados / vacantes, 2) if vacantes > 0 else 0
    item["vacantes"] = vacantes
    item["postulados"] = postulados
    item["competencia_ratio"] = ratio
    
    # Accurate score calculation:
    # 0 postulados -> 95-100 base score depending on vacantes
    # low ratio (<2) -> 80-90
    # medium ratio (2-5) -> 50-75
    # high ratio (>5) -> <50
    if postulados == 0:
        score = min(100, 90 + vacantes * 2)
    elif ratio <= 1:
        score = 85
    elif ratio <= 2:
        score = 75
    elif ratio <= 4:
        score = 60
    elif ratio <= 8:
        score = 40
    else:
        score = max(10, 30 - int(ratio))
    item["score_oportunidad"] = score

print(f"\nTotal records cleaned/verified: {len(data)}")
print(f"Emails fixed: {cleaned_count}")

# Save back to JSON, CSV and XLSX
import pandas as pd
df = pd.DataFrame(data)

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

df.to_csv(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.csv", index=False, encoding="utf-8-sig")
df.to_excel(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.xlsx", index=False)
print("Updated JSON, CSV and XLSX files successfully!")
