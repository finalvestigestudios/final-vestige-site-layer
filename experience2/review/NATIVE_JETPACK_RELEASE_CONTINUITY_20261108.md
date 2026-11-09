# EX2 — Native Jetpack / Focus / Margins release-continuity gate
**2026-11-08 · DRAFT · RELEASE HOLD · no CMS write**

## Read-only authenticated evidence
- WordPress site: production `256784396` (the only site listed under environment=all); theme **Assembler**.
- Published WordPress **Page 6** editor source modified **2026-11-05 12:07:24**, 150,710 characters returned by the WordPress connector.
- Editor source contains exactly **one** native `<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->` block, **72** `fv-margin-strip__item` records with indices 0–71, and the public Focus / Dispatch paths.
- The native block appears in a Dispatch section alongside an unsubscribe notice. Existing 52-page Focus Fieldbook is a distinct offer; do not replace it or claim a receipt is a signup.
- Actual protected private Playground bundle contains a **local** home-page shortcode `[fv_ex2_playground]` and a deliberately nonfunctional `/fv-ex2-focus-review/`. That is correct for preview isolation, but **it is not a production editor-block replacement**. Its rendered evidence room does **not** prove that the native Jetpack block would survive any future Page 6 change.

## New release contract
This standalone verifier compares an authorized read-only RAW WordPress Page 6 editor-content export with a proposed, separate Page 6 editor block document. It fails closed if:
1. the native Jetpack subscriptions block is lost, duplicated, or has its serialized Gutenberg options modified;
2. the existing 72 public Margins records change in text or order, or the rotator container changes count;
3. Focus Fieldbook and Dispatch/unsubscribe pathways disappear; or
4. review-only shortcode/Focus route/activation markers leak into a possible release page.

It hashes both input editor documents for custody; **do not commit user emails, visitor information, credentials or database exports**. Use only public WordPress editor content. A positive source verdict is **not** proof of actual WordPress parse_blocks, Jetpack rendering, a confirmed subscriber, email delivery, accessibility or sales.

## Reproduce safely
```bash
python -m unittest -v experience2/review/test_native_signup_continuity.py
python experience2/review/verify_native_signup_continuity.py \
  --baseline /secure/public-page6-editor-content.html \
  --candidate /secure/proposed-page6-editor-content.html \
  --out /secure/release-source-continuity.json
```
Expected: **0** exit code only for intact public editor-block structure; **2** for release HOLD. Never substitute rendered private preview HTML for the proposed editor document. Do **not** publish a Page 6 candidate merely because this static gate passes.

## Measured local evidence and important constraints
A local Python regression implementation passed **12/12 synthetic positive/negative scenarios**. It used synthetic examples, **not WordPress Core** or real Jetpack. The present private Playground's standalone shortcode document is intentionally **not source-continuous with the published Page 6**; it must not be confused with a release-ready replacement. Authenticated source review was read-only. Pending actual independent checkout/CI review, this gate is REVIEW-ONLY.

## Critical additional release gates
- Free isolated WordPress Playground with actual pinned Assembler, working theme, and the source-controlled seven-chapter shortcodes; no production writes, no subscriber database.
- Separate **proposed final Page 6 Gutenberg block assembly** that keeps the native Jetpack block and 72 Margins in-place, tested with WordPress `parse_blocks` and front-end rendering before ANY release approval.
- Exact-head Chromium keyboard/touch/reduced-motion/no-JS/200% zoom; genuine axe-core, Lighthouse/CWV; archival image HTTP body bytes and source-rights reconciliation.
- On the *existing production host*, after founder approval, test real Jetpack form rendering, independent subscription confirmation and download delivery without fabricating successful signups. Do not initiate test subscriptions without explicit consent.
- CI and independent QD PASS on exact commit; no unapproved merge, deployment, theme/navigation changes, affiliate activation or subscriptions.

## Conversion-first decision record
**OFFER:** Free 52-page Seven Day Focus Fieldbook, editorial bridge from archives.
**FUNNEL STEP:** Historical evidence → native Dispatch/Focus capture.
**BLOCKER:** Preview-only shortcode output cannot certify preservation of the *existing native Jetpack block* on eventual Page 6 release.
**CHANGE:** Exact-block, exact-record and route source-continuity preflight on an isolated draft.
**EVIDENCE:** 1 native subscription block and 72 public records observed in authenticated Page 6; 12 synthetic local regression controls.
**OWNER:** Interim homepage engineering source gate; Claude owns Jetpack/runtime/attribution; Grok and Praxxis own social acquisition.
**BUSINESS OUTCOME:** Zero verified incremental confirmed leads, paid orders, affiliate commissions or realized net revenue from this change.

Related: Issue #150, #820, #818; separate Apollo #158, frozen PR #49; stacks above #1652. Release **HOLD**.
