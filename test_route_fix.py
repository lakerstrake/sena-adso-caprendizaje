import asyncio
from playwright.async_api import async_playwright

async def test_route_fix():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        context = await browser.new_context(ignore_https_errors=True)

        # Route interceptor to rewrite http://caprendizaje.sena.edu.co to https://
        async def handle_route(route):
            url = route.request.url
            if url.startswith("http://caprendizaje.sena.edu.co"):
                new_url = url.replace("http://caprendizaje.sena.edu.co", "https://caprendizaje.sena.edu.co")
                print(f"[REWRITE ROUTE] {url} -> {new_url}")
                # We can redirect the route or fetch with new url
                try:
                    response = await context.request.fetch(route.request, url=new_url)
                    await route.fulfill(response=response)
                except Exception as e:
                    print(f"Error fetching rewritten route: {e}")
                    await route.continue_()
            else:
                await route.continue_()

        page = await context.new_page()
        await page.route("**/*", handle_route)

        page.on("request", lambda r: print(f"[REQ] {r.method} {r.url}"))
        page.on("response", lambda r: print(f"[RES] {r.status} {r.url}"))

        print("Navigating to login...")
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        print("Clicking #aprendices...")
        await page.click("#aprendices")
        await asyncio.sleep(0.5)

        print("Filling credentials...")
        await page.fill("#tbLoginUsuario", "1074808317")
        await page.fill("#__tbPasswordUsuario", "C26D398F")

        print("Submitting login...")
        await page.click("#ini_session_aprendiz")

        print("Waiting for network idle...")
        await page.wait_for_load_state("networkidle", timeout=30000)
        await asyncio.sleep(4)

        print("Current URL:", page.url)
        print("Page Title:", await page.title())

        await page.screenshot(path=r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\05_logged_in.png", full_page=True)

        content = await page.content()
        print("Page content length:", len(content))
        with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\logged_in_page.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("Saved logged_in_page.html and 05_logged_in.png successfully!")

        await browser.close()

asyncio.run(test_route_fix())
