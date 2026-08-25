import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
})

print("1. Fetching login page...")
r = session.get("https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx")
print(f"Status: {r.status_code}, Cookies: {session.cookies.get_dict()}")

soup = BeautifulSoup(r.text, "html.parser")
viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
viewstategen = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"] if soup.find("input", {"id": "__VIEWSTATEGENERATOR"}) else ""

print(f"VIEWSTATE len: {len(viewstate)}, EVENTVALIDATION len: {len(eventvalidation)}")

# Post payload for Aprendiz login
payload = {
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewstategen,
    "__EVENTVALIDATION": eventvalidation,
    "tbLoginUsuario": "1074808317",
    "__tbPasswordUsuario": "C26D398F",
    "ini_session_aprendiz": "Iniciar sesión"
}

print("2. Posting login payload...")
# Do not follow redirects automatically so we can inspect the Location header and rewrite to HTTPS
post_res = session.post(
    "https://caprendizaje.sena.edu.co/sgva/SGVA_Diseno/pag/login.aspx",
    data=payload,
    allow_redirects=False
)

print(f"Post status: {post_res.status_code}")
print(f"Headers: {dict(post_res.headers)}")
print(f"Cookies after post: {session.cookies.get_dict()}")

location = post_res.headers.get("Location")
print(f"Redirect Location: {location}")

if location:
    if location.startswith("http://"):
        location = location.replace("http://", "https://")
    elif location.startswith("/"):
        location = "https://caprendizaje.sena.edu.co" + location

    print(f"Fetching redirect destination: {location}")
    res_index = session.get(location)
    print(f"Index status: {res_index.status_code}")
    print(f"Index final URL: {res_index.url}")
    print(f"Index content snippet:\n{res_index.text[:2000]}")

    with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index_aprendiz.html", "w", encoding="utf-8") as f:
        f.write(res_index.text)
    print("Saved index_aprendiz.html successfully!")
else:
    print("No redirect Location header found! Response text:")
    print(post_res.text[:1000])
