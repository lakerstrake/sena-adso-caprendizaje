import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8878
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\f64e925a-a1fa-4e35-b388-b9f016f83488"

def start_server():
    os.chdir(os.path.join(ROOT, "output"))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def capture_ui_evidence():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        url = f"http://localhost:{PORT}/index.html"
        page.goto(url)
        page.wait_for_selector(".data-table tbody tr", timeout=8000)

        # 1. Capture Dashboard with Toolbar and Quick Sync Buttons
        img1 = os.path.join(ARTIFACT_DIR, "01_dashboard_sync_buttons.png")
        page.screenshot(path=img1)
        print(f"[+] Screenshot 1 saved: {img1}")

        # 2. Trigger Sync and capture Toast & Active State
        page.click("#btnToolbarSyncSgva")
        page.wait_for_selector("#toastMsg", state="visible", timeout=4000)
        img2 = os.path.join(ARTIFACT_DIR, "02_sync_toast_feedback.png")
        page.screenshot(path=img2)
        print(f"[+] Screenshot 2 saved: {img2}")

        # 3. Open SGVA Sync & Diagnostics Modal
        time.sleep(2.2)
        page.click("#btnSgvaStatusBadge")
        page.wait_for_selector("#sgvaSyncModal", state="visible", timeout=3000)
        img3 = os.path.join(ARTIFACT_DIR, "03_sgva_sync_modal.png")
        page.screenshot(path=img3)
        print(f"[+] Screenshot 3 saved: {img3}")

        # 4. Light theme capture of Modal
        page.keyboard.press("Escape")
        time.sleep(0.3)
        page.click("#themeBtn") # Switch to light mode
        time.sleep(0.3)
        page.click("#btnSgvaStatusBadge")
        page.wait_for_selector("#sgvaSyncModal", state="visible", timeout=3000)
        img4 = os.path.join(ARTIFACT_DIR, "04_sgva_modal_light.png")
        page.screenshot(path=img4)
        print(f"[+] Screenshot 4 saved: {img4}")

        browser.close()

if __name__ == "__main__":
    capture_ui_evidence()
