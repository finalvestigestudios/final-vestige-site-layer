# R448 — Preparedness original-article dependency matrix (DRAFT / HARD HOLD)

Scope: **Issue #136 only**; commercial cross-reference **#820** and charter **#818**. This is an **additive, read-only** integration instrument for the R397 original-source dossier and R446 independent review packet. It neither chooses a Claude manuscript nor changes the live site, CMS, navigation, paid products, tracking, social production or release status.

## Source custody and what the output means

Original Git blob: `86d22a1d504c93db7689b914e2202a7845b648e2` at commit `a22c8797da58ecf186f50fcf47063bd195fd3c17`. Review packet Git blob: `0e655316ced77212abeff77459898253a1e768fd`, originating from R446. The companion JSON ledger carries the **full 35-body SHA candidate multiplicity**, exact **203 source-ID/280-occurrence/181 URL** crosswalk, **17 unmerged shared-URL groups**, **five unadjudicated source/reading-scope disputes**, **nine unselected body/meta/source-fragment forks**, and nine originally frozen Claude/Shelter contributor HEADs. No body text is silently shortened, normalized or selected.

Four articles have locally identifiable body/metadata forks: `family-communication-plan`, `home-fire-escape-plan`, `outage-heat-cold-generators`, `shelter-or-evacuate`. The shared `preparedness/sources/fragments/shelter.json` is a separate global fork. **Actual per-manuscript citation occurrences are not available in the R397 crosswalk**: do not pretend that source-ID presence proves a given article cites it, that all links have been human-checked, or that unreviewed advice is safe. Every one of 35 article rows retains a global evidence/QD/export hold, and 4 articles have additional local manuscript-fork holds.

## Running in a trusted authenticated checkout

From the root of a **complete original repository checkout** with all source files present:

```sh
python -I preparedness/tools/r448_article_readiness_matrix.py \
  --docket preparedness/reviews/r397_original_source_fork_docket.json \
  --packet preparedness/reviews/R446_AUTHENTIC_R397_CONFLICT_REVIEW_QUEUE.json \
  --observed-heads /path/to/independently-fetched-nine-branch-heads.json \
  --output /tmp/preparedness-r448-hold-matrix.json
python -I -m unittest discover -s preparedness/tests -p 'test_r448_article_readiness_matrix.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Exit code `2` from the R448 matrix is **by design**, including on structurally consistent inputs; never treat it as a build error to suppress or a signal to publish. Inspect `structural_evidence_pass` and `errors` separately. The native validator/build and genuine browser/WordPress export parity must be run **separately**, against the full source tree, with independent qualified editorial/safety review. The R448 synthetic tests do **not** authenticate article advice, per-article source usage or source-site availability.

## Independent review and non-interference

- QA PR #157 and synthetic-fixture PR #169 must remain independent draft gates; dependent fixture repair PR #2205 requires separate review. Do not merge, close, rewrite, or infer QD PASS from a green synthetic test.
- The original seven Claude cluster branches and two Shelter descendants were each compared to the R397 frozen HEAD and were identical (0 ahead / 0 behind) at this run. Recheck exact HEADs before any new integration attempt.
- Article #11 editorial, Apollo/home engineering, Claude analytics, Grok creator queue and Praxxis' asset-verification scope are separate. Do not cherry-pick them or amend their branches here.

## Offer → funnel step → blocker → proposed experiment → evidence → owner

| Offer / funnel | Blocker | Proposed draft-only change or acceptance check | Evidence now | Owner |
|---|---|---|---|---|
| One genuinely existing, rights-cleared FV Preparedness pack → paid checkout | No independently authenticated seller/SKU/license, functioning checkout, delivery/refund terms or settlement | Verify in merchant source-of-truth **before** creating any paid CTA; test mobile product→payment→delivery→refund disclosures privately | **FAIL/HOLD:** payable product not confirmed; paid conversions and net revenue **NOT COMPUTABLE** | Founder/Commerce |
| Existing **published** family-contact/reunification social asset → free official guide | Real Grok `asset_id`, post URL/date, narration/rights and mobile destination not matched | Ask Praxxis to verify *existing* Grok post only, without writing social copy or editing TASK-008 production queue; source-matched draft CTA “Review the official household emergency checklist” | **HOLD:** original R397 crosswalk includes Ready.gov `/plan` under two original source IDs; **no live HTTP/asset attestation** | Grok/Praxxis |
| Free guide → optional practical Tool #104 | Article #15 original manuscript variants unselected; child-contact privacy, printing/accessibility and Tool #102/#104 distinction lack qualified review | Provide optional, clearly labeled **non-essential** printable tool only after qualified privacy/emergency/accessibility review; never gate the free safety guidance | **HARD HOLD**, no live tool claim or upsell | Preparedness/QD |
| Qualified visitors → free CTA → consented confirmed lead → verified paid purchase → net proceeds | No consented source-tagged cohort or settled merchant orders | Align with Claude's **existing** attribution/consent systems; do not install duplicate scripts; audit click/lead/order distinctions and refunds/fees at 7 and 30 days | **NOT COMPUTABLE**: no merchant-confirmed purchase/fees/refunds with campaign linking | Claude/Commerce |

**Primary KPI** (only after real data): realized net revenue per 1,000 qualified human sessions = `1,000 * (settled gross - refunds - fees) / qualified-human sessions`. Segment by unique Grok asset ID and campaign, 7/30-day cohorts; annotate tiny samples and missing source attribution. Do not mistake affiliate outbound clicks, checkout starts, followers or confirmed leads for paid orders.

## Still required for any future release

Qualified adjudication of all five original source disputes, nine forks and 17 shared-URL identity groups; independently frozen citation placement/body evidence; the authentic full 35-article native build; 70 genuine WordPress/private-preview exports including CSS provenance; browser/mobile, privacy, food/medical/emergency and QD reviews; actual Grok asset verification; **and** a real purchasable Preparedness offer with rights, delivery and settlements before paid conversion can even be measured.

**Release state is always DRAFT/HARD HOLD. Never publish, merge, change CMS/nav, activate a merchant, email/social post, change an affiliate, spend money, or claim QD/commerce PASS under this PR.**
