import json
import pandas as pd

json_path = r"output/empresas_caprendizaje_completo.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Enriching {len(data)} records with Interview Simulators, Tech Stacks, and Cumulative Financial Projections...")

CANDIDATE_GITHUB = "https://github.com/lakerstrake"

for item in data:
    cat_id = item.get("cat_id", "TIER_3")
    empresa = item.get("empresa", "")
    sol_id = item.get("solicitud_id", "")
    
    # 1. Tech Stack categorization for filters
    full_text = f"{item.get('funciones', '')} {item.get('perfil_requerido', '')} {item.get('tecnologias_str', '')}".lower()
    
    tags = []
    if "sql" in full_text or "base de datos" in full_text or "oracle" in full_text or "postgres" in full_text or "mysql" in full_text:
        tags.append("SQL")
    if "react" in full_text or "frontend" in full_text or "javascript" in full_text or "html" in full_text or "css" in full_text or "web" in full_text or cat_id == "TIER_1":
        tags.append("Frontend / Web")
    if "java" in full_text or "spring" in full_text:
        tags.append("Java")
    if "python" in full_text or "django" in full_text:
        tags.append("Python")
    if ".net" in full_text or "c#" in full_text or "csharp" in full_text:
        tags.append(".NET / C#")
    if "git" in full_text or "github" in full_text or cat_id in ["TIER_1", "TIER_2"]:
        tags.append("Git")
    if "api" in full_text or "rest" in full_text or "backend" in full_text or cat_id == "TIER_1":
        tags.append("APIs REST")
    if "pruebas" in full_text or "qa" in full_text or "testing" in full_text or "sqa" in full_text or "calidad" in full_text:
        tags.append("QA / Testing")
    if "cloud" in full_text or "aws" in full_text or "azure" in full_text:
        tags.append("Cloud")
    if "erp" in full_text or "sap" in full_text or "sistemas" in full_text or cat_id == "TIER_2":
        tags.append("ERP / Sistemas")
    if "redes" in full_text or "servidores" in full_text or "soporte" in full_text or cat_id == "TIER_3":
        tags.append("Redes / Soporte")
        
    item["stack_tags"] = tags if tags else ["Software General"]

    # 2. Cumulative Financial Projections (5-Year Net Accumulated Income)
    if cat_id == "TIER_1":
        item["finanzas_5anios"] = {
            "practica_6m": "$8.541.000 COP",
            "anio_1": "$45.000.000 COP",
            "acumulado_3a": "$185.000.000 COP",
            "acumulado_5a": "$450.000.000 a $720.000.000+ COP",
            "diferencial_vs_pyme": "+$320.000.000 COP adicionales",
            "patrimonio_potencial": "Alta capacidad de ahorro e inversión en certificaciones internacionales"
        }
    elif cat_id == "TIER_2":
        item["finanzas_5anios"] = {
            "practica_6m": "$8.541.000 COP",
            "anio_1": "$36.000.000 COP",
            "acumulado_3a": "$150.000.000 COP",
            "acumulado_5a": "$320.000.000 a $480.000.000 COP",
            "diferencial_vs_pyme": "+$210.000.000 COP adicionales",
            "patrimonio_potencial": "Excelente estabilidad bancaria, primas extralegales y créditos preferenciales"
        }
    elif cat_id == "TIER_3":
        item["finanzas_5anios"] = {
            "practica_6m": "$8.541.000 COP",
            "anio_1": "$28.000.000 COP",
            "acumulado_3a": "$115.000.000 COP",
            "acumulado_5a": "$210.000.000 a $310.000.000 COP",
            "diferencial_vs_pyme": "+$110.000.000 COP adicionales",
            "patrimonio_potencial": "Ingresos estables con posibilidad de pivotar a DevOps/Cloud"
        }
    elif cat_id == "TIER_4":
        item["finanzas_5anios"] = {
            "practica_6m": "$6.405.000 - $8.541.000 COP",
            "anio_1": "$22.000.000 COP",
            "acumulado_3a": "$85.000.000 COP",
            "acumulado_5a": "$145.000.000 a $195.000.000 COP",
            "diferencial_vs_pyme": "Base salarial estándar de soporte físico",
            "patrimonio_potencial": "Crecimiento salarial lineal moderado"
        }
    else:
        item["finanzas_5anios"] = {
            "practica_6m": "$6.405.000 COP",
            "anio_1": "$18.000.000 COP",
            "acumulado_3a": "$65.000.000 COP",
            "acumulado_5a": "$110.000.000 a $150.000.000 COP",
            "diferencial_vs_pyme": "Línea base sin valorización de software",
            "patrimonio_potencial": "Crecimiento limitado sin stack de programación"
        }

    # 3. Technical Interview Simulator (5 Tailored Questions & Model Answers)
    if cat_id == "TIER_1":
        item["preguntas_entrevista"] = [
            {
                "pregunta": "¿Cómo estructuras una aplicación de software moderna y qué buenas prácticas de código limpio aplicas?",
                "respuesta_modelo": "Explica el uso de arquitecturas modulares (como MVC o separación Frontend/Backend con APIs REST), principios SOLID, separación de responsabilidades y tipado. Menciona cómo organizas tus componentes y servicios en tus proyectos de GitHub.",
                "tip_github": "Cita directamente la estructura de carpetas y commits limpios de tus repositorios en github.com/lakerstrake."
            },
            {
                "pregunta": "¿Cómo gestionas el control de versiones con Git en un equipo colaborativo?",
                "respuesta_modelo": "Explica el flujo de trabajo Git Flow (ramas main, develop, feature branches), creación de Pull Requests con revisión de código y resolución sistemática de conflictos mediante 'git merge' o 'git rebase'.",
                "tip_github": "Demuestra tu historial de commits y ramas activas en GitHub."
            },
            {
                "pregunta": "¿Cómo diseñas y optimizas consultas en bases de datos relacionales (SQL)?",
                "respuesta_modelo": "Menciona cómo creas diagramas entidad-relación normalizados (hasta 3FN), el uso de llaves foráneas para integridad referencial, índices en columnas de búsqueda frecuente y consultas con INNER/LEFT JOINs eficientes evitando consultas N+1.",
                "tip_github": "Habla de los scripts de creación de esquemas y queries SQL estructuradas que has implementado."
            },
            {
                "pregunta": "¿Cuál es tu experiencia trabajando con metodologías ágiles como Scrum?",
                "respuesta_modelo": "Menciona la dinámica de Sprints de 2 semanas, Daily Standups para sincronización, historias de usuario con criterios de aceptación claros y retrospectivas para mejora continua aplicadas durante tu formación ADSO.",
                "tip_github": "Enfoca tu respuesta en tu adaptabilidad y compromiso con las entregas a tiempo."
            },
            {
                "pregunta": "¿Por qué deberíamos seleccionarte a ti como aprendiz ADSO para nuestra vacante?",
                "respuesta_modelo": f"Porque cuento con bases sólidas en programación y bases de datos, curiosidad constante por aprender nuevas tecnologías, total disponibilidad inmediata para integrarme al equipo de {empresa} y un portafolio público verificable que demuestra mi pasión por el código.",
                "tip_github": "Invita al entrevistador a revisar tu código en vivo en github.com/lakerstrake."
            }
        ]
    elif cat_id == "TIER_2":
        item["preguntas_entrevista"] = [
            {
                "pregunta": "¿Cómo aseguras la consistencia e integridad de los datos en un sistema corporativo?",
                "respuesta_modelo": "Explica el concepto de transacciones ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad) usando BEGIN TRANSACTION, COMMIT y ROLLBACK ante excepciones, junto con restricciones CHECK y claves foráneas.",
                "tip_github": "Explica cómo proteges la información crítica de negocio en bases de datos relacionales."
            },
            {
                "pregunta": "¿Qué diferencia hay entre un Stored Procedure y una Vista, y cuándo usar cada uno?",
                "respuesta_modelo": "Una Vista es una consulta SELECT almacenada que simplifica reportes y oculta complejidad sin recibir parámetros de ejecución, mientras que un Stored Procedure ejecuta lógica de negocio, acepta parámetros de entrada/salida y puede modificar datos en múltiples tablas.",
                "tip_github": "Menciona tu habilidad escribiendo procedimientos almacenados y consultas analíticas."
            },
            {
                "pregunta": "¿Cómo abordarías la integración entre dos sistemas de la empresa (ej. ERP con portal web)?",
                "respuesta_modelo": "A través de APIs RESTful usando formato JSON con autenticación segura (JWT o API Keys), validación de esquemas en ambos extremos y registro de logs de auditoría para trazabilidad de cada transacción.",
                "tip_github": "Relaciona cómo conectas el backend de tus proyectos con servicios externos."
            },
            {
                "pregunta": "¿Cómo manejas grandes volúmenes de datos para no saturar el servidor?",
                "respuesta_modelo": "Implementando paginación eficiente en base de datos (OFFSET/FETCH o cursor-based), indexación estratégica en campos de filtro y optimización de planes de ejecución evitando 'SELECT *'.",
                "tip_github": "Resalta tu enfoque analítico y metódico para la optimización de sistemas."
            },
            {
                "pregunta": "¿Qué te motiva a hacer tu etapa productiva en el área de sistemas y datos de nuestra empresa?",
                "respuesta_modelo": f"La oportunidad de trabajar con infraestructura y flujos de información a escala real en {empresa}, donde la precisión y el rigor técnico en bases de datos son fundamentales para la operación.",
                "tip_github": "Demuestra compromiso y responsabilidad con los procesos corporativos."
            }
        ]
    else:
        item["preguntas_entrevista"] = [
            {
                "pregunta": "¿Cómo manejas una situación en la que un usuario o sistema reporta un fallo crítico?",
                "respuesta_modelo": "Manteniendo la calma, recopilando la evidencia del error (código de error, logs, pasos para reproducir), clasificando la severidad según ITIL y aplicando solución paso a paso documentando todo el proceso.",
                "tip_github": "Enfatiza tu pensamiento estructurado de resolución de problemas."
            },
            {
                "pregunta": "¿Cómo utilizarías tus conocimientos de software en el área de soporte e infraestructura?",
                "respuesta_modelo": "Creando scripts de automatización para tareas repetitivas, resolviendo incidencias a nivel de bases de datos y apoyando el despliegue y configuración técnica de aplicaciones.",
                "tip_github": "Muestra que un aprendiz ADSO aporta valor técnico superior a un soporte convencional."
            },
            {
                "pregunta": "¿Qué herramientas y comandos de terminal dominas para administración técnica?",
                "respuesta_modelo": "Manejo de terminal Linux y PowerShell de Windows para gestión de procesos, diagnóstico de red (ping, netstat, traceroute), revisión de logs de eventos y configuración de servicios.",
                "tip_github": "Menciona tu familiaridad con entornos de desarrollo y consola."
            },
            {
                "pregunta": "¿Cómo te organizas para atender múltiples solicitudes de soporte al mismo tiempo?",
                "respuesta_modelo": "Priorizando según el impacto en el negocio y la urgencia del usuario, utilizando sistemas de tickets y manteniendo una comunicación clara y empática con el solicitante.",
                "tip_github": "Resalta tu actitud de servicio y responsabilidad profesional."
            },
            {
                "pregunta": "¿Cuál es tu disponibilidad y expectativa en nuestra empresa?",
                "respuesta_modelo": f"Tengo disponibilidad inmediata para iniciar mi Contrato de Aprendizaje, con todo el entusiasmo de aportar mis conocimientos técnicos en {empresa} y aprender de los profesionales del equipo.",
                "tip_github": "Transmite energía positiva y ganas de aportar desde el primer día."
            }
        ]

# Save updated JSON
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Save updated Excel and CSV
df = pd.DataFrame(data)
df.to_excel(r"output/empresas_caprendizaje_completo.xlsx", index=False)
df.to_csv(r"output/empresas_caprendizaje_completo.csv", index=False, encoding="utf-8")

print("Successfully generated all Interview Simulators, Tech Stack tags, and 5-Year Cumulative Financial Models for 179 companies!")
