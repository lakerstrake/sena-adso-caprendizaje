import asyncio
from playwright.async_api import async_playwright

async def debug_login():
    async with async_playwright() as p:
        # Launch with ignore_https_errors=True
        browser = await p.chromium.launch(
            headless=True,
            args=["--ignore-certificate-errors", "--disable-web-security"]
        )
        context = await browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        page.on("request", lambda r: print(f"[REQ] {r.method} {r.url}"))
        page.on("response", lambda r: print(f"[RES] {r.status} {r.url}"))
        page.on("requestfailed", lambda r: print(f"[REQ FAILED] {r.url} : {r.failure}"))
        page.on("dialog", lambda d: print(f"[DIALOG] {d.type}: {d.message}"))
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))

        print("Navigating to login...")
        await page.goto("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx", wait_until="networkidle")

        print("Clicking #aprendices...")
        await page.click("#aprendices")
        await asyncio.sleep(0.5)

        print("Filling credentials...")
        await page.fill("#tbLoginUsuario", "1074808317")
        await page.fill("#__tbPasswordUsuario", "C26D398F")

        print("Submitting login...")
        # Check form action
        form_action = await page.evaluate("() => document.forms[0] ? document.forms[0].action : 'No form'")
        print(f"Form action is: {form_action}")

        # Let's listen for navigation
        async with page.expect_navigation(timeout=30000) as nav_info:
            await page.click("#ini_session_aprendiz")

        print("Navigation finished!")
        await asyncio.sleep(3)
        print("Final URL:", page.url)
        print("Final Title:", await page.title())
        content = await page.content()
        print("Content length:", len(content))
        print("Content preview:\n", content[:1500])

        await page.screenshot(path=r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\04_debug_login.png", full_page=True)
        await browser.close()

asyncio.run(debug_login())
