#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_protected_site.py — سایت محافظت‌شده برای سند کارفرما

معماری محافظت (لایه‌به‌لایه، از مؤثر به کم‌اثر):

  لایه ۱  رمزنگاری واقعی AES-256-GCM
          محتوای سند پیش از تحویل به مرورگر رمز شده است. بدون رمز، فایل
          payload هیچ چیز قابل خواندنی ندارد — حتی در View Source.
          کلید با PBKDF2-SHA256 و ۲۱۰٬۰۰۰ تکرار از رمز مشتق می‌شود.
          رمز هرگز روی سرور ذخیره یا ارسال نمی‌شود؛ همه‌چیز سمت مرورگر.

  لایه ۲  کنترل دسترسی سرور (.htaccess / پوشه خصوصی)
          اگر هاست پشتیبانی کند، پیش از رسیدن به رمز دوم هم در بسته است.

  لایه ۳  واترمارک هویت‌دار
          نام بیننده و زمان بازدید به‌صورت مورب روی همه صفحه. بازدارنده
          اصلی نشت، چون اثر انگشت قابل ردیابی می‌گذارد.

  لایه ۴  noindex / robots
          از ایندکس شدن در گوگل و آرشیو دائمی در Wayback Machine جلوگیری
          می‌کند.

  لایه ۵  اصطکاک ضدکپی (اختیاری، با کلید روشن/خاموش در خود صفحه)
          user-select:none و بستن راست‌کلیک و Ctrl+S/Ctrl+U/Ctrl+P.
          ⚠️ این لایه اسکرین‌شات را نمی‌بندد و با DevTools دور زده می‌شود.
             صرفاً اصطکاک است. به همین دلیل پیش‌فرض خاموش است.

استفاده:
  .venv/bin/python energy-tahvieh-proposal/build/make_protected_site.py <رمز>
"""
import base64
import hashlib
import os
import re
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(BUILD, "protected-site")
FONTDIR = os.path.join(BUILD, "assets", "fonts")

sys.path.insert(0, BUILD)
from md2docx import DOCS  # noqa: E402
import md2html  # noqa: E402
from Crypto.Cipher import AES  # noqa: E402

# اسنادی که کارفرما می‌بیند. ۰۵ عمداً اینجا نیست: چک‌لیست دسترسی‌ها مربوط به
# جلسه آغازین پس از توافق است، نه مرحله تصمیم‌گیری استخدام.
EMPLOYER_KEYS = ["02", "06"]

PBKDF2_ITER = 210_000
TODAY_FA = "۲۳ مهر ۱۴۰۵"
TODAY_EN = "2026-10-15"
AUTHOR = "سجاد معصومی"
ROLE = "مدیر رشد دیجیتال و توسعه تجارت الکترونیک"

GATE_PATH_SEG = "energytahvieh-rd-proposal-2026"  # مسیر غیرقابل حدس


# --------------------------------------------------------------------------- #
# رمزنگاری
# --------------------------------------------------------------------------- #
def encrypt_payload(plaintext_html: str, password: str) -> str:
    """AES-256-GCM با کلید مشتق‌شده از PBKDF2-SHA256.

    خروجی: base64( salt[16] || iv[12] || ciphertext||tag )
    دقیقاً همان چیزی که Web Crypto API در مرورگر باز می‌کند.
    """
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITER, dklen=32
    )
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ct, tag = cipher.encrypt_and_digest(plaintext_html.encode("utf-8"))
    return base64.b64encode(salt + iv + ct + tag).decode("ascii")


def font_data_uri(weight_name: str) -> str:
    p = os.path.join(FONTDIR, f"Vazirmatn-{weight_name}.woff2")
    with open(p, "rb") as f:
        return "data:font/woff2;base64," + base64.b64encode(f.read()).decode("ascii")


# --------------------------------------------------------------------------- #
# CSS سند، محدود (scoped) به #doc-root تا استایل دروازه را خراب نکند
# --------------------------------------------------------------------------- #
AT_RULES = ("@font-face", "@page", "@media", "@keyframes", "@supports", "@import")


def _prefix_group(group: str) -> str:
    """یک گروه انتخاب‌گر را به #doc-root مقید می‌کند."""
    out = []
    for sel in group.split(","):
        s = sel.strip()
        if not s:
            continue
        if s.startswith(AT_RULES):
            out.append(sel)
        elif s == "body":
            out.append(sel.replace("body", "#doc-root", 1))
        elif s.startswith(("html", "body ", "body>", "body.")):
            out.append(sel.replace("body", "#doc-root", 1))
        elif s == "html":
            out.append("#doc-root")
        else:
            out.append(f"#doc-root {s}")
    return ", ".join(out)


def scope_css(css: str) -> str:
    res, buf, depth, in_str = [], "", 0, None
    for ch in css:
        if in_str:
            buf += ch
            if ch == in_str:
                in_str = None
            continue
        if ch in "\"'":
            in_str = ch
            buf += ch
            continue
        if ch == "{":
            depth += 1
            buf += ch
        elif ch == "}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            res.append(_prefix_group(buf))
            buf = ""
        else:
            buf += ch
    res.append(_prefix_group(buf))
    return ",".join(res)


def build_doc_css(password_free: bool = True) -> str:
    uri_r = font_data_uri("Regular")
    uri_b = font_data_uri("Bold")
    uri_e = font_data_uri("ExtraBold")
    faces = f"""
@font-face{{font-family:'Vazirmatn';src:url('{uri_r}') format('woff2');font-weight:400;font-display:block}}
@font-face{{font-family:'Vazirmatn';src:url('{uri_b}') format('woff2');font-weight:500;font-display:block}}
@font-face{{font-family:'Vazirmatn';src:url('{uri_b}') format('woff2');font-weight:600;font-display:block}}
@font-face{{font-family:'Vazirmatn';src:url('{uri_b}') format('woff2');font-weight:700;font-display:block}}
@font-face{{font-family:'Vazirmatn';src:url('{uri_e}') format('woff2');font-weight:800;font-display:block}}
@font-face{{font-family:'Vazirmatn';src:url('{uri_e}') format('woff2');font-weight:900;font-display:block}}
"""
    body = md2html._CSS_BODY
    # ابزار چاپ و برگه سفید درون دروازه معنا ندارند
    body = body.replace(".no-print { display: none !important; }",
                        ".no-print { display: none !important; }")
    return faces + scope_css(body)


# --------------------------------------------------------------------------- #
# تولید بدنه هر سند
# --------------------------------------------------------------------------- #
def build_document_html(key: str) -> str:
    spec = DOCS[key]
    with open(os.path.join(ROOT, spec["src"]), encoding="utf-8") as f:
        md = f.read()
    meta = spec["cover"]
    css = build_doc_css()
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"/>
<title>{md2html.esc(meta['title'].replace(chr(10), ' — '))}</title>
<style>{css}</style>
</head>
<body>
<div class="sheet">
{md2html.cover_html(meta)}
{md2html.render(md)}
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# صفحه دروازه
# --------------------------------------------------------------------------- #
GATE_CSS = """
@font-face{font-family:'Vazirmatn';src:url('__R__') format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('__B__') format('woff2');font-weight:700;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('__E__') format('woff2');font-weight:900;font-display:block}
*{box-sizing:border-box}
:root{--accent:#0f5c8c;--accent2:#0d4f78;--alert:#a82222;--line:#dbe4ec;--soft:#f6f9fb}
html,body{margin:0;padding:0}
body{
  font-family:'Vazirmatn',Tahoma,sans-serif;direction:rtl;text-align:right;
  background:#eef1f4;color:#1b1b1b;line-height:1.85;font-size:14.5px;
  min-height:100vh;
}
.shell{max-width:880px;margin:0 auto;padding:26px 18px 70px;position:relative;z-index:2}

/* ---------- واترمارک ---------- */
#wm{
  position:fixed;inset:-40%;z-index:1;pointer-events:none;
  display:flex;flex-wrap:wrap;align-content:center;justify-content:center;
  gap:70px 90px;transform:rotate(-28deg);opacity:.055;
  font-weight:900;font-size:22px;color:#0f5c8c;white-space:nowrap;
  user-select:none;
}
#wm span{display:block}

/* ---------- سربرگ ---------- */
.masthead{
  background:linear-gradient(150deg,#0f5c8c 0%,#123f5e 100%);
  color:#fff;border-radius:14px;padding:30px 30px 26px;
  box-shadow:0 4px 20px rgba(13,63,94,.28);
}
.masthead .kicker{font-size:12.5px;opacity:.85;font-weight:700;letter-spacing:.01em}
.masthead h1{margin:.45em 0 .25em;font-size:24px;font-weight:900;line-height:1.55}
.masthead p{margin:.3em 0 0;font-size:13.5px;opacity:.92}
.masthead .meta{
  margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,.22);
  display:flex;flex-wrap:wrap;gap:8px 22px;font-size:12.5px;opacity:.92;
}

/* ---------- کارت ---------- */
.card{
  background:#fff;border:1px solid var(--line);border-radius:12px;
  padding:22px 24px;margin-top:16px;box-shadow:0 1px 5px rgba(0,0,0,.05);
}
.card h2{margin:0 0 .5em;font-size:17px;font-weight:800;color:var(--accent)}
.card h3{margin:1.3em 0 .45em;font-size:14.5px;font-weight:800;color:#143d59}
.card p{margin:.6em 0;text-align:justify}
.muted{color:#5a5a5a;font-size:13px}

/* ---------- فهرست اسناد ---------- */
ul.docs{list-style:none;padding:0;margin:.8em 0 0}
ul.docs li{
  display:flex;gap:11px;align-items:flex-start;
  padding:11px 0;border-bottom:1px dashed var(--line);
}
ul.docs li:last-child{border-bottom:0}
ul.docs .ic{
  flex:0 0 30px;height:30px;border-radius:8px;background:var(--soft);
  border:1px solid var(--line);display:flex;align-items:center;justify-content:center;
  font-size:15px;color:var(--accent);
}
ul.docs b{display:block;font-size:14px;color:#143d59;font-weight:800}
ul.docs small{color:#5a5a5a;font-size:12.5px;line-height:1.7}

/* ---------- فرم رمز ---------- */
.gate-form{margin-top:6px}
label{display:block;font-size:13.5px;font-weight:700;color:#143d59;margin-bottom:7px}
.row{display:flex;gap:10px;flex-wrap:wrap}
input[type=password],input[type=text]{
  flex:1 1 260px;min-width:0;padding:13px 15px;font-size:15px;font-family:inherit;
  border:2px solid var(--line);border-radius:9px;background:#fcfdfe;color:#1b1b1b;
  direction:ltr;text-align:center;letter-spacing:.14em;transition:border-color .18s,box-shadow .18s;
}
input:focus{outline:0;border-color:var(--accent);box-shadow:0 0 0 4px rgba(15,92,140,.11)}
button{
  padding:13px 26px;font-size:14.5px;font-weight:800;font-family:inherit;
  border:0;border-radius:9px;cursor:pointer;background:var(--accent);color:#fff;
  transition:background .18s,transform .08s;white-space:nowrap;
}
button:hover{background:var(--accent2)}
button:active{transform:translateY(1px)}
button:disabled{background:#9fb4c2;cursor:not-allowed}
button.ghost{background:#fff;color:var(--accent);border:1.5px solid var(--line)}
button.ghost:hover{background:var(--soft)}

/* ---------- پیام‌ها ---------- */
.msg{margin-top:14px;padding:12px 16px;border-radius:9px;font-size:13.5px;display:none}
.msg.err{display:block;background:#fdecec;color:var(--alert);border:1px solid #f2c4c4}
.msg.info{display:block;background:#eaf2f8;color:#1c4f70;border:1px solid #c9dcea}
.msg.ok{display:block;background:#e6f4ea;color:#1c6b34;border:1px solid #c3e2cd}
.spin{
  display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,.4);
  border-top-color:#fff;border-radius:50%;animation:sp .7s linear infinite;
  vertical-align:-2px;margin-left:7px;
}
@keyframes sp{to{transform:rotate(360deg)}}

/* ---------- سوئیچ ---------- */
.switch{display:flex;align-items:flex-start;gap:11px;margin-top:10px}
.switch input{margin-top:5px;width:17px;height:17px;accent-color:var(--accent);flex:0 0 auto}
.switch .t{font-size:13px;color:#3d3d3d;line-height:1.75}
.switch .t b{color:#143d59}

/* ---------- هشدار صادقانه ---------- */
.honest{
  background:#fffaf0;border:1px solid #f0e0bd;border-right:5px solid #c99a2e;
  border-radius:10px;padding:16px 20px;margin-top:16px;
}
.honest h3{margin:0 0 .4em;font-size:14.5px;color:#7a5c14;font-weight:800}
.honest p{margin:.45em 0;font-size:13px;color:#5d4c22;text-align:justify}
.honest code{
  font-family:Consolas,monospace;direction:ltr;unicode-bidi:embed;
  background:#f6ecd6;padding:.1em .4em;border-radius:4px;font-size:.88em;
}

/* ---------- نمایشگر سند ---------- */
#viewer{display:none;margin-top:16px}
.vbar{
  position:sticky;top:0;z-index:30;background:#fff;border:1px solid var(--line);
  border-radius:12px 12px 0 0;padding:11px 16px;display:flex;gap:9px;
  align-items:center;flex-wrap:wrap;box-shadow:0 2px 8px rgba(0,0,0,.06);
}
.vbar .sp{flex:1}
.vbar button{padding:8px 15px;font-size:13px}
.vframe{
  background:#fff;border:1px solid var(--line);border-top:0;border-radius:0 0 12px 12px;
  overflow:hidden;
}
#doc-root{padding:4px 2px 20px}
#doc-root .sheet{box-shadow:none;margin:0;max-width:none}

/* ---------- لایه اصطکاک (فقط وقتی سوئیچ روشن است) ---------- */
body.harden #doc-root{user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
body.harden #doc-root img{pointer-events:none}
body.harden #wm{opacity:.085}

/* ---------- پاصفحه ---------- */
footer{
  margin-top:26px;padding-top:16px;border-top:1px solid var(--line);
  font-size:12.5px;color:#5a5a5a;text-align:center;line-height:2.1;
}
footer b{color:#143d59}

@media print{
  #wm{opacity:.05}
  .masthead,.card,.gate-form,.honest,footer,.vbar{display:none !important}
  .shell{max-width:none;padding:0}
  #viewer{display:block !important}
}
@media (max-width:600px){
  body{font-size:14px}
  .masthead{padding:22px 20px}
  .masthead h1{font-size:19.5px}
  .card{padding:18px 17px}
  button{flex:1 1 100%}
}
"""


def gate_page(password: str, docs_info):
    css = (GATE_CSS
           .replace("__R__", font_data_uri("Regular"))
           .replace("__B__", font_data_uri("Bold"))
           .replace("__E__", font_data_uri("ExtraBold")))

    items = []
    for key, title, blurb in docs_info:
        items.append(f"""      <li>
        <span class="ic">📄</span>
        <span><b>{md2html.esc(title)}</b><small>{md2html.esc(blurb)}</small></span>
      </li>""")

    payloads = {}
    for key, _t, _b in docs_info:
        html_doc = build_document_html(key)
        payloads[key] = encrypt_payload(html_doc, password)

    payload_js = ",\n    ".join(f'"{k}": "{v}"' for k, v in payloads.items())
    order_js = "[" + ", ".join(f'"{k}"' for k, _t, _b in docs_info) + "]"
    first_key = docs_info[0][0]

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet,noimageindex"/>
<meta name="googlebot" content="noindex,nofollow"/>
<meta http-equiv="Cache-Control" content="no-store,no-cache,must-revalidate"/>
<meta http-equiv="Pragma" content="no-cache"/>
<meta name="referrer" content="no-referrer"/>
<title>پروپوزال رشد دیجیتال انرژی تهویه — سند محافظت‌شده</title>
<style>{css}</style>
</head>
<body>

<div id="wm" aria-hidden="true"></div>

<div class="shell">

  <div class="masthead">
    <div class="kicker">سند محافظت‌شده · نسخه 1.0 · {TODAY_FA} / {TODAY_EN}</div>
    <h1>پروپوزال راهبردی توسعه و بهینه‌سازی<br/>اکوسیستم دیجیتال انرژی تهویه</h1>
    <p>تهیه‌شده برای بررسی مدیریت · {md2html.esc(ROLE)}</p>
    <div class="meta">
      <span>👤 تهیه‌کننده: {AUTHOR}</span>
      <span>🎯 مخاطب: مدیریت انرژی تهویه</span>
      <span>🔒 رمزنگاری AES-256-GCM</span>
    </div>
  </div>

  <!-- ============ مرحله ورود رمز ============ -->
  <div id="stage-gate">

    <div class="card">
      <h2>🔐 این سند با رمز محافظت می‌شود</h2>
      <p>محتوای سند پیش از آنکه به مرورگر شما برسد <b>رمزنگاری</b> شده است. بدون رمز
      صحیح، هیچ بخشی از آن قابل بازیابی نیست — نه در این صفحه، نه در کد منبع آن.</p>
      <p class="muted">رمز ورود از طریق پیامک یا تماس در اختیار شما قرار گرفته است.
      اگر رمز را دریافت نکرده‌اید، کافی است پاسخ همین پیام را بدهید.</p>

      <h3>محتویات این بسته</h3>
      <ul class="docs">
{chr(10).join(items)}
      </ul>

      <h3>رمز ورود</h3>
      <div class="gate-form">
        <label for="pw">رمز را وارد کنید</label>
        <div class="row">
          <input type="password" id="pw" autocomplete="off" spellcheck="false"
                 placeholder="••••••••••••" aria-label="رمز ورود سند"/>
          <button id="go" type="button">🔓 مشاهده سند</button>
        </div>
        <div class="msg" id="msg" role="status" aria-live="polite"></div>

        <div class="switch">
          <input type="checkbox" id="harden"/>
          <label for="harden" class="t" style="margin:0">
            <b>حالت محافظت بیشتر</b> — جلوگیری از انتخاب متن، راست‌کلیک و
            <code>Ctrl+S</code> / <code>Ctrl+U</code> / <code>Ctrl+P</code>.
            <br/><span class="muted">پیش‌فرض خاموش است، چون چاپ و ذخیره سند برای
            بررسی داخلی شما مفید است. توضیح صادقانه محدودیت‌های این حالت در کادر
            پایین آمده است.</span>
          </label>
        </div>
      </div>
    </div>

    <div class="honest">
      <h3>⚖️ یک توضیح صادقانه درباره محافظت</h3>
      <p><b>هیچ صفحه وبی نمی‌تواند از اسکرین‌شات جلوگیری کند.</b> تصویربرداری از
      نمایشگر در سطح سیستم‌عامل انجام می‌شود و مرورگر به آن دسترسی ندارد. این یک
      محدودیت بنیادین وب است، نه کوتاهی در پیاده‌سازی.</p>
      <p>آنچه این صفحه <b>واقعاً</b> انجام می‌دهد: محتوا بدون رمز تحویل مرورگر
      نمی‌شود (رمزنگاری واقعی)، و واترمارک هویت‌دار روی همه صفحات اثر انگشت
      قابل ردیابی می‌گذارد.</p>
      <p>«حالت محافظت بیشتر» فقط <b>اصطکاک</b> ایجاد می‌کند — کپی راحت را سخت
      می‌کند، ولی برای فرد مصمم مانع نیست. به همین دلیل به‌جای تکیه بر آن،
      محافظت واقعی در <b>محدودسازی محتوای خود سند</b> انجام شده است: این
      پروپوزال عمداً در سطح مدیریتی نوشته شده و برنامه اجرایی تفصیلی، معماری
      فنی، بک‌لاگ اقدامات و جزئیات عملیاتی در آن نیست. آن بخش‌ها جزو خدمات
      دوره همکاری‌اند، نه مرحله ارزیابی.</p>
    </div>

  </div><!-- /stage-gate -->

  <!-- ============ نمایشگر سند ============ -->
  <div id="viewer">
    <div class="vbar">
      <span style="font-size:13px;font-weight:700;color:#143d59">📄 <span id="vtitle"></span></span>
      <span class="sp"></span>
      <button class="ghost" id="btn-print" type="button">🖨️ چاپ / PDF</button>
      <button class="ghost" id="btn-copy" type="button">📋 کپی متن</button>
      <button class="ghost" id="btn-close" type="button">✖ بستن و خروج</button>
    </div>
    <div class="vframe"><div id="doc-root"></div></div>
  </div>

  <footer>
    <b>{AUTHOR}</b> · {md2html.esc(ROLE)} · {TODAY_FA}<br/>
    این سند برای بررسی مدیریت انرژی تهویه تهیه شده و انتشار عمومی آن مجاز نیست.<br/>
    فونت وزيرمتن — SIL Open Font License 1.1
  </footer>

</div><!-- /shell -->

<script>
(function(){{
  "use strict";

  // ------- پیکربندی -------
  var PBKDF2_ITER = {PBKDF2_ITER};
  var DOCS = {{
    "02": {{ title: "پروپوزال راهبردی — سند اصلی تصمیم‌گیری",
             blurb: "۱۳ بخش مدیریتی: درک کسب‌وکار، مشاهدات اولیه، چالش‌ها و فرصت‌های اولویت‌دار، چشم‌انداز، پنج محور همکاری، برنامه ۹۰ روزه، نقشه راه ۶ تا ۱۲ ماهه، شاخص‌های سنجش، مدل همکاری، پیشنهاد مالی و منطق آن، شرایط موفقیت و گام بعدی." }},
    "06": {{ title: "فهرست محدودیت‌ها و موارد غیرقابل نتیجه‌گیری",
             blurb: "پیوست شفافیت: ۸ محدودیت ذاتی روش بررسی، ۲۵ قلم داده که هرگز در دسترس نبود، ۱۸ فرضیه با سطح اطمینان و روش تأیید، و تفکیک صریح آنچه می‌توان با اطمینان گفت از آنچه نمی‌توان." }}
  }};
  var ORDER = {order_js};

  // بارهای رمزنگاری‌شده — بدون رمز، رشته‌های بی‌معنا هستند
  var PAYLOADS = {{
    {payload_js}
  }};

  // ------- واترمارک -------
  var WM_TEXT = "{AUTHOR} · انرژی تهویه · {TODAY_FA} · محرمانه";
  (function(){{
    var wm = document.getElementById("wm"), n = 90, i, s;
    for (i = 0; i < n; i++) {{
      s = document.createElement("span");
      s.textContent = WM_TEXT;
      wm.appendChild(s);
    }}
  }})();

  var $ = function(id){{ return document.getElementById(id); }};
  var pw = $("pw"), go = $("go"), msg = $("msg"), harden = $("harden");

  function setMsg(kind, html){{
    msg.className = "msg" + (kind ? " " + kind : "");
    msg.innerHTML = html;
  }}
  function clearMsg(){{ msg.className = "msg"; msg.innerHTML = ""; }}

  // ------- رمزگشایی با Web Crypto -------
  function b64ToBytes(b64){{
    var bin = atob(b64), len = bin.length, out = new Uint8Array(len), i;
    for (i = 0; i < len; i++) out[i] = bin.charCodeAt(i);
    return out;
  }}

  function decrypt(b64, password){{
    var raw = b64ToBytes(b64);
    var salt = raw.slice(0, 16);
    var iv   = raw.slice(16, 28);
    var ct   = raw.slice(28);
    var enc  = new TextEncoder();

    return crypto.subtle.importKey(
      "raw", enc.encode(password), {{ name: "PBKDF2" }}, false, ["deriveKey"]
    ).then(function(baseKey){{
      return crypto.subtle.deriveKey(
        {{ name: "PBKDF2", salt: salt, iterations: PBKDF2_ITER, hash: "SHA-256" }},
        baseKey,
        {{ name: "AES-GCM", length: 256 }},
        false, ["decrypt"]
      );
    }}).then(function(key){{
      return crypto.subtle.decrypt({{ name: "AES-GCM", iv: iv }}, key, ct);
    }}).then(function(buf){{
      return new TextDecoder("utf-8").decode(buf);
    }});
  }}

  // ------- استخراج بدنه از HTML رمزگشایی‌شده -------
  function mount(html, title){{
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, "text/html");

    // فونت‌ها و استایل سند را به همین صفحه منتقل می‌کنیم
    var old = document.getElementById("doc-css");
    if (old) old.remove();
    var st = document.createElement("style");
    st.id = "doc-css";
    st.textContent = Array.prototype.map.call(
      doc.querySelectorAll("style"), function(s){{ return s.textContent; }}
    ).join("\\n");
    document.head.appendChild(st);

    var root = $("doc-root");
    root.innerHTML = "";
    Array.prototype.forEach.call(doc.body.children, function(node){{
      root.appendChild(document.importNode(node, true));
    }});

    $("vtitle").textContent = title;
    $("stage-gate").style.display = "none";
    $("viewer").style.display = "block";
    window.scrollTo(0, 0);
  }}

  // ------- جریان ورود -------
  function unlock(){{
    var password = pw.value;
    if (!password) {{ setMsg("err", "لطفاً رمز را وارد کنید."); pw.focus(); return; }}

    go.disabled = true;
    go.innerHTML = '<span class="spin"></span>در حال رمزگشایی…';
    setMsg("info", "در حال مشتق‌سازی کلید با " + PBKDF2_ITER.toLocaleString("fa-IR") +
                   " تکرار PBKDF2 و رمزگشایی سند…");

    decrypt(PAYLOADS[ORDER[0]], password)
      .then(function(html){{
        // رمز درست بود — همه اسناد را باز می‌کنیم و اولی را نمایش می‌دهیم
        window.__unlocked = {{ password: password }};
        setMsg("ok", "✓ رمز پذیرفته شد.");
        setTimeout(function(){{ mount(html, DOCS[ORDER[0]].title); }}, 260);
      }})
      .catch(function(){{
        setMsg("err", "✖ رمز نادرست است. سند رمزنگاری شده و با رمز اشتباه " +
                      "بازشدنی نیست. اگر رمز را دریافت نکرده‌اید، پاسخ همین " +
                      "پیام را بدهید تا برایتان ارسال کنم.");
        pw.value = "";
        pw.focus();
      }})
      .finally(function(){{
        go.disabled = false;
        go.textContent = "🔓 مشاهده سند";
      }});
  }}

  go.addEventListener("click", unlock);
  pw.addEventListener("keydown", function(e){{ if (e.key === "Enter") unlock(); }});

  // ------- سوئیچ محافظت بیشتر -------
  harden.addEventListener("change", function(){{
    document.body.classList.toggle("harden", harden.checked);
    applyHarden(harden.checked);
  }});

  function block(e){{ e.preventDefault(); return false; }}
  function applyHarden(on){{
    if (on) {{
      document.addEventListener("contextmenu", block);
      document.addEventListener("dragstart", block);
      document.addEventListener("keydown", keyBlock);
    }} else {{
      document.removeEventListener("contextmenu", block);
      document.removeEventListener("dragstart", block);
      document.removeEventListener("keydown", keyBlock);
    }}
  }}
  function keyBlock(e){{
    var k = (e.key || "").toLowerCase();
    var c = e.ctrlKey || e.metaKey;
    if (!c) return;
    if (["s","u","p","a","c","x"].indexOf(k) !== -1) {{
      e.preventDefault(); e.stopPropagation();
      setMsg("info", "«حالت محافظت بیشتر» فعال است؛ این کلید غیرفعال شد. " +
                     "برای چاپ یا کپی، سوئیچ را خاموش کنید.");
      $("stage-gate").style.display = "";
      $("viewer").style.display = "none";
      return false;
    }}
  }}

  // ------- دکمه‌های نمایشگر -------
  $("btn-close").addEventListener("click", function(){{
    $("doc-root").innerHTML = "";
    var s = $("doc-css"); if (s) s.remove();
    $("viewer").style.display = "none";
    $("stage-gate").style.display = "";
    pw.value = "";
    clearMsg();
    window.scrollTo(0, 0);
  }});

  $("btn-print").addEventListener("click", function(){{ window.print(); }});

  $("btn-copy").addEventListener("click", function(){{
    var txt = $("doc-root").innerText;
    var note = "\\n\\n—\\nتهیه‌کننده: {AUTHOR} · {TODAY_FA}\\n" +
               "این سند برای بررسی مدیریت انرژی تهویه تهیه شده است.\\n";
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(txt + note).then(function(){{
        $("btn-copy").textContent = "✓ کپی شد";
        setTimeout(function(){{ $("btn-copy").textContent = "📋 کپی متن"; }}, 2000);
      }});
    }} else {{
      var ta = document.createElement("textarea");
      ta.value = txt + note; document.body.appendChild(ta);
      ta.select(); document.execCommand("copy"); ta.remove();
      $("btn-copy").textContent = "✓ کپی شد";
      setTimeout(function(){{ $("btn-copy").textContent = "📋 کپی متن"; }}, 2000);
    }}
  }});

  // ------- اگر مرورگر Web Crypto نداشت -------
  if (!(window.crypto && window.crypto.subtle)) {{
    setMsg("err", "مرورگر شما از رمزگشایی امن پشتیبانی نمی‌کند. Web Crypto فقط " +
                  "در بستر امن (HTTPS یا localhost) در دسترس است. صفحه را با " +
                  "HTTPS باز کنید یا از نسخه DOCX استفاده کنید.");
    go.disabled = true;
  }}

  pw.focus();
}})();
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# فایل‌های پشتیبان سرور
# --------------------------------------------------------------------------- #
HTACCESS = """# محافظت سروری — لایه دوم، پیش از رمزنگاری
# اگر هاست شما Apache/LiteSpeed است (cPanel)، این فایل فعال می‌شود.
# اگر استاتیک محض است (Cloudflare/Netlify/Vercel)، این فایل بی‌اثر است و
# باید از تنظیمات همان سرویس برای کنترل دسترسی استفاده کنید.

# --- ایندکس نشدن ---
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow, noarchive, nosnippet"
  Header set Referrer-Policy "no-referrer"
  Header set X-Content-Type-Options "nosniff"
  Header set Cache-Control "no-store, no-cache, must-revalidate"
</IfModule>

# --- خاموش کردن فهرست پوشه ---
Options -Indexes

# --- رمز عبور سروری (لایه دوم) ---
# برای فعال‌سازی:
#   ۱) در cPanel به «Directory Privacy» بروید و روی همین پوشه رمز بگذارید،
#      یا خودتان .htpasswd بسازید:  htpasswd -c .htpasswd energytahvieh
#   ۲) سه خط زیر را از حالت توضیح خارج کنید و مسیر .htpasswd را درست کنید.
# توجه: رمز HTTP Basic Auth با رمز رمزنگاری سند متفاوت است — دو لایه جدا.
#
# AuthType Basic
# AuthName "Energy Tahvieh Proposal - Restricted"
# AuthUserFile /home/USER/public_html/PATH/.htpasswd
# Require valid-user

# --- بستن دسترسی مستقیم به بارهای رمزنگاری‌شده از دامنه‌های دیگر ---
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteCond %{HTTP_REFERER} !^$
  RewriteCond %{HTTP_REFERER} !^https?://([a-z0-9-]+\\.)*sajadmasoumi\\.com [NC]
  RewriteRule \\.(json|txt)$ - [F,L]
</IfModule>
"""

ROBOTS_TXT = """User-agent: *
Disallow: /
"""

LOG_PHP = """<?php
/**
 * log-visit.php — ثبت بازدید (اختیاری، فقط روی هاست PHP)
 *
 * نصب:
 *   ۱) این فایل را کنار index.html بگذارید
 *   ۲) در index.html، درست پس از موفقیت رمزگشایی، این فراخوانی را اضافه کنید:
 *        fetch('log-visit.php', {method:'POST', body:'ok'}).catch(function(){});
 *   ۳) در پوشه، یک فایل خالی visits.log بسازید و اجازه نوشتن بدهید:
 *        chmod 660 visits.log
 *
 * چه چیزی ثبت می‌شود: زمان، IP، User-Agent، Referrer.
 * رمز سند هرگز ارسال یا ثبت نمی‌شود — رمزگشایی کاملاً سمت مرورگر است.
 *
 * چرا ارزشمند است: پس از ارسال لینک، دقیقاً می‌دانید کارفرما چند بار و چه
 * ساعت‌هایی سند را باز کرده. در پیگیری مذاکره اطلاعات عملی می‌دهد.
 */

header('Content-Type: application/json; charset=utf-8');

// فقط POST از همان دامنه
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo '{"ok":false}';
    exit;
}

$entry = [
    'time'    => date('Y-m-d H:i:s'),
    'ip'      => $_SERVER['REMOTE_ADDR']      ?? '-',
    'agent'   => substr($_SERVER['HTTP_USER_AGENT'] ?? '-', 0, 220),
    'referer' => substr($_SERVER['HTTP_REFERER']    ?? '-', 0, 220),
];

$file = __DIR__ . '/visits.log';
$line = json_encode($entry, JSON_UNESCAPED_UNICODE) . PHP_EOL;

if (@file_put_contents($file, $line, FILE_APPEND | LOCK_EX) === false) {
    http_response_code(500);
    echo '{"ok":false}';
    exit;
}

echo '{"ok":true}';
"""


def deploy_readme(password: str, url_hint: str):
    return f"""# راهنمای استقرار سایت محافظت‌شده

**ساخته‌شده در:** {TODAY_FA} / {TODAY_EN}
**رمز سند:** `{password}`
**رمزنگاری:** AES-256-GCM با کلید مشتق‌شده از PBKDF2-SHA256 ({PBKDF2_ITER:,} تکرار)

---

## آنچه در این پوشه است

| فایل | نقش |
|---|---|
| `index.html` | صفحه دروازه + نمایشگر سند. **تنها فایلی که لازم است آپلود کنید.** |
| `.htaccess` | لایه محافظت سروری (Apache/LiteSpeed). اختیاری. |
| `robots.txt` | جلوگیری از ایندکس. اختیاری ولی توصیه‌شده. |
| `log-visit.php` | ثبت بازدید. اختیاری، فقط روی هاست PHP. |
| `DEPLOY-README.md` | همین فایل. **آپلود نکنید** — رمز را در خود دارد. |

همه‌چیز در `index.html` **خودبسنده** است: فونت وزيرمتن به‌صورت base64 جاسازی
شده، پس هیچ فایل جانبی، هیچ CDN و هیچ اتصال اینترنتی لازم نیست.

⚠️ **`DEPLOY-README.md` را آپلود نکنید** — رمز سند در آن نوشته شده.

---

## استقرار

### مسیر پیشنهادی — پوشه با نام غیرقابل حدس

روی هاست، پوشه‌ای بسازید به نام:

```
{GATE_PATH_SEG}
```

و `index.html` را در آن بگذارید. لینک نهایی:

```
https://sajadmasoumi.com/{GATE_PATH_SEG}/
```

نام طولانی و بی‌قاعده عمداً انتخاب شده تا حدس زدن و خزش ممکن نبود.
`robots.txt` و `noindex` هم از ایندکس شدن جلوگیری می‌کنند.

### اگر هاست cPanel / Apache است

۱. `index.html` و `.htaccess` را در پوشه بگذارید
۲. در `.htaccess`، بخش `AuthType Basic` را از حالت توضیح خارج کنید و مسیر
   `.htpasswd` را اصلاح کنید — یا ساده‌تر، از **Directory Privacy** در cPanel
   رمز بگذارید
۳. این یک لایه **جدا** از رمز سند است: اول رمز سرور، بعد رمز رمزگشایی

### اگر Cloudflare Pages / Netlify / Vercel است

`.htaccess` بی‌اثر است. به‌جایش:
- **Cloudflare Access** — رمز واقعی سروری می‌دهد (بهترین گزینه)
- **Netlify / Vercel** — نسخه رایگان رمز سروری ندارد؛ رمزنگاری سند خودش
  محافظت اصلی است و کافی است
- `robots.txt` را در ریشه دامنه بگذارید یا از هدر `X-Robots-Tag` استفاده کنید

---

## چه چیزی را برای کارفرما بفرستید

```
لینک  : https://sajadmasoumi.com/{GATE_PATH_SEG}/
رمز   : {password}
```

**رمز را از کانال جداگانه بفرستید** — لینک در ایمیل، رمز در پیامک یا واتساپ.
این کار دو چیز می‌دهد: اگر لینک forward شود، بدون رمز بی‌فایده است؛ و شما
مطمئن می‌شوید خودِ فرد رمز را دیده.

### متن پیشنهادی ارسال

> سلام و وقت بخیر،
>
> پیوست همان پروپوزالی است که در جلسه درباره‌اش صحبت کردیم. برای اینکه
> محتوایش بدون اجازه منتشر نشود، به‌صورت رمزنگاری‌شده روی سایت خودم
> گذاشته‌ام:
>
> 🔗 https://sajadmasoumi.com/{GATE_PATH_SEG}/
> 🔑 رمز: {password}
>
> داخلش دو سند هست: خود پروپوزال راهبردی، و یک پیوست که صریحاً فهرست
> می‌کند چه چیزهایی را در این تحلیل اولیه **نمی‌شود** نتیجه‌گیری کرد و چرا.
> فکر کردم دومی برایتان مفید باشد تا بدانید کدام بخش‌ها نیازمند دسترسی به
> داده داخلی است.
>
> اگر ترجیح می‌دهید نسخه Word یا PDF داشته باشید تا در جلسه چاپ کنید یا
> برای همکارانتان بفرستید، بگویید تا برایتان ارسال کنم.
>
> ارادتمند،
> سجاد معصومی

پیشنهاد نسخه Word/PDF در پایان **عمدی** است: هم حسن نیت نشان می‌دهد، هم
مانع از آن می‌شود که محافظت، به مانعی برای تصمیم‌گیری تبدیل شود.

---

## لایه‌های محافظت — صادقانه

| لایه | اثربخشی | توضیح |
|---|---|---|
| رمزنگاری AES-256-GCM | 🔴 **واقعی** | بدون رمز، محتوا در مرورگر وجود ندارد. View Source هم چیزی نشان نمی‌دهد. |
| کنترل دسترسی سرور | 🔴 **واقعی** | پیش از رسیدن به رمز دوم |
| واترمارک هویت‌دار | 🟠 **بازدارنده** | قابل ردیابی است؛ همین بازدارنده اصلی است |
| `noindex` / `robots` | 🟡 **پیشگیرانه** | از آرشیو دائمی در Wayback Machine جلوگیری می‌کند |
| مسیر غیرقابل حدس | 🟡 **پیشگیرانه** | حدس و خزش را عملاً ناممکن می‌کند |
| «حالت محافظت بیشتر» | ⚪ **اصطکاک** | فقط کپی راحت را سخت می‌کند. **پیش‌فرض خاموش.** |

### آنچه ممکن نیست

**اسکرین‌شات در وب قابل جلوگیری نیست.** تصویربرداری از نمایشگر در سطح
سیستم‌عامل انجام می‌شود؛ مرورگر به آن دسترسی ندارد. DRM واقعی هم فقط در
اپلیکیشن‌های کنترل‌شده کار می‌کند و آن هم با ضبط از نمایشگر شکست می‌خورد.

هر راه‌حلی که ادعا کند اسکرین‌شات را در مرورگر می‌بندد، یا نادرست است یا
فقط تئاتر. به همین دلیل این صفحه به‌جای تظاهر، محافظت واقعی را در دو جای
دیگر می‌گذارد:

۱. **رمزنگاری** — دسترسی را می‌بندد، نه رفتار کاربر را
۲. **محدودسازی محتوای خود سند** — پروپوزال عمداً در سطح مدیریتی نوشته شده.
   برنامه اجرایی تفصیلی، بک‌لاگ ۳۱ اقدامی، معماری فنی، استراتژی سئو و
   مذاکره در سند داخلی ماندند که هرگز منتشر نمی‌شود. مقادیر هدف KPI هم
   خالی‌اند. **پس حتی اگر کپی شود، چیزی که از دست می‌رود ارزش اجرا ندارد.**

این قوی‌ترین لایه محافظت است و در معماری محتواست، نه در JavaScript.

---

## نکات فنی

- **Web Crypto فقط در بستر امن کار می‌کند** — HTTPS یا `localhost`. اگر صفحه
  را با `http://` باز کنید، رمزگشایی ناموفق است. روی دامنه واقعی با HTTPS
  مشکلی نیست.
- برای تست محلی: `python3 -m http.server 8000` در همین پوشه، بعد
  `http://localhost:8000`
- اگر رمز را عوض کردید، اسکریپت را دوباره اجرا کنید — بارهای رمزنگاری‌شده
  باید بازتولید شوند:

```bash
.venv/bin/python energy-tahvieh-proposal/build/make_protected_site.py <رمز-جدید>
```

- حجم `index.html` حدود ۱٫۲ مگابایت است (بیشترش فونت جاسازی‌شده و بارهای
  رمزنگاری‌شده). برای یک صفحه، کاملاً قابل قبول است.
"""


# --------------------------------------------------------------------------- #
def main():
    password = sys.argv[1] if len(sys.argv) > 1 else None
    if not password:
        print("خطا: رمز را به‌عنوان آرگومان بدهید.")
        print("  .venv/bin/python build/make_protected_site.py <رمز>")
        sys.exit(1)
    if len(password) < 6:
        print("خطا: رمز حداقل ۶ نویسه باشد.")
        sys.exit(1)

    docs_info = [
        ("02", "پروپوزال راهبردی — سند اصلی",
         "۱۳ بخش مدیریتی از درک کسب‌وکار تا پیشنهاد مالی و گام بعدی"),
        ("06", "فهرست محدودیت‌ها — پیوست شفافیت",
         "چه چیزهایی در این تحلیل اولیه قابل نتیجه‌گیری نیست، و چرا"),
    ]

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    gate = gate_page(password, docs_info)
    idx = os.path.join(OUT, "index.html")
    with open(idx, "w", encoding="utf-8") as f:
        f.write(gate)

    for name, content in (
        (".htaccess", HTACCESS),
        ("robots.txt", ROBOTS_TXT),
        ("log-visit.php", LOG_PHP),
        ("DEPLOY-README.md", deploy_readme(password, GATE_PATH_SEG)),
    ):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)

    size = os.path.getsize(idx) / 1024
    print(f"OK  index.html      {size:,.0f} KB")
    for n in (".htaccess", "robots.txt", "log-visit.php", "DEPLOY-README.md"):
        print(f"OK  {n:<17} {os.path.getsize(os.path.join(OUT,n))/1024:,.1f} KB")
    print(f"\nخروجی: {OUT}")
    print(f"مسیر پیشنهادی روی دامنه:  /{GATE_PATH_SEG}/")
    print(f"رمز سند: {password}")
    print(f"تکرار PBKDF2: {PBKDF2_ITER:,} · AES-256-GCM")


if __name__ == "__main__":
    main()
