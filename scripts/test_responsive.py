from playwright.sync_api import sync_playwright
import os

VIEWPORTS = [
    {"name": "mobile_small_360x640", "width": 360, "height": 640},
    {"name": "mobile_iphone13_390x844", "width": 390, "height": 844},
    {"name": "tablet_ipad_portrait_768x1024", "width": 768, "height": 1024},
    {"name": "tablet_ipad_landscape_1024x768", "width": 1024, "height": 768},
    {"name": "laptop_1280x585", "width": 1280, "height": 585},
    {"name": "desktop_1920x1080", "width": 1920, "height": 1080}
]

def test_all_viewports():
    os.makedirs("output/test_screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for vp in VIEWPORTS:
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            file_path = "file:///" + os.path.abspath("output/index.html").replace("\\", "/")
            page.goto(file_path)
            
            # Wait for either table row or card
            page.wait_for_selector(".data-table tbody tr, .clean-card", timeout=5000)
            
            # Screenshot directory
            page.screenshot(path=f"output/test_screenshots/{vp['name']}_dir.png")
            
            # Open Auth Modal
            page.click("[data-action='openAuthModal']")
            page.wait_for_selector("#authModal[style*='display: flex']", timeout=3000)
            page.screenshot(path=f"output/test_screenshots/{vp['name']}_auth.png")
            
            # Switch to guest tab
            page.click("[data-action='switchAuthTab'][data-tab='guest']")
            page.screenshot(path=f"output/test_screenshots/{vp['name']}_auth_guest.png")
            
            # Click guest login to authenticate and close modal
            page.click("[data-action='submitGuestLogin']")
            
            # Open detail modal on first item
            first_item = page.locator("[data-action='openDetailModal']").first
            first_item.click()
            
            page.wait_for_selector("#detailModal[style*='display: flex']", timeout=3000)
            page.screenshot(path=f"output/test_screenshots/{vp['name']}_modal.png")
            
            # Close modal
            page.click("[data-action='closeDetailModal']")
            
            print(f"Captured: {vp['name']}")
            page.close()
            
        browser.close()

if __name__ == "__main__":
    test_all_viewports()
