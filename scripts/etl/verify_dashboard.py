import asyncio
from playwright.async_api import async_playwright
import os

async def screenshot_dashboard():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        file_path = os.path.abspath(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index.html")
        await page.goto(f"file:///{file_path}")
        await asyncio.sleep(1)
        
        screenshot_path = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\dashboard_preview.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print("Captured dashboard screenshot successfully!")
        
        # Test modal
        await page.click(".offer-card")
        await asyncio.sleep(0.5)
        screenshot_modal = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\modal_preview.png"
        await page.screenshot(path=screenshot_modal, full_page=False)
        print("Captured modal screenshot successfully!")
        
        await browser.close()

asyncio.run(screenshot_dashboard())
