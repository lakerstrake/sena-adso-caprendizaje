import json
import re

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total registros: {len(data)}")

email_issues = []
phone_issues = []
nit_issues = []
city_issues = []
text_issues = []

for idx, item in enumerate(data):
    emp = item.get("empresa", "")
    email = item.get("email", "")
    tel = item.get("telefono", "")
    nit = item.get("nit", "")
    city = item.get("ciudad", "")
    dpto = item.get("departamento", "")
    
    # Check email
    if email:
        if " " in email or "imagen" in email.lower() or "perfil" in email.lower() or "\n" in email:
            email_issues.append((idx, emp, email))
            
    # Check phone
    if tel:
        if len(tel) > 30 or "imagen" in tel.lower() or "\n" in tel:
            phone_issues.append((idx, emp, tel))
            
    # Check city/dpto
    if not city or not dpto:
        city_issues.append((idx, emp, city, dpto))

print(f"\n--- PROBLEMAS EN EMAILS ({len(email_issues)}) ---")
for idx, emp, em in email_issues[:20]:
    print(f"#{idx} {emp}: '{em}'")

print(f"\n--- PROBLEMAS EN TELÉFONOS ({len(phone_issues)}) ---")
for idx, emp, ph in phone_issues[:20]:
    print(f"#{idx} {emp}: '{ph}'")

print(f"\n--- PROBLEMAS EN CIUDAD/DPTO ({len(city_issues)}) ---")
for idx, emp, c, d in city_issues[:20]:
    print(f"#{idx} {emp}: Ciudad='{c}', Dpto='{d}'")
