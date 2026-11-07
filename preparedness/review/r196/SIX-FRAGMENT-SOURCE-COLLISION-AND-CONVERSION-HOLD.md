# R196 — six-fragment source custody and cross-cluster collision workorders

**Owner:** Preparedness #136. **Coordinate:** #820 / #818. **State:** `BUILT / SYNTHETICALLY TESTED / DRAFT_HARD_HOLD`. Never QD PASS, source approval, commercial activation, or WordPress publication.

## Newly observed authentic evidence (2026-11-07)

R195 pins the seven article-body/meta pairs but does not independently inspect the *six original source-fragment Git objects* in the R194 docket. R196 adds a separate read-only, fail-closed custody gate over the three affected Claude clusters (each frozen + observed, exactly six Git objects).

Authenticated GitHub blob reads (not a local full repository build):
- Historical Field: **26 → 28 source rows**. New `hist-field-oac-breen-diary` and `hist-field-ia-hastings-guide`. `loc-prairie-traveler` changes its `supports` and `notes` explanation.
- Historical Food: **28 → 28 rows**. Removed `hist-food-nchfp-jerky`, introduced `nchfp-jerky`; these IDs MUST NOT be auto-aliased even if their pages appear closely related. The original source rationale explicitly records NCHFP/USDA FSIS guidance differences. Human food-safety review remains required.
- Historical Home: **27 → 29 rows**. New `hist-home-wellcome-chadwick-1842` and `hist-home-msu-simmons-1798`. `hist-home-loc-simmons-1796` notes change, distinguishing catalogue-only 1796 evidence from partially read 1798 text.

**New cross-cluster discovery:** `loc-prairie-traveler` and `loc-pioneer-diaries` occur in both Historical Field and Historical Food observed fragments but contain different metadata and/or claim explanations under the same ID. The first differs in title/publisher/supports/notes; the second differs in title/publisher/published/verified_on/supports/notes. Do not allow an unordered fragment merge to choose one silently. Require human choice of a source claim scope and carry forward both interpretations until resolved. No finding here proves that either source itself is invalid.

All **85 observed source entries in these three fragments** have `human_link_check: false` (confirmed by authenticated source reads); a `verified_on` string is not evidence of a separately performed human link or safety check. These 85 rows are **not the entire 35-article crosswalk**. The full archive remains held.

## New preflight

`preparedness/tools/r196_fragment_source_custody_gate.py`: pins exact R194 docket Git blob and six fragment Git blobs, enforces the **81 frozen → 85 observed** local fragment-row census, rejects missing/substituted objects, duplicate IDs *within* a fragment, malformed JSON / duplicate keys, unsupported external URLs, silent addition/removal/redefinition, and unauthorized approval fields. Emits deterministic *PENDING* workorders for source additions, removed/unaliased IDs, changed claim scopes, and cross-cluster same-ID differences. Never merges/rebases; successful structural evidence still exits **2 (`DRAFT_HARD_HOLD`)**; invalid evidence exits **3 (`INVALID_HARD_HOLD`)**.

Tests: exact new Python module plus separate conflict-specific regressions executed locally with synthetic blobs; **59/59 PASS**, Python isolated compilation PASS. This proves only synthetic predicate behavior, NOT actual original-source safety, Git checkout, 35+6 native validation/build, WordPress exports or QD.

## Integration order and independent QA

Maintain R195 seven-article body/citation custody, add R196 six-fragment source review, **then** reconcile cross-cluster source IDs under an explicit human ledger before any claim that all 35 guides and six tools can render with a coherent safe bibliography. Safety PR #157 remains independent; fixture PR #169 + follow-up #973 must retain temporary isolated source-fixture behavior; all touch the original test suite and must not be blindly merged.

Seven Claude branches are at their unchanged last-known current heads (exact refs checked separately); historical crosswalk drift still needs deliberate source/reading review. Home lead latest draft is separate. Complete original `python -I preparedness/tools/validate.py`, `build.py`, `python -I -m unittest discover -s preparedness/tests -v`, 41 exports, browser, print and independent reviews are blocked by local GitHub DNS/complete-checkout unavailability. **No claim of full native pass.**

## Conversion-first acceptance: OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Experiment / acceptance checks | State | Owner |
|---|---|---|---|---|---|
| Existing **Legacy Triage** public PDF candidate | Optional paid household-records continuity pack | Actual FV merchant identity/rights, SKU contents, accurate pricing, checkout, fulfillment, returns and fees not independently authenticated | Founder/Commerce verify owned digital file, rights-cleared licensing, signed-out mobile merchant path, actual delivered download, fee/refund ledger *before* activating any CTA; match exact benefit to records audiences, never school pickup/medical safety | **HARD HOLD**; no paid sale verified | Founder / Commerce / Claude |
| Grok records-continuity topic | Published creator asset → already-public, ungated `/preparedness/` agency-resource gateway | No matching authenticated published asset_id, post URL, rights, approved destination, actual UTM from current TASK-008 | Grok/Praxxis check existing queue only; for a real approved asset require `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=<real asset_id>`, page-intent match and mobile link integrity | **UNVERIFIED** | Grok / Praxxis |
| Original Household Emergency Plan | Official-source reading → comprehensive free guide | Source adjudication, food/medicine safety, qualified QD, full native rendering | Source/date/claim trace, no unsupported directives, ungated access, review stamps, visible offline citations; do NOT link visitors to draft slug | **UNPUBLISHED / HARD HOLD** | Preparedness / Independent QA |
| Family Reunification Card | Optional FREE printable, never an invented paid upsell | 11 unresolved tool source decisions; sensitive child contact info; browser/print acceptance missing | Only synthetic family data at 360/390/768/1440px, keyboard-only, offline/print consistency, blocked network/storage/third-party embeds and consent text where relevant | **UNPUBLISHED / HARD HOLD** | Preparedness / Site QA |
| Confirmed commercial purchases | Paid order → net revenue per 1,000 qualified-human sessions | No confirmed merchant paid orders, fees/refunds, genuine social attribution, qualified session denominator | Reconcile first-party `asset_id`/UTM → relevant CTA → qualified session → merchant-paid settled order → refunds/fees → net revenue; report 7/30d and low-N uncertainty | **NOT COMPUTABLE** | Commerce / Analytics |

Draft CTA copy only (NOT deployed): “Keep essential documents and contact details findable. Read the free official-source preparedness starting points.” If an authenticated and independently reviewed paid records pack is approved later, make a **separate, clearly labeled optional product** with visible exact deliverable, price, refund terms and no fear/urgency framing. Preserve the current Seven Day Focus Fieldbook; never revive retired water freebies.

## Release boundary

No production branch merge, WP/CMS/nav/homepage/analytics/vendor/script/email/social/merchant or spending action. No invented public draft URLs, offer states, approval, real-person financial results, safety certification, or creator performance. Human source/medical/food/privacy review, independent QD and founder release consent remain mandatory.
