# R223 — Authentic producer-pin recovery and executable-test repair (DRAFT / HARD HOLD)

**Owner:** Preparedness Archive integration / source and citation safety. **Issues:** #136, #820; charter #818. **Parent:** R222 draft PR #1621, immutable head `d64a442bfcc30fc70b42bd2b781fb6bca6fdfbb0`. This patch does not modify any author article, source text, metadata, taxonomy, canonical route, WordPress export, safety decision, website, navigation, CMS, email, social asset, merchant or analytics configuration.

## Independent finding and exact repair

Praxxis independent review of R222 found two **fail-closed release blockers**, not evidence of a publication bypass:

1. Frozen `sources/fragments/hist-food.json` expected `d10628342fea5f177a8d1be00ddc7a9c2003d661` (wrong); actual authentic Git blob `d10628342fea5f177a8d1be00dd906d0c9c7850e`. Frozen `hist-home.json` expected `8d85fd868508c5caba14a839d119d55f31f14f` (38 hex characters); actual `8d85fd868508c5caba14a839d119d55f31f14f72`. Corrected both by fetching the actual files from this exact GitHub head, not by adjusting to a synthetic fixture.
2. R222 test module tried loading the gate from `preparedness/tests/`, while the committed gate is in `preparedness/tools/`. Repaired the path to `HERE.parent / 'tools' / 'r222_producer_source_bundle_gate.py'`.

The R222 gate now rejects any malformed/non-40-hex frozen ID *before reading the filesystem*. The suite adds two malformed/invalid-ID negative cases and two tests outside the patched synthetic fixture: strict frozen identity grammar, and a **real-checkout 20-file comparison** that fails if original corpus inputs are absent or changed. R220's expected R222 module blob was updated to the corrected module Git identity. Existing all-HOLD semantics and all prior source checks are preserved. No approval can be returned.

## Custody evidence

All **20/20** frozen producer/source input paths were independently fetched and checked against their **actual GitHub blob SHAs** at the R223 draft head: build.py, stylesheet, source register, source crosswalk, seven fragments, nine JS files. All matched. This is a remote exact-blob audit of those 20 files, **not** execution of the actual build or source/veracity adjudication.

The exact committed Git blob for the repaired R222 gate is `bd57ef0caba7ad68381fa6a22af64aff4d486c84`; R220 is re-pinned to this value. The revised test blob is `2bd5cefac3f15f7c57d0c3979660f1ee12199dea`. A local reproduction was reconstructed byte-for-byte from connected GitHub and the blob OIDs were verified before running Python.

**Executed locally against those exact two committed blobs:**
- Python isolated compilation: PASS.
- 92/92 targeted tests PASS: 91 synthetic mutation/hold/malformed-pin tests + one non-mocked real-pin *shape/known identity* test.
- Unfiltered suite discovers **93** tests; the additional real-checkout **content** test fails closed with `missing or symlinked source bundle directory: sources/fragments` because the local runtime contains only the two reconstructed files, not the authentic repository. This is an **environment/corpus blocker**, **not** 93/93 PASS and not a safety or QD approval.
- The original repository validation/build and 35 article + 6 tool -> 41 route / 82 WordPress+preview exports remain **NOT EXECUTED**. Local GitHub DNS fails; the connected GitHub API works only for file/commit retrieval here.

Release prerequisites in a complete, trusted checkout:
```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness
```
Expected source/custody output is still **DRAFT_HARD_HOLD** when structurally valid, not QD PASS. No merging or publishing on this evidence alone.

## Contributor / independent QA coordination (2026-11-08)

All seven Claude contributor branches compared identical against original frozen heads: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. Independent QA PR #157 and fixture PR #169 were inspected separately (PR #169 has no executed full native suite). Homepage lead draft #1620 is at `d20027e1dbba058ae4f0008f8d9f1ce291c1f82d`, untouched. This PR is stacked on R222 and cannot certify inherited R219/R220/R221 assertions by itself.

**Outstanding human safety/evidence gates:** article #7 two unexplained CDC citations; article #20 one unexplained Ready.gov citation; seven historical shared-source ID conflicts; full source-by-claim review, reading-depth preservation, qualified medical/food/water/electrical safety review, and independent QD. There is also an inherited ordinary-import/cache/read-binding limitation after preflight that requires separate executable review in a complete checkout.

**Candidate live-link discrepancy to investigate, not an accepted proof:** public Archive search extraction under “Current validated preservation practices” appears to list a California Department of Public Health CO safety link instead of NCHFP/USDA food preservation sources. Confirm actual live HTML/DOM link placement and semantics before filing a source-correction release; do not silently change live content.

## ONE conversion-first, safety-preserving draft map — no activation

**Audience/topic:** households searching for an emergency contact + important document plan after a power outage, caregiving emergency or evacuation. **Existing free destination:** public `https://finalvestige.com/preparedness/` page, “Create a household emergency plan” section linking to FEMA/Ready.gov emergency checklist; the authored long-form `/preparedness/start-here/household-emergency-plan/` is **unpublished** and must **not** be used as a live campaign destination.

**Optional provisional paid candidate:** Legacy Triage `https://payhip.com/b/n1RhV` publicly lists a $19 instant-download PDF with a nine-part family-records/contacts organizer. External listing ≠ verified owner rights, seller authorization, fulfillment, refund terms, secure handling of completed account/password details, actual purchase, sales or cleared revenue. **No paid CTA activation** until founder/Commerce verification.

Proposed **draft-only** CTA copy after free primary advice, not a signup gate: “Need a place to organize contacts and document locations? An optional printable records organizer may help. First use the free FEMA checklist above. If offered here after review, the organizer is a paid digital download, not emergency advice; keep completed copies secured and don't share passwords publicly.” Do not add product name, buy button or merchant redirect before approval.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Free current FEMA checklist → agency guidance | Creator asset URL/internal `asset_id` and tappable mobile destination unverified | TASK-008: link one **existing published** Grok asset, factual hook, media rights, date and real `utm_content=asset_id`; confirm tap leads to existing public Archive | NOT VERIFIED; no invented asset or attribution | Grok / Praxxis |
| Free Archive → authored detailed guide | Author manuscript not live; source and qualified safety holds | Run full native tests, independent claim adjudication, no misleading preview route | HARD HOLD | Preparedness / QA |
| Free planning guidance → optional Legacy Triage | Rights, truthful disclosures, poor-fit/privacy risk | Founder/Commerce review actual PDF, rights, password-handling and opt-in CTA text; no false urgency | NOT APPROVED | Founder / Commerce |
| Optional pack → payment and delivery | Mobile checkout/confirmation/PDF/refunds unverified | Authorized mobile 360/390/768/1440px and keyboard test, order receipt, valid PDF, payment/refund state | NOT TESTED | Commerce |
| Qualified campaign sessions → realized net | No confirmed attributable orders/commissions, fees/refunds, qualified human denominator | 7/30-day privacy-safe ledger: session by verified `asset_id`/campaign → relevant CTA → confirmed lead if any → confirmed paid order → refunds/fees → net revenue | NOT COMPUTABLE | Analytics / Commerce |

**Primary KPI:** realized net revenue per 1,000 qualified human sessions = `1000 * (settled paid revenue - refunds - platform/processing fees) / verified qualified human sessions`; denominator must be > 0, numerator may be zero or negative. Report missing attribution and tiny samples, no conversions inferred from page views, link clicks or claimed checkouts. Do not introduce new analytics scripts, offers, coupons, social posts or merchant settings.

**Release state:** BUILT / 92 TARGETED TESTS PASS / 20 REMOTE BLOB IDENTITIES MATCH / AUTHENTIC PIPELINE NOT EXECUTED / DRAFT_HARD_HOLD. No source editorial approval, QD PASS, medical safety claim, live page, WordPress, navigation, social, email, affiliate, checkout or spending writes.
