# Apollo R52 — two exact Research Desk profiles (STAGING / RELEASE HOLD)

## Confirmed integration defect

R50/R51 checks only the original PR #158 Research Desk pilot's four Git blob IDs, but the actual R51 ancestry carries the later R38 Research Desk. Those R38 PHP, HTML, CSS and JS blobs are different. The R51 suite would therefore show its fallback even with both components present. This was a real release-integration incompatibility, not a missing-feature request.

I independently read both versions' actual GitHub files on 2026-11-01:

| Research Desk file | PR #158 original blob | R38 in R51 ancestry blob |
|---|---|---|
| final-vestige-ex2-research-desk.php | d1879a90101b5475990132369178f42743f4b57c | 44a43c63ba262de4193295563f5762df6e731077 |
| templates/ledger.html | 403d128c57b9bc82dac7c619651689070edef86c | 4842afb84b4c993cfc4861ce7f5a7a4d7b451871 |
| assets/source-ledger.css | b8cf00afeceba115a9e9d19044fc11dcf2890cbe | 7b0972fc3a920ded08f9783fddcfc9c609c7ff06 |
| assets/source-ledger.js | 32e757cc4dc8708397ff65ac21e89dd319781d78 | 57f4a639d4c37fc4355b10fe7dec085bf87c6eb7 |
| sources/R37_PHOTO_CUSTODY_CROSSWALK.json | not in original pilot | ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea |

These are Git blob SHA-1 IDs, not hashes of bare file bytes.

## R52 correction

Only two **whole, immutable, mutually exclusive** profiles may be admitted: PR #158 original (four exact files) or R38 custody/search (four source files plus the exact R37 crosswalk). A missing file, mutation, mixed profile, unrecognized plugin or unsafe relative path fails closed to the existing Apollo article. The adapter is now 0.0.52-staging. No Research Desk or homepage source was changed.

## Verification executed

- PHP lint on adapter and CLI test probe PASS.
- Python component/regression suite: 79 tests run, 79 OK, one explicit skip because the local distributable R51 ZIP contains Atlas code and the R37 crosswalk but not the complete R38 Research Desk directory. The new tests exercise full-profile verification, missing/tampered files, mixed versions and path escape rejection. In a full GitHub checkout the R38 whole-profile test runs rather than skips.
- Original Atlas tests: 11/11 PASS. Node JavaScript syntax check PASS.
- Existing R50 PHP-assembled Chromium browser regression rerun: 16/16 PASS across 320, 360, 390, 428, 768, 1024, 1440, 1920px, JS on/off and touch/reduced-motion emulation. The browser uses synthetic Desk markup and original pilot JS; it does not exercise actual R38 markup or installed WordPress. Real full-page QA screenshots captured at 390 and 1440px. No unexpected request, console page error, or horizontal overflow observed.
- Browser set_content LCP/CLS observations are **component-only lab measurements**, not hosted or field Web Vitals. No axe-core was executed this sprint.
- Actual R38 GitHub blob IDs were independently checked against the adapter pins; full five-file **runtime** admission in WordPress has not been tested.

## Required release gates

1. Run the complete R38 source admission test in an actual full repository checkout.
2. Install exact Desk, Atlas and suite adapter in isolated WordPress/Assembler staging and confirm real asset enqueue, top-level/reusable/template-part shortcode rendering, no FOUC, duplication and keyboard focus.
3. Execute genuine axe-core, assistive technology/Safari checks, hosted Lighthouse metrics, independent QD and hosted CI on the frozen release candidate.
4. Obtain individual image-use reviews for all six NASA photographs and resolve the record 01 unconfirmed S67-19766 catalog association. No photo bytes or map pins were added.
5. Obtain founder approval before any merge, WordPress content/settings update, activation or deployment.

**STAGING ONLY — DRAFT PR — PRODUCTION HOLD.** Homepage PR #49, Claude's homepage lane, original Research Desk PR #158, all WordPress production pages/settings and Apollo source crosswalk remain untouched.
