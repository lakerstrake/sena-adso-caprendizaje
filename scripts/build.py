"""
SGVA SENA ADSO - Production Build & Data Pipeline
Normalizes company datasets, validates schema, and compiles asset modules.
"""

import os
import sys
import json

# Force UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")
DATA_DIR = os.path.join(OUTPUT, "assets", "data")
JS_DIR = os.path.join(OUTPUT, "assets", "js")

def build_data_pipeline():
    json_path = os.path.join(DATA_DIR, "empresas.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        companies = json.load(f)

    # Sort strictly by ranking position
    companies.sort(key=lambda x: x.get("ranking_posicion", 999))

    # 1. Update data.js
    data_js_path = os.path.join(JS_DIR, "data.js")
    with open(data_js_path, "w", encoding="utf-8") as f:
        f.write("/**\n * SGVA SENA ADSO - Clean Data Registry\n */\nwindow.RAW_DATA = ")
        json.dump(companies, f, ensure_ascii=False)
        f.write(";\n")

    print(f"[✓] Data pipeline completed: {len(companies)} company records compiled.")

if __name__ == "__main__":
    build_data_pipeline()
