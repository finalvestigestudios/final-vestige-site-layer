# EX2 Assembler / rendered-script provenance — exact-head incident note (2026-11-03)

**HOLD. Synthetic, loopback-only WordPress Playground. No production WordPress changes.**

## Verified triggering run

- Stacked parent: PR #850 at `f567edc0dd41ee6fe2566e4b5988765d92279bbe`.
- Real hosted GitHub Actions run: https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41728776758, failed at 22:15 UTC in the actual Gutenberg/Assembler browser gate. Workflow startup, 11-source candidate assembly, safe Assembler archive preparation, and browser tooling all succeeded. Source tests and the other applicable workflows had succeeded.
- Exact logged browser assertion: `playground_assembler_render_gate.mjs:167:68`, `0 !== 4`. A **real saved 320px Chromium screenshot** was uploaded as artifact 13275887455, with screenshot-before-assert behavior working. Screenshot exists; no other widths, no axe, no media decode and no no-JS gate were reached on that run.
- The 320px screenshot also visibly exposes a separate theme-header link wrapping each letter ("Learn more") in a narrow column. It is not a certified accessibility diagnosis; test it under full Assembler browser QA and avoid conflating the theme header with the flagship root.

## Source-grounded root cause of *the failing assertion*

`write_source_flagship_playground_candidate.py` builds the single source-controlled seven-chapter body, which includes and closes its `[data-fv-home-flagship]` root, then **appends** the four `<script data-fv-source="...">` tags. They are sibling nodes, not root descendants. The failing assertion counted `root.querySelectorAll('script[data-fv-source]')` and expected four. A count of zero at that scope does **not** establish that Gutenberg stripped scripts or that the four scripts failed to execute. Their actual rendered presence still needs real-browser evidence.

## Exact corrective gate

- Enumerate `script[data-fv-source]` from the **document** in the real browser, not the flagship subtree.
- Assert the exact four in their canonical order: `flagship.js`, `observer-lab.js`, `chronicle-lens.js`, `reading-trail.js`. Missing, duplicate, reordered or substituted scripts FAIL CLOSED. Do not silently turn the check off or inject scripts through the browser.
- Emit only a safe script-name custody receipt before later layout/media/axe failures. Keep all saved CSS, geometry, 72 synthetic Margins, Jetpack fixture, seven chapters, real archival media, no-JS, image rights and accessibility gates intact.
- Add dependency-free regression tests that reproduce the sibling-vs-root mismatch, reject corrupt script inventories, and ensure the browser harness calls the document-level inventory rather than only the root.

## Required next evidence

A new **exact-head** GitHub Actions browser run must show the four document-level scripts and progress to saved-layout geometry, 1440px full-page and 320/390/768/1440/1920 screenshots, real media decoding/HTTP body receipts, full-document axe, no-JS 390, keyboard/touch/zoom checks and eventually measured Lighthouse. Every failure remains HOLD. Screenshot, script presence and JS execution are distinct: the four tags being present does not prove all four interactions work.

The historical NYPL Malbone capture is withheld pending capture-specific rights proof. The live page 6 has actual 72 Margins, Jetpack and Focus Fieldbook; this Playground candidate contains **synthetic** Margins/Jetpack. WordPress.com Personal has no native staging clone, and Playground does not certify WordPress.com Atomic/Jetpack parity, manual WCAG 2.2 AA or field CWV. Frozen PR #49, Apollo #158 and Mind #171 are out of scope.

**No merge, publication, theme/navigation/plugin changes, site data export, payment, QD approval or release approval.**

## Verified follow-up on exact head `1d2fdd9f9acd7322bad45fa5abd9dfd8655b8d57`

The actual hosted [Assembler run 41736296933](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41736296933) **failed**, but the corrected document-scope script check passed at all three widths it reached: **320, 390, 768**. Each emitted the exact canonical four script names. The serious **whole-document** axe finding remains at **768px**: rule `list`, selector `.wp-block-navigation__container` (in the default Assembler theme header, *outside* the flagship component). Both component and whole-document axe scans had no violations before 768px; at 768px component-only still had none, demonstrating why whole-document testing must remain mandatory. The CI uploaded three saved WordPress screenshots as [artifact 13279271420](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41736296933/artifacts/13279271420).

This establishes that **script tags were not stripped** in the tested local WordPress/Assembler rendered DOM; it does *not* establish that all four JS interactions work. The real navigation violation stopped the original loop before the remaining 1440/1920 images, no-JS and 1440px media proof. The follow-on code now **collects all five viewport attempts despite individual failures, then throws a combined fail-closed HOLD after no-JS**. This is diagnostic completeness, not an axe waiver or theme modification. Its newest exact-head run must still be inspected; results cannot be inferred from tests or prior branches.
