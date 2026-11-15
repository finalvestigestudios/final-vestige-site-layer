# R380 — Original 35-article link grammar and historical safety-label custody

**2026-11-14 PT · #136 · #820 · #818 · DRAFT / HARD HOLD · NO PUBLICATION**

## Source-provenance finding — actual original GitHub blobs, not fixture claims

Read R374 Git-object manifest `5e7d9a8972872c82b4bc46ac13aab18883d8149a`, original taxonomy `15c547bb3018ac182b12a51036389cfa39a59168`, and the 35 representative original body + 35 corresponding metadata Git blobs by their manifest SHA. These representative reads use the manifest's *last listed* variant for each path **only as a read-only diagnostic**, not as a decision that any Shelter version should be merged or published. Seven Claude branches and two Shelter successors were independently compared to R374 pinned heads: **9/9 identical, ahead=behind=0**. The nine unresolved source-object conflicts remain unselected.

- **Actual native internal-link grammar** is `{{link:slug|Readable label}}` in original `preparedness/tools/build.py` (Git blob `349173d1e1d735eade218d95c7a0a2649c8cccd9`). R379 incorrectly scanned `{{link:slug}}` and thus silently returned zero crosslink tokens for authentic bodies.
- **138 native internal-link tokens** were identified across the 35 representative original article bodies; each destination slug was present in the authenticated taxonomy's 35-article slate or nine private/held tools. This is an authenticated remote source inspection, **not** a successful native build, a live-link/mobile test, or proof a private tool is available.
- The 35 corresponding original representative metadata snapshots are **all publish=draft**, but their *historical* `safety_review.state` is **29 pending / 2 approved / 4 not-required**. R379 previously asserted *all* originals were pending. The two authentic founder-labeled approvals are `making-water-safer` and `salt-beef-salt-pork-age-of-sail`, dated 2026-10-29. These labels must remain visible **without being elevated to independent source, emergency, medical, child-privacy, QD or release approval**. The four historically `not-required` articles are `navigation-before-gps`, `pioneer-supply-chains-failed`, `root-cellars-cool-storage` and `sanitation-before-germ-theory`.
- **Original source-use parity gap:** `homemade-water-filters` BODY Git blob `67aa44e9a332f57fb70298a3867410d8f66c8c15` contains a `{{cite:cdc-find-clean-water}}` token absent from its companion META `source_use` (blob `33789d3db0ec06007deb50d0293361f07cea27ae`). This is **missing article-specific reading-scope evidence**, not proof the citation URL is broken, nor permission to silently add text. A human must reconcile the exact claim, reading scope and source fragment before a safe candidate export.
- The previous five semantically divergent source-ID groups, 17 shared-source-URL groups, nine Shelter object forks, Tool #104 physical/child privacy gates and Article #11 food-safety dispute remain unadjudicated. Shared citation URLs are not, by themselves, duplicate canonical article URLs.

## R380 engineering delta (isolated, nondestructive)

Modify only R379's audit tool and its synthetic test, plus a new adversarial R380 suite, stacked on exact R379 commit `e8887026be01ab52f0a7ba396ef3fe5a9fdeb432`:

1. Parse real `{{link:slug|label}}` syntax, reject malformed/unrecognized tokens and unresolved article/tool targets, and count private tool links separately without claiming availability or adding public navigation.
2. Cross-check exactly the 35 article slugs and existing private tool slugs against source-pinned taxonomy. It does not make tools publicly available or promote links to paid CTAs.
3. Preserve historical safety labels and require a named/date-stamped record for existing `approved` labels, while consistently stating **independent QD is not granted**; no author/field is auto-selected, changed or approved.
4. Retain exact original body/meta/fragment Git-object SHA custody, source-use parity, canonical URL uniqueness and minimum reading-depth warnings.
5. CLI still returns **exit 2** even if source-custody checks have no error.

**Locally executed tests:** 115/115 PASS (=60 updated inherited R379 tests +55 new R380 adversarial tests, including 35 per-article broken-link injections). Python `-W error` compileall PASS. Source/test file blobs must match the local tested hashes before reviewer acceptance. The real native validate/build and 50 WordPress + 50 private-preview pairs remain **NOT EXECUTED** because complete authenticated git checkout cannot be obtained from this local environment (GitHub DNS lookup failure). The remote original read-only inspection is evidence of particular source facts, not an executable native integration proof.

## Conversion-first decision matrix — no commercial success inferred

| Offer → funnel step | Blocker | Change / proposed acceptance experiment | Evidence | Owner |
|---|---|---|---|---|
| ONE genuinely FV-owned, rights-cleared Preparedness pack → paid order | No verified payable and deliverable active SKU, refunds or rights manifest | Founder verifies exact seller, SKU, checkout, delivery, refunds and entitlement before any proposed paid CTA | No confirmed paid SKU; HOLD | Founder / Commerce |
| Existing official-resource family preparedness guide → free archive visit | Actual published family-emergency-contact Grok post asset ID + factual hook + permitted mobile destination not independently matched | Praxxis audits existing post and destination, with Grok asset owner; preserve existing TASK-008 queue | `asset_id` UNVERIFIED; no UTM claim | Grok / Praxxis |
| Free guide → optional Tool #104 card | Child privacy, physical cutout and emergency-source review unresolved; original internal links to private tools are not proof of availability | Keep tool links as review-only; require independent QD and actual print/mobile testing before any tool CTA | HARD HOLD | Preparedness / QD |
| Relevant CTA → verified paid order → realized net revenue per 1,000 qualified human sessions | No consented attribution/cohorts or merchant receipts, fees and refunds | Claude/Commerce validate event definitions and verified merchant outcomes, not clicks as purchases | NOT COMPUTABLE | Claude / Commerce |

Potential **unposted free-only CTA**: “Start With Trusted Preparedness Resources” → existing `https://finalvestige.com/preparedness/`. Do not introduce a retired water freebie, unapproved paid offer, affiliate/tracking script, deceptive urgency, new product or unsupported healthcare claim. Cross-reference #136, #820, #818 and the existing Grok/Praxxis TASK-008 handoff **without modifying the creator queue**.

**Release governance:** no merges, production WordPress/CMS or navigation writes, site analytics changes, merchant changes, paid spending, emails, social posts, independent approval assertions or public publishing. BUILT/TESTED = local source gate + synthetic tests; LIVE = no; VERIFIED SAFE / PAID = no.
