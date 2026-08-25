import asyncio
from playwright.async_api import async_playwright

async def dump_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        # Get all visible buttons and links
        buttons = await page.query_selector_all("button, a, input[type='button'], input[type='submit'], .btn, [role='button']")
        print("--- All interactive buttons/links ---")
        for b in buttons:
            txt = (await b.inner_text()).strip()
            val = await b.get_attribute("value") or ""
            b_id = await b.get_attribute("id") or ""
            b_cls = await b.get_attribute("class") or ""
            vis = await b.is_visible()
            print(f"Tag={await b.evaluate('e => e.tagName')} id='{b_id}' class='{b_cls}' text='{txt}' val='{val}' vis={vis}")

        await browser.close()

asyncio.run(dump_form())
