import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8877

def start_server():
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def test_sgva_sync():
    print("=" * 70)
    print(" PRUEBA E2E: BOTON Y SISTEMA DE ACTUALIZACION SGVA SENA (HTTP)")
    print("=" * 70)

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        url = f"http://localhost:{PORT}/index.html"
        print(f"[*] Abriendo aplicacion en servidor HTTP: {url}")

        console_errors = []
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)

        page.goto(url)
        page.wait_for_selector(".data-table tbody tr", timeout=8000)
        print("[+] Aplicacion cargada correctamente.")

        # 1. Verify buttons exist
        btn_quick = page.locator("#btnQuickSyncSgva")
        btn_toolbar = page.locator("#btnToolbarSyncSgva")
        btn_badge = page.locator("#btnSgvaStatusBadge")
        
        assert btn_quick.is_visible(), "El boton de actualizacion rapida en el Navbar no es visible"
        assert btn_toolbar.is_visible(), "El boton de actualizacion en la Toolbar no es visible"
        assert btn_badge.is_visible(), "La insignia de estado de sincronizacion no es visible"
        print("[✓] Verificacion 1: Todos los botones de sincronizacion estan presentes y visibles.")

        # 2. Click toolbar sync button and verify toast
        print("[*] Ejecutando sincronizacion desde la Toolbar...")
        btn_toolbar.click()
        page.wait_for_selector("#toastMsg", state="visible", timeout=4000)
        toast_text = page.locator("#toastMsg").text_content()
        print(f"[+] Toast detectado: {toast_text}")
        assert "Sincronizado" in toast_text or "actualizadas" in toast_text, "El mensaje de toast no confirma la sincronizacion"
        print("[✓] Verificacion 2: Sincronizacion en caliente y toast de confirmacion ejecutados.")

        # 3. Open SGVA Sync Modal
        print("[*] Abriendo Modal de Diagnostico y Sincronizacion SGVA...")
        btn_badge.click()
        page.wait_for_selector("#sgvaSyncModal", state="visible", timeout=3000)
        modal_title = page.locator("#mSyncTitle").text_content()
        assert "Sincronización SGVA" in modal_title or "Sincronizacion SGVA" in modal_title, "El titulo del modal no coincide"
        print("[✓] Verificacion 3: Modal de Sincronizacion SGVA abierto correctamente.")

        # 4. Trigger sync inside Modal
        print("[*] Ejecutando sincronizacion paso a paso dentro del Modal...")
        page.locator("#btnModalTriggerSync").click()
        time.sleep(1.0)
        
        # Check stepper steps
        step1 = page.locator("#step1")
        assert "step-ok" in step1.get_attribute("class"), "Paso 1 del pipeline no finalizo en OK"
        print("[✓] Verificacion 4: Pipeline ETL interactivo ejecutado paso a paso con exito.")

        # Close Modal
        page.keyboard.press("Escape")
        time.sleep(0.3)
        assert not page.locator("#sgvaSyncModal").is_visible(), "El modal no se cerro con la tecla Escape"
        print("[✓] Verificacion 5: Cierre accesible con tecla Escape validado.")

        # 5. Test Keyboard Shortcut (Alt + S)
        print("[*] Probando atajo de teclado accesible (Alt + S)...")
        time.sleep(3.2) # Wait for debounce lockout to clear
        page.keyboard.press("Alt+s")
        page.wait_for_selector("#toastMsg", state="visible", timeout=4000)
        print(f"[+] Toast por atajo: {page.locator('#toastMsg').text_content()}")
        print("[✓] Verificacion 6: Atajo de teclado Alt + S validado.")

        print("\n[✓] ¡TODAS LAS PRUEBAS E2E PASARON EXITOSAMENTE CON SERVIDOR HTTP!")

        browser.close()

if __name__ == "__main__":
    test_sgva_sync()
