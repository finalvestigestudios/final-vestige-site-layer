# Apollo Evidence Atlas R56 — visible NASA custody and rights uncertainty (STAGING HOLD)

**Scope:** `experience2/evidence-atlas/` only. Parent: R55 `0307e64dac54ee3a94c6015d4257ed830008c2e1`. All homepage branches, frozen PR #49, original Research Desk PR #158, live WordPress and site settings untouched. **Not approved for installation, merge or publication.**

## Visitor-facing improvement

The six NASA photographic references now carry a genuinely useful **readable source-custody disclosure** in each native `<details>` SourceDrawer: identifier-verification status, credit displayed by NASA (or explicitly absent from reviewed metadata), producing-center field (not treated as a credit), NASA page revision date, the 2026-11-01 editorial metadata-check date, and explicit outstanding rights/human-verification notices. A static section before the gallery states the material distinction: **five** linked NASA pages display the associated PIA/catalog reference, **one** (`S67-19766`) does not, and **zero** photographs have individual use approval or are embedded. All disclosures remain legible with JavaScript off, in print, on keyboard, and under filtering.

The source of this additional display is the pre-existing six-record `sources/NASA_PAGE_RIGHTS_AUDIT_R55.json` (SHA-256 `a3c87196da3c48490a84e6a5b1ad7f3e6a21f4d908ebccded7ab8517597f25c9`). `build_atlas.validate_rights_audit` rejects any byte drift and any source-ID, URL, catalog, release-status, human-review, likeness-review or catalog-confirmation mutation. It matches the unchanged R37 custody blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`. This protects accidental editorial regression; it is not a cryptographic trust boundary against a malicious maintainer.

Runtime distribution version `0.0.56-staging` uses a new exact WordPress template SHA-256 `5d76b85ab62feb0c9a3a5733cd0718d8f0f4fe8f820edb1d61f57e499d0fdb73`; the adapter verifies the reviewed Atlas PHP Git blob `f7b41a7aafb92208afce661b9f6f1c7171f4e13b`, CSS blob `ad64e7967f84856672fd8a229a61370d7a865227`, and unchanged JS blob `23212093d354917e403a5a9dbd9dca6b0eb8ca28`. Both original PR #158 and full R38 Research Desk profiles remain independently pinned. No code was modified under `experience2/research-desk/`.

## Actual executed local tests, November 1, 2026

- `python -I -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q`: **96 run, 95 passed, 1 skipped**. The skip is the full-R38-on-local-filesystem test (the source archive includes only the R38 custody JSON). Four new R56 unit tests verify metadata, a byte-mutated audit build refusal, six accessible drawers, and the WordPress fragment. Existing tests' exact versions/hashes updated intentionally.
- `python -I experience2/evidence-atlas/test_atlas.py`: **11/11 passed**.
- `python experience2/evidence-atlas/build_wordpress_stage.py --output staging-r56`: success; staged template contains six records and no NASA image binaries or geographic pins.
- `python -I experience2/evidence-atlas/tests/browser_r56_custody_ui.py --output qa-r56`: **16/16 real-source Chromium cases passed** (320/360/390/428/768/1024/1440/1920 pixels, JS enabled and disabled, reduced motion, touch at narrow widths, keyboard-operated SourceDrawer, print with all six drawers, filtering/revealing records, zero unexpected requests, zero horizontal overflow). Screenshots at 390 and 1440 reproduced byte-for-byte on repeated capture within each run.
- Previously source-controlled R55 deep acceptance **16/16**, R54 source-built Atlas acceptance **16/16** re-ran against the updated code and passed.
- PHP lint of the Atlas plugin and integration adapter, `node --check atlas.js`: passed.
- In this local fragment test only, LCP observer readings ranged **88–112 milliseconds** and CLS was **0** across JavaScript-enabled widths. These are **not hosted Core Web Vitals**, nor Lighthouse p75 performance numbers.

**QA artifact hashes:** `qa-r56/r56-custody-390.png` SHA-256 `011f1504ef43957f5f76cda825083aa1e3ee886c2b7c7651632ddfe1d8580ae4`; `qa-r56/r56-custody-1440.png` SHA-256 `8c3ed38335d979bb9644a1f9612925735ccde9a445bc78c7745bde0cab58f402`; browser receipt SHA-256 `02f05ac1b142362f5e6a4324534b18dea1066c039353c40706fc47b4278b718b`.

## Remaining hard blockers

1. **Photographic reuse:** zero of six photographs independently assessed/cleared. Review NASA/third-party credits, depicted people, endorsement and exact proposed context. Never conflate metadata verification with a license. `S67-19766` photograph association remains provisional. https://www.nasa.gov/image-detail/apollo-1-crew-honored/ ; https://www.nasa.gov/nasa-brand-center/ .
2. **Actual R38 acceptance:** five exact R38 source files exist in the repository but were not present in this local isolated archive. Run `tests/browser_r53_actual_r38.py` against a *full checkout*; no synthetic fixture substitution. Real Research Desk co-host **not certified**.
3. **Genuine private WordPress.com Atomic / Assembler installation:** not attempted. Nested reusable-block prehead CSS, shortcode initialization order, actual links, keyboard focus and browser network loading remain unverified. No WordPress content/settings writes are authorized.
4. **Verified axe-core, assistive technologies, independent QD, hosted LCP/CLS/INP, and green CI on the exact reviewed SHA:** pending or unavailable. Do not use local `page.set_content` data as WordPress proof.

**Release decision: HOLD.** Do not merge, deploy or embed unreviewed NASA photographs. No speculative geographical edges or map pins. Next engineering action should be full-original-R38 co-hosted acceptance, verified axe-core, then a founder-authorized **private** WordPress/Assembler test with independent QA before any release decision.
