# Apollo Experience 2.0 — R321 print custody and extreme-text acceptance

**STAGING ONLY · DRAFT · NOT LIVE · HARD HOLD**. Stacked on R320 PR #2260, under Issue #150 and #818/#820. Homepage PR #49 and independent Research Desk PR #158 untouched. No WordPress, social, commerce, analytics or paid-service writes.

## Proven printed-document defect and narrow fix

Actual R320 Chromium PDF displayed a closed "Inspect the source and custody record" disclosure immediately above the fully printed source text. This can mislead educators and researchers. Previous CSS SHA-256: 0c31dbffe1a78500c10f08806d76eb5399be93207eef1fed4c1bb6de7d8d17e9; exact negative control reproduced the behavior.

R321 fixes print-only CSS under feature-query support for details::details-content, so modern print engines remove the contradictory closed-state label and explicitly expose source details. Older print engines retain the summary as a fallback. New CSS SHA-256: 6572c271e1d12049775000427b3cc0fdcbdf71d4c83f163794aeb3bb3800f12f, pinned in the PHP style version. No historical text, NASA URLs, images, geography, scripts or CTA altered.

## Executable evidence

Checked-in gate: python experience2/apollo-r321/qa/print_custody_gate.py (PHP, Node, Chromium, Python playwright and pypdf).

Independent extended LOCAL gate executed:
- 42/42 offline Chromium contexts, widths 320/360/390/768/1024/1440/1920, JS/no-JS/CSS-off/forced-colors/200%- and 400%-text, reduced-motion and touch configurations; unique IDs, native source focus, chronology, no invented image/pin, and one free editorial CTA per Atlas.
- 2 actual Chromium-generated print PDFs with all source drawers closed before printing; pypdf verifies original NASA custody text, date reconciliation, media accession/caveats, official links, and disappearance of the false collapsed-state label.
- Negative controls: exact old CSS reproduces the defect; wrong NASA accession and broken source fragment are rejected.
- PHP lint and JS syntax run; Git blobs of PHP/CSS/JS pinned in the test. Extended gate executable files, screenshots, PDFs and integrity manifest in evidence ZIP.
- Offline fixture LCP and CLS observations are NOT production Core Web Vitals.

## Primary sources and rights (checked November 12, 2026)

NASA Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
Board proceedings: https://www.nasa.gov/history/Apollo204/proceed.html
Board narrative: https://www.nasa.gov/history/Apollo204/narr.html
Later NASA safety summary: https://sma.nasa.gov/sma-disciplines/accllp/apollo-1
Archived memorandum: https://www.nasa.gov/history/Apollo204/15.html
NASA image accessions (link-only): S67-15717, S66-58038, S67-21294, KSC-20170124-PH_KLS01_0090.
NASA advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

Official source links do not certify reuse of a photograph, publicity rights, or NASA endorsement. Apollo 1 ignition origin remains unproven in precise location; Board authority Jan 27 oral / Jan 28 convening / Jan 31 memorandum receipt / Feb 3 written confirmation must remain distinct.

## Conversion-first boundary and release

Future funnel: Grok Apollo documentary → NASA source Atlas → one free FV Apollo investigation → separately authorized payable history/education offer. Published asset ID, merchant checkout acceptance, rights-cleared product, verified human sessions, leads, settled orders, fees and refunds are not authenticated. Revenue/1,000 qualified human sessions: NOT COMPUTABLE. A source click/print is not a sale.

Release HARD HOLD: no installed WP/Assembler/CDN, native browser HTTP(S) blocked, genuine axe-core unavailable (npm DNS), independent NVDA/VoiceOver, cross-browser print, field CWV, hosted CI/QD, rights review or founder production approval. Grok owns video/distribution, Praxxis owns creator QA, Claude owns production/analytics, Apollo lane owns this isolated source/print QA.
