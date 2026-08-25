import asyncio
from playwright.async_api import async_playwright
import os

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        
        path = os.path.abspath(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index.html")
        await page.goto(f"file:///{path}")
        await page.wait_for_selector("#tableBody tr")
        
        print("Clicking row...")
        await page.locator("#tableBody tr").first.click()
        
        modal_visible = await page.is_visible("#detailModal")
        print(f"Modal visible after tr click: {modal_visible}")
        
        await page.keyboard.press("Escape")
        print("Closing modal...")
        
        print("Clicking .btn-open-detail...")
        btn = page.locator(".btn-open-detail").first
        await btn.click()
        
        modal_visible_btn = await page.is_visible("#detailModal")
        print(f"Modal visible after .btn-open-detail click: {modal_visible_btn}")
        
        if errors:
            print("Errors detected:", errors)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())
