# R129 — Seven-cluster three-way drift reconciliation | DRAFT / HOLD
**Scope:** Preparedness Archive #136, coordinated with creator-to-revenue #820 and business charter #818. This is a new read-only reviewer gate, not source or medical safety approval. No WordPress, navigation, homepage, email, merchant, social, live release, or published-content change.

## Exact GitHub observations (November 4, 2026)
The full 35-article release candidate #584 is frozen at ddb3528ba6494dada1fa1c3a142ce746e3a67706. The seven Claude cluster branches were resolved through Git refs and compared with their original frozen contributor commits:

| Cluster | Frozen | Observed head | Change against frozen |
|---|---|---|---|
| Start Here | 2122d856 | 2122d856 | unchanged |
| Shelter/power | 5daeaf2d | 5daeaf2d | unchanged |
| Food | e9cd7766 | f911ff7a | DIVERGED: ahead 1, behind 1, merge base 4b009361; 2 changed paths |
| Health | d2212d0c | d5ef5baf | ahead 1; 1 changed path |
| Historical food | 2acf65ca | 67e116e5 | ahead 1; 7 changed paths |
| Historical home | f654e600 | 7504a5f0 | ahead 2; 8 changed paths |
| Historical field | a5ce8a62 | 4e5caf81 | ahead 1; 5 changed paths |

**23 changed-path observations, 22 distinct paths.** Food and historical food both edit the same test file; no automated cherry-picking is authorized. The separate shelter follow-up evidence branch is 6a5998ead97eca997e573ce8d3ceacf1c6aabad4 and is not silently counted as an eighth core cluster.

## High-consequence differences independently inspected
Seven changed article bodies were retrieved at frozen/current/candidate SHAs and compared. Approximate words and raw citation-token counts are structural evidence, not editorial quality or safety approval:

| Article | Frozen to current words | Frozen to current citation occurrences | Candidate disposition |
|---|---:|---:|---|
| Pemmican/dried meats | 2413 to 2413 | 46 to 46 | RC matches OLD; current changes citation ID from hist-food-nchfp-jerky to nchfp-jerky. **S-7 HOLD** |
| Pioneer travel rations | 2350 to 2350 | 39 to 39 | RC matches OLD; same held citation-ID replacement |
| Pickling/fermentation | 2384 to 2746 | 42 to 49 | RC matches CURRENT byte-for-byte; no safety approval |
| Root cellars | 2427 to 2793 | 37 to 42 | RC is THIRD byte version despite matching current counts |
| Sanitation before germ theory | 2639 to 2673 | 47 to 48 | RC is THIRD byte version |
| Navigation before GPS | 2889 to 2889 | 47 to 47 | RC is THIRD byte version despite matching counts |
| Pioneer supply chains | 2777 to 3136 | 57 to 63 | RC is THIRD byte version despite matching counts |

Hist-food source fragment: frozen and RC at d1062834 (28 records), live contributor c1856c99 (28 records), replacing source-ID hist-food-nchfp-jerky with nchfp-jerky; never collapse source interpretation without review.
Hist-home: frozen 6460d4b0 (27 records); RC and current 8d85fd86 (29 records) add hist-home-msu-simmons-1798 and hist-home-wellcome-chadwick-1842.
Hist-field: frozen 4f369122 (26 records); current 6b65e0aa and RC 3dafa942 (28 records each). Both include hist-field-ia-hastings-guide and hist-field-oac-breen-diary, but byte differences require source-by-source adjudication.

## New deterministic gate and tests
- Tool: preparedness/tools/r129_contributor_drift_gate.py; reads frozen, observed and RC *immutable Git objects* for all 23 observed paths with git show.
- Classification: candidate matches old head, new head, or is a third version. Protects article slug/publish/safety states, citation counts/ID replacement, author-specific source explanations and source-register changes (including source URL and reading-scope differences).
- Fail-closed on missing Git objects, wrong pinned candidate/branch references, changed or incomplete file inventories, malformed citations/JSON and unexpected non-Preparedness paths. Every row stays OPEN_HUMAN_ADJUDICATION; no automatic approval or merge.
- Test: preparedness/tests/test_r129_contributor_drift_gate.py. **68 Python synthetic/adversarial tests passed locally**; python compilation passed. The exact committed Git blob hashes match locally executed files: gate e2e2978152bd1f6fd7adb7f88bc28d3846489c0e, tests fd4c2c649c85ac7ad83d2fd7ae06037dcbc2de49.
- **Not verified:** full exact-checkout execution against all 23 triples, native validation, WordPress draft build, full suite, browser QA, GitHub CI, and independent QD.

Recommended isolated commands after fetching all immutable refs and ensuring the seven branch heads have not advanced:

    python -I preparedness/tools/r129_contributor_drift_gate.py --repository . --check-current-branch-refs > r129-review.json
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Run only in a scratch checkout. These commands do not authorize publication.

## Other independent lanes (read-only checks)
- #157 draft head 7d1ae6b8: electrical-drill and refrigerated-medication safety wording needs qualified adjudication.
- #169 draft head e9cd7766: legacy shared-directory fixture risk remains until separately proposed #973 fix (4d40996a) is integrated, tested and reviewed. No modifications to either.
- #584 draft RC ddb3528b; R128 #986 parent 0cd27c7a; homepage #49 and flagship #604 remain separate. #604 is bdf01b4a, DRAFT/HOLD.
- 32 shared-URL source groups are still pending human adjudication. Preserve 35 drafts, citations, reading depth, unique routes and safety labels.

## Conversion-first pilot and acceptance gates
One proposed high-intent social topic: household emergency contacts and family reunification. The current source-backed *Household Emergency Plan* is the free guide candidate, but remains on safety/production HOLD. Its emergency guidance must remain freely available once approved, without a commercial or email gate.

Draft free-resource CTA, NOT published: “Make a plan your household can actually use. Read the free Household Emergency Plan, including contacts, meeting places and a practice checklist.”

Optional paid pack is **INACTIVE**: there is no independently authenticated FV-owned, rights-cleared, currently purchasable Preparedness SKU, price, license, payment acceptance, refund policy and actual download fulfillment. No fictional product, merchant button, retired water freebie, or unverified affiliate offer.

| Offer to funnel step | Blocker | Acceptance test/change | Evidence | Owner |
|---|---|---|---|---|
| Existing paid pack to actual sale | No authenticated SKU | Verify Payhip owner/product, rights, price, tax, refunds, delivered file | UNVERIFIED / HOLD | Growth, Claude, founder |
| Free household guide to human reader | Source/medical safety review | Resolve #157 and 32 groups; mobile/keyboard/browser checks at 360, 390, 768, 1440 px | NOT TESTED / HOLD | Preparedness and QA |
| Grok asset to guide | No verified matching asset ID/destination | TASK-008 social inventory with unique asset_id, permitted link type and destination; never seize Grok queue | UNVERIFIED | Grok/Praxxis |
| Guide to optional paid offer | No accepted checkout or rights | Staged only: intent fit, disclosure, consent, CTA, checkout and file delivery; no duplicate tracking scripts | NOT TESTED | Claude/Site QA |
| Paid order to net revenue | No merchant-confirmed order/qualified-human denominator | 7/30-day matched cohorts, paid conversion rate, net revenue minus refunds/fees per 1,000 qualified sessions | N/A | Growth/Claude |

Observation contract: platform/asset_id/utm_source/utm_campaign/utm_content to qualified-human landing session, CTA, confirmed lead (if applicable), merchant-confirmed paid order, fees/refunds, realized net revenue. Affiliate outbound clicks, follows, pageviews and checkout starts are **not** purchases. Tiny-sample warnings required. No new scripts, advertising, spending, checkout activation, publishing or QD PASS.
