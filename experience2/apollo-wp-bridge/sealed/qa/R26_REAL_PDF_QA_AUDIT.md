# Apollo Experience 2.0 — R26 actual-PDF custody QA (DRAFT/HOLD)

**Scope:** Staged Apollo 1 print ledger only. Base: draft Apollo R25 PR #339, exact parent `d1de0fa0fdba8b66698dc5d0c18d69a6cd655d6c`. No change to homepage PR #49, its lead's branches, Research Desk PR #158, WordPress content or settings, main or production.

## Improvement

The six-source NASA print ledger now prints immutable identifiers for the **staged files used to produce it**: pinned casefile commit `74375657f2cdaac0710f94c6de6c24534ee06858`, `records.json` SHA-256 `8592bfc7e3a1dbb0dde3d15c40241070b973772813b93427c06fd8d64603541d`, and generated `evidence-export.json` SHA-256 `60941d48649f68add5ab5d5ca47be68ab7eb7a56a859de2e33de937caaf92c85`. These identify staged bytes, **not independent NASA authentication, copyright clearance or endorsement**. Six photographs remain external NASA links; `S67-19766` catalog-label dispute unresolved; zero approved map coordinates/edges.

The R26 browser test actually calls Chromium `page.pdf()` with JS **disabled**, verifies readable PDF text and 3-page A4 pagination at **320, 360, 390, 768, 1024, 1440, 1920** viewport widths, checks all six source-link URLs and individual nonreuse notices, confirms each record's notice stays on its record page, checks PDF image-object count is zero with `pdfimages -list`, and extracts fingerprints with `pdftotext`. Two screenshot PNGs are rasterizations of actual generated PDFs, not HTML-only screenshots. Chromium PDF bytes can contain render-environment/metadata differences; do **not** treat repeated PDF byte identity as guaranteed.

## Actually run locally (2026-10-31)

- Recovered the R25 staging source package from the prior sprint archives, restoring historical modules from source bridges. **156/156** reconstructed Python tests passed, including new R26 offline fingerprint tests and prior mutation/security tests. This is not a claim of a full pristine exact-head Git checkout (R25 previously reported 159 tests).
- R25 existing Chromium print suite: **7/7 PASS** after the R26 generator change. New actual Chromium `page.pdf()` + PDF-tools audit: **7/7 PASS**; three A4 pages at all seven widths, six source URLs and rights warnings each, catalog identity warning, no embedded images or nonce/admin links.
- PHP `-l` on sealed staging template: PASS.
- Two private PHP package builds byte-identical: ZIP SHA-256 `f3ad3d4a5cbf020a9e33ed70685a545e0187ee888dd89f7ea3e7e27ba7ac4d50` (the ZIP is a sealed staging package **not an installation instruction**).
- Three changed code blob hashes: generator `1925540075667d432e976f404112eb58b64e692a`; unit contract `fb0869ce8e6054426677d95300bcbc4347c61a51`; real-PDF browser test `d99f224dcb3e5f8293f8e876b66438c0c5589fde`. Locally tested source matches these Git blobs.

## Reproduce

From the **complete, clean Git checkout** of the R26 head:

```sh
cd experience2/apollo-wp-bridge/sealed
PYTHONPATH=qa python -m unittest discover -s qa -p 'test_*.py'
python qa/browser_print_r25.py
python qa/browser_pdf_r26.py
php -l fv-ex2-apollo-sealed-template.php
python build_sealed.py --out /tmp/apollo-r26-a.zip
python build_sealed.py --out /tmp/apollo-r26-b.zip
cmp /tmp/apollo-r26-a.zip /tmp/apollo-r26-b.zip
sha256sum /tmp/apollo-r26-a.zip
```

Requires Chromium, Playwright for Python, PHP, and Poppler tools (`pdfinfo`, `pdftotext`, `pdfimages`, `pdftoppm`). The browser test writes `qa/R26_REAL_PDF_RESULTS.json`, seven generated PDF files and two rasterized first-page PNGs. Screenshots/PDF binary evidence distributed separately in the QA archive; no sensitive WordPress assets or credentials included.

## Explicit release gates

**HOLD.** No real authenticated WordPress/Assembler staging install; no browser-enforced HTTP/CSP/cookies; no authenticated hosted CDN/rights tests; no independently version/SHA-verified axe-core bundle (npm could not resolve registry DNS); no Safari/VoiceOver/NVDA or zoom/reflow manual signoff; no production p75 LCP/INP/CLS; no individual NASA photo-reuse clearance; unresolved first-photo catalog ID; no independent QD, successful hosted CI, or founder publication approval. None of those gates is asserted passing. No merge, live deployment, CMS writes, navigation changes or paid service.
