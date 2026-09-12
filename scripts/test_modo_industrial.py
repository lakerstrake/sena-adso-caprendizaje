# -*- coding: utf-8 -*-
"""Verifica el modo Ingeniería Industrial: datos reales, filtros y cartas."""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/index.html"
passed, failed = [], []


def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(("  PASS  " if cond else "  FALLO ") + name + ((" :: " + str(detail)) if detail else ""))


with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_context(viewport={"width": 1500, "height": 950}).new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); time.sleep(1.7)

    print("\n== DATOS VERIFICADOS EN EL REGISTRO MERCANTIL ==")
    stats = pg.evaluate("""() => {
        const d = window.RAW_DATA || [];
        return {
            total: d.length,
            verificadas: d.filter(x => x.rues_verificado).length,
            conCiiu: d.filter(x => x.rues_ciiu).length,
            conSector: d.filter(x => x.ind_sector && x.ind_sector !== 'Sin verificar').length,
            manufactura: d.filter(x => x.ind_sector === 'Manufactura').length,
            logistica: d.filter(x => x.ind_sector === 'Transporte y Logística').length,
            conCorreo: d.filter(x => x.email && x.email.includes('@')).length
        };
    }""")
    check("dataset completo", stats["total"] == 195, stats["total"])
    check("empresas verificadas en el registro", stats["verificadas"] >= 185, stats["verificadas"])
    check("actividad CIIU declarada", stats["conCiiu"] >= 185, stats["conCiiu"])
    check("sector económico asignado", stats["conSector"] >= 185, stats["conSector"])
    check("manufactura real identificada", stats["manufactura"] >= 15, stats["manufactura"])
    check("logística real identificada", stats["logistica"] >= 8, stats["logistica"])
    check("contactos reales disponibles", stats["conCorreo"] >= 190, stats["conCorreo"])

    print("\n== CAMBIO DE MODO ==")
    check("selector de modo visible", pg.is_visible(".mode-switch"))
    check("arranca en modo software", pg.get_attribute("[data-mode='software']", "aria-pressed") == "true")
    grupos_sw = pg.eval_on_selector_all(".tier-seg-btn", "e=>e.map(b=>b.innerText.split('\\n')[0].trim())")
    check("grupos de software son tiers", any("Tier" in g for g in grupos_sw), grupos_sw[:4])

    pg.click("[data-mode='industrial']"); time.sleep(1.2)
    check("modo industrial activo", pg.get_attribute("[data-mode='industrial']", "aria-pressed") == "true")
    check("body marcado como industrial", pg.evaluate("() => document.body.classList.contains('modo-industrial')"))
    grupos_ind = pg.eval_on_selector_all(".tier-seg-btn", "e=>e.map(b=>b.innerText.split('\\n')[0].trim())")
    check("grupos pasan a sectores reales", any("Manufactura" in g for g in grupos_ind), grupos_ind[:5])
    check("desaparecen los chips de stack", not pg.is_visible(".stack-row"))

    cabeceras = pg.eval_on_selector_all(".data-table thead th", "e=>e.map(t=>t.innerText.trim())")
    check("columna de sector", any("SECTOR" in c.upper() for c in cabeceras), cabeceras[4:7])
    check("columna de actividad CIIU", any("CIIU" in c.upper() for c in cabeceras))
    check("columna de relevancia", any("RELEVANCIA" in c.upper() for c in cabeceras))

    print("\n== ORDEN Y CONTENIDO INDUSTRIAL ==")
    primeras = pg.eval_on_selector_all("#tableBody tr", "e=>e.slice(0,6).map(r=>r.innerText.replace(/\\n/g,' | '))")
    sectores_top = pg.eval_on_selector_all("#tableBody tr .sector-badge", "e=>e.slice(0,6).map(x=>x.innerText.trim())")
    check("las primeras filas son sectores industriales",
          all(s in ("Manufactura", "Transporte y Logística", "Minería y Petróleo", "Energía",
                    "Construcción", "Agroindustria") for s in sectores_top), sectores_top)
    check("se muestra el código CIIU", pg.eval_on_selector_all(".ciiu-code", "e=>e.length") > 0)
    check("se muestra el sello de verificación", pg.eval_on_selector_all(".verif-chip", "e=>e.length") > 0)
    if primeras:
        print("     1ª fila:", primeras[0][:110])

    print("\n== FILTRO POR SECTOR ==")
    pg.click(".tier-seg-btn:has-text('Manufactura')"); time.sleep(0.9)
    n = int(pg.inner_text("#lblVisibleCount"))
    check("filtra por Manufactura", 10 < n < 40, n)
    solo = pg.eval_on_selector_all("#tableBody tr .sector-badge", "e=>[...new Set(e.map(x=>x.innerText.trim()))]")
    check("solo empresas de ese sector", solo == ["Manufactura"], solo)
    pg.click(".tier-seg-btn[data-tier='']"); time.sleep(0.8)

    print("\n== CARTA DE INGENIERÍA INDUSTRIAL ==")
    pg.click("button.candidate-pill"); time.sleep(0.8)
    for k, v in {
        "nombre": "Julián López López",
        "profesion": "Ingeniero Industrial",
        "experiencia": "2 años en planeación de producción",
        "email": "julian.lopez@ejemplo.com",
        "telefono": "(+57) 310 222 3344",
        "cv": "https://drive.google.com/file/d/JULIAN_CV/view",
        "linkedin": "https://linkedin.com/in/julian-lopez",
    }.items():
        pg.fill(f"#perfil_{k}", v)
    pg.click("[data-action='saveProfile']"); time.sleep(1.2)
    check("perfil industrial guardado", "Julián López López" in pg.inner_text("#candidateBanner"))

    pg.click("#tableBody tr:nth-child(1) button:has-text('Detalle')"); time.sleep(1.2)
    pg.click(".modal-tab-item:has-text('Carta')"); time.sleep(0.7)
    carta = pg.inner_text("#mOutreachBody")
    check("firma como Julián", "Julián López López" in carta)
    check("se presenta como ingeniero industrial", "Ingeniero Industrial" in carta)
    check("menciona la experiencia declarada", "planeación de producción" in carta)
    actividad = pg.evaluate("() => { const it = window.RAW_DATA.find(x => document.getElementById('mTitle').textContent.trim() === x.empresa); return it ? (it.ind_actividad || '') : ''; }")
    check("cita la actividad real de la empresa",
          bool(actividad) and actividad.lower() in carta.lower(), actividad)
    check("incluye la hoja de vida", "JULIAN_CV" in carta)
    check("sin rastro del perfil de software",
          not any(t in carta for t in ("Juan Manuel", "jmlagos2003", "lakerstrake", "Mecatrónica", "ADSO")))
    check("no habla de contrato de aprendizaje", "aprendizaje" not in carta.lower())
    print("     carta:", carta[:120].replace("\n", " "))

    for canal, sel in (("wa", "#mChWA"), ("linkedin", "#mChLinkedIn")):
        pg.click(sel); time.sleep(0.7)
        t = pg.inner_text("#mOutreachBody")
        check(f"{canal} a nombre de Julián", "Julián" in t, t[:70])
        check(f"{canal} sin datos del perfil de software",
              not any(x in t for x in ("Juan Manuel", "lakerstrake", "Mecatrónica")))
    check("nota de LinkedIn bajo 300 caracteres", len(pg.inner_text("#mOutreachBody")) <= 300)
    pg.keyboard.press("Escape"); time.sleep(0.5)

    print("\n== EL MODO PERSISTE Y NO ROMPE EL OTRO ==")
    pg.reload(wait_until="networkidle"); time.sleep(1.7)
    check("sigue en modo industrial tras recargar",
          pg.evaluate("() => document.body.classList.contains('modo-industrial')"))
    pg.click("[data-mode='software']"); time.sleep(1.1)
    check("vuelve a software", not pg.evaluate("() => document.body.classList.contains('modo-industrial')"))
    grupos = pg.eval_on_selector_all(".tier-seg-btn", "e=>e.map(b=>b.innerText.split('\\n')[0].trim())")
    check("los tiers vuelven", any("Tier" in g for g in grupos), grupos[:4])
    check("los chips de stack vuelven", pg.is_visible(".stack-row"))
    check("filas siguen renderizando", pg.eval_on_selector_all("#tableBody tr", "e=>e.length") == 50)

    check("sin errores de JavaScript", not errs, errs)
    br.close()

print(f"\n===== RESULTADO: {len(passed)} PASAN / {len(failed)} FALLAN =====")
for f in failed:
    print("  FALLO:", f)
sys.exit(1 if failed else 0)
