import asyncio
from playwright.async_api import async_playwright
import os

os.makedirs(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output", exist_ok=True)

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("Navigating to login...")
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        print("Filling credentials...")
        await page.fill("#tbLoginUsuario", "1074808317")
        await page.fill("#__tbPasswordUsuario", "C26D398F")

        print("Clicking ini_session_aprendiz...")
        await page.click("#ini_session_aprendiz")

        # Wait for navigation or change
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        current_url = page.url
        print(f"Current URL after login: {current_url}")
        print("Page title:", await page.title())

        await page.screenshot(path=r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\02_after_login.png", full_page=True)

        # Print all links, buttons and menu items
        links = await page.query_selector_all("a, button, input[type='submit']")
        print(f"\n--- Found {len(links)} interactive links/buttons ---")
        for idx, el in enumerate(links):
            text = (await el.inner_text()).strip()
            href = await el.get_attribute("href") or ""
            el_id = await el.get_attribute("id") or ""
            onclick = await el.get_attribute("onclick") or ""
            if text or href or el_id:
                print(f"[{idx}] id='{el_id}' text='{text}' href='{href}' onclick='{onclick}'")

        # Also let's dump the HTML body structure summary or iframes
        frames = page.frames
        print(f"\nTotal frames: {len(frames)}")
        for f in frames:
            print(f"Frame name='{f.name}' url='{f.url}'")

        await browser.close()

asyncio.run(test_login())
