import shutil
import os

src_dir = r"C:\Users\USER PC\.gemini\antigravity-ide\scratch\sena_caprendizaje\output"
dst_dir = r"C:\Users\USER PC\.gemini\antigravity-ide\brain\ffde248b-3297-4c4e-ad1d-d22d8f4e653c"

for fname in ["dashboard_preview.png", "modal_preview.png"]:
    s = os.path.join(src_dir, fname)
    d = os.path.join(dst_dir, fname)
    if os.path.exists(s):
        shutil.copy2(s, d)
        print(f"Copied {fname} to artifacts.")
