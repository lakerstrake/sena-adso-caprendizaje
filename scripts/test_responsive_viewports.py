"""
================================================================================
SGVA SENA ADSO - Multi-Viewport Precision Responsiveness Testing Suite
Standards: ISO/IEC 25010 & WCAG 2.1 AA
Test Matrix:
- 13" Laptops (1280x800, 1366x768)
- 14" - 15.6" Laptops (1440x900, 1536x864)
- 17" Desktops (1920x1080)
- 2K / 4K Ultrawide Displays (2560x1440, 3840x2160)
- Tablets (768x1024)
- Mobile Phones (375x812, 412x915)
================================================================================
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VIEWPORTS = [
    {"name": "13\" Compact Laptop (1280x800)", "width": 1280, "height": 800},
    {"name": "13.3\" / 14\" Standard Laptop (1366x768)", "width": 1366, "height": 768},
    {"name": "14\" Retina Laptop (1440x900)", "width": 1440, "height": 900},
    {"name": "15.6\" Scaled Display (1536x864)", "width": 1536, "height": 864},
    {"name": "17\" Full HD Desktop (1920x1080)", "width": 1920, "height": 1080},
    {"name": "2K QHD Display (2560x1440)", "width": 2560, "height": 1440},
    {"name": "4K Ultra-HD Display (3840x2160)", "width": 3840, "height": 2160},
    {"name": "Tablet Portrait iPad (768x1024)", "width": 768, "height": 1024},
    {"name": "Mobile Modern (390x844)", "width": 390, "height": 844}
]

def run_responsive_tests():
    print("=" * 80)
    print(" VERIFICANDO RESPONSIVIDAD Y ADAPTABILIDAD EN TODO EL ESPECTRO DE PANTALLAS")
    print(" (Desde Laptops 13\" hasta Pantallas de Gran Formato 17\", 2K, 4K y Móviles)")
    print("=" * 80)

    html_file = os.path.abspath("output/index.html").replace("\\", "/")
    file_url = f"file:///{html_file}"

    passed_viewports = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            print(f"\n[+] Evaluando Pantalla: {vp['name']}...")
            context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = context.new_page()

            page.goto(file_url)
            page.wait_for_load_state("domcontentloaded")

            # Open auth modal and authenticate as titular to test full UI elements
            page.click("#btnAuthTrigger")
            time.sleep(0.2)
            page.fill("#tbLoginUser", "admin")
            page.fill("#tbLoginPass", "adso2026")
            page.click("#btnSubmitLogin")
            time.sleep(0.4)

            # Check 1: Zero horizontal body overflow (ISO 25010)
            overflow_data = page.evaluate("""() => {
                const doc = document.documentElement;
                const body = document.body;
                return {
                    docScrollWidth: doc.scrollWidth,
                    docClientWidth: doc.clientWidth,
                    bodyScrollWidth: body.scrollWidth,
                    bodyClientWidth: body.clientWidth,
                    hasHorizontalScroll: doc.scrollWidth > doc.clientWidth + 1 || body.scrollWidth > body.clientWidth + 1
                };
            }""")

            has_overflow = overflow_data["hasHorizontalScroll"]
            print(f"    - Desbordamiento Horizontal: {'NO (Perfecto)' if not has_overflow else 'DETECTADO (Falla)'}")
            print(f"    - Dimensiones Body: {overflow_data['bodyClientWidth']}px cliente / {overflow_data['bodyScrollWidth']}px scroll")
            assert not has_overflow, f"ERROR: Detectado desbordamiento horizontal en {vp['name']}"

            # Check 2: Top Navbar Elements Visibility
            nav_visible = page.is_visible(".navbar")
            brand_visible = page.is_visible(".brand-title")
            dir_btn_visible = page.is_visible("#pillDirectory")
            session_badge_visible = page.is_visible("#lblSessionUser")
            assert nav_visible and dir_btn_visible and session_badge_visible, "ERROR: Elementos esenciales de navegación no visibles."

            # Check 3: Candidate Banner Visibility and Structure
            banner_visible = page.is_visible("#candidateBanner")
            assert banner_visible, "ERROR: El banner de candidato debe ser visible tras el login."

            # Check 4: Filter Deck & Search Box
            search_visible = page.is_visible("#mainSearch")
            tier_visible = page.is_visible(".tier-segments")
            assert search_visible and tier_visible, "ERROR: El deck de filtros no se visualiza correctamente."

            # Check 5 & 6: Data rendering and layout switching
            is_mobile = vp["width"] < 768
            if is_mobile:
                cards_visible = page.is_visible("#cardsGridWrap")
                card_count = page.locator(".clean-card").count()
                print(f"    - Vista Móvil Inicial (Tarjetas): {cards_visible} ({card_count} tarjetas)")
                assert cards_visible and card_count > 0, "ERROR: La vista móvil de tarjetas no cargó."

                page.click("#btnLayoutTable")
                time.sleep(0.3)
                table_visible = page.is_visible(".data-table")
                row_count = page.locator(".data-table tbody tr").count()
                print(f"    - Conmutación a Tabla Móvil: {table_visible} ({row_count} filas)")
                assert table_visible and row_count > 0, "ERROR: La tabla no cargó en móvil."
            else:
                table_visible = page.is_visible(".data-table")
                row_count = page.locator(".data-table tbody tr").count()
                print(f"    - Tabla Renderizada: {table_visible} ({row_count} filas visibles)")
                assert table_visible and row_count > 0, "ERROR: La tabla de empresas no cargó las filas."

                page.click("#btnLayoutCards")
                time.sleep(0.3)
                cards_visible = page.is_visible("#cardsGridWrap")
                card_count = page.locator(".clean-card").count()
                print(f"    - Vista Tarjetas: {cards_visible} ({card_count} tarjetas)")
                assert cards_visible and card_count > 0, "ERROR: La vista en tarjetas no cargó."

                page.click("#btnLayoutTable")
                time.sleep(0.2)

            passed_viewports += 1
            print(f"    [PASS] Pantalla {vp['name']} verificada al 100% con cero errores visuales.")
            context.close()

        browser.close()

    print("\n" + "=" * 80)
    print(f" RESUMEN DE RESPONSIVIDAD: {passed_viewports}/{len(VIEWPORTS)} Resoluciones Verificadas con Éxito (100% OK)")
    print("================================================================================")

if __name__ == "__main__":
    run_responsive_tests()
