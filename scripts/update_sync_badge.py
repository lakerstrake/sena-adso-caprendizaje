#!/usr/bin/env python3
"""
================================================================================
SGVA SENA - Auto-Sync Badge Updater
================================================================================
Actualiza el badge de ultima sincronizacion GitHub -> Cloudflare en index.html
con la fecha y mensaje del ultimo commit de git.
Se ejecuta automaticamente antes de cada push (desde scripts/build.py).
================================================================================
"""
import os
import re
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(ROOT, "output", "index.html")

MONTH_ES = {
    1: "ene", 2: "feb", 3: "mar", 4: "abr",
    5: "may", 6: "jun", 7: "jul", 8: "ago",
    9: "sep", 10: "oct", 11: "nov", 12: "dic"
}

def get_last_commit():
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%ci"],
            cwd=ROOT, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None
        parts = result.stdout.strip().split("|", 2)
        if len(parts) < 3:
            return None
        commit_hash = parts[0][:7]
        commit_msg  = parts[1].strip()
        commit_date_str = parts[2].strip()[:19]
        dt = datetime.strptime(commit_date_str, "%Y-%m-%d %H:%M:%S")
        month = MONTH_ES[dt.month]
        friendly_date = f"{dt.day} {month} {dt.year}, {dt.hour:02d}:{dt.minute:02d}"
        return {"hash": commit_hash, "msg": commit_msg, "date": friendly_date}
    except Exception as e:
        print(f"[!] Error obteniendo commit: {e}")
        return None

def update_sync_badge(commit):
    if not os.path.exists(INDEX_HTML):
        print(f"[!] No se encontro {INDEX_HTML}")
        return False
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'(<span id="syncDate"[^>]*>)[^<]*(</span>)',
        rf'\g<1>{commit["date"]}\g<2>',
        content
    )
    msg = commit["msg"]
    if len(msg) > 60:
        msg = msg[:57] + "..."
    content = re.sub(
        r'(<span id="syncMsg"[^>]*>)\s*[^<]*\s*(</span>)',
        rf'\g<1>{msg}\g<2>',
        content, flags=re.DOTALL
    )
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(content)
    return True

def main():
    print("=" * 60)
    print(" AUTO-SYNC BADGE UPDATER -- GitHub -> Cloudflare")
    print("=" * 60)
    commit = get_last_commit()
    if not commit:
        print("[!] No se pudo obtener el ultimo commit.")
        sys.exit(1)
    print(f"[*] Ultimo commit: {commit['hash']} -- {commit['msg']}")
    print(f"[*] Fecha formateada: {commit['date']}")
    if update_sync_badge(commit):
        print(f"[OK] Badge actualizado en index.html")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
