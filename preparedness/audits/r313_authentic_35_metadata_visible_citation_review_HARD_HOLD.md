# R313 — Authenticated metadata state + visible citation custody audit (HARD HOLD)

**Scope:** Preparedness Archive only; Issue #136, conversion coordination #820. Read-only source examination, no publish/merge/navigation/CMS/social/merchant/analytics writes. No independent safety or QD approval.

## Real-source result, 2026-11-12

GitHub connector fetched the actual `preparedness/audits/r306_live_lineage_35_articles_HARD_HOLD.json`, the pinned `preparedness/taxonomy.json` and **all 35 original article metadata JSON files** from the R312 baseline (head `6526b7934c4965cffc77a943d7c4eea0cb5cab41`). Each of the 35 live metadata Git blobs matches the `integrated_meta_blob` recorded for that slug in the R306 authenticated ledger. Each `status` remains `{"editorial":"drafted","publish":"draft"}`, and each `section` and `track` matches taxonomy.

| Authentic metadata state | Number | Finding |
|---|---:|---|
| `pending` | 29 | Unapproved; no claim-level review established |
| `not-required` | 4 | All four taxonomy `gate=false`, not a safety certificate |
| `approved` | **2** | Both taxonomy `gate=true`; independent safety/QD **not** established |
| **Total** | **35** | Exact Git identities, not a complete 41-export build |

**Two specific blockers requiring editorial adjudication:**

- `making-water-safer.meta.json`, exact Git blob `827d861eb3beebfd010ee98fcca764b23a2de90e`: `safety_review.state="approved"`, taxonomy `gate=true`. The metadata itself says the Oct 29 approval was an ambiguous founder chat reply, not qualified claim-level safety verification, and specifically says **review NOT COMPLETE until founder confirms scope**. Do not represent this as verified safe.
- `salt-beef-salt-pork-age-of-sail.meta.json`, exact Git blob `1c4c5396da703f3724b584c67e49e2128ab1f4c6`: same `approved` mismatch against a qualified review requirement. Metadata explicitly says historical primary records are not all pulled; no independent factual or safety review and no QD.

The four `not-required` records are `root-cellars-cool-storage`, `navigation-before-gps`, `sanitation-before-germ-theory` and `pioneer-supply-chains-failed`; all are ungated in the authentic taxonomy. All remaining records are pending. This audit does **not** prove the truth, freshness, rights or safety of a single claim.

## Engineering change

R313 is additive on exact R312 predecessor Git blob `2ae6f2a8532c33c15e925166479e52f662b3f39f`. It uses a read-only HTML parse to distinguish **visible article-body citation occurrences** from source IDs hidden in HTML comments, attributes, templates, script/style, visually hidden or inaccessible content. It checks editorial state, taxonomy safety-gate parity, section/track identity, duplicate JSON metadata keys and exact input blob custody. It inherits R312/R311/R310 error gates, does not mutate the 35 article bodies, and always returns `publication_authorized=false`, `medical_safety_verified=false`, `independent_qd_pass=false`.

The local exact-committed-scope package passed **297 Python tests** (74 new R313 + 223 inherited R310–R312), Python compilation and an incomplete-native-checkout fail-closed negative control. This is **not** execution of the complete authenticated native build or 41 WordPress exports; no release approval follows from test success.

## Current upstream comparison and independent review

All seven canonical Claude contributor refs compare **identical (0 ahead / 0 behind)** to the R306 pinned R200 cluster SHAs, checked this run. Two later Shelter descendant branches remain separate and unadjudicated. PR #157 is open/draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. PR #169 is open/draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its diff corrects one temporary-file test but retains a separate test that writes `_dup_test.json` beneath real `ROOT/sources/fragments`. Homepage lead PR #1689 open/draft at `f55c36b6598eec558dd8bb24e4c8988becc51be0`; untouched. R312 baseline #2172 HEAD `6526b7934c4965cffc77a943d7c4eea0cb5cab41`.

## Release and business holds — offer → funnel step → blocker → acceptance → evidence owner

| Offer / funnel step | Blocker and change/experiment | Pass/fail evidence / owner |
|---|---|---|
| Authentic Grok family-contact social asset → existing free Preparedness Archive | Published asset ID / mobile-permitted URL not confirmed. Research-only candidate is `/preparedness/`, not the unpublished detailed guide | **NOT VERIFIED**; Grok/Praxxis TASK-008 |
| Free official-source index → optional free Tool #104 family reunification card | Distinct Tool #102 and #104 identities must be preserved; qualified emergency wording, child privacy, print, no-JavaScript, accessibility and real exported link tests required | **HARD HOLD**; Preparedness/QD |
| Free resources → optional **existing** paid practical pack | No verified rights-cleared, currently purchasable, clearly relevant FV Preparedness SKU, delivery proof or refunds. Do not substitute speculative/retired offers or publish paid CTA | **NO APPROVED SKU**; Founder/Commerce |
| Qualified human sessions → CTA → confirmed lead → merchant-confirmed paid sale → refunds/fees → realized net revenue | Missing authenticated `utm_content=asset_id`, consent-safe event chain and merchant settlements. 7/30-day tiny sample disclosure required | **NOT COMPUTABLE**; Claude/Commerce |

**Draft free-resource CTA (not published):** “Build a plan for how your household will reconnect. Start with free, cited official resources.” Must be placed only on an actually reviewed destination; no forced email gate for safety guidance. Checkout CTA deferred until a SKU is authenticated.

## Remaining hard holds

Native complete checkout/build plus all **41** actual WordPress draft exports; ten substantive article-body changes and twelve metadata differences; duplicate USDA `fsis-power-failure` fetch records; two contributor-local tool-number collisions; Article #7 hazardous-water guidance; Article #15 / Tool #104 emergency messaging, privacy, print, accessibility and disabled-JS testing; independent qualified source/safety and QD. Never claim passing synthetic tests equal a safety approval, an implemented funnel, a live page or commercial conversion.

**No public release or commercial action authorized.**