# EX2 flagship — archive image network admission (2026-11-08)

**State: REVIEW ONLY / RELEASE HOLD.** This complements #1573's keyboard/no-JS suite. It does **not** replace #252 CSP, #254 folio, #224 private renderer, or native WordPress testing. Frozen #49 remains unchanged.

## Exact verified source
- Parent: PR #1573, `868bd71ec47f547daceadda99d8d4dddcb9fcb4c`.
- Source: `experience2/review/verify_archival_network_bytes.py`.
- Protected renderer executed **in PHP with WordPress function stubs**, source SHA-256 `7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee`. Resulting HTML uses original 2 archival image elements, Focus route, 7 chapter links and 72 Margins records. No protected renderer or private data committed here.

## What was actually tested
Using real headless Chromium against PHP-rendered **offline** HTML, with deliberately **synthetic images** supplied by Playwright response interception:
- **10/10** positive cases: widths 320 / 390 / 768 / 1440 / 1920, JS on/off. The browser transferred nonempty fixture bytes, decoded images, checked dimensions, MIME+magic, response status, byte counts and SHA-256. Captured one 390px screenshot.
- **6/6** negative controls rejected: missing HTTP response, empty 200, HTML masquerading as an image, corrupt image bytes, 1×1 pixel, and foreign-host source.
- **Production-domain execution rejected** at argument admission (`--url https://finalvestige.com`, exit 2). No production site writes or privileged calls.
- Committed file was independently fetched from GitHub; Git blob SHA matched the local exact tested file.
- **NO actual WordPress/Assembler runtime; NO actual Final Vestige/NASA/Franklin image transfer; NO axe; NO Lighthouse; NO Jetpack-confirmed lead.** This is a test of the admission mechanism, not of the real archive assets.

## Reproduction (offline)
```sh
python experience2/review/verify_archival_network_bytes.py --fixture /private/path/php-rendered.html --out ./media_evidence
```
Dependencies: Python 3, Playwright for Python, Pillow, BeautifulSoup4, Chromium at `/usr/bin/chromium`. The HTML fixture must come from the pinned protected PHP review renderer. Do not commit that private review content.

## Staging admission (future, authorized only)
```sh
python experience2/review/verify_archival_network_bytes.py --url http://localhost:PORT/fv-ex2-review/ --out ./staging_media_evidence
```
Only localhost or **exact** `wpsandbox.wordpress.net` origin admitted. Confirm no production CMS writes and activate nothing without release approval. The tool inspects the actual browser image responses (including lazy/inactive cases by forcing image fetch), asserts bytes/content-type/header magic, image decoding and intrinsic dimensions, and outputs per-asset SHA-256. It does not certify image rights. Actual review must use an authorized disposable WordPress/Assembler instance, include explicit screenshot comparisons and measure network performance. Host-specific WordPress.com/Jetpack behavior remains unverified by Playground.

## Rights and release
- Apollo 1 file: `s67-19766.webp`; source label NASA. Source provenance does not constitute technical image-transfer evidence.
- Franklin file: `Franklinexpeditionnote.jpg`; identify as historical document reproduction and preserve original collection attribution and alt text.
- Published WordPress Page 6 still contains a fourth image element, including the **NYPL map derivative**, that is excluded from this two-image private review. Confirm original-to-derivative provenance and item-specific reuse rights separately before reconciling. Do not infer that live publication establishes clearance.
- The 52-page Focus Fieldbook, native Jetpack block, seven chapters and 72 Margins cannot be removed; no new affiliate URL or unverifiable benefits.
- Additional release gates: actual native WP/Assembler import; primary/fallback image bytes; independent axe and manual WCAG 2.2 AA; keyboard/no-JS/touch/real 200% zoom; Lighthouse + field CWV with sources and dates; Jetpack signup-success truth (#1451); independent CI/QD; founder's **explicit** production release approval. No merges or publishing.

## Conversion contract
**OFFER:** free 52-page Focus Fieldbook → **STEP:** mobile above-fold contextual CTA → **BLOCKER:** visually credible archival assets must load and build trust; actual source transfer remains unverified → **CHANGE:** fail-closed real-byte admission harness → **EVIDENCE:** 10 valid fixture flows, 6 deliberate failures, 0 real source transfers → **OWNER:** interim homepage engineer and Site QA; Claude retains Jetpack/checkout/attribution, Grok/Praxxis remain acquisition owners. Do not label clicks/submits paid revenue. Net revenue per 1,000 qualified human sessions: **not measured**.
