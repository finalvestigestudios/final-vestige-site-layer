# R146 — Current-HEAD source integrity HOLD

**Preparedness Archive #136; cross-reference conversion #820 and business charter #818. DRAFT/HOLD.** This PR adds three review files only. No article/source/taxonomy/CMS/navigation/homepage/analytics/commerce/social changes.

## Integrity gap found and addressed

R145 checks the 80 original protected source and article Git blobs at the **frozen R144 commit**, while allowing a later HEAD descending from that commit. Its optional native runner uses the later HEAD. Thus a later original-article/source edit could pass R145's historical custody test without checking the current HEAD's version. This is a **possible coverage gap**, not evidence the articles have actually changed.

R146 independently verifies the **current HEAD** and refuses changed evidence or other files. It requires an explicit exact 40-character expected SHA, the frozen R145 parent cdc12532be2e5aed3addba914110a620bae583cc, and exact immutable R133 lock blob 3eead06268a9a69eeb3130dcdcc8588bd95e980c. It rechecks the 80 frozen original objects at current HEAD (35 HTML bodies, 35 metadata, 10 other original evidence/source/taxonomy objects), 35 unique body/metadata pairings and the historical 2,000-citation expectation. It uses NUL-separated Git diff over the **whole repository**, requiring exactly the three new review files; no changes or deletions anywhere. It checks Git modes to block symlinks/gitlinks and altered object identities, and rejects dirty/untracked checkouts or moving HEAD.

An integrity pass says CURRENT_HEAD_CUSTODY_PASS_RELEASE_HOLD. It **does not** grant medical, QD, merchant or publication approval. Optional --native delegates to R145 temporary Git-archive validation, build and full unittest suite, never CMS.

Trusted full-checkout commands:

    python -I preparedness/tools/r146_head_custody.py --repo . --expected-head EXACT_R146_HEAD
    python -I preparedness/tools/r146_head_custody.py --repo . --expected-head EXACT_R146_HEAD --native
    python -I -m unittest discover -s preparedness/tests -p 'test_r146_head_custody.py' -v

**Testing:** 150 synthetic/adversarial unit tests, including a real local 80-blob test Git repository; 80 independent altered original blobs and 35 separately missing articles. This is structural testing and not medical or editorial safety validation. Native execution against actual 35-article private repository remains blocked by unavailable full local checkout/GitHub DNS; existing Actions have failed before runner steps.

## Contributor and independent QA coordination — 2026-11-05

Seven Claude branches were compared to pinned exact SHAs through GitHub; all **IDENTICAL, zero ahead/behind**. Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Food f911ff7a655de8d81535ea86ec3d65a49ee76648; Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2; Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c.

QA PR #157 head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa provides refrigerated-medication wording for qualified review only. Wholesale older replacement loses article depth and citations. Synthetic-fixture PR #169 head e9cd7766dac59d47ab467d8945269b9146c2aef5 still writes into a shared test tree; follow-up #973 head 4d40996a559b0124d74a9bb3bdcd481ad1992aa8 has proposed isolation correction. Homepage PR #49 10495883299d53596992c26a8987f629b2904670 and #604 bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 remain other agents' work. No merges or edits to their lanes. The 32 shared-source groups, Historical Food eight jerky citation-ID retargets, high-consequence safety wording and QD remain unresolved.

## Commercial funnel and acceptance — proposed, not live

ONE intent hypothesis: parents/caregivers preparing school pickup, out-of-area contact and family reunification. Proposed existing source-backed free destination is the Household Emergency Plan (currently **DRAFT/HOLD**); the optional existing reunification printable needs mobile, privacy, accessibility, download and print QA. Emergency safety guidance remains free without gating. No retired water product.

| OFFER → STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| FV-owned paid Preparedness pack → purchase | No authenticated matching currently purchasable rights-cleared SKU, delivery/refund evidence | Read-only merchant product/rights audit BEFORE any paid CTA | HOLD; no verified product | Growth/Claude |
| Free Household Emergency Plan → reader | Source/safety/QD approvals missing | Qualified human citation/safety review, native build, staged mobile QA | DRAFT/HOLD | Preparedness/QA |
| Guide → optional private reunification printable | 360/390px keyboard/print/privacy/download untested | Stage-only accessibility and local-data test without entering real child details | NOT TESTED | Site QA |
| Grok published asset → approved article | No authenticated Preparedness asset_id, post URL, permitted UTM and destination in TASK-008 | Grok/Praxxis provide real ID/link placement, no queue/production changes | UNVERIFIED | Grok/Praxxis |
| Human-qualified sessions → paid orders → net | No merchant-confirmed orders/fees/refunds or session denominator | Reconcile consent-safe 7/30-day cohorts under #820; do not count clicks as sales | NOT COMPUTABLE | Growth/Analytics |

**Unpublished CTA draft:** “Make a family contact and pickup plan before you need it. Read the free, source-linked Household Emergency Plan; optionally print a family reunification card and keep the details on your own device.” Only promote after article qualified review and independent QD.

Staged acceptance: actual Grok asset_id and linked destination; UTM source/medium=organic_social/campaign=cluster_pilot_yyyy_mm/content=asset_id, qualified-human landing sessions, accessible relevant CTA, confirmed lead only where observed, merchant-confirmed settled payment distinct from checkout/outbound link, refunds/fees and truthful net revenue per 1,000 qualified sessions with 7/30-day tiny-sample warning. Preserve #820 analytics ownership, no duplicate tags, no paid services, deceptive claims, unapproved social posts or merchant changes.

**Release status: DRAFT/HOLD, automatic merge false, medical review required, independent QD not approved, merchant offer not verified.**
