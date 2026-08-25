import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        # Let's find all buttons, tabs, spans, divs with text 'Aprendiz' or role
        elements = await page.query_selector_all("button, a, div, span, li, input")
        for el in elements:
            txt = (await el.inner_text()).strip() if await el.evaluate("el => el.children.length === 0") else ""
            tag = await el.evaluate("el => el.tagName")
            el_id = await el.get_attribute("id") or ""
            el_class = await el.get_attribute("class") or ""
            if "aprendiz" in txt.lower() or "aprendiz" in el_id.lower() or "aprendiz" in el_class.lower():
                is_visible = await el.is_visible()
                print(f"[{tag}] id='{el_id}' class='{el_class}' text='{txt}' visible={is_visible}")

        await browser.close()

asyncio.run(inspect())
