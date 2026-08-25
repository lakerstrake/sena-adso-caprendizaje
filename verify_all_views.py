import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        file_path = os.path.abspath(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index.html")
        await page.goto(f"file:///{file_path}")
        await asyncio.sleep(0.8)
        
        out_dir = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output"
        
        # 1. Dark Cards
        await page.screenshot(path=os.path.join(out_dir, "01_dark_cards.png"), full_page=False)
        print("1. Captured 01_dark_cards.png")
        
        # 2. Dark Modal
        await page.click(".offer-card")
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "02_dark_modal.png"), full_page=False)
        print("2. Captured 02_dark_modal.png")
        
        # Close modal with escape key
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.3)
        
        # 3. Dark Table View
        await page.click("#btnTableView")
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "03_dark_table.png"), full_page=False)
        print("3. Captured 03_dark_table.png")
        
        # 4. Toggle Light Mode
        await page.click("#themeToggleBtn")
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "04_light_table.png"), full_page=False)
        print("4. Captured 04_light_table.png")
        
        # 5. Light Cards
        await page.click("#btnCardView")
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "05_light_cards.png"), full_page=False)
        print("5. Captured 05_light_cards.png")
        
        await browser.close()
        print("All screenshots captured successfully!")

asyncio.run(verify())
