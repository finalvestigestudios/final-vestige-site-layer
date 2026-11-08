# Experience 2.0 — truthful Dispatch consent beside the LIVE homepage form (review only)

**Evidence read:** 2026-11-08 UTC. **Production remains untouched.** WordPress.com Personal offers no separate native staging clone. Preview on a disposable Playground/isolated Assembler clone, with public-only content; do not migrate the production database.

## Confirmed source condition

Authenticated `context=edit` reads:
- Published WordPress **Page 6** (modified `2026-11-05T12:07:24`, 150710 source characters; previously recorded SHA-256 `685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b`) contains one **Jetpack Subscribe block**, 7 historical chapter IDs, 72 Margins spans and 4 `<img>` elements. Its near-form heading currently says **"One email a week from Final Vestige."**
- Published **Focus Page 1579** (modified `2026-11-05T17:44:02`) describes The Dispatch as sent **when new work is published**, with a possible affiliate-commission disclosure.
- Jetpack's official Newsletter documentation (updated 2026-11-04) says subscribers are emailed upon publishing eligible **new posts**, not on a guaranteed weekly schedule: https://jetpack.com/support/newsletter/
- **Consequent conversion/trust blocker:** Homepage subscription cadence promises a fixed weekly email even though the adjacent Focus consent copy and official delivery design describe a publication-dependent cadence. Homepage form's 10px auxiliary copy does not mention potential affiliate recommendations or link to privacy next to that form. No live subscriber conversion test was performed.

## Isolated four-target proposal — not a production patch

1. Heading: `One email a week from Final Vestige.` → `New investigations, delivered when we publish.`
2. Near-form copy: `Sent when we publish. Some emails may contain recommendations that earn us a commission. Unsubscribe anytime · About The Dispatch · Privacy Policy` (with existing link destinations and added existing /privacy-policy/).
3. Increase the **specific near-form disclosure** rendered inline font size from 10px to 14px, reducing the previous 750 weight to 400 and 0.1em tracking to normal so the disclosure reads as body copy rather than shouty microcopy; preserve color and spacing.
4. Update the paired WordPress paragraph block metadata from 10px/750/0.1em to 14px/400/normal, keeping source and block editor synchronized.

Historical hero, Franklin folio, Apollo 1, NYPL map, 7 chapter IDs, 72 Margins, Jetpack block, 52-page Focus offer, its landing route, scripts, styles, imagery and all other source bytes are unchanged by the proposed review. No direct merchant links, affiliate claim, popup, measurement script or tracking parameter is added.

## Executable source custody

`node experience2/review/dispatch_consent_review.cjs --self-test` should report 13 passing assertions (one positive and 12 rejected mutated fixtures). The script is pure read-only; it accepts two separately exported WordPress `context=edit` JSON files, with local paths only:

`node experience2/review/dispatch_consent_review.cjs ./page6.json ./focus1579.json`

Admission checks exact page IDs, status, timestamps, source length, recorded SHA-256 (Node), Focus cadence, existing gift script, one Jetpack block, 72 Margins, 7 chapter anchors and four unique source-replacement anchors; then proves all changes reverse byte-for-byte. It outputs a **description**, not a CMS update payload. Never commit private WP exports, user records or secrets.

**Executed during authoring:** 13/13 logic tests in isolated V8, 12/12 Python fixture regression tests in a separate local harness, authenticated read-only source presence checks of both published WP pages. GitHub blob was independently re-fetched byte-for-byte. The Node CLI's live exact-hash path has **not yet been exercised** with full source exports in Node and must not be represented as passing.

## Conversion measurement and release dependencies

**Offer:** existing 52-page Focus Fieldbook. **Funnel:** relevant historical reader → optional Focus CTA / Jetpack form → *confirmed* subscriber (not a scripted download notice) → independently confirmed paid order or merchant affiliate settlement → refunds/fees → net revenue per 1,000 qualified human sessions in 7/30-day cohorts. No measured leads, orders or revenue uplift from this review.

**Companion gates:** PR #1529 hero→Focus CTA; PR #1451 Focus gift-state correction (do not treat `?subscribe=` as proof of signup); PR #1536 cross-route admission. Owner for consent/Jetpack reality is the production engineer (Claude when available); Grok retains creative posting and asset IDs, Praxxis independently reconciles. Founder retains release and spending approval.

**Still HOLD:** native isolated WordPress/Assembler render with real Jetpack behavior, independent WCAG 2.2 AA/axe, keyboard/no-JS/touch/200% zoom, first-party archive image transfer bytes, NYPL exact-capture rights beyond the U.S. statement, real Lighthouse/CWV, QD/CI and founder signoff. WordPress Playground cannot qualify WordPress.com host-specific behavior.

**Asset provenance remains unchanged:** WP media #473 Apollo 1 NASA image (78346 metadata bytes), #474 Franklin 1869 reproduction (466043 metadata bytes), #1258 NYPL 1903 BRT map (5553669 metadata bytes). Metadata does not prove transfer. NYPL item https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0; NYPL's guidance for "no known U.S. copyright restrictions" does not certify other jurisdictions: https://qa-digitalcollections.nypl.org/about.

**Release decision: HOLD.** No WordPress updates, theme/nav/settings writes, merges, deployments, subscribers, email sends, affiliate activation or paid services.

## Post-commit small-screen typography refinement

An isolated **synthetic** Chromium study of the form-area excerpt showed the first 14px treatment with inherited 750 weight and 0.1em letter spacing was visually overpowering. The revised candidate uses 14px regular-weight body-style disclosure and normal tracking, preserving the paragraph's antique gold/dark palette context. A separate 16-state fixture sweep (320/390/768/1440px × 100/200% CSS zoom × before/after) observed zero root overflow. **These are fragment fixtures, not native WordPress/Jetpack or real CWV measurements; visual staging remains HOLD.**
