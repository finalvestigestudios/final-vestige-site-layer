# Apollo R107 — Staging-only artifact integrity and safe browser progress

**Status: STAGING HOLD.** This is a QA hardening sprint on top of Apollo R106 (#878), not publication approval. Original Research Desk PR #158 and frozen homepage PR #49 are untouched. No production/CMS/WordPress write.

## Reviewed source and defect

Read Issue #150 and PR #158 plus the actual R106 `qa_receipt_r105.py`, `test_qa_receipt_r105.py`, genuine disposable WordPress browser runner and GitHub workflow. R106 checked only the eight-byte PNG signature and five-byte PDF signature before accepting valid SHA-256 hashes. This allowed arbitrary files with matching hashes but no valid image, no screenshot dimensions or pixel data, and no complete PDF print to be certified. Progress receipts also wrote arbitrary `performance_lab_samples` fields without type/URL/token scrubbing before completion gate.

## R107 source-controlled changes

- New `tests/qa_artifacts_r107.py`: bounded standard-library PNG parser with magic/IHDR, actual 320/390/1440 viewport dimensions, height >= 900, 8-bit RGB/RGBA, width*height pixel budget, chunk order and CRCs, bounded zlib decoding, exact per-scanline pixel count and terminal IEND. Print-PDF validation checks version, bounded size, terminal `startxref` and `%%EOF`. These are **structural checks, not proof of correct page content or legal rights**.
- New `tests/test_qa_artifacts_r107.py`: thirteen hostile format/progress cases; synthetic real PNG/PDF bytes rather than misleading header-only fixtures.
- `tests/qa_receipt_r105.py`: receipt finalization now verifies file digest then actual PNG/PDF structure, with no relaxation of R106 browser matrix, selected-state axe scans, six LCP/CLS trials, LCP<=2,500ms or CLS<=0.1. Intermediate progress accepts only finite bounded numeric samples and replaces strings, NaN, Infinity, booleans or malformed entries with null; it never copies arbitrary Playwright exception text.
- `tests/test_qa_receipt_r105.py`: legacy fixture updated to genuine generated media to preserve all existing 27 tests and exercise new parser.
- Genuine disposable WordPress workflow includes both R107 paths in PR trigger, compiles parser and invokes new tests before building the WordPress test suite.

## Validation and limits

Local equivalent source: **40/40 Python unittest cases passed** (27 inherited + 13 new); Python compile passed. The structural validator separately passed actual historical R102 isolated-WordPress Chromium artifacts: source comparison PNG 390 x 7789, source comparison PNG 1440 x 3426, gallery-print PDF 54,736 bytes. These are **prior R102 evidence**, not screenshots or LCP from an R107 exact-head run. Reproducible local test log and source-file hashes are packaged outside the repo.

Exact-head GitHub Actions / actual R107 WordPress + Assembler interaction, axe, LCP and CLS tests must run and pass; recent R104–R106 Actions jobs failed **before runner steps**. If the platform remains blocked, classify these tests **NOT EXECUTED**. Do not mark CI green from hermetic tests.

## Immutable boundaries and remaining release blockers

NASA individual photograph-use review remains **0/6**; no images embedded. Proposed `S67-19766` crew-portrait attribution provisional. Curated Atlas has zero invented coordinates/pins or inferred relationship edges. Hosted WordPress.com/Assembler acceptance, manual VoiceOver/NVDA, real-device touch/zoom and contrast, independent historical and rights/editorial review, reproducible repeat-run field-like performance and founder approval remain required.

R107 does not alter evidence claims, site content, WordPress settings, original PR #158, homepage PR #49, homepage art branches, or paid-service configuration. **No merge, install, deployment or publication authorized.**
