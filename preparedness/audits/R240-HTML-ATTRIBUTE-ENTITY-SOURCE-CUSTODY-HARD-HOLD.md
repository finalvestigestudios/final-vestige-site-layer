# Preparedness R240 — HTML attribute decoding / source visibility gate (2026-11-09 PT)

**Issue:** #136 · **Conversion coordination:** #820 · **Business charter:** #818. **DRAFT_HARD_HOLD.** This is a stacked isolated Preparedness-only change on R239 #1745, not main. No merge, WordPress, CMS, navigation, analytics, merchant/affiliate, email, social, public publishing or spending.

## New failure mode and bounded correction

In source HTML, the R238 lexer inspects raw attribute spellings. HTML browsers first decode character references **inside attribute values**, so a draft such as `<div aria-hidden="tr&#117;e">{{cite:ready-plan}}</div>` is hidden to readers while R238's raw `aria-hidden="true"` regex can miss it. The equivalent CSS example `<p style="display:&#110;one">{{cite:ready-plan}}</p>` also conceals evidence. This is a structural citation-visibility concern, **not an assertion that any original manuscript contains that mutation**.

R240 adds independently pinned `r240_html_attribute_entity_custody_hold.py`. It fails closed on encoded values in `aria-hidden`, `style`, `class` and `id` attributes; these may affect hidden state or existing CSS selectors. It also rejects duplicate visibility-sensitive attributes. Normal text citations and benign character references in unrelated `title`/`data-note` are preserved. It uses the standard-library HTML parser as an *additional* syntactic screen; R238/R239/export DOM validators and qualified human review remain mandatory. The parser is **not** claimed to model all HTML5 error recovery or computed CSS.

The new guard is authenticated by exact Git blob `123c8a7993029d65e6afa8f56aba5c5e18121afd`, installed before rendering in R220 and rechecked after audit. It reads the original 35-body roster through the preexisting safe reader, counts citation tokens, produces SHA-256 source-body receipts, and always returns false publication/QD/source/medical approvals and `human_review_required=True`. No original article, source record, crosswalk, taxonomy, routes, publication status or build output is modified.

## Actual execution evidence, limitations and release hold

- **117/117 local isolated Python unittest cases passed**, including 105 generated individual source-mutation methods, earlier negative controls, 35-roster/receipt integrity and unaffected SVG/benign entity controls. `python -m py_compile` passed. The executed module/test files match Git blob identities `123c8a7993029d65e6afa8f56aba5c5e18121afd` and `420cb52267c91c7b29f6bbcff9c9556a7eb93a77`.
- The execution was **synthetic**. The entire native repository is not mounted in the local runtime and the local shell could not resolve `github.com`; **full `python -I preparedness/tools/validate.py`, `build.py`, inherited test suite, real WordPress exports and full R220 integration were NOT executed**. No source semantics, safety or QD was approved.
- All seven original Claude contributor refs were read via GitHub exact-ref comparisons against frozen R200 manifest SHA: 7/7 unchanged. Independent review #157 and synthetic-fixture #169 remain draft/unmerged, separate from this stacked integration; homepage lead #1689 remains untouched. The full authentic 35-article HTML parsing by the **committed Python R240** remains unverified.
- Still held: three source-to-claim citation occurrences (Article #7 CDC twice; Article #20 Ready.gov once), 32 shared-source scope groups and qualified high-consequence editorial/safety review. A present source-use note is not a source-support finding. The original 35 articles and six tools remain unreleased.

## Conversion acceptance — one provisional pathway, NO activation

Audience: households assembling an out-of-area contact plan and essential family documents. **Free destination:** existing approved public `/preparedness/` resources (not the unpublished 35 detailed guides). Existing **Legacy Triage ($19 PDF)** is a *provisional* possible optional practical pack only; as an estate/incapacity product it may be a poor disaster-readiness fit and has not passed rights, private-data handling, product-fit, merchant checkout, fulfillment, refund or commercial approval. No paid CTA proposed for publication. No retired water guide or invented product.

**Offer → funnel step → blocker → change/experiment → evidence → owner**

1. Grok household contact asset → free Archive → no verified published asset ID/allowed landing link → authenticate one actual asset and `utm_content=asset_id` through TASK-008 → **UNVERIFIED** → Grok/Praxxis.
2. Free landing → trustworthy plan/guide → authored 35-slate still held → authenticate native build and independent source/safety review before considering detailed-guide link → **HARD HOLD** → Preparedness/QA.
3. Free resource → optional Legacy Triage → suitability, commercial rights and sensitive password/account handling unknown → inspect original PDF, disclosures and demand; decline inappropriate upsell → **NOT APPROVED** → Founder/Commerce.
4. Qualified CTA → paid product → mobile destination, checkout, delivery and refund policies untested → authorized no-spend checkout/fulfillment QA when approved → **NOT TESTED** → Commerce.
5. Campaign visits → net revenue → no independently confirmed transactions, refunds/fees or human-session attribution → 7-/30-day cohorts based on merchant records with tiny-sample flags → **NOT COMPUTABLE** → Analytics/Commerce.

**Net realized revenue per 1,000 qualified human sessions: NOT COMPUTABLE.** No affiliate clicks, newsletter confirmations, visits or checkout starts were represented as paid orders. Founder release authority and Grok's publishing ownership remain unchanged.
