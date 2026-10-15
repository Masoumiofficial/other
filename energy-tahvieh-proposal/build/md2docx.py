#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown -> DOCX converter with full Persian/RTL support.

Builds employer-facing and internal dossiers for the Energy Tahvieh proposal.
RTL handling is done at three levels:
  1. Document defaults (styles)      -> w:bidi on paragraph properties
  2. Every emitted paragraph         -> w:bidi + right alignment
  3. Every table                     -> w:bidiVisual + right-to-left column order
"""
import os
import re
import sys

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
FA_FONT = "B Nazanin"          # widely available Persian Word font
FA_FONT_ALT = "Vazirmatn"      # modern fallback if the user has it
LATIN_FONT = "Calibri"
MONO_FONT = "Consolas"

BODY_SIZE = Pt(10.5)
H1_SIZE = Pt(18)
H2_SIZE = Pt(14.5)
H3_SIZE = Pt(12.5)
H4_SIZE = Pt(11.5)

COLOR_ACCENT = RGBColor(0x0F, 0x5C, 0x8C)     # deep blue
COLOR_H2 = RGBColor(0x14, 0x3D, 0x59)
COLOR_H3 = RGBColor(0x1F, 0x5C, 0x82)
COLOR_MUTED = RGBColor(0x5A, 0x5A, 0x5A)
COLOR_ALERT = RGBColor(0xA8, 0x22, 0x22)

PAGE_W = Cm(21.0)      # A4
PAGE_H = Cm(29.7)
MARGIN = Cm(2.0)


# --------------------------------------------------------------------------
# Low-level XML helpers
# --------------------------------------------------------------------------
def _el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k.replace("_", ":")), v)
    return e


def set_bidi(paragraph, bidi=True):
    """Force right-to-left paragraph direction."""
    pPr = paragraph._p.get_or_add_pPr()
    for existing in pPr.findall(qn("w:bidi")):
        pPr.remove(existing)
    pPr.append(_el("w:bidi", w_val="1" if bidi else "0"))


def set_rtl_run(run):
    """Mark a run as complex-script (RTL)."""
    rPr = run._r.get_or_add_rPr()
    if not rPr.findall(qn("w:rtl")):
        rPr.append(_el("w:rtl", w_val="1"))


def set_run_fonts(run, size=None, bold=None, color=None, mono=False):
    latin = MONO_FONT if mono else LATIN_FONT
    cs = MONO_FONT if mono else FA_FONT
    run.font.name = latin
    rPr = run._r.get_or_add_rPr()

    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), latin)
    rFonts.set(qn("w:hAnsi"), latin)
    rFonts.set(qn("w:cs"), cs)
    rFonts.set(qn("w:eastAsia"), latin)

    sz_val = str(int((size or BODY_SIZE).pt * 2))
    for tag in ("w:sz", "w:szCs"):
        for old in rPr.findall(qn(tag)):
            rPr.remove(old)
        rPr.append(_el(tag, w_val=sz_val))

    if bold is not None:
        run.bold = bold
        for tag in ("w:b", "w:bCs"):
            for old in rPr.findall(qn(tag)):
                rPr.remove(old)
            if bold:
                rPr.append(_el(tag))

    if color is not None:
        run.font.color.rgb = color

    set_rtl_run(run)


def set_cell_shading(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:shd")):
        tcPr.remove(old)
    tcPr.append(_el("w:shd", w_val="clear", w_color="auto", w_fill=hex_fill))


def set_cell_bidi(cell):
    for p in cell.paragraphs:
        set_bidi(p)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def set_table_rtl(table):
    tblPr = table._tbl.tblPr
    for tag in ("w:bidiVisual", "w:rightToLeft"):
        for old in tblPr.findall(qn(tag)):
            tblPr.remove(old)
    tblPr.append(_el("w:bidiVisual"))


def set_table_borders(table, color="BFBFBF"):
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(_el(f"w:{edge}", w_val="single", w_sz="4",
                           w_space="0", w_color=color))
    tblPr.append(borders)


def add_paragraph_shading(paragraph, hex_fill):
    pPr = paragraph._p.get_or_add_pPr()
    for old in pPr.findall(qn("w:shd")):
        pPr.remove(old)
    pPr.append(_el("w:shd", w_val="clear", w_color="auto", w_fill=hex_fill))


def add_paragraph_border(paragraph, color="0F5C8C", edge="right"):
    pPr = paragraph._p.get_or_add_pPr()
    pbdr = pPr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        pPr.append(pbdr)
    pbdr.append(_el(f"w:{edge}", w_val="single", w_sz="18",
                    w_space="8", w_color=color))


def add_hr(document, color="C8C8C8"):
    p = document.add_paragraph()
    set_bidi(p)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    pbdr.append(_el("w:bottom", w_val="single", w_sz="6",
                    w_space="1", w_color=color))
    pPr.append(pbdr)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    return p


# --------------------------------------------------------------------------
# Document setup
# --------------------------------------------------------------------------
def new_document():
    doc = Document()

    sec = doc.sections[0]
    sec.page_width = PAGE_W
    sec.page_height = PAGE_H
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.left_margin = MARGIN
    sec.right_margin = MARGIN
    sec.top_margin = Cm(1.8)
    sec.bottom_margin = Cm(1.8)
    sec.header_distance = Cm(1.0)
    sec.footer_distance = Cm(1.0)

    # RTL section
    sectPr = sec._sectPr
    for old in sectPr.findall(qn("w:bidi")):
        sectPr.remove(old)
    sectPr.append(_el("w:bidi", w_val="1"))

    # Normal style
    normal = doc.styles["Normal"]
    normal.font.name = LATIN_FONT
    normal.font.size = BODY_SIZE
    rPr = normal.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), LATIN_FONT)
    rFonts.set(qn("w:hAnsi"), LATIN_FONT)
    rFonts.set(qn("w:cs"), FA_FONT)
    if not rPr.findall(qn("w:rtl")):
        rPr.append(_el("w:rtl", w_val="1"))

    pf = normal.paragraph_format
    pf.space_after = Pt(6)
    pf.line_spacing = 1.32
    pf.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pPr = normal.element.get_or_add_pPr()
    if not pPr.findall(qn("w:bidi")):
        pPr.append(_el("w:bidi", w_val="1"))

    return doc


def add_page_number_footer(doc, left_text=""):
    footer = doc.sections[0].footer
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.text = ""
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if left_text:
        r = p.add_run(left_text + "   |   صفحه ")
        set_run_fonts(r, size=Pt(8.5), color=COLOR_MUTED)
    else:
        r = p.add_run("صفحه ")
        set_run_fonts(r, size=Pt(8.5), color=COLOR_MUTED)

    r2 = p.add_run()
    set_run_fonts(r2, size=Pt(8.5), color=COLOR_MUTED)
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    r2._r.append(fld1); r2._r.append(instr); r2._r.append(fld2)

    r3 = p.add_run(" از ")
    set_run_fonts(r3, size=Pt(8.5), color=COLOR_MUTED)
    r4 = p.add_run()
    set_run_fonts(r4, size=Pt(8.5), color=COLOR_MUTED)
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
    it.text = " NUMPAGES "
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r4._r.append(f1); r4._r.append(it); r4._r.append(f2)


# --------------------------------------------------------------------------
# Inline markdown -> runs
# --------------------------------------------------------------------------
INLINE_RE = re.compile(
    r"(\*\*\*.+?\*\*\*"       # ***bold italic***
    r"|\*\*.+?\*\*"           # **bold**
    r"|__.+?__"               # __bold__
    r"|\*[^*\n]+\*"           # *italic*
    r"|`[^`\n]+`"             # `code`
    r"|\[[^\]]*\]\([^)]*\)"   # [text](url)
    r")",
    re.S,
)


def emit_inline(paragraph, text, base_size=None, base_color=None,
                base_bold=False):
    text = text.replace("<br>", " ").replace("<br/>", " ")
    for chunk in INLINE_RE.split(text):
        if not chunk:
            continue
        bold, italic, mono, color = base_bold, False, False, base_color
        content = chunk

        if chunk.startswith("***") and chunk.endswith("***") and len(chunk) > 6:
            content, bold, italic = chunk[3:-3], True, True
        elif chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
            content, bold = chunk[2:-2], True
        elif chunk.startswith("__") and chunk.endswith("__") and len(chunk) > 4:
            content, bold = chunk[2:-2], True
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            content, italic = chunk[1:-1], True
        elif chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 2:
            content, mono = chunk[1:-1], True
            color = color or RGBColor(0xB0, 0x30, 0x30)
        elif chunk.startswith("[") and "](" in chunk and chunk.endswith(")"):
            m = re.match(r"\[([^\]]*)\]\(([^)]*)\)", chunk, re.S)
            if m:
                content = m.group(1) or m.group(2)
                color = COLOR_ACCENT

        content = content.replace("\\|", "|")
        if not content:
            continue
        run = paragraph.add_run(content)
        set_run_fonts(run, size=base_size or BODY_SIZE,
                      bold=bold or None, color=color, mono=mono)
        if italic:
            run.italic = True


def strip_md(text):
    text = re.sub(r"\*\*\*|\*\*|__|(?<!\w)\*|\*(?!\w)|`", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("<br>", " ").replace("\\|", "|")
    return text.strip()


# --------------------------------------------------------------------------
# Block builders
# --------------------------------------------------------------------------
def add_heading(doc, text, level):
    sizes = {1: H1_SIZE, 2: H2_SIZE, 3: H3_SIZE, 4: H4_SIZE}
    colors = {1: COLOR_ACCENT, 2: COLOR_H2, 3: COLOR_H3, 4: COLOR_H3}
    p = doc.add_paragraph()
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.space_before = Pt(20 if level <= 2 else 14)
    pf.space_after = Pt(8 if level <= 2 else 5)
    pf.keep_with_next = True
    emit_inline(p, text, base_size=sizes.get(level, H4_SIZE),
                base_color=colors.get(level, COLOR_H3), base_bold=True)
    if level == 1:
        add_paragraph_border(p, color="0F5C8C", edge="bottom")
    elif level == 2:
        add_paragraph_border(p, color="D6E3EC", edge="bottom")
    return p


def add_body(doc, text):
    p = doc.add_paragraph()
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    emit_inline(p, text)
    return p


def add_list_item(doc, text, level=0, ordered=False, number=None):
    p = doc.add_paragraph()
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.right_indent = Cm(0.6 + level * 0.7)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.28
    bullet = f"{number}. " if ordered else ("•  " if level == 0 else "–  ")
    r = p.add_run(bullet)
    set_run_fonts(r, color=COLOR_ACCENT, bold=True)
    emit_inline(p, text)
    return p


def add_task_item(doc, text, level=0):
    p = doc.add_paragraph()
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.right_indent = Cm(0.6 + level * 0.7)
    pf.space_after = Pt(2)
    r = p.add_run("☐  ")
    set_run_fonts(r, color=COLOR_ACCENT, bold=True, size=Pt(11))
    emit_inline(p, text)
    return p


def add_quote(doc, text):
    p = doc.add_paragraph()
    set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.right_indent = Cm(0.5)
    pf.left_indent = Cm(0.3)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    add_paragraph_shading(p, "F4F7FA")
    add_paragraph_border(p, color="0F5C8C", edge="right")
    emit_inline(p, text, base_color=RGBColor(0x22, 0x3A, 0x4A))
    return p


def add_code_block(doc, lines):
    for i, line in enumerate(lines):
        p = doc.add_paragraph()
        set_bidi(p, bidi=False)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = p.paragraph_format
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.05
        pf.left_indent = Cm(0.4)
        pf.right_indent = Cm(0.4)
        add_paragraph_shading(p, "F5F5F5")
        r = p.add_run(line if line else " ")
        set_run_fonts(r, size=Pt(8.5), mono=True,
                      color=RGBColor(0x2B, 0x2B, 0x2B))
        # code blocks: keep LTR for ASCII art but allow the box to draw
        rPr = r._r.get_or_add_rPr()
        for old in rPr.findall(qn("w:rtl")):
            rPr.remove(old)


def _split_row(line):
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


def add_table(doc, rows):
    if not rows:
        return None
    n_cols = max(len(r) for r in rows)
    rows = [r + [""] * (n_cols - len(r)) for r in rows]

    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.RIGHT
    table.autofit = True
    set_table_rtl(table)
    set_table_borders(table)

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = ""
            para = cell.paragraphs[0]
            set_bidi(para)
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            para.paragraph_format.space_after = Pt(2)
            para.paragraph_format.space_before = Pt(2)
            para.paragraph_format.line_spacing = 1.15

            if ri == 0:
                set_cell_shading(cell, "0F5C8C")
                emit_inline(para, val, base_size=Pt(9.5),
                            base_color=RGBColor(0xFF, 0xFF, 0xFF),
                            base_bold=True)
            else:
                if ri % 2 == 0:
                    set_cell_shading(cell, "F6F9FB")
                emit_inline(para, val, base_size=Pt(9.5))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_callout(doc, title, body, fill="FFF6E5", bar="C8881A"):
    if title:
        p = doc.add_paragraph()
        set_bidi(p)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_paragraph_shading(p, fill)
        add_paragraph_border(p, color=bar, edge="right")
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        set_run_fonts(r, size=Pt(10.5), bold=True,
                      color=RGBColor(0x7A, 0x52, 0x0F))
    p2 = doc.add_paragraph()
    set_bidi(p2)
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_paragraph_shading(p2, fill)
    add_paragraph_border(p2, color=bar, edge="right")
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(8)
    emit_inline(p2, body, base_size=Pt(10))
    return p2


# --------------------------------------------------------------------------
# Title page / cover
# --------------------------------------------------------------------------
def add_cover(doc, meta):
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph(); set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(meta.get("kicker", ""))
    set_run_fonts(r, size=Pt(11), bold=True, color=COLOR_MUTED)

    p = doc.add_paragraph(); set_bidi(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(meta.get("title", ""))
    set_run_fonts(r, size=Pt(26), bold=True, color=COLOR_ACCENT)

    if meta.get("subtitle"):
        p = doc.add_paragraph(); set_bidi(p)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(meta["subtitle"])
        set_run_fonts(r, size=Pt(14), bold=True, color=COLOR_H3)

    add_hr(doc, color="0F5C8C")

    if meta.get("badge"):
        p = doc.add_paragraph(); set_bidi(p)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(10)
        r = p.add_run(meta["badge"])
        set_run_fonts(r, size=Pt(12), bold=True, color=COLOR_ALERT)

    doc.add_paragraph()

    rows = [[k, v] for k, v in meta.get("facts", [])]
    if rows:
        t = doc.add_table(rows=len(rows), cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_rtl(t)
        set_table_borders(t, color="D6E3EC")
        for ri, (k, v) in enumerate(rows):
            for ci, val in enumerate((k, v)):
                cell = t.cell(ri, ci)
                cell.text = ""
                para = cell.paragraphs[0]
                set_bidi(para)
                para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                para.paragraph_format.space_before = Pt(3)
                para.paragraph_format.space_after = Pt(3)
                if ci == 0:
                    set_cell_shading(cell, "EAF1F6")
                emit_inline(para, val, base_size=Pt(10),
                            base_bold=(ci == 0))
        t.columns[0].width = Cm(5.2)
        t.columns[1].width = Cm(11.0)

    doc.add_page_break()


# --------------------------------------------------------------------------
# Markdown parser
# --------------------------------------------------------------------------
def is_table_sep(line):
    s = line.strip()
    return bool(re.match(r"^\|?[\s:\-|]+\|?$", s)) and "-" in s and "|" in s


def render_markdown(doc, md):
    lines = md.split("\n")
    i = 0
    n = len(lines)
    skip_first_h1 = True

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code
        if stripped.startswith("```"):
            j = i + 1
            buf = []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            add_code_block(doc, buf)
            i = j + 1
            continue

        # blank
        if not stripped:
            i += 1
            continue

        # horizontal rule
        if re.match(r"^-{3,}$|^\*{3,}$|^_{3,}$", stripped):
            add_hr(doc)
            i += 1
            continue

        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if level == 1 and skip_first_h1:
                skip_first_h1 = False
                i += 1
                continue
            add_heading(doc, text, min(level, 4))
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            rows = [_split_row(stripped)]
            j = i + 2
            while j < n and lines[j].strip().startswith("|"):
                rows.append(_split_row(lines[j]))
                j += 1
            add_table(doc, rows)
            i = j
            continue

        # blockquote
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            text = " ".join(x.strip() for x in buf if x.strip())
            add_quote(doc, text)
            continue

        # task list
        m = re.match(r"^(\s*)-\s+\[[ xX]\]\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            add_task_item(doc, m.group(2).strip(), level=indent // 2)
            i += 1
            continue

        # list items
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            indent = len(m.group(1))
            marker = m.group(2)
            content = m.group(3).strip()
            ordered = marker[0].isdigit()
            number = marker.rstrip(".") if ordered else None
            add_list_item(doc, content, level=indent // 2,
                          ordered=ordered, number=number)
            i += 1
            continue

        # paragraph (collect until blank / block start)
        buf = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith("#") or nxt.startswith("|")
                    or nxt.startswith(">") or nxt.startswith("```")
                    or re.match(r"^-{3,}$", nxt)
                    or re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[i])):
                break
            buf.append(nxt)
            i += 1
        add_body(doc, " ".join(buf))

    return doc


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
DOCS = {
    "01": {
        "src": "docs/01-خلاصه-تحلیل-اولیه.md",
        "out": "build/01-خلاصه-تحلیل-اولیه-انرژی-تهویه.docx",
        "cover": {
            "kicker": "سند تحلیلی — نسخه داخلی",
            "title": "خلاصه تحلیل اولیه سایت انرژی تهویه",
            "subtitle": "تفکیک یافته‌های تأییدشده از فرضیه‌ها",
            "facts": [
                ("تهیه‌کننده", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("سایت هدف", "https://energytahvieh.com/"),
                ("یافته تأییدشده", "۵۵ مورد با شاهد مستقیم"),
                ("استنتاج فنی", "۱۲ مورد (نیازمند تأیید)"),
                ("محدودیت", "۸ مورد ذاتی روش + ۲۵ داده غایب"),
            ],
            "footer": "خلاصه تحلیل اولیه — انرژی تهویه",
        },
    },
    "02": {
        "src": "docs/02-پروپوزال-کارفرما.md",
        "out": "build/02-پروپوزال-راهبردی-انرژی-تهویه.docx",
        "cover": {
            "kicker": "پروپوزال رسمی همکاری",
            "title": "پروپوزال راهبردی توسعه و بهینه‌سازی\nاکوسیستم دیجیتال انرژی تهویه",
            "subtitle": "تحلیل وضعیت موجود · چشم‌انداز رشد · برنامه اجرایی · پیشنهاد همکاری",
            "facts": [
                ("ارائه‌شده به", "مدیریت محترم عامل / منابع انسانی — انرژی تهویه"),
                ("ارائه‌شده از سوی", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("سایت هدف", "https://energytahvieh.com/"),
                ("نقش پیشنهادی", "مدیر رشد دیجیتال و توسعه تجارت الکترونیک"),
            ],
            "footer": "پروپوزال راهبردی — انرژی تهویه",
        },
    },
    "03": {
        "src": "docs/03-سند-محرمانه-داخلی.md",
        "out": "build/03-سند-محرمانه-داخلی-انرژی-تهویه.docx",
        "cover": {
            "kicker": "🔒 محرمانه — نسخه شخصی",
            "title": "سند محرمانه تحلیل، برنامه اجرایی\nو استراتژی رشد دیجیتال انرژی تهویه",
            "subtitle": "نسخه داخلی سجاد معصومی",
            "badge": "⛔ این سند برای ارائه به کارفرما نیست",
            "facts": [
                ("مالک سند", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("طبقه‌بندی", "محرمانه — شخصی"),
                ("بخش‌ها", "۱۴ بخش + پیوست"),
                ("اقدامات بک‌لاگ", "۲۸ اقدام با قالب ۱۶ فیلدی"),
            ],
            "footer": "🔒 سند محرمانه داخلی — انرژی تهویه",
        },
    },
    "04": {
        "src": "docs/04-راهنمای-مذاکره.md",
        "out": "build/04-راهنمای-مذاکره-انرژی-تهویه.docx",
        "cover": {
            "kicker": "🔒 راهنمای شخصی",
            "title": "راهنمای مذاکره حقوق و شرایط همکاری",
            "subtitle": "انرژی تهویه — نقش مدیر رشد دیجیتال و توسعه تجارت الکترونیک",
            "badge": "مبلغ هدف: ۷۵٬۰۰۰٬۰۰۰ تومان در ماه",
            "facts": [
                ("تهیه‌کننده", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("طبقه‌بندی", "شخصی — محرمانه"),
                ("بخش‌ها", "متن‌های آماده ارسال · دفاع شفاهی · ۶ اعتراض · ۳۰ پرسش · خط قرمزها"),
            ],
            "footer": "راهنمای مذاکره — انرژی تهویه",
        },
    },
    "05": {
        "src": "docs/05-چک‌لیست-دسترسی‌ها.md",
        "out": "build/05-چک‌لیست-دسترسی‌ها-انرژی-تهویه.docx",
        "cover": {
            "kicker": "پیوست عملیاتی — قابل ارسال به کارفرما",
            "title": "چک‌لیست اطلاعات و دسترسی‌های\nمورد نیاز در شروع همکاری",
            "subtitle": "پیش‌نیاز اجرای فاز صفر در سه هفته",
            "facts": [
                ("تهیه‌کننده", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("سطوح اولویت", "۴ سطح (حیاتی / ضروری / مهم / تسهیل‌کننده)"),
                ("موارد", "بیش از ۷۰ قلم دسترسی و اطلاعات"),
            ],
            "footer": "چک‌لیست دسترسی‌ها — انرژی تهویه",
        },
    },
    "06": {
        "src": "docs/06-محدودیت‌ها.md",
        "out": "build/06-محدودیت‌ها-و-موارد-معلق-انرژی-تهویه.docx",
        "cover": {
            "kicker": "پیوست شفافیت",
            "title": "فهرست محدودیت‌ها و موارد\nغیرقابل نتیجه‌گیری",
            "subtitle": "آنچه این تحلیل نمی‌تواند بگوید",
            "facts": [
                ("تهیه‌کننده", "سجاد معصومی"),
                ("تاریخ", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("محدودیت روش", "۸ مورد"),
                ("داده غایب", "۲۵ مورد"),
                ("فرضیه تأییدنشده", "۱۸ مورد"),
            ],
            "footer": "محدودیت‌ها و موارد معلق — انرژی تهویه",
        },
    },
    "00": {
        "src": "evidence/00-evidence-log.md",
        "out": "build/00-سند-شواهد-انرژی-تهویه.docx",
        "cover": {
            "kicker": "🔒 سند پشتیبان شواهد",
            "title": "Evidence Log — انرژی تهویه",
            "subtitle": "ثبت یافته‌های تأییدشده با شاهد مستقیم",
            "facts": [
                ("تهیه‌کننده", "سجاد معصومی"),
                ("تاریخ بررسی", "۲۳ مهر ۱۴۰۵ / ۱۵ اکتبر ۲۰۲۶"),
                ("نسخه", "1.0"),
                ("روش", "بازیابی مستقیم صفحات عمومی + sitemap/robots + منابع عمومی بازار"),
            ],
            "footer": "سند شواهد — انرژی تهویه",
        },
    },
}


def build(key, root):
    spec = DOCS[key]
    src = os.path.join(root, spec["src"])
    out = os.path.join(root, spec["out"])
    with open(src, "r", encoding="utf-8") as f:
        md = f.read()

    doc = new_document()
    cover = dict(spec["cover"])
    footer_text = cover.pop("footer", "")
    add_cover(doc, cover)
    render_markdown(doc, md)
    add_page_number_footer(doc, footer_text)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc.save(out)
    return out


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    keys = sys.argv[1:] or list(DOCS.keys())
    for k in keys:
        if k not in DOCS:
            print(f"SKIP unknown key: {k}")
            continue
        p = build(k, root)
        size = os.path.getsize(p)
        print(f"OK  {k} -> {p}  ({size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
