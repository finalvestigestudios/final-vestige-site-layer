# Apollo R425 — Immutable Research Desk source bootstrap

**Draft only · Production HARD HOLD.** This isolated QA utility resolves the R424 source retrieval gap; it does not satisfy real WordPress/browser accessibility/performance gates.

Four immutable file blobs are pinned to original Research Desk PR #158 commit `250d7f05a4de037e73826dcf0cfaef0ec4c29383`; two are pinned to R423 commit `93dda51158453fbc8e2fcc353ef535490eac0d73`. Downloaded bytes are verified against immutable Git object SHA-1 and file lengths before writing anything. A deterministic SHA-256 manifest is written. Changed, missing, redirected, symlinked, stale or partially fetched inputs fail closed. No fallback to mutable `main` or synthetic HTML.

## Reproduce

Offline unit suite: `cd experience2/apollo-r425/qa && python -m unittest -v test_bootstrap`.

With read-only GitHub API access: `python experience2/apollo-r425/qa/bootstrap_exact_sources.py --output /tmp/apollo-reviewed-r425`. Supply GITHUB_TOKEN only if needed for repository read permission. Output location must not already exist.

Then run the existing R424 authentic acceptance against actual reviewed bytes: `python experience2/apollo-r424/qa/real_research_desk_acceptance.py --repo /tmp/apollo-reviewed-r425 --bridge-dir /tmp/apollo-reviewed-r425/experience2/apollo-r423 --output /tmp/apollo-r425-real-qa`.

**Execution boundary:** eight new offline negative/positive custody assertions pass in local testing. The source bootstrap cannot fetch from the current sandbox network (no GitHub DNS), so no authentic R424 integration PASS, navigated browser screenshot, axe-core, navigated LCP/CLS, installed staging, screen-reader review or production Core Web Vitals is claimed. GitHub exact-head CI and QD review remain required. R417's earlier four-file archive-to-GitHub mismatch remains separately OPEN.

## Editorial, rights and conversion

NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; the ignition initiator remained undetermined. Later Command Module 102 deliberate ignitions belong to December 1967–February 1968 testing: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . NASA media cannot imply commercial endorsement: https://www.nasa.gov/nasa-brand-center/ . R425 republishes no photos or insignia and adds no invented Atlas pins.

One coherent journey only: verified Grok Apollo long-form → source-grounded Research Desk → existing free investigation https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → original teacher kit **only after** a rights-cleared sellable SKU, functioning checkout/fulfillment and founder permission are confirmed. No new commercial CTA, tracking scripts, social publication, emails or spend.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Original Apollo educator kit | Confirmed paid order | No verified price/SKU/rights/fulfillment | Withhold paid CTA | HOLD | Founder/Claude |
| Grok Apollo documentary | Qualified attributed session | Published asset_id/UTM and human visits unknown | Reuse TASK-008 source inventory | UNVERIFIED | Grok/Praxxis |
| Research Desk | Relevant investigation click | Authentic R424 checkout unavailable | Immutable six-source bootstrap | 8/8 offline tests PASS; real integration HOLD | Apollo/QD |
| Realized net revenue | 7/30-day paid cohort | Merchant settlement, fees, refunds, qualified visitors unavailable | Require verified orders and denominator | NOT COMPUTABLE | Claude/Commerce |

Coordinate in issues #150, #820 and charter #818. Do not modify homepage PR #49, Research Desk PR #158 or their owners' branches; no WordPress writes or unreviewed release.
