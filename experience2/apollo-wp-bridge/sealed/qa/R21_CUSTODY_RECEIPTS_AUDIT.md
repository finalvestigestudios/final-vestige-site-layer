# Apollo Experience 2.0 — R21 Evidence Export Custody Receipts

**2026-10-31**, draft-only, separate from homepage PR #49 and Research Desk PR #158. R20 parent `c784423205075ae0d5f31138dff93214ebcb8939` (draft PR #306). NASA source-custody pin `74375657f2cdaac0710f94c6de6c24534ee06858` remains unchanged. **DO NOT MERGE OR DEPLOY.**

## Implemented
- Editor-only **Evidence Export Custody Shelf** within the NASA Apollo 1 private staging experience, positioned next to Source Concordance and the NASA media-rights desk.
- Seven exports each have filename, exact byte count, SHA-256 digest and individually nonce-gated link; no JS required. Links are under existing editor-only Ajax allowlist. Digests describe comparison to this build, **not digital signatures or independent NASA attestation**.
- A tampered, missing, reordered or oversized export fails the deterministic source build. PHP verifies each packed asset, structure, seven required placeholders, and safe substitution prior to output; source integrity response header is provided for read-only audit.
- Separate read-only staging admission checks SHA-256 HTTP header, exact seven HTML records, file+digest correspondence and same-origin/nonce integrity of each link. Mutation tests demonstrate rejection of swapped names, spoofed download attributes, missing headers, tampered bytes and improper access.
- No NASA photos embedded, no geography inferred, no cacheable unauthorized exports, no WP settings/content changes or paid services. Original 1966/1967/2017 source-era distinctions and catalog-label discrepancy stay visible.

## Executed locally
- Python/PHP simulated WordPress + real loopback **HTTP transport**: **121/121** unit, hostile-transport and admission tests (10 additional vs R20's 111).
- Chromium/Playwright dedicated custody shelf: **7/7 widths** at 320, 360, 390, 768, 1024, 1440, 1920; 7 accessible named downloads, no external resource requests, keyboard focus, touch target >=44px, reduced-motion, no-JavaScript and 390px nested WordPress-style container; screenshots 390/1440.
- Main exact Chromium casefile suite: **7/7 widths** passed earlier in sprint following R21 integration. Re-run at end of sprint was interrupted by runner timeout; not counted as second successful execution.
- R20 rights desk, R19 Atlas, R18 source crosswalk and R17 dual-witness independent Chromium scripts each passed 7 widths during R21 run. R16 full AX script exceeded timeout; not a fresh pass.
- `php -l` PASS, deterministic plugin ZIP SHA-256 `e52ef2bd218a1f514b39cd0be5cd493b59af32ba62de6980518725f5b8a622ef` (twice identical), bundled plugin PHP SHA-256 `9fd16df918f503f80a76f7ad88d130902f48de0c821123435033cefa5bc71c81`.
- Strict axe-core: no authenticated bundle, **NOT RUN**. The mandatory `--require-axe` release gate remains fail closed.
- Native browser HTTP navigation at 127.0.0.1 blocked by administrator (`ERR_BLOCKED_BY_ADMINISTRATOR`); real CSP enforcement, cookie sandbox semantics and installed WP lifecycle are **NOT claimed**. Curl/urllib actual PHP HTTP is tested separately through synthetic WordPress router. No hosted p75 LCP/CLS/INP, Safari/VoiceOver/NVDA or independent QD review.

## Repeat
```
python -m unittest discover -s qa -p 'test_*.py' -q
python qa/browser_exact.py
python qa/browser_custody_receipts_r21.py
python qa/browser_media_rights_r20.py
python qa/browser_atlas_admission_r19.py
python qa/browser_crosswalk_r18.py
python qa/browser_dual_witness_r17.py
python qa/browser_exact.py --require-axe # expected HOLD until verified axe bundle
python build_sealed.py --out /tmp/review-a.zip
python build_sealed.py --out /tmp/review-b.zip
sha256sum /tmp/review-{a,b}.zip
php -l fv-ex2-apollo-sealed-template.php
```

## Separate release admission / outstanding requirements
Installed isolated WordPress staging under actual current Assembler/Jetpack, browser-enforced HTTP/CSP and sandbox, independently verified axe-core WCAG A/AA, Safari/VoiceOver/NVDA, live field CWV, individual NASA third-party/likeness/branding checks, first-party adjudication of `NASA S67-19766`, QD review, successful hosted CI on exact SHA and founder approval. The NASA general informational-use policy is **not per-photo approval**; see https://www.nasa.gov/nasa-brand-center/images-and-media/ . Homepage PR #49 and Research Desk PR #158 remain untouched.
