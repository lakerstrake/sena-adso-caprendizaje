# -*- coding: utf-8 -*-
"""Verifica cada NIT del dataset contra el RUES publicado en datos.gov.co.

Devuelve, para cada empresa, si sigue activa en el registro mercantil y cual es
su actividad economica realmente declarada (CIIU), que es lo que decide si el
puesto tiene sentido para un ingeniero industrial.
"""
import json, sys, time, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"c:/Users/USER PC/.gemini/antigravity-ide/scratch/sena_caprendizaje/output"
API = "https://www.datos.gov.co/resource/c82u-588k.json"
SALIDA = r"C:/Users/USERPC~1/AppData/Local/Temp/claude/c--Users-USER-PC--gemini-antigravity-ide-scratch-sena-caprendizaje-output/e4b91793-dfe8-4c57-aa6a-efba368ac512/scratchpad/rues.json"

d = json.load(open(BASE + "/assets/data/empresas.json", encoding="utf-8"))
nits = sorted({str(x.get("nit", "")).strip() for x in d if str(x.get("nit", "")).strip().isdigit()})
print(f"NIT a consultar: {len(nits)}")


def consultar(lote):
    lista = ",".join(f"'{n}'" for n in lote)
    params = {
        "$where": f"numero_identificacion in ({lista})",
        "$select": "numero_identificacion,razon_social,estado_matricula,"
                   "cod_ciiu_act_econ_pri,camara_comercio,fecha_matricula,organizacion_juridica",
        "$limit": "2000",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for intento in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  reintento {intento+1}: {str(e)[:70]}")
            time.sleep(3)
    return []


registros = []
LOTE = 40
for i in range(0, len(nits), LOTE):
    lote = nits[i:i + LOTE]
    filas = consultar(lote)
    registros.extend(filas)
    print(f"  lote {i//LOTE + 1}/{(len(nits)+LOTE-1)//LOTE}: {len(filas)} filas")
    time.sleep(0.4)

# Un mismo NIT aparece varias veces (traslados de domicilio, cancelaciones).
# Se conserva la matricula vigente mas reciente.
mejor = {}
ACTIVOS = ("ACTIVA", "MATRÍCULA NUEVA", "RENOVADA")
for r in registros:
    nit = r["numero_identificacion"]
    estado = (r.get("estado_matricula") or "").upper()
    vigente = any(estado.startswith(a) for a in ACTIVOS)
    actual = mejor.get(nit)
    puntos = (2 if vigente else 0, r.get("fecha_matricula") or "")
    if not actual or puntos > actual["_puntos"]:
        mejor[nit] = {**r, "_vigente": vigente, "_puntos": puntos}

for v in mejor.values():
    v.pop("_puntos", None)

json.dump(mejor, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
encontrados = len(mejor)
vigentes = sum(1 for v in mejor.values() if v["_vigente"])
con_ciiu = sum(1 for v in mejor.values() if v.get("cod_ciiu_act_econ_pri"))
print(f"\nNIT encontrados en el registro: {encontrados} de {len(nits)}")
print(f"  con matricula vigente: {vigentes}")
print(f"  con actividad CIIU declarada: {con_ciiu}")
