# R351 — Builder-derived canonical URL integrity (DRAFT / HARD HOLD)

**2026-11-13 PT · Issue #136 · conversion coordination #820 / charter #818.**
Never merge, publish, create CMS drafts, alter navigation, modify public pages, change product status, send messages, or declare qualified source/safety/QD PASS from this work.

## The source custody gap this closes

R350's metadata-only route check correctly reports `URL_NOT_AUTHENTICATED` when original article metadata omits an explicit `canonical_url`. **Omission does not mean the builder has no route.** The actual inherited `preparedness/tools/build.py` computes `Library.url_path(slug)` as `taxonomy.base_path + article.section + '/' + slug + '/'`. R351 reads the exact AST of that function **and** `section_path`, then derives the identity of every proposed route without running or trusting arbitrary builder code.

The current integrated builder Git blob is `349173d1e1d735eade218d95c7a0a2649c8cccd9`. Native integrated acceptance requires that exact blob and full 35 article + six tool inventory. This is deliberately a *pinned* contract: a legitimate later builder change requires fresh review and pin update rather than silent green results.

## Safe implementation, without content or CMS mutation

- A read-only Git-object lane checks the exact original seven Claude cluster heads and two Shelter descendants pinned in the R350 source-custody module; rejects changed or missing SHA, metadata/body pairing gaps, nonregular objects, unexpected filename/slug and absent complete checkout.
- Derives proposed routes; crosschecks article-to-taxonomy section, case-sensitive and percent-decoded normalized path identities, duplicate document IDs, unexpected or omitted documents, shared tool/article slug overwrites, invalid section/slug, drift across branch variants, and contradictory explicit canonical/permalink/URL fields.
- URL values are SHA-256 fingerprints in the review output. No private body text or customer/event data is exported. The audit does not attempt to prove WordPress actually serves those URLs.
- All existing drafted/pending/not-required safety constraints are preserved. Neither a source checked date nor a structurally good route implies safety, rights, permission, or valid paid conversion.
- Runs under `python -I` with isolated sibling import. Always returns exit code **2** as an explicit publication hard hold; a structurally consistent route roster is only `DRAFT_ROUTE_PARITY_ONLY_HARD_HOLD`.

## Verification, exactly classified

| Evidence | Result |
|---|---|
| Committed R351 implementation blob | `aaac2009bea3bfa1ecb0562d03f26c2d468819ec` |
| Committed R351 test blob | `0a7d211818ac598851fa27533359134c6eaa6099` |
| Inherited R350 implementation blob | `4f3446a907b4c53c3ea33773d8f2c25cd512c94a` |
| 93 R351 exact-code standalone tests | **PASS** |
| 68 inherited R350 standalone tests | **PASS** |
| Combined isolated test executions | **161/161 PASS** |
| Python compilation | **PASS** |
| Isolated mode missing native checkout | **INVALID_HARD_HOLD, exit 2** (expected) |
| Authenticated full checkout, native validate/build, 100 WordPress/preview outputs | **NOT EXECUTED** |
| Hosted CI, actual live route verification, mobile/print acceptance | **NOT VERIFIED** |
| Human safety/privacy/source claims and qualified QD | **NOT APPROVED** |

Tests and source blobs were compared with actual committed Git identities. The 161 tests are **synthetic/isolated only**, not a full repository build or independent editorial approval. Source checked dates and HTTPS links cannot replace individual claim-level support checks.

## Independent QA and unresolved source holds

- Independent QA PR #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`: open draft, no QD approval.
- Synthetic fixture QA PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`: open draft; one canonical duplicate-source test still writes inside the checkout.
- Remediation PR #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a`: open dependent draft against #169; unmerged.
- Home lead PR #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`: open draft, untouched.
- Original **15 editorial conflicts**, **17 Article #15 / Tool #104 child-privacy/emergency reviews**, **four competing source identifiers** and **17 disputed in-body citation occurrences** remain unresolved. The 17 occurrences are not the same category as the 17 safety obligations.

## Conversion-first acceptance: one intent, not a fictitious product

| Offer | Funnel step | Blocker | Required change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| ONE existing rights-cleared FV Preparedness practical pack | Verified checkout → paid order → usable delivery | No genuinely purchasable matching pack authenticated | Verify active seller SKU, intellectual-property rights, purchase, fulfillment, refunds, taxes/fees as applicable; **no activation now** | HOLD; no paid order/rights evidence | Founder/Commerce |
| Free source-backed Preparedness Archive | Official resources → optional detailed guide / tool | Article #15 / Tool #104 safety, privacy, citations and print checks | Preserve freely accessible authoritative links; qualified claim-level review before linking private guide/tool | HARD HOLD on originals | Preparedness + QD |
| Grok family-contact/reunification social asset | Published asset_id + UTM → mobile Archive landing | No authenticated exact published asset_id/URL/topic handoff | Grok/Praxxis verify actual post and platform-permitted mobile link in TASK-008; don't edit creator queue | UNVERIFIED | Grok/Praxxis |
| Existing opt-in, where relevant | Landing → contextual CTA → confirmed lead | No evidence of consent, actual signup confirmation or email delivery for this path | Use existing consented Focus mechanism; inspect production behavior read-only first | NOT TESTED | Claude/Commerce |
| Merchant-confirmed settlement | Qualified human sessions → confirmed orders → refunds and fees → realized net revenue | Merchant receipts and attributable human cohorts missing | Deduplicate 7/30-day cohorts, separate affiliate outbound clicks from paid affiliate reports; flag tiny samples | NOT COMPUTABLE | Claude/Commerce |

**Candidate draft free CTA**: “Start With Trusted Preparedness Resources” → existing public `https://finalvestige.com/preparedness/`. Do not deploy or imply detailed original guides/tools are public. Retired water downloads stay retired. No paid offer link, social post, email, analytics script, merchant write or purchase is created.

## Next executable gate

On an authenticated complete nine-ref checkout, run `python -I preparedness/tools/r351_canonical_route_gate.py --repo-root .` (exit 2 is intentional); run native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and `python -I -m unittest discover -s preparedness/tests -v`, then compare **all 50 WordPress + 50 preview private draft exports** and inspect canonical links/anchors against actual builder records. Any disagreement remains a hard hold; no silent cherry-pick or publish. Founder retains release/spending authority, Claude core-site engineering, Grok posts, Praxxis social QA.
