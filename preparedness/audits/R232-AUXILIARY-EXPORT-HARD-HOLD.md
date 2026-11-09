# Preparedness R232 — Auxiliary Draft Export Custody (2026-11-08 PT)

**Issues:** #136 integration/source safety, #820 verified conversion, #818 business governance. **Release state:** BUILT / SYNTHETICALLY TESTED / NATIVE NOT EXECUTED / DRAFT_HARD_HOLD. This is not human source approval, medical/food/water safety review, independent QD, commerce approval, or permission to publish.

## Discovered gap and change

R231 protected each of the 35 original article plus six existing tool outputs in the WordPress and preview channels (41 × 2 = 82). The actual authenticated `build.py` also emits a Preparedness **landing** and zero or more populated **section hubs** in BOTH channels. Before R232, the R220 custody loop did **not** compare complete bytes of these auxiliary pages, reconcile their report rows, or reject stale/unreviewed extra filenames in the build directories. A synthetic extra merchant/CTA page could therefore coexist with otherwise valid 82 protected outputs. No public-site exploit was observed.

R232 adds one pinned, read-only validator:
- Independently reconstruct every landing and hub through the R222-authenticated builder with draft mode on, checking EXACT UTF-8 bytes of each `wp` and `preview` output.
- Reconcile `build-report.json` landing populated-section/card totals and hub section/order/count to the reconstructed producer result.
- Reject any extra, missing, symlinked or non-file member in `build/wp` and `build/preview`. Protect original 41 article/tool filenames; no unexpected CTA, HTML, redirect file or tracker can silently become an extra output. No `--public` mode substitute is accepted.
- Validate unique safe section and article slugs, unique combined filenames, and preservation of explicit `DRAFT_HARD_HOLD`/false authorization indicators.
- Execute R232 only after all original R220 article/source/citation gates, then recheck the new guard's pinned Git identity before reporting HOLD. It does not alter articles, safety labels, citations, source-register entries, canonical routes, CSS, builder source, WordPress, site navigation, or analytics.

### Test evidence and limits

Local executed Python test path: `preparedness/tests/test_r232_auxiliary_export_custody_hold.py`. **139/139 PASS** with offline isolated synthetic `TemporaryDirectory` fixtures. Python compilation PASS. Git blob IDs of executed local source and test files verified byte-for-byte against GitHub branch:
- Module `d723f888dba57d8e280ac24003239e93e30cae65`.
- Test `0691b2bd67b7bd3c6dcf72b5d898df29b1df3b12`.

Tests include 88 missing-output mutations across both channels; 24 auxiliary injection mutations, 10 extra-output mutants and controls for symlinks, report drift, invalid slugs, malformed generated records and positive HOLD. None of these tests requires a public CMS, merchant or internet access.

**NOT RUN:** full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited R220 integration suite, native original 35-body source verification, full authentic 41+hub+landing render inspection. The worker container cannot resolve GitHub and lacks a trusted complete checkout. Connector checks establish source and commit identity, not native executable readiness. Extra shell pages add exports beyond the 82 article/tool files; their authentic number will be determined by the actual populated taxonomy.

**Preserved blockers:** Original three citation-use exceptions (two CDC #7, one Ready.gov #20); seven historical source-ID adjudications; Article #20 household water, service-animal / ESA and powered-device restoration language; human source and appropriate qualified safety/QD review. Do not reclassify historical descriptions as instructions. Independent QA PRs #157 and #169/#973 remain unmerged, separate.

## One creator-to-guide candidate, no queue takeover

Topic: **out-of-area household contact and locating essential family documents**. Grok/Praxxis TASK-008 must identify an *already published* actual social `asset_id`, platform URL, date, accurate factual hook, caption destination/rights and final mobile journey before any attribution claim. The only confirmed free endpoint to propose remains `https://finalvestige.com/preparedness/` and its link to an official household planning guide; the unpublished original 35 drafts are not public destinations.

**Draft on-page editorial CTA, NOT for deployment:** “Have you chosen an out-of-area contact and written down where your household keeps its essential documents? Start with the free official emergency-planning checklist.” No lead gate for essential safety guidance.

**SINGLE provisional commercial candidate:** Existing *Legacy Triage* PDF, advertised $19 via Vested Wisdom Payhip. This product addresses estate/incapacity records, **not disaster response**; privacy, account-access handling, founder seller rights, product/guide intent fit, refund, merchant checkout/fulfillment and confirmed orders are NOT verified. It is **NOT APPROVED for a Preparedness paid CTA**. Do not create or publish a replacement offer without founder approval; do not revive retired water guide.

### Offer → funnel → blocker → experiment → evidence → owner

| Offer / step | Blocker | Draft acceptance check / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Existing creator asset → free `/preparedness/` | No confirmed real post ID, final UTM/caption or human session | Match platform post URL, `utm_source`/`utm_campaign`/`utm_content=asset_id`, mobile destination, rights in TASK-008 | UNVERIFIED | Grok / Praxxis |
| Free official checklist → original detailed guide | Article #7/#20 exceptions, source-ID conflicts, missing native build and qualified review | Run full validate/build and independent checks; leave official guidance free, preserve original reading depth | HARD HOLD | Preparedness / QA |
| Free guide → optional Legacy Triage | Product mismatch, commercial authorization and privacy unknown | Read original PDF, evaluate rights, clear account-access advice and accurate estate-not-disaster disclaimer before even drafting paid placement | NOT APPROVED | Founder / Commerce |
| Eligible paid product → completed purchase | Merchant checkout, mobile readability, fulfillment, refunds unverified | Authorized end-to-end payment and file delivery QA, clear price/tax/refund/disclosure; no unapproved transactions | NOT TESTED | Commerce |
| Sessions → actual net revenue | Paid orders, fees, refunds, qualified-human denominator not joined | Seven- and 30-day order-level reconciliation (merchant-confirmed purchases only), net revenue per 1,000 qualified sessions with tiny-N warning | NOT COMPUTABLE | Analytics / Commerce |

Measurement definitions: `qualified_human_sessions → landing → relevant CTA click → provider-confirmed optional lead → merchant-settled order / confirmed affiliate sale → refunds/fees → realized net`. Clicks, downloads, signup URL success, checkout starts and followers are *not* purchases. No new scripts, public CTAs, products, emails or paid services authorized.

## Re-run acceptance

From a trusted complete repo checkout at this branch (once available): verify exact branch heads, isolated Python suite plus >=36 tests, source/citation native validator, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness`, examine both build directories and resulting audit JSON, then independent human source/safety and QD sign-off. **Do not equate a validator DRAFT_HARD_HOLD result or exact-byte parity with a publication PASS.**
