import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

html_file = os.path.abspath("output/index.html").replace("\\", "/")
file_url = f"file:///{html_file}"
out_dir = os.path.abspath("C:/Users/USER PC/.gemini/antigravity-ide/brain/23325202-d426-4fc1-afd3-954b0cfbf0cd/.tempmediaStorage").replace("\\", "/")
os.makedirs(out_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 1. Desktop 1080p - Default Guest Mode
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto(file_url)
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.goto(file_url)
    time.sleep(0.5)
    page.screenshot(path=f"{out_dir}/sgva_default_guest_mode.png")
    print(f"[✓] Saved: {out_dir}/sgva_default_guest_mode.png")

    # 2. Auth Modal
    page.click("#btnAuthTrigger")
    time.sleep(0.3)
    page.screenshot(path=f"{out_dir}/sgva_auth_modal.png")
    print(f"[✓] Saved: {out_dir}/sgva_auth_modal.png")

    # 3. Titular Mode
    page.fill("#tbLoginUser", "admin")
    page.fill("#tbLoginPass", "adso2026")
    page.click("#btnSubmitLogin")
    time.sleep(0.5)
    page.screenshot(path=f"{out_dir}/sgva_titular_elevated_mode.png")
    print(f"[✓] Saved: {out_dir}/sgva_titular_elevated_mode.png")

    # 4. Detail & Outreach with Clean CV Button
    page.click("button[data-action='openDetailModal']")
    time.sleep(0.4)
    page.screenshot(path=f"{out_dir}/sgva_outreach_cv_clean.png")
    print(f"[✓] Saved: {out_dir}/sgva_outreach_cv_clean.png")

    browser.close()
