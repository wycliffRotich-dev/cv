"""Regenerate assets/resume-preview.png (both pages side by side) from the built PDF."""
import os, subprocess, sys, tempfile, glob
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "Wycliffe_Kipleting_Rotich_Resume_Public.pdf")
OUT = os.path.join(ROOT, "assets", "resume-preview.png")

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["pdftoppm", "-png", "-r", "110", PDF, os.path.join(tmp, "p")], check=True)
    pages = [Image.open(f).convert("RGB") for f in sorted(glob.glob(os.path.join(tmp, "p-*.png")))][:2]
    a, b = pages[0], pages[-1]
    pad, gap = 40, 30
    W, H = a.width + b.width + gap + pad * 2, a.height + pad * 2
    bg = Image.new("RGB", (W, H), (238, 241, 247))
    for i, im in enumerate((a, b)):
        x, y = pad + i * (a.width + gap), pad
        sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((30, 38, 30 + im.width, 38 + im.height), fill=(10, 16, 32, 70))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        bg.paste(sh, (x - 30, y - 30), sh)
        bg.paste(im, (x, y))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bg.save(OUT, optimize=True)
    print("preview written:", OUT)
