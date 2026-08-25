import requests
from inspect_aplicar import get_session

session = get_session()

print("Testing especialidad=0 (all specialties if possible)...")
r0 = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params={
    "especialidad": 0,
    "dpto": 0,
    "ciudad": "0",
    "RSocial": ""
})
print("Status (esp=0):", r0.status_code, "Count:", len(r0.json().get("aaData", [])))

print("Testing especialidad=136456 (ADSO)...")
r_adso = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params={
    "especialidad": 136456,
    "dpto": 0,
    "ciudad": "0",
    "RSocial": ""
})
adso_count = len(r_adso.json().get("aaData", []))
print("Status (esp=136456):", r_adso.status_code, "Count:", adso_count)
