import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def test_login_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("1. Navigating to login page...")
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        print("2. Clicking '#aprendices' tab...")
        await page.click("#aprendices")
        await asyncio.sleep(1)

        print("3. Checking visible inputs after clicking '#aprendices'...")
        # Inspect visible inputs
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            vis = await inp.is_visible()
            inp_id = await inp.get_attribute("id") or ""
            inp_type = await inp.get_attribute("type") or ""
            inp_val = await inp.get_attribute("value") or ""
            placeholder = await inp.get_attribute("placeholder") or ""
            print(f"Input: id='{inp_id}' type='{inp_type}' val='{inp_val}' placeholder='{placeholder}' vis={vis}")

        print("4. Filling credentials for Aprendiz (1074808317 / C26D398F)...")
        await page.fill("#tbLoginUsuario", "1074808317")
        await page.fill("#__tbPasswordUsuario", "C26D398F")

        print("5. Clicking '#ini_session_aprendiz'...")
        await page.click("#ini_session_aprendiz")

        print("6. Waiting for navigation/response...")
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as e:
            print("Wait error:", e)

        await asyncio.sleep(4)

        current_url = page.url
        print(f"Current URL after login: {current_url}")
        print("Page title:", await page.title())

        await page.screenshot(path=r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\03_after_aprendiz_login.png", full_page=True)

        # Dump text / alerts / tables / navigation
        body_text = await page.inner_text("body")
        print("\n--- Body text snippet (first 1000 chars) ---")
        print(body_text[:1000])

        # Find all navigation links
        links = await page.query_selector_all("a, button, input[type='submit']")
        print(f"\n--- Links / Menus after login ({len(links)}) ---")
        for l in links:
            txt = (await l.inner_text()).strip()
            href = await l.get_attribute("href") or ""
            lid = await l.get_attribute("id") or ""
            if txt or "javascript" in href or "aspx" in href:
                print(f"Link: id='{lid}' text='{txt}' href='{href}'")

        await browser.close()

asyncio.run(test_login_flow())
