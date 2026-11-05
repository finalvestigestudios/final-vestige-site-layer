# R145 — 12-PR chain, original-source custody, isolated-native preflight

**ISSUE #136; cross-links #820 and #818. DRAFT / HOLD.** No merge, public publishing, WordPress/CMS, homepage, navigation, analytics, payment, affiliate, email, Grok queue, or spending.

## Authenticated GitHub evidence (2026-11-05)

All twelve open Preparedness draft PRs were inspected at their actual head/base SHAs, with full per-PR changed-file inventories: #1025, #1031, #1037, #1043, #1049, #1057, #1063, #1069, #1076, #1083, #1090, #1096. Their bases match their immediate predecessors. GitHub's cumulative compare from R132 anchor 5685b54796d520e8dd50e0cdf4d35e38c9cec7a4 through R144 head ee0dcc6e3ad7a3c63a52b1327b99310d3e7e4edc shows **53 commits, 41 additions, 0 modifications/deletions/renames**, all under Preparedness docs/tools/tests. Thus this *review stack* has not modified original article bodies, metadata, source registers, taxonomy, route data or public site content. The comparison is not a full native test result or a source-safety clearance.

The seven Claude branch heads were independently compared to their immutable pins: **7/7 identical**. QA #157, food-fixture #169, follow-up #973 and homepage #49/#604 were inspected, remain separate and were not modified. The eight Historical Food jerky citation-ID substitutions, high-consequence QA wording and 32 shared-source groups remain human-review HOLD.

## Engineering

**Frozen stack manifest:** preparedness/docs/r145/r145_stack_manifest.json pins every PR's parent/head SHA and added path; seven contributors; independent fixture/QA and homepage references; 35 articles / 2,000 citations; denial of any approval or automatic merge.

**New offline verifier:** preparedness/tools/r145_chain_integrity.py validates exact Git ancestry and each addition-only diff, then checks the original R133 immutable-lock Git blob, all **80 pinned source/article/meta/taxonomy Git object identities**, **35 original draft articles and 35 metadata**, distinct slugs, article-specific source-use and the 2,000 citation occurrences. Rejects loss, modification, renames, duplicate slugs, changed approvals and missing evidence. An integrity pass is always **DRAFT_HOLD; publication_allowed=false; independent_qd=NOT_APPROVED**.

**Optional --native** runs *only after custody verification*, using a temporary Preparedness-only Git archive. Executes isolated Python validation, build and full Preparedness unittest discovery; captures statuses and stops on failure, without WordPress or original source writes. The build artifact is a **draft**, never an automatic release.

Run from an authenticated checkout containing the stacked review commits:

    python -I preparedness/tools/r145_chain_integrity.py --manifest preparedness/docs/r145/r145_stack_manifest.json --repo . --native

**Execution evidence:** 185/185 isolated adversarial Python unittest cases PASS, Python compilation PASS. Committed tool/test/manifest blobs match local tested bytes. Complete native validate/build/full corpus and independent browser/QD have **NOT** executed: available runtime lacks the trusted full checkout; direct GitHub DNS resolution fails. CLI on the available runtime correctly returns exit 2 / HOLD. Repeated hosted Actions failures before any runner step are not Python failures or passes; no budget-consuming rerun is authorized. No claim that advice is medically safe.

## Conversion-first Preparedness funnel — proposed only

**One audience hypothesis:** parents/caregivers planning school pickup, out-of-area contacts and household reunification. Proposed already-authentic free guide: *Household Emergency Plan*, still unreviewed **DRAFT/HOLD**. Optional existing family-reunification printable remains delivery/privacy/mobile/printing **NOT TESTED**. Core emergency information stays freely accessible; do not revive retired water freebies.

**ONE paid Preparedness SKU required before launch:** No matching FV-owned, rights-cleared, currently purchasable product has been independently authenticated, nor merchant price, fulfillment, refund policy or buyer entitlement. Therefore **NO paid CTA or checkout link may be rendered**. Grok/Praxxis TASK-008 does not yet authenticate a Preparedness social asset ID, real post URL, placement or approved destination.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing paid Preparedness pack → verified purchase | Authentic SKU, rights, pricing, checkout, file delivery, refund proof unavailable | Read-only merchant/rights verification; staged complete checkout only after approval | HOLD / NO VERIFIED MATCH | Growth / Claude |
| Free Household Emergency Plan → qualified reader | 32 author-source groups and medicine, fire, food, CO and evacuation claims not adjudicated | Preserve full depth and original citations; qualified review, native QA and independent QD | DRAFT / NOT RELEASED | Preparedness / QA |
| Guide → optional reunification printable | 360/390px mobile, keyboard, print, privacy and delivery untested | Stage accessibility/download/print and local-only storage | NOT TESTED | Site QA |
| Actual Grok social asset → guide | Missing published asset_id, post URL, approved destination/link mode | Grok/Praxxis confirm TASK-008 identifiers and platform-permitted UTM route; no posts or queue changes | UNVERIFIED | Grok / Praxxis |
| Confirmed order → net revenue per 1,000 qualified sessions | Paid order/refund/fee evidence and qualified-human denominator missing | Existing #820 analytics; reconcile actual 7/30-day cohorts, disclaim small sample | NOT COMPUTABLE | Growth / Analytics |

**Draft CTA, not deployed:** “Need a family contact and pickup plan? Read the free source-linked Household Emergency Plan. You can optionally print a reunification card and keep your information private.”

No false checkout, affiliate sale, subscriber attribution, clinical safety, QD approval, Grok post or revenue claim. Preserve founder-controlled release governance and all 35 instructional articles as **DRAFT/HOLD**.
