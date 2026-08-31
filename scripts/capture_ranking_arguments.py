import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PORT = 8881
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACT_DIR = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\f64e925a-a1fa-4e35-b388-b9f016f83488"

def start_server():
    os.chdir(os.path.join(ROOT, "output"))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def capture_ranking_evidence():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        url = f"http://localhost:{PORT}/index.html"
        page.goto(url)
        page.wait_for_selector(".data-table tbody tr", timeout=8000)

        # 1. Capture Top Ranked Table View (#01 Claro Insurance, #02 Wasi, #03 Geocom, #04 Stefanini)
        img1 = os.path.join(ARTIFACT_DIR, "05_meticulous_ranking_table.png")
        page.screenshot(path=img1)
        print(f"[+] Screenshot 1 saved: {img1}")

        # 2. Click on #01 to see the Arguments Modal
        page.locator(".data-table tbody tr").first.click()
        page.wait_for_selector("#detailModal", state="visible", timeout=3000)
        time.sleep(0.4)
        img2 = os.path.join(ARTIFACT_DIR, "06_modal_ranking_arguments_top1.png")
        page.screenshot(path=img2)
        print(f"[+] Screenshot 2 saved: {img2}")

        # 3. Close modal with Escape
        page.keyboard.press("Escape")
        time.sleep(0.3)

        # 4. Open #04 Stefanini (row 4) to capture its specific arguments
        page.locator(".data-table tbody tr").nth(3).click()
        page.wait_for_selector("#detailModal", state="visible", timeout=3000)
        time.sleep(0.4)
        img3 = os.path.join(ARTIFACT_DIR, "07_modal_stefanini_arguments.png")
        page.screenshot(path=img3)
        print(f"[+] Screenshot 3 saved: {img3}")

        # 5. Close modal and filter by Tier 5 (No TI / Operativas)
        page.keyboard.press("Escape")
        time.sleep(0.3)
        page.click("button[data-tier='TIER_5']")
        time.sleep(0.4)
        img4 = os.path.join(ARTIFACT_DIR, "08_tier5_non_tech_filter.png")
        page.screenshot(path=img4)
        print(f"[+] Screenshot 4 saved: {img4}")

        # 6. Open Detail for a Tier 5 to see why it was penalized and the "Peros"
        page.locator(".data-table tbody tr").first.click()
        page.wait_for_selector("#detailModal", state="visible", timeout=3000)
        time.sleep(0.4)
        img5 = os.path.join(ARTIFACT_DIR, "09_modal_tier5_penalization_arguments.png")
        page.screenshot(path=img5)
        print(f"[+] Screenshot 5 saved: {img5}")

        browser.close()

if __name__ == "__main__":
    capture_ranking_evidence()
