"""
================================================================================
SGVA SENA ADSO - End-to-End Zero-Trust Security & UI Penetration Testing
================================================================================
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run_e2e_security_tests():
    print("=" * 80)
    print(" EJECUTANDO PRUEBAS E2E DE INTERFAZ & PENETRACIÓN (PLAYWRIGHT)")
    print("=" * 80)

    html_file = os.path.abspath("output/index.html").replace("\\", "/")
    file_url = f"file:///{html_file}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on("console", lambda msg: print(f"    [BROWSER CONSOLE] {msg.text}"))
        page.on("pageerror", lambda err: print(f"    [BROWSER ERROR] {err}"))

        # Clear any prior storage and load fresh
        page.goto(file_url)
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        page.goto(file_url)
        page.wait_for_load_state("domcontentloaded")

        # ----------------------------------------------------------------------
        # TEST 1: Default Guest Mode on Initial Load (Public Exploration Access)
        # ----------------------------------------------------------------------
        print("\n[+] Test 1: Verificando Ingreso por Defecto en Modo Invitado (Exploración Inmediata)...")
        time.sleep(0.5)
        is_modal_hidden = page.is_hidden("#authModal")
        is_dir_visible = page.is_visible("#sectionDirectory")
        user_badge = page.inner_text("#lblSessionUser")
        cand_name = page.inner_text("#navCandidateName")
        print(f"    - Modal de Acceso Oculto Inicialmente: {is_modal_hidden}")
        print(f"    - Directorio de Vacantes Visible Inmediato: {is_dir_visible}")
        print(f"    - Estado de Sesión en Header: '{user_badge}'")
        print(f"    - Nombre en Header Público: '{cand_name}'")
        assert is_modal_hidden, "ERROR: La página debe entrar directamente sin modal bloqueante."
        assert is_dir_visible, "ERROR: El directorio debe ser visible de inmediato en Modo Invitado."
        assert "Invitado" in user_badge, "ERROR: Debe iniciar por defecto en Modo Invitado."
        print("    [PASS] Ingreso inmediato en Modo Invitado por defecto verificado al 100%.")

        # ----------------------------------------------------------------------
        # TEST 2: Open Auth Modal & Rejection of Invalid Credentials
        # ----------------------------------------------------------------------
        print("\n[+] Test 2: Probando Apertura de Modal y Rechazo de Credenciales Inválidas...")
        page.click("#btnAuthTrigger")
        time.sleep(0.3)
        assert page.is_visible("#authModal"), "ERROR: Clic en el badge de invitado debe abrir el modal de autenticación."

        page.fill("#tbLoginUser", "hacker")
        page.fill("#tbLoginPass", "wrong_pin_123")
        page.click("#btnSubmitLogin")
        time.sleep(0.3)

        alert_text = page.inner_text("#authAlertText")
        print(f"    - Mensaje de Alerta: '{alert_text}'")
        assert "Credenciales" in alert_text or "inválidas" in alert_text, f"Esperaba mensaje de error, obtuve: {alert_text}"
        print("    [PASS] Intruso rechazado con éxito.")

        # ----------------------------------------------------------------------
        # TEST 3: Successful Master Authentication & Full UI Unlocking
        # ----------------------------------------------------------------------
        print("\n[+] Test 3: Probando Elevación a Modo Titular (Juan Manuel Lagos)...")
        page.fill("#tbLoginUser", "admin")
        page.fill("#tbLoginPass", "adso2026")
        page.click("#btnSubmitLogin")
        time.sleep(0.5)

        is_modal_hidden = page.is_hidden("#authModal")
        is_dir_visible = page.is_visible("#sectionDirectory")
        user_badge = page.inner_text("#lblSessionUser")
        cand_name = page.inner_text("#navCandidateName")
        cand_links_visible = page.is_visible("#navCandidateLinks")
        is_timer_visible = page.is_visible("#lblSessionTimer")
        timer_text = page.inner_text("#lblSessionTimer")

        print(f"    - Modal Oculto tras Login: {is_modal_hidden}")
        print(f"    - Directorio Visible: {is_dir_visible}")
        print(f"    - Estado de Sesión en Header: '{user_badge}'")
        print(f"    - Nombre del Titular en Header: '{cand_name}'")
        print(f"    - Enlaces Privados Visibles: {cand_links_visible}")
        print(f"    - Temporizador de Sesión: '{timer_text}' (Visible: {is_timer_visible})")
        
        assert is_modal_hidden, "ERROR: El modal debe cerrarse tras login exitoso."
        assert is_dir_visible, "ERROR: El directorio debe desbloquearse."
        assert "Juan Manuel" in user_badge or "Titular" in user_badge, "ERROR: El badge debe mostrar el nombre del titular."
        banner_links_visible = page.is_visible("#candidateBanner a[href*='drive.google.com']")
        assert banner_links_visible, "ERROR: Los enlaces del titular deben ser visibles en modo Titular."
        assert is_timer_visible, "ERROR: El temporizador de sesión activa debe ser visible."
        print("    [PASS] Titular autenticado con datos completos y temporizador activo.")

        # Test Master Outreach Privacy Content
        page.click("button[data-action='openDetailModal']")
        time.sleep(0.3)
        outreach_text = page.inner_text("#mOutreachBody")
        assert "Juan Manuel" in outreach_text, "ERROR: En modo Titular la carta debe contener los datos reales del titular."
        page.click("button[data-action='closeDetailModal']")
        time.sleep(0.2)
        print("    [PASS] Cartas de postulación personalizadas para el Titular.")

        # ----------------------------------------------------------------------
        # TEST 4: Instant Secure Logout & Return to Guest Mode
        # ----------------------------------------------------------------------
        print("\n[+] Test 4: Probando Cierre de Sesión Seguro y Retorno a Modo Invitado...")
        page.click("#btnAuthTrigger")
        time.sleep(0.3)
        user_badge_after = page.inner_text("#lblSessionUser")
        print(f"    - Estado de Sesión tras Logout: '{user_badge_after}'")
        assert "Invitado" in user_badge_after, "ERROR: Tras logout debe volver a Modo Invitado."
        assert page.is_visible("#sectionDirectory"), "ERROR: El directorio debe permanecer visible para exploración pública."
        print("    [PASS] Cierre de sesión ejecutado con retorno inmediato a Modo Invitado.")

        # ----------------------------------------------------------------------
        # TEST 5: Guest / Public Mode & Strict Data Privacy Masking
        # ----------------------------------------------------------------------
        print("\n[+] Test 5: Probando Modo Invitado / Evaluador (Protección y Enmascaramiento de Datos)...")
        guest_dir_visible = page.is_visible("#sectionDirectory")
        guest_user_badge = page.inner_text("#lblSessionUser")
        guest_cand_name = page.inner_text("#navCandidateName")
        guest_cand_links_hidden = page.is_hidden("#navCandidateLinks")

        print(f"    - Directorio Visible: {guest_dir_visible}")
        print(f"    - Estado de Sesión: '{guest_user_badge}'")
        print(f"    - Nombre en Header Público: '{guest_cand_name}'")
        print(f"    - Enlaces Privados Ocultos: {guest_cand_links_hidden}")

        assert guest_dir_visible, "ERROR: El directorio debe ser visible para invitados."
        assert "Invitado" in guest_user_badge or "Público" in guest_user_badge, "ERROR: El badge debe indicar Modo Invitado."
        assert "Juan Manuel Lagos" not in guest_cand_name, "ERROR: En modo Invitado el nombre no debe ser expuesto en el header."
        assert guest_cand_links_hidden, "ERROR: En modo Invitado los enlaces privados deben estar ocultos."
        print("    [PASS] Modo Invitado activo con datos del titular 100% ocultos en navegación.")

        # Test Guest Outreach Privacy Masking
        page.click("button[data-action='openDetailModal']")
        time.sleep(0.3)
        guest_outreach = page.inner_text("#mOutreachBody")
        print(f"    - Muestra de Carta en Modo Invitado: {guest_outreach[:100]}...")
        assert "Juan Manuel Lagos" not in guest_outreach, "ERROR: Datos privados expuestos en carta para invitados."
        assert "300 727 9875" not in guest_outreach, "ERROR: Teléfono privado expuesto en carta para invitados."
        assert "jmlagos2003@gmail.com" not in guest_outreach, "ERROR: Correo privado expuesto en carta para invitados."
        page.click("button[data-action='closeDetailModal']")
        time.sleep(0.2)
        print("    [PASS] Privacidad y enmascaramiento RBAC verificado al 100%.")
        assert "Juan Manuel" not in guest_cand_name, "ERROR: No deben aparecer datos personales en el header en modo invitado."
        assert guest_cand_links_hidden, "ERROR: Los enlaces personales (CV Drive, LinkedIn, GitHub) deben estar 100% ocultos en modo invitado."
        print("    [PASS] Modo Invitado activo con datos del titular 100% ocultos en navegación.")

        # Test Guest Outreach Privacy Masking (No PII leaks)
        page.click("button[data-action='openDetailModal']")
        time.sleep(0.3)
        guest_outreach_text = page.inner_text("#mOutreachBody")
        print(f"    - Muestra de Carta en Modo Invitado: {guest_outreach_text[:120]}...")
        assert "Juan Manuel" not in guest_outreach_text, "ERROR CRÍTICO: El nombre del titular no debe filtrarse en modo invitado."
        assert "jmlagos2003" not in guest_outreach_text, "ERROR CRÍTICO: El correo privado no debe filtrarse en modo invitado."
        assert "300 727" not in guest_outreach_text, "ERROR CRÍTICO: El teléfono privado no debe filtrarse en modo invitado."
        assert "[Nombre del Aprendiz]" in guest_outreach_text, "ERROR: Debe mostrarse el placeholder genérico [Nombre del Aprendiz]."
        page.click("button[data-action='closeDetailModal']")
        time.sleep(0.2)
        print("    [PASS] Privacidad y enmascaramiento RBAC verificado al 100%.")

        # ----------------------------------------------------------------------
        # TEST 6: Open & Close Auth Modal from Guest Mode
        # ----------------------------------------------------------------------
        print("\n[+] Test 6: Probando Apertura de Modal de Acceso desde Modo Invitado...")
        page.click("#btnAuthTrigger")
        time.sleep(0.3)
        assert page.is_visible("#authModal"), "ERROR: El modal de acceso debe abrirse al hacer clic en el badge de invitado."
        page.click("button[data-action='closeAuthModal']")
        time.sleep(0.2)
        assert page.is_hidden("#authModal"), "ERROR: El modal debe cerrarse correctamente."
        print("    [PASS] Modal de acceso y conmutación de roles verificado con éxito.")

        browser.close()

    print("\n" + "=" * 80)
    print(" TODAS LAS PRUEBAS E2E DE SEGURIDAD & PRIVACIDAD PASARON CON ÉXITO (100% OK)")
    print("================================================================================")

if __name__ == "__main__":
    run_e2e_security_tests()
