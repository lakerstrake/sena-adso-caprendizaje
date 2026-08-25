from playwright.sync_api import sync_playwright
import os

def test_light():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 600})
        file_path = "file:///" + os.path.abspath("output/index.html").replace("\\", "/")
        page.goto(file_path)
        page.click("#themeBtn")
        page.screenshot(path="output/01_light_clean_header.png")
        print("Captured light theme screenshot: output/01_light_clean_header.png")
        browser.close()

if __name__ == "__main__":
    test_light()
