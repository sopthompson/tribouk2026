#!/usr/bin/env python3
"""Render web/programme.html to PDF via headless Chrome, then stamp the running
purple header band, footer rule and page numbers with PyMuPDF.

Usage:  python3 build.py
Output: TriboUK 2026 - Conference Programme (web).pdf
"""
import os, sys, subprocess, tempfile
import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "docs", "programme.html")
OUT  = os.path.join(HERE, "docs", "TriboUK-2026-Programme.pdf")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]
WHITE_LOGO = os.path.join(HERE, "docs", "img", "Logo_TriboUK_full_white.png")
PURPLE = (0x44/255, 0x00/255, 0x99/255)
SKY    = (0x9A/255, 0xDB/255, 0xE8/255)
LILAC  = (0xD0/255, 0xBF/255, 0xE5/255)
GREY   = (0x6B/255, 0x6E/255, 0x78/255)
LINE   = (0xE4/255, 0xDE/255, 0xF0/255)
MM = 72/25.4

def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p): return p
    sys.exit("No Chrome/Edge/Chromium found — install one or add it to build.py")

def render_html(chrome):
    raw = os.path.join(tempfile.gettempdir(), "triBoUK_raw.pdf")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--virtual-time-budget=6000", f"--print-to-pdf={raw}",
           "file://" + HTML]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return raw

# running header title per section — detected from the page's own heading,
# carried forward onto that section's continuation pages
SECTION_ANCHORS = [
    ("Welcome to TriboUK",   "Welcome"),
    ("DAY 1",                "Schedule"),
    ("DAY 2",                "Schedule"),
    ("Keynote Speakers",     "Keynote Speakers"),
    ("Oral Presentations",   "Oral Presentations"),
    ("Poster Presentations", "Poster Presentations"),
    ("Voting",               "Voting"),
    ("Our Sponsors",         "Sponsors & Partners"),
    ("Organising Committee", "Organising Committee"),
]

def stamp(raw):
    doc = fitz.open(raw)
    # drop empty pages that multi-column + forced page-break can emit in Chromium
    drop = [i for i in range(1, doc.page_count)
            if not doc[i].get_text().strip() and not doc[i].get_images()]
    for i in reversed(drop):
        doc.delete_page(i)
    W = doc[0].rect.width
    pm = fitz.Pixmap(WHITE_LOGO); logo_ratio = pm.width / pm.height
    current = "TriboUK 2026"
    for i, page in enumerate(doc):
        if i == 0:
            continue  # cover: full-bleed, no chrome
        txt = page.get_text()
        for anchor, title in SECTION_ANCHORS:
            if anchor in txt:
                current = title
                break
        # ---- header band (sits in the 24 mm top @page margin) ----
        page.draw_rect(fitz.Rect(0, 0, W, 20.5*MM), color=None, fill=PURPLE)
        page.draw_rect(fitz.Rect(0, 20.5*MM, W, 22*MM), color=None, fill=SKY)
        page.insert_text((18*MM, 13*MM), current,
                         fontname="hebo", fontsize=15, color=(1, 1, 1))
        # white TriboUK logo on the right
        lh = 17*MM
        lw = lh * logo_ratio
        ly = (20.5*MM - lh) / 2
        lrect = fitz.Rect(W-18*MM-lw, ly, W-18*MM, ly+lh)
        page.insert_image(lrect, filename=WHITE_LOGO, keep_proportion=True)
        # ---- footer rule + text + page number ----
        fy = page.rect.height - 9*MM
        page.draw_line(fitz.Point(18*MM, fy), fitz.Point(W-18*MM, fy), color=LINE, width=0.6)
        page.insert_text((18*MM, fy+3.5*MM), "TriboUK 2026 · University of Sheffield",
                         fontname="helv", fontsize=8, color=GREY)
        num = str(i)  # cover unnumbered; first interior page = 1
        tw = fitz.get_text_length(num, fontname="helv", fontsize=8)
        page.insert_text((W-18*MM-tw, fy+3.5*MM), num, fontname="helv", fontsize=8, color=GREY)
    doc.save(OUT, deflate=True, garbage=4)
    doc.close()

if __name__ == "__main__":
    chrome = find_chrome()
    raw = render_html(chrome)
    stamp(raw)
    os.remove(raw)
    print("FINAL ->", OUT, "pages:", fitz.open(OUT).page_count)
