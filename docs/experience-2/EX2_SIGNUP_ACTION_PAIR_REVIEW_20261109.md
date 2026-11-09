# EX2 — complete first-screen Jetpack opt-in action (review only)

**9 November 2026 PT · homepage/Focus conversion integrity · P0 · no production writes**

Parent: draft PR #1709 at `31ad0ca7e7c8f775a0d09073d8b94186b5aa1abc`. Frozen PR #49 remains untouched. Reviewed live published Page 6 (modified 2026-11-05 12:07:24) and Page 1579 Focus (modified 2026-11-05 17:44:02) through read-only WordPress editor access. The published seven-chapter homepage has 72 Margins records and contextual Focus pathways; the Focus editor has its native `jetpack/subscriptions` block and 52-page download offer. No content has been edited.

## P0 defect in the prior acceptance harness, not yet proof of a live-site failure

The parent `verify_optin_viewport_geometry.py` checks **the email input only**. A perfectly visible and labelled field receives `labeled_unobstructed_first_viewport=1` even if its submit button is missing, disabled, covered, outside the first screen, or belongs to another form. This can produce an incorrect mobile-funnel acceptance result.

Reproduced those five variants in independent, real *offline Chromium* (390px; no forms filled or submitted). Each returned 1 under the existing field-only metric; each returns 0 under the new **same-form actionable pair** metric.

## Change

- Add a read-only browser probe: find only Jetpack email fields and associated submit buttons in the **same form**.
- Require both controls to be visible, accessible-name-equipped, enabled, keyboard-focusable, wholly inside the first viewport, unclipped, and unobstructed at a 3×3 sample grid.
- Embedded-frame fields remain unverified because parent iframe occlusion is not established.
- Do not read any form value, visitor identity, email or subscriber data. Do not click, submit, track or inject JS onto WordPress.
- Wire `verify_guest_optin_readonly.py` to record `signup_pair` and fail closed on Focus widths <=390px if no actionable pair is present. Retain the parent's existing input diagnostics.
- Keep homepage seven-chapter/72-record preservation checks and the independent Jetpack-confirmation/CI/QD gates.

## Evidence and limits

Locally executed against exact module blob `1f0ef5da0e2c411d37eff9277d1a9eeae81f66b6` and exact test blob `4015f2278f0efef52a8451fcdccb45a7af5ce0fc`, obtained from the committed branch. **39/39** offline Chromium scenarios passed: three healthy variants × six widths (320/360/390/768/1440/1920), and 21 negative controls. Negative controls include absent, wrong-type, obscured, offscreen, disabled, unnamed, inert, unrelated-form and inaccessible controls. Pre-existing field-only heuristic incorrectly admitted five specifically demonstrated cases.

Reproduce from checkout with local Chromium and Playwright installed:
`python tests/experience-2/test_optin_submission_pair.py`.
It writes a *synthetic-only* receipt at `docs/experience-2/local_signup_pair_receipt.json`. The test is **not** a substitute for running `verify_guest_optin_readonly.py` against the actual anonymous WordPress/Assembler public site. The current local runner has no DNS path to finalvestige.com, and hosted browser/Jetpack, axe/WCAG 2.2 AA, 200% zoom, Safari, actual media transfer, independent CI and field CWV remain unverified. A usable form does not equal a confirmed lead, sale, or realized net revenue.

## Conversion decision contract

**OFFER:** Free 52-page Seven Day Focus Fieldbook.
**FUNNEL STEP:** Anonymous Focus visitor -> *usable field and submit action* -> Jetpack request -> independently confirmed lead -> verified purchase.
**BLOCKER:** Field-only positive readiness mistakenly accepted unusable forms.
**CHANGE:** Same-form, complete first-screen mobile admission with 39 independent synthetic controls.
**EVIDENCE:** 5 old false positives reproduced; candidate rejects all; 39/39 offline tests.
**OWNER:** Interim engineering owns this read-only QA branch. Claude owns actual Jetpack event confirmation and attribution; Grok and Praxxis own creator/channel asset IDs under #820.

**Release: HOLD.** No affiliate activation, social post, subscriber creation, direct merchant link, analytics deployment, merge, WordPress edit, or spending. The separate real Focus `?subscribe=` false-success defect remains in draft PR #1681 and must be reviewed independently. Three visual art directions remain on record under Issue #150; this PR makes no aesthetic or historical-content changes.
