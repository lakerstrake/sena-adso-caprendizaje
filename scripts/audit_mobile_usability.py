import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8883
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\f64e925a-a1fa-4e35-b388-b9f016f83488"

def start_server():
    os.chdir(os.path.join(ROOT, "output"))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def audit_mobile_viewports():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with sync_playwright() as p:
        print("\n--- AUDITANDO VIEWPORT: iPhone 14 Pro (393x852) ---")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = context.new_page()

        url = f"http://localhost:{PORT}/index.html"
        page.goto(url)
        page.wait_for_selector(".data-table tbody tr, .clean-card", timeout=8000)

        # 1. Main Home Mobile View
        img1 = os.path.join(ARTIFACT_DIR, "mobile_01_home.png")
        page.screenshot(path=img1)
        print(f"[+] 1. Home guardada: {img1}")

        # 2. Switch to Cards View
        page.click("#btnLayoutCards")
        time.sleep(0.3)
        img2 = os.path.join(ARTIFACT_DIR, "mobile_02_cards.png")
        page.screenshot(path=img2)
        print(f"[+] 2. Cards View guardada: {img2}")

        # 3. Open Detail Modal
        page.locator(".clean-card").first.click()
        page.wait_for_selector("#detailModal", state="visible", timeout=3000)
        time.sleep(0.4)
        img3 = os.path.join(ARTIFACT_DIR, "mobile_03_detail_modal.png")
        page.screenshot(path=img3)
        print(f"[+] 3. Detail Modal guardada: {img3}")

        # 4. Scroll inside detail modal
        modal_body = page.locator("#detailModal .modal-body")
        if modal_body.is_visible():
            modal_body.evaluate("el => el.scrollTop = 350")
            time.sleep(0.3)
            img4 = os.path.join(ARTIFACT_DIR, "mobile_04_modal_scrolled.png")
            page.screenshot(path=img4)
            print(f"[+] 4. Modal Scrolled guardada: {img4}")

        # 5. Switch to Outreach Tab inside Modal
        page.click("#mTabOutreach")
        time.sleep(0.3)
        img5 = os.path.join(ARTIFACT_DIR, "mobile_05_modal_outreach.png")
        page.screenshot(path=img5)
        print(f"[+] 5. Outreach Tab guardada: {img5}")

        # 6. Close Modal and Open SGVA Sync Modal
        page.keyboard.press("Escape")
        time.sleep(0.3)
        page.click("#btnSgvaStatusBadge")
        page.wait_for_selector("#sgvaSyncModal", state="visible", timeout=3000)
        time.sleep(0.4)
        img6 = os.path.join(ARTIFACT_DIR, "mobile_06_sgva_sync_modal.png")
        page.screenshot(path=img6)
        print(f"[+] 6. SGVA Sync Modal guardada: {img6}")

        browser.close()

if __name__ == "__main__":
    audit_mobile_viewports()
