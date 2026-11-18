# R449 — Original 35-article claim/citation occurrence custody · DRAFT / HARD HOLD

**Issue #136 only; conversion owner #820; charter #818.** This is additive and read-only. No manuscript selection, paid offer, WordPress edit, newsletter, social post, measurement script, merge or release.

## Why this engineering lift matters

R397 and R448 independently preserved the 35 article identities, 203 source IDs, 280 source occurrences, 181 literal URLs, 17 unmerged exact-URL groups, five unresolved source disputes and nine unselected forks. But those global totals did **not** prove which claim in a given original body actually carried a source citation or whether its contributor metadata declared a matching reading scope. R449 adds a per-candidate original HTML parser and a nine-original-checkout replay. For each original body/meta pairing it records contributor branch, two Git blob SHAs, visible literal `{{cite:source-id}}` occurrences, line numbers, original passage fingerprint, declared `meta.source_use` IDs and missing or undeclared source use. Original repeated-body appearances are preserved as a **multiset**, not discarded as duplicate bytes. Every original body/meta/source-fragment fork remains unselected and must match its own independent Git blob.

It rejects source IDs absent from the original R397 register, malformed citation markers, citations hidden in comments/attributes/script/template/style, suspicious entity-encoded marker input, unpublished body/meta substitutions, premature safety/publication states and forged original fork blobs. It does **not** independently establish that a cited source supports a claim, that a medical/food/emergency instruction is safe, or that an article may publish.

### One real original manuscript family verified read-only by connector, not by native R449

The existing unpublished Article #15 has **three different** original contributor candidates:

| Original branch | Body Git blob | Meta Git blob | Raw literal cite markers / unique IDs | Unknown IDs / IDs absent from source_use |
|---|---|---|---|---|
| `claude/prep-shelter-5e1e0e` | `16e2b1ec37fd6ea37f442d13e831180253c709b9` | `e63bbe70f5b93936da5cd71c030e33d82256d3ee` | 62 / 14 | 0 / 0 |
| `claude/prep-shelter-continuation` | `cbfe7830e9412ac99a1920c581a14d2913a9eaf6` | `0ad68a8c456f50912ddef11c44bfc05c3c2d3513` | 67 / 18 | 0 / 0 |
| `claude/prep-shelter-followup-evidence` | `c97a79761dc3be1c44e5f9322a606ccc7fd11c6e` | `a8618235711cca039f142ad59962c1153654aa45` | 69 / 20 | 0 / 0 |

These are direct GitHub original-file/readback counts using a literal regex, **not** an actual execution of the new gate over all original candidates. Their difference is evidence that a globally unchanged source count can hide manuscript reading-depth drift; do **not** infer that any version is qualified-safe or choose a winner. Article #15's child-contact privacy, 911 threshold, school-reunification scope and Tool #104 printing/storage still need qualified review.

## Execution and release gates

- Local **standalone full-companion** R449 implementation: Python compilation PASS, 71/71 synthetic unit tests PASS including adverse mutations; combined with R448 existing local module 132/132 PASS. The local companion is in the R449 downloadable engineering package and **is not the same file as the shortened committed PR implementation**. Therefore no claim of an exact committed R449 Python test execution is made.
- The committed PR includes a newly written per-candidate gate and its own 49 discoverable synthetic test methods. These committed files must be run in an authenticated checkout and checked in CI before describing them as tested. Green tests alone cannot grant QD, publication or commerce authorization.
- Native `preparedness/tools/validate.py` and `build.py` attempted locally: both exited 2 because the full original source checkout is not mounted here. Genuine 35 original bodies + nine original head roots, native build, 70 real WordPress/private-preview exports, browser/print/mobile checks, independently reviewed citation reading depth and emergency/medical/food/child-privacy QD: **NOT RUN / NOT APPROVED**.
- R449 CLI always returns `2 / DRAFT_HARD_HOLD`, including on structurally good input. Never transform an exit-2 hold into a green QD claim. Full original R397 docket Git blob: `86d22a1d504c93db7689b914e2202a7845b648e2`; R446 review packet Git blob `0e655316ced77212abeff77459898253a1e768fd`.
- Check exact current heads every time. This run found all nine Claude/Shelter branch heads identical to the frozen R397 pins (0 ahead / 0 behind). QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, independent food fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, separate repair #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, home #2931 `c43980270e3e9d31c03fcb70e0f1126914c58604`, and editorial #2789 **moved** to `e9fb12fbe80fcced17fabf3337be76a9e29ab75f`; none modified.

Run after obtaining **nine independently verified, unmodified original branch checkout roots** as `roots.json`, current GitHub `heads.json`, and the authentic original docket/packet:

```sh
python -I preparedness/tools/r449_original_citation_incidence_gate.py \
 --docket preparedness/reviews/r397_original_source_fork_docket.json \
 --packet preparedness/reviews/R446_AUTHENTIC_R397_CONFLICT_REVIEW_QUEUE.json \
 --observed-heads /independent/heads.json --roots /independent/roots.json \
 --output /private/r449-claim-incidence-hold.json
python -I -m unittest discover -s preparedness/tests -p 'test_r449_original_citation_incidence_gate.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
```

## Strictly prioritized commercial acceptance, not activation

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE → OWNER |
|---|---|---|---|
| One **genuine existing FV-owned** rights-cleared Preparedness pack → verified paid checkout | No authenticated FV-owned seller/SKU, licensed/deliverable download, refund/fee evidence | Founder/Commerce privately verifies real product ownership, mobile payment, fulfillment and refund terms *before* paid CTA | **HOLD**, no merchant-confirmed order. Founder/Commerce |
| Already published Grok family-contact/reunification asset → official free guide | Real immutable post `asset_id`, rights, narrated hook and mobile route unverified | Praxxis independently verifies one **existing** intent-matched post only; free original source candidate is official `https://www.ready.gov/plan`, original reference not fresh HTTP/browser proof | **UNMATCHED**. Grok/Praxxis |
| Source-backed free guide → optional Tool #104 | Child privacy, Article #15 source/911 scope, printable accessibility, separate Tool #102 identity | Qualified private safety/print/browser review without gating essential free guidance | **HARD HOLD**. Preparedness/QD |
| Qualified-human campaign visits → relevant CTA → confirmed lead where applicable → settled order → refunds/fees → net proceeds | No verified attribution, settlements, fees or trusted 7/30-day cohort | Claude tests **existing** consent-compliant measurement (no duplicate scripts); distinguish outbound click/checkout/email from confirmed paid conversion | **NOT COMPUTABLE**. Claude/Commerce |

Proposed **unpublished** free CTA: “Review the official household emergency checklist.” Net revenue per 1,000 qualified humans is only computable using independently confirmed settled paid gross minus refunds and fees divided by qualified-human sessions; no substitute pageview or click counts. No retired water freebies or unapproved products. Founder retains commercial/release/spend authorization; Grok owns all production and posting; Praxxis independently checks existing social assets; Claude owns website and analytics.
