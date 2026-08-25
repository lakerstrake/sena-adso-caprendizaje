import requests
from inspect_aplicar import get_session

session = get_session()
r = session.get("https://caprendizaje.sena.edu.co/sgva/bundles/aprendiz_solicitudes?v=-a6gBc_Ewo3bV87o3GbomfAJgOZi0rdoqKtQL2eHzDA1")
print("Bundle status:", r.status_code)
print("Bundle size:", len(r.text))

with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\aprendiz_solicitudes.js", "w", encoding="utf-8") as f:
    f.write(r.text)

print("Saved bundle to output/aprendiz_solicitudes.js")
