# EX2 Focus signup — semantic-fragment keyboard correction (2026-11-05)

**Status:** REVIEW-ONLY / NOT LIVE / RELEASE HOLD. Stacked on draft PR #1171 at exact parent `22eb4f57480408bda15d96ab27d01dbdfd91e148`. Frozen release PR #49 and canonical seven-chapter homepage are unchanged.

## Source-grounded issue

WordPress production Page **1579** (slug `focus`, last modified `2026-11-03T14:36:15`, read-only) has five `href="#subscribe-blog"` signup CTAs, one native `wp:jetpack/subscriptions` block and no literal static element with that ID. A JavaScript installer dynamically inserts a span. Draft #1171 proposed a static `aria-hidden="true"` span, solving scroll-only navigation but **not** putting keyboard focus or an accessible label at the destination.

Representative actual Chromium keyboard comparison at 320, 390 and 1440 CSS px (JavaScript on **and** off):
- **Old #1171 static span:** URL hash updates and page scrolls, but focus falls to `BODY`; the target's text is hidden from accessibility APIs (`aria-hidden="true"`).
- **This corrected candidate:** one `<h2 id="subscribe-blog" class="screen-reader-text" tabindex="-1" style="scroll-margin-top:5rem">Subscribe to receive the free Seven Day Focus Fieldbook</h2>` before the existing Jetpack Gutenberg block. Hash navigation focuses the meaningful heading and the next Tab reaches the representative email field. No overlay, popup, tracking script, vendor change or new product claim.

## Reviewable source and test receipts

- Existing bounded CJS read-only transformer `review/focus_1579_nojs_anchor_proposal.cjs` was **updated** rather than duplicated. Only the proposed HTML anchor markup and its self-test assertions changed. No WordPress mutation.
- Source transformer executed in V8 against the actual **31,683-character** Page 1579 editor content: one inserted 193-character native Gutenberg HTML block, **31,876** proposed characters, five original links, one new `id`, one untouched Jetpack block, original client-side installer preserved, original Fieldbook PDF reference preserved.
- CJS `--self-test` executed under native Node 22: **1 positive + 6 adversarial rejections PASS**. Original input, existing scripts and the unique subscription block otherwise byte-preserved.
- New `review/verify_focus_semantic_fragment.py` was executed with native Python Playwright/Chromium: **12/12 synthetic-fixture browser scenarios PASS** (320/390/1440; JS enabled/disabled; prior span vs semantic heading), including keyboard Enter, focus target, subsequent Tab to mock email field and no horizontal overflow. Chromium fixture is **NOT the live Focus page, WordPress block render, Jetpack subscription or screen-reader AT test**.
- Isolated read-only source audit of the full seven-chapter Playground candidate: 20 unique DOM IDs, 10 internal fragment links all resolve, 8 buttons all typed, 9 details+9 summary, and all exposed aria-labelledby/describedby/controls references resolved **in static source**. This is **not** a WCAG 2.2 AA verdict.
- Archival rights/provenance remain **unchanged**: Apollo S67-19766 image ID matching and Franklin binary matching require actual proofs; NYPL image remains excluded. No media, image bytes, or derived asset was copied into this PR.

## Conversion and release decision

**OFFER:** existing 52-page Seven Day Focus Fieldbook. **FUNNEL:** contextual homepage CTA → Focus landing → five signup links → subscribe → confirmed lead → independently verified paid order. **BLOCKER:** static fragment scroll-only proposal does not support meaningful keyboard focus and announcement. **CHANGE:** semantic, keyboard-focusable static heading instead of hidden span. **PASS EVIDENCE:** exact Page 1579 source transformation and 12 native browser *fixture* cases. **OWNER:** homepage engineering proposal; Claude/Jetpack and independent Site QA for actual guest path; Grok/Praxxis retain acquisition.

Not certified: real WordPress staging/Assembler seven-chapter render, actual anonymous Jetpack email flow/delivery, screen reader, Lighthouse/field CWV, 200% browser zoom, full axe, rights and image-transfer receipts, exact-head CI/QD, conversions or net revenue. WordPress.com Personal plan native clone remains unavailable; use free isolated Playground, not production. Earlier nonce/iframe admission harness does **not** certify the new shortcode-based import. All production writes, merge, publishing, analytics deployment, affiliate activation and spending remain prohibited absent exact founder release approval.

**Decision: HOLD.**