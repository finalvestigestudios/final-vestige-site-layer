# Preparedness R266 — bounded Chromium printing observation (DRAFT / HARD HOLD)

**Issue:** #136. **Commercial coordination:** #820 / charter #818.
**Scope:** only `preparedness/`. **Source:** original held R264 HTML Git blob `40782ef142edfd348fec53eb6d8a0dc673244dea` (unchanged).
**Frozen seven-cluster custody:** R200 manifest `5822f9dfde21d1f3bdfc26658769d852c639438c`; 35 articles/2,000 citation occurrences unchanged.
**Review boundary:** independent QA PR #157, isolated fixture PR #169, homepage PR #1689 unchanged. No public or merchant write.

## Empirical offline print evidence — 2026-11-10 UTC

The complete R264 candidate HTML was reconstructed byte for byte in the local
test environment and independently matched to its Git blob. Chromium 144,
via Playwright `page.set_content`, printed it to a single Letter PDF
with JavaScript enabled AND disabled, print backgrounds enabled. In both
modes, SHA-256 of the PDF bytes was
`1dae8e974cd87e629f670e3393a5361bccc328ff9307e7984a32c9f899f6d251`.
`pdftotext -layout` showed both privacy warnings, and the resulting PDF
was rasterized and visually inspected. Both card-face cautions appear within
their respective printed faces in this *one* tested rendering.

Bounded Chromium computed geometry: unfolded card 672x206 CSS px,
two 335px-wide faces, computed privacy-note font approximately 10.6667
CSS px (=8 pt). The current source explicitly fixes its card to 7 inches.
This is **not** a determination of adequate font size, contrast, real printer
fidelity, paper-cutting safety or child-data exposure.

**Separate mobile negative finding:** screen widths of 360px and 390px
produce document scroll widths of 680px. Screen widths of 768px and 1440px
do not overflow in the same experiment. This **is a bounded reproducible
mobile overflow finding in the draft preview**, not evidence of a currently
deployed live issue. Keep this as a release/design-review blocker rather than
manufacture an unreviewed responsive fix.

## Safety/custody implementation

- `tools/r266_wallet_browser_observation_custody_hold.py` locks the exact
  original HTML source Git blob and browser-observation receipt.
- Strict JSON duplicate-key, key-set, type and value checks prevent turning
  the observation into QD, privacy, source, merchant or release approval.
- R220 loads this gate **before held WordPress draft rendering**, requires
  explicit negative statuses and records `wallet_card_bounded_browser_observation`.
  The module and receipt Git blobs are rechecked at audit completion.
- `tests/test_r266_wallet_browser_observation_custody_hold.py` contains
  53 executed isolated unit cases covering exact source/pin parity,
  29+ mutated evidence fields, previous-gate false-PASS changes and
  malformed/duplicated evidence. This is NOT full native repo testing.
- No original article, tool, citation, route, R264 candidate, safety-state
  designation, WordPress CMS content or existing analytics tracking was edited.

## MUST remain HARD HOLD

- The full `python -I preparedness/tools/validate.py`,
  `python -I preparedness/tools/build.py`, and 36+ inherited repository
  tests could not run here: local DNS cannot resolve `github.com` to clone
  the private authenticated repository. Browser/tests are isolated source
  checks, not authenticated all-41 export verification.
- Actual physical paper print, cut/fold, human readability, device/browser
  matrix, screen-reader/keyboard testing and qualified child-privacy review
  remain outstanding. The original Tool #104 was NOT browser-tested.
- All 32 shared-source groups still require independent source adjudication;
  the three held disputed original citations (Article #7 two CDC, Article #20
  one Ready.gov) and Article #7 chemical-contamination advice remain held.
- No independent QD PASS, medical/privacy safety certification, product
  approval, public publication, navigation, CMS write or commercial activation.

## Conversion-first bounded acceptance / owner map

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Free official-resource Preparedness Archive | Existing Grok asset → landing | Immutable matching asset_id, rights and signed-out mobile destination not verified | Read existing TASK-008 and confirm previously published matching asset only | NO VERIFIED MATCH; no new Grok assignment | Grok/Praxxis |
| Free original family guide / Tool #104 | Guide → candidate wallet card | 360/390 screen overflow; child/privacy/physical print and source holds | One-Chromium print smoke and pinned receipt; real accessibility/paper review remains | PDF text/warnings observed; 360/390 OVERFLOW; release HOLD | Preparedness + independent QA |
| Existing Legacy Triage owned PDF (provisional, not approved upsell) | Optional guided tool → paid product | Rights, source provenance, PDF privacy/credentials and audience fit unverified | Complete owned-product audit and founder approval before a contextual CTA | NONE APPROVED | Founder/Commerce |
| Same proposed product | Checkout → fulfilled paid order | Delivery, fees, refunds, purchaser consent unknown | Authorized merchant acceptance check without live transaction mutation | NOT TESTED | Commerce |
| Same proposed product | Cohort → realized net receipts | No authenticated orders/fees/refunds or per-asset qualified-human sessions | 7/30-day cohort reconciliation through existing measurement ownership | Net revenue per 1,000 sessions NOT COMPUTABLE | Analytics/Commerce |

No retired water freebie, new product, social post, email or affiliate activation.
No paid services or duplicate measurement scripts. Preserve Grok creator control and
Claude site-engineering ownership. The candidate remains an **unapproved source-only concept**.
