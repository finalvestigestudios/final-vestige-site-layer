# Apollo R75 — Authentic WordPress PDF pagination review (STAGING_HOLD)

Tracks #150. This work is deliberately stacked on draft R74 PR #670 and is
independent of homepage PR #49, homepage engineering, and Research Desk PR #158.

## Reproduced print defect

Exact-head genuine WordPress/Assembler R74 Chromium PDF from GitHub Actions
run 41514082792, original SHA-256
`a586ad36b78e1d429db6b6f5ba53d536b8cea687c7453c1a31318b62225ab61a`,
contains 21 pages. Page 21 is a nearly blank **decorative-only** terminal
sheet: no text, annotations, images or dark pixels when grayscale rasterized
at 0.6pt scale; light-gray ink fraction 0.029644. This is a layout defect,
not a source-record loss.

## R75 implementation

`tests/wp_pdf_pagination_r75.py` checks the actual Chromium PDF using
both pypdf document custody and PyMuPDF visual/pagination inspection. It
refuses to delete content-bearing text, images, links, annotations, dark
illustrations or interior empty sheets. A maximum of three demonstrably
decorative terminal pages can be removed **from an OFFLINE REVIEW COPY ONLY**.

Both original and normalized PDFs are independently checked against the R74
source-custody requirement: all six unique NASA catalog IDs and original
source URLs, six source identity/revision statements, and every reuse
limitation. The exact extracted text of every retained page must match
before and after serialization. Output is deterministic
(`no_new_id=True`) and recorded in `R75_PAGINATION_RECEIPT.json`.

The original file `R74_AUTHENTIC_WP_PRINT_1440.pdf` is **always retained**
in the genuine WordPress QA artifact; the normalized companion is
`R75_SOURCE_SAFE_PRINT_REVIEW.pdf`. The R75 helper executes only when
the existing R74 1440px **genuine local WordPress, JavaScript-disabled**
PDF-source gate has already passed. The two modes are never conflated.

Local replay against the independently verified R74 CI artifact produced
a 20-page reviewed copy, SHA-256
`8c2d8deb708c00c72711a238691a934a6108473b0be69780088ad86903d8954d`,
and **five passing unit tests** including a dark textless diagram,
a source-link annotation, and deterministic repeated conversion.

## What this does NOT establish

This change does **not fix the underlying WordPress/Assembler browser-print
CSS**. Visitors using the browser print dialog can still receive an extra
page until that separate layout defect is corrected and retested on a
representative hosted site. It is not a publication-ready PDF or a user
download feature. Hosted WordPress.com parity, NVDA/VoiceOver and physical
devices, field p75 LCP/CLS/INP, independent review and founder signoff remain
outstanding.

All six individual NASA photograph-use assessments are PENDING;
`S67-19766` catalog-to-photo mapping is provisional. No photograph
binary, geographic pin, invented relationship edge, WordPress production
write, deployment, or paid service is introduced. **RELEASE: HOLD.**
