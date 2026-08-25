import requests
from inspect_aplicar import get_session
import json

session = get_session()

print("1. Querying AprendizConsultarAcademicos...")
r_acad = session.get("https://caprendizaje.sena.edu.co/sgva/AprendizAcademico/AprendizConsultarAcademicos")
print("Status:", r_acad.status_code)
acad_data = r_acad.json()
print("Academic data:")
print(json.dumps(acad_data, indent=2, ensure_ascii=False))

# Extract apprentice parameters
last_acad = acad_data["aaData"][-1]
especialidad_id = last_acad[7]
dpto_id = last_acad[2]
ciudad_id = last_acad[4]

print(f"\nApprentice info:")
print(f"Especialidad ID: {especialidad_id} ({last_acad[8] if len(last_acad)>8 else ''})")
print(f"Dpto: {dpto_id}, Ciudad: {ciudad_id}")

print("\n2. Querying AprendizConsultarSolicitudesRequeridas for this especialidad (all dpto=0, ciudad=0)...")
# Let's test with dpto=0 (national) and with user's dpto
params_all = {
    "especialidad": especialidad_id,
    "dpto": 0,
    "ciudad": "0",
    "RSocial": ""
}
r_sol_all = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params=params_all)
print("Status all:", r_sol_all.status_code)
sol_all_data = r_sol_all.json()
total_sol_all = len(sol_all_data.get("aaData", []))
print(f"Total requests found (national): {total_sol_all}")

# If national returns 0 or needs specific dpto, let's test with apprentice dpto
params_user_dpto = {
    "especialidad": especialidad_id,
    "dpto": dpto_id,
    "ciudad": "0",
    "RSocial": ""
}
r_sol_dpto = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/AprendizConsultarSolicitudesRequeridas", params=params_user_dpto)
sol_dpto_data = r_sol_dpto.json()
total_sol_dpto = len(sol_dpto_data.get("aaData", []))
print(f"Total requests found (user dpto {dpto_id}): {total_sol_dpto}")

# Let's inspect first 3 offers in sol_all_data or sol_dpto_data
offers = sol_all_data.get("aaData", []) or sol_dpto_data.get("aaData", [])
if offers:
    print("\nSample offer #0 raw:")
    print(offers[0])

    # Extract solicitud ID from the HTML in offers[0][0]
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(offers[0][0], "html.parser")
    btn = soup.find(attrs={"data-id-solicitud": True})
    sol_id = btn["data-id-solicitud"] if btn else None
    print(f"Extracted Solicitud ID: {sol_id}")

    if sol_id:
        print(f"\n3. Querying detail for Solicitud ID {sol_id}...")
        r_det = session.get("https://caprendizaje.sena.edu.co/sgva/Solicitudes/ConsultarSolicitud", params={"solicitudID": sol_id})
        det_data = r_det.json()
        print("Detail raw response:")
        print(json.dumps(det_data, indent=2, ensure_ascii=False))
