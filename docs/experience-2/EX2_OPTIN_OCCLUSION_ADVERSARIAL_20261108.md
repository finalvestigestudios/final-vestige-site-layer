# EX2 P0 — Guest opt-in occlusion / keyboard false-pass hardening
**Read-only review only · 2026-11-08 PT · Parent #1702 at d0ae48390996abcb71eddc7c0f3eb38b3f27f139 · release HOLD**

## Source and deployment boundary
This change is **stacked only on #1702**. PR #49 (frozen SHA 10495883299d53596992c26a8987f629b2904670) is untouched. No WordPress CMS editing, plugin installation, subscriber action, affiliate CTA, tracking, email send, deployment, merge, or new paid service was performed.

Fresh authenticated read-only WordPress inspections on 2026-11-08 PT established:
- Production Page 6: published, editor modified 2026-11-05 12:07:24 site-local, 150,710 characters, seven live chapter targets, 72 Margins records, native Jetpack subscription block, two Focus links in the protected opening/homepage experience.
- Focus Page 1579: published, editor modified 2026-11-05 17:44:02 site-local, native Jetpack block. Existing script fvf-gift-v2 still accepts non-error URL query-string subscribe values to expose the PDF panel; refer to separate repair #1681. **This hardening does not fix or claim to fix that live behavior.**
- Dispatch Page 523: published; native Jetpack subscription block.
- WordPress site listing: only production site 256784396, no staging clone. Personal plan does not make a native WordPress.com staging environment available. Never confuse its included wpcomstaging.com hostname with an isolated staging site.

No private editor exports or subscriber data were checked into GitHub.

## Reproduced weakness in the parent harness
The existing first-viewport verifier checked input.is_visible(), style opacity of the input itself, the **single center hit-test point**, and !input.disabled. Real isolated Chromium demonstrated **seven false-positive cases**, despite the positive result implying that a mobile visitor could use the signup field:

| Synthetic negative control | Parent #1702 | This branch |
| --- | --- | --- |
| Ancestor aria-hidden=true | Incorrect PASS | Reject |
| Disabled fieldset surrounding enabled-looking input | Incorrect PASS | Reject |
| Read-only email field | Incorrect PASS | Reject |
| Fixed overlay covering left 45% with center clear | Incorrect PASS | Reject |
| Ancestor opacity:0 | Incorrect PASS | Reject |
| tabindex=-1 keyboard-inaccessible email input | Incorrect PASS | Reject |
| Overflow-clipped parent hiding part of field | Incorrect PASS | Reject |
| pointer-events:none field | Already rejected | Reject |

This is a **harness defect**, not proof any of these states presently occurs on finalvestige.com.

## Implemented without adding production code
Updated tools/experience-2/verify_optin_viewport_geometry.py in place, preserving its public inspect_optin_viewport(page) return key. Replaces center-only acceptance with a 3x3 unobstructed hit test; respects clipping containers, ancestor visibility/opacity/inert/aria-hidden/pointer-events, disabled fieldsets, readonly and tabindex=-1. A positive result now requires ALL nine hit points and a plausible accessible name in markup. Form fields inside nested iframes are **diagnostic only**: a hidden iframe can pass its own internal geometry but cannot certify parent-page visibility. The API returns no form values, addresses, or user inputs.

Added tests/experience-2/test_optin_adversarial.py. In local Chromium, **25/25 PASS**: 5 good responsive widths, 18 adversarial states including hidden nested iframe and labels hidden from accessibility, and 2 valid ARIA-label cases. The preexisting parent Chromium suite still passes **13/13**, total **38/38 synthetic browser scenarios**. Exact committed blobs were checked against the locally executed files.

Run from a complete exact checkout:
\`\`\`sh
python tests/experience-2/test_optin_geometry.py
python tests/experience-2/test_optin_adversarial.py
\`\`\`
The tests are offline synthetic fixtures, with no network or subscriber submissions. The committed adversarial suite emits docs/experience-2/local_adversarial_optin_receipt.json for a reviewer running it. The host environment here lacks outbound DNS/network access, so an honest anonymous hosted WordPress visitor run is NOT available. No Lighthouse, Web Vitals, axe/WCAG, Safari, genuine email confirmation, paid order or net-revenue result is claimed.

## Commercial acceptance plan
**Offer:** Free 52-page Seven Day Focus Fieldbook (retain current PDF + Jetpack subscription form).  
**Funnel step:** Qualified human traffic from Grok-owned content -> actual in-app mobile landing -> truly operable signup field -> independent confirmed Jetpack lead -> eventual independently verified purchase.  
**Blocker:** False-positive browser checks risk declaring the field usable when it is covered, inaccessible or non-operable. The separate live false-success script remains P0 (#1681).  
**Change/experiment:** Run this stricter guest-browser verifier without form submission on homepage, /focus/, /dispatch/ at 320, 360, 390, 768, 1440 and 1920px; inspect actual screenshots/geometry, 200% zoom and keyboard/assistive-tech; compare before/after if a real issue is identified.  
**Pass/fail evidence:** 38/38 Chromium synthetic tests PASS; seven old false-pass cases now rejected; **hosted tests BLOCKED**, no subscriber conversion proven.  
**Owner:** Interim homepage engineering maintains this review-only QA; Claude owns Jetpack state and backend attribution; Grok/Praxxis own creator asset IDs/distribution; founder approves any production change.

A 7- or 30-day net revenue per 1,000 qualified-human-sessions KPI is **not computable** from pageview totals. Do not count CTA clicks, form impressions or UI success messages as paid sales or confirmed subscribers.

## Remaining governed release checks
Real WordPress/Assembler presentation and genuine first-party media transfer; axe-based WCAG 2.2 AA including no-JS, reduced motion, 200% zoom and keyboard; measured Lighthouse/CWV, authoritative media/rights; Jetpack pending/confirmed/already-subscribed/email delivery; independent exact-head CI + QD, then founder release approval. Existing source-controlled PRs remain unmerged and production is not to be altered.

No new chapter or commercial claims. Preserve the seven-chapter archive, Franklin folio, all 72 Margins entries, Focus/Dispatch and editorial independence.
