#!/usr/bin/env python3
"""
SGVA SENA - Tri-Sync Badge Updater
Actualiza el panel de sincronizacion triple (SGVA, GitHub, Cloudflare) en index.html.
"""
import os
import re
import subprocess
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(ROOT, "output", "index.html")
DATA_JSON  = os.path.join(ROOT, "output", "assets", "data", "empresas.json")

MONTH_ES = {1:"ene",2:"feb",3:"mar",4:"abr",5:"may",6:"jun",
            7:"jul",8:"ago",9:"sep",10:"oct",11:"nov",12:"dic"}

def fmt_date(dt):
    return f"{dt.day} {MONTH_ES[dt.month]} {dt.year}, {dt.hour:02d}:{dt.minute:02d}"

def get_last_commit():
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%ci"],
            cwd=ROOT, capture_output=True, text=True, timeout=10
        )
        parts = result.stdout.strip().split("|", 2)
        if len(parts) < 3:
            return None
        dt = datetime.strptime(parts[2].strip()[:19], "%Y-%m-%d %H:%M:%S")
        msg = parts[1].strip()
        if len(msg) > 55:
            msg = msg[:52] + "..."
        return {"hash": parts[0][:7], "msg": msg, "date": fmt_date(dt), "cf_date": f"{fmt_date(dt).rsplit(',',1)[0]}, ~{dt.hour:02d}:{dt.minute+2:02d}"}
    except Exception as e:
        print(f"[!] Git error: {e}")
        return None

def get_sgva_info():
    try:
        stat = os.stat(DATA_JSON)
        dt = datetime.fromtimestamp(stat.st_mtime)
        with open(DATA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data)
        return {"date": fmt_date(dt), "count": count}
    except Exception as e:
        print(f"[!] SGVA data error: {e}")
        return {"date": "N/A", "count": 0}

def replace_id(content, elem_id, new_text):
    pattern = rf'(<[^>]+\bid="{elem_id}"[^>]*>)[^<]*(</)'
    return re.sub(pattern, rf'\g<1>{new_text}\g<2>', content)

def update_panel(commit, sgva):
    if not os.path.exists(INDEX_HTML):
        print(f"[!] No se encontro {INDEX_HTML}")
        return False
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # GitHub row
    content = replace_id(content, "syncDate", commit["date"])
    content = replace_id(content, "syncHash", commit["hash"])
    content = re.sub(
        r'(<[^>]+\bid="syncMsg"[^>]*>)\s*[^<]*\s*(</)',
        rf'\g<1>{commit["msg"]}\g<2>',
        content, flags=re.DOTALL
    )

    # SGVA row
    content = replace_id(content, "sgvaDate", sgva["date"])
    content = re.sub(
        r'(<[^>]+\bid="sgvaMsg"[^>]*>)\s*[^<]*\s*(</)',
        rf'\g<1>Multi-AI Engine v2 — {sgva["count"]} vacantes procesadas\g<2>',
        content, flags=re.DOTALL
    )

    # Cloudflare row (commit time + ~2min deploy lag)
    content = replace_id(content, "cfDate", commit["cf_date"])

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    return True

def main():
    print("=" * 60)
    print(" TRI-SYNC BADGE UPDATER -- SGVA | GitHub | Cloudflare")
    print("=" * 60)
    commit = get_last_commit()
    sgva   = get_sgva_info()
    if not commit:
        print("[!] No se pudo obtener commit de git.")
        sys.exit(1)
    print(f"[*] GitHub:     {commit['hash']} — {commit['date']}")
    print(f"[*] SGVA ETL:   {sgva['date']} — {sgva['count']} vacantes")
    print(f"[*] Cloudflare: {commit['cf_date']} (auto-deploy)")
    if update_panel(commit, sgva):
        print(f"[OK] Panel de sincronizacion actualizado en index.html")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
