import http.server
import socketserver
import threading
from playwright.sync_api import sync_playwright
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ARTIFACT_DIR = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\f64e925a-a1fa-4e35-b388-b9f016f83488"
PORT = 8884
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def start_server():
    os.chdir(os.path.join(ROOT, "output"))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        httpd.serve_forever()

def capture_mobile_scrolled():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        page = context.new_page()

        url = f"http://localhost:{PORT}/index.html"
        page.goto(url)
        page.wait_for_selector(".data-table tbody tr, .clean-card", timeout=8000)

        # Scroll to cards
        page.click("#btnLayoutCards")
        time.sleep(0.3)
        page.evaluate("window.scrollTo(0, 450)")
        time.sleep(0.3)
        img_cards_scrolled = os.path.join(ARTIFACT_DIR, "mobile_07_cards_scrolled.png")
        page.screenshot(path=img_cards_scrolled)
        print(f"[+] Cards Scrolled guardada: {img_cards_scrolled}")

        # Scroll more down
        page.evaluate("window.scrollTo(0, 950)")
        time.sleep(0.3)
        img_cards_deep = os.path.join(ARTIFACT_DIR, "mobile_08_cards_deep.png")
        page.screenshot(path=img_cards_deep)
        print(f"[+] Cards Deep guardada: {img_cards_deep}")

        browser.close()

if __name__ == "__main__":
    capture_mobile_scrolled()
