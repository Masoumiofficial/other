#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_showcase.py — صفحه ارائه تمام‌صفحه‌ای برای کارفرما

یک فایل HTML مستقل. بدون رمز، بدون پروپوزال رمزنگاری‌شده، بدون فایل جانبی.
فونت‌ها base64 جاسازی شده‌اند، پس آفلاین هم درست کار می‌کند.

  .venv/bin/python build/make_showcase.py

خروجی: build/showcase/index.html
"""
import base64
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
FONTDIR = os.path.join(BUILD, "assets", "fonts")
OUT = os.path.join(BUILD, "showcase")

# وزن‌هایی که جاسازی می‌شوند — نظام تایپوگرافیک کامل
WEIGHTS = {300: "Light", 400: "Regular", 600: "SemiBold",
           700: "Bold", 800: "ExtraBold", 900: "Black"}


def font_uri(weight_name):
    with open(os.path.join(FONTDIR, f"Vazirmatn-{weight_name}.woff2"), "rb") as f:
        return "data:font/woff2;base64," + base64.b64encode(f.read()).decode()


def esc(s):
    import html
    return html.escape(str(s), quote=False)


# ═══════════════════════════════════════════════════════════════════════════
#  داده — همه اعداد از evidence/00-evidence-log.md
#  هیچ عدد ساختگی، هیچ رتبه، هیچ ترافیک، هیچ نرخ تبدیل، هیچ درصد رشد.
# ═══════════════════════════════════════════════════════════════════════════
DATA = {
    "company": "انرژی تهویه",
    "domain": "energytahvieh.com",
    "site": "https://energytahvieh.com/",
    "city": "شیراز",
    "since": "۱۳۹۰",
    "author": "سجاد معصومی",
    "role": "مدیر رشد دیجیتال و توسعه تجارت الکترونیک",
    "dateFa": "۲۳ مهر ۱۴۰۵",
    "dateEn": "۱۵ اکتبر ۲۰۲۶",
    "version": "2.0",

    "hero": {
        "kicker": "تحلیل اولیه و پروپوزال همکاری · نسخه 2.0",
        "lines": ["سه مسیر درآمدی", "که خود سایت", "تبلیغ می‌کند،", "کار نمی‌کنند."],
        "lead": ("اقساط، عمده‌فروشی و پیش‌فاکتور. هر سه در جای‌جای سایت تبلیغ "
                 "می‌شوند و هیچ‌کدام کار نمی‌کند. این یک حدس نیست — نتیجه "
                 "خواندن مستقیم ۱۴ صفحه سایت، robots.txt و چهار فایل sitemap است، "
                 "بدون هیچ دسترسی داخلی."),
        "ctaPrimary": "دیدن یافته‌ها",
        "ctaSecondary": "گام بعدی",
    },

    "stats": [
        {"n": 14,    "suffix": "",   "label": "صفحه سایت",       "sub": "خوانده‌شده، خط‌به‌خط"},
        {"n": 55,    "suffix": "",   "label": "یافته تأییدشده",  "sub": "با URL و نقل‌قول مستقیم"},
        {"n": 191,   "suffix": "",   "label": "محصول در سایت",    "sub": "شمارش از product-sitemap.xml"},
        {"n": 10000, "suffix": "+",  "label": "محصول رقیب",       "sub": "شناسه محصول در damatajhiz.com"},
        {"n": 25,    "suffix": "",   "label": "داده غایب",        "sub": "صریحاً اعلام‌شده، نه پنهان"},
        {"n": 0,     "suffix": "",   "label": "عدد ساختگی",       "sub": "در کل این پروپوزال"},
    ],

    "marquee": ["پیش‌فاکتور", "اقساط", "عمده‌فروشی", "داده فنی محصول", "صفحه درباره ما",
                "سیاست مرجوعی", "محتوای دسته‌بندی", "نصب قدیمی", "هدایت صفحه نخست",
                "بلاگ", "اعتماد", "B2B"],

    "findings": {
        "num": "۰۱", "kicker": "بخش یکم",
        "title": "یافته‌های تأییدشده",
        "lead": ("هر مورد با نشانی دقیق صفحه و نقل‌قول مستقیم از همان صفحه ثبت شده. "
                 "هرچه را نتوانستم ببینم، به‌جای حدس زدن در بخش تعهد صحت فهرست کرده‌ام."),
        "filters": ["همه", "بحرانی", "مهم", "متوسط"],
        "groups": [
            {"sev": "بحرانی", "cls": "crit", "title": "مسیرهای درآمدی که خود سایت تبلیغ می‌کند",
             "note": "در بازاری که خرید اقساطی و عمده موتور اصلی فروش است، این سه عملاً بسته‌اند.",
             "items": [
                 {"t": "صفحه «درخواست پیش‌فاکتور» به‌جای فرم، رشته کد رندرنشده نشان می‌دهد",
                  "d": "عبارت [yith_ywraq_request_quote] خام روی صفحه چاپ می‌شود. یعنی افزونه نصب است ولی شورت‌کد در قالب فراخوانی نشده. مشتری B2B که پیش‌فاکتور می‌خواهد، به‌جای فرم با یک خط کد روبه‌رو می‌شود.",
                  "ev": "energytahvieh.com/request-quote/",
                  "url": "https://energytahvieh.com/request-quote/"},
                 {"t": "صفحه «شرایط وام» خالی است",
                  "d": "درحالی‌که «خرید اقساطی» در صفحه‌های مختلف تبلیغ می‌شود. مشتری که روی وعده اقساط می‌آید، به صفحه‌ای می‌رسد که چیزی در آن نیست.",
                  "ev": "energytahvieh.com/شرایط-وام/",
                  "url": "https://energytahvieh.com/شرایط-وام/"},
                 {"t": "صفحه «خرید عمده کالا» خالی است",
                  "d": "همان الگو در مسیر عمده‌فروشی. این دو صفحه یعنی کل ورودی B2B سایت به بن‌بست می‌رسد.",
                  "ev": "energytahvieh.com/خرید-عمده-کالا/",
                  "url": "https://energytahvieh.com/خرید-عمده-کالا/"}]},
            {"sev": "بحرانی", "cls": "crit", "title": "لایه اعتماد، محتوای پیش‌فرض دارد",
             "note": "تنها صفحاتی که باید اعتبار ۲۰ ساله را روایت کنند، پر از محتوای نمونه‌اند.",
             "items": [
                 {"t": "صفحه «درباره ما» تماماً Lorem Ipsum است",
                  "d": "متن انگلیسی نمونه، با شمارنده‌هایی که روی صفر ایستاده‌اند. صفحه‌ای که باید ۲۰ سال تخصص مهندسی را روایت کند، محتوای پیش‌فرض قالب دارد.",
                  "ev": "energytahvieh.com/about-us/",
                  "url": "https://energytahvieh.com/about-us/"},
                 {"t": "«سیاست بازگشت کالا» نمونه انگلیسی پیش‌فرض ووکامرس است",
                  "d": "عبارت This is a sample page و placeholderهای پرنشده {email} و {physical address} هنوز در سند حقوقی فروشگاه هستند.",
                  "ev": "energytahvieh.com/refund_returns/",
                  "url": "https://energytahvieh.com/refund_returns/"},
                 {"t": "تضاد مستقیم در سیاست مرجوعی",
                  "d": "برچسب «بازگشت ۷ روزه» در صفحه محصول، در برابر ۳۰ روز در صفحه بازگشت کالا. این یک ریسک حقوقی و عملیاتی است، نه یک ایراد ظاهری.",
                  "ev": "صفحه محصول ⟷ refund_returns", "url": ""},
                 {"t": "بلاک‌های «فروشنده شوید» مارکت‌پلیس در صفحه درباره ما",
                  "d": "بخش‌هایی از قالب مارکت‌پلیس که به این کسب‌وکار مربوط نیستند و روی صفحه اعتبار باقی مانده‌اند.",
                  "ev": "energytahvieh.com/about-us/",
                  "url": "https://energytahvieh.com/about-us/"}]},
            {"sev": "بحرانی", "cls": "crit", "title": "داده فنی محصول نادرست است",
             "note": "در کالای مهندسی، داده غلط یعنی مرجوعی و از دست رفتن اعتماد خریدار فنی.",
             "items": [
                 {"t": "پکیج دیواری ۲۸٬۰۰۰ کیلوکالری با «قدرت حرارتی ۶۴۰۰ BTU»",
                  "d": "حدود ۴٪ مقدار واقعی. این عدد در پنل ویژگی‌های همان محصول درج شده و خریدار فنی را مستقیماً گمراه می‌کند.",
                  "ev": "energytahvieh.com/product/m28ff/",
                  "url": "https://energytahvieh.com/product/m28ff/"},
                 {"t": "فیلد وزن به‌جای عدد، عبارت «به کیلوگرم» دارد",
                  "d": "یعنی الگوی داده ویژگی‌ها درست تعریف نشده؛ واحد را به‌جای مقدار وارد کرده‌اند. این یک اشتباه موردی نیست، یک الگوست.",
                  "ev": "همان صفحه محصول", "url": ""},
                 {"t": "توضیحات همان صفحه به مدل دیگری ارجاع می‌دهد",
                  "d": "شرح محصول M28FF درباره L24FF حرف می‌زند. نشانه کپی‌برداری دسته‌جمعی بدون بازبینی است.",
                  "ev": "همان صفحه محصول", "url": ""},
                 {"t": "برچسب تعداد با مقدار اشتباه",
                  "d": "یکی دیگر از فیلدهای همان پنل ویژگی‌ها که برچسب و مقدارشان به هم نمی‌خورد.",
                  "ev": "همان صفحه محصول", "url": ""}]},
            {"sev": "مهم", "cls": "high", "title": "هدایت کاربر در صفحه نخست شکسته است",
             "note": "مسیرهایی که کاربر را به‌جای مقصد، به جای دیگری می‌برند.",
             "items": [
                 {"t": "سه بنر اصلی صفحه نخست، هر سه به یک مقصد می‌روند",
                  "d": "هر سه بنر به /heaters/ لینک شده‌اند. یعنی ارزشمندترین فضای صفحه نخست عملاً یک پیام دارد.",
                  "ev": "energytahvieh.com/", "url": "https://energytahvieh.com/"},
                 {"t": "کاشی «مشعل» به حوله‌خشک‌کن لینک شده",
                  "d": "کاربری که دنبال مشعل است به دسته‌ای می‌رسد که ربطی به پرس‌وجویش ندارد.",
                  "ev": "energytahvieh.com/", "url": "https://energytahvieh.com/"},
                 {"t": "چهار کاشی بدون لینک",
                  "d": "عناصری که کاربر انتظار کلیک‌پذیری‌شان را دارد ولی هیچ مقصدی ندارند.",
                  "ev": "energytahvieh.com/", "url": "https://energytahvieh.com/"},
                 {"t": "سه بخش نمونه صفحه نخست، همان شش محصول را تکرار می‌کنند",
                  "d": "بخش‌های دموی قالب که حذف نشده‌اند و ویترین را تکراری کرده‌اند.",
                  "ev": "energytahvieh.com/", "url": "https://energytahvieh.com/"}]},
            {"sev": "مهم", "cls": "high", "title": "محتوای ارگانیک عملاً صفر است",
             "note": "هیچ ادعایی درباره رتبه یا ترافیک نمی‌کنم — فقط آنچه در خود سایت دیدم.",
             "items": [
                 {"t": "بلاگ خالی است و حتی در sitemap index ثبت نشده",
                  "d": "مسیر /blog/ وجود دارد ولی هیچ نوشته‌ای در آن نیست و post-sitemap در فهرست اصلی sitemapها حضور ندارد.",
                  "ev": "energytahvieh.com/blog/ · sitemap_index.xml",
                  "url": "https://energytahvieh.com/blog/"},
                 {"t": "صفر محتوای دسته‌بندی",
                  "d": "در برابر رقیبی که صفحه دسته‌اش یک راهنمای خرید کامل است: ۹ نکته، جدول قیمت ۱۰ برند سال ۱۴۰۵، و جدول ظرفیت‌یابی BTU.",
                  "ev": "مقایسه با damatajhiz.com", "url": "https://damatajhiz.com/"},
                 {"t": "عنوان صفحه‌ها با « - » بی‌محتوا تمام می‌شود",
                  "d": "الگوی عنوان قالب درست پیکربندی نشده و جای نام برند خالی مانده است.",
                  "ev": "چندین صفحه", "url": ""}]},
            {"sev": "متوسط", "cls": "mid", "title": "یک نصب قدیمی که رها شده",
             "note": "هزینه سنگین خزیدن و ریسک محتوای تکراری.",
             "items": [
                 {"t": "صفحات «ایران کالا» (۲۰۲۰) و دموهای قالب هنوز زنده‌اند و در sitemap",
                  "d": "یعنی خزنده هر بار بودجه خود را صرف صفحه‌هایی می‌کند که به کسب‌وکار امروز مربوط نیستند.",
                  "ev": "page-sitemap.xml", "url": ""},
                 {"t": "صفحات تکراری: cart-2، checkout-2، my-account-2، blog-2، blog-3",
                  "d": "معمولاً نشانه ادغام یا مهاجرت ناتمام است. صفحه پرداخت تکراری ریسک عملیاتی هم دارد.",
                  "ev": "page-sitemap.xml", "url": ""}]},
        ],
    },

    "strengths": {
        "num": "۰۲", "kicker": "بخش دوم",
        "title": "سه نقطه قوت که باید هسته استراتژی شوند",
        "lead": "تحلیل فقط ایراد پیدا کردن نیست. اینها دارایی‌هایی‌اند که رقیب ندارد.",
        "items": [
            {"icon": "◆", "t": "قیمت‌گذاری شفاف تومانی",
             "d": "در بازاری که بسیاری از فروشگاه‌ها قیمت را اعلام نمی‌کنند یا محصول را با «۰ ریال» فهرست می‌کنند، شفافیت قیمت تومانی یک مزیت رقابتی واقعی است، نه یک پیش‌فرض."},
            {"icon": "◆", "t": "کیفیت خوب توضیحات محصولات تازه",
             "d": "محصولات تازه‌افزوده‌شده ساختار پرسش‌محور با FAQ و فراخوان به اقدام دارند. یعنی الگوی درست در سازمان وجود دارد — فقط مقیاس نشده."},
            {"icon": "◆", "t": "robots.txt هوشمند و سایت فعال",
             "d": "پارامترهای فیلتر بسته شده‌اند و سایت فعالانه به‌روزرسانی می‌شود. یعنی زیرساخت فنی رها نشده — مشکل در لایه محتوا و داده است."},
        ],
    },

    "gap": {
        "num": "۰۳", "kicker": "بخش سوم",
        "title": "شکاف مقیاس، با عدد",
        "lead": "بدون اغراق و بدون وعده. این فاصله در ۱۲ ماه بسته نمی‌شود و من چنین ادعایی نمی‌کنم.",
        "before": {"label": "انرژی تهویه امروز", "tag": "وضعیت موجود"},
        "after": {"label": "رقیب مرجع بازار", "tag": "damatajhiz.com"},
        "rows": [
            {"metric": "تعداد محصول",       "us": "۱۹۱",        "them": "۱۰٬۰۰۰+", "note": "شمارش از sitemap در برابر شناسه محصول"},
            {"metric": "محتوای صفحه دسته",  "us": "صفر",         "them": "راهنمای کامل خرید", "note": "۹ نکته + جدول قیمت ۱۰ برند + جدول BTU"},
            {"metric": "برند فیلترپذیر",    "us": "۳ از ۸",      "them": "فیلتر برند و ظرفیت", "note": "الگوی مطلوب در artatabrid.com دیده شد"},
            {"metric": "نظر کاربر",         "us": "تقریباً صفر",  "them": "۴٫۷ ستاره", "note": "اعتماد اجتماعی ساخته نشده"},
            {"metric": "زبان‌های سایت",     "us": "فارسی",       "them": "فارسی / انگلیسی / عربی", "note": "بازار صادراتی و گردشگری بسته است"},
            {"metric": "سابقه روایت‌شده",   "us": "از ۱۳۹۰",     "them": "از ۱۳۸۳", "note": "هفت سال فاصله در روایت اعتبار"},
        ],
        "honest": ("رقابت سربه‌سر ملی با این بازیگر، هدف ۱۲ ماهه واقع‌بینانه نیست و "
                   "من هرگز چنین وعده‌ای نمی‌دهم. آنچه در ادامه می‌آید سه میدانی است "
                   "که در آن‌ها شانس برد ساختاری داریم."),
    },

    "fortress": {
        "num": "۰۴", "kicker": "بخش چهارم",
        "title": "سه دژ قابل دفاع",
        "lead": "به‌جای حمله به جایی که نمی‌توان برد، سه میدانی که مزیت ساختاری داریم.",
        "cards": [
            {"n": "۰۱", "t": "پرس‌وجوهای محلی شیراز و فارس",
             "d": "رتبه شما در یک دایرکتوری محلی ۲۰ از ۲۵ ثبت شده است. پایه پایین است، ولی مزیت ساختاری هم دارید: فروشگاه فیزیکی و تیم نصب واقعی — چیزی که بازیگر ملی مستقر در تهران نمی‌تواند در شیراز ادعا کند.",
             "tag": "مزیت ساختاری: حضور فیزیکی"},
            {"n": "۰۲", "t": "صفحات هاب برند برای برندهای نمایندگی",
             "d": "نام برند «انرژی» هم‌نام با خود شرکت است — یک فرصت برندینگ دوتایی که کاملاً دست‌نخورده مانده. هر برند نمایندگی می‌تواند یک صفحه هاب مستقل داشته باشد.",
             "tag": "فرصت دست‌نخورده: برندینگ دوتایی"},
            {"n": "۰۳", "t": "نیش B2B هیتر صنعتی و گرمایش کارگاهی",
             "d": "فوتر سایت ادعای چیلر، برج خنک‌کننده، مینی‌چیلر، هواساز، ایرواشر، فن‌کویل، داکت اسپلیت و استخر-سونا دارد — ولی کاتالوگ هیچ‌کدام را ندارد. این شکاف، خودِ داستان رشد عمودی است.",
             "tag": "ادعای موجود، کاتالوگ خالی"},
        ],
    },

    "roleSec": {
        "num": "۰۵", "kicker": "بخش پنجم",
        "title": "نقش پیشنهادی: پنج محور یکپارچه",
        "lead": ("این یک فهرست از کارهای پراکنده نیست — تولید محتوا یا مدیریت سایت "
                 "نیست. مالکیت عملیاتی یک برنامه رشد یکپارچه است."),
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
        "note": ("اختیارات لازم برای این پنج محور باید پیش از شروع روشن شود. بدون "
                 "آن اختیارات، این نقش به مجموعه‌ای از کارهای پراکنده تبدیل می‌شود "
                 "که نه قابل اندازه‌گیری است نه قابل تحویل."),
    },

    "salary": {
        "num": "۰۶", "kicker": "بخش ششم",
        "title": "مبلغ پیشنهادی و منطق آن",
        "lead": ("مبلغ پیشنهادی ۷۵٬۰۰۰٬۰۰۰ تومان در ماه است. مبنای آن داده‌های "
                 "بازار کار ۱۴۰۵ و دامنه واقعی نقش است، نه برآورد شخصی."),
        "target": 75,
        "unit": "میلیون تومان در ماه",
        "bars": [
            {"label": "میانه مدیر دیجیتال مارکتینگ — تهران",            "v": 67, "src": "گزارش حقوق و دستمزد ۱۴۰۵ ایران‌تلنت"},
            {"label": "آگهی زنده «مدیر رشد و بازاریابی دیجیتال» — تهران", "v": 80, "src": "irantalent.com/jobs · بازه اعلامی ۶۰ تا ۸۰"},
            {"label": "میانه مدیر بازرگانی و تجارت — تهران",             "v": 89, "src": "گزارش حقوق و دستمزد ۱۴۰۵ ایران‌تلنت"},
        ],
        "points": [
            "مبلغ پیشنهادی ۱۲٪ بالاتر از میانه مدیر دیجیتال مارکتینگ تهران است.",
            "با بازه اعلامی آگهی‌های زنده «مدیر رشد و بازاریابی دیجیتال» در تهران (۶۰ تا ۸۰ میلیون) هم‌پوشانی دارد.",
            "از میانه مدیر بازرگانی و تجارت تهران (۸۹ میلیون) پایین‌تر است، درحالی‌که دامنه این نقش ترکیبی از هر دو است.",
            "مبنای این عدد دامنه نقش است: پنج محور یکپارچه که هریک به‌تنهایی بخشی از یک شغل تمام‌وقت‌اند.",
            "هر عدد این نمودار از منبع عمومی و تاریخ‌دار گرفته شده و مستقل قابل راستی‌آزمایی است.",
        ],
    },

    "roadmap": {
        "num": "۰۷", "kicker": "بخش هفتم",
        "title": "مسیر اجرا",
        "lead": "سه فاز، با معیار پذیرش عینی در پایان هر فاز. هیچ درصد رشدی وعده داده نمی‌شود، چون خط پایه هنوز اندازه‌گیری نشده.",
        "phases": [
            {"tag": "فاز صفر", "days": "۱۴ روز", "t": "خط پایه و ایمن‌سازی",
             "items": ["اندازه‌گیری خط پایه واقعی", "پشتیبان‌گیری کامل و تست بازیابی",
                       "رفع سه مسیر درآمدی بسته", "تصحیح سیاست‌های مرجوعی"]},
            {"tag": "۹۰ روز", "days": "هفته ۱ تا ۱۳", "t": "زیرساخت و داده",
             "items": ["پاک‌سازی نصب قدیمی و صفحات تکراری", "اصلاح الگوی داده محصول",
                       "معماری دسته‌بندی", "نقشه رویدادهای تحلیلی"]},
            {"tag": "۶ تا ۱۲ ماه", "days": "ماه ۴ به بعد", "t": "رشد و گسترش",
             "items": ["محتوای دسته‌بندی و صفحات هاب برند", "پرس‌وجوهای محلی شیراز و فارس",
                       "گسترش عمودی به دسته‌های صنعتی", "اتوماسیون در نقاط دارای مسئله نام‌دار"]},
        ],
    },

    "conditions": {
        "num": "۰۸", "kicker": "بخش هشتم",
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

    "honesty": {
        "num": "۰۹", "kicker": "بخش نهم",
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
             "d": "فهرست آنچه نمی‌توان نتیجه‌گیری کرد، به‌صورت سند جداگانه همراه این پروپوزال ارائه می‌شود."},
        ],
    },

    "next": {
        "num": "۱۰", "kicker": "بخش دهم",
        "title": "گام بعدی",
        "lead": ("یک جلسه کاری ۹۰ دقیقه‌ای. نه جلسه معرفی، نه ارائه — جلسه‌ای که "
                 "در آن این تحلیل را با داده داخلی شما می‌سنجیم."),
        "agenda": [
            {"n": "۱", "t": "سنجش یافته‌ها با داده داخلی شما",
             "d": "هر یافته را کنار آمار واقعی فروش، مرجوعی و پرسش‌های مشتریان می‌گذاریم تا معلوم شود کدام‌ها اثر تجاری واقعی دارند."},
            {"n": "۲", "t": "تعیین خط پایه",
             "d": "با دسترسی‌هایی که در همان جلسه روشن می‌شود، خط پایه واقعی اندازه‌گیری می‌شود — و تا آن اندازه‌گیری، هیچ هدف KPI نوشته نمی‌شود."},
            {"n": "۳", "t": "روشن کردن دامنه مسئولیت و اختیارات",
             "d": "پنج محور همکاری، مرزهای مشخص، و اختیاراتی که برای تحویل لازم است. بدون این، نقش به کارهای پراکنده تبدیل می‌شود."},
        ],
        "note": ("اگر ترجیح می‌دهید پیش از جلسه، نسخه Word یا PDF این تحلیل را "
                 "داشته باشید تا چاپ کنید یا برای همکارانتان بفرستید، بگویید تا "
                 "ارسال کنم. سند «فهرست محدودیت‌ها» هم همراهش می‌آید."),
    },

    "footer": {
        "line": "این سند برای بررسی مدیریت انرژی تهویه تهیه شده و انتشار عمومی آن مجاز نیست.",
        "font": "فونت وزيرمتن — SIL Open Font License 1.1",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
CSS = r"""
/* ═══════════════ نظام طراحی ═══════════════ */
:root{
  /* کانال‌های RGB — تا مود روشن بتواند همه سایه‌ها را یکجا عوض کند */
  --gold-rgb:240,188,104;  --teal-rgb:99,214,203;
  --crit-rgb:255,114,100;  --high-rgb:255,171,99;
  --mid-rgb:232,214,138;   --ok-rgb:111,224,164;
  --ink-rgb:5,7,13;        --w-rgb:255,255,255; --ov-rgb:255,255,255;
  --orb3-rgb:120,120,240;  --tgtbg-rgb:23,15,4;

  --ink:#05070d; --ink2:#080c15; --ink3:#0b1120;
  --sf:rgba(var(--w-rgb),.030); --sf2:rgba(var(--w-rgb),.055); --sf3:rgba(var(--w-rgb),.085);
  --ln:rgba(var(--w-rgb),.075); --ln2:rgba(var(--w-rgb),.15); --ln3:rgba(var(--w-rgb),.26);
  --gold:#f0bc68; --on-gold:#170f04; --gold2:#ffe0a6; --gold3:#c8963f;
  --teal:#63d6cb; --ice:#a9c8e8;
  --crit:#ff7264; --high:#ffab63; --mid:#e8d68a; --ok:#6fe0a4;
  --t1:#f2f6fc; --t2:#b0bccf; --t3:#7b889e; --t4:#6e7b93;
  /* جو و پس‌زمینه — در مود روشن جداگانه تنظیم می‌شوند */
  --mesh-rgb:255,255,255; --mesh-a:.026; --mesh-op:.30;
  --noise-op:.030; --noise-blend:overlay;
  --vig-op:.75; --vig-inner:transparent;
  --orb1:.55; --orb2:.45; --orb3:.40;
  --fort-end:.20; --shadow-a:.24;

  --e:cubic-bezier(.16,1,.3,1);
  --e2:cubic-bezier(.22,.61,.36,1);
  --mx:1180px; --mn:840px;
  --pad:clamp(18px,4.4vw,26px);
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--ink);color:var(--t1);
  font-family:'Vazirmatn',Tahoma,sans-serif;font-weight:400;
  font-size:15.5px;line-height:1.98;direction:rtl;text-align:right;
  overflow-x:hidden;font-feature-settings:"ss01";
  -webkit-font-smoothing:antialiased;
}
::selection{background:rgba(var(--gold-rgb),.30);color:#fff}
img,svg{max-width:100%}

/* ═══════════════ پس‌زمینه لایه‌ای ═══════════════ */
.fx{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.fx .orb{position:absolute;border-radius:50%;filter:blur(100px);will-change:transform}
.o1{width:66vw;height:66vw;top:-26vw;right:-16vw;opacity:var(--orb1);
    background:radial-gradient(circle,rgba(var(--gold-rgb),.20),transparent 64%);
    animation:drift1 34s ease-in-out infinite}
.o2{width:56vw;height:56vw;top:34vh;left:-20vw;opacity:var(--orb2);
    background:radial-gradient(circle,rgba(var(--teal-rgb),.15),transparent 64%);
    animation:drift2 42s ease-in-out infinite}
.o3{width:48vw;height:48vw;bottom:-18vw;right:20vw;opacity:var(--orb3);
    background:radial-gradient(circle,rgba(var(--orb3-rgb),.13),transparent 64%);
    animation:drift3 38s ease-in-out infinite}
@keyframes drift1{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(-4vw,3vh,0) scale(1.09)}}
@keyframes drift2{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(5vw,-4vh,0) scale(1.12)}}
@keyframes drift3{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(-3vw,-5vh,0) scale(1.07)}}
.fx .mesh{
  position:absolute;inset:0;opacity:var(--mesh-op);
  background-image:linear-gradient(rgba(var(--mesh-rgb),var(--mesh-a)) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(var(--mesh-rgb),var(--mesh-a)) 1px,transparent 1px);
  background-size:72px 72px;
  mask-image:radial-gradient(ellipse 110% 70% at 50% 0%,#000 18%,transparent 76%);
  -webkit-mask-image:radial-gradient(ellipse 110% 70% at 50% 0%,#000 18%,transparent 76%);
}
.fx .noise{
  position:absolute;inset:0;opacity:var(--noise-op);mix-blend-mode:var(--noise-blend);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.82' numOctaves='4'/%3E%3C/filter%3E%3Crect width='150' height='150' filter='url(%23n)'/%3E%3C/svg%3E");
}
.fx .vig{position:absolute;inset:0;background:radial-gradient(ellipse 130% 90% at 50% 40%,var(--vig-inner) 40%,rgba(var(--ink-rgb),var(--vig-op)) 100%)}

/* ═══════════════ مود روشن ═══════════════
   کاغذ گرم — نه سفید مطلق، چون سفید مطلق با لهجه طلایی سرد و بی‌روح
   می‌شود. سطح‌ها لایه‌های «تیره» نیمه‌شفاف روی کاغذند (نه سفید)، پس
   بدترین پس‌زمینه ممکن #e4e3df است و همه رنگ‌ها بر همان پایه تنظیم
   شده‌اند، نه بر کاغذ خالی.

   همه رنگ‌های لهجه و هر چهار پله متن تیره شده‌اند تا کنتراست به
   WCAG AA (۴٫۵:۱ برای متن ریز) برسد. هر ۲۰ جفت متن/پس‌زمینه در
   این مود اندازه‌گیری شده و همه ≥ ۴٫۵:۱ هستند — حتی متن ۱۱ پیکسل.

   نمونه: طلایی مود تیره (#f0bc68) روی کاغذ فقط ۱٫۵۸:۱ است و عملاً
   خوانا نیست، پس به #865d0d تبدیل شد: ۵٫۳۳:۱ روی کاغذ، ۴٫۵۶:۱ روی
   تیره‌ترین سطح، و ۵٫۷۵:۱ با متن سفید روی دکمه. به همین دلیل طلایی
   در این مود به کهربایی/برنزی نزدیک می‌شود — این بهای اجتناب‌ناپذیر
   خوانایی است، نه سهل‌انگاری در انتخاب رنگ. */
[data-theme="light"]{
  --ink:#f6f4ef; --ink2:#fdfcfa; --ink3:#ffffff;
  --sf:rgba(var(--ov-rgb),.028); --sf2:rgba(var(--ov-rgb),.050); --sf3:rgba(var(--ov-rgb),.078);
  --ln:rgba(var(--ov-rgb),.105); --ln2:rgba(var(--ov-rgb),.19); --ln3:rgba(var(--ov-rgb),.32);

  --gold:#865d0d; --gold2:#845e0f; --gold3:#7a5409; --on-gold:#fffdf6;
  --teal:#0d7168; --ice:#3f6488;
  --crit:#b93428; --high:#92570d; --mid:#746413; --ok:#1a7348;

  --t1:#14181f; --t2:#47515e; --t3:#545b66; --t4:#60656e;

  --gold-rgb:134,93,13;  --teal-rgb:13,113,104;
  --crit-rgb:185,52,40;   --high-rgb:146,87,13;
  --mid-rgb:116,100,19;   --ok-rgb:26,115,72;
  --ink-rgb:246,244,239;  --w-rgb:255,255,255; --ov-rgb:20,24,31;
  --orb3-rgb:110,120,220; --tgtbg-rgb:255,253,248;

  --mesh-rgb:20,24,31; --mesh-a:.045; --mesh-op:.42;
  --noise-op:.022; --noise-blend:multiply;
  --vig-op:.55; --vig-inner:transparent;
  --orb1:.30; --orb2:.24; --orb3:.20;
  --fort-end:.34; --shadow-a:.10;
}
/* در مود روشن، لهجه‌ها روی پس‌زمینه روشن باید کمی اشباع‌تر باشند
   تا همان «حس طلایی» حفظ شود */
[data-theme="light"] .st.zero .n{text-shadow:0 0 22px rgba(var(--ok-rgb),.22)}
[data-theme="light"] .card:hover,
[data-theme="light"] .find:hover,
[data-theme="light"] .axis:hover,
[data-theme="light"] .ag:hover,
[data-theme="light"] .ph:hover{box-shadow:0 10px 30px rgba(var(--ov-rgb),.07)}
[data-theme="light"] .btn-p{box-shadow:0 4px 22px rgba(var(--gold-rgb),.28)}
[data-theme="light"] .btn-p:hover{box-shadow:0 12px 36px rgba(var(--gold-rgb),.40)}
[data-theme="light"] .ncta{box-shadow:0 2px 14px rgba(var(--gold-rgb),.26)}
[data-theme="light"] .cmp-hnd{box-shadow:0 0 18px rgba(var(--gold-rgb),.45)}
[data-theme="light"] .cmp-knob{box-shadow:0 4px 22px rgba(var(--gold-rgb),.40)}
[data-theme="light"] .fil{background:linear-gradient(90deg,rgba(var(--teal-rgb),.55),var(--teal))}
[data-theme="light"] .brow.tgt .fil{background:linear-gradient(90deg,var(--gold3),var(--gold),var(--gold2));
  box-shadow:0 0 20px rgba(var(--gold-rgb),.34)}
[data-theme="light"] .trk{background:rgba(var(--ov-rgb),.075);border-color:rgba(var(--ov-rgb),.05)}
[data-theme="light"] .brow.tgt .trk{background:rgba(var(--tgtbg-rgb),.55)}
[data-theme="light"] .prog{box-shadow:0 0 12px rgba(var(--gold-rgb),.35)}
[data-theme="light"] .brand .bd{box-shadow:0 0 0 4px rgba(var(--gold-rgb),.16)}
[data-theme="light"] .eyebrow .lv{background:var(--ok);box-shadow:0 0 0 3px rgba(var(--ok-rgb),.18)}
[data-theme="light"] .next{background:linear-gradient(158deg,rgba(var(--gold-rgb),.085),rgba(var(--w-rgb),.55) 58%);
  border-color:rgba(var(--gold-rgb),.26)}
[data-theme="light"] .ag{background:rgba(var(--w-rgb),.66)}
[data-theme="light"] .ag:hover{background:#fff}
[data-theme="light"] .hbox{background:rgba(var(--gold-rgb),.065);border-color:rgba(var(--gold-rgb),.24)}
[data-theme="light"] .ph::before{box-shadow:0 0 0 5px var(--ink),0 0 20px rgba(var(--gold-rgb),.45)}
[data-theme="light"] .ph:nth-child(2)::before{box-shadow:0 0 0 5px var(--ink),0 0 20px rgba(var(--teal-rgb),.42)}
[data-theme="light"] .ph:nth-child(3)::before{box-shadow:0 0 0 5px var(--ink)}
[data-theme="light"] .hi.no .mk{background:rgba(var(--crit-rgb),.09)}
[data-theme="light"] .hi.yes .mk{background:rgba(var(--ok-rgb),.10)}
[data-theme="light"] .str .ic{background:rgba(var(--ok-rgb),.09);border-color:rgba(var(--ok-rgb),.28)}
[data-theme="light"] .find .ev{background:rgba(var(--teal-rgb),.075);border-color:rgba(var(--teal-rgb),.24)}
[data-theme="light"] .find .ev:hover{background:rgba(var(--teal-rgb),.15)}
[data-theme="light"] .axis .num{background:rgba(var(--gold-rgb),.09);border-color:rgba(var(--gold-rgb),.30)}
[data-theme="light"] .chip.on{background:rgba(var(--gold-rgb),.13);border-color:rgba(var(--gold-rgb),.50);
  box-shadow:0 0 18px rgba(var(--gold-rgb),.12) inset}
[data-theme="light"] nav.stuck{background:rgba(var(--ink-rgb),.80)}
[data-theme="light"] footer{background:rgba(var(--ink-rgb),.70)}
[data-theme="light"] .st{background:var(--ink2)}
[data-theme="light"] .st:hover{background:var(--ink3)}
[data-theme="light"] .stats{background:var(--ln)}
[data-theme="light"] .cmp{background:var(--ink2)}
[data-theme="light"] .cmp-hd{background:rgba(var(--ov-rgb),.025)}
[data-theme="light"] .cmp-r{border-bottom-color:rgba(var(--ov-rgb),.055)}
[data-theme="light"] .cmp-hint{background:rgba(var(--ov-rgb),.022)}

/* ═══════════════ گذار میان مودها ═══════════════ */
body,nav,.card,.find,.axis,.ph,.hi,.ag,.st,.cmp,.chart,.hbox,.nbox,.chip,.btn,.cond,.str{
  transition-property:background-color,border-color,color,box-shadow,transform,opacity;
  transition-duration:.42s;transition-timing-function:var(--e2)}
.theme-sw body,.theme-sw body *{transition-duration:.42s!important}
@media (prefers-reduced-motion:reduce){
  .theme-sw body,.theme-sw body *{transition-duration:.001s!important}
}

/* ═══════════════ دکمه مود ═══════════════ */
.tgl{display:inline-flex;align-items:center;gap:7px;flex:0 0 auto;
  background:var(--sf);border:1px solid var(--ln);color:var(--t2);
  font-family:inherit;font-size:12.2px;font-weight:700;padding:8px 14px;border-radius:11px;
  transition:background .26s,border-color .26s,color .26s,transform .22s var(--e)}
.tgl:hover{background:var(--sf2);border-color:var(--ln2);color:var(--t1);transform:translateY(-1px)}
.tgl .ic{position:relative;width:15px;height:15px;flex:0 0 auto;display:block}
.tgl .ic::before,.tgl .ic::after{content:"";position:absolute;inset:0;
  transition:opacity .34s var(--e),transform .44s var(--e)}
/* ماه (مود تیره فعال) */
.tgl .ic::before{border-radius:50%;background:currentColor;
  box-shadow:5px -3px 0 0 var(--ink) inset;transform:rotate(-24deg)}
/* خورشید (مود روشن فعال) */
.tgl .ic::after{border-radius:50%;background:currentColor;opacity:0;transform:scale(.4) rotate(90deg)}
[data-theme="light"] .tgl .ic::before{opacity:0;transform:scale(.4) rotate(-90deg)}
[data-theme="light"] .tgl .ic::after{opacity:1;transform:none;
  box-shadow:0 -7px 0 -5px currentColor,0 7px 0 -5px currentColor,
             -7px 0 0 -5px currentColor,7px 0 0 -5px currentColor}
.tgl .lb{white-space:nowrap}
@media (max-width:760px){ .tgl .lb{display:none} .tgl{padding:8px 11px} }

/* ═══════════════ نشانگر سفارشی ═══════════════ */
.cur,.curd{position:fixed;top:0;left:0;pointer-events:none;z-index:9999;border-radius:50%;
  will-change:transform;mix-blend-mode:difference;display:none}
.cur{width:34px;height:34px;margin:-17px 0 0 -17px;border:1.4px solid rgba(var(--w-rgb),.72);
  transition:width .28s var(--e),height .28s var(--e),margin .28s var(--e),border-color .28s}
.curd{width:5px;height:5px;margin:-2.5px 0 0 -2.5px;background:#fff}
body.point .cur{width:62px;height:62px;margin:-31px 0 0 -31px;border-color:var(--gold)}
@media (hover:hover) and (pointer:fine){ .cur,.curd{display:block} }
@media (hover:hover) and (pointer:fine){
  a,button,.chip,.find,.card{cursor:none}
  body{cursor:none}
}

/* ═══════════════ نوار پیشرفت ═══════════════ */
.prog{position:fixed;top:0;right:0;left:0;height:2px;z-index:120;transform:scaleX(0);transform-origin:right;
  background:linear-gradient(90deg,var(--gold3),var(--gold),var(--gold2),var(--teal));
  box-shadow:0 0 14px rgba(var(--gold-rgb),.45)}
@supports (animation-timeline:scroll()){
  .prog{animation:grow linear both;animation-timeline:scroll(root block);transform:none}
  @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
}

/* ═══════════════ ناوبری ═══════════════ */
nav{position:sticky;top:0;z-index:110;transition:background .4s,border-color .4s,backdrop-filter .4s;
  border-bottom:1px solid transparent}
nav.stuck{background:rgba(var(--ink-rgb),.70);backdrop-filter:blur(20px) saturate(1.7);
  -webkit-backdrop-filter:blur(20px) saturate(1.7);border-bottom-color:var(--ln)}
.nin{max-width:var(--mx);margin:0 auto;padding:0 var(--pad);height:64px;
  display:flex;align-items:center;gap:20px}
.brand{display:flex;align-items:center;gap:10px;font-weight:900;font-size:13.6px;
  letter-spacing:-.01em;white-space:nowrap;color:var(--t1)}
.brand .bd{width:8px;height:8px;border-radius:50%;background:var(--gold);flex:0 0 auto;
  box-shadow:0 0 0 4px rgba(var(--gold-rgb),.15);animation:bp 2.8s ease-in-out infinite}
@keyframes bp{0%,100%{box-shadow:0 0 0 4px rgba(var(--gold-rgb),.15)}50%{box-shadow:0 0 0 9px rgba(var(--gold-rgb),.04)}}
.brand em{font-style:normal;color:var(--t3);font-weight:600;font-size:11.6px;
  border-right:1px solid var(--ln2);padding-right:10px;margin-right:2px}
.nlinks{display:flex;gap:1px;margin-right:auto;overflow-x:auto;scrollbar-width:none}
.nlinks::-webkit-scrollbar{display:none}
.nlinks a{color:var(--t3);text-decoration:none;font-size:12.6px;font-weight:600;
  padding:7px 11px;border-radius:9px;white-space:nowrap;position:relative;
  transition:color .25s,background .25s}
.nlinks a:hover{color:var(--t1);background:var(--sf2)}
.nlinks a.on{color:var(--gold)}
.nlinks a.on::after{content:"";position:absolute;bottom:2px;right:11px;left:11px;height:1.5px;
  background:var(--gold);border-radius:2px;box-shadow:0 0 8px rgba(var(--gold-rgb),.6)}
.ncta{flex:0 0 auto;background:linear-gradient(135deg,var(--gold2),var(--gold));color:var(--on-gold);
  font-weight:800;font-size:12.8px;padding:9px 18px;border-radius:11px;text-decoration:none;
  white-space:nowrap;box-shadow:0 2px 16px rgba(var(--gold-rgb),.24);
  transition:transform .22s var(--e),box-shadow .3s}
.ncta:hover{transform:translateY(-2px);box-shadow:0 7px 26px rgba(var(--gold-rgb),.40)}

/* ═══════════════ چیدمان ═══════════════ */
main{position:relative;z-index:1}
section{padding:clamp(66px,9vw,112px) var(--pad);scroll-margin-top:66px}
.wrap{max-width:var(--mx);margin:0 auto}
.wrapn{max-width:var(--mn);margin:0 auto}

.kick{display:flex;align-items:center;gap:12px;margin:0 0 18px;flex-wrap:wrap}
.kick .n{font-size:11.6px;font-weight:900;letter-spacing:.14em;color:var(--gold);
  font-variant-numeric:tabular-nums}
.kick .bar{width:26px;height:1.5px;background:linear-gradient(90deg,var(--gold),transparent);border-radius:2px}
.kick .tx{font-size:11.4px;font-weight:700;letter-spacing:.09em;color:var(--t4)}
h2{font-size:clamp(25px,3.9vw,41px);font-weight:900;line-height:1.38;margin:0 0 18px;
  letter-spacing:-.022em;max-width:22ch}
h2 .hl{background:linear-gradient(115deg,var(--gold2),var(--gold) 46%,var(--gold3));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.lead{font-size:15.6px;font-weight:300;color:var(--t2);max-width:64ch;margin:0 0 44px;line-height:2.12}
.lead b{font-weight:700;color:var(--t1)}

/* ═══════════════ قهرمان ═══════════════ */
.hero{position:relative;padding:clamp(58px,8vw,96px) var(--pad) clamp(48px,6vw,72px);overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.5;
  background:radial-gradient(760px circle at var(--hx,50%) var(--hy,26%),rgba(var(--gold-rgb),.10),transparent 62%);
  transition:opacity .5s}
.hin{max-width:var(--mx);margin:0 auto;position:relative}
.eyebrow{display:inline-flex;align-items:center;gap:11px;flex-wrap:wrap;
  background:var(--sf);border:1px solid var(--ln);border-radius:999px;
  padding:8px 19px;font-size:12.6px;color:var(--t2);margin-bottom:clamp(28px,4vw,42px);
  backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
  opacity:0;transform:translateY(14px);animation:fu 1s var(--e) .1s forwards}
.eyebrow b{color:var(--gold);font-weight:800}
.eyebrow .sp{width:1px;height:13px;background:var(--ln2)}
.eyebrow .lv{width:6px;height:6px;border-radius:50%;background:var(--ok);
  box-shadow:0 0 0 3px rgba(var(--ok-rgb),.16);animation:bp2 2.4s ease-in-out infinite}
@keyframes bp2{0%,100%{box-shadow:0 0 0 3px rgba(var(--ok-rgb),.16)}50%{box-shadow:0 0 0 7px rgba(var(--ok-rgb),.04)}}

.h1{margin:0 0 clamp(24px,3.4vw,34px);font-weight:900;letter-spacing:-.038em;line-height:1.14}
.lm{display:block;overflow:hidden;padding-bottom:.055em}
.lm>span{display:block;font-size:clamp(35px,8.2vw,84px);transform:translateY(122%);opacity:0;
  animation:lu 1.15s var(--e) forwards}
.lm:nth-child(1)>span{animation-delay:.20s}
.lm:nth-child(2)>span{animation-delay:.31s}
.lm:nth-child(3)>span{animation-delay:.42s}
.lm:nth-child(4)>span{animation-delay:.53s;
  background:linear-gradient(102deg,var(--gold2) 4%,var(--gold) 42%,var(--gold3) 92%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
@keyframes lu{to{transform:translateY(0);opacity:1}}
@keyframes fu{to{transform:translateY(0);opacity:1}}

.hlead{font-size:clamp(15px,1.8vw,17px);font-weight:300;color:var(--t2);max-width:60ch;
  line-height:2.2;margin:0 0 clamp(28px,3.6vw,38px);
  opacity:0;transform:translateY(18px);animation:fu 1.05s var(--e) .80s forwards}
.hlead b{font-weight:700;color:var(--t1)}
.hcta{display:flex;gap:13px;flex-wrap:wrap;opacity:0;transform:translateY(18px);
  animation:fu 1.05s var(--e) .94s forwards}
.btn{position:relative;display:inline-flex;align-items:center;gap:10px;text-decoration:none;
  font-weight:800;font-size:14.4px;padding:15px 28px;border-radius:14px;border:1px solid transparent;
  font-family:inherit;transition:transform .26s var(--e),box-shadow .34s,background .28s,border-color .28s,color .28s;
  will-change:transform;overflow:hidden}
.btn-p{background:linear-gradient(135deg,var(--gold2),var(--gold) 55%,var(--gold3));color:var(--on-gold);
  box-shadow:0 4px 28px rgba(var(--gold-rgb),.26)}
.btn-p::after{content:"";position:absolute;inset:0;opacity:0;transition:opacity .35s;
  background:linear-gradient(105deg,transparent 34%,rgba(var(--w-rgb),.42) 50%,transparent 66%)}
.btn-p:hover::after{opacity:1;animation:sheen 1.05s var(--e)}
@keyframes sheen{from{transform:translateX(-120%)}to{transform:translateX(120%)}}
.btn-p:hover{box-shadow:0 12px 44px rgba(var(--gold-rgb),.44)}
.btn-g{background:var(--sf);border-color:var(--ln2);color:var(--t1);backdrop-filter:blur(10px)}
.btn-g:hover{background:var(--sf2);border-color:var(--gold);color:var(--gold)}
.btn .ar{transition:transform .3s var(--e);display:inline-block}
.btn:hover .ar{transform:translateX(-5px)}

.hmeta{display:flex;gap:11px 32px;flex-wrap:wrap;margin-top:clamp(34px,4.6vw,48px);
  padding-top:26px;border-top:1px solid var(--ln);font-size:12.4px;color:var(--t4);
  opacity:0;animation:fu 1s var(--e) 1.08s forwards}
.hmeta span{display:inline-flex;align-items:center;gap:8px}
.hmeta b{color:var(--t2);font-weight:700}
.hmeta i{font-style:normal;color:var(--ln3)}

/* ═══════════════ آمار ═══════════════ */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(162px,1fr));gap:1px;
  background:var(--ln);border:1px solid var(--ln);border-radius:24px;overflow:hidden;
  margin-top:clamp(38px,5vw,56px);
  opacity:0;transform:translateY(20px);animation:fu 1.05s var(--e) 1.20s forwards}
.st{position:relative;background:var(--ink2);padding:clamp(22px,2.6vw,30px) clamp(16px,2vw,22px);
  transition:background .35s;overflow:hidden}
.st::after{content:"";position:absolute;top:0;right:0;left:0;height:1.5px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent);
  opacity:0;transition:opacity .4s}
.st:hover{background:var(--ink3)}
.st:hover::after{opacity:.85}
.st .n{font-size:clamp(27px,3.6vw,42px);font-weight:900;line-height:1.06;letter-spacing:-.042em;
  font-variant-numeric:tabular-nums;color:var(--t1)}
.st .n .sf{color:var(--gold);font-size:.58em;margin-right:2px}
.st.zero .n{color:var(--ok);text-shadow:0 0 26px rgba(var(--ok-rgb),.34)}
.st .lb{font-size:13.2px;font-weight:700;color:var(--t2);margin-top:10px;letter-spacing:-.005em}
.st .sb{font-size:11.4px;font-weight:300;color:var(--t4);margin-top:4px;line-height:1.72}

/* ═══════════════ نوار متحرک ═══════════════ */
.mq{position:relative;overflow:hidden;padding:20px 0;margin-top:clamp(34px,4.4vw,50px);
  border-top:1px solid var(--ln);border-bottom:1px solid var(--ln);
  mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent)}
.mqt{display:flex;gap:0;width:max-content;animation:mq 44s linear infinite}
.mq:hover .mqt{animation-play-state:paused}
@keyframes mq{from{transform:translateX(0)}to{transform:translateX(50%)}}
.mqt span{display:inline-flex;align-items:center;gap:26px;padding:0 26px;
  font-size:12.8px;font-weight:600;color:var(--t4);white-space:nowrap;letter-spacing:.01em}
.mqt span::after{content:"◆";font-size:7px;color:var(--gold3);opacity:.7}

/* ═══════════════ ستون چسبان (یافته‌ها) ═══════════════ */
.stick{display:grid;grid-template-columns:minmax(268px,.82fr) minmax(0,1.6fr);gap:clamp(26px,4.4vw,62px);
  align-items:start}
.stick-l{position:sticky;top:96px}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:26px 0 18px}
.chip{font-family:inherit;font-size:12.4px;font-weight:700;padding:8px 16px;border-radius:999px;
  background:var(--sf);border:1px solid var(--ln);color:var(--t2);
  transition:all .28s var(--e);position:relative;overflow:hidden}
.chip:hover{border-color:var(--ln2);color:var(--t1);background:var(--sf2)}
.chip.on{background:rgba(var(--gold-rgb),.13);border-color:rgba(var(--gold-rgb),.48);color:var(--gold2);
  box-shadow:0 0 20px rgba(var(--gold-rgb),.13) inset}
.chip .c{font-size:10.6px;opacity:.62;margin-right:5px;font-variant-numeric:tabular-nums}
.fcount{font-size:12.4px;color:var(--t4);font-weight:300;margin:0 0 6px;
  font-variant-numeric:tabular-nums;transition:opacity .3s}
.fcount b{color:var(--gold);font-weight:800}

.grp{margin-bottom:clamp(30px,3.8vw,44px)}
.grp-h{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:7px}
.sev{flex:0 0 auto;font-size:10.9px;font-weight:900;letter-spacing:.06em;padding:5px 12px;
  border-radius:8px;border:1px solid}
.sev.crit{color:var(--crit);border-color:rgba(var(--crit-rgb),.36);background:rgba(var(--crit-rgb),.10)}
.sev.high{color:var(--high);border-color:rgba(var(--high-rgb),.32);background:rgba(var(--high-rgb),.085)}
.sev.mid{color:var(--mid);border-color:rgba(var(--mid-rgb),.28);background:rgba(var(--mid-rgb),.065)}
.grp-h h3{margin:0;font-size:clamp(16px,2vw,19.5px);font-weight:800;letter-spacing:-.015em;line-height:1.55}
.gnote{color:var(--t3);font-size:13.2px;font-weight:300;margin:0 0 18px;max-width:64ch;line-height:1.95}

.find{position:relative;display:grid;grid-template-columns:auto 1fr;gap:0 17px;
  padding:20px 22px;border:1px solid var(--ln);border-radius:16px;background:var(--sf);
  margin-bottom:10px;overflow:hidden;
  transition:border-color .32s,background .32s,transform .34s var(--e),opacity .34s,max-height .42s var(--e),
             margin .34s var(--e),padding .34s var(--e)}
.find::before{content:"";position:absolute;inset:0;opacity:0;transition:opacity .4s;pointer-events:none;
  background:radial-gradient(460px circle at var(--mx,50%) var(--my,50%),rgba(var(--gold-rgb),.075),transparent 60%)}
.find:hover{border-color:var(--ln2);background:var(--sf2);transform:translateX(-5px)}
.find:hover::before{opacity:1}
.find.hide{opacity:0;transform:scale(.97);max-height:0!important;margin-bottom:0;
  padding-top:0;padding-bottom:0;border-width:0;pointer-events:none}
.find .bar{grid-row:1/3;width:3px;border-radius:3px;background:var(--ln2);align-self:stretch;min-height:40px}
.find.crit .bar{background:linear-gradient(180deg,var(--crit),rgba(var(--crit-rgb),.28));
  box-shadow:0 0 16px rgba(var(--crit-rgb),.40)}
.find.high .bar{background:linear-gradient(180deg,var(--high),rgba(var(--high-rgb),.26))}
.find.mid .bar{background:linear-gradient(180deg,var(--mid),rgba(var(--mid-rgb),.24))}
.find h4{margin:0;font-size:14.9px;font-weight:800;line-height:1.78;color:var(--t1);letter-spacing:-.008em}
.find p{margin:7px 0 0;font-size:13.5px;font-weight:300;color:var(--t2);line-height:2.02}
.find .ev{grid-column:2;margin-top:12px;display:inline-flex;align-items:center;gap:7px;
  font-family:Consolas,'Courier New',monospace;direction:ltr;unicode-bidi:embed;
  font-size:11.2px;color:var(--teal);background:rgba(var(--teal-rgb),.075);
  border:1px solid rgba(var(--teal-rgb),.20);border-radius:8px;padding:4px 11px;text-decoration:none;
  max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
  transition:background .26s,border-color .26s,transform .26s var(--e)}
.find .ev:hover{background:rgba(var(--teal-rgb),.16);border-color:rgba(var(--teal-rgb),.44);transform:translateY(-1px)}

/* ═══════════════ کارت عمومی ═══════════════ */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(292px,1fr));gap:16px}
.card{position:relative;background:var(--sf);border:1px solid var(--ln);border-radius:18px;
  padding:28px 26px 26px;overflow:hidden;
  transition:border-color .34s,transform .38s var(--e),background .34s}
.card::before{content:"";position:absolute;inset:0;border-radius:inherit;opacity:0;
  transition:opacity .4s;pointer-events:none;
  background:radial-gradient(460px circle at var(--mx,50%) var(--my,50%),rgba(var(--gold-rgb),.085),transparent 60%)}
.card::after{content:"";position:absolute;top:0;right:22px;left:22px;height:1px;
  background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:0;transition:opacity .4s}
.card:hover{border-color:var(--ln2);transform:translateY(-4px);background:var(--sf2)}
.card:hover::before{opacity:1}
.card:hover::after{opacity:.7}

.str .ic{width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;
  background:rgba(var(--ok-rgb),.10);border:1px solid rgba(var(--ok-rgb),.26);color:var(--ok);
  font-size:15px;margin-bottom:18px;transition:transform .4s var(--e),box-shadow .4s}
.str:hover .ic{transform:scale(1.09) rotate(-5deg);box-shadow:0 0 26px rgba(var(--ok-rgb),.20)}
.str h4{margin:0 0 9px;font-size:15.8px;font-weight:800;letter-spacing:-.012em;line-height:1.6}
.str p{margin:0;font-size:13.7px;font-weight:300;color:var(--t2);line-height:2.02}

/* ═══════════════ مقایسه لغزان ═══════════════ */
.cmp{position:relative;border:1px solid var(--ln);border-radius:22px;overflow:hidden;
  background:var(--ink2);user-select:none;touch-action:pan-y}
.cmp-side{position:absolute;inset:0;display:flex;flex-direction:column}
.cmp-a{clip-path:inset(0 0 0 var(--pos,50%))}
.cmp-b{clip-path:inset(0 calc(100% - var(--pos,50%)) 0 0)}
.cmp-hd{display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:15px 22px;border-bottom:1px solid var(--ln);background:rgba(var(--w-rgb),.022)}
.cmp-hd .lb{font-size:13.4px;font-weight:800;letter-spacing:-.01em}
.cmp-a .cmp-hd .lb{color:var(--crit)}
.cmp-b .cmp-hd .lb{color:var(--teal)}
.cmp-hd .tg{font-size:10.8px;font-weight:700;color:var(--t4);border:1px solid var(--ln);
  border-radius:999px;padding:3px 11px;font-family:Consolas,monospace;direction:ltr}
.cmp-rows{padding:6px 0}
.cmp-r{display:grid;grid-template-columns:minmax(120px,.9fr) minmax(0,1.5fr);gap:4px 16px;
  padding:14px 22px;border-bottom:1px solid rgba(var(--w-rgb),.045)}
.cmp-r:last-child{border-bottom:0}
.cmp-r .m{font-size:12.6px;font-weight:600;color:var(--t3);padding-top:2px}
.cmp-r .v{font-size:15.4px;font-weight:900;letter-spacing:-.02em;line-height:1.5}
.cmp-a .cmp-r .v{color:var(--crit)}
.cmp-b .cmp-r .v{color:var(--teal)}
.cmp-r small{grid-column:2;display:block;font-size:11.3px;font-weight:300;color:var(--t4);
  margin-top:4px;line-height:1.7}
.cmp-hnd{position:absolute;top:0;bottom:0;right:var(--pos,50%);width:2px;
  background:linear-gradient(180deg,transparent,var(--gold),var(--gold),transparent);
  transform:translateX(1px);pointer-events:none;box-shadow:0 0 20px rgba(var(--gold-rgb),.55)}
.cmp-knob{position:absolute;top:50%;right:var(--pos,50%);transform:translate(50%,-50%);
  width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,var(--gold2),var(--gold));
  display:flex;align-items:center;justify-content:center;gap:2px;color:var(--on-gold);font-size:12px;font-weight:900;
  box-shadow:0 4px 26px rgba(var(--gold-rgb),.46);pointer-events:none;z-index:3}
.cmp-in{position:absolute;inset:0;z-index:4;cursor:ew-resize;background:transparent}
.cmp-hint{display:flex;align-items:center;justify-content:center;gap:9px;padding:12px;
  font-size:12px;color:var(--t4);font-weight:300;border-top:1px solid var(--ln);
  background:rgba(var(--w-rgb),.018)}
.hbox{margin-top:24px;padding:22px 26px;border-radius:18px;font-size:14.6px;font-weight:300;
  background:rgba(var(--gold-rgb),.055);border:1px solid rgba(var(--gold-rgb),.20);
  border-right:4px solid var(--gold);color:var(--t2);line-height:2.1}
.hbox b{color:var(--gold2);font-weight:800}

/* ═══════════════ دژها ═══════════════ */
.fort{padding:32px 28px}
.fort .n{font-size:clamp(40px,5.4vw,54px);font-weight:900;line-height:1;letter-spacing:-.06em;
  background:linear-gradient(148deg,var(--gold2),rgba(var(--gold-rgb),var(--fort-end)));
  -webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:18px}
.fort h4{margin:0 0 11px;font-size:17px;font-weight:800;line-height:1.62;letter-spacing:-.014em}
.fort p{margin:0;font-size:13.9px;font-weight:300;color:var(--t2);line-height:2.08}
.fort .tag{display:inline-block;margin-top:18px;font-size:11.5px;font-weight:700;color:var(--teal);
  background:rgba(var(--teal-rgb),.075);border:1px solid rgba(var(--teal-rgb),.20);border-radius:999px;padding:5px 14px}

/* ═══════════════ نقش: چیدمان متناوب ═══════════════ */
.axes{display:grid;gap:12px}
.axis{position:relative;display:grid;grid-template-columns:auto 1fr;gap:0 20px;align-items:start;
  padding:24px 26px;border:1px solid var(--ln);border-radius:18px;background:var(--sf);
  overflow:hidden;transition:border-color .32s,background .32s,transform .36s var(--e)}
.axis:nth-child(even){margin-right:clamp(0px,3.4vw,46px)}
.axis:nth-child(odd){margin-left:clamp(0px,3.4vw,46px)}
.axis::before{content:"";position:absolute;inset:0;opacity:0;transition:opacity .4s;pointer-events:none;
  background:radial-gradient(520px circle at var(--mx,50%) var(--my,50%),rgba(var(--teal-rgb),.075),transparent 60%)}
.axis:hover{border-color:rgba(var(--gold-rgb),.34);background:var(--sf2);transform:translateX(-5px)}
.axis:hover::before{opacity:1}
.axis .num{grid-row:1/3;width:40px;height:40px;border-radius:12px;display:flex;align-items:center;
  justify-content:center;background:rgba(var(--gold-rgb),.10);border:1px solid rgba(var(--gold-rgb),.26);
  color:var(--gold);font-weight:900;font-size:15.5px;flex:0 0 auto;align-self:start;
  transition:transform .4s var(--e),box-shadow .4s}
.axis:hover .num{transform:scale(1.1) rotate(-6deg);box-shadow:0 0 26px rgba(var(--gold-rgb),.22)}
.axis h4{margin:0;font-size:16px;font-weight:800;letter-spacing:-.014em;padding-top:7px;line-height:1.6}
.axis p{margin:6px 0 0;font-size:13.7px;font-weight:300;color:var(--t2);line-height:2.02;grid-column:2}
.nbox{margin-top:22px;padding:20px 24px;border-radius:16px;font-size:14.2px;font-weight:300;
  background:var(--sf);border:1px solid var(--ln);border-right:4px solid var(--teal);
  color:var(--t2);line-height:2.05}

/* ═══════════════ حقوق ═══════════════ */
.pay{display:grid;grid-template-columns:minmax(0,1.32fr) minmax(0,1fr);gap:clamp(20px,3vw,34px);align-items:start}
.chart{border:1px solid var(--ln);border-radius:22px;padding:clamp(22px,2.8vw,30px);background:var(--sf);
  position:relative;overflow:hidden}
.chart::before{content:"";position:absolute;top:0;right:0;left:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(var(--gold-rgb),.55),transparent)}
.brow{margin-bottom:24px}
.brow:last-child{margin-bottom:0}
.btop{display:flex;justify-content:space-between;align-items:baseline;gap:14px;margin-bottom:9px;flex-wrap:wrap}
.blb{font-size:13.1px;font-weight:600;color:var(--t2);flex:1 1 190px;line-height:1.65}
.bv{font-size:16px;font-weight:900;color:var(--t1);font-variant-numeric:tabular-nums;
  white-space:nowrap;letter-spacing:-.024em}
.bv small{font-size:10.6px;font-weight:500;color:var(--t4);margin-right:4px;letter-spacing:0}
.trk{height:12px;border-radius:7px;background:rgba(var(--w-rgb),.055);overflow:hidden;position:relative;
  border:1px solid rgba(var(--w-rgb),.045)}
.fil{height:100%;border-radius:7px;width:0;
  background:linear-gradient(90deg,rgba(var(--teal-rgb),.45),var(--teal));
  transition:width 1.7s var(--e)}
.bsrc{font-size:11.1px;font-weight:300;color:var(--t4);margin-top:7px;line-height:1.6}
.brow.tgt .fil{background:linear-gradient(90deg,var(--gold3),var(--gold),var(--gold2));
  box-shadow:0 0 24px rgba(var(--gold-rgb),.45)}
.brow.tgt .bv{color:var(--gold);font-size:22px}
.brow.tgt .blb{color:var(--gold2);font-weight:800}
.brow.tgt{padding:18px 20px;margin:0 -8px 26px;border-radius:16px;
  background:linear-gradient(135deg,rgba(var(--gold-rgb),.085),rgba(var(--gold-rgb),.018));
  border:1px solid rgba(var(--gold-rgb),.24)}
.brow.tgt .trk{background:rgba(var(--tgtbg-rgb),.42)}
.ppts{list-style:none;padding:0;margin:0}
.ppts li{position:relative;padding:13px 28px 13px 0;font-size:13.9px;font-weight:300;
  color:var(--t2);line-height:1.98;border-bottom:1px dashed var(--ln)}
.ppts li:last-child{border-bottom:0}
.ppts li::before{content:"";position:absolute;right:5px;top:22px;width:7px;height:7px;
  border-radius:50%;background:var(--gold);opacity:.75;box-shadow:0 0 10px rgba(var(--gold-rgb),.5)}
.ppts li:nth-child(4)::before{background:var(--crit);box-shadow:0 0 10px rgba(var(--crit-rgb),.5)}

/* ═══════════════ نقشه راه ═══════════════ */
.tl{position:relative;padding-right:clamp(26px,4vw,46px)}
.tl::before{content:"";position:absolute;right:8px;top:12px;bottom:12px;width:2px;border-radius:2px;
  background:linear-gradient(180deg,var(--gold),var(--teal) 52%,rgba(var(--teal-rgb),.14))}
.ph{position:relative;padding:26px 28px;background:var(--sf);border:1px solid var(--ln);
  border-radius:18px;margin-bottom:16px;overflow:hidden;
  transition:border-color .34s,transform .38s var(--e),background .34s}
.ph::before{content:"";position:absolute;top:34px;right:calc(-1 * clamp(26px,4vw,46px) - 1px);
  width:16px;height:16px;border-radius:50%;background:var(--ink);
  border:2.5px solid var(--gold);transform:translateX(50%);z-index:2;
  box-shadow:0 0 0 5px var(--ink),0 0 22px rgba(var(--gold-rgb),.55)}
.ph:nth-child(2)::before{border-color:var(--teal);box-shadow:0 0 0 5px var(--ink),0 0 22px rgba(var(--teal-rgb),.5)}
.ph:nth-child(3)::before{border-color:rgba(var(--teal-rgb),.5);box-shadow:0 0 0 5px var(--ink)}
.ph:hover{border-color:var(--ln2);transform:translateX(-6px);background:var(--sf2)}
.ph-h{display:flex;align-items:center;gap:13px;flex-wrap:wrap;margin-bottom:14px}
.ph .tag{font-size:11.2px;font-weight:900;letter-spacing:.06em;color:var(--gold);
  background:rgba(var(--gold-rgb),.10);border:1px solid rgba(var(--gold-rgb),.26);border-radius:8px;padding:4px 12px}
.ph:nth-child(2) .tag,.ph:nth-child(3) .tag{color:var(--teal);background:rgba(var(--teal-rgb),.085);
  border-color:rgba(var(--teal-rgb),.24)}
.ph .days{font-size:11.6px;font-weight:300;color:var(--t4);font-variant-numeric:tabular-nums}
.ph h4{margin:0 0 15px;font-size:17.4px;font-weight:800;line-height:1.6;letter-spacing:-.016em}
.ph ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:2px 22px}
.ph li{position:relative;padding:8px 20px 8px 0;font-size:13.4px;font-weight:300;color:var(--t2);line-height:1.85}
.ph li::before{content:"";position:absolute;right:3px;top:17px;width:5px;height:5px;border-radius:50%;
  background:var(--teal);opacity:.75}

/* ═══════════════ شروط ═══════════════ */
.conds{display:grid;grid-template-columns:repeat(auto-fit,minmax(272px,1fr));gap:16px}
.cond{border-right:4px solid var(--crit)}
.cond .n{font-size:clamp(32px,4vw,42px);font-weight:900;line-height:1;letter-spacing:-.055em;
  color:rgba(var(--crit-rgb),.34);margin-bottom:15px}
.cond h4{margin:0 0 10px;font-size:15.8px;font-weight:800;line-height:1.7;letter-spacing:-.012em}
.cond p{margin:0;font-size:13.6px;font-weight:300;color:var(--t2);line-height:2.02}

/* ═══════════════ صداقت ═══════════════ */
.hon{display:grid;grid-template-columns:repeat(auto-fit,minmax(296px,1fr));gap:12px}
.hi{display:grid;grid-template-columns:auto 1fr;gap:0 15px;padding:22px 23px;border:1px solid var(--ln);
  border-radius:16px;background:var(--sf);transition:border-color .3s,background .3s,transform .34s var(--e)}
.hi:hover{background:var(--sf2);border-color:var(--ln2);transform:translateY(-3px)}
.hi .mk{grid-row:1/3;width:30px;height:30px;border-radius:10px;display:flex;align-items:center;
  justify-content:center;font-weight:900;font-size:13.5px;align-self:start;margin-top:2px;flex:0 0 auto}
.hi.no .mk{background:rgba(var(--crit-rgb),.10);border:1px solid rgba(var(--crit-rgb),.28);color:var(--crit)}
.hi.yes .mk{background:rgba(var(--ok-rgb),.10);border:1px solid rgba(var(--ok-rgb),.28);color:var(--ok)}
.hi h4{margin:0;font-size:14.7px;font-weight:800;line-height:1.72;letter-spacing:-.01em}
.hi p{margin:6px 0 0;font-size:13.2px;font-weight:300;color:var(--t2);line-height:1.98}

/* ═══════════════ گام بعدی ═══════════════ */
.next{position:relative;overflow:hidden;border-radius:26px;border:1px solid rgba(var(--gold-rgb),.22);
  background:linear-gradient(158deg,rgba(var(--gold-rgb),.075),rgba(var(--w-rgb),.018) 58%);
  padding:clamp(32px,4.6vw,54px) clamp(24px,3.6vw,46px)}
.next::before{content:"";position:absolute;top:-46%;left:-16%;width:130%;height:110%;pointer-events:none;
  background:radial-gradient(ellipse at center,rgba(var(--gold-rgb),.10),transparent 62%)}
.next>*{position:relative;z-index:1}
.agenda{display:grid;grid-template-columns:repeat(auto-fit,minmax(252px,1fr));gap:14px;margin:30px 0 0}
.ag{padding:22px 22px;border-radius:16px;background:rgba(var(--ink-rgb),.42);border:1px solid var(--ln);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  transition:border-color .32s,transform .36s var(--e),background .32s}
.ag:hover{border-color:rgba(var(--gold-rgb),.40);transform:translateY(-4px);background:rgba(var(--ink-rgb),.62)}
.ag .n{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;
  border-radius:10px;background:rgba(var(--gold-rgb),.13);border:1px solid rgba(var(--gold-rgb),.30);
  color:var(--gold2);font-weight:900;font-size:14px;margin-bottom:14px}
.ag h4{margin:0 0 8px;font-size:15.2px;font-weight:800;line-height:1.68;letter-spacing:-.01em}
.ag p{margin:0;font-size:13.3px;font-weight:300;color:var(--t2);line-height:2}
.nnote{margin-top:26px;padding-top:22px;border-top:1px solid var(--ln);
  font-size:14px;font-weight:300;color:var(--t2);line-height:2.05;max-width:70ch}

/* ═══════════════ پاصفحه ═══════════════ */
footer{position:relative;z-index:1;padding:clamp(38px,5vw,54px) var(--pad) clamp(44px,5.6vw,60px);
  border-top:1px solid var(--ln);background:rgba(var(--ink-rgb),.62);text-align:center}
footer .fa{font-size:16px;font-weight:900;color:var(--t1);letter-spacing:-.02em}
footer .fb{font-size:13.2px;font-weight:300;color:var(--t2);margin-top:7px}
footer .fc{font-size:11.8px;font-weight:300;color:var(--t4);line-height:2.15;margin-top:18px}
footer .fd{display:inline-flex;gap:9px;align-items:center;margin-top:16px;font-size:11.4px;
  color:var(--t4);border:1px solid var(--ln);border-radius:999px;padding:5px 15px}

/* ═══════════════ ظهور با اسکرول ═══════════════ */
[data-rev]{opacity:0;transform:translateY(26px);
  transition:opacity .92s var(--e),transform .92s var(--e)}
[data-rev].in{opacity:1;transform:none}
[data-rev][data-d="1"]{transition-delay:.075s}
[data-rev][data-d="2"]{transition-delay:.15s}
[data-rev][data-d="3"]{transition-delay:.225s}
[data-rev][data-d="4"]{transition-delay:.30s}
[data-rev][data-d="5"]{transition-delay:.375s}

/* ═══════════════ واکنش‌گرا ═══════════════ */
@media (max-width:1000px){
  .pay{grid-template-columns:1fr}
  .stick{grid-template-columns:1fr;gap:26px}
  .stick-l{position:static}
  .axis:nth-child(even),.axis:nth-child(odd){margin:0}
}
@media (max-width:760px){
  body{font-size:15px}
  .nin{height:58px;gap:12px}
  .nlinks{display:none}
  .brand em{display:none}
  .cmp-r{grid-template-columns:1fr;gap:2px}
  .cmp-r small{grid-column:1}
  .cmp-hd .tg{display:none}
  .ph ul{grid-template-columns:1fr}
  .btn{width:100%;justify-content:center}
  .hcta{flex-direction:column}
  .stats{grid-template-columns:repeat(2,1fr)}
  .find,.axis,.hi{grid-template-columns:1fr}
  .find .bar{grid-row:auto;width:38px;height:3px;margin-bottom:12px}
  .axis .num,.hi .mk{grid-row:auto;margin-bottom:12px}
  .find .ev,.axis p{grid-column:1}
  .ph{padding:22px 20px}
  .tl{padding-right:22px}
  .ph::before{right:-23px;top:28px;width:13px;height:13px}
}
@media (max-width:400px){ .stats{grid-template-columns:1fr} }

/* ═══════════════ کاهش حرکت ═══════════════ */
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.001s!important;animation-delay:0s!important;
    animation-iteration-count:1!important;transition-duration:.001s!important}
  .lm>span{transform:none;opacity:1}
  [data-rev]{opacity:1;transform:none}
  .eyebrow,.hlead,.hcta,.hmeta,.stats{opacity:1;transform:none}
  .cur,.curd,.mqt{display:none!important}
}

/* ═══════════════ چاپ ═══════════════ */
@media print{
  body{background:#fff;color:#111}
  nav,.prog,.fx,.cur,.curd,.mq,.hcta,.cmp-in,.cmp-hint{display:none!important}
  section{padding:16px 0;break-inside:avoid}
  .card,.find,.ph,.cond,.hi,.ag,.chart,.cmp{background:#fff!important;border-color:#d8d8d8!important;
    transform:none!important;opacity:1!important}
  h2,.st .n,.fort h4,.axis h4,.cond h4,.hi h4,.ag h4,.bv,.fort .n{color:#111!important;
    -webkit-text-fill-color:#111!important;text-shadow:none!important}
  p,li,td,.lead,.gnote,.find p,.fort p,.axis p,.cond p,.hi p,.ag p,.ppts li,.blb,.bsrc{color:#333!important}
  .h1,.lm>span{color:#111!important;-webkit-text-fill-color:#111!important}
  .stick-l{position:static}
  .cmp-a,.cmp-b{clip-path:none!important;position:static}
}
"""


JS = r"""
(function(){
"use strict";

var D   = __DATA__;
var CFG = __CFG__;
var FA  = "fa-IR";
var q   = new URLSearchParams(location.search);
var $   = function(s,r){ return (r||document).querySelector(s); };
var $$  = function(s,r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };
var RM  = window.matchMedia && window.matchMedia("(prefers-reduced-motion:reduce)").matches;

function esc(s){
  return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function fa(n){ return Number(n).toLocaleString(FA); }

/* ─────────── شخصی‌سازی با ?to= ─────────── */
var to = (q.get("to") || "").trim().slice(0,70);
if (to){
  var gt = $("#greet-to");
  if (gt){ gt.textContent = to; gt.style.display = ""; }
  document.title = to + " — " + D.company;
} else {
  var gs = $("#greet-sep"); if (gs) gs.style.display = "none";
}

/* ─────────── مود روشن / تیره ─────────── */
var THEME_KEY = "et-theme";
function themeSet(mode, animate){
  var root = document.documentElement;
  if (animate && !RM) root.classList.add("theme-sw");
  if (mode === "light") root.dataset.theme = "light";
  else root.removeAttribute("data-theme");
  var t = $("#tgl");
  if (t){
    var light = mode === "light";
    t.setAttribute("aria-pressed", light ? "true" : "false");
    var lb = t.querySelector(".lb"); if (lb) lb.textContent = light ? "مود تیره" : "مود روشن";
  }
  /* رنگ نوار وضعیت مرورگر موبایل هم باید همراه مود عوض شود */
  var mc = document.querySelector('meta[name="theme-color"]');
  if (mc) mc.setAttribute("content", mode === "light" ? "#f6f4ef" : "#05070d");
  try{ localStorage.setItem(THEME_KEY, mode); }catch(e){}
  if (animate && !RM) setTimeout(function(){ root.classList.remove("theme-sw"); }, 520);
}
function themeInit(){
  var saved = null;
  try{ saved = localStorage.getItem(THEME_KEY); }catch(e){}
  var mode = (saved === "light" || saved === "dark") ? saved : "dark";
  /* همگام‌سازی با آنچه اسکریپت head از پیش اعمال کرده */
  var pre = document.documentElement.dataset.theme;
  if (pre === "light" && saved === null) mode = "light";
  themeSet(mode, false);
  var t = $("#tgl");
  if (t) t.addEventListener("click", function(){
    var cur = document.documentElement.dataset.theme === "light" ? "light" : "dark";
    themeSet(cur === "light" ? "dark" : "light", true);
  });
}

/* ─────────── ساخت محتوا ─────────── */
function build(){
  var h = D.hero;
  $("#h-kick").textContent = h.kicker;
  $("#h1").innerHTML = h.lines.map(function(l){
    return '<span class="lm"><span>' + esc(l) + '</span></span>';
  }).join("");
  $("#h-lead").innerHTML = esc(h.lead);
  $("#cta-p").innerHTML = esc(h.ctaPrimary) + ' <span class="ar">←</span>';
  $("#cta-s").textContent = h.ctaSecondary;

  /* آمار */
  $("#stats").innerHTML = D.stats.map(function(s){
    return '<div class="st' + (s.n===0?" zero":"") + '">'
      + '<div class="n"><span class="ct" data-to="' + s.n + '">۰</span>'
      + (s.suffix ? '<span class="sf">' + esc(s.suffix) + '</span>' : '') + '</div>'
      + '<div class="lb">' + esc(s.label) + '</div>'
      + '<div class="sb">' + esc(s.sub) + '</div></div>';
  }).join("");

  /* نوار متحرک */
  var mq = D.marquee.concat(D.marquee).map(function(t){
    return "<span>" + esc(t) + "</span>";
  }).join("");
  $("#mqt").innerHTML = mq;

  /* یافته‌ها */
  var F = D.findings;
  $("#f-n").textContent = F.num; $("#f-k").textContent = F.kicker;
  $("#f-t").innerHTML = F.title; $("#f-l").innerHTML = esc(F.lead);

  var counts = {all:0};
  F.groups.forEach(function(g){ counts[g.sev] = (counts[g.sev]||0) + g.items.length; counts.all += g.items.length; });
  $("#chips").innerHTML = F.filters.map(function(f,i){
    var c = f==="همه" ? counts.all : (counts[f]||0);
    return '<button type="button" class="chip' + (i===0?" on":"") + '" data-f="' + esc(f) + '">'
      + esc(f) + '<span class="c">' + fa(c) + '</span></button>';
  }).join("");

  $("#fgrid").innerHTML = F.groups.map(function(g){
    var items = g.items.map(function(it,k){
      var ev = it.url
        ? '<a class="ev" href="' + esc(it.url) + '" target="_blank" rel="noopener nofollow">↗ ' + esc(it.ev) + '</a>'
        : '<span class="ev">' + esc(it.ev) + '</span>';
      return '<div class="find ' + g.cls + '" data-sev="' + esc(g.sev) + '" data-rev data-d="'
        + Math.min(k,5) + '"><span class="bar"></span><h4>' + esc(it.t) + '</h4>'
        + '<p>' + esc(it.d) + '</p>' + ev + '</div>';
    }).join("");
    return '<div class="grp" data-sev="' + esc(g.sev) + '">'
      + '<div class="grp-h" data-rev><span class="sev ' + g.cls + '">' + esc(g.sev) + '</span>'
      + '<h3>' + esc(g.title) + '</h3></div>'
      + '<p class="gnote" data-rev>' + esc(g.note) + '</p>' + items + '</div>';
  }).join("");
  $("#fcount").innerHTML = "نمایش <b>" + fa(counts.all) + "</b> یافته از " + fa(counts.all);

  /* نقاط قوت */
  var S = D.strengths;
  $("#s-n").textContent=S.num; $("#s-k").textContent=S.kicker; $("#s-t").innerHTML=S.title;
  $("#s-l").innerHTML=esc(S.lead);
  $("#sgrid").innerHTML = S.items.map(function(s,k){
    return '<div class="card str" data-rev data-d="' + k + '"><div class="ic">' + esc(s.icon)
      + '</div><h4>' + esc(s.t) + '</h4><p>' + esc(s.d) + '</p></div>';
  }).join("");

  /* شکاف + مقایسه لغزان */
  var G = D.gap;
  $("#g-n").textContent=G.num; $("#g-k").textContent=G.kicker; $("#g-t").innerHTML=G.title;
  $("#g-l").innerHTML=esc(G.lead);
  var side = function(cfg, key, cls){
    var rows = G.rows.map(function(r){
      return '<div class="cmp-r"><div class="m">' + esc(r.metric) + '</div>'
        + '<div class="v">' + esc(r[key]) + '</div>'
        + (key==="them" && r.note ? '<small>' + esc(r.note) + '</small>' : '') + '</div>';
    }).join("");
    return '<div class="cmp-side ' + cls + '"><div class="cmp-hd"><span class="lb">'
      + esc(cfg.label) + '</span><span class="tg">' + esc(cfg.tag) + '</span></div>'
      + '<div class="cmp-rows">' + rows + '</div></div>';
  };
  $("#cmp").innerHTML = side(G.after,"them","cmp-b") + side(G.before,"us","cmp-a")
    + '<div class="cmp-hnd"></div><div class="cmp-knob"><span>›</span><span>‹</span></div>'
    + '<div class="cmp-in" id="cmpin"></div>';
  $("#cmphint").textContent = "برای مقایسه، دستگیره را بکشید یا روی نوار کلیک کنید";
  $("#g-honest").innerHTML = esc(G.honest);

  /* دژها */
  var FT = D.fortress;
  $("#ft-n").textContent=FT.num; $("#ft-k").textContent=FT.kicker; $("#ft-t").innerHTML=FT.title;
  $("#ft-l").innerHTML=esc(FT.lead);
  $("#ftgrid").innerHTML = FT.cards.map(function(c,k){
    return '<div class="card fort" data-rev data-d="' + k + '"><div class="n">' + esc(c.n)
      + '</div><h4>' + esc(c.t) + '</h4><p>' + esc(c.d) + '</p>'
      + '<span class="tag">' + esc(c.tag) + '</span></div>';
  }).join("");

  /* نقش */
  var R = D.roleSec;
  $("#r-n").textContent=R.num; $("#r-k").textContent=R.kicker; $("#r-t").innerHTML=R.title;
  $("#r-l").innerHTML=esc(R.lead);
  $("#axes").innerHTML = R.axes.map(function(a,k){
    return '<div class="axis" data-rev data-d="' + Math.min(k,5) + '"><span class="num">' + esc(a.n)
      + '</span><h4>' + esc(a.t) + '</h4><p>' + esc(a.d) + '</p></div>';
  }).join("");
  $("#r-note").textContent = R.note;

  /* حقوق */
  var P = D.salary, MX = 100;
  $("#p-n").textContent=P.num; $("#p-k").textContent=P.kicker; $("#p-t").innerHTML=P.title;
  $("#p-l").innerHTML=esc(P.lead);
  var bars = '<div class="brow tgt" data-rev><div class="btop"><span class="blb">مبلغ پیشنهادی این نقش</span>'
    + '<span class="bv">' + fa(P.target) + '<small>' + esc(P.unit) + '</small></span></div>'
    + '<div class="trk"><div class="fil" data-w="' + (P.target/MX*100) + '"></div></div>'
    + '<div class="bsrc">پنج محور یکپارچه · داده بازار کار ۱۴۰۵</div></div>';
  bars += P.bars.map(function(b,k){
    return '<div class="brow" data-rev data-d="' + Math.min(k+1,5) + '"><div class="btop">'
      + '<span class="blb">' + esc(b.label) + '</span>'
      + '<span class="bv">' + fa(b.v) + '<small>میلیون</small></span></div>'
      + '<div class="trk"><div class="fil" data-w="' + (b.v/MX*100) + '"></div></div>'
      + '<div class="bsrc">' + esc(b.src) + '</div></div>';
  }).join("");
  $("#chart").innerHTML = bars;
  $("#ppts").innerHTML = P.points.map(function(p){ return "<li>" + esc(p) + "</li>"; }).join("");

  /* نقشه راه */
  var RM2 = D.roadmap;
  $("#rm-n").textContent=RM2.num; $("#rm-k").textContent=RM2.kicker; $("#rm-t").innerHTML=RM2.title;
  $("#rm-l").innerHTML=esc(RM2.lead);
  $("#tl").innerHTML = RM2.phases.map(function(p,k){
    return '<div class="ph" data-rev data-d="' + k + '"><div class="ph-h"><span class="tag">'
      + esc(p.tag) + '</span><span class="days">' + esc(p.days) + '</span></div>'
      + '<h4>' + esc(p.t) + '</h4><ul>'
      + p.items.map(function(x){ return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>";
  }).join("");

  /* شروط */
  var C = D.conditions;
  $("#c-n").textContent=C.num; $("#c-k").textContent=C.kicker; $("#c-t").innerHTML=C.title;
  $("#c-l").innerHTML=esc(C.lead);
  $("#cgrid").innerHTML = C.items.map(function(c,k){
    return '<div class="card cond" data-rev data-d="' + k + '"><div class="n">' + esc(c.n)
      + '</div><h4>' + esc(c.t) + '</h4><p>' + esc(c.d) + '</p></div>';
  }).join("");

  /* صداقت */
  var H = D.honesty;
  $("#h-n").textContent=H.num; $("#h-k").textContent=H.kicker; $("#h-t").innerHTML=H.title;
  $("#h-l").innerHTML=esc(H.lead);
  $("#hgrid").innerHTML = H.items.map(function(x,k){
    return '<div class="hi ' + x.cls + '" data-rev data-d="' + Math.min(k,5) + '">'
      + '<span class="mk">' + esc(x.icon) + '</span><h4>' + esc(x.t) + '</h4>'
      + '<p>' + esc(x.d) + '</p></div>';
  }).join("");

  /* گام بعدی */
  var N = D.next;
  $("#n-n").textContent=N.num; $("#n-k").textContent=N.kicker; $("#n-t").innerHTML=N.title;
  $("#n-l").innerHTML=esc(N.lead);
  $("#agenda").innerHTML = N.agenda.map(function(a,k){
    return '<div class="ag" data-rev data-d="' + k + '"><span class="n">' + esc(a.n)
      + '</span><h4>' + esc(a.t) + '</h4><p>' + esc(a.d) + '</p></div>';
  }).join("");
  $("#n-note").textContent = N.note;

  /* پاصفحه */
  $("#f-comp").textContent = D.company + " · " + D.role;
  $("#f-auth").textContent = D.author + " · " + D.dateFa + " / " + D.dateEn + " · نسخه " + D.version;
  $("#f-line").textContent = D.footer.line;
  $("#f-font").textContent = D.footer.font;
}

/* ─────────── شمارنده ─────────── */
function countUp(el){
  if (el.dataset.done) return;
  el.dataset.done = "1";
  var target = parseInt(el.dataset.to,10) || 0;
  if (target === 0 || RM){ el.textContent = fa(target); return; }
  var dur = 1600, t0 = null;
  function step(ts){
    if (!t0) t0 = ts;
    var p = Math.min((ts-t0)/dur,1), e = 1-Math.pow(1-p,3);
    el.textContent = fa(Math.round(target*e));
    if (p<1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ─────────── رمزگشایی ظاهری عنوان‌ها ─────────── */
var POOL = "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی۰۱۲۳۴۵۶۷۸۹";
function scramble(el){
  if (RM || el.dataset.sc) return;
  el.dataset.sc = "1";
  var final = el.textContent;
  if (!final.trim()) return;
  var nodes = [];
  (function walk(n){
    for (var i=0;i<n.childNodes.length;i++){
      var c = n.childNodes[i];
      if (c.nodeType === 3 && c.nodeValue.trim()) nodes.push(c);
      else if (c.nodeType === 1) walk(c);
    }
  })(el);
  if (!nodes.length) return;
  var originals = nodes.map(function(n){ return n.nodeValue; });
  var frame = 0, total = 26;
  function tick(){
    frame++;
    var prog = frame/total;
    nodes.forEach(function(n,ni){
      var orig = originals[ni], out = "", i;
      for (i=0;i<orig.length;i++){
        var ch = orig[i];
        if (ch === " " || ch === "\u200c"){ out += ch; continue; }
        if (i/orig.length < prog) out += ch;
        else out += POOL[(Math.random()*POOL.length)|0];
      }
      n.nodeValue = out;
    });
    if (frame < total) requestAnimationFrame(tick);
    else nodes.forEach(function(n,ni){ n.nodeValue = originals[ni]; });
  }
  requestAnimationFrame(tick);
}

/* ─────────── تعامل‌ها ─────────── */
function wire(){
  /* ظهور + شمارنده + نوارها */
  var io = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      var t = e.target;
      t.classList.add("in");
      io.unobserve(t);
      var ct = t.querySelector(".ct"); if (ct) countUp(ct);
      $$(".fil", t).forEach(function(f){
        if (!f.dataset.done){ f.dataset.done="1"; f.style.width = f.dataset.w + "%"; }
      });
      if (t.matches("h2")) scramble(t);
    });
  }, {rootMargin:"0px 0px -8% 0px", threshold:.1});
  $$("[data-rev]").forEach(function(el){ io.observe(el); });
  $$("h2").forEach(function(el){ io.observe(el); });

  /* شمارنده‌های آمار — ناظر جداگانه، چون کارت‌های .st خودشان
     data-rev ندارند (ظرفشان انیمان ورود مستقل دارد) */
  var stats = $("#stats");
  if (stats){
    var io0 = new IntersectionObserver(function(en){
      en.forEach(function(e){
        if (!e.isIntersecting) return;
        $$(".ct", e.target).forEach(countUp);
        io0.unobserve(e.target);
      });
    }, {threshold:.25});
    io0.observe(stats);
  }

  /* نوارهای نمودار */
  var io2 = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      $$(".fil", e.target).forEach(function(f){
        if (!f.dataset.done){ f.dataset.done="1"; f.style.width = f.dataset.w + "%"; }
      });
      io2.unobserve(e.target);
    });
  }, {threshold:.18});
  var ch = $("#chart"); if (ch) io2.observe(ch);

  /* فیلتر یافته‌ها */
  var chips = $$("#chips .chip"), finds = $$("#fgrid .find"), groups = $$("#fgrid .grp");
  var fc = $("#fcount");
  chips.forEach(function(c){
    c.addEventListener("click", function(){
      chips.forEach(function(x){ x.classList.toggle("on", x===c); });
      var f = c.dataset.f, n = 0;
      finds.forEach(function(el){
        var show = (f === "همه" || el.dataset.sev === f);
        el.classList.toggle("hide", !show);
        if (show) n++;
      });
      groups.forEach(function(g){
        var any = $$(".find:not(.hide)", g).length > 0;
        g.style.display = any ? "" : "none";
      });
      fc.innerHTML = "نمایش <b>" + fa(n) + "</b> یافته";
    });
  });

  /* مقایسه لغزان */
  var cmp = $("#cmp"), cin = $("#cmpin");
  if (cmp && cin){
    var setPos = function(cx){
      var r = cmp.getBoundingClientRect();
      /* اگر عرض صفر باشد (پنهان، یا پیش از چیدمان) هیچ نکن — در غیر این
         صورت --pos مقدار NaN می‌گیرد، clip-path باطل می‌شود و هر دو طرف
         روی هم می‌افتند. مقدار پیش‌فرض CSS همان ۵۰٪ است. */
      if (!r.width || !isFinite(cx)) return;
      /* RTL: سمت راست = ۰٪ */
      var p = (r.right - cx) / r.width * 100;
      if (!isFinite(p)) return;
      p = Math.max(4, Math.min(96, p));
      cmp.style.setProperty("--pos", p.toFixed(2) + "%");
    };
    var initPos = function(){
      var r = cmp.getBoundingClientRect();
      if (r.width) setPos(r.right - r.width/2);
    };
    initPos();
    /* اگر نخستین چیدمان عرض نداشت، پس از بارگذاری کامل دوباره تلاش کن */
    if (document.readyState !== "complete")
      addEventListener("load", initPos, {once:true});
    var drag = false;
    cin.addEventListener("pointerdown", function(e){ drag=true; cmp.setPointerCapture(e.pointerId); setPos(e.clientX); });
    cin.addEventListener("pointermove", function(e){ if (drag) setPos(e.clientX); });
    cin.addEventListener("pointerup",   function(){ drag=false; });
    cin.addEventListener("pointercancel",function(){ drag=false; });
    /* کیبورد */
    cin.setAttribute("tabindex","0");
    cin.setAttribute("role","slider");
    cin.setAttribute("aria-label","مقایسه انرژی تهویه با رقیب مرجع");
    cin.addEventListener("keydown", function(e){
      var cur = parseFloat(getComputedStyle(cmp).getPropertyValue("--pos"));
      if (!isFinite(cur)) cur = 50;
      var d = e.key==="ArrowLeft" ? 4 : e.key==="ArrowRight" ? -4 : 0;
      if (!d) return;
      e.preventDefault();
      cmp.style.setProperty("--pos", Math.max(4,Math.min(96,cur+d)) + "%");
    });
  }

  /* نور دنبال‌کننده نشانگر */
  $$(".card,.find,.axis,.ag,.st").forEach(function(c){
    c.addEventListener("pointermove", function(e){
      var r = c.getBoundingClientRect();
      c.style.setProperty("--mx", (e.clientX-r.left)+"px");
      c.style.setProperty("--my", (e.clientY-r.top)+"px");
    });
  });

  /* نشانگر سفارشی */
  if (!RM && window.matchMedia("(hover:hover) and (pointer:fine)").matches){
    var cur=$(".cur"), curd=$(".curd"), cx=innerWidth/2, cy=innerHeight/2, tx=cx, ty=cy;
    document.addEventListener("pointermove", function(e){
      tx=e.clientX; ty=e.clientY;
      curd.style.transform="translate3d("+tx+"px,"+ty+"px,0)";
    }, {passive:true});
    (function loop(){
      cx += (tx-cx)*.17; cy += (ty-cy)*.17;
      cur.style.transform="translate3d("+cx+"px,"+cy+"px,0)";
      requestAnimationFrame(loop);
    })();
    document.addEventListener("pointerover", function(e){
      document.body.classList.toggle("point", !!e.target.closest("a,button,.chip,.cmp-in"));
    });
  }

  /* دکمه‌های مغناطیسی */
  if (!RM && window.matchMedia("(hover:hover)").matches){
    $$(".btn,.ncta,.chip").forEach(function(b){
      b.addEventListener("pointermove", function(e){
        var r=b.getBoundingClientRect();
        b.style.transform="translate("+((e.clientX-r.left-r.width/2)*.20)+"px,"
          +((e.clientY-r.top-r.height/2)*.26)+"px)";
      });
      b.addEventListener("pointerleave", function(){ b.style.transform=""; });
    });
  }

  /* نورافکن قهرمان */
  var hero=$(".hero");
  if (hero && !RM){
    hero.addEventListener("pointermove", function(e){
      var r=hero.getBoundingClientRect();
      hero.style.setProperty("--hx", ((e.clientX-r.left)/r.width*100)+"%");
      hero.style.setProperty("--hy", ((e.clientY-r.top)/r.height*100)+"%");
    }, {passive:true});
  }

  /* ناوبری */
  var nav=$("#nav"), prog=$("#prog");
  var tl = CSS.supports && CSS.supports("animation-timeline","scroll()");
  function onScroll(){
    nav.classList.toggle("stuck", scrollY>14);
    if (!tl){
      var hh = document.documentElement.scrollHeight - innerHeight;
      prog.style.transform = "scaleX(" + (hh>0 ? scrollY/hh : 0) + ")";
    }
  }
  addEventListener("scroll", onScroll, {passive:true}); onScroll();

  /* جاسوس اسکرول */
  var links = $$(".nlinks a");
  var secs = links.map(function(a){ return $(a.getAttribute("href")); });
  var spy = new IntersectionObserver(function(en){
    en.forEach(function(e){
      if (!e.isIntersecting) return;
      var i = secs.indexOf(e.target);
      links.forEach(function(l,k){ l.classList.toggle("on", k===i); });
    });
  }, {rootMargin:"-44% 0px -44% 0px"});
  secs.forEach(function(s){ if (s) spy.observe(s); });
}

themeInit();
build();
wire();
})();
"""


HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet,noimageindex"/>
<meta name="googlebot" content="noindex,nofollow"/>
<meta name="referrer" content="no-referrer"/>
<meta name="theme-color" content="#05070d"/>
<meta name="author" content="__AUTHOR__"/>
<meta name="description" content="__DESC__"/>
<meta property="og:type" content="article"/>
<meta property="og:locale" content="fa_IR"/>
<meta property="og:title" content="__OGTITLE__"/>
<meta property="og:description" content="__DESC__"/>
<title>__TITLE__</title>
<script>
/* مود ذخیره‌شده را پیش از نخستین رنگ‌آمیزی اعمال می‌کند تا سوسوی
   جابه‌جایی مود (flash) دیده نشود. این تنها اسکریپت مسدودکننده است. */
(function(){
  try{
    var t = localStorage.getItem("et-theme");
    if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
  }catch(e){}
})();
</script>
<style>
__FONTS__
__CSS__
</style>
</head>
<body>

<div class="prog" id="prog"></div>
<div class="cur" id="cur"></div>
<div class="curd" id="curd"></div>

<div class="fx" aria-hidden="true">
  <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
  <div class="mesh"></div><div class="noise"></div><div class="vig"></div>
</div>

<nav id="nav">
  <div class="nin">
    <span class="brand"><span class="bd"></span><span>__AUTHOR__</span>
      <em>__ROLE_SHORT__</em></span>
    <div class="nlinks">
      <a href="#findings">یافته‌ها</a>
      <a href="#strengths">نقاط قوت</a>
      <a href="#gap">شکاف</a>
      <a href="#fortress">راهبرد</a>
      <a href="#role">نقش</a>
      <a href="#salary">مبلغ</a>
      <a href="#roadmap">مسیر</a>
      <a href="#honesty">صحت</a>
    </div>
    <button class="tgl" id="tgl" type="button" aria-pressed="false"
            aria-label="تغییر مود روشن و تیره" title="تغییر مود روشن و تیره">
      <span class="ic" aria-hidden="true"></span><span class="lb">مود روشن</span>
    </button>
    <a class="ncta" href="#next">گام بعدی</a>
  </div>
</nav>

<main>

  <!-- ═══ قهرمان ═══ -->
  <header class="hero" id="top">
    <div class="hin">
      <div class="eyebrow">
        <span class="lv"></span>
        <span id="greet-to" style="display:none"></span>
        <span class="sp" id="greet-sep"></span>
        <span>تهیه‌شده برای <b>__COMPANY__</b></span>
        <span class="sp"></span>
        <span>__CITY__ · از __SINCE__</span>
        <span class="sp"></span>
        <span>__DOMAIN__</span>
      </div>

      <p class="kick" id="h-kick-wrap" style="margin-bottom:20px">
        <span class="bar"></span><span class="tx" id="h-kick"></span>
      </p>

      <h1 class="h1" id="h1"></h1>

      <p class="hlead" id="h-lead"></p>

      <div class="hcta">
        <a class="btn btn-p" id="cta-p" href="#findings"></a>
        <a class="btn btn-g" id="cta-s" href="#next"></a>
      </div>

      <div class="hmeta">
        <span>تهیه‌کننده <b>__AUTHOR__</b></span><i></i>
        <span>نقش پیشنهادی <b>__ROLE__</b></span><i></i>
        <span>تاریخ <b>__DATEFA__</b></span><i></i>
        <span>نسخه <b>__VERSION__</b></span>
      </div>

      <div class="stats" id="stats"></div>

      <div class="mq" aria-hidden="true"><div class="mqt" id="mqt"></div></div>
    </div>
  </header>

  <!-- ═══ یافته‌ها ═══ -->
  <section id="findings">
    <div class="wrap stick">
      <div class="stick-l">
        <p class="kick"><span class="n" id="f-n"></span><span class="bar"></span>
          <span class="tx" id="f-k"></span></p>
        <h2 id="f-t" data-rev></h2>
        <p class="lead" id="f-l" data-rev style="margin-bottom:0"></p>
        <div class="chips" id="chips"></div>
        <p class="fcount" id="fcount"></p>
      </div>
      <div id="fgrid"></div>
    </div>
  </section>

  <!-- ═══ نقاط قوت ═══ -->
  <section id="strengths">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="s-n"></span><span class="bar"></span>
        <span class="tx" id="s-k"></span></p>
      <h2 id="s-t" data-rev></h2>
      <p class="lead" id="s-l" data-rev></p>
      <div class="cards" id="sgrid"></div>
    </div>
  </section>

  <!-- ═══ شکاف ═══ -->
  <section id="gap">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="g-n"></span><span class="bar"></span>
        <span class="tx" id="g-k"></span></p>
      <h2 id="g-t" data-rev></h2>
      <p class="lead" id="g-l" data-rev></p>
      <div class="cmp" id="cmp" data-rev></div>
      <p class="cmp-hint" id="cmphint"></p>
      <div class="hbox" id="g-honest" data-rev></div>
    </div>
  </section>

  <!-- ═══ دژها ═══ -->
  <section id="fortress">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="ft-n"></span><span class="bar"></span>
        <span class="tx" id="ft-k"></span></p>
      <h2 id="ft-t" data-rev></h2>
      <p class="lead" id="ft-l" data-rev></p>
      <div class="cards" id="ftgrid"></div>
    </div>
  </section>

  <!-- ═══ نقش ═══ -->
  <section id="role">
    <div class="wrapn">
      <p class="kick" data-rev><span class="n" id="r-n"></span><span class="bar"></span>
        <span class="tx" id="r-k"></span></p>
      <h2 id="r-t" data-rev></h2>
      <p class="lead" id="r-l" data-rev></p>
      <div class="axes" id="axes"></div>
      <div class="nbox" id="r-note" data-rev></div>
    </div>
  </section>

  <!-- ═══ مبلغ ═══ -->
  <section id="salary">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="p-n"></span><span class="bar"></span>
        <span class="tx" id="p-k"></span></p>
      <h2 id="p-t" data-rev></h2>
      <p class="lead" id="p-l" data-rev></p>
      <div class="pay">
        <div class="chart" id="chart"></div>
        <ul class="ppts" id="ppts" data-rev></ul>
      </div>
    </div>
  </section>

  <!-- ═══ نقشه راه ═══ -->
  <section id="roadmap">
    <div class="wrapn">
      <p class="kick" data-rev><span class="n" id="rm-n"></span><span class="bar"></span>
        <span class="tx" id="rm-k"></span></p>
      <h2 id="rm-t" data-rev></h2>
      <p class="lead" id="rm-l" data-rev></p>
      <div class="tl" id="tl"></div>
    </div>
  </section>

  <!-- ═══ شروط ═══ -->
  <section id="conditions">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="c-n"></span><span class="bar"></span>
        <span class="tx" id="c-k"></span></p>
      <h2 id="c-t" data-rev></h2>
      <p class="lead" id="c-l" data-rev></p>
      <div class="conds" id="cgrid"></div>
    </div>
  </section>

  <!-- ═══ صداقت ═══ -->
  <section id="honesty">
    <div class="wrap">
      <p class="kick" data-rev><span class="n" id="h-n"></span><span class="bar"></span>
        <span class="tx" id="h-k"></span></p>
      <h2 id="h-t" data-rev></h2>
      <p class="lead" id="h-l" data-rev></p>
      <div class="hon" id="hgrid"></div>
    </div>
  </section>

  <!-- ═══ گام بعدی ═══ -->
  <section id="next">
    <div class="wrap">
      <div class="next" data-rev>
        <p class="kick"><span class="n" id="n-n"></span><span class="bar"></span>
          <span class="tx" id="n-k"></span></p>
        <h2 id="n-t" style="max-width:26ch"></h2>
        <p class="lead" id="n-l" style="margin-bottom:0"></p>
        <div class="agenda" id="agenda"></div>
        <p class="nnote" id="n-note"></p>
      </div>
    </div>
  </section>

</main>

<footer>
  <div class="fa">__COMPANY__</div>
  <div class="fb" id="f-comp"></div>
  <div class="fc" id="f-auth"></div>
  <div class="fc" id="f-line"></div>
  <div class="fd" id="f-font"></div>
</footer>

<script>__JS__</script>
</body>
</html>
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    faces = "\n".join(
        "@font-face{font-family:'Vazirmatn';src:url('%s') format('woff2');"
        "font-weight:%d;font-style:normal;font-display:block}"
        % (font_uri(name), w) for w, name in sorted(WEIGHTS.items())
    )

    js = (JS.replace("__DATA__", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__CFG__", json.dumps({"slug": "energytahvieh"}, ensure_ascii=False)))
    js = js.replace("</script", "<\\/script")

    title = f"پروپوزال رشد دیجیتال — {DATA['company']}"
    desc = ("تحلیل مستند ۱۴ صفحه سایت، ۵۵ یافته تأییدشده با نشانی و نقل‌قول "
            "مستقیم، سه میدان راهبردی و برنامه سه‌فاز — بدون هیچ عدد ساختگی.")
    role_short = DATA["role"].split(" و ")[0]

    page = (HTML
            .replace("__FONTS__", faces)
            .replace("__CSS__", CSS)
            .replace("__JS__", js)
            .replace("__TITLE__", esc(title))
            .replace("__OGTITLE__", esc(title))
            .replace("__DESC__", esc(desc))
            .replace("__COMPANY__", esc(DATA["company"]))
            .replace("__DOMAIN__", esc(DATA["domain"]))
            .replace("__CITY__", esc(DATA["city"]))
            .replace("__SINCE__", esc(DATA["since"]))
            .replace("__AUTHOR__", esc(DATA["author"]))
            .replace("__ROLE__", esc(DATA["role"]))
            .replace("__ROLE_SHORT__", esc(role_short))
            .replace("__DATEFA__", esc(DATA["dateFa"]))
            .replace("__VERSION__", esc(DATA["version"])))

    idx = os.path.join(OUT, "index.html")
    with open(idx, "w", encoding="utf-8") as f:
        f.write(page)

    # فایل‌های کمکی هاست
    src = os.path.join(BUILD, "deploy", "subdomain-package")
    for n in (".htaccess", "htaccess-fallback.txt", "robots.txt", "log-visit.php"):
        s = os.path.join(src, n)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(OUT, n))

    sz = os.path.getsize(idx)
    print(f"OK  index.html   {sz:,} B  ({sz/1024:,.0f} KB)")
    for n in sorted(os.listdir(OUT)):
        if n != "index.html":
            print(f"OK  {n:<20} {os.path.getsize(os.path.join(OUT,n)):,} B")
    print(f"\nخروجی: {OUT}")
    print(f"لینک : https://proposal.sajadmasoumi.com/?to=مدیریت محترم {DATA['company']}")
    print(f"وزن‌های جاسازی‌شده: {', '.join(str(w) for w in sorted(WEIGHTS))}")


if __name__ == "__main__":
    main()
