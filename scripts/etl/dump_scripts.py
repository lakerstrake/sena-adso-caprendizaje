from bs4 import BeautifulSoup

with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\aplicar_aprendiz.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

scripts = soup.find_all("script")
for idx, s in enumerate(scripts):
    src = s.get("src", "")
    content = s.string or ""
    print(f"=== SCRIPT #{idx} (src='{src}') ===")
    if content:
        print(content)
