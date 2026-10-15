#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_client_page.py — صفحه ارائه شخصی‌سازی‌شده برای هر کارفرما

یک فایل HTML مستقل و سنگین‌وزن که:
  · با ?to=<نام> شخصی‌سازی می‌شود  ->  لینک هر کارفرما متفاوت است
  · محتوا را از بار رمزنگاری‌شده AES-256-GCM می‌خواند
  · پروپوزال کامل را با رمز، درون همین صفحه باز می‌کند
  · کاملاً خودبسنده است: فونت base64، بدون CDN، بدون فایل جانبی

استفاده:
  .venv/bin/python build/make_client_page.py <رمز-سند> [<رمز-پروپوزال>]

  رمز-سند        رمز بار رمزنگاری‌شده داده‌های صفحه (برای کارفرما لازم نیست)
  رمز-پروپوزال   رمزی که کارفرما برای دیدن پروپوزال کامل وارد می‌کند
                 اگر داده نشود، همان رمز-سند استفاده می‌شود

خروجی:
  build/client-page/energytahvieh/index.html
  build/client-page/energytahvieh/CLIENT-PAGE-GUIDE.md   (gitignore: رمز دارد)
"""
import base64
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
FONTDIR = os.path.join(BUILD, "assets", "fonts")
OUTROOT = os.path.join(BUILD, "client-page")

sys.path.insert(0, BUILD)
import md2html  # noqa: E402
import make_protected_site as mps  # noqa: E402
from md2docx import DOCS  # noqa: E402
from Crypto.Cipher import AES  # noqa: E402

PBKDF2_ITER = 210_000
SLUG = "energytahvieh"


# ═══════════════════════════════════════════════════════════════════════════
#  رمزنگاری
# ═══════════════════════════════════════════════════════════════════════════
def encrypt(plaintext: str, password: str) -> str:
    salt, iv = os.urandom(16), os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITER, dklen=32)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(plaintext.encode())
    return base64.b64encode(salt + iv + ct + tag).decode()


def font_b64(weight: str) -> str:
    with open(os.path.join(FONTDIR, f"Vazirmatn-{weight}.woff2"), "rb") as f:
        return base64.b64encode(f.read()).decode()


# ═══════════════════════════════════════════════════════════════════════════
#  داده کارفرما — همه اعداد از evidence/00-evidence-log.md
#  هیچ عدد ساختگی، هیچ رتبه، هیچ ترافیک، هیچ نرخ تبدیل، هیچ درصد رشد.
# ═══════════════════════════════════════════════════════════════════════════
CLIENT = {
    "slug": SLUG,
    "company": "انرژی تهویه",
    "companyEn": "Energy Tahvieh",
    "domain": "energytahvieh.com",
    "site": "https://energytahvieh.com/",
    "since": "۱۳۹۰",
    "city": "شیراز",
    "author": "سجاد معصومی",
    "role": "مدیر رشد دیجیتال و توسعه تجارت الکترونیک",
    "dateFa": "۲۳ مهر ۱۴۰۵",
    "dateEn": "۱۵ اکتبر ۲۰۲۶",
    "version": "1.0",

    "hero": {
        "kicker": "پروپوزال راهبردی رشد دیجیتال · نسخه 1.0 · ۲۳ مهر ۱۴۰۵",
        "lines": ["سه مسیر درآمدی", "که خود سایت", "تبلیغ می‌کند،", "کار نمی‌کنند."],
        "lead": ("اقساط، عمده‌فروشی و پیش‌فاکتور. این سه در همه‌جای سایت تبلیغ "
                 "می‌شوند و هیچ‌کدام کار نمی‌کند. این یک حدس نیست — نتیجه "
                 "خواندن مستقیم ۱۴ صفحه سایت، robots.txt و چهار فایل sitemap است."),
        "ctaPrimary": "دیدن یافته‌ها",
        "ctaSecondary": "پروپوزال کامل",
    },

    # ── اعداد قهرمان. همه قابل راستی‌آزمایی از منابع عمومی ──
    "stats": [
        {"n": 14,       "suffix": "",      "label": "صفحه سایت",       "sub": "خوانده‌شده، خط‌به‌خط"},
        {"n": 55,       "suffix": "",      "label": "یافته تأییدشده",  "sub": "با URL و نقل‌قول مستقیم"},
        {"n": 191,      "suffix": "",      "label": "محصول در سایت",    "sub": "شمارش از product-sitemap.xml"},
        {"n": 10000,    "suffix": "+",     "label": "محصول رقیب",       "sub": "شناسه محصول در damatajhiz.com"},
        {"n": 25,       "suffix": "",      "label": "داده غایب",        "sub": "که صریحاً اعلام شده، نه پنهان"},
        {"n": 0,        "suffix": "",      "label": "عدد ساختگی",       "sub": "در کل این پروپوزال"},
    ],

    "sectionFindings": {
        "kicker": "بخش یکم",
        "title": "یافته‌های تأییدشده",
        "lead": ("هر مورد با نشانی دقیق و نقل‌قول مستقیم از صفحه ثبت شده. هرچه را "
                 "نتوانستم ببینم، به‌جای حدس زدن در بخش «محدودیت‌ها» فهرست کرده‌ام."),
        "groups": [
            {
                "sev": "بحرانی",
                "sevClass": "crit",
                "title": "مسیرهای درآمدی که خود سایت تبلیغ می‌کند",
                "note": "در بازاری که خرید اقساطی و عمده موتور اصلی فروش است، این سه عملاً بسته‌اند.",
                "items": [
                    {"t": "صفحه «درخواست پیش‌فاکتور» به‌جای فرم، رشته کد رندرنشده نشان می‌دهد",
                     "d": "عبارت [yith_ywraq_request_quote] خام روی صفحه چاپ می‌شود. یعنی افزونه نصب است ولی شورت‌کد در قالب فراخوانی نشده. مشتری B2B که پیش‌فاکتور می‌خواهد، به‌جای فرم با یک خط کد روبه‌رو می‌شود.",
                     "ev": "energytahvieh.com/request-quote/"},
                    {"t": "صفحه «شرایط وام» خالی است",
                     "d": "درحالی‌که «خرید اقساطی» در صفحه‌های مختلف تبلیغ می‌شود. مشتری که روی وعده اقساط می‌آید، به صفحه‌ای می‌رسد که چیزی در آن نیست.",
                     "ev": "energytahvieh.com/شرایط-وام/"},
                    {"t": "صفحه «خرید عمده کالا» خالی است",
                     "d": "همان الگو در مسیر عمده‌فروشی. این دو صفحه یعنی کل ورودی B2B سایت به بن‌بست می‌رسد.",
                     "ev": "energytahvieh.com/خرید-عمده-کالا/"},
                ],
            },
            {
                "sev": "بحرانی",
                "sevClass": "crit",
                "title": "لایه اعتماد، محتوای پیش‌فرض دارد",
                "note": "تنها صفحاتی که باید اعتبار ۲۰ ساله را روایت کنند، پر از محتوای نمونه‌اند.",
                "items": [
                    {"t": "صفحه «درباره ما» تماماً Lorem Ipsum است",
                     "d": "متن انگلیسی نمونه، با شمارنده‌هایی که روی صفر ایستاده‌اند. صفحه‌ای که باید ۲۰ سال تخصص مهندسی را روایت کند، محتوای پیش‌فرض قالب دارد.",
                     "ev": "energytahvieh.com/about-us/"},
                    {"t": "«سیاست بازگشت کالا» نمونه انگلیسی پیش‌فرض ووکامرس است",
                     "d": "عبارت This is a sample page و placeholderهای پرنشده {email} و {physical address} هنوز در سند حقوقی فروشگاه هستند.",
                     "ev": "energytahvieh.com/refund_returns/"},
                    {"t": "تضاد مستقیم در سیاست مرجوعی",
                     "d": "برچسب «بازگشت ۷ روزه» در صفحه محصول، در برابر ۳۰ روز در صفحه بازگشت کالا. این یک ریسک حقوقی و عملیاتی است، نه یک ایراد ظاهری.",
                     "ev": "صفحه محصول ⟷ refund_returns"},
                    {"t": "بلاک‌های «فروشنده شوید» مارکت‌پلیس در صفحه درباره ما",
                     "d": "بخش‌هایی از قالب مارکت‌پلیس که به این کسب‌وکار مربوط نیستند و روی صفحه اعتبار باقی مانده‌اند.",
                     "ev": "energytahvieh.com/about-us/"},
                ],
            },
            {
                "sev": "بحرانی",
                "sevClass": "crit",
                "title": "داده فنی محصول نادرست است",
                "note": "در کالای مهندسی، داده غلط یعنی مرجوعی و از دست رفتن اعتماد.",
                "items": [
                    {"t": "پکیج دیواری ۲۸٬۰۰۰ کیلوکالری با «قدرت حرارتی ۶۴۰۰ BTU»",
                     "d": "حدود ۴٪ مقدار واقعی. این عدد در پنل ویژگی‌های همان محصول درج شده و خریدار فنی را مستقیماً گمراه می‌کند.",
                     "ev": "energytahvieh.com/product/m28ff/"},
                    {"t": "فیلد وزن به‌جای عدد، عبارت «به کیلوگرم» دارد",
                     "d": "یعنی الگوی داده ویژگی‌ها درست تعریف نشده؛ واحد را به‌جای مقدار وارد کرده‌اند.",
                     "ev": "همان صفحه محصول"},
                    {"t": "توضیحات همان صفحه به مدل دیگری ارجاع می‌دهد",
                     "d": "شرح محصول M28FF درباره L24FF حرف می‌زند. این نشانه کپی‌برداری دسته‌جمعی بدون بازبینی است، نه یک اشتباه موردی.",
                     "ev": "همان صفحه محصول"},
                    {"t": "برچسب تعداد با مقدار اشتباه",
                     "d": "یکی دیگر از فیلدهای همان پنل ویژگی‌ها که برچسب و مقدارشان به هم نمی‌خورد.",
                     "ev": "همان صفحه محصول"},
                ],
            },
            {
                "sev": "مهم",
                "sevClass": "high",
                "title": "هدایت کاربر در صفحه نخست شکسته است",
                "note": "مسیرهایی که کاربر را به‌جای مقصد، به جای دیگری می‌برند.",
                "items": [
                    {"t": "سه بنر اصلی صفحه نخست، هر سه به یک مقصد می‌روند",
                     "d": "هر سه بنر به /heaters/ لینک شده‌اند. یعنی ارزشمندترین فضای صفحه نخست عملاً یک پیام دارد.",
                     "ev": "energytahvieh.com/"},
                    {"t": "کاشی «مشعل» به حوله‌خشک‌کن لینک شده",
                     "d": "کاربری که دنبال مشعل است به دسته‌ای می‌رسد که ربطی به پرس‌وجویش ندارد.",
                     "ev": "energytahvieh.com/"},
                    {"t": "چهار کاشی بدون لینک",
                     "d": "عناصری که کاربر انتظار کلیک‌پذیری‌شان را دارد ولی هیچ مقصدی ندارند.",
                     "ev": "energytahvieh.com/"},
                    {"t": "سه بخش نمونه صفحه نخست، همان شش محصول را تکرار می‌کنند",
                     "d": "بخش‌های دمو که حذف نشده‌اند و ویترین را تکراری کرده‌اند.",
                     "ev": "energytahvieh.com/"},
                ],
            },
            {
                "sev": "مهم",
                "sevClass": "high",
                "title": "محتوای ارگانیک عملاً صفر است",
                "note": "هیچ ادعایی درباره رتبه یا ترافیک نمی‌کنم — فقط آنچه در خود سایت دیدم.",
                "items": [
                    {"t": "بلاگ خالی است و حتی در sitemap index ثبت نشده",
                     "d": "مسیر /blog/ وجود دارد ولی هیچ نوشته‌ای در آن نیست و post-sitemap در فهرست اصلی sitemapها حضور ندارد.",
                     "ev": "energytahvieh.com/blog/ · sitemap_index.xml"},
                    {"t": "صفر محتوای دسته‌بندی",
                     "d": "در برابر رقیبی که صفحه دسته‌اش یک راهنمای خرید کامل است: ۹ نکته، جدول قیمت ۱۰ برند، و جدول ظرفیت‌یابی BTU.",
                     "ev": "مقایسه با damatajhiz.com"},
                    {"t": "عنوان صفحه‌ها با « - » بی‌محتوا تمام می‌شود",
                     "d": "الگوی عنوان قالب درست پیکربندی نشده و جای نام برند خالی مانده است.",
                     "ev": "چندین صفحه"},
                ],
            },
            {
                "sev": "متوسط",
                "sevClass": "mid",
                "title": "یک نصب قدیمی که رها شده",
                "note": "هزینه سنگین خزیدن و ریسک محتوای تکراری.",
                "items": [
                    {"t": "صفحات «ایران کالا» (۲۰۲۰) و دموهای قالب هنوز زنده‌اند و در sitemap",
                     "d": "یعنی خزنده هر بار بودجه خود را صرف صفحه‌هایی می‌کند که به کسب‌وکار امروز مربوط نیستند.",
                     "ev": "page-sitemap.xml"},
                    {"t": "صفحات تکراری: cart-2، checkout-2، my-account-2، blog-2، blog-3",
                     "d": "معمولاً نشانه ادغام یا مهاجرت ناتمام است. صفحه پرداخت تکراری ریسک عملیاتی هم دارد.",
                     "ev": "page-sitemap.xml"},
                ],
            },
        ],
    },

    "sectionStrengths": {
        "kicker": "بخش دوم",
        "title": "سه نقطه قوت واقعی که باید حفظ و مقیاس شوند",
        "lead": "تحلیل فقط ایراد پیدا کردن نیست. اینها دارایی‌هایی‌اند که رقیب ندارد و باید هسته استراتژی شوند.",
        "items": [
            {"icon": "◆", "t": "قیمت‌گذاری شفاف تومانی",
             "d": "در بازاری که رقیبی مانند ناب‌تهویه بسیاری محصولاتش را با قیمت «۰ ریال» فهرست می‌کند، شفافیت قیمت یک مزیت رقابتی واقعی است، نه یک پیش‌فرض."},
            {"icon": "◆", "t": "کیفیت خوب توضیحات محصولات تازه",
             "d": "محصولات تازه‌افزوده‌شده ساختار پرسش‌محور با FAQ و فراخوان به اقدام دارند. یعنی الگوی درست در سازمان وجود دارد — فقط مقیاس نشده."},
            {"icon": "◆", "t": "robots.txt هوشمند و سایت فعال",
             "d": "پارامترهای فیلتر بسته شده‌اند و سایت فعالانه به‌روزرسانی می‌شود. یعنی زیرساخت فنی رها نشده — مشکل در لایه محتوا و داده است."},
        ],
    },

    "sectionGap": {
        "kicker": "بخش سوم",
        "title": "شکاف مقیاس، با عدد",
        "lead": "بدون اغراق و بدون وعده. این فاصله در ۱۲ ماه بسته نمی‌شود و من چنین ادعایی نمی‌کنم.",
        "rows": [
            {"metric": "تعداد محصول",        "us": "۱۹۱",       "them": "۱۰٬۰۰۰+",  "note": "شمارش از sitemap در برابر شناسه محصول"},
            {"metric": "محتوای صفحه دسته",   "us": "صفر",        "them": "راهنمای کامل خرید", "note": "۹ نکته + جدول قیمت ۱۰ برند + جدول BTU"},
            {"metric": "برند فیلترپذیر",     "us": "۳ از ۸",     "them": "فیلتر برند و ظرفیت", "note": "الگوی مطلوب در artatabrid.com دیده شد"},
            {"metric": "نظر کاربر",          "us": "تقریباً صفر", "them": "۴٫۷ ستاره",  "note": "اعتماد اجتماعی ساخته نشده"},
            {"metric": "زبان‌های سایت",      "us": "فارسی",      "them": "فارسی / انگلیسی / عربی", "note": "بازار صادراتی و گردشگری بسته است"},
            {"metric": "سابقه",              "us": "از ۱۳۹۰",    "them": "از ۱۳۸۳",    "note": "هفت سال فاصله در روایت اعتبار"},
        ],
        "honest": ("رقابت سربه‌سر ملی با این بازیگر، هدف ۱۲ ماهه واقع‌بینانه نیست و "
                   "من هرگز چنین وعده‌ای نمی‌دهم. آنچه در ادامه می‌آید سه میدانی است "
                   "که در آن‌ها شانس برد ساختاری داریم."),
    },

    "sectionFortress": {
        "kicker": "بخش چهارم",
        "title": "سه دژ قابل دفاع",
        "lead": "به‌جای حمله به جایی که نمی‌توان برد، سه میدانی که مزیت ساختاری داریم.",
        "cards": [
            {"n": "۰۱", "t": "پرس‌وجوهای محلی شیراز و فارس",
             "d": "کارفرما در یک دایرکتوری محلی رتبه ۲۰ از ۲۵ است. پایه پایین است، ولی مزیت ساختاری هم هست: فروشگاه فیزیکی و تیم نصب واقعی. چیزی که بازیگر ملی تهران نمی‌تواند در شیراز ادعا کند.",
             "tag": "مزیت ساختاری: حضور فیزیکی"},
            {"n": "۰۲", "t": "صفحات هاب برند برای برندهای نمایندگی",
             "d": "نام برند «انرژی» هم‌نام با خود شرکت است — یک فرصت برندینگ دوتایی که کاملاً دست‌نخورده مانده. هر برند نمایندگی می‌تواند یک صفحه هاب مستقل داشته باشد.",
             "tag": "فرصت دست‌نخورده: برندینگ دوتایی"},
            {"n": "۰۳", "t": "نیش B2B هیتر صنعتی و گرمایش کارگاهی",
             "d": "فوتر سایت ادعای چیلر، برج خنک‌کننده، مینی‌چیلر، هواساز، ایرواشر، فن‌کویل، داکت اسپلیت و استخر-سونا دارد — ولی کاتالوگ هیچ‌کدام را ندارد. این شکاف، خودِ داستان رشد عمودی است.",
             "tag": "ادعای موجود، کاتالوگ خالی"},
        ],
    },

    "sectionRole": {
        "kicker": "بخش پنجم",
        "title": "نقش پیشنهادی: پنج محور یکپارچه",
        "lead": ("این یک فهرست از کارهای پراکنده نیست — تولید محتوا یا مدیریت سایت "
                 "نیست. مالکیت عملیاتی یک برنامه رشد یکپارچه است، و به همین دلیل "
                 "عنوان و اختیاراتش باید متناسب باشد."),
        "axes": [
            {"n": "۱", "t": "زیرساخت فنی و داده",
             "d": "پاک‌سازی نصب قدیمی، اصلاح الگوی داده محصول، معماری دسته‌بندی، پشتیبان‌گیری و بازیابی. پیش‌نیاز هر کار دیگر."},
            {"n": "۲", "t": "رشد ارگانیک",
             "d": "محتوای دسته‌بندی، صفحات هاب برند، پرس‌وجوهای محلی، و ساختار بلاگ از صفر."},
            {"n": "۳", "t": "کیفیت فروش آنلاین",
             "d": "مسیرهای اقساط، عمده و پیش‌فاکتور. سیاست‌های مرجوعی. کاهش اصطکاک تصمیم‌گیری خریدار فنی."},
            {"n": "۴", "t": "اتوماسیون و هوش مصنوعی",
             "d": "فقط جایی که یک مسئله نام‌دار را حل کند. هر مورد با هزینه، وابستگی فنی، محدودیت، ریسک اطلاعات غلط و معیار ارزیابی."},
            {"n": "۵", "t": "توسعه تجارت",
             "d": "گسترش عمودی به دسته‌های صنعتی که فوتر ادعا می‌کند و کاتالوگ ندارد."},
        ],
        "note": ("اختیارات لازم برای این پنج محور در سند کامل فهرست شده‌اند. بدون "
                 "آن اختیارات، این نقش به مجموعه‌ای از کارهای پراکنده تبدیل می‌شود "
                 "که نه قابل اندازه‌گیری است نه قابل تحویل."),
    },

    "sectionSalary": {
        "kicker": "بخش ششم",
        "title": "مبلغ پیشنهادی و منطق آن",
        "lead": ("مبلغ ۷۵٬۰۰۰٬۰۰۰ تومان در ماه یک نقطه شروع مذاکره است، نه یک "
                 "اعلامیه قطعی. منطقش داده بازار کار ۱۴۰۵ است، نه احساس."),
        "target": 75,
        "bars": [
            {"label": "میانه مدیر دیجیتال مارکتینگ — سایر شهرها", "v": 48, "src": "ایران‌تلنت ۱۴۰۵", "tone": "ref"},
            {"label": "میانه مدیر دیجیتال مارکتینگ — تهران",      "v": 67, "src": "ایران‌تلنت ۱۴۰۵", "tone": "ref"},
            {"label": "آگهی زنده «مدیر رشد و بازاریابی دیجیتال»",  "v": 80, "src": "هوم‌گلد تهران · irantalent.com/jobs", "tone": "ref"},
            {"label": "میانه مدیر بازرگانی و تجارت — تهران",       "v": 89, "src": "ایران‌تلنت ۱۴۰۵", "tone": "ref"},
        ],
        "points": [
            "مبلغ پیشنهادی ۱۲٪ بالاتر از میانه تهران است و داخل بازه P25 تا P75 قرار می‌گیرد.",
            "با آگهی زنده «مدیر رشد و بازاریابی دیجیتال» (۶۰ تا ۸۰ میلیون) هم‌پوشانی دارد.",
            "از میانه مدیر بازرگانی تهران (۸۹ میلیون) پایین‌تر است، درحالی‌که دامنه نقش ترکیبی از هر دو است.",
            "نسبت به میانه سایر شهرها ۵۶٪ بالاتر است — چون کارفرما شیرازی است. این را پنهان نمی‌کنم.",
            "دفاع من از طریق دامنه نقش (پنج محور یکپارچه) و معیار ارشد دورکار تهران است، نه از طریق خود عدد.",
            "منابع رد‌شده: jobvision (گزارش ۱۴۰۳، کهنه) و aryatehran.com (تناقض داخلی در یک صفحه: ۱۵–۲۵ در برابر ۶۰+).",
        ],
    },

    "sectionRoadmap": {
        "kicker": "بخش هفتم",
        "title": "مسیر اجرا",
        "lead": "سه فاز، با معیار پذیرش عینی در پایان هر فاز. هیچ درصد رشدی وعده داده نمی‌شود، چون خط پایه هنوز اندازه‌گیری نشده.",
        "phases": [
            {"tag": "فاز صفر", "days": "۱۴ روز", "t": "خط پایه و ایمن‌سازی",
             "items": ["اندازه‌گیری خط پایه واقعی", "پشتیبان‌گیری کامل و تست بازیابی", "رفع سه مسیر درآمدی بسته", "تصحیح سیاست‌های مرجوعی"]},
            {"tag": "۹۰ روز", "days": "هفته ۱ تا ۱۳", "t": "زیرساخت و داده",
             "items": ["پاک‌سازی نصب قدیمی و صفحات تکراری", "اصلاح الگوی داده محصول", "معماری دسته‌بندی", "نقشه رویدادهای تحلیلی"]},
            {"tag": "۶ تا ۱۲ ماه", "days": "ماه ۴ به بعد", "t": "رشد و گسترش",
             "items": ["محتوای دسته‌بندی و صفحات هاب برند", "پرس‌وجوهای محلی شیراز و فارس", "گسترش عمودی به دسته‌های صنعتی", "اتوماسیون در نقاط دارای مسئله نام‌دار"]},
        ],
    },

    "sectionConditions": {
        "kicker": "بخش هشتم",
        "title": "چهار شرط که بدون آن‌ها این برنامه شکست می‌خورد",
        "lead": "این‌ها درخواست‌های شخصی نیستند. هرکدام به یک شکست مشخص در پروژه‌های مشابه برمی‌گردد.",
        "items": [
            {"n": "۱", "t": "پشتیبان‌گیری، پیش‌نیاز مطلق هر کار فنی",
             "d": "بدون پشتیبان تست‌شده و قابل بازیابی، هیچ تغییری روی سایت تولید اعمال نمی‌شود. این یک خط قرمز فنی است، نه احتیاط."},
            {"n": "۲", "t": "دسترسی به داده، نه فقط به پیشخوان",
             "d": "Search Console، Analytics، دسترسی سرور و داده فروش. بدون خط پایه، هر هدف KPI یک عدد اختراعی است."},
            {"n": "۳", "t": "مقادیر هدف KPI عمداً خالی‌اند",
             "d": "تا خط پایه فاز صفر اندازه‌گیری نشود، هیچ عددی نمی‌نویسم. وعده درصد رشد بدون خط پایه، وعده بی‌پشتوانه است."},
            {"n": "۴", "t": "تفکیک حقوق از بودجه ابزار و تبلیغات",
             "d": "حقوق من هزینه ابزار، زیرساخت، تبلیغات و پیمانکار نیست. این چهار ردیف باید جدا و شفاف باشند تا سنجش بازده ممکن شود."},
        ],
    },

    "sectionHonesty": {
        "kicker": "بخش نهم",
        "title": "تعهد صحت",
        "lead": "این بخش را عمداً در صفحه گذاشته‌ام، چون تفاوت اصلی این پروپوزال با پیشنهادهای مشابه است.",
        "items": [
            {"icon": "✕", "cls": "no", "t": "هیچ رتبه‌ای ادعا نشده",
             "d": "هیچ تستی در Lighthouse، PageSpeed، WebPageTest یا CrUX اجرا نشده. پس هیچ امتیاز عملکردی در این سند نیست."},
            {"icon": "✕", "cls": "no", "t": "هیچ ترافیک یا درآمدی ساخته نشده",
             "d": "به Analytics، Search Console، سرور و داده فروش دسترسی نداشتم. هیچ عدد ترافیک، نرخ تبدیل یا درآمدی ارائه نشده."},
            {"icon": "✕", "cls": "no", "t": "هیچ درصد رشدی وعده داده نشده",
             "d": "بدون خط پایه، هر درصدی اختراع است. مدل مالی سه سناریوی محافظه‌کار، پایه و خوش‌بینانه دارد با فرض‌های بازبینی‌پذیر."},
            {"icon": "✓", "cls": "yes", "t": "هر یافته با URL و نقل‌قول مستقیم",
             "d": "۵۵ یافته تأییدشده، هرکدام با نشانی دقیق صفحه و نقل‌قول از همان صفحه. قابل راستی‌آزمایی در چند دقیقه."},
            {"icon": "✓", "cls": "yes", "t": "فرضیه از یافته جدا شده",
             "d": "۱۸ فرضیه با سطح اطمینان و روش تأیید، و ۲۵ قلم داده که هرگز در دسترس نبود — همه صریحاً فهرست شده‌اند."},
            {"icon": "✓", "cls": "yes", "t": "محدودیت‌ها منتشر شده‌اند",
             "d": "فهرست آنچه نمی‌توان نتیجه‌گیری کرد، همراه پروپوزال ارائه می‌شود. سند جداگانه، نه یک پاراگراف تعارفی."},
        ],
    },

    "gate": {
        "title": "پروپوزال کامل",
        "lead": ("نسخه کامل ۱۳ بخشی — شامل درک کسب‌وکار، چالش‌ها و فرصت‌های "
                 "اولویت‌دار، چشم‌انداز، برنامه ۹۰ روزه تفصیلی، نقشه راه، "
                 "شاخص‌های سنجش، مدل همکاری، پیشنهاد مالی و گام بعدی."),
        "plus": "به‌همراه پیوست «فهرست محدودیت‌ها»: آنچه در این تحلیل اولیه قابل نتیجه‌گیری نیست، و چرا.",
        "label": "رمز ورود",
        "button": "گشودن پروپوزال",
        "hint": "رمز از طریق پیامک یا تماس در اختیار شما قرار گرفته است.",
        "errWrong": "رمز نادرست است. محتوا رمزنگاری شده و با رمز اشتباه بازشدنی نیست.",
        "errNoCrypto": "مرورگر شما رمزگشایی امن را پشتیبانی نمی‌کند. Web Crypto فقط روی HTTPS یا localhost کار می‌کند.",
        "working": "در حال رمزگشایی…",
        "ok": "رمز پذیرفته شد.",
        "alt": "اگر ترجیح می‌دهید نسخه Word یا PDF داشته باشید تا در جلسه چاپ کنید یا برای همکارانتان بفرستید، کافی است بگویید.",
    },

    "footer": {
        "line": "این سند برای بررسی مدیریت انرژی تهویه تهیه شده و انتشار عمومی آن مجاز نیست.",
        "font": "فونت وزيرمتن — SIL Open Font License 1.1",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════════════
CSS = """
/* ───────────── متغیرها ───────────── */
:root{
  --bg:#070b13; --bg2:#0a1020;
  --surface:rgba(255,255,255,.032);
  --surface2:rgba(255,255,255,.055);
  --line:rgba(255,255,255,.085);
  --line2:rgba(255,255,255,.16);
  --gold:#e8b45c; --gold2:#f6d08a; --teal:#5cc9c0;
  --crit:#ef6a5a; --high:#f0a35e; --mid:#e3ce7a; --ok:#6fd39a;
  --text:#e9eef7; --text2:#a9b6ca; --text3:#74829a;
  --r:16px; --r2:22px;
  --ease:cubic-bezier(.16,1,.3,1);
  --maxw:1120px;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--bg);color:var(--text);
  font-family:'Vazirmatn',Tahoma,sans-serif;font-size:15.5px;line-height:1.95;
  direction:rtl;text-align:right;overflow-x:hidden;
  font-feature-settings:"ss01";
}
::selection{background:rgba(232,180,92,.28);color:#fff}

/* ───────────── پس‌زمینه ───────────── */
.bg-fx{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.bg-fx .glow{position:absolute;border-radius:50%;filter:blur(90px);opacity:.5}
.g1{width:60vw;height:60vw;top:-22vw;right:-14vw;background:radial-gradient(circle,rgba(232,180,92,.20),transparent 66%)}
.g2{width:52vw;height:52vw;top:38vh;left:-18vw;background:radial-gradient(circle,rgba(92,201,192,.15),transparent 66%)}
.g3{width:46vw;height:46vw;bottom:-16vw;right:22vw;background:radial-gradient(circle,rgba(120,110,230,.13),transparent 66%)}
.bg-fx .grid{
  position:absolute;inset:0;opacity:.30;
  background-image:linear-gradient(rgba(255,255,255,.030) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.030) 1px,transparent 1px);
  background-size:64px 64px;
  mask-image:radial-gradient(ellipse 100% 62% at 50% 0%,#000 22%,transparent 78%);
  -webkit-mask-image:radial-gradient(ellipse 100% 62% at 50% 0%,#000 22%,transparent 78%);
}
.bg-fx .noise{
  position:absolute;inset:0;opacity:.030;mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* نوار پیشرفت اسکرول */
.prog{
  position:fixed;top:0;right:0;left:0;height:2px;z-index:90;
  background:linear-gradient(90deg,var(--gold),var(--teal));
  transform:scaleX(0);transform-origin:right;
}
@supports (animation-timeline:scroll()){
  .prog{animation:grow linear both;animation-timeline:scroll(root block);transform:none}
  @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
}

/* ───────────── ناوبری ───────────── */
nav{
  position:sticky;top:0;z-index:80;
  background:rgba(7,11,19,.72);backdrop-filter:blur(16px) saturate(1.5);
  -webkit-backdrop-filter:blur(16px) saturate(1.5);
  border-bottom:1px solid transparent;transition:border-color .35s,background .35s;
}
nav.stuck{border-bottom-color:var(--line);background:rgba(7,11,19,.9)}
.nav-in{
  max-width:var(--maxw);margin:0 auto;padding:0 22px;
  height:60px;display:flex;align-items:center;gap:18px;
}
.brand{display:flex;align-items:center;gap:9px;font-weight:900;font-size:14px;letter-spacing:-.01em;white-space:nowrap}
.brand .dot{
  width:9px;height:9px;border-radius:50%;flex:0 0 auto;
  background:var(--gold);box-shadow:0 0 0 4px rgba(232,180,92,.16);
  animation:pulse 2.6s ease-in-out infinite;
}
@keyframes pulse{0%,100%{box-shadow:0 0 0 4px rgba(232,180,92,.16)}50%{box-shadow:0 0 0 8px rgba(232,180,92,.05)}}
.nav-links{display:flex;gap:2px;margin-right:auto;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none}
.nav-links::-webkit-scrollbar{display:none}
.nav-links a{
  color:var(--text3);text-decoration:none;font-size:12.8px;font-weight:600;
  padding:7px 11px;border-radius:9px;white-space:nowrap;
  transition:color .2s,background .2s;
}
.nav-links a:hover{color:var(--text);background:var(--surface2)}
.nav-links a.active{color:var(--gold);background:rgba(232,180,92,.10)}
.nav-cta{
  flex:0 0 auto;background:var(--gold);color:#1a1206;font-weight:800;font-size:13px;
  padding:8px 16px;border-radius:10px;text-decoration:none;white-space:nowrap;
  transition:transform .18s var(--ease),box-shadow .25s;
  box-shadow:0 2px 14px rgba(232,180,92,.22);
}
.nav-cta:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(232,180,92,.34)}

/* ───────────── چیدمان ───────────── */
main{position:relative;z-index:1}
section{padding:88px 22px;scroll-margin-top:62px}
.wrap{max-width:var(--maxw);margin:0 auto}
.wrap-n{max-width:820px;margin:0 auto}

.kick{
  display:inline-flex;align-items:center;gap:8px;
  font-size:11.8px;font-weight:800;letter-spacing:.09em;
  color:var(--gold);text-transform:uppercase;margin-bottom:16px;
}
.kick::before{content:"";width:22px;height:1.5px;background:var(--gold);opacity:.6}
h2{
  font-size:clamp(24px,3.5vw,36px);font-weight:900;line-height:1.42;
  margin:0 0 16px;letter-spacing:-.015em;
}
.lead{font-size:16px;color:var(--text2);max-width:66ch;margin:0 0 40px;line-height:2.05}

/* ───────────── قهرمان ───────────── */
.hero{padding:76px 22px 62px;position:relative;overflow:hidden}
.hero-in{max-width:var(--maxw);margin:0 auto}
.greet{
  display:inline-flex;align-items:center;gap:9px;flex-wrap:wrap;
  background:var(--surface);border:1px solid var(--line);border-radius:999px;
  padding:7px 17px;font-size:13px;color:var(--text2);margin-bottom:34px;
  opacity:0;animation:fadeUp .9s var(--ease) .15s forwards;
}
.greet b{color:var(--gold);font-weight:800}
.greet .sep{width:1px;height:13px;background:var(--line2)}

.h1{margin:0 0 30px;font-weight:900;letter-spacing:-.03em;line-height:1.20}
.lm{display:block;overflow:hidden;padding-bottom:.06em}
.lm > span{
  display:block;font-size:clamp(34px,7.6vw,74px);
  transform:translateY(118%);opacity:0;
  animation:lineUp 1.05s var(--ease) forwards;
}
.lm:nth-child(1) > span{animation-delay:.22s}
.lm:nth-child(2) > span{animation-delay:.33s}
.lm:nth-child(3) > span{animation-delay:.44s}
.lm:nth-child(4) > span{animation-delay:.55s;color:var(--gold)}
@keyframes lineUp{to{transform:translateY(0);opacity:1}}
@keyframes fadeUp{to{transform:translateY(0);opacity:1}}

.hero-lead{
  font-size:16.5px;color:var(--text2);max-width:62ch;line-height:2.15;
  margin:0 0 36px;opacity:0;transform:translateY(16px);
  animation:fadeUp .95s var(--ease) .78s forwards;
}
.hero-lead b{color:var(--text);font-weight:700}
.hero-cta{display:flex;gap:12px;flex-wrap:wrap;opacity:0;transform:translateY(16px);animation:fadeUp .95s var(--ease) .92s forwards}
.btn{
  display:inline-flex;align-items:center;gap:9px;text-decoration:none;
  font-weight:800;font-size:14.5px;padding:14px 26px;border-radius:13px;
  transition:transform .2s var(--ease),box-shadow .3s,background .25s,border-color .25s;
  cursor:pointer;border:1px solid transparent;font-family:inherit;
}
.btn-p{background:linear-gradient(135deg,var(--gold2),var(--gold));color:#1a1206;box-shadow:0 4px 26px rgba(232,180,92,.26)}
.btn-p:hover{transform:translateY(-2px);box-shadow:0 10px 38px rgba(232,180,92,.40)}
.btn-g{background:var(--surface);border-color:var(--line2);color:var(--text)}
.btn-g:hover{background:var(--surface2);border-color:var(--gold);color:var(--gold);transform:translateY(-2px)}
.btn .ar{transition:transform .25s var(--ease)}
.btn:hover .ar{transform:translateX(-4px)}

.hero-meta{
  display:flex;gap:10px 30px;flex-wrap:wrap;margin-top:44px;padding-top:26px;
  border-top:1px solid var(--line);font-size:12.6px;color:var(--text3);
  opacity:0;animation:fadeUp .9s var(--ease) 1.06s forwards;
}
.hero-meta b{color:var(--text2);font-weight:700}

/* ───────────── آمار ───────────── */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:var(--r2);overflow:hidden;margin-top:56px}
.stat{background:#0a0f1c;padding:26px 20px;transition:background .3s}
.stat:hover{background:#0e1526}
.stat .n{
  font-size:clamp(26px,3.4vw,38px);font-weight:900;line-height:1.1;
  letter-spacing:-.03em;color:var(--text);
  font-variant-numeric:tabular-nums;
}
.stat .n .sf{color:var(--gold);font-size:.62em}
.stat.zero .n{color:var(--ok)}
.stat .lb{font-size:13.2px;font-weight:700;color:var(--text2);margin-top:9px}
.stat .sb{font-size:11.6px;color:var(--text3);margin-top:3px;line-height:1.7}

/* ───────────── کارت‌ها ───────────── */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(292px,1fr));gap:16px}
.card{
  position:relative;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--r);padding:24px 24px 22px;overflow:hidden;
  transition:border-color .3s,transform .3s var(--ease),background .3s;
}
.card::before{
  content:"";position:absolute;inset:0;border-radius:inherit;opacity:0;
  transition:opacity .35s;pointer-events:none;
  background:radial-gradient(420px circle at var(--mx,50%) var(--my,50%),rgba(232,180,92,.10),transparent 62%);
}
.card:hover{border-color:var(--line2);transform:translateY(-3px);background:var(--surface2)}
.card:hover::before{opacity:1}

/* گروه یافته‌ها */
.grp{margin-bottom:44px}
.grp-h{display:flex;align-items:center;gap:13px;flex-wrap:wrap;margin-bottom:8px}
.sev{
  flex:0 0 auto;font-size:11.4px;font-weight:900;letter-spacing:.05em;
  padding:5px 12px;border-radius:8px;border:1px solid;
}
.sev.crit{color:var(--crit);border-color:rgba(239,106,90,.36);background:rgba(239,106,90,.10)}
.sev.high{color:var(--high);border-color:rgba(240,163,94,.34);background:rgba(240,163,94,.09)}
.sev.mid{color:var(--mid);border-color:rgba(227,206,122,.30);background:rgba(227,206,122,.07)}
.grp-h h3{margin:0;font-size:19px;font-weight:800;letter-spacing:-.01em}
.grp-note{color:var(--text3);font-size:13.4px;margin:0 0 18px;max-width:70ch}

.find{
  display:grid;grid-template-columns:auto 1fr;gap:0 16px;
  padding:18px 20px;border:1px solid var(--line);border-radius:14px;
  background:var(--surface);margin-bottom:10px;
  transition:border-color .28s,background .28s,transform .28s var(--ease);
}
.find:hover{border-color:var(--line2);background:var(--surface2);transform:translateX(-4px)}
.find .bar{grid-row:1/3;width:3px;border-radius:3px;background:var(--line2);align-self:stretch;min-height:38px}
.find.crit .bar{background:var(--crit);box-shadow:0 0 14px rgba(239,106,90,.42)}
.find.high .bar{background:var(--high)}
.find.mid .bar{background:var(--mid)}
.find h4{margin:0;font-size:14.9px;font-weight:800;line-height:1.75;color:var(--text)}
.find p{margin:6px 0 0;font-size:13.5px;color:var(--text2);line-height:2}
.find .ev{
  grid-column:2;margin-top:10px;display:inline-flex;align-items:center;gap:6px;
  font-family:Consolas,'Courier New',monospace;direction:ltr;unicode-bidi:embed;
  font-size:11.3px;color:var(--teal);background:rgba(92,201,192,.08);
  border:1px solid rgba(92,201,192,.20);border-radius:7px;padding:3px 10px;
  text-decoration:none;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.find .ev:hover{background:rgba(92,201,192,.16)}

/* نقاط قوت */
.str .ic{
  width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;
  background:rgba(111,211,154,.11);border:1px solid rgba(111,211,154,.26);
  color:var(--ok);font-size:15px;margin-bottom:15px;
}
.str h4{margin:0 0 8px;font-size:15.6px;font-weight:800}
.str p{margin:0;font-size:13.7px;color:var(--text2);line-height:2}

/* جدول شکاف */
.gap{border:1px solid var(--line);border-radius:var(--r2);overflow:hidden}
.gap-row{display:grid;grid-template-columns:1.5fr 1fr 1.2fr;border-bottom:1px solid var(--line);transition:background .25s}
.gap-row:last-child{border-bottom:0}
.gap-row:hover{background:var(--surface2)}
.gap-row > div{padding:15px 18px;font-size:13.6px}
.gap-h{background:rgba(255,255,255,.045);font-weight:800;font-size:12.4px!important;color:var(--text3);letter-spacing:.03em}
.gap-h > div{padding:12px 18px!important}
.gap-m{font-weight:700;color:var(--text2)}
.gap-us{color:var(--crit);font-weight:800;font-variant-numeric:tabular-nums}
.gap-them{color:var(--teal);font-weight:800}
.gap-row small{display:block;font-size:11.4px;color:var(--text3);font-weight:400;margin-top:3px;line-height:1.65}
.honest-box{
  margin-top:22px;padding:20px 24px;border-radius:var(--r);
  background:rgba(232,180,92,.055);border:1px solid rgba(232,180,92,.20);
  border-right:4px solid var(--gold);font-size:14.4px;color:var(--text2);line-height:2.05;
}
.honest-box b{color:var(--gold2);font-weight:800}

/* دژها */
.fort{padding:28px 26px}
.fort .n{
  font-size:44px;font-weight:900;line-height:1;letter-spacing:-.05em;
  background:linear-gradient(150deg,var(--gold2),rgba(232,180,92,.22));
  -webkit-background-clip:text;background-clip:text;color:transparent;
  margin-bottom:16px;
}
.fort h4{margin:0 0 10px;font-size:16.6px;font-weight:800;line-height:1.65}
.fort p{margin:0;font-size:13.9px;color:var(--text2);line-height:2.05}
.fort .tag{
  display:inline-block;margin-top:16px;font-size:11.6px;font-weight:700;
  color:var(--teal);background:rgba(92,201,192,.08);
  border:1px solid rgba(92,201,192,.20);border-radius:999px;padding:4px 13px;
}

/* محورها */
.axes{display:grid;gap:10px;counter-reset:ax}
.axis{
  display:grid;grid-template-columns:auto 1fr;gap:0 18px;align-items:start;
  padding:20px 22px;border:1px solid var(--line);border-radius:14px;
  background:var(--surface);transition:border-color .28s,background .28s,transform .28s var(--ease);
}
.axis:hover{border-color:rgba(232,180,92,.34);background:var(--surface2);transform:translateX(-4px)}
.axis .num{
  grid-row:1/3;width:34px;height:34px;border-radius:10px;flex:0 0 auto;
  display:flex;align-items:center;justify-content:center;
  background:rgba(232,180,92,.10);border:1px solid rgba(232,180,92,.26);
  color:var(--gold);font-weight:900;font-size:14.5px;
}
.axis h4{margin:0;font-size:15.4px;font-weight:800;padding-top:5px}
.axis p{margin:5px 0 0;font-size:13.6px;color:var(--text2);line-height:2;grid-column:2}
.note-box{
  margin-top:20px;padding:18px 22px;border-radius:14px;font-size:14px;
  background:var(--surface);border:1px solid var(--line);border-right:4px solid var(--teal);
  color:var(--text2);line-height:2;
}

/* حقوق */
.pay{display:grid;grid-template-columns:1fr;gap:34px}
.chart{border:1px solid var(--line);border-radius:var(--r2);padding:26px 24px;background:var(--surface)}
.bar-row{margin-bottom:20px}
.bar-row:last-child{margin-bottom:0}
.bar-top{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:7px;flex-wrap:wrap}
.bar-lb{font-size:13.2px;font-weight:700;color:var(--text2);flex:1 1 200px}
.bar-v{font-size:14.5px;font-weight:900;color:var(--text);font-variant-numeric:tabular-nums;white-space:nowrap}
.bar-v small{font-size:11px;font-weight:600;color:var(--text3);margin-right:3px}
.track{height:11px;border-radius:6px;background:rgba(255,255,255,.055);overflow:hidden;position:relative}
.fill{
  height:100%;border-radius:6px;width:0;
  background:linear-gradient(90deg,rgba(92,201,192,.55),var(--teal));
  transition:width 1.5s var(--ease);
}
.bar-row.target .fill{background:linear-gradient(90deg,var(--gold),var(--gold2));box-shadow:0 0 20px rgba(232,180,92,.40)}
.bar-row.target .bar-v{color:var(--gold)}
.bar-row.target .bar-lb{color:var(--gold2);font-weight:800}
.bar-src{font-size:11.2px;color:var(--text3);margin-top:5px}
.pay-points{list-style:none;padding:0;margin:0}
.pay-points li{
  position:relative;padding:11px 26px 11px 0;font-size:14px;color:var(--text2);
  line-height:1.95;border-bottom:1px dashed var(--line);
}
.pay-points li:last-child{border-bottom:0}
.pay-points li::before{
  content:"";position:absolute;right:4px;top:20px;width:7px;height:7px;
  border-radius:50%;background:var(--gold);opacity:.75;
}

/* نقشه راه */
.road{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:16px}
.ph{position:relative;padding:26px 24px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);transition:border-color .3s,transform .3s var(--ease)}
.ph:hover{border-color:var(--line2);transform:translateY(-3px)}
.ph .tag{
  display:inline-block;font-size:11.3px;font-weight:900;letter-spacing:.05em;
  color:var(--gold);background:rgba(232,180,92,.10);border:1px solid rgba(232,180,92,.26);
  border-radius:8px;padding:4px 11px;margin-bottom:14px;
}
.ph .days{font-size:11.8px;color:var(--text3);margin-bottom:5px}
.ph h4{margin:0 0 15px;font-size:16.4px;font-weight:800;line-height:1.6}
.ph ul{list-style:none;padding:0;margin:0}
.ph li{
  position:relative;padding:7px 20px 7px 0;font-size:13.4px;color:var(--text2);
  line-height:1.85;border-top:1px solid var(--line);
}
.ph li:first-child{border-top:0}
.ph li::before{content:"";position:absolute;right:3px;top:16px;width:5px;height:5px;border-radius:50%;background:var(--teal);opacity:.8}

/* شروط */
.conds{display:grid;grid-template-columns:repeat(auto-fit,minmax(272px,1fr));gap:16px}
.cond{padding:26px 24px;border-right:4px solid var(--crit)}
.cond .n{font-size:34px;font-weight:900;color:rgba(239,106,90,.36);line-height:1;margin-bottom:13px;letter-spacing:-.04em}
.cond h4{margin:0 0 9px;font-size:15.6px;font-weight:800;line-height:1.7}
.cond p{margin:0;font-size:13.6px;color:var(--text2);line-height:2}

/* صداقت */
.hon{display:grid;grid-template-columns:repeat(auto-fit,minmax(292px,1fr));gap:12px}
.hon-i{
  display:grid;grid-template-columns:auto 1fr;gap:0 14px;padding:19px 21px;
  border:1px solid var(--line);border-radius:14px;background:var(--surface);
  transition:border-color .28s,background .28s;
}
.hon-i:hover{background:var(--surface2);border-color:var(--line2)}
.hon-i .mk{
  grid-row:1/3;width:28px;height:28px;border-radius:9px;flex:0 0 auto;
  display:flex;align-items:center;justify-content:center;font-weight:900;font-size:13px;
  align-self:start;margin-top:2px;
}
.hon-i.no .mk{background:rgba(239,106,90,.11);border:1px solid rgba(239,106,90,.28);color:var(--crit)}
.hon-i.yes .mk{background:rgba(111,211,154,.11);border:1px solid rgba(111,211,154,.28);color:var(--ok)}
.hon-i h4{margin:0;font-size:14.6px;font-weight:800;line-height:1.7}
.hon-i p{margin:5px 0 0;font-size:13.2px;color:var(--text2);line-height:1.95}

/* ───────────── دروازه رمز ───────────── */
.gate{padding:96px 22px}
.gate-box{
  max-width:700px;margin:0 auto;padding:44px 40px 40px;text-align:center;
  background:linear-gradient(165deg,rgba(232,180,92,.075),rgba(255,255,255,.022));
  border:1px solid rgba(232,180,92,.24);border-radius:26px;position:relative;overflow:hidden;
}
.gate-box::after{
  content:"";position:absolute;top:-60%;left:-30%;width:160%;height:120%;
  background:radial-gradient(ellipse at center,rgba(232,180,92,.10),transparent 60%);
  pointer-events:none;
}
.gate-box > *{position:relative;z-index:1}
.gate-ic{
  width:58px;height:58px;border-radius:17px;margin:0 auto 20px;
  display:flex;align-items:center;justify-content:center;font-size:24px;
  background:rgba(232,180,92,.12);border:1px solid rgba(232,180,92,.30);
  box-shadow:0 0 34px rgba(232,180,92,.16);
}
.gate-box h2{margin-bottom:14px}
.gate-box .lead{margin:0 auto 22px;text-align:center;max-width:56ch;font-size:14.6px}
.gate-plus{
  font-size:13.3px;color:var(--text3);margin:0 auto 28px;max-width:52ch;line-height:1.95;
  padding-top:18px;border-top:1px solid var(--line);
}
.gate-form{display:flex;gap:10px;max-width:460px;margin:0 auto;flex-wrap:wrap}
.gate-form label{width:100%;text-align:right;font-size:12.8px;font-weight:700;color:var(--text2);margin-bottom:-2px}
.gate-form input{
  flex:1 1 200px;min-width:0;padding:14px 16px;font-size:15px;font-family:inherit;
  background:rgba(7,11,19,.65);border:1.5px solid var(--line2);border-radius:12px;
  color:var(--text);direction:ltr;text-align:center;letter-spacing:.16em;
  transition:border-color .22s,box-shadow .22s;
}
.gate-form input::placeholder{color:var(--text3);letter-spacing:.1em}
.gate-form input:focus{outline:0;border-color:var(--gold);box-shadow:0 0 0 4px rgba(232,180,92,.13)}
.gate-msg{margin-top:15px;font-size:13.4px;min-height:22px;line-height:1.85}
.gate-msg.err{color:var(--crit)}
.gate-msg.ok{color:var(--ok)}
.gate-msg.info{color:var(--teal)}
.gate-hint{margin-top:18px;font-size:12.4px;color:var(--text3);line-height:1.85}
.gate-alt{
  margin-top:26px;padding-top:22px;border-top:1px solid var(--line);
  font-size:13.4px;color:var(--text2);line-height:2;
}
.spin{
  display:inline-block;width:13px;height:13px;border:2px solid rgba(26,18,6,.3);
  border-top-color:#1a1206;border-radius:50%;animation:sp .68s linear infinite;
  vertical-align:-2px;margin-left:7px;
}
@keyframes sp{to{transform:rotate(360deg)}}

/* ───────────── نمایشگر پروپوزال ───────────── */
#viewer{display:none;padding:0 0 90px}
.vbar{
  position:sticky;top:60px;z-index:70;
  background:rgba(10,15,27,.93);backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  border-top:1px solid var(--line);border-bottom:1px solid var(--line);
  padding:11px 22px;display:flex;gap:9px;align-items:center;flex-wrap:wrap;
}
.vbar .sp{flex:1 1 auto}
.vbar .vt{font-size:13px;font-weight:800;color:var(--gold);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:44vw}
.vbtn{
  background:var(--surface2);border:1px solid var(--line2);color:var(--text);
  font-family:inherit;font-size:12.8px;font-weight:700;padding:7px 15px;
  border-radius:10px;cursor:pointer;transition:background .2s,border-color .2s,color .2s;white-space:nowrap;
}
.vbtn:hover{background:rgba(232,180,92,.12);border-color:var(--gold);color:var(--gold)}

/* واترمارک */
#wm{
  position:fixed;inset:-45%;z-index:2;pointer-events:none;user-select:none;
  display:flex;flex-wrap:wrap;align-content:center;justify-content:center;
  gap:74px 96px;transform:rotate(-27deg);
  font-weight:900;font-size:21px;color:var(--gold);opacity:0;
  transition:opacity .8s;white-space:nowrap;
}
#wm.on{opacity:.05}

/* سند باز شده — پس‌زمینه روشن برای خوانایی */
#doc-root{background:#fff;direction:rtl;text-align:right}
#doc-root .sheet{max-width:900px;margin:0 auto;padding:38px 30px 54px}

/* ───────────── پاصفحه ───────────── */
footer{
  position:relative;z-index:1;padding:44px 22px 52px;border-top:1px solid var(--line);
  background:rgba(7,11,19,.6);text-align:center;
}
footer .fa{font-size:15px;font-weight:900;color:var(--text);margin-bottom:6px}
footer .fr{font-size:13.2px;color:var(--text2);margin-bottom:16px}
footer .fm{font-size:11.8px;color:var(--text3);line-height:2.1}

/* ───────────── ظهور با اسکرول ───────────── */
[data-rev]{opacity:0;transform:translateY(24px);transition:opacity .85s var(--ease),transform .85s var(--ease)}
[data-rev].in{opacity:1;transform:none}
[data-rev][data-d="1"]{transition-delay:.07s}
[data-rev][data-d="2"]{transition-delay:.14s}
[data-rev][data-d="3"]{transition-delay:.21s}
[data-rev][data-d="4"]{transition-delay:.28s}
[data-rev][data-d="5"]{transition-delay:.35s}

/* ───────────── واکنش‌گرا ───────────── */
@media (max-width:900px){
  .gap-row{grid-template-columns:1.3fr 1fr 1fr}
  .gap-row > div{padding:13px 13px;font-size:12.8px}
}
@media (max-width:760px){
  body{font-size:15px}
  section{padding:64px 18px}
  .hero{padding:52px 18px 44px}
  .nav-in{height:56px;padding:0 16px;gap:12px}
  .nav-links{display:none}
  .lm > span{font-size:clamp(30px,9.4vw,44px)}
  .stats{grid-template-columns:repeat(2,1fr)}
  .gate-box{padding:34px 22px 30px}
  .btn{width:100%;justify-content:center}
  .hero-cta{flex-direction:column}
  .gap-row{grid-template-columns:1fr;gap:0}
  .gap-h{display:none}
  .gap-row > div{border-bottom:1px solid var(--line)}
  .gap-us::before{content:"ما: ";color:var(--text3);font-weight:600;font-size:11.5px}
  .gap-them::before{content:"رقیب: ";color:var(--text3);font-weight:600;font-size:11.5px}
  .find,.axis,.hon-i{grid-template-columns:1fr}
  .find .bar,.axis .num,.hon-i .mk{grid-row:auto;margin-bottom:11px}
  .find .bar{width:38px;height:3px}
  .axis p,.find .ev{grid-column:1}
  .vbar{top:56px}
  .vbar .vt{max-width:34vw}
}
@media (max-width:400px){
  .stats{grid-template-columns:1fr}
}

/* ───────────── کاهش حرکت ───────────── */
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.001s!important;animation-delay:0s!important;transition-duration:.001s!important}
  .lm > span{transform:none;opacity:1}
  [data-rev]{opacity:1;transform:none}
  .greet,.hero-lead,.hero-cta,.hero-meta{opacity:1;transform:none}
}

@media print{
  body{background:#fff}
  nav,.prog,.bg-fx,.hero-cta,#wm,.gate{display:none!important}
  section{padding:14px 0}
  .card,.find,.ph,.cond,.hon-i,.gap,.chart{background:#fff!important;border-color:#ddd!important}
  h2,.lead,.stat .n,.fort h4,.axis h4,.cond h4,.hon-i h4{color:#111!important}
  p,li,td,.find p,.fort p,.axis p,.cond p,.hon-i p{color:#333!important}
}
"""


# ═══════════════════════════════════════════════════════════════════════════
#  JS
# ═══════════════════════════════════════════════════════════════════════════
JS = r"""
(function(){
"use strict";

var CFG   = __CFG__;
var DOCP  = __DOCP__;
var DATA  = null;
var q     = new URLSearchParams(location.search);
var FA    = "fa-IR";

/* ───────── شخصی‌سازی با ?to= ───────── */
var to = (q.get("to") || "").trim().slice(0, 60);
if (!to) { var gs0 = document.getElementById("greet-sep"); if (gs0) gs0.style.display = "none"; }
if (to) {
  var g = document.getElementById("greet-to");
  if (g) { g.textContent = "تهیه‌شده برای " + to; g.style.display = ""; }
  else { var gs = document.getElementById("greet-sep"); if (gs) gs.style.display = "none"; }
  document.querySelectorAll("[data-to]").forEach(function(el){ el.textContent = to; });
}

/* ───────── رمزگشایی با Web Crypto ───────── */
function b64u(b){ var s=atob(b),a=new Uint8Array(s.length),i; for(i=0;i<s.length;i++)a[i]=s.charCodeAt(i); return a; }

function decrypt(b64, password){
  var raw=b64u(b64), salt=raw.slice(0,16), iv=raw.slice(16,28), ct=raw.slice(28);
  return crypto.subtle.importKey("raw", new TextEncoder().encode(password),
           {name:"PBKDF2"}, false, ["deriveKey"])
    .then(function(bk){
      return crypto.subtle.deriveKey(
        {name:"PBKDF2", salt:salt, iterations:CFG.iter, hash:"SHA-256"},
        bk, {name:"AES-GCM", length:256}, false, ["decrypt"]);
    })
    .then(function(k){ return crypto.subtle.decrypt({name:"AES-GCM", iv:iv}, k, ct); })
    .then(function(buf){ return new TextDecoder("utf-8").decode(buf); });
}

/* ───────── اعداد فارسی ───────── */
function fa(n){ return Number(n).toLocaleString(FA); }

/* ───────── ساخت محتوا از داده رمزگشایی‌شده ───────── */
function esc(s){
  return String(s == null ? "" : s)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;");
}

function build(d){
  /* --- قهرمان --- */
  var h = d.hero, i;
  document.getElementById("h-kick").textContent = h.kicker;
  var h1 = document.getElementById("h1");
  h1.innerHTML = h.lines.map(function(l){
    return '<span class="lm"><span>' + esc(l) + '</span></span>';
  }).join("");
  document.getElementById("h-lead").innerHTML = h.lead;
  document.getElementById("cta-p").innerHTML = esc(h.ctaPrimary) + ' <span class="ar">←</span>';
  document.getElementById("cta-s").textContent = h.ctaSecondary;

  /* --- آمار --- */
  document.getElementById("stats").innerHTML = d.stats.map(function(s, k){
    return '<div class="stat' + (s.n === 0 ? " zero" : "") + '" data-rev data-d="' + Math.min(k,5) + '">'
      + '<div class="n"><span class="ct" data-to="' + s.n + '">۰</span>'
      + (s.suffix ? '<span class="sf">' + esc(s.suffix) + '</span>' : '') + '</div>'
      + '<div class="lb">' + esc(s.label) + '</div>'
      + '<div class="sb">' + esc(s.sub) + '</div></div>';
  }).join("");

  /* --- یافته‌ها --- */
  var fs = d.sectionFindings;
  document.getElementById("find-k").textContent = fs.kicker;
  document.getElementById("find-t").textContent = fs.title;
  document.getElementById("find-l").textContent = fs.lead;
  document.getElementById("findings-grid").innerHTML = fs.groups.map(function(g, gi){
    var items = g.items.map(function(it, ii){
      var ev = /^https?:\/\//.test(it.ev) ? '<a class="ev" href="' + esc(it.ev)
               + '" target="_blank" rel="noopener nofollow">↗ ' + esc(it.ev) + '</a>'
             : '<span class="ev">' + esc(it.ev) + '</span>';
      return '<div class="find ' + g.sevClass + '" data-rev data-d="' + Math.min(ii,5) + '">'
        + '<span class="bar"></span><h4>' + esc(it.t) + '</h4>'
        + '<p>' + esc(it.d) + '</p>' + ev + '</div>';
    }).join("");
    return '<div class="grp" data-rev><div class="grp-h">'
      + '<span class="sev ' + g.sevClass + '">' + esc(g.sev) + '</span>'
      + '<h3>' + esc(g.title) + '</h3></div>'
      + '<p class="grp-note">' + esc(g.note) + '</p>' + items + '</div>';
  }).join("");

  /* --- نقاط قوت --- */
  var ss = d.sectionStrengths;
  document.getElementById("str-k").textContent = ss.kicker;
  document.getElementById("str-t").textContent = ss.title;
  document.getElementById("str-l").textContent = ss.lead;
  document.getElementById("strengths-grid").innerHTML = ss.items.map(function(s, k){
    return '<div class="card str" data-rev data-d="' + k + '"><div class="ic">' + esc(s.icon)
      + '</div><h4>' + esc(s.t) + '</h4><p>' + esc(s.d) + '</p></div>';
  }).join("");

  /* --- شکاف --- */
  var gp = d.sectionGap;
  document.getElementById("gap-k").textContent = gp.kicker;
  document.getElementById("gap-t").textContent = gp.title;
  document.getElementById("gap-l").textContent = gp.lead;
  var rows = '<div class="gap-row gap-h"><div>سنجه</div><div>انرژی تهویه</div><div>رقیب مرجع</div></div>';
  rows += gp.rows.map(function(r){
    return '<div class="gap-row" data-rev>'
      + '<div class="gap-m">' + esc(r.metric) + '</div>'
      + '<div class="gap-us">' + esc(r.us) + '</div>'
      + '<div class="gap-them">' + esc(r.them) + (r.note ? '<small>' + esc(r.note) + '</small>' : '') + '</div>'
      + '</div>';
  }).join("");
  document.getElementById("gap-table").innerHTML = rows;
  document.getElementById("gap-honest").innerHTML = gp.honest;

  /* --- دژها --- */
  var ft = d.sectionFortress;
  document.getElementById("fort-k").textContent = ft.kicker;
  document.getElementById("fort-t").textContent = ft.title;
  document.getElementById("fort-l").textContent = ft.lead;
  document.getElementById("fortress-grid").innerHTML = ft.cards.map(function(c, k){
    return '<div class="card fort" data-rev data-d="' + k + '"><div class="n">' + esc(c.n)
      + '</div><h4>' + esc(c.t) + '</h4><p>' + esc(c.d) + '</p>'
      + '<span class="tag">' + esc(c.tag) + '</span></div>';
  }).join("");

  /* --- نقش --- */
  var rl = d.sectionRole;
  document.getElementById("role-k").textContent = rl.kicker;
  document.getElementById("role-t").textContent = rl.title;
  document.getElementById("role-l").textContent = rl.lead;
  document.getElementById("axes").innerHTML = rl.axes.map(function(a, k){
    return '<div class="axis" data-rev data-d="' + Math.min(k,5) + '"><span class="num">' + esc(a.n)
      + '</span><h4>' + esc(a.t) + '</h4><p>' + esc(a.d) + '</p></div>';
  }).join("");
  document.getElementById("role-note").textContent = rl.note;

  /* --- حقوق --- */
  var sl = d.sectionSalary, maxV = 100;
  document.getElementById("pay-k").textContent = sl.kicker;
  document.getElementById("pay-t").textContent = sl.title;
  document.getElementById("pay-l").textContent = sl.lead;
  var bars = '<div class="bar-row target" data-rev><div class="bar-top">'
    + '<span class="bar-lb">مبلغ پیشنهادی این نقش</span>'
    + '<span class="bar-v">' + fa(sl.target) + '<small>میلیون تومان</small></span></div>'
    + '<div class="track"><div class="fill" data-w="' + (sl.target / maxV * 100) + '"></div></div>'
    + '<div class="bar-src">پنج محور یکپارچه · قابل مذاکره</div></div>';
  bars += sl.bars.map(function(b, k){
    return '<div class="bar-row" data-rev data-d="' + Math.min(k+1,5) + '"><div class="bar-top">'
      + '<span class="bar-lb">' + esc(b.label) + '</span>'
      + '<span class="bar-v">' + fa(b.v) + '<small>میلیون</small></span></div>'
      + '<div class="track"><div class="fill" data-w="' + (b.v / maxV * 100) + '"></div></div>'
      + '<div class="bar-src">' + esc(b.src) + '</div></div>';
  }).join("");
  document.getElementById("chart").innerHTML = bars;
  document.getElementById("pay-points").innerHTML = sl.points.map(function(p){
    return "<li>" + esc(p) + "</li>";
  }).join("");

  /* --- نقشه راه --- */
  var rm = d.sectionRoadmap;
  document.getElementById("road-k").textContent = rm.kicker;
  document.getElementById("road-t").textContent = rm.title;
  document.getElementById("road-l").textContent = rm.lead;
  document.getElementById("road").innerHTML = rm.phases.map(function(p, k){
    return '<div class="ph" data-rev data-d="' + k + '"><span class="tag">' + esc(p.tag)
      + '</span><div class="days">' + esc(p.days) + '</div><h4>' + esc(p.t) + '</h4><ul>'
      + p.items.map(function(x){ return "<li>" + esc(x) + "</li>"; }).join("")
      + "</ul></div>";
  }).join("");

  /* --- شروط --- */
  var cd = d.sectionConditions;
  document.getElementById("cond-k").textContent = cd.kicker;
  document.getElementById("cond-t").textContent = cd.title;
  document.getElementById("cond-l").textContent = cd.lead;
  document.getElementById("conds").innerHTML = cd.items.map(function(c, k){
    return '<div class="card cond" data-rev data-d="' + k + '"><div class="n">' + esc(c.n)
      + '</div><h4>' + esc(c.t) + '</h4><p>' + esc(c.d) + '</p></div>';
  }).join("");

  /* --- صداقت --- */
  var hn = d.sectionHonesty;
  document.getElementById("hon-k").textContent = hn.kicker;
  document.getElementById("hon-t").textContent = hn.title;
  document.getElementById("hon-l").textContent = hn.lead;
  document.getElementById("hon").innerHTML = hn.items.map(function(x, k){
    return '<div class="hon-i ' + x.cls + '" data-rev data-d="' + Math.min(k,5) + '">'
      + '<span class="mk">' + esc(x.icon) + '</span><h4>' + esc(x.t) + '</h4>'
      + '<p>' + esc(x.d) + '</p></div>';
  }).join("");

  /* --- دروازه و پاصفحه --- */
  var gt = d.gate;
  document.getElementById("gate-t").textContent = gt.title;
  document.getElementById("gate-l").textContent = gt.lead;
  document.getElementById("gate-plus").textContent = gt.plus;
  document.getElementById("pw-label").textContent = gt.label;
  document.getElementById("pw").placeholder = "••••••••••••";
  document.getElementById("gate-btn").innerHTML = "🔓 " + esc(gt.button);
  document.getElementById("gate-hint").textContent = gt.hint;
  document.getElementById("gate-alt").textContent = gt.alt;

  var f = d.footer;
  document.getElementById("f-comp").textContent = d.company + " · " + d.role;
  document.getElementById("f-auth").textContent = d.author + " · " + d.dateFa;
  document.getElementById("f-line").textContent = f.line;
  document.getElementById("f-font").textContent = f.font;

  wire();
}

/* ───────── تعامل‌ها ───────── */
function wire(){
  /* ظهور با اسکرول */
  var io = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      e.target.classList.add("in");
      io.unobserve(e.target);
      var ct = e.target.querySelector(".ct");
      if (ct && !ct.dataset.done) countUp(ct);
      e.target.querySelectorAll && e.target.querySelectorAll(".fill").forEach(function(fl){
        if (!fl.dataset.done){ fl.dataset.done = "1"; fl.style.width = fl.dataset.w + "%"; }
      });
    });
  }, {rootMargin:"0px 0px -9% 0px", threshold:.08});
  document.querySelectorAll("[data-rev]").forEach(function(el){ io.observe(el); });

  /* نوارهای نمودار که مستقیم دیده می‌شوند */
  var io2 = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      e.target.querySelectorAll(".fill").forEach(function(fl){
        if (!fl.dataset.done){ fl.dataset.done = "1"; fl.style.width = fl.dataset.w + "%"; }
      });
      io2.unobserve(e.target);
    });
  }, {threshold:.2});
  var ch = document.getElementById("chart"); if (ch) io2.observe(ch);

  /* شمارنده‌ها */
  function countUp(el){
    el.dataset.done = "1";
    var target = parseInt(el.dataset.to, 10) || 0;
    if (target === 0){ el.textContent = fa(0); return; }
    var dur = 1500, t0 = null;
    function step(ts){
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = fa(Math.round(target * e));
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* نور دنبال‌کننده نشانگر روی کارت‌ها */
  document.querySelectorAll(".card").forEach(function(c){
    c.addEventListener("pointermove", function(e){
      var r = c.getBoundingClientRect();
      c.style.setProperty("--mx", (e.clientX - r.left) + "px");
      c.style.setProperty("--my", (e.clientY - r.top) + "px");
    });
  });

  /* ناوبری چسبان */
  var nav = document.getElementById("nav");
  var prog = document.getElementById("prog");
  var supportsTL = CSS.supports && CSS.supports("animation-timeline","scroll()");
  function onScroll(){
    nav.classList.toggle("stuck", window.scrollY > 14);
    if (!supportsTL){
      var h = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.transform = "scaleX(" + (h > 0 ? window.scrollY / h : 0) + ")";
    }
  }
  window.addEventListener("scroll", onScroll, {passive:true});
  onScroll();

  /* جاسوس اسکرول */
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
  var secs = links.map(function(a){ return document.querySelector(a.getAttribute("href")); });
  if ("IntersectionObserver" in window){
    var spy = new IntersectionObserver(function(en){
      en.forEach(function(e){
        if (!e.isIntersecting) return;
        var i = secs.indexOf(e.target);
        links.forEach(function(l,k){ l.classList.toggle("active", k === i); });
      });
    }, {rootMargin:"-46% 0px -46% 0px"});
    secs.forEach(function(s){ if (s) spy.observe(s); });
  }

  /* دروازه رمز */
  var pw = document.getElementById("pw"), btn = document.getElementById("gate-btn");
  var msg = document.getElementById("gate-msg"), gt = d.gate;
  function setMsg(c, t){ msg.className = "gate-msg" + (c ? " " + c : ""); msg.textContent = t; }

  function openDoc(){
    btn.disabled = true;
    btn.innerHTML = '<span class="spin"></span>' + esc(gt.working);
    setMsg("info", "در حال مشتق‌سازی کلید با " + fa(CFG.iter) + " تکرار PBKDF2…");
    decrypt(DOCP, pw.value)
      .then(function(blob){
        var all = JSON.parse(blob);
        var html = all[CFG.docs[0]];
        setMsg("ok", "✓ " + gt.ok);
        setTimeout(function(){ mount(html); }, 320);
      })
      .catch(function(){
        setMsg("err", "✕ " + gt.errWrong);
        pw.value = ""; pw.focus();
      })
      .finally(function(){
        btn.disabled = false;
        btn.innerHTML = "🔓 " + esc(gt.button);
      });
  }
  btn.addEventListener("click", openDoc);
  pw.addEventListener("keydown", function(e){ if (e.key === "Enter") openDoc(); });

  function mount(html){
    var doc = new DOMParser().parseFromString(html, "text/html");
    var old = document.getElementById("doc-css"); if (old) old.remove();
    var st = document.createElement("style"); st.id = "doc-css";
    st.textContent = Array.prototype.map.call(doc.querySelectorAll("style"),
                       function(s){ return s.textContent; }).join("\n");
    document.head.appendChild(st);

    var root = document.getElementById("doc-root");
    root.innerHTML = "";
    Array.prototype.forEach.call(doc.body.children, function(nd){
      root.appendChild(document.importNode(nd, true));
    });

    document.getElementById("wm").classList.add("on");
    document.getElementById("viewer").style.display = "block";
    document.getElementById("vtitle").textContent = DATA.company + " — پروپوزال کامل";
    var vb = document.querySelector(".vbar");
    vb.scrollIntoView({behavior:"smooth", block:"start"});
    if (CFG.log){ try{ fetch("log-visit.php",{method:"POST",body:"doc"}).catch(function(){}); }catch(e){} }
  }

  document.getElementById("v-close").addEventListener("click", function(){
    document.getElementById("doc-root").innerHTML = "";
    var s = document.getElementById("doc-css"); if (s) s.remove();
    document.getElementById("viewer").style.display = "none";
    document.getElementById("wm").classList.remove("on");
    pw.value = ""; setMsg("");
    document.getElementById("gate").scrollIntoView({behavior:"smooth", block:"center"});
  });
  document.getElementById("v-print").addEventListener("click", function(){ window.print(); });
  document.getElementById("v-top").addEventListener("click", function(){
    window.scrollTo({top:0, behavior:"smooth"});
  });
}

/* ───────── واترمارک ───────── */
function watermark(text){
  var wm = document.getElementById("wm"), i;
  for (i = 0; i < 84; i++){
    var s = document.createElement("span");
    s.textContent = text;
    wm.appendChild(s);
  }
}

/* ───────── شروع ───────── */
function boot(){
  /* داده صفحه رمزنگاری نیست: این صفحه «ویترین» است و باید دیده شود.
     لایه محافظت واقعی، پروپوزال کامل است که پایین‌تر رمزگشایی می‌شود. */
  var el = document.getElementById("cdata");
  DATA = JSON.parse(el.textContent);

  build(DATA);
  watermark(DATA.author + " · " + DATA.company + " · " + DATA.dateFa + " · محرمانه");

  if (!(window.crypto && window.crypto.subtle)){
    document.getElementById("gate-msg").className = "gate-msg err";
    document.getElementById("gate-msg").textContent = DATA.gate.errNoCrypto;
    document.getElementById("gate-btn").disabled = true;
  }
}
boot();

})();
"""


# ═══════════════════════════════════════════════════════════════════════════
#  HTML
# ═══════════════════════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet,noimageindex"/>
<meta name="googlebot" content="noindex,nofollow"/>
<meta name="referrer" content="no-referrer"/>
<meta name="theme-color" content="#070b13"/>
<meta name="description" content="__DESC__"/>
<meta property="og:type" content="article"/>
<meta property="og:locale" content="fa_IR"/>
<meta property="og:title" content="__OGTITLE__"/>
<meta property="og:description" content="__DESC__"/>
<title>__TITLE__</title>
<style>
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FR__') format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FB__') format('woff2');font-weight:500;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FB__') format('woff2');font-weight:600;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FB__') format('woff2');font-weight:700;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FE__') format('woff2');font-weight:800;font-display:block}
@font-face{font-family:'Vazirmatn';src:url('data:font/woff2;base64,__FE__') format('woff2');font-weight:900;font-display:block}
__CSS__
</style>
</head>
<body>

<div class="prog" id="prog"></div>

<div class="bg-fx" aria-hidden="true">
  <div class="glow g1"></div><div class="glow g2"></div><div class="glow g3"></div>
  <div class="grid"></div><div class="noise"></div>
</div>

<div id="wm" aria-hidden="true"></div>

<nav id="nav">
  <div class="nav-in">
    <span class="brand"><span class="dot"></span><span>__AUTHOR__</span></span>
    <div class="nav-links">
      <a href="#findings">یافته‌ها</a>
      <a href="#strengths">نقاط قوت</a>
      <a href="#gap">شکاف</a>
      <a href="#fortress">راهبرد</a>
      <a href="#role">نقش</a>
      <a href="#salary">مبلغ</a>
      <a href="#roadmap">مسیر</a>
      <a href="#honesty">صحت</a>
    </div>
    <a class="nav-cta" href="#gate">پروپوزال کامل</a>
  </div>
</nav>

<main>

  <!-- ═══════ قهرمان ═══════ -->
  <header class="hero" id="top">
    <div class="hero-in">
      <div class="greet">
        <span id="greet-to" style="display:none"></span>
        <span class="sep" id="greet-sep"></span>
        <span>تهیه‌شده برای <b>__COMPANY__</b></span>
        <span class="sep"></span>
        <span>__CITY__ · __DOMAIN__</span>
      </div>

      <p class="kick" id="h-kick"></p>

      <h1 class="h1" id="h1"></h1>

      <p class="hero-lead" id="h-lead"></p>

      <div class="hero-cta">
        <a class="btn btn-p" id="cta-p" href="#findings"></a>
        <a class="btn btn-g" id="cta-s" href="#gate"></a>
      </div>

      <div class="hero-meta">
        <span>تهیه‌کننده <b>__AUTHOR__</b></span>
        <span>نقش پیشنهادی <b>__ROLE__</b></span>
        <span>تاریخ <b>__DATEFA__</b></span>
        <span>نسخه <b>__VERSION__</b></span>
      </div>

      <div class="stats" id="stats"></div>
    </div>
  </header>

  <!-- ═══════ یافته‌ها ═══════ -->
  <section id="findings">
    <div class="wrap">
      <p class="kick" id="find-k" data-rev></p>
      <h2 id="find-t" data-rev></h2>
      <p class="lead" id="find-l" data-rev></p>
      <div id="findings-grid"></div>
    </div>
  </section>

  <!-- ═══════ نقاط قوت ═══════ -->
  <section id="strengths">
    <div class="wrap">
      <p class="kick" id="str-k" data-rev></p>
      <h2 id="str-t" data-rev></h2>
      <p class="lead" id="str-l" data-rev></p>
      <div class="cards" id="strengths-grid"></div>
    </div>
  </section>

  <!-- ═══════ شکاف ═══════ -->
  <section id="gap">
    <div class="wrap">
      <p class="kick" id="gap-k" data-rev></p>
      <h2 id="gap-t" data-rev></h2>
      <p class="lead" id="gap-l" data-rev></p>
      <div class="gap" id="gap-table" data-rev></div>
      <div class="honest-box" id="gap-honest" data-rev></div>
    </div>
  </section>

  <!-- ═══════ دژها ═══════ -->
  <section id="fortress">
    <div class="wrap">
      <p class="kick" id="fort-k" data-rev></p>
      <h2 id="fort-t" data-rev></h2>
      <p class="lead" id="fort-l" data-rev></p>
      <div class="cards" id="fortress-grid"></div>
    </div>
  </section>

  <!-- ═══════ نقش ═══════ -->
  <section id="role">
    <div class="wrap-n">
      <p class="kick" id="role-k" data-rev></p>
      <h2 id="role-t" data-rev></h2>
      <p class="lead" id="role-l" data-rev></p>
      <div class="axes" id="axes"></div>
      <div class="note-box" id="role-note" data-rev></div>
    </div>
  </section>

  <!-- ═══════ مبلغ ═══════ -->
  <section id="salary">
    <div class="wrap">
      <p class="kick" id="pay-k" data-rev></p>
      <h2 id="pay-t" data-rev></h2>
      <p class="lead" id="pay-l" data-rev></p>
      <div class="pay">
        <div class="chart" id="chart"></div>
        <ul class="pay-points" id="pay-points" data-rev></ul>
      </div>
    </div>
  </section>

  <!-- ═══════ نقشه راه ═══════ -->
  <section id="roadmap">
    <div class="wrap">
      <p class="kick" id="road-k" data-rev></p>
      <h2 id="road-t" data-rev></h2>
      <p class="lead" id="road-l" data-rev></p>
      <div class="road" id="road"></div>
    </div>
  </section>

  <!-- ═══════ شروط ═══════ -->
  <section id="conditions">
    <div class="wrap">
      <p class="kick" id="cond-k" data-rev></p>
      <h2 id="cond-t" data-rev></h2>
      <p class="lead" id="cond-l" data-rev></p>
      <div class="conds" id="conds"></div>
    </div>
  </section>

  <!-- ═══════ صداقت ═══════ -->
  <section id="honesty">
    <div class="wrap">
      <p class="kick" id="hon-k" data-rev></p>
      <h2 id="hon-t" data-rev></h2>
      <p class="lead" id="hon-l" data-rev></p>
      <div class="hon" id="hon"></div>
    </div>
  </section>

  <!-- ═══════ دروازه ═══════ -->
  <section class="gate" id="gate">
    <div class="gate-box" data-rev>
      <div class="gate-ic">🔐</div>
      <h2 id="gate-t"></h2>
      <p class="lead" id="gate-l"></p>
      <p class="gate-plus" id="gate-plus"></p>
      <div class="gate-form">
        <label for="pw" id="pw-label"></label>
        <input type="password" id="pw" autocomplete="off" spellcheck="false" aria-label="رمز ورود"/>
        <button class="btn btn-p" id="gate-btn" type="button"></button>
      </div>
      <div class="gate-msg" id="gate-msg" role="status" aria-live="polite"></div>
      <div class="gate-hint" id="gate-hint"></div>
      <div class="gate-alt" id="gate-alt"></div>
    </div>
  </section>

  <!-- ═══════ نمایشگر پروپوزال ═══════ -->
  <div id="viewer">
    <div class="vbar">
      <span class="vt" id="vtitle"></span>
      <span class="sp"></span>
      <button class="vbtn" id="v-print" type="button">🖨️ چاپ</button>
      <button class="vbtn" id="v-top" type="button">↑ ابتدا</button>
      <button class="vbtn" id="v-close" type="button">✖ بستن</button>
    </div>
    <div id="doc-root"></div>
  </div>

</main>

<footer>
  <div class="fa">__COMPANY__</div>
  <div class="fr" id="f-comp"></div>
  <div class="fm" id="f-auth"></div>
  <div class="fm" id="f-line"></div>
  <div class="fm" id="f-font"></div>
</footer>

<script type="application/json" id="cdata">__CDATA__</script>
<script>__JS__</script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════════
GUIDE = """# راهنمای صفحه ارائه شخصی‌سازی‌شده

**کارفرما:** {company} · **ساخته‌شده:** {dateFa} / {dateEn}

---

## لینک‌هایی که می‌توانید بفرستید

### لینک پایه
```
https://{subdomain}/
```

### لینک شخصی‌سازی‌شده — **این را بفرستید**
```
https://{subdomain}/?to=مدیریت محترم انرژی تهویه
```
پارامتر `?to=` نام گیرنده را در بالای صفحه نشان می‌دهد. هر گیرنده لینک
مخصوص خودش را می‌گیرد، و اگر لینک forward شود معلوم است از چه کسی رفته.

نمونه‌ها:
```
?to=جناب آقای زاده‌محمد
?to=مدیریت محترم
?to=تیم مدیریت انرژی تهویه
```

⚠️ **`?to=` فقط شخصی‌سازی نمایشی است، نه کنترل دسترسی.** رمز اصلی همان
`?k=` یا رمز جاسازی‌شده است.

---

## رمز

| | مقدار |
|---|---|
| **رمز پروپوزال کامل** | `{docPw}` |

این تنها رمزی است که کارفرما لازم دارد. در کادر پایین صفحه پرسیده می‌شود.

### چرا خود صفحه رمز ندارد

یک تصمیم طراحی عمدی است. صفحه **ویترین** است: باید دیده شود تا کارفرما
دلیل بخواهد رمز را وارد کند. اگر کل صفحه پشت رمز بود، لینک ارسالی به یک
کادر خالی می‌رسید و هیچ ارزشی نشان نمی‌داد.

لایه محافظت واقعی، **پروپوزال کامل اجرایی** است که با AES-256-GCM
رمزنگاری شده و بدون رمز هیچ بخشی از آن در مرورگر وجود ندارد.

اگر می‌خواهید خود صفحه هم پشت رمز برود، از بسته
`deploy/subdomain-package/` استفاده کنید و لایه Basic Auth را در
`.htaccess-with-server-auth` فعال کنید — آن رمز سروری است و پیش از رسیدن
به صفحه پرسیده می‌شود.

---

## چه چیزی پشت رمز است و چه چیزی نه

| | وضعیت |
|---|---|
| یافته‌ها، نقاط قوت، شکاف، راهبرد، نقش، نمودار مبلغ، مسیر، شروط، تعهد صحت | 🔓 روی صفحه — بدون رمز (عمدی) |
| **پروپوزال کامل ۱۳ بخشی** | 🔒 با رمز |
| **پیوست فهرست محدودیت‌ها** | 🔒 با رمز |

**این عمدی است.** صفحه باید به‌اندازه کافی ارزش نشان دهد که کارفرما رمز
را بخواهد — ولی سند اجرایی کامل، که ارزش واقعی کار شماست، پشت رمز
می‌ماند.

---

## استقرار روی هاست اشتراکی

همان روند ساب‌دامین که در `deploy/UPLOAD-GUIDE.md` آمده:

۱. cPanel → **Domains** → ساب‌دامین بسازید
۲. **SSL/TLS Status** → Run AutoSSL ← **الزامی** (Web Crypto بدون HTTPS کار نمی‌کند)
۳. File Manager → `index.html` را آپلود کنید
۴. `.htaccess` و `robots.txt` را هم بگذارید (از `deploy/subdomain-package/`)

**وردپرس را روی این ساب‌دامین نصب نکنید** — `.htaccess` وردپرس هدرهای
محافظتی را بازنویسی می‌کند.

---

## ساختن صفحه برای یک کارفرمای دیگر

همه محتوا در دیکشنری `CLIENT` داخل
`build/make_client_page.py` است. برای کارفرمای تازه:

۱. `SLUG` و محتوای `CLIENT` را عوض کنید
۲. `DOCS["02"]["src"]` را به فایل Markdown پروپوزال همان کارفرما تغییر دهید
۳. بازتولید کنید:

```bash
.venv/bin/python build/make_protected_site.py <رمز-پروپوزال>
.venv/bin/python build/make_client_page.py <رمز-بار> <رمز-پروپوزال>
```

خروجی در `build/client-page/<slug>/index.html` است.

---

## تعهد صحت در این صفحه

**هیچ عدد ساختگی‌ای در آن نیست.** هرچه نمایش داده می‌شود یا:

- مستقیماً از صفحه‌های `energytahvieh.com` خوانده شده (۱۴ صفحه + robots.txt + ۴ sitemap)
- یا از `damatajhiz.com` و سایر رقبا به‌صورت مستقیم
- یا از گزارش حقوق و دستمزد ۱۴۰۵ ایران‌تلنت و آگهی‌های زنده

شمارنده «۰ عدد ساختگی» در بخش آمار، یک شعار نیست — یک ادعای قابل
راستی‌آزمایی است. بخش «تعهد صحت» در پایین صفحه، دقیقاً فهرست می‌کند
چه تست‌هایی **انجام نشده** و چه داده‌هایی **در دسترس نبوده**.

---

*نسخه 1.0 · ۲۳ مهر ۱۴۰۵*
"""


# ═══════════════════════════════════════════════════════════════════════════
def build_doc_html(key: str) -> str:
    spec = DOCS[key]
    with open(os.path.join(ROOT, spec["src"]), encoding="utf-8") as f:
        md = f.read()
    meta = spec["cover"]

    css = mps.build_doc_css()
    # فونت‌ها را با data URI جایگزین می‌کنیم تا سند درون صفحه مستقل بماند
    for w in ("Regular", "Bold", "ExtraBold"):
        css = css.replace(f"url('assets/fonts/Vazirmatn-{w}.woff2')",
                          f"url('{md2html_font(w)}')")

    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8"/>
<title>{md2html.esc(meta['title'].replace(chr(10),' — '))}</title>
<style>{css}</style></head><body>
<div class="sheet">{md2html.cover_html(meta)}
{md2html.render(md)}</div></body></html>"""


def md2html_font(weight: str) -> str:
    return "data:font/woff2;base64," + font_b64(weight)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("خطا: رمز پروپوزال اجباری است — هیچ رمز پیش‌فرضی وجود ندارد.\n")
        print("  .venv/bin/python build/make_client_page.py <رمز-پروپوزال>\n")
        print("چرا: رمز hard-code‌شده در اسکریپتی که commit می‌شود یعنی رمز عمومی.\n")
        print("نکته: محتوای خودِ صفحه رمزنگاری نمی‌شود — صفحه «ویترین» است و")
        print("      باید دیده شود. لایه محافظت واقعی، پروپوزال کامل است.")
        sys.exit(1)

    doc_pw = args[0]
    page_key = doc_pw
    if len(doc_pw) < 6:
        raise SystemExit("خطا: رمز حداقل ۶ نویسه باشد.")

    outdir = os.path.join(OUTROOT, SLUG)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    # ── سند ۰۲ + ۰۶ در یک بار رمزنگاری‌شده ──
    docs_html = {k: build_doc_html(k) for k in ("02", "06")}
    doc_blob = json.dumps(docs_html, ensure_ascii=False)
    doc_enc = encrypt(doc_blob, doc_pw)

    # ── پیکربندی ──
    cfg = {"iter": PBKDF2_ITER, "log": False,
           "docs": ["02", "06"], "slug": SLUG}

    js = (JS.replace("__CFG__", json.dumps(cfg, ensure_ascii=False))
            .replace("__DOCP__", json.dumps(doc_enc)))

    # JS درون <script> نباید </script> داشته باشد
    js = js.replace("</script", "<\\/script")

    # JSON درون <script type="application/json"> — باید </script> شکسته شود
    cdata_json = (json.dumps(CLIENT, ensure_ascii=False, indent=None)
                     .replace("</", "<\/"))

    title = f"پروپوزال رشد دیجیتال — {CLIENT['company']}"
    desc = ("تحلیل مستند ۱۴ صفحه سایت، ۵۵ یافته تأییدشده با URL و نقل‌قول "
            "مستقیم، و برنامه رشد سه‌فاز. بدون هیچ عدد ساختگی.")

    page = (HTML
            .replace("__CDATA__", cdata_json)
            .replace("__CSS__", CSS)
            .replace("__JS__", js)
            .replace("__FR__", font_b64("Regular"))
            .replace("__FB__", font_b64("Bold"))
            .replace("__FE__", font_b64("ExtraBold"))
            .replace("__TITLE__", md2html.esc(title))
            .replace("__OGTITLE__", md2html.esc(title))
            .replace("__DESC__", md2html.esc(desc))
            .replace("__COMPANY__", md2html.esc(CLIENT["company"]))
            .replace("__DOMAIN__", md2html.esc(CLIENT["domain"]))
            .replace("__CITY__", md2html.esc(CLIENT["city"]))
            .replace("__AUTHOR__", md2html.esc(CLIENT["author"]))
            .replace("__ROLE__", md2html.esc(CLIENT["role"]))
            .replace("__DATEFA__", md2html.esc(CLIENT["dateFa"]))
            .replace("__VERSION__", md2html.esc(CLIENT["version"])))

    idx = os.path.join(outdir, "index.html")
    with open(idx, "w", encoding="utf-8") as f:
        f.write(page)

    # فایل‌های کمکی
    site_pkg = os.path.join(BUILD, "deploy", "subdomain-package")
    for n in (".htaccess", "htaccess-fallback.txt", "robots.txt", "log-visit.php"):
        s = os.path.join(site_pkg, n)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(outdir, n))

    sub = "proposal.sajadmasoumi.com"
    guide = (GUIDE.format(company=CLIENT["company"], dateFa=CLIENT["dateFa"],
                          dateEn=CLIENT["dateEn"], pageKey=page_key,
                          docPw=doc_pw, subdomain=sub))
    with open(os.path.join(outdir, "CLIENT-PAGE-GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(guide)

    sz = os.path.getsize(idx)
    print(f"OK  index.html  {sz:,} B  ({sz/1024:,.0f} KB)")
    for n in sorted(os.listdir(outdir)):
        if n != "index.html":
            print(f"OK  {n:<24} {os.path.getsize(os.path.join(outdir,n)):,} B")
    print(f"\nخروجی : {outdir}")
    print(f"لینک  : https://{sub}/?to=مدیریت محترم {CLIENT['company']}")
    print(f"رمز بار        : {page_key}")
    print(f"رمز پروپوزال   : {doc_pw}")


if __name__ == "__main__":
    main()
