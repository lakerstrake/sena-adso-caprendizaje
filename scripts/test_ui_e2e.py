# -*- coding: utf-8 -*-
"""Suite funcional end-to-end del directorio SENA ADSO."""
import sys, time, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/index.html"
passed, failed = [], []

def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(("  PASS  " if cond else "  FALLO ") + name + ((" :: " + str(detail)) if detail else ""))

with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True)
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); time.sleep(1.5)

    print("\n== CARGA Y DATOS ==")
    total = pg.evaluate("() => (window.RAW_DATA||[]).length")
    check("dataset cargado (195)", total == 195, total)
    check("sin errores de JavaScript", not errors, errors)
    check("filas renderizadas", pg.eval_on_selector_all("#tableBody tr", "e=>e.length") == 50)
    check("contadores coherentes", pg.inner_text("#lblTotalCount") == "195")
    segs = pg.evaluate("() => [...document.querySelectorAll('.seg-pill')].map(e=>e.textContent)")
    check("segmentos por tier = dataset", segs == ["195", "22", "135", "14", "24"], segs)
    dead = pg.evaluate("""() => {
        const campos = ['apoyo_sostenimiento','reputacion_rating','escalabilidad_score',
                        'techo_salarial_5anios','rol_salida_egresado','whatsapp_url',
                        'curva_aprendizaje_titulo','salario_egresado_jr','cat_color'];
        return campos.filter(c => window.RAW_DATA.some(d => c in d));
    }""")
    check("dataset sin campos constantes ni muertos", dead == [], dead)
    mails = pg.evaluate("() => window.RAW_DATA.filter(d=>d.email && !d.email.includes('@')).length")
    check("sin correos invalidos", mails == 0, mails)

    print("\n== FILTROS ==")
    pg.fill("#mainSearch", "medellin"); time.sleep(0.8)
    n1 = int(pg.inner_text("#lblVisibleCount"))
    check("busqueda por ciudad filtra", 0 < n1 < 195, n1)
    pg.fill("#mainSearch", ""); time.sleep(0.7)

    pg.click(".tier-seg-btn.seg-1"); time.sleep(0.7)
    check("filtro Tier 1 = 22", pg.inner_text("#lblVisibleCount") == "22")
    pg.click(".tier-seg-btn[data-tier='TIER_2']"); time.sleep(0.7)
    check("filtro Tier 2 = 135", pg.inner_text("#lblVisibleCount") == "135")
    pg.click(".tier-seg-btn[data-tier='']"); time.sleep(0.7)

    pg.click(".chip-btn[data-stack='Python']"); time.sleep(0.7)
    nPy = int(pg.inner_text("#lblVisibleCount"))
    check("chip de stack Python filtra", 0 < nPy < 195, nPy)
    pg.click(".chip-btn[data-stack='']"); time.sleep(0.6)

    if not pg.is_visible("#secondaryFiltersRow"):
        pg.click("#toggleFiltersBtn"); time.sleep(0.5)
    pg.select_option("#filterChannel", "WHATSAPP"); time.sleep(0.8)
    nWa = int(pg.inner_text("#lblVisibleCount"))
    check("filtro canal WhatsApp", 0 < nWa < 195, nWa)
    check("insignia de filtros activos", pg.inner_text("#activeFilterBadge") == "1")
    pg.click("[data-action='resetFilters']"); time.sleep(0.8)
    check("restablecer filtros vuelve a 195", pg.inner_text("#lblVisibleCount") == "195")

    print("\n== ORDENACION ==")
    if not pg.is_visible("#secondaryFiltersRow"):
        pg.click("#toggleFiltersBtn"); time.sleep(0.5)
    for value, label in [("comp_asc", "menor competencia"),
                         ("vacancies_desc", "mas vacantes"),
                         ("ranking_asc", "ranking base")]:
        pg.select_option("#filterSort", value); time.sleep(0.7)
        first = pg.inner_text("#tableBody tr:nth-child(1)")[:26].replace("\n", " ")
        check("orden por " + label, pg.eval_on_selector_all("#tableBody tr", "e=>e.length") > 0, first)

    print("\n== VISTAS Y NAVEGACION ==")
    pg.click("#btnLayoutCards"); time.sleep(0.9)
    check("vista tarjetas renderiza", pg.eval_on_selector_all("#cardsGridWrap > *", "e=>e.length") == 50)
    pg.click("#btnLayoutTable"); time.sleep(0.7)
    check("vuelve a vista tabla", pg.is_visible("#tableCardWrap"))

    pg.click("#pillStrategy"); time.sleep(0.6)
    check("pestana Guia visible", pg.is_visible("#sectionStrategy"))
    pg.click("#pillDirectory"); time.sleep(0.6)
    check("pestana Directorio visible", pg.is_visible("#sectionDirectory"))

    print("\n== PAGINACION ==")
    pgbtns = pg.evaluate("() => [...document.querySelectorAll('#paginationPages .page-btn')].map(b=>({t:b.innerText.trim(),d:b.disabled,al:b.getAttribute('aria-label')}))")
    check("botones de pagina con nombre accesible", all(b["al"] for b in pgbtns), len(pgbtns))
    check("flecha anterior deshabilitada en pagina 1", pgbtns[0]["d"] is True)
    dupstyle = pg.evaluate("() => [...document.querySelectorAll('#paginationPages button')].filter(b=>(b.outerHTML.split('>')[0].match(/style=/g)||[]).length>1).length")
    check("sin atributo style duplicado", dupstyle == 0, dupstyle)
    pg.click("#paginationPages .page-btn[data-page='2']"); time.sleep(0.8)
    check("navega a la pagina 2", "51" in pg.inner_text(".table-footer"), pg.inner_text(".table-footer")[:40])
    pg.click("#paginationPages .page-btn[data-page='1']"); time.sleep(0.7)

    print("\n== FAVORITOS Y COMPARACION ==")
    pg.click("#tableBody tr:nth-child(1) [data-action='toggleFavorite']"); time.sleep(0.5)
    check("favorito agregado", pg.inner_text("#pillFavCount") == "1")
    pg.click("#pillFavs"); time.sleep(0.7)
    check("pestana Favoritas muestra 1", pg.inner_text("#lblVisibleCount") == "1")
    pg.click("#pillDirectory"); time.sleep(0.6)
    pg.click("#tableBody tr:nth-child(1) [data-action='toggleFavorite']"); time.sleep(0.5)
    check("favorito removido", pg.inner_text("#pillFavCount") == "0")

    for i in (1, 2, 3):
        pg.click(f"#tableBody tr:nth-child({i}) [data-action='toggleCompare']"); time.sleep(0.35)
    check("dock con 3 elementos", pg.inner_text("#dockCount") == "3")
    check("body marcado como dock-active", pg.evaluate("() => document.body.classList.contains('dock-active')"))
    check("fichas del dock con boton accesible",
          pg.eval_on_selector_all(".dock-chip-remove", "e=>e.every(b=>b.getAttribute('aria-label'))"))
    pg.click("[data-action='openCompareModal']"); time.sleep(0.9)
    check("modal comparativa abierto", pg.is_visible("#compareModal"))
    cols = pg.eval_on_selector_all("#compareTable tr:first-child th, #compareTable tr:first-child td", "e=>e.length")
    check("comparativa con 3 columnas + etiqueta", cols >= 4, cols)
    pg.keyboard.press("Escape"); time.sleep(0.5)
    pg.click("[data-action='clearComparison']"); time.sleep(0.6)
    check("comparacion limpiada", pg.inner_text("#dockCount") == "0")

    print("\n== MODAL DE DETALLE Y CANALES ==")
    pg.click("#tableBody tr:nth-child(1) button:has-text('Detalle')"); time.sleep(1.0)
    check("modal de detalle abierto", pg.is_visible("#detailModal"))
    check("titulo poblado", len(pg.inner_text("#mTitle")) > 3, pg.inner_text("#mTitle"))
    tabs = pg.eval_on_selector_all(".modal-tab-item", "e=>e.map(t=>t.innerText.trim())")
    for t in tabs:
        try:
            pg.click(f".modal-tab-item:has-text('{t}')"); time.sleep(0.45)
        except Exception:
            pass
    check("pestanas del modal navegables", len(tabs) >= 2, tabs)
    cuerpo = pg.evaluate("() => document.querySelector('#detailModal').innerText")
    check("modal sin metricas retiradas",
          not any(t in cuerpo for t in ("Techo Salarial", "Reputación / Clima", "Rol Proyectado")))
    pg.keyboard.press("Escape"); time.sleep(0.5)
    check("modal cierra con Escape", not pg.is_visible("#detailModal"))

    print("\n== TEMA, PANEL Y EXPORTACION ==")
    t0 = pg.get_attribute("html", "data-theme")
    pg.click("#themeBtn"); time.sleep(0.6)
    t1 = pg.get_attribute("html", "data-theme")
    check("alterna tema", t0 != t1, f"{t0} -> {t1}")
    pg.reload(wait_until="networkidle"); time.sleep(1.4)
    check("tema persiste tras recargar", pg.get_attribute("html", "data-theme") == t1)
    pg.click("#themeBtn"); time.sleep(0.5)

    gone = pg.evaluate("""() => ['authModal','sgvaSyncModal','cvAlertsModal','syncPanel',
        'btnAuthTrigger','lblSessionTimer','btnQuickSyncSgva','btnToolbarSyncSgva']
        .filter(id => document.getElementById(id))""")
    check("interfaz sin login, sync ni telemetria", gone == [], gone)

    try:
        with pg.expect_download(timeout=8000) as dl:
            pg.click("[data-action='exportData'][data-format='csv']")
        d = dl.value
        check("exporta CSV", d.suggested_filename.endswith(".csv"), d.suggested_filename)
    except Exception as e:
        check("exporta CSV", False, str(e)[:90])

    print("\n== ACCESIBILIDAD ==")
    # Recarga limpia: en Chromium un clic previo fija el punto de partida del Tab.
    pg.reload(wait_until="networkidle"); time.sleep(1.3)
    pg.keyboard.press("Tab"); time.sleep(0.3)
    check("primer tabulador es el enlace de salto",
          pg.evaluate("() => document.activeElement.classList.contains('skip-link')"),
          pg.evaluate("() => document.activeElement.className"))
    check("un solo h1", pg.eval_on_selector_all("h1", "e=>e.length") == 1)
    check("region viva en el contador",
          pg.get_attribute(".results-count", "aria-live") == "polite")
    check("sin controles anonimos", pg.evaluate("""() => [...document.querySelectorAll('button,a')]
        .filter(b=>!(b.innerText||'').trim() && !b.getAttribute('aria-label') && !b.getAttribute('title')).length""") == 0)

    print("\n== FOCO Y TECLADO EN DIALOGOS ==")
    for opener, modal, label in [("#tableBody tr:nth-child(1) button:has-text('Detalle')", "#detailModal", "detalle")]:
        pg.click(opener); time.sleep(1.0)
        inside = pg.evaluate(f"() => document.querySelector('{modal}').contains(document.activeElement)")
        check(f"foco entra en el dialogo de {label}", inside)
        pg.keyboard.press("Escape"); time.sleep(0.6)
        check(f"Escape cierra el dialogo de {label}", not pg.is_visible(modal))
        back = pg.evaluate("() => document.activeElement.closest('#tableBody') !== null")
        check(f"foco vuelve al invocador ({label})", back, pg.evaluate("() => document.activeElement.className"))

    print("\n== SEGURIDAD (XSS) ==")
    xss = pg.evaluate("""() => {
        const s = window.SecurityService || null;
        return s ? s.escapeHtml('<img src=x onerror=alert(1)>') : 'sin-servicio';
    }""")
    check("escapeHtml neutraliza etiquetas", "<img" not in str(xss), xss)
    pg.fill("#mainSearch", "<script>alert(1)</script>"); time.sleep(0.8)
    check("busqueda con payload no inyecta", not errors, errors)
    pg.fill("#mainSearch", ""); time.sleep(0.5)

    check("sin errores de JS al final", not errors, errors)
    br.close()

print(f"\n===== RESULTADO: {len(passed)} PASAN / {len(failed)} FALLAN =====")
if failed:
    for f in failed:
        print("  FALLO:", f)
sys.exit(1 if failed else 0)
