import json
import pandas as pd

json_path = r"output/empresas_caprendizaje_completo.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Enriching {len(data)} records with Career Escalation, Learning Curves, and Quality of Life Projections...")

for item in data:
    cat_id = item.get("cat_id", "TIER_3")
    empresa = item.get("empresa", "").upper()
    
    # Tier 1: Pure Software, Tech Multinational, High Innovation
    if cat_id == "TIER_1":
        item["escalabilidad_score"] = 96
        item["escalabilidad_nivel"] = "Exponencial (Alta Demanda Global)"
        item["curva_aprendizaje_titulo"] = "Desarrollo de Software Full-Stack & Arquitectura Cloud"
        item["curva_aprendizaje_detalle"] = "Dominio de frameworks modernos (React, Angular, Vue, Node.js, Spring Boot, .NET Core), bases de datos relacionales/NoSQL, control de versiones Git avanzado, integración continua (CI/CD) y metodologías ágiles (Scrum/Kanban)."
        item["hitos_carrera"] = [
            {"periodo": "Año 0 (Meses 1-6)", "rol": "Aprendiz ADSO Etapa Productiva", "salario": "$1.423.500 - $2.000.000 COP", "foco": "Inmersión en código real, resolución de bugs, pruebas y buenas prácticas."},
            {"periodo": "Año 1 (Junior)", "rol": "Desarrollador Junior Full-Stack", "salario": "$3.000.000 - $4.800.000 COP", "foco": "Desarrollo autónomo de módulos, APIs RESTful y componentes web."},
            {"periodo": "Año 3 (Semi-Senior)", "rol": "Desarrollador Mid-Level / Cloud Engineer", "salario": "$5.500.000 - $8.500.000 COP", "foco": "Diseño de arquitectura, microservicios, optimización de base de datos y cloud."},
            {"periodo": "Año 5+ (Senior / Remoto)", "rol": "Senior Developer / Tech Lead / Remoto Global", "salario": "$10.000.000 a $22.000.000+ COP ($3.000 - $5.500 USD/mes)", "foco": "Liderazgo técnico, arquitectura distribuida y trabajo para empresas internacionales."}
        ]
        item["impacto_vida_resumen"] = "Máximo: Alta opción de trabajo remoto/híbrido, autonomía horaria, bonos técnicos y libertad geográfica para trabajar internacionalmente."
        item["techo_salarial_5anios"] = "$10M - $22M+ COP ($3.0k - $5.5k USD)"

    # Tier 2: Enterprise Systems, Banking, Large Database ERPs
    elif cat_id == "TIER_2":
        item["escalabilidad_score"] = 88
        item["escalabilidad_nivel"] = "Alta (Sector Corporativo & Financiero)"
        item["curva_aprendizaje_titulo"] = "Bases de Datos Masivas, ERPs & Arquitectura Empresarial"
        item["curva_aprendizaje_detalle"] = "Especialización en SQL avanzado, PL/SQL Oracle, PostgreSQL, integración de sistemas corporativos (SAP, Dynamics), seguridad informática, análisis de datos y procesos transaccionales críticos."
        item["hitos_carrera"] = [
            {"periodo": "Año 0 (Meses 1-6)", "rol": "Aprendiz ADSO Sistemas / Datos", "salario": "$1.423.500 COP + Prestaciones", "foco": "Mapeo de datos, consultas complejas y soporte de procesos de sistemas."},
            {"periodo": "Año 1 (Junior)", "rol": "Analista / Desarrollador SQL & Sistemas", "salario": "$2.500.000 - $3.800.000 COP", "foco": "Automatización de reportes, procedimientos almacenados y flujos ETL."},
            {"periodo": "Año 3 (Semi-Senior)", "rol": "Ingeniero de Datos / Consultor ERP", "salario": "$4.800.000 - $7.200.000 COP", "foco": "Optimización de bases de datos masivas, gobierno de datos y migraciones."},
            {"periodo": "Año 5+ (Senior / Líder)", "rol": "DBA Senior / Data Architect / Líder BI", "salario": "$8.500.000 a $15.000.000 COP", "foco": "Dirección de infraestructura de datos y consultoría estratégica empresarial."}
        ]
        item["impacto_vida_resumen"] = "Muy Alto: Gran estabilidad en sectores bancarios e industriales sólidos, excelentes prestaciones sociales corporativas y convenios empresariales."
        item["techo_salarial_5anios"] = "$8.5M - $15.0M COP"

    # Tier 3: IT Support, Infrastructure & Applications
    elif cat_id == "TIER_3":
        item["escalabilidad_score"] = 72
        item["escalabilidad_nivel"] = "Moderada (Infraestructura, Redes & DevOps)"
        item["curva_aprendizaje_titulo"] = "Administración de Sistemas, Redes & Soporte Especializado"
        item["curva_aprendizaje_detalle"] = "Manejo de servidores Windows/Linux, redes TCP/IP, seguridad perimetral, gestión de incidentes ITIL, soporte a plataformas web y automatización con scripting."
        item["hitos_carrera"] = [
            {"periodo": "Año 0 (Meses 1-6)", "rol": "Aprendiz Soporte TI / Redes", "salario": "$1.423.500 COP + Prestaciones", "foco": "Mantenimiento preventivo, soporte de primer y segundo nivel."},
            {"periodo": "Año 1 (Junior)", "rol": "Administrador de Sistemas Junior", "salario": "$2.000.000 - $2.800.000 COP", "foco": "Gestión de servidores, monitoreo de redes y accesos."},
            {"periodo": "Año 3 (Semi-Senior)", "rol": "Ingeniero de Infraestructura / Cloud Jr", "salario": "$3.800.000 - $5.500.000 COP", "foco": "Virtualización, servidores en la nube y ciberseguridad."},
            {"periodo": "Año 5+ (Senior)", "rol": "SysAdmin Senior / DevOps Engineer", "salario": "$6.500.000 a $11.000.000 COP", "foco": "Automatización de despliegues y gestión de infraestructura crítica."}
        ]
        item["impacto_vida_resumen"] = "Moderado: Trabajo mixto o presencial, turnos de disponibilidad según incidentes, posibilidad de pivotar hacia DevOps y Cloud."
        item["techo_salarial_5anios"] = "$6.5M - $11.0M COP"

    # Tier 4: Hardware Maintenance & General IT
    elif cat_id == "TIER_4":
        item["escalabilidad_score"] = 52
        item["escalabilidad_nivel"] = "Básica (Operaciones & Soporte de Campo)"
        item["curva_aprendizaje_titulo"] = "Mantenimiento Técnico y Ensamble"
        item["curva_aprendizaje_detalle"] = "Ensamble, formateo, configuración de periféricos, mantenimiento físico de equipos y atención presencial a usuarios."
        item["hitos_carrera"] = [
            {"periodo": "Año 0 (Meses 1-6)", "rol": "Aprendiz Soporte Físico", "salario": "75% - 100% SMMLV", "foco": "Mantenimiento de computadores y periféricos."},
            {"periodo": "Año 1 (Junior)", "rol": "Técnico de Mesa de Ayuda", "salario": "$1.500.000 - $2.000.000 COP", "foco": "Tickets de soporte y mantenimiento presencial."},
            {"periodo": "Año 3 (Semi-Senior)", "rol": "Coordinador de Soporte TI", "salario": "$2.500.000 - $3.500.000 COP", "foco": "Gestión de inventarios y proveedores de hardware."},
            {"periodo": "Año 5+ (Senior)", "rol": "Jefe de Soporte Técnico", "salario": "$4.000.000 a $6.000.000 COP", "foco": "Gestión operativa de equipos técnicos."}
        ]
        item["impacto_vida_resumen"] = "Básico: Mayormente presencial, requiere desplazamiento físico constante, menor apalancamiento salarial en software."
        item["techo_salarial_5anios"] = "$4.0M - $6.0M COP"

    # Tier 5: Non-Prioritized / Low Code / High Saturation
    else:
        item["escalabilidad_score"] = 40
        item["escalabilidad_nivel"] = "Baja para Perfil ADSO"
        item["curva_aprendizaje_titulo"] = "Operación Administrativa y Asistencial"
        item["curva_aprendizaje_detalle"] = "Labores de digitación, archivo, atención telefónica y tareas de oficina con mínimo o nulo contacto con desarrollo de software."
        item["hitos_carrera"] = [
            {"periodo": "Año 0 (Meses 1-6)", "rol": "Aprendiz Asistencial", "salario": "75% - 100% SMMLV", "foco": "Tareas operativas y ofimática básica."},
            {"periodo": "Año 1 (Junior)", "rol": "Auxiliar Administrativo", "salario": "$1.423.500 - $1.800.000 COP", "foco": "Manejo de documentos y procesos básicos."},
            {"periodo": "Año 3 (Semi-Senior)", "rol": "Asistente Operativo", "salario": "$2.000.000 - $2.600.000 COP", "foco": "Supervisión de procesos no técnicos."},
            {"periodo": "Año 5+ (Senior)", "rol": "Coordinador Administrativo", "salario": "$3.000.000 a $4.500.000 COP", "foco": "Operación general de oficina."}
        ]
        item["impacto_vida_resumen"] = "Bajo: No fortalece tu portafolio como programador, obligando a estudiar por cuenta propia en las noches para no perder ritmo técnico."
        item["techo_salarial_5anios"] = "$3.0M - $4.5M COP"

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save updated Excel and CSV
df = pd.DataFrame(data)
df.to_excel(r"output/empresas_caprendizaje_completo.xlsx", index=False)
df.to_csv(r"output/empresas_caprendizaje_completo.csv", index=False, encoding="utf-8")

print("Successfully enriched 179 records with comprehensive Career Escalation, 5-Year Salary Milestones, and Quality of Life indices!")
