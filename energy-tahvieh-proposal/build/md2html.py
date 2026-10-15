#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown -> print-ready RTL HTML.

Why this exists: the sandbox has no PDF toolchain (no libpango for WeasyPrint,
no font packages, no headless Chromium). These HTML files are styled for
@page A4 and load Vazirmatn from a CDN, so opening one in a browser and using
Print -> Save as PDF produces a correct Persian/RTL PDF on the user's machine.
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CSS_BODY = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm; }
@media print {
  .no-print { display: none !important; }
  h1, h2, h3 { break-after: avoid; }
  table, pre, blockquote { break-inside: avoid; }
  tr { break-inside: avoid; }
  a { color: inherit !important; text-decoration: none !important; }
}
:root{
  --accent:#0f5c8c; --h2:#143d59; --h3:#1f5c82; --muted:#5a5a5a;
  --alert:#a82222; --line:#dbe4ec; --soft:#f6f9fb; --code:#f5f5f5;
}
*{box-sizing:border-box}
html{ -webkit-text-size-adjust:100% }
body{
  font-family:'Vazirmatn','B Nazanin','IRANSans','Tahoma',sans-serif;
  direction:rtl; text-align:right; line-height:1.85;
  color:#1b1b1b; background:#eef1f4; margin:0; padding:0;
  font-size:14px; font-feature-settings:"ss01";
}
.sheet{
  background:#fff; max-width:210mm; margin:24px auto; padding:20mm 16mm;
  box-shadow:0 2px 18px rgba(0,0,0,.14);
}
@media print{ body{background:#fff} .sheet{box-shadow:none;margin:0;padding:0;max-width:none} }

.toolbar{
  position:sticky; top:0; z-index:50; background:#0f5c8c; color:#fff;
  padding:10px 18px; display:flex; gap:14px; align-items:center;
  justify-content:center; flex-wrap:wrap; font-size:13px;
  box-shadow:0 2px 8px rgba(0,0,0,.2);
}
.toolbar button{
  background:#fff; color:#0f5c8c; border:0; padding:8px 18px; border-radius:6px;
  font-family:inherit; font-size:13px; font-weight:700; cursor:pointer;
}
.toolbar button:hover{ background:#dbe9f2 }

h1,h2,h3,h4{ line-height:1.5; font-weight:800; }
h1{
  font-size:23px; color:var(--accent); margin:1.9em 0 .7em;
  padding-bottom:.35em; border-bottom:3px solid var(--accent);
  break-before:page;
}
h1:first-of-type{ break-before:auto; margin-top:.2em }
h2{
  font-size:18px; color:var(--h2); margin:1.7em 0 .6em;
  padding-bottom:.3em; border-bottom:1px solid var(--line);
}
h3{ font-size:15.5px; color:var(--h3); margin:1.4em 0 .5em }
h4{ font-size:14px; color:var(--h3); margin:1.2em 0 .4em }
p{ margin:.75em 0; text-align:justify; }
ul,ol{ margin:.7em 0; padding-right:1.5em; padding-left:0 }
li{ margin:.32em 0 }
li::marker{ color:var(--accent); font-weight:700 }
strong{ font-weight:800; color:#0d3f5f }
em{ font-style:italic; color:#33475b }
code{
  font-family:'Consolas','Courier New',monospace; direction:ltr; unicode-bidi:embed;
  background:#fdf1f1; color:#a8222a; padding:.12em .4em; border-radius:4px;
  font-size:.86em; display:inline-block;
}
pre{
  background:var(--code); border:1px solid #e2e2e2; border-radius:8px;
  padding:12px 14px; overflow-x:auto; direction:ltr; text-align:left;
  font-size:11.5px; line-height:1.55; margin:1em 0;
}
pre code{ background:none; color:#2b2b2b; padding:0; display:block; direction:ltr }
blockquote{
  margin:1em 0; padding:.85em 1.1em; background:#f4f7fa;
  border-right:5px solid var(--accent); border-radius:0 8px 8px 0;
  color:#223a4a;
}
blockquote p{ margin:.35em 0 }
hr{ border:0; border-top:1px solid #d8dee4; margin:2em 0 }
a{ color:var(--accent); text-decoration:none; border-bottom:1px dotted rgba(15,92,140,.4) }
a:hover{ border-bottom-style:solid }

table{
  width:100%; border-collapse:collapse; margin:1.1em 0; font-size:12.5px;
  direction:rtl;
}
th{
  background:var(--accent); color:#fff; font-weight:700; text-align:right;
  padding:8px 10px; border:1px solid #0d4f78; vertical-align:top;
}
td{ padding:7px 10px; border:1px solid var(--line); vertical-align:top }
tbody tr:nth-child(even) td{ background:var(--soft) }
thead{ display:table-header-group }

.cover{ text-align:center; padding:2.2em 0 1.4em; border-bottom:3px solid var(--accent); margin-bottom:1.6em }
.cover .kicker{ font-size:13px; letter-spacing:.02em; color:var(--muted); font-weight:700 }
.cover .title{ font-size:29px; font-weight:900; color:var(--accent); line-height:1.45; margin:.55em 0 .3em; white-space:pre-line }
.cover .subtitle{ font-size:16px; font-weight:700; color:var(--h3); margin:.35em 0 }
.cover .badge{
  display:inline-block; margin-top:1.1em; padding:.5em 1.2em; border-radius:8px;
  background:#fdecec; color:var(--alert); font-weight:800; font-size:14px;
  border:1px solid #f2c4c4;
}
.cover table{ margin:1.8em auto 0; max-width:92%; font-size:13px; text-align:right }
.cover table td:first-child{ background:#eaf1f6; font-weight:700; width:34% }

ul.task{ list-style:none; padding-right:.4em }
ul.task li{ padding-right:1.6em; position:relative }
ul.task li::before{
  content:"☐"; position:absolute; right:0; top:0; color:var(--accent);
  font-weight:700; font-size:1.05em;
}
"""

TOOLBAR = """
<div class="toolbar no-print">
  <span>برای ساخت PDF: دکمه زیر یا <b>Ctrl/Cmd + P</b> → «Save as PDF» → حاشیه: Default → «Background graphics» فعال</span>
  <button onclick="window.print()">🖨️ چاپ / ذخیره PDF</button>
</div>
"""


FONT_FACE = """
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-Regular.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-Bold.woff2') format('woff2');font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-Bold.woff2') format('woff2');font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-Bold.woff2') format('woff2');font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-ExtraBold.woff2') format('woff2');font-weight:800;font-style:normal;font-display:swap}
@font-face{font-family:'Vazirmatn';src:url('assets/fonts/Vazirmatn-ExtraBold.woff2') format('woff2');font-weight:900;font-style:normal;font-display:swap}
"""

CSS = FONT_FACE + _CSS_BODY


def esc(s):
    return html.escape(s, quote=False)


INLINE = re.compile(
    r"(\*\*\*.+?\*\*\*|\*\*.+?\*\*|__.+?__|\*[^*\n]+\*|`[^`\n]+`|\[[^\]]*\]\([^)]*\))",
    re.S,
)


def inline(text):
    text = text.replace("<br>", "<br/>").replace("<br/>", "<br/>")
    parts = []
    for chunk in INLINE.split(text):
        if not chunk:
            continue
        if chunk.startswith("***") and chunk.endswith("***") and len(chunk) > 6:
            parts.append(f"<strong><em>{inline(chunk[3:-3])}</em></strong>")
        elif chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
            parts.append(f"<strong>{inline(chunk[2:-2])}</strong>")
        elif chunk.startswith("__") and chunk.endswith("__") and len(chunk) > 4:
            parts.append(f"<strong>{inline(chunk[2:-2])}</strong>")
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            parts.append(f"<em>{inline(chunk[1:-1])}</em>")
        elif chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 2:
            parts.append(f"<code>{esc(chunk[1:-1])}</code>")
        elif chunk.startswith("[") and "](" in chunk and chunk.endswith(")"):
            m = re.match(r"\[([^\]]*)\]\(([^)]*)\)", chunk, re.S)
            if m:
                label, url = m.group(1) or m.group(2), m.group(2)
                if url.startswith(("http://", "https://")):
                    parts.append(f'<a href="{esc(url)}">{inline(label)}</a>')
                else:
                    parts.append(inline(label))
            else:
                parts.append(esc(chunk))
        else:
            parts.append(esc(chunk))
    return "".join(parts)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, cur, i = [], "", 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur += "|"
            i += 2
            continue
        if line[i] == "|":
            cells.append(cur)
            cur = ""
        else:
            cur += line[i]
        i += 1
    cells.append(cur)
    return [c.strip() for c in cells]


def is_sep(line):
    s = line.strip()
    return bool(re.match(r"^\|?[\s:\-|]+\|?$", s)) and "-" in s and "|" in s


def render(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    skip_h1 = True
    list_stack = []

    def close_lists():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < n:
        line = lines[i]
        s = line.strip()

        if s.startswith("```"):
            close_lists()
            j, buf = i + 1, []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append("<pre><code>" + esc("\n".join(buf)) + "</code></pre>")
            i = j + 1
            continue

        if not s:
            close_lists()
            i += 1
            continue

        if re.match(r"^-{3,}$|^\*{3,}$|^_{3,}$", s):
            close_lists()
            out.append("<hr/>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            close_lists()
            lvl = len(m.group(1))
            if lvl == 1 and skip_h1:
                skip_h1 = False
                i += 1
                continue
            out.append(f"<h{min(lvl,4)}>{inline(m.group(2).strip())}</h{min(lvl,4)}>")
            i += 1
            continue

        if s.startswith("|") and i + 1 < n and is_sep(lines[i + 1]):
            close_lists()
            rows = [split_row(s)]
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            w = max(len(r) for r in rows)
            rows = [r + [""] * (w - len(r)) for r in rows]
            t = ["<table>", "<thead><tr>"]
            for c in rows[0]:
                t.append(f"<th>{inline(c)}</th>")
            t.append("</tr></thead><tbody>")
            for r in rows[1:]:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            i = j
            continue

        if s.startswith(">"):
            close_lists()
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner = " ".join(x.strip() for x in buf if x.strip())
            out.append(f"<blockquote><p>{inline(inner)}</p></blockquote>")
            continue

        m = re.match(r"^(\s*)-\s+\[[ xX]\]\s+(.*)$", line)
        if m:
            if not list_stack or list_stack[-1] != "ul class=task":
                close_lists()
                out.append('<ul class="task">')
                list_stack.append("ul class=task")
            out.append(f"<li>{inline(m.group(2).strip())}</li>")
            i += 1
            continue

        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            marker = m.group(2)
            tag = "ol" if marker[0].isdigit() else "ul"
            if not list_stack or list_stack[-1] != tag:
                close_lists()
                out.append(f"<{tag}>")
                list_stack.append(tag)
            out.append(f"<li>{inline(m.group(3).strip())}</li>")
            i += 1
            continue

        close_lists()
        buf = [s]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "```"))
                    or re.match(r"^-{3,}$", nxt)
                    or re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i])):
                break
            buf.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    close_lists()
    return "\n".join(out)


def cover_html(meta):
    parts = ['<div class="cover">']
    if meta.get("kicker"):
        parts.append(f'<div class="kicker">{esc(meta["kicker"])}</div>')
    parts.append(f'<div class="title">{esc(meta.get("title",""))}</div>')
    if meta.get("subtitle"):
        parts.append(f'<div class="subtitle">{esc(meta["subtitle"])}</div>')
    if meta.get("badge"):
        parts.append(f'<div class="badge">{esc(meta["badge"])}</div>')
    facts = meta.get("facts") or []
    if facts:
        parts.append("<table><tbody>")
        for k, v in facts:
            parts.append(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>")
        parts.append("</tbody></table>")
    parts.append("</div>")
    return "\n".join(parts)


def build(key, spec):
    with open(os.path.join(ROOT, spec["src"]), "r", encoding="utf-8") as f:
        md = f.read()
    meta = spec["cover"]
    title = meta.get("title", "").replace("\n", " ")
    doc = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
{TOOLBAR}
<div class="sheet">
{cover_html(meta)}
{render(md)}
</div>
</body>
</html>
"""
    out = os.path.join(ROOT, spec["out"].replace(".docx", ".html"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return out


def main():
    sys.path.insert(0, os.path.join(ROOT, "build"))
    from md2docx import DOCS  # reuse the same spec table

    keys = sys.argv[1:] or list(DOCS.keys())
    for k in keys:
        if k not in DOCS:
            print(f"SKIP {k}")
            continue
        p = build(k, DOCS[k])
        print(f"OK  {k} -> {p}  ({os.path.getsize(p)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
