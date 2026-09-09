# -*- coding: utf-8 -*-
"""Comprueba que el perfil guardado sustituya los datos en todas las cartas."""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8899/index.html"
OWNER = ["Juan Manuel", "jmlagos2003@gmail.com", "300 727 9875",
         "1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln", "github.com/lakerstrake",
         "juan-manuel-lagos-monroy", "Mecatrónica"]
passed, failed = [], []


def check(name, cond, detail=""):
    (passed if cond else failed).append(name)
    print(("  PASS  " if cond else "  FALLO ") + name + ((" :: " + str(detail)) if detail else ""))


with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_context(viewport={"width": 1440, "height": 900}).new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); time.sleep(1.6)

    print("\n== ESTADO INICIAL (perfil de ejemplo) ==")
    check("avisa que el perfil es de ejemplo", pg.is_visible(".perfil-aviso"))
    check("boton Mi perfil en la cabecera", pg.is_visible("button.candidate-pill"))

    print("\n== GUARDAR UN PERFIL PROPIO ==")
    pg.click("button.candidate-pill"); time.sleep(0.8)
    check("modal de perfil abierto", pg.is_visible("#profileModal"))
    check("foco dentro del modal",
          pg.evaluate("() => document.querySelector('#profileModal').contains(document.activeElement)"))

    datos = {
        "nombre": "Ana María Ruiz Peña",
        "email": "ana.ruiz@ejemplo.com",
        "telefono": "(+57) 301 555 4433",
        "formacion": "Técnica en Sistemas del SENA",
        "cv": "https://drive.google.com/file/d/ANA_CV_123/view",
        "certificados": "https://drive.google.com/drive/folders/ANA_CERTS",
        "github": "https://github.com/anaruiz",
        "linkedin": "https://linkedin.com/in/ana-ruiz",
    }
    for k, v in datos.items():
        pg.fill(f"#perfil_{k}", v)

    pg.click("[data-action='saveProfile']"); time.sleep(1.2)
    check("modal cerrado tras guardar", not pg.is_visible("#profileModal"))
    check("banner muestra el nuevo nombre", "Ana María Ruiz Peña" in pg.inner_text("#candidateBanner"))
    check("desaparece el aviso de ejemplo", not pg.is_visible(".perfil-aviso"))

    print("\n== LA CARTA SALE A SU NOMBRE ==")
    pg.click("#tableBody tr:nth-child(1) button:has-text('Detalle')"); time.sleep(1.2)
    carta = pg.inner_text("#mOutreachBody")
    check("firma con el nombre nuevo", "Ana María Ruiz Peña" in carta)
    check("correo sustituido", "ana.ruiz@ejemplo.com" in carta or "@" not in carta)
    check("CV sustituido", "ANA_CV_123" in carta)
    check("GitHub sustituido", "github.com/anaruiz" in carta)
    check("LinkedIn sustituido", "ana-ruiz" in carta)
    check("formación sustituida", "Técnica en Sistemas del SENA" in carta)
    fugas = [t for t in OWNER if t in carta]
    check("sin rastro del perfil de ejemplo", fugas == [], fugas)

    href = pg.get_attribute("#mOutreachActions a[href^='mailto'], #mOutreachActions a[href*='mail.google']", "href") or ""
    check("el enlace de correo lleva los datos nuevos", "Ana" in href.replace("%20", " "), href[:70])

    print("\n== WHATSAPP Y LINKEDIN ==")
    # Los selectores de canal viven en la pestaña de postulación del modal.
    pg.click(".modal-tab-item:has-text('Carta')"); time.sleep(0.6)
    for canal, sel, esperado in [("wa", "#mChWA", "Ana María"),
                                 ("linkedin", "#mChLinkedIn", "Ana")]:
        try:
            pg.click(sel); time.sleep(0.7)
            txt = pg.inner_text("#mOutreachBody")
            check(f"mensaje de {canal} personalizado", esperado in txt, txt[:60])
            check(f"{canal} sin datos del ejemplo", not any(t in txt for t in OWNER))
        except Exception as e:
            check(f"canal {canal}", False, str(e)[:80])
    pg.keyboard.press("Escape"); time.sleep(0.5)

    print("\n== PERSISTE Y SE PUEDE BORRAR ==")
    pg.reload(wait_until="networkidle"); time.sleep(1.6)
    check("el perfil sobrevive a la recarga", "Ana María Ruiz Peña" in pg.inner_text("#candidateBanner"))

    pg.click("button.candidate-pill"); time.sleep(0.8)
    check("el formulario se rellena con lo guardado",
          pg.input_value("#perfil_nombre") == "Ana María Ruiz Peña")
    pg.click("[data-action='resetProfile']"); time.sleep(1.0)
    check("al borrar vuelve el perfil de ejemplo", pg.is_visible(".perfil-aviso"))

    print("\n== VALIDACION DEL FORMULARIO ==")
    pg.click("button.candidate-pill"); time.sleep(0.7)
    pg.fill("#perfil_nombre", ""); pg.fill("#perfil_email", "ana@x.com")
    pg.click("[data-action='saveProfile']"); time.sleep(0.5)
    check("exige el nombre", pg.is_visible("#perfilError"))
    pg.fill("#perfil_nombre", "Ana"); pg.fill("#perfil_email", "sin-arroba")
    pg.click("[data-action='saveProfile']"); time.sleep(0.5)
    check("exige un correo valido", pg.is_visible("#perfilError"))
    pg.fill("#perfil_email", "ana@x.com"); pg.fill("#perfil_cv", "javascript:alert(1)")
    pg.click("[data-action='saveProfile']"); time.sleep(0.5)
    check("rechaza enlaces que no son http(s)", pg.is_visible("#perfilError"))

    print("\n== CAMPOS VACIOS ==")
    for k in ("github", "linkedin", "certificados", "formacion"):
        pg.fill(f"#perfil_{k}", "")
    pg.fill("#perfil_cv", "https://ejemplo.com/cv.pdf")
    pg.click("[data-action='saveProfile']"); time.sleep(1.0)
    check("guarda con los opcionales vacios", not pg.is_visible("#profileModal"))
    pg.click("#tableBody tr:nth-child(1) button:has-text('Detalle')"); time.sleep(1.2)
    carta2 = pg.inner_text("#mOutreachBody")
    check("la carta no ofrece GitHub ajeno", "lakerstrake" not in carta2)
    check("la carta no ofrece LinkedIn ajeno", "juan-manuel-lagos" not in carta2)
    check("no atribuye estudios ajenos", "Mecatrónica" not in carta2)
    pg.keyboard.press("Escape"); time.sleep(0.4)

    check("sin errores de JavaScript", not errs, errs)
    br.close()

print(f"\n===== RESULTADO: {len(passed)} PASAN / {len(failed)} FALLAN =====")
for f in failed:
    print("  FALLO:", f)
sys.exit(1 if failed else 0)
