from bs4 import BeautifulSoup

with open(r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output\index_aprendiz.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("--- PAGE TITLE ---")
print(soup.title.string if soup.title else "No title")

print("\n--- ALL LINKS (<a>) ---")
for a in soup.find_all("a"):
    href = a.get("href", "")
    text = a.get_text(strip=True)
    a_id = a.get("id", "")
    a_class = a.get("class", "")
    print(f"Text: '{text}' | href: '{href}' | id: '{a_id}' | class: '{a_class}'")

print("\n--- ALL FORMS / BUTTONS / INPUTS ---")
for btn in soup.find_all(["button", "input"]):
    b_type = btn.get("type", "")
    val = btn.get("value", "")
    b_id = btn.get("id", "")
    txt = btn.get_text(strip=True)
    print(f"Tag: {btn.name} | type: '{b_type}' | id: '{b_id}' | value: '{val}' | text: '{txt}'")

print("\n--- MENUS / NAVS ---")
for nav in soup.find_all(["nav", "ul", "ol", "div"]):
    if "menu" in str(nav.get("class", "")).lower() or "nav" in str(nav.get("class", "")).lower():
        print(f"NAV/MENU [{nav.get('class')}]:")
        for item in nav.find_all("li"):
            print("  - ", item.get_text(strip=True), "| a-href:", item.find("a")["href"] if item.find("a") else "")
