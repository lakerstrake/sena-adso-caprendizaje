from playwright.sync_api import sync_playwright
import os

def test_viewport():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Exact user viewport: 1280x585
        page = browser.new_page(viewport={"width": 1280, "height": 585})
        file_path = "file:///" + os.path.abspath("output/index.html").replace("\\", "/")
        page.goto(file_path)
        page.wait_for_selector(".data-table tbody tr", timeout=5000)
        
        # Test dark
        page.screenshot(path="output/test_1280x585_dark.png")
        print("Captured dark 1280x585 screenshot")
        
        # Test light
        page.click("#themeBtn")
        page.screenshot(path="output/test_1280x585_light.png")
        print("Captured light 1280x585 screenshot")
        
        browser.close()

if __name__ == "__main__":
    test_viewport()
