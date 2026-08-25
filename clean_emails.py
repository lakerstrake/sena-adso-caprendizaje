import json
import re

def extract_valid_email(raw_email):
    if not raw_email:
        return ""
    # Remove 'imagen de perfil' variations
    cleaned = re.sub(r'(?i)imagen\s*de\s*perfil.*', '', raw_email).strip()
    cleaned = re.sub(r'(?i)imagen.*', '', cleaned).strip()
    # Search for email pattern
    match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', cleaned)
    if match:
        email = match.group(1).lower().rstrip('.')
        # Clean trailing non-domain words
        email = re.sub(r'(com|co|org|net|edu|la|es|io|gov|mil)(imagen|de|perfil).*$', r'\1', email)
        return email
    return cleaned

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    orig = item.get("email", "")
    val = extract_valid_email(orig)
    if orig != val:
        print(f"{item.get('empresa')}: '{orig}' -> '{val}'")
    item["email"] = val

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

import pandas as pd
df = pd.DataFrame(data)
df.to_csv(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.csv", index=False, encoding="utf-8-sig")
df.to_excel(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.xlsx", index=False)
print("Done verified email cleaning!")
