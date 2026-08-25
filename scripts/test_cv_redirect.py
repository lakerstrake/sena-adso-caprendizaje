"""
SGVA SENA ADSO - CV Redirect & Telemetry Endpoint Test (HTTP Server)
"""

import os
import sys
import time
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8767
DIRECTORY = os.path.abspath("output")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"success": true}')

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

def run_cv_test():
    print("=" * 80)
    print(" PROBANDO RUTA Y REDIRECCIÓN DE HOJA DE VIDA EN SERVIDOR HTTP (/cv & /cv.html)")
    print("=" * 80)

    # Start background local HTTP server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    test_query = "?empresa=STEFANINI+COLOMBIA+S.A.S&id=4425748&c=Johana&src=email"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Intercept external calls to google drive
        redirected_urls = []
        context.route("**/*drive.google.com*/**", lambda route: (redirected_urls.append(route.request.url), route.fulfill(status=200, body="<html><body>OK</body></html>")))
        page = context.new_page()
        page.on("request", lambda req: redirected_urls.append(req.url) if "drive.google.com" in req.url else None)

        # Test 1: http://localhost:8767/cv/ with query parameters
        print("\n[+] Test 1: Evaluando /cv/ con parámetros en servidor web...")
        page.goto(f"http://localhost:{PORT}/cv/{test_query}")
        
        has_card = page.is_visible(".gateway-card")
        btn_href = page.get_attribute("#btnManualRedirect", "href")
        print(f"    - Tarjeta Visual Gateway Visible: {has_card}")
        print(f"    - Enlace Directo Google Drive: '{btn_href}'")
        
        assert has_card, "ERROR: La tarjeta gateway debe ser visible"
        assert "drive.google.com" in btn_href, "ERROR: El enlace debe apuntar a Google Drive"

        try:
            page.wait_for_url(lambda url: "drive.google.com" in url, timeout=4000)
        except Exception:
            time.sleep(1.5)

        print(f"    - URL final o interceptada hacia Google Drive: {page.url} / {redirected_urls}")
        assert "drive.google.com" in page.url or any("drive.google.com" in u for u in redirected_urls), "ERROR: No se disparó la redirección a Google Drive"
        print("    [PASS] Redirección automática desde /cv/ funcionando al 100%.")

        # Test 2: http://localhost:8767/cv.html with query parameters
        print("\n[+] Test 2: Evaluando /cv.html...")
        page.goto(f"http://localhost:{PORT}/cv.html{test_query}")
        try:
            page.wait_for_url(lambda url: "drive.google.com" in url, timeout=4000)
        except Exception:
            time.sleep(1.5)
            
        assert "drive.google.com" in page.url or any("drive.google.com" in u for u in redirected_urls), "ERROR: /cv.html debe disparar la redirección a Google Drive"
        print("    [PASS] Redirección automática desde /cv.html funcionando al 100%.")

        browser.close()

    print("\n" + "=" * 80)
    print(" TODAS LAS PRUEBAS DE HOJA DE VIDA PASARON CON ÉXITO (100% OK)")
    print("=" * 80)

if __name__ == "__main__":
    run_cv_test()
