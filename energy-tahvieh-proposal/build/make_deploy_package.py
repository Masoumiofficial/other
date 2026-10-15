#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_deploy_package.py — بسته آماده آپلود برای هاست اشتراکی وردپرسی (cPanel)

خروجی:
  build/deploy/subdomain-package/   <- همان چیزی که آپلود می‌کنید
  build/deploy/sajadmasoumi-subdomain-deploy.zip
  build/deploy/UPLOAD-GUIDE.md      <- راهنمای گام‌به‌گام فارسی

استفاده:
  .venv/bin/python energy-tahvieh-proposal/build/make_deploy_package.py \
      <رمز-سند> [<رمز-سرور>]

اگر آرگومان ندهید، از رمز پیش‌فرض استفاده می‌کند.
"""
import base64
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
SITE = os.path.join(BUILD, "protected-site")
DEPLOY = os.path.join(BUILD, "deploy")
PKG = os.path.join(DEPLOY, "subdomain-package")

DOMAIN = "sajadmasoumi.com"
SUBDOMAIN = "proposal"
HOST_USER = "USER"  # در راهنما گفته می‌شود جایگزین کنند

# رمز پیش‌فرض عمداً وجود ندارد. اگر اینجا مقدار ثابتی بود، با commit شدن
# اسکریپت در یک ریپوی عمومی، رمز هم عمومی می‌شد و کل رمزنگاری بی‌اثر.
# برای همین رمز یک آرگومان اجباری است.
SRV_USER = "energytahvieh"


# --------------------------------------------------------------------------- #
# .htaccess — نسخه اصلی، ایمن برای هاست اشتراکی
# --------------------------------------------------------------------------- #
def htaccess_main(with_auth: bool) -> str:
    auth_block = f"""
# ══════════ لایه دوم: رمز عبور سروری ══════════
# فعال است. دو پرسش می‌دهد: اول رمز سرور (اینجا)، بعد رمز سند (در صفحه).
# برای غیرفعال کردن موقت، این چهار خط را با # ببندید.
#
# ⚠️ مسیر AuthUserFile را با مسیر واقعی پوشه خودتان جایگزین کنید.
#    در cPanel از File Manager روی پوشه کلیک راست → Properties مسیر را
#    می‌دهد. معمولاً چیزی شبیه این است:
#      /home/{HOST_USER}/{SUBDOMAIN}.{DOMAIN}/.htpasswd
#    یا اگر زیر public_html است:
#      /home/{HOST_USER}/public_html/{SUBDOMAIN}/.htpasswd
AuthType Basic
AuthName "Proposal - Restricted"
AuthUserFile /home/{HOST_USER}/{SUBDOMAIN}.{DOMAIN}/.htpasswd
Require valid-user
""" if with_auth else f"""
# ══════════ لایه دوم: رمز عبور سروری (غیرفعال) ══════════
# برای فعال‌سازی: چهار خط زیر را از حالت # خارج کنید و مسیر AuthUserFile را
# با مسیر واقعی پوشه خودتان جایگزین کنید. ساده‌تر از این: در cPanel به
# «Directory Privacy» بروید و روی همین پوشه رمز بگذارید — خودش این خطوط را
# می‌نویسد و .htpasswd را هم می‌سازد.
#
# AuthType Basic
# AuthName "Proposal - Restricted"
# AuthUserFile /home/{HOST_USER}/{SUBDOMAIN}.{DOMAIN}/.htpasswd
# Require valid-user
"""

    return f"""# ══════════════════════════════════════════════════════════════════════
#  .htaccess — ساب‌دامین {SUBDOMAIN}.{DOMAIN}
#  هاست اشتراکی وردپرسی (Apache یا LiteSpeed) · cPanel
# ══════════════════════════════════════════════════════════════════════
#
#  این فایل عمداً ساده نگه داشته شده. در هاست اشتراکی، هر دستورِ خارج از
#  AllowOverride باعث خطای ۵۰۰ می‌شود. برای همین از این‌ها عمداً استفاده
#  نشده:
#    ✖ Options -Indexes        <- در بعضی هاست‌ها ۵۰۰ می‌دهد
#    ✖ RewriteRule             <- اینجا لازم نیست (فایل .json جدا نداریم)
#    ✖ php_value / php_flag    <- در CGI/FPM باعث ۵۰۰ می‌شود
#
#  اگر بعد از آپلود سایت خطای ۵۰۰ داد، نسخه htaccess-fallback.txt را
#  جایگزین کنید.
# ══════════════════════════════════════════════════════════════════════

# ────────── ایندکس نشدن در گوگل و آرشیو نشدن ──────────
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow, noarchive, nosnippet, noimageindex"
  Header set Referrer-Policy "no-referrer"
  Header set X-Content-Type-Options "nosniff"
  Header set Cache-Control "no-store, no-cache, must-revalidate"
  Header set Pragma "no-cache"
</IfModule>

# ────────── صفحه پیش‌فرض ──────────
# index.html باید بر index.php اولویت داشته باشد. اگر وردپرس را اشتباهاً
# روی همین پوشه نصب کرده باشید، بدون این خط ممکن است وردپرس بالا بیاید.
<IfModule mod_dir.c>
  DirectoryIndex index.html index.php index.htm
</IfModule>
{auth_block}
# ────────── بستن دسترسی به فایل‌های حساس ──────────
<FilesMatch "^\\.(htaccess|htpasswd|gitignore)">
  Require all denied
</FilesMatch>

<FilesMatch "\\.(log|md)$">
  Require all denied
</FilesMatch>

# ────────── فشرده‌سازی ──────────
# فایل index.html حدود ۱٫۴ مگابایت است (بیشترش فونت جاسازی‌شده).
# با gzip به حدود ۱٫۱ مگابایت می‌رسد. اگر فعال نباشد هم سایت کار می‌کند.
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript
</IfModule>

# ────────── UTF-8 ──────────
<IfModule mod_mime.c>
  AddDefaultCharset UTF-8
</IfModule>
"""


HTACCESS_FALLBACK = """# نسخه اضطراری — اگر .htaccess اصلی خطای ۵۰۰ داد، فقط این را بگذارید.
# کمینه مطلق: فقط هدرها، آن هم داخل IfModule که اگر mod_headers نبود
# بی‌صدا رد شود.
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow, noarchive"
  Header set Cache-Control "no-store"
</IfModule>
"""

ROBOTS = """# robots.txt — ریشه ساب‌دامین
# این ساب‌دامین فقط برای همین سند محافظت‌شده است، پس همه‌چیز بسته است.
# اگر بعداً محتوای دیگری روی این ساب‌دامین گذاشتید، این را تغییر دهید.
User-agent: *
Disallow: /
"""

HTPASSWD_NOTE = """این فایل عمداً اینجا نیست.

فایل .htpasswd حاوی hash رمز سروری است و نباید در بسته عمومی باشد.
با این دستور ساخته می‌شود:

    .venv/bin/python energy-tahvieh-proposal/build/make_deploy_package.py \
        <رمز-سند> <رمز-سرور> --htpasswd

یا ساده‌تر: در cPanel به «Directory Privacy» بروید و روی پوشه رمز بگذارید.
خودِ cPanel هم .htpasswd را می‌سازد هم خطوط لازم را در .htaccess می‌نویسد.
"""


# --------------------------------------------------------------------------- #
def make_htpasswd(password: str, path: str) -> str:
    import bcrypt

    pw = password.encode("utf-8")
    if len(pw) > 72:
        raise SystemExit(
            f"خطا: رمز سروری {len(pw)} بایت است؛ bcrypt حداکثر ۷۲ بایت می‌پذیرد.\n"
            f"     (هر نویسه فارسی ۲ بایت است، پس حداکثر ~۳۶ نویسه فارسی)"
        )
    h = bcrypt.hashpw(pw, bcrypt.gensalt(rounds=12, prefix=b"2b"))
    # Apache با $2y$ سازگارتر است؛ bcrypt $2b$ تولید می‌کند که معادل است
    # Apache با $2y$ سازگارتر است؛ bcrypt $2b$ می‌دهد که معادل است
    h2y = (b"$2y$" + h[4:]).decode("ascii")
    line = f"{SRV_USER}:{h2y}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(line + "\n")
    return line


GUIDE = """# راهنمای استقرار روی ساب‌دامین — هاست اشتراکی وردپرسی

**دامنه:** `{DOMAIN}` · **ساب‌دامین پیشنهادی:** `{SUBDOMAIN}.{DOMAIN}`
**لینک نهایی:** `https://{SUBDOMAIN}.{DOMAIN}/`

---

## پیش از شروع — سه نکته که اگر ندانید وقتتان تلف می‌شود

### ۱. وردپرس را روی این ساب‌دامین نصب نکنید ⚠️

این مهم‌ترین نکته این راهنماست.

نصب وردپرس `.htaccess` خودش را می‌نویسد و **هدرهای محافظتی ما را پاک
می‌کند**. این صفحه یک فایل HTML مستقل است و به وردپرس هیچ نیازی ندارد —
نه پایگاه داده، نه افزونه، نه قالب.

اگر ناخواسته وردپرس نصب شد:
- `.htaccess` وردپرس جای ما را می‌گیرد ← هدرهای `noindex` و `no-store` از دست می‌روند
- ولی چون در `.htaccess` ما `DirectoryIndex index.html` قبل از `index.php`
  تنظیم شده، **صفحه ما همچنان بالا می‌آید**
- راه‌حل: وردپرس را از آن پوشه پاک کنید و `.htaccess` اصلی را دوباره بگذارید

### ۲. `robots.txt` باید در **ریشه ساب‌دامین** باشد، نه در زیرپوشه

گوگل فقط `https://{SUBDOMAIN}.{DOMAIN}/robots.txt` را می‌خواند. اگر مسیر
`https://{SUBDOMAIN}.{DOMAIN}/proposal/robots.txt` باشد، **کاملاً بی‌اثر** است.

پس اگر صفحه را در زیرپوشه می‌گذارید، `robots.txt` را یک سطح بالاتر ببرید.

### ۳. SSL الزامی است — بدون آن رمزگشایی کار نمی‌کند 🔴

مرورگرها `crypto.subtle` را **فقط در بستر امن** در اختیار می‌گذارند: HTTPS
یا `localhost`. اگر صفحه با `http://` باز شود، سند باز نمی‌شود و پیام خطای
مناسب نمایش داده می‌شود.

در cPanel: **SSL/TLS Status** → دامنه را انتخاب → **Run AutoSSL**.
رایگان است و معمولاً زیر چند دقیقه صادر می‌شود.

---

## گام‌به‌گام

### گام ۱ — ساخت ساب‌دامین

cPanel → **Domains** (در نسخه‌های جدید) یا **Subdomains** (نسخه‌های قدیمی)

```
Subdomain : proposal
Domain    : {DOMAIN}
Document Root : (خودکار پر می‌شود)
```

مسیر Document Root را یادداشت کنید. یکی از این دو حالت است:

| حالت | مسیر |
|---|---|
| جدا از public_html | `/home/{HOST_USER}/{SUBDOMAIN}.{DOMAIN}` |
| زیر public_html | `/home/{HOST_USER}/public_html/{SUBDOMAIN}` |

این مسیر را برای `.htaccess` لازم دارید.

### گام ۲ — فعال کردن SSL

cPanel → **SSL/TLS Status** → `proposal.{DOMAIN}` را تیک بزنید → **Run AutoSSL**

صبر کنید تا قفل سبز شود. بعد `https://{SUBDOMAIN}.{DOMAIN}/` را تست کنید.

### گام ۳ — آپلود فایل‌ها

cPanel → **File Manager** → به Document Root بروید → **Upload**

این فایل‌ها را آپلود کنید:

| فایل | لازم است؟ |
|---|---|
| `index.html` | 🔴 **بله — تنها فایل اجباری** |
| `.htaccess` | 🟠 بله — محافظت سروری |
| `robots.txt` | 🟠 بله — در **ریشه ساب‌دامین** |
| `log-visit.php` | 🟢 اختیاری — ثبت بازدید |

**`index.html` کاملاً خودبسنده است.** فونت وزيرمتن به‌صورت base64 داخلش
جاسازی شده، پس هیچ پوشه `assets/`، هیچ فایل جانبی و هیچ CDN لازم نیست.
یک فایل، تمام.

> در File Manager، برای دیدن `.htaccess` باید **Settings → Show Hidden Files**
> را روشن کنید.

### گام ۴ — تست

```
https://{SUBDOMAIN}.{DOMAIN}/
```

باید صفحه دروازه با سربرگ آبی و کادر رمز بالا بیاید. رمز را بزنید و سند
باید باز شود.

اگر خطا دیدید، جدول عیب‌یابی پایین را ببینید.

### گام ۵ — (اختیاری ولی توصیه‌شده) فعال کردن ثبت بازدید

۱. `log-visit.php` را آپلود کنید
۲. در همان پوشه یک فایل خالی به نام `visits.log` بسازید
۳. روی `visits.log` کلیک راست → **Change Permissions** → `660` یا `664`
۴. در `index.html` جستجو کنید: `setMsg("ok"` — و درست **بعد** از آن خط،
   این را اضافه کنید:

```javascript
        fetch("log-visit.php", {{ method: "POST", body: "ok" }}).catch(function(){{}});
```

۵. بعد از هر بازدید، `visits.log` را ببینید: زمان، IP، User-Agent و
   Referrer ثبت می‌شود

**چرا ارزش دارد:** پس از ارسال لینک، می‌فهمید کارفرما چند بار و چه ساعت‌هایی
سند را باز کرده. در پیگیری مذاکره اطلاعات عملی می‌دهد — اگر سه بار باز کرده
و خبری نشده، می‌دانید باید پیگیری کنید.

⚠️ `.htaccess` طوری تنظیم شده که فایل‌های `.log` و `.md` از بیرون قابل
دسترس نباشند (`Require all denied`). پس `visits.log` عمومی نمی‌شود.

**رمز سند هرگز به سرور ارسال یا در لاگ ثبت نمی‌شود** — رمزگشایی کاملاً
سمت مرورگر انجام می‌شود.

---

## جدول عیب‌یابی

| نشانه | علت | راه‌حل |
|---|---|---|
| **خطای ۵۰۰** پس از آپلود | `.htaccess` دستوری دارد که `AllowOverride` هاست اجازه نمی‌دهد | `htaccess-fallback.txt` را به `.htaccess` تغییر نام دهید |
| «مرورگر شما از رمزگشایی امن پشتیبانی نمی‌کند» | صفحه با `http://` باز شده | SSL را فعال کنید (گام ۲) و با `https://` باز کنید |
| رمز درست است ولی سند باز نمی‌شود | `index.html` با رمز دیگری ساخته شده | اسکریپت را با رمز درست دوباره اجرا کنید |
| صفحه وردپرس بالا می‌آید | وردپرس روی همین پوشه نصب شده | وردپرس را پاک کنید، یا `DirectoryIndex index.html` را در `.htaccess` وردپرس **قبل از** `index.php` بگذارید |
| فونت فارسی به‌هم ریخته | فایل ناقص آپلود شده | `index.html` را دوباره آپلود کنید؛ باید ~۱٬۴۴۱٬۰۰۰ بایت باشد |
| سایت در گوگل پیدا می‌شود | `robots.txt` در زیرپوشه است نه ریشه | به ریشه ساب‌دامین منتقلش کنید |
| `visits.log` نوشته نمی‌شود | اجازه نوشتن ندارد | `chmod 664 visits.log` |

---

## رمزها

| | مقدار | کجا استفاده می‌شود |
|---|---|---|
| **رمز سند** | `{DOC_PW}` | در خود صفحه، برای رمزگشایی محتوا |
| **رمز سرور** | `{SRV_PW}` | در پرسش HTTP مرورگر (اگر لایه دوم را فعال کنید) |
| **نام کاربری سرور** | `{SRV_USER}` | همراه رمز سرور |

این دو **جدا و مستقل**‌اند. لایه سرور را می‌توانید خاموش بگذارید — رمزنگاری
سند به‌تنهایی محافظت اصلی است.

### عوض کردن رمز سند

```bash
.venv/bin/python energy-tahvieh-proposal/build/make_protected_site.py <رمز-جدید>
.venv/bin/python energy-tahvieh-proposal/build/make_deploy_package.py <رمز-جدید>
```

### ساخت `.htpasswd`

```bash
.venv/bin/python energy-tahvieh-proposal/build/make_deploy_package.py <رمز-سند> <رمز-سرور> --htpasswd
```

یا ساده‌تر: cPanel → **Directory Privacy** → روی پوشه رمز بگذارید. خودش
هم `.htpasswd` می‌سازد هم خطوط لازم را در `.htaccess` می‌نویسد.

⚠️ **محدودیت bcrypt:** رمز سروری حداکثر ۷۲ بایت. هر نویسه فارسی ۲ بایت
است، پس حداکثر ~۳۶ نویسه فارسی. رمز لاتین بلندتر می‌تواند باشد.

---

## چه چیزی را برای کارفرما بفرستید

### حالت الف — بدون رمز سروری (پیشنهاد من)

```
🔗 https://{SUBDOMAIN}.{DOMAIN}/
🔑 رمز: {DOC_PW}
```

رمز را **از کانال جداگانه** بفرستید: لینک در ایمیل، رمز در پیامک یا واتساپ.
دو فایده دارد — اگر لینک forward شود بدون رمز بی‌فایده است، و مطمئن
می‌شوید خودِ فرد رمز را دیده.

### حالت ب — با رمز سروری

دو رمز لازم می‌شود و برای کارفرما گیج‌کننده است. فقط اگر واقعاً نگران
دیدن شدن خودِ صفحه دروازه هستید این حالت را انتخاب کنید.

### متن پیشنهادی ارسال

> سلام و وقت بخیر،
>
> پیوست همان پروپوزالی است که در جلسه درباره‌اش صحبت کردیم. برای اینکه
> محتوایش بدون اجازه منتشر نشود، به‌صورت رمزنگاری‌شده روی ساب‌دامین خودم
> گذاشته‌ام:
>
> 🔗 https://{SUBDOMAIN}.{DOMAIN}/
> 🔑 رمز: {DOC_PW}
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
نگذارد محافظت به مانعی برای تصمیم‌گیری تبدیل شود. مدیر استخدام باید بتواند
سند را به شریکش نشان دهد.

---

## صادقانه درباره اینکه این محافظت چقدر واقعی است

| لایه | اثربخشی |
|---|---|
| رمزنگاری AES-256-GCM | 🔴 **واقعی** — بدون رمز، محتوا در مرورگر وجود ندارد |
| رمز سروری (Basic Auth) | 🔴 **واقعی** — پیش از رمز دوم |
| واترمارک هویت‌دار | 🟠 **بازدارنده** — قابل ردیابی است |
| `noindex` + `robots.txt` | 🟡 از آرشیو دائمی در Wayback Machine جلوگیری می‌کند |
| «حالت محافظت بیشتر» | ⚪ **فقط اصطکاک** — پیش‌فرض خاموش |

**اسکرین‌شات در وب قابل جلوگیری نیست.** تصویربرداری از نمایشگر در سطح
سیستم‌عامل انجام می‌شود و مرورگر به آن دسترسی ندارد. این محدودیت بنیادین
وب است، نه کوتاهی در پیاده‌سازی.

**و قوی‌ترین لایه شما اصلاً فنی نیست:** این پروپوزال عمداً در سطح مدیریتی
نوشته شده. بک‌لاگ ۳۱ اقدامی، معماری فنی، استراتژی سئو، معماری AI، سناریوهای
مذاکره و مقادیر هدف KPI در سند داخلی ماندند که هرگز منتشر نمی‌شود. پس حتی
اگر کپی شود، آنچه از دست می‌رود **ارزش اجرا ندارد**.

---

*ساخته‌شده در ۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶ · نسخه 1.1*
""".replace("{DOMAIN}", DOMAIN).replace("{SUBDOMAIN}", SUBDOMAIN).replace("{HOST_USER}", HOST_USER)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_htpasswd_only = "--htpasswd" in sys.argv

    if not args:
        print("خطا: رمز سند اجباری است — هیچ رمز پیش‌فرضی وجود ندارد.")
        print()
        print("  .venv/bin/python build/make_deploy_package.py <رمز-سند> [<رمز-سرور>]")
        print("  .venv/bin/python build/make_deploy_package.py <رمز-سند> <رمز-سرور> --htpasswd")
        print()
        print("چرا اجباری: اگر رمز پیش‌فرض در همین اسکریپت بود، با commit شدنش")
        print("در ریپازیتوری عمومی رمز هم عمومی می‌شد و رمزنگاری بی‌اثر می‌شد.")
        print("رمز سند باید همان باشد که make_protected_site.py با آن ساخته شده.")
        sys.exit(1)

    doc_pw = args[0]

    # رمز سروری: اگر داده نشد، یک رمز تصادفی قوی تولید می‌شود و در
    # server-auth-credentials.txt نوشته می‌شود (که در .gitignore است).
    # هیچ رمز ثابتی در این اسکریپت hard-code نمی‌شود — چون اسکریپت
    # commit می‌شود و رمز hard-code‌شده یعنی رمز عمومی.
    if len(args) > 1:
        srv_pw = args[1]
        srv_generated = False
    else:
        import secrets
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
        srv_pw = "".join(secrets.choice(alphabet) for _ in range(18))
        srv_generated = True

    if not os.path.isdir(SITE) or not os.path.exists(os.path.join(SITE, "index.html")):
        print("خطا: protected-site/index.html پیدا نشد.")
        print("اول این را اجرا کنید:")
        print(f"  .venv/bin/python build/make_protected_site.py {doc_pw}")
        sys.exit(1)

    if want_htpasswd_only:
        p = os.path.join(DEPLOY, ".htpasswd")
        os.makedirs(DEPLOY, exist_ok=True)
        print("خط .htpasswd:")
        print("  " + make_htpasswd(srv_pw, p))
        print(f"\nنوشته شد در: {p}")
        return

    if os.path.isdir(DEPLOY):
        shutil.rmtree(DEPLOY)
    os.makedirs(PKG)

    # index.html — بدون تغییر، خودبسنده است
    shutil.copy2(os.path.join(SITE, "index.html"), os.path.join(PKG, "index.html"))

    files = {
        ".htaccess": htaccess_main(with_auth=False),
        ".htaccess-with-server-auth": htaccess_main(with_auth=True),
        "htaccess-fallback.txt": HTACCESS_FALLBACK,
        "robots.txt": ROBOTS,
        "log-visit.php": open(os.path.join(SITE, "log-visit.php"), encoding="utf-8").read(),
        "HTPASSWD-NOTE.txt": HTPASSWD_NOTE,
        "UPLOAD-GUIDE.md": GUIDE.replace("{DOC_PW}", doc_pw)
                               .replace("{SRV_PW}", srv_pw)
                               .replace("{SRV_USER}", SRV_USER),
    }
    for name, content in files.items():
        with open(os.path.join(PKG, name), "w", encoding="utf-8") as f:
            f.write(content)

    # .htpasswd واقعی
    make_htpasswd(srv_pw, os.path.join(PKG, ".htpasswd"))

    # ZIP
    zp = os.path.join(DEPLOY, "sajadmasoumi-subdomain-deploy.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(os.listdir(PKG)):
            z.write(os.path.join(PKG, n), n)

    # راهنما هم در سطح deploy/
    shutil.copy2(os.path.join(PKG, "UPLOAD-GUIDE.md"),
                 os.path.join(DEPLOY, "UPLOAD-GUIDE.md"))

    # اعتبارنامه‌ها در فایلی که gitignore شده — نه در این اسکریپت، نه در git
    cred = os.path.join(DEPLOY, "server-auth-credentials.txt")
    with open(cred, "w", encoding="utf-8") as f:
        bar = "=" * 58
        f.write(
            f"اعتبارنامه لایه دوم (رمز عبور سروری / HTTP Basic Auth)\n"
            f"{bar}\n\n"
            f"نام کاربری : {SRV_USER}\n"
            f"رمز        : {srv_pw}\n"
            f"منبع       : {'تصادفی تولیدشده' if srv_generated else 'دستی داده‌شده'}\n\n"
            f"رمز سند (لایه اصلی، در صفحه پرسیده می‌شود):\n  {doc_pw}\n\n"
            "این فایل در .gitignore است و commit نمی‌شود.\n"
            "پس از تغییر رمز سروری، .htpasswd را دوباره بسازید:\n"
            f"  .venv/bin/python build/make_deploy_package.py <رمز-سند> {srv_pw} --htpasswd\n"
        )

    idx = os.path.getsize(os.path.join(PKG, "index.html"))
    print(f"OK  بسته در: {PKG}")
    print(f"    index.html  {idx:,} B  ({idx/1024:,.0f} KB)")
    for n in sorted(os.listdir(PKG)):
        if n != "index.html":
            print(f"    {n:<34} {os.path.getsize(os.path.join(PKG,n)):,} B")
    print(f"\nOK  ZIP: {zp}  ({os.path.getsize(zp)/1024:,.0f} KB)")
    print(f"\nرمز سند  : {doc_pw}")
    print(f"رمز سرور : {srv_pw}  (کاربر: {SRV_USER})"
          + ("   <- تصادفی تولید شد" if srv_generated else ""))
    print(f"اعتبارنامه‌ها در: {cred}")
    print("  (این فایل در .gitignore است و commit نمی‌شود)")
    print(f"لینک     : https://{SUBDOMAIN}.{DOMAIN}/")


if __name__ == "__main__":
    main()
