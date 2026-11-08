# EX2 — exact PHP no-JS meaning & Focus conversion-path QA (8 Nov 2026)

**Scope:** Review-only, isolated from production. Parent PR #1568 exact SHA `e8176caa9d3d1dcc5bd47f0cf6dd1b5d16d11ebf`. Frozen PR #49 SHA `10495883299d53596992c26a8987f629b2904670` **not edited**. Do not merge, deploy, write WordPress or activate affiliates.

## What was newly exercised

Previous #1568 verified interaction/Chrome AX/touch behavior; this run tests that **historical meaning is not gated behind JavaScript**. The exact protected Playground PHP plugin `7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee` was executed using the committed PHP WordPress-function stub; its resulting full seven-chapter HTML SHA-256 was `f3c3416a531dd88e84d900c4f972a71035a158e8e947848f5e49b15db13ac749`. Real Chromium 144.0.7559.96 tested **320, 390, 768, 1440 CSS-pixel viewports** with JavaScript both disabled and enabled. **84/84 checks PASS; three mutation controls were properly rejected.**

When JS is disabled, **all three evidence cases (Apollo, Franklin, Malbone), both dated Franklin entries, and both comparison illustrations stay readable**. Enhancement-only controls remain hidden rather than presenting dead buttons. Native disclosure opens without JS. With JS enabled, deliberate case selection exposes exactly one case and the three controls work. All tested routes retain chapter anchors and at least two visible existing free Focus Fieldbook destinations. No document horizontal overflow or page error was observed; 72 Margins records and two rights-reviewed candidate images remain present. This is **functional parity in the PHP-generated fixture**, not production functional confirmation.

## Before/after visual observation

This is **a comparison of no-JS and JS states, not an edited design**. Source renderer unchanged. Screenshot `nojs_390_details.png`: the open observation evidence note has readable explanation about the removed studio seal, with both illustrations still present and without nonfunctional controls. Screenshot `js_390_case_selection.png`: the original three evidence selector cards permit selecting Malbone and show the selected state. Both are local Chromium captures with external image requests blocked, *not* current WordPress screenshots.

## Fresh production reconciliation

Authenticated WordPress Page **6** on 2026-11-08 remains **published**, last edited `2026-11-05T12:07:24`, with 150,710 content characters, seven-chapter navigation, 72 Margins entries, four image HTML elements and one Jetpack block. The review renderer is **NOT equivalent**: it contains two archive images and omits the live NYPL Brooklyn Rapid Transit map. Do not replace the published page from this candidate or claim a staging certificate. WordPress.com exposes production site **256784396** only, no native staging clone on the Personal plan.

## Source and rights

WordPress media metadata still lists Apollo #473, NASA S67-19766, **78,346 bytes**; Franklin #474, note reproduction, **466,043 bytes**; and the live NYPL map derivative #1258, **5,553,669 bytes**. Those are metadata, **zero successful network transfers were measured in this offline test**. The NYPL edited derivative is excluded from the protected review and remains pending exact-file provenance and rights clearance. No historical claims or images altered.

## Conversion priority and owner

**OFFER:** Existing free 52-page Seven Day Focus Fieldbook. **STEP:** Reader reaches source/contextual Focus route, then authentic Jetpack signup, then separately independently confirmed paid order. **BLOCKER:** No real WordPress/Jetpack subscriber proof and no verified net revenue; no-JS reachability was a separate test gap. **CHANGE:** Source-controlled regression and negative-control harness, not new UI, affiliate CTA or measurement scripts. **EVIDENCE:** 84 real Chromium checks, 3 mutation rejections, SHA-pinned PHP and screenshots. **OWNER:** Interim homepage engineering QA; Claude owns hosted form and attribution; Grok owns acquisition. **IMPACT:** Accessibility/conversion-path robustness confirmed only in fixture, **no uplift or paid conversion claimed**.

## Release decision: HOLD

Still required: isolated native WordPress core/Assembler (Playground/local install) using public-only content; real first-party archival transfer status/bytes; independent axe + manual WCAG 2.2 AA, actual 200% browser zoom, screen reader, mobile Safari if available; measured Lighthouse and hosted field CWV; real Jetpack consent and verified lead (with founder-approved test only); existing Focus fake-success bug #1451 resolved; merchant-confirmed orders/refunds/fees for net-revenue KPI; exact-SHA CI/QD and founder release approval.

Run: `python experience2/review/verify_nojs_conversion_truth.py --bundle /safe/private/fv-ex2-official-playground-web-review.zip --out /tmp/nojs-results` with PHP CLI, Playwright Python and Chromium. Add the existing sibling `experience2/review/verify_php_playground_renderer_browser.py` to the same Python import path. The private ZIP is **not** committed to GitHub.
