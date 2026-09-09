import http.server
import socketserver
import threading
import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8893
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
ARTIFACT_DIR = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\98329ed8-18d0-4152-b2f9-801d4c91531a"

def start_server():
    os.chdir(OUTPUT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def run_tests():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.6)

    with sync_playwright() as p:
        print("\n=======================================================")
        print("  1. PRUEBA EN DISPOSITIVO MÓVIL (iPhone 14 Pro 390x844)")
        print("=======================================================")
        browser = p.chromium.launch(headless=True)
        mobile_context = browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        mobile_page = mobile_context.new_page()
        mobile_page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        mobile_page.on("pageerror", lambda err: print(f"[Browser Error] {err}"))
        mobile_page.goto(f"http://localhost:{PORT}/index.html")
        mobile_page.wait_for_selector(".clean-card", timeout=8000)

        # 1.1 Verificar botones de correo en las tarjetas
        card_mail_links = mobile_page.locator(".clean-card a[data-email-action='true']")
        count = card_mail_links.count()
        print(f"[+] Total tarjetas con enlaces de correo detectados: {count}")
        assert count > 0, "Debe haber al menos una tarjeta con acción de correo"

        first_mail = card_mail_links.first
        first_href = first_mail.get_attribute("href")
        first_target = first_mail.get_attribute("target")
        first_text = first_mail.inner_text()
        first_class = first_mail.get_attribute("class")

        print(f"    - href: {first_href[:60]}...")
        print(f"    - target: {first_target}")
        print(f"    - text: {first_text}")
        print(f"    - class: {first_class}")

        assert first_href.startswith("mailto:"), f"En móvil el href debe ser mailto:, encontrado: {first_href}"
        assert "mail.google.com" not in first_href, "En móvil no debe apuntar a mail.google.com"
        assert first_target is None or first_target == "" or first_target == "_self", f"En móvil no debe tener target='_blank', encontrado: {first_target}"
        assert "Correo (App)" in first_text, f"El texto en móvil debe ser 'Correo (App)', encontrado: {first_text}"
        assert "mini-mail-app" in first_class, f"Debe tener clase mini-mail-app, encontrado: {first_class}"
        print("[✓] Verificación de botones en tarjetas móviles: EXITOSA")

        # Screenshot de vista de tarjetas en móvil
        mobile_page.evaluate("window.scrollTo(0, 520)")
        time.sleep(0.3)
        img_mobile_cards = os.path.join(ARTIFACT_DIR, "mobile_01_cards_email_app.png")
        mobile_page.screenshot(path=img_mobile_cards)
        print(f"[+] Captura guardada: {img_mobile_cards}")

        # 1.2 Abrir Modal de Detalle
        detail_btn = mobile_page.locator(".clean-card button[data-action='openDetailModal']").first
        detail_btn.scroll_into_view_if_needed()
        time.sleep(0.2)
        detail_btn.click()
        mobile_page.wait_for_selector("#detailModal", state="visible", timeout=5000)
        time.sleep(0.3)

        # Verificar correo en ficha de contacto
        contact_email_link = mobile_page.locator("#mContactEmail a")
        if contact_email_link.count() > 0:
            contact_href = contact_email_link.first.get_attribute("href")
            print(f"[+] Correo en datos de contacto: {contact_href[:50]}...")
            assert contact_href.startswith("mailto:"), "El correo de contacto debe ser mailto:"
            print("[✓] Correo en datos de contacto es enlace mailto: EXITOSA")

        # 1.3 Cambiar a Pestaña Outreach (Carta de Postulación)
        mobile_page.click("#mTabOutreach")
        time.sleep(0.4)

        # En móvil, el botón debe ser "Abrir en App de Correo" y NO "Redactar en Gmail"
        outreach_mail_btn = mobile_page.locator("#mOutreachActions a.btn-mail-app")
        assert outreach_mail_btn.count() > 0, "En móvil debe existir el botón .btn-mail-app"
        
        btn_href = outreach_mail_btn.first.get_attribute("href")
        btn_target = outreach_mail_btn.first.get_attribute("target")
        btn_text = outreach_mail_btn.first.inner_text()

        print(f"[+] Botón Outreach Móvil:")
        print(f"    - href: {btn_href[:60]}...")
        print(f"    - target: {btn_target}")
        print(f"    - text: {btn_text}")

        assert btn_href.startswith("mailto:"), "En móvil el botón de postulación debe ser mailto:"
        assert btn_target is None or btn_target == "", "En móvil no debe tener target='_blank'"
        assert "Abrir en App de Correo" in btn_text, "El texto del botón debe ser 'Abrir en App de Correo'"

        # Verificar que NO hay botón web de Gmail en móvil
        gmail_web_btns = mobile_page.locator("#mOutreachActions a.btn-gmail")
        assert gmail_web_btns.count() == 0, "En móvil NO debe aparecer el botón de Gmail Web"
        print("[✓] Verificación de pestaña Outreach en móvil: EXITOSA (Sin redirección web)")

        # Screenshot del modal con el botón de app de correo
        img_mobile_modal = os.path.join(ARTIFACT_DIR, "mobile_02_modal_email_app.png")
        mobile_page.screenshot(path=img_mobile_modal)
        print(f"[+] Captura guardada: {img_mobile_modal}")

        mobile_context.close()

        print("\n=======================================================")
        print("  2. PRUEBA EN ESCRITORIO (Desktop 1280x800)")
        print("=======================================================")
        desktop_context = browser.new_context(viewport={"width": 1280, "height": 800})
        desktop_page = desktop_context.new_page()
        desktop_page.goto(f"http://localhost:{PORT}/index.html")
        desktop_page.wait_for_selector(".data-table tbody tr", timeout=8000)

        # En escritorio, la tabla muestra el botón de Gmail con target=_blank
        table_gmail = desktop_page.locator(".data-table tbody tr a.mini-gmail").first
        t_href = table_gmail.get_attribute("href")
        t_target = table_gmail.get_attribute("target")
        print(f"[+] Enlace en tabla escritorio: {t_href[:50]}... | target={t_target}")
        assert "mail.google.com" in t_href, "En escritorio se mantiene opción web Gmail"
        assert t_target == "_blank", "En escritorio Gmail abre en nueva pestaña"

        # Abrir modal en escritorio
        desktop_page.locator(".data-table tbody tr button[data-action='openDetailModal']").first.click()
        desktop_page.wait_for_selector("#detailModal", state="visible", timeout=4000)
        time.sleep(0.3)
        desktop_page.click("#mTabOutreach")
        time.sleep(0.3)

        # En escritorio deben existir ambos botones (Gmail Web y Correo App)
        desk_gmail = desktop_page.locator("#mOutreachActions a.btn-gmail")
        desk_mailto = desktop_page.locator("#mOutreachActions a[data-email-action='true']")
        print(f"[+] Botones en escritorio: Gmail Web={desk_gmail.count()}, Correo App={desk_mailto.count()}")
        assert desk_gmail.count() > 0, "En escritorio existe botón de Gmail Web"
        assert desk_mailto.count() > 0, "En escritorio existe botón de Correo App"
        print("[✓] Verificación de escritorio: EXITOSA (Mantiene compatibilidad completa)")

        desktop_context.close()
        browser.close()

        print("\n=======================================================")
        print("  [✓✓✓] TODAS LAS PRUEBAS PASARON SATISFACTORIAMENTE")
        print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
