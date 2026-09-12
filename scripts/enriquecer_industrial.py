# -*- coding: utf-8 -*-
"""Añade al dataset la verificación del registro mercantil y la relevancia
para ingeniería industrial, derivada de la actividad económica real (CIIU).
"""
import json, sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r"c:/Users/USER PC/.gemini/antigravity-ide/scratch/sena_caprendizaje/output"
SCR = r"C:/Users/USERPC~1/AppData/Local/Temp/claude/c--Users-USER-PC--gemini-antigravity-ide-scratch-sena-caprendizaje-output/e4b91793-dfe8-4c57-aa6a-efba368ac512/scratchpad"

# Descripción oficial CIIU Rev. 4 A.C. de los códigos presentes en el registro.
CIIU = {
    "0125": "Cultivo de flores de corte", "0141": "Cría de ganado bovino y bufalino",
    "0145": "Cría de ovejas y cabras", "0161": "Apoyo a la agricultura",
    "0610": "Extracción de petróleo crudo",
    "1011": "Procesamiento y conservación de carne", "1020": "Procesamiento de pescado y mariscos",
    "1031": "Elaboración de aceites y grasas", "1311": "Preparación e hilatura de fibras textiles",
    "1410": "Confección de prendas de vestir", "1513": "Fabricación de artículos de viaje y marroquinería",
    "2013": "Fabricación de plásticos en formas primarias", "2022": "Fabricación de pinturas y barnices",
    "2100": "Fabricación de productos farmacéuticos", "2221": "Fabricación de formas primarias de plástico",
    "2229": "Fabricación de artículos de plástico", "2394": "Fabricación de cemento, cal y yeso",
    "2592": "Tratamiento y revestimiento de metales", "2712": "Fabricación de aparatos de distribución eléctrica",
    "3313": "Mantenimiento y reparación de equipo electrónico y óptico",
    "3514": "Comercialización de energía eléctrica", "3600": "Captación y distribución de agua",
    "4290": "Construcción de otras obras de ingeniería civil",
    "4620": "Comercio al por mayor de materias primas agropecuarias",
    "4631": "Comercio al por mayor de productos alimenticios", "4645": "Comercio al por mayor de productos farmacéuticos",
    "4651": "Comercio al por mayor de computadores y equipo", "4652": "Comercio al por mayor de equipo electrónico",
    "4659": "Comercio al por mayor de maquinaria y equipo", "4661": "Comercio al por mayor de combustibles",
    "4663": "Comercio al por mayor de materiales de construcción", "4664": "Comercio al por mayor de productos químicos",
    "4665": "Comercio al por mayor de desperdicios y chatarra", "4711": "Comercio al por menor en establecimientos no especializados",
    "4723": "Comercio al por menor de bebidas y tabaco", "4741": "Comercio al por menor de computadores",
    "4752": "Comercio al por menor de artículos de ferretería", "4759": "Comercio al por menor de electrodomésticos",
    "4771": "Comercio al por menor de prendas de vestir", "4773": "Comercio al por menor de productos farmacéuticos",
    "4774": "Comercio al por menor de artículos de segunda mano",
    "4921": "Transporte de pasajeros", "4923": "Transporte de carga por carretera",
    "5224": "Manipulación de carga", "5229": "Actividades complementarias al transporte",
    "5511": "Alojamiento en hoteles", "5813": "Edición de periódicos y revistas",
    "5820": "Edición de programas de informática", "6110": "Telecomunicaciones alámbricas",
    "6190": "Otras telecomunicaciones", "6201": "Desarrollo de sistemas informáticos",
    "6202": "Consultoría informática", "6209": "Otras actividades de tecnologías de información",
    "6311": "Procesamiento de datos y hosting", "6412": "Bancos comerciales",
    "6492": "Actividades financieras de fondos", "6499": "Otras actividades de servicio financiero",
    "6619": "Otras actividades auxiliares de servicios financieros",
    "6810": "Actividades inmobiliarias con bienes propios", "6820": "Actividades inmobiliarias a cambio de retribución",
    "6910": "Actividades jurídicas", "6920": "Contabilidad y auditoría",
    "7010": "Actividades de administración empresarial", "7020": "Consultoría de gestión",
    "7112": "Actividades de ingeniería y consultoría técnica", "7220": "Investigación y desarrollo",
    "7310": "Publicidad", "7490": "Otras actividades profesionales y técnicas",
    "7730": "Alquiler de maquinaria y equipo", "7911": "Actividades de agencias de viaje",
    "8010": "Actividades de seguridad privada", "8220": "Centros de llamadas (contact center)",
    "8291": "Agencias de cobranza y bureaus de crédito", "8299": "Otros servicios de apoyo a empresas",
    "8544": "Educación superior", "8621": "Actividades de medicina general",
    "8699": "Otras actividades de atención de la salud", "8899": "Otras actividades de asistencia social",
    "9101": "Bibliotecas y archivos", "9200": "Juegos de azar y apuestas",
    "9312": "Actividades de clubes deportivos", "9499": "Otras asociaciones",
}

# Sección CIIU (letra oficial) a partir de la división, y peso para el perfil
# de ingeniería industrial: procesos, producción, logística y calidad.
SECCIONES = [
    (1, 3, "Agroindustria", 86), (5, 9, "Minería y Petróleo", 90),
    (10, 33, "Manufactura", 100), (35, 35, "Energía", 90),
    (36, 39, "Agua y Saneamiento", 84), (41, 43, "Construcción", 88),
    (45, 47, "Comercio y Distribución", 74), (49, 53, "Transporte y Logística", 95),
    (55, 56, "Hotelería y Alimentos", 58), (58, 63, "Tecnología", 45),
    (64, 66, "Financiero", 52), (68, 68, "Inmobiliario", 46),
    (69, 75, "Consultoría e Ingeniería", 70), (77, 82, "Servicios a Empresas", 66),
    (84, 84, "Sector Público", 60), (85, 85, "Educación", 48),
    (86, 88, "Salud", 62), (90, 93, "Entretenimiento", 42),
    (94, 96, "Otros Servicios", 44),
]

# Competencias que cada sector demanda de un ingeniero industrial. Se usan para
# redactar la carta con argumentos propios del sector, no genéricos.
COMPETENCIAS = {
    "Manufactura": ("optimización de líneas de producción, balanceo de cargas y reducción de desperdicio",
                    "Lean Manufacturing, estudio de tiempos y movimientos, OEE y control estadístico de procesos"),
    "Transporte y Logística": ("planeación de la cadena de abastecimiento, gestión de inventarios y diseño de rutas",
                               "modelos de inventario, S&OP, indicadores de nivel de servicio y costeo logístico"),
    "Agroindustria": ("estandarización de procesos productivos y trazabilidad",
                      "BPM, HACCP, control de calidad y planeación de cosecha y producción"),
    "Minería y Petróleo": ("confiabilidad de activos, productividad y seguridad operacional",
                           "mantenimiento centrado en confiabilidad, gestión de riesgos y SG-SST"),
    "Energía": ("eficiencia operativa y gestión de activos",
                "indicadores de disponibilidad, mantenimiento preventivo y análisis de causa raíz"),
    "Agua y Saneamiento": ("eficiencia de procesos y control operativo",
                           "gestión de indicadores, mejora continua y normatividad ambiental"),
    "Construcción": ("programación de obra, control de presupuesto y productividad en campo",
                     "ruta crítica, curvas S, control de costos y SG-SST"),
    "Comercio y Distribución": ("gestión de inventarios, planeación de la demanda y eficiencia en distribución",
                                "pronósticos de demanda, rotación de inventario, layout de bodega y costeo"),
    "Consultoría e Ingeniería": ("levantamiento y rediseño de procesos y formulación de proyectos",
                                 "mapeo de procesos BPMN, análisis de datos y evaluación financiera de proyectos"),
    "Servicios a Empresas": ("diseño de procesos, productividad del personal e indicadores de servicio",
                             "estudio de métodos, dimensionamiento de capacidad y tableros de control"),
    "Salud": ("mejora de procesos asistenciales y administrativos",
              "gestión por procesos, habilitación, indicadores de oportunidad y mejora continua"),
    "Financiero": ("eficiencia operativa y automatización de procesos",
                   "mapeo de procesos, control interno y análisis de datos"),
    "Sector Público": ("gestión por procesos e indicadores de desempeño",
                       "MIPG, formulación de proyectos e indicadores de gestión"),
}
GENERICA = ("mejora de procesos, productividad e indicadores de gestión",
            "gestión por procesos, análisis de datos, control de calidad y SG-SST")


def seccion_de(ciiu):
    try:
        div = int(str(ciiu)[:2])
    except (TypeError, ValueError):
        return "Sin clasificar", 40
    for lo, hi, nombre, peso in SECCIONES:
        if lo <= div <= hi:
            return nombre, peso
    return "Sin clasificar", 40


def main():
    datos = json.load(open(BASE + "/assets/data/empresas.json", encoding="utf-8"))
    rues = json.load(open(SCR + "/rues.json", encoding="utf-8"))

    verificadas = 0
    for row in datos:
        nit = str(row.get("nit", "")).strip()
        reg = rues.get(nit)
        if not reg:
            row["rues_verificado"] = False
            row["ind_sector"] = "Sin verificar"
            row["ind_score"] = 35
            row["ind_actividad"] = ""
            continue

        verificadas += 1
        ciiu = reg.get("cod_ciiu_act_econ_pri") or ""
        sector, peso = seccion_de(ciiu)

        row["rues_verificado"] = True
        row["rues_razon_social"] = reg.get("razon_social", "")
        row["rues_estado"] = reg.get("estado_matricula", "")
        row["rues_camara"] = reg.get("camara_comercio", "")
        row["rues_ciiu"] = ciiu
        row["ind_actividad"] = CIIU.get(ciiu, f"Actividad CIIU {ciiu}")
        row["ind_sector"] = sector

        # Vacantes y competencia son señales reales de demanda: suman al peso
        # del sector para ordenar a quién escribir primero.
        vac = row.get("vacantes") or 0
        post = row.get("postulados") or 0
        bono = min(10, vac * 2) + (6 if post == 0 else 3 if post <= 2 else 0)
        row["ind_score"] = min(100, peso + bono)

        enfoque, herramientas = COMPETENCIAS.get(sector, GENERICA)
        row["ind_enfoque"] = enfoque
        row["ind_herramientas"] = herramientas

    json.dump(datos, open(BASE + "/assets/data/empresas.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    import collections
    c = collections.Counter(r["ind_sector"] for r in datos)
    print(f"verificadas en el registro mercantil: {verificadas} de {len(datos)}")
    print(f"{'SECTOR':28} {'EMPRESAS':>9}")
    for s, n in c.most_common():
        print(f"{s:28} {n:9}")


if __name__ == "__main__":
    main()
