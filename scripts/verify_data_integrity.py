import json

with open(r"c:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\empresas_caprendizaje_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

zero_postulados = [x for x in data if x.get("postulados") == 0]
print(f"Total registros: {len(data)}")
print(f"Total empresas unicas: {len(set(x['empresa'] for x in data))}")
print(f"Total vacantes: {sum(x['vacantes'] for x in data)}")
print(f"Total postulaciones: {sum(x['postulados'] for x in data)}")
print(f"Total con 0 postulados: {len(zero_postulados)}")

for idx, z in enumerate(zero_postulados):
    print(f"  #{idx+1}: {z['empresa']} - {z['ciudad']}, {z['departamento']} - Vacantes: {z['vacantes']} - Cierre: {z['fecha_cierre']}")

# Verify all fields are present and valid
missing_fields = []
for idx, d in enumerate(data):
    for field in ["empresa", "departamento", "ciudad", "vacantes", "postulados", "solicitud_id", "fecha_cierre"]:
        if d.get(field) is None or str(d.get(field)).strip() == "":
            missing_fields.append((idx, d.get("empresa"), field))

print(f"\nMissing critical fields: {len(missing_fields)}")
if missing_fields:
    for m in missing_fields:
        print("  Missing:", m)
