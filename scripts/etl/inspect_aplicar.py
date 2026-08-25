import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    })

    # Step 1: Login page
    r = session.get("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx")
    soup = BeautifulSoup(r.text, "html.parser")
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
    viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"] if soup.find("input", {"id": "__VIEWSTATEGENERATOR"}) else ""

    # Step 2: Login post
    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategen,
        "__EVENTVALIDATION": eventvalidation,
        "tbLoginUsuario": "1074808317",
        "__tbPasswordUsuario": "C26D398F",
        "ini_session_aprendiz": "Iniciar sesión"
    }

    session.post(
        "https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx",
        data=payload,
        allow_redirects=False
    )
    return session

session = get_session()
print("Logged in. Fetching AplicarAprendiz.aspx...")
res_aplicar = session.get("https://caprendizaje.sena.edu.co/sgva/APRENDICES/pag/AplicarAprendiz.aspx")
print(f"Status: {res_aplicar.status_code}")
print(f"Final URL: {res_aplicar.url}")

with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\aplicar_aprendiz.html", "w", encoding="utf-8") as f:
    f.write(res_aplicar.text)

print("Saved aplicar_aprendiz.html")

# Let's inspect scripts and tables in AplicarAprendiz
soup = BeautifulSoup(res_aplicar.text, "html.parser")
tables = soup.find_all("table")
print(f"Found {len(tables)} tables")
for t in tables:
    t_id = t.get("id", "")
    t_class = t.get("class", "")
    rows = t.find_all("tr")
    print(f"Table id='{t_id}' class='{t_class}' rows={len(rows)}")
    for r in rows[:5]:
        cols = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        print("  ROW:", cols)

# Also check scripts for AJAX URLs, DataTables configs or ASP.NET postbacks
scripts = soup.find_all("script")
print(f"\nFound {len(scripts)} scripts. Searching for keywords...")
for s in scripts:
    content = s.string or ""
    if any(k in content.lower() for k in ["datatable", "ajax", "url:", "post", "get", "empresa", "aplicar", "solicitud"]):
        print("--- SCRIPT MATCH ---")
        print(content[:1500])
        print("="*40)
