import asyncio
from playwright.async_api import async_playwright
import os

os.makedirs(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output", exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("Navigating to login page...")
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")
        await page.screenshot(path=r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\01_login_page.png")
        print("Page title:", await page.title())

        # Inspect all inputs and selects
        inputs = await page.query_selector_all("input, select, button, a")
        print(f"Found {len(inputs)} interactive elements on login page.")
        for el in inputs:
            tag = await el.evaluate("el => el.tagName")
            el_id = await el.get_attribute("id") or ""
            name = await el.get_attribute("name") or ""
            el_type = await el.get_attribute("type") or ""
            text = (await el.inner_text()).strip() if tag == "A" or tag == "BUTTON" else ""
            value = await el.get_attribute("value") or ""
            if el_id or name or text:
                print(f"[{tag}] id='{el_id}' name='{name}' type='{el_type}' text='{text}' value='{value}'")

        selects = await page.query_selector_all("select")
        for s in selects:
            s_id = await s.get_attribute("id")
            options = await s.query_selector_all("option")
            opt_texts = [f"{(await opt.get_attribute('value'))}: {(await opt.inner_text()).strip()}" for opt in options]
            print(f"Select {s_id} options: {opt_texts}")

        await browser.close()

asyncio.run(run())
