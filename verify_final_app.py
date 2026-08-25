from playwright.sync_api import sync_playwright
import time
import os

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        file_path = "file:///" + os.path.abspath("output/index.html").replace("\\", "/")
        print("Navigating to clean SaaS dashboard:", file_path)
        
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda msg: errors.append(f"Console {msg.type}: {msg.text}") if msg.type == "error" else None)
        
        page.goto(file_path)
        page.wait_for_selector(".data-table tbody tr", timeout=5000)
        
        # 1. Capture clean table view
        page.screenshot(path="output/01_clean_table_view.png")
        print("1. Captured 01_clean_table_view.png")

        # 2. Test Tier Segment Filter
        page.click("text=Tier 1 · Software")
        time.sleep(0.3)
        page.screenshot(path="output/02_tier1_segment.png")
        print("2. Captured 02_tier1_segment.png")

        # 3. Open Detail Modal
        page.locator(".data-table tbody tr").first.click()
        page.wait_for_selector("#detailModal", state="visible", timeout=3000)
        time.sleep(0.3)
        page.screenshot(path="output/03_clean_modal_outreach.png")
        print("3. Captured 03_clean_modal_outreach.png")

        # Click Interview tab
        page.click("#mTabInterview")
        time.sleep(0.3)
        page.screenshot(path="output/04_clean_modal_interview.png")
        print("4. Captured 04_clean_modal_interview.png")

        # Click Career & Finances tab
        page.click("#mTabCareer")
        time.sleep(0.3)
        page.screenshot(path="output/05_clean_modal_career.png")
        print("5. Captured 05_clean_modal_career.png")

        # Close Modal
        page.click("button:has-text('Listo')")
        time.sleep(0.3)

        # 4. Test Side-by-Side Comparison
        checkboxes = page.locator(".data-table tbody tr input[type='checkbox']")
        checkboxes.nth(0).check()
        checkboxes.nth(1).check()
        time.sleep(0.3)
        page.click("text=Ver Comparativa")
        page.wait_for_selector("#compareModal", state="visible", timeout=3000)
        page.screenshot(path="output/06_clean_compare_modal.png")
        print("6. Captured 06_clean_compare_modal.png")

        browser.close()
        
        if errors:
            print("Errors detected:", errors)
        else:
            print("SUCCESS: 0 errors! Ultra-clean minimalist executive SaaS dashboard verified!")

if __name__ == "__main__":
    test_app()
