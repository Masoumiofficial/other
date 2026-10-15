#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_publish.py — ساخت نسخه قابل انتشار با نام فایل ASCII

چرا: نام فایل‌های فارسی در URL گیت‌هاب به‌صورت percent-encode در می‌آیند
(مثلا %D9%BE%D8%B1%D9%88%D9%BE...) که هم زشت است هم در پیام‌رسان‌ها می‌شکند.
این اسکریپت همان فایل‌ها را با نام کوتاه انگلیسی در build/publish/ کپی می‌کند
تا لینک مستقیم تمیز باشد، و دو بسته ZIP جداگانه می‌سازد:

  sajad-energytahvieh-employer-package.zip   <- فقط آنچه به کارفرما می‌دهید
  sajad-energytahvieh-full-package.zip       <- همه‌چیز، فقط برای خودتان

استفاده:  .venv/bin/python energy-tahvieh-proposal/build/make_publish.py
"""
import os
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
PUB = os.path.join(BUILD, "publish")

# نام ASCII -> (شماره سند، عنوان کوتاه)
SLUG = {
    "00": ("evidence-log", "سند شواهد"),
    "01": ("analysis-summary", "خلاصه تحلیل اولیه"),
    "02": ("proposal", "پروپوزال راهبردی (سند کارفرما)"),
    "03": ("internal-dossier", "سند محرمانه داخلی"),
    "04": ("negotiation-playbook", "راهنمای مذاکره"),
    "05": ("access-checklist", "چک‌لیست دسترسی‌ها"),
    "06": ("limitations", "فهرست محدودیت‌ها"),
}

# چه چیزی به کارفرما داده می‌شود — بقیه هرگز
EMPLOYER = ["02", "05", "06"]
ALL = ["02", "05", "06", "01", "00", "04", "03"]

sys.path.insert(0, BUILD)
from md2docx import DOCS  # noqa: E402


def main():
    if os.path.isdir(PUB):
        shutil.rmtree(PUB)
    os.makedirs(os.path.join(PUB, "assets", "fonts"), exist_ok=True)

    # فونت‌ها برای HTMLهای مستقل
    for f in os.listdir(os.path.join(BUILD, "assets", "fonts")):
        shutil.copy2(os.path.join(BUILD, "assets", "fonts", f),
                     os.path.join(PUB, "assets", "fonts", f))

    made = []
    for key in ALL:
        slug = SLUG[key][0]
        src_docx = os.path.join(ROOT, DOCS[key]["out"])
        src_html = src_docx.replace(".docx", ".html")
        for src, ext in ((src_docx, "docx"), (src_html, "html")):
            if not os.path.exists(src):
                print(f"MISS {src}")
                continue
            dst = os.path.join(PUB, f"{key}-{slug}.{ext}")
            shutil.copy2(src, dst)
            made.append(dst)

    # README بسته
    shutil.copy2(os.path.join(ROOT, "README.md"), os.path.join(PUB, "README.md"))

    # صفحه نخست با نام ASCII
    idx = os.path.join(BUILD, "index.html")
    if os.path.exists(idx):
        shutil.copy2(idx, os.path.join(PUB, "index.html"))

    # --- ZIP بسته کارفرما ---
    emp_zip = os.path.join(BUILD, "sajad-energytahvieh-employer-package.zip")
    with zipfile.ZipFile(emp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for key in EMPLOYER:
            slug = SLUG[key][0]
            for ext in ("docx", "html"):
                p = os.path.join(PUB, f"{key}-{slug}.{ext}")
                if os.path.exists(p):
                    z.write(p, f"{key}-{slug}.{ext}")
        for f in ("Vazirmatn-Regular.woff2", "Vazirmatn-Bold.woff2",
                  "Vazirmatn-ExtraBold.woff2", "OFL-Vazirmatn.txt"):
            src = os.path.join(PUB, "assets", "fonts", f)
            if os.path.exists(src):
                z.write(src, f"assets/fonts/{f}")

    # --- ZIP کامل ---
    full_zip = os.path.join(BUILD, "sajad-energytahvieh-full-package.zip")
    with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in made:
            z.write(p, os.path.basename(p))
        z.write(os.path.join(PUB, "README.md"), "README.md")
        if os.path.exists(os.path.join(PUB, "index.html")):
            z.write(os.path.join(PUB, "index.html"), "index.html")
        for f in os.listdir(os.path.join(PUB, "assets", "fonts")):
            z.write(os.path.join(PUB, "assets", "fonts", f), f"assets/fonts/{f}")

    print(f"\npublish/ : {len(made)} فایل")
    print(f"ZIP کارفرما : {os.path.getsize(emp_zip)/1024:.0f} KB -> {os.path.basename(emp_zip)}")
    print(f"ZIP کامل    : {os.path.getsize(full_zip)/1024:.0f} KB -> {os.path.basename(full_zip)}")


if __name__ == "__main__":
    main()
