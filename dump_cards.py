import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def dump_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')

        # Find where login buttons/forms are
        cards = soup.find_all(class_=lambda c: c and ('card' in c or 'login' in c.lower() or 'box' in c.lower() or 'col' in c.lower()))
        print("--- Relevant HTML sections ---")
        for card in cards[:15]:
            if 'aprendiz' in str(card).lower() or 'empresa' in str(card).lower():
                print("CARD/DIV:")
                print(card.prettify()[:1000])
                print("="*40)

        await browser.close()

asyncio.run(dump_html())
