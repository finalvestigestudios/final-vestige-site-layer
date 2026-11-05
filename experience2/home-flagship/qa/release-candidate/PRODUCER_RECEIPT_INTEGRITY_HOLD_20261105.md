# EX2 current-head producer-receipt contract hardening — 2026-11-05

**DRAFT / RELEASE HOLD.** Stack on PR #1108 exact base `8da44d367084acbb1d76e5e98c53ffa19ec6120a`. Frozen PR #49 and live WordPress remain untouched. This changes **the already-existing release-evidence join**, not homepage design, Jetpack behavior, navigation, analytics, or deployment.

## Reproduced false admission before the fix

The prior pure join accepted an input pack with `{checks:{made_up:true}}` at **every** WordPress viewport, a lone arbitrary true value for the no-JS evidence, `image_http_delivery:{status:'PASS'}` with **zero image response-body receipts**, and a fabricated `{checks:{made_up:true}}` at every guest width. The other input fields had the right labels and values, but the decisive viewport checks had never actually run.

Native Node reproduction against **the exact original Git blob** `68b2a8320a11b66d7c5b3f2813698f144b22c249` returned `lab_evidence_satisfied:true`, classification `LOCAL_WORDPRESS_AND_GUEST_LAB_EVIDENCE_COMPLETE_NOT_RELEASE`; `release` was still HOLD. The weakness could misleadingly imply real browser and image transfer evidence was complete.

## Implemented, source-grounded admission

The updated join requires named checks **actually emitted by** `verify_exact_staging.py` (five real WordPress widths, CSP, chapters, images, Franklin folio, NYPL not reproduced, axe), its no-JavaScript browser branch, and `focus_guest_gate.py` (four guest widths, accessible email/submit and no self-link substitution).

The archival image receipt must contain **both** labeled Apollo and Franklin images with observed HTTP 200, a raster type, SHA-256 image-body hash, bounded positive decoded payload bytes, nonduplicated hashes, no failure codes, and consistent total decoded bytes. **Decoded body bytes are not exact network-wire bytes**; the underlying `media_transfer_admission.py` enforces actual response magic/MIME as a separate gate. No NYPL historical photo is added; capture-specific rights remain on HOLD.

**Crucially, these checks consume existing producer fields.** They do not add a third analytics tool, new scripts, a paid service, another chapter, or a competing campaign tracker.

## Verified local native execution

- Node v22 local runtime, original committed source blobs: `68b2a8320a11b66d7c5b3f2813698f144b22c249` and `17a26ab8c764241ab38a188264f89219d4b5fea8`, **28/28 native tests PASS**. This closes the earlier V8-only execution gap in #1108.
- Modified contract blob `9ba0bd173c9369ebf623f5449f736f657e0ad760`; modified tests blob `88872d88579a3fdae2fec35c4c529e92c224a5ed`. **36/36 native tests PASS**, adding eight adversarial cases.
- Same forged receipt used for before/after testing: before **incorrectly accepts**; after **rejects** with explicit failure codes for each stage width, image transfer, no-JS and Focus guest evidence.
- Running the pure source contract and tests is NOT running an actual current WordPress Playground, publicly hosted browser, live /focus/ form, axe against the site, Lighthouse, mobile Safari, or manual WCAG 2.2 AA audit. No live signup submission or merchant order was attempted.

## Current execution blockers and safe next path

The runtime has Node, Python Playwright, Chromium and PHP. But direct external network resolution is blocked, there is no installed WP Playground CLI/WordPress core, and no independently authenticated official Assembler theme ZIP or separate axe-core JS. The WordPress.com account still lists **only production site 256784396**, on Personal; the alternate wpcomstaging.com address is not a second staging clone.

Therefore actual seven-chapter isolated WP/Assembler staging remains **NOT RUN**; do not carry forward PR #637's earlier successful measurements to this head. On a properly provisioned isolated developer machine, execute the existing `run_local_staging_admission.py` and current-source `verify_exact_staging.py`, guest read-only browser, Lighthouse and usability paths, then let this hardened join check the resulting receipts. Keep the production CMS untouched.

## Conversion-first experiment disposition

**Offer:** Free 52-page Focus Fieldbook. **Funnel:** seven-chapter evidence experience → honest /focus/ CTA → actual anonymous opt-in → confirmed email lead (if independently observable) → verifiable merchant order. **Blocker:** receipt join could accept made-up success labels rather than genuine conversion-path and archive-media checks. **Change:** hardened producer-shaped contract. **Evidence:** true native Node 28/28 baseline and 36/36 corrected tests; falsified media/guest data now rejected. **Owner:** homepage engineering; Claude owns attribution/Jetpack production work, Grok/Praxxis own acquisition. **Paid sales / net revenue:** NOT MEASURED, not implied.

**No production merge, deployment, CMS write, subscriber action, image-rights clearance or revenue claim. Release: HOLD.**
