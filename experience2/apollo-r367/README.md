# Apollo Experience 2.0 / R367 — sealed chronology custody (draft)

Scope: Issue #150. Conversion source of truth: Issue #820. Base: R366 Draft PR #2512. Never modify frozen homepage PR #49, or separate Research Desk PR #158. **Do not install, merge or deploy.**

## Fix

R365 guards individually reviewed Apollo 1 claims but its low-level renderer can be passed an entire out-of-order, duplicated or incomplete sequence. R367 adds an opt-in shortcode: [fv_apollo_chronology_r367].

The new wrapper validates the exact order, four reviewed identities, all source/claim fields and an independently pinned SHA-256 of the original R365 canonical sequence: 522ffa8829d6292b90e2ad115f26412d5ec92ef19423d0f2ab125775c08cf5f3.

Changes to a record, date, publication class, source link, or sequence order withhold the **whole timeline and all NASA source citations**. A readable fallback retains a single link to the existing free Apollo investigation. This is an internal content-integrity guard, not a digital signature or a NASA certification. R365 still needs to be loaded separately; this wrapper does not register assets or alter WordPress settings.

## Reproduction

From the checkout root:

    php -l experience2/apollo-r367/sealed-chronology.php
    php -l experience2/apollo-r367/qa/contract.php
    php experience2/apollo-r367/qa/contract.php
    python experience2/apollo-r367/qa/browser_gate.py
    python experience2/apollo-r367/qa/build_evidence.py

QA is PHP local-stub plus Playwright Chromium local set_content, not an HTTP/WordPress install. The browser harness checks eight desktop/mobile/no-JS/touch/keyboard/forced-colors/reduced-motion/zoom and altered-record scenarios; prints a NASA-link dossier and collects synthetic local LCP/CLS (not production CWV). The zip freezes screenshots/PDF and source manifests, and is reproducible byte-for-byte for identical source/artifacts. Regenerating browser measurements or print metadata can change the zip.

The 320px/4x-root-font stress is intentionally harsher than normal browser 400% zoom and exhibits extremely narrow text columns; no claim of WCAG 2.2 AA acceptance is made.

## NASA and rights

- Original Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- Post-fire tests (Feb 14, 2018 NASA retrospective): https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
- Mixed-gas decision (Mar 9, 2018 NASA retrospective): https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/

The original 1967 Board did not conclusively identify one exact ignition source. The later 102 test ignitions were post-fire engineering tests. NASA photographs, protected identifiers, endorsements and commercial media reuse are not cleared by this component. No geo pins, inferred relationships, scripts, checkout, paid claims, email or tracking were introduced.

## Conversion and governance

One proposed route only: Grok's Apollo documentary (published asset_id unverified) to NASA chronology to the existing free investigation to an educator product only after founder and merchant verify rights, checkout and fulfillment. Do not imply that CTA clicks or subscribers are paid sales. Claude owns site and analytics; Praxxis owns independent creator review; Grok owns content and distribution; founder/QD retains release approval.

**Release HARD HOLD:** actual installed WordPress/Assembler, real browser HTTP/CSP (local navigation blocked by administrator), genuine axe-core, screen readers, Firefox/WebKit, exact-head hosted CI, permissions, verified relevant SKU, confirmed paid order reporting and founder/QD signoff. Read-only production plugin inventory on November 14 confirmed Assembler active and no installed Apollo/Research Desk plugin by name, not a staging acceptance.

No WordPress or production writes, social posts, email, analytics setup, merchant activation, spending, merge or deployment.
