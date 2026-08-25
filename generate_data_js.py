import json
import os

json_path = r"output/empresas_caprendizaje_completo.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False)

os.makedirs(r"output/assets/js", exist_ok=True)
os.makedirs(r"output/assets/data", exist_ok=True)

# Write assets/js/data.js
js_content = f"""/**
 * SGVA SENA ADSO - Dataset Module
 * Synchronized with official SENA Caprendizaje registry
 */
window.RAW_DATA = {json_str};
"""

with open(r"output/assets/js/data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

# Write assets/data/empresas.json
with open(r"output/assets/data/empresas.json", "w", encoding="utf-8") as f:
    f.write(json_str)

print("Generated output/assets/js/data.js and output/assets/data/empresas.json successfully!")
