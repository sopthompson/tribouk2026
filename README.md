# TriboUK 2026 — Conference Programme

Website **and** print PDF for the TriboUK 2026 Postgraduate Tribology Conference
(University of Sheffield, 1–2 July 2026).

- **Live site:** https://tribouk2026.github.io/programme/
- **Download PDF:** https://tribouk2026.github.io/programme/TriboUK-2026-Programme.pdf

## Layout
- `docs/` — the published website (GitHub Pages serves this folder).
  - `index.html`, `site.css`, `site.js` — the website.
  - `data.js` — all content (schedule, keynotes, posters, sponsors). **Edit this to change the programme.**
  - `TriboUK-2026-Programme.pdf` — the downloadable PDF, linked from the site.
  - `img/` — logos and sponsor images.
  - `programme.html`, `styles.css`, `render.js` — print layout used to build the PDF.
- `build.py` — renders `docs/programme.html` to the PDF (headless Chrome) and stamps the header band + page numbers.
- `generate_data.py` — regenerates `docs/data.js` from the abstract spreadsheet (kept locally, **not** in this repo).

## Updating the programme
1. Edit `docs/data.js` (or re-run `python3 generate_data.py` after updating the spreadsheet).
2. Rebuild the PDF: `python3 build.py`.
3. Commit and push — GitHub Pages redeploys automatically.
