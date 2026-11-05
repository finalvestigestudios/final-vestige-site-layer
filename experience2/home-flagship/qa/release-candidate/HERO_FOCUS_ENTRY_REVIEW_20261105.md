# EX2 P0 — evidence-first hero → clear Focus lead capture (review only)
**2026-11-05** | Issues #150 / #820 | Independent conversion UX candidate | **DRAFT / HOLD**

## Exact parent and scope
Parent branch: `qa/ex2-margins-review-receipt-rollback-20261105` at `3de43ed824e049cb734535cc13d59b688bd6e43e` (draft PR #1075). Do not merge or publish independently of full stacked review. Frozen PR #49 `10495883299d53596992c26a8987f629b2904670` remains untouched. No new chapter, CMS change, Jetpack setting, script, pixel, affiliate URL, paid offer, historical media, font, or subscription.

## Offer → funnel → blocker → testable hypothesis
- **Offer:** existing free **52-page Seven Day Focus Fieldbook**, not a paid product; lead capture is not revenue.
- **Audience:** history/evidence readers from genuine Grok-produced topic-matched video/assets. Keep links/platform attribution owned by Grok/Praxxis and Claude (#820/TASK-008); this branch changes **no** UTMs or tracking.
- **Funnel:** credible Franklin source-driven homepage → contextual free Fieldbook → voluntary Jetpack confirmation → verified subscriber → future rights-cleared paid product/merchant verified order if available.
- **Blocker:** original hero's secondary action was generic `Read the investigations`, while Fieldbook exposure depended on header or much-later chapters; at mobile narrow widths, the secondary text link had no 44px tap-height guarantee. This is a UX **hypothesis**, not an observed abandonment rate.
- **Change:** preserve the original primary `Enter the evidence room` action and Royal Museums Greenwich original-object source. Change only the existing secondary hero link to `Explore the free 52-page Focus Fieldbook` using existing `/focus/` destination; add 44px touch target and wrap containment, including 200%-CSS-zoom reflow.
- **Hypothesis:** specific, relevant action increases qualified confirmed leads without reducing source engagement or harming commercial conversion; no resulting change can be claimed until controlled, consent-respecting observation and verified CRM/merchant events.
- **Owner:** Homepage UX engineering (this candidate); Claude owns attribution/commerce; Grok and Praxxis own asset IDs and acquisition; founder approves release.

## Before → proposed after (NOT LIVE)
| Existing unpublished candidate | New isolated draft |
| --- | --- |
| Evidence-primary + secondary generic investigations link | Evidence-primary + secondary explicit free 52-page Fieldbook |
| Hero text target in representative fixture ~18.2px high | Proposed second action 44px high on 320/360/390/768/1440/1920 |
| Extra hero click returns to broad blog | Contextual next action goes to existing Focus offer |
| No additional merchant truth/CTA | No paid claim; existing source links and independent editorial proof remain |
| No proven visitor conversion | Still **no proven conversion**: staged UX candidate only |

The first screen is **not** replaced by an affiliate promotion; 7 chapter navigation anchors, Franklin folio original-source link, 4 script tags and existing evidence-primary CTA remain source-identical apart from the single link replacement. Public Page 6, 72 Margins, Jetpack, Collection and signup are **not** modified.

## Source and browser verification (strictly scoped)
- Exact GitHub source read at parent: `index.html` blob `71511fec93f724a3a2123cd863d654014f030d7e` and `flagship.css` blob `13e6c31c06e1d2afe9ca145409437e7ad25fc786`.
- Exact branch source preflight: one changed hero anchor; Focus destination occurrences in **candidate** 4→5; 7 chapter anchors and RMG source link retained, no additional JS. **This count does not describe published WordPress Page 6.**
- New committed Node `tests/test_hero_focus_entry.mjs` has 12 native-targeted positive/adversarial checks. The 12 exact committed test bodies were executed against exact GitHub source strings in a V8 adaptation: **12/12 PASS** after correcting two poorly scoped negative mutants. **Native Node exact checkout remains unexecuted**.
- Local Python Playwright/system Chromium ran a **representative offline first-screen fixture**: old/proposed variants × 6 viewport widths = **12/12 checks PASS** with no JavaScript and reduced motion; old secondary target ~18.2px height, proposed ~44px; no detected document-root horizontal scroll. Generated review screenshots for 320/390/768/1440/1920 proposed and 320/390/1440 before. This fixture is **not** the complete GitHub page, WordPress Assembler, the production site, WCAG audit or real network image transfer.
- Additional Playwright fixture keyboard checks at 320/390/768/1440/1920: **5/5 Focus links keyboard reachable**. CSS `zoom:2` **surrogate** CTA box inside viewport **5/5**, after a first attempted inline-flex treatment showed clipped CTA at 320px; fixed in draft by switching to block wrapping and zero min-width. **CSS zoom surrogate is not a certification of native 200% browser zoom or WCAG 2.2 AA.**
- No actual WP staging or live anonymous Chromium. No axe result, Safari, real photo byte verification, current Lighthouse/CWV, merchant confirmed purchase or attributed confirmed lead. No release pass.

## QA and handoff gates
1. **Read-only** check PR exact head and latest code; run `node --test experience2/home-flagship/tests/test_hero_focus_entry.mjs` in exact checkout (fail closed).
2. Qualify the complete seven-chapter page in real isolated WP/Assembler harness (PR #637 workflow pattern): 320/360/390/768/1440/1920, actual source CSS and images, exact SHA receipt, axe WCAG 2.2 AA, keyboard/touch/no-JS, reduced motion, native 200% zoom and Lighthouse. The Personal WordPress.com plan has **no native second staging clone**; Playground is a nonproduction approximation, not evidence for Atomic host-specific cookies/Jetpack/field CWV.
3. Test entry promise and CTA clarity with founder on visual screenshots, ensure no sticky popup traps the reader, and confirm `/focus/` link/consent/delivery before release.
4. Rights & provenance: zero new assets or factual claims; existing Franklin museum citation/rights and all image-rights gates remain open until independently cleared. No Inspire3 benefit or payout assertion.
5. Founder-specific release approval, QD exact SHA, runner-backed CI green. **HOLD**; do not merge or publish by default.

**Commercial acceptance KPI:** realized **net revenue per 1,000 qualified human sessions** with 7/30-day cohorts, verified merchant orders and refunds/fees. Supporting metrics: confirmed opt-in leads and lead-to-customer conversion; clicks and form opens are not sales. No outcome implied by this draft.
