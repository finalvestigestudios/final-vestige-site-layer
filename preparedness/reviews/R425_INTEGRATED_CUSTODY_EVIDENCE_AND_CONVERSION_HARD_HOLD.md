# R425 — Integrated 35-article original-source / paired-draft / campaign custody

**Status: DRAFT / HARD HOLD. Issue #136; conversion acceptance #820; charter #818.**
**Scope:** Additive read-only Preparedness integration validator and synthetic tests. No article/citation/source/taxonomy/route edits, no CMS or customer information, no commercial activation.

## The gap R425 addresses

R409–R420's article/source/export gates and R421–R424's campaign/merchant evidence gates were previously run and reported independently. A set of individually plausible results did **not** establish that the same exact 35 originals, all unselected forks, all 70 WordPress/preview export bytes, article routes and source-ID arrays had been locked **as one reviewed bundle**. A campaign receipt could be discussed separately from the actual source/export inventory. R425 adds a single read-only integration gate and exact-content SHA-256 review lock.

## Contract and private inputs

`python -I preparedness/tools/r425_integrated_custody_gate.py ORIGINAL_DOCKET.json MANIFEST.json EXPORT_ROOT PRIVATE_CANDIDATE_ROOT EVIDENCE_LOCK.json CAMPAIGN_RECEIPT.json`

- ORIGINAL_DOCKET is pinned to Git blob `86d22a1d504c93db7689b914e2202a7845b648e2` (R397 unselected original graph), not a generated substitute.
- MANIFEST is R410's 35-item internal review manifest; no public route writes.
- EXPORT_ROOT has **only** `wordpress/<slug>.html` and `preview/<slug>.html` for each of the 35 original slugs.
- PRIVATE_CANDIDATE_ROOT has exactly `<slug>/<original_git_blob>.txt` for every original manuscript candidate, **including all unresolved Shelter forks**. Original inputs remain private and uncommitted.
- EVIDENCE_LOCK is a review-created JSON object with exactly `schema:1`, `issue:136`, `release_state:DRAFT_HARD_HOLD`, `approved:false`, `original_docket_git_blob` and `articles`. Each article row has `slug`, `canonical_path`, **ordered** `source_ids`, sorted `original_git_blobs`, `wordpress_sha256` and `preview_sha256`. Never manufacture hashes for absent authentic files.
- CAMPAIGN_RECEIPT follows R421–R424's existing read-only, unattributed default shape. The current real commercial receipt remains unmatched/unverified; hashes can never authenticate purchases.

The gate rejects malformed or duplicate identities, absent/extra originals, loss or selection of a manuscript fork, source-order divergence, duplicate/drifted routes, one-channel swaps, changed bytes even if both exports look alike, unexpected files, path escapes, symlinks, unsafe JSON and premature approval flags. It calls the inherited R420 (which recursively checks R409–R419 source/citation/claim/attribute custody), then R424 (which invokes R421–R423 funnel identity and privacy checks). The output explicitly separates source and campaign results, uses a deterministic review-only digest, and **always exits 2, never permits publishing or paid activation**.

## Verification limits and unblocked progress

Local source-derived Python suite: **58/58 new synthetic adversarial regression tests PASS** (35-article/70-channel fixture; one Article #15 original fork; numerous mutations). Independent inherited module re-runs against available assembled code: R409 66/66, R410 77/77, R420 58/58, R421 74/74, R422 79/79, R423 90/90, R424 62/62: **564 passing tests in eight separate runs**, **not a full native site suite and not CI**. This checkout's remote new source/test bytes must be executed by a trusted runner before claiming an exact remote-commit PASS; local construction and pushed Git blob bytes are not assumed identical.

**Missing:** Authentic complete 35-article original Git body bytes, 70 genuine paired WordPress/private exports, reviewer-authored SHA lock, native repository tools/build, independent source-to-claim/food/emergency/privacy QD adjudication, and a confirmed payable/deliverable Preparedness SKU. The release cannot progress from this synthetic-only evidence. No false QD PASS.

## Exact unchanged dependencies to re-check

- Seven Claude producer refs: start `2122d856`, food `f911ff7a`, health `d5ef5baf`, hist-field `4e5caf81`, hist-food `67e116e5`, hist-home `7504a5f0`, shelter `5daeaf2d`. Shelter descendants `ac8625fa`, `6a5998ea`. All 9 identical to their original pins as independently compared 2026-11-16 PT.
- Independent QA #157 `7d1ae6b8` (drill electricity / medication / status gating); fixture #169 `e9cd7766` (test-only yet canonical-source fixture mutation still under discussion), dependent correction #2205 `bbcf1859` not merged; home #1689 `f55c36b6` unchanged. Do not modify any of these workstreams.
- Original inventory preserved by custody only: 35 articles, 203 distinct source IDs, 280 occurrences, 17 exact shared-URL review groups, 5 source-scope disputes and 9 unresolved forks. They are **not newly adjudicated**.

## Highest-priority conversion contract — no invented outcome

**OFFER:** One *actually current*, FV-owned/licensed, rights-cleared, payable and fulfillable Preparedness pack remains **UNAUTHENTICATED** → **FUNNEL STEP:** one genuine already-published Grok family-contact/reunification asset to the existing agency-linked free `https://finalvestige.com/preparedness/` → **BLOCKER:** no authenticated matched native post, asset ID or approved SKU; Article #15 / optional Tool #104 remains private, emergency and child-privacy **HOLD** → **CHANGE:** keep free-only CTA **"Start With Trusted Preparedness Resources"** as draft and require Grok/Praxxis asset rights/hook/mobile UTM review, founder/commerce seller/checkout/delivery/refund verification, and Preparedness QD/source signoff → **PASS/FAIL EVIDENCE:** local synthetic structure only; no published CTA, no verified lead, orders, affiliate settlements or net revenue → **OWNERS:** Grok social creator, Praxxis independent asset QA, Preparedness/QD source review, Claude core site/analytics, founder commerce/release/spend.

No retired water offer, Tool #102 substitution, paid upsell, social post, email, live page or tracking scripts. Core safety instructions remain free; commercial events never stand in for confirmed customer payments. 7/30-day revenue per 1,000 *qualified human sessions* is **NOT COMPUTABLE** without merchant-proven orders, refunds, fees and attribution.

**Release posture:** DRAFT / HARD HOLD, no merge, no site changes, no publisher action, no false QD PASS.
