# R152 — eight-citation Historical Food source alias custody

Issues: #136 (engineering/source safety), #820 (conversion), #818 (business charter). Date: 2026-11-05 Pacific. Status: DRAFT / HARD HOLD. Parent: R151 PR #1144 at commit 274e7f1e8d442678b956e6f6585e0684ba5297e1. New additive code, tests and review documentation ONLY; original 35 articles, source files, crosswalk, routes, safety states and WordPress are unchanged.

## Exact GitHub evidence

The frozen candidate is 2826612f9caf327dff3ef00b242e4e67a3491200; the Historical Food contributor head is 67e116e536c7410bed30f8f3b1bb8c166f3c223d.

| Article | Old source ID | Upstream ID | Substitutions | Total citations |
| --- | --- | --- | ---: | ---: |
| Pemmican and Dried Meats | hist-food-nchfp-jerky | nchfp-jerky | 7 | 46 |
| Pioneer Travel Rations | hist-food-nchfp-jerky | nchfp-jerky | 1 | 39 |
| **Total** | **Not approved for replacement** | **Human review pending** | **8** | **85** |

An exact independent GitHub comparison found that the only article changes are those eight citation IDs and CRLF vs LF line endings. No word, markup, non-target citation, or reading-depth substitution was detected. This is **structural evidence only**, not a medically or food-safety-approved account.

Three different **source records** exist for the same NCHFP jerky page/path:
1. Base register: nchfp-jerky is a placeholder, with no specific author interpretation or independently checked reading.
2. Food fragment: nchfp-jerky has a detailed author-specific supports explanation covering heat, handling and storage guidance.
3. Historical Food fragment: hist-food-nchfp-jerky has an independently written explanation and notes about differences from USDA FSIS guidance.

All three source entries have human_link_check = false. The exact URL paths differ only by trailing slash; that **cannot establish that the distinct readings, claims and risk statements are interchangeable**. The NCHFP jerky page does not automatically validate pemmican as safe shelf-stable food.

## Gate and tests

The Python validator in preparedness/tools/r152_jerky_alias_gate.py loads both exact article versions and the three source registers from frozen Git commits and verifies original Git blob IDs. It preserves 46 + 39 citations, their order, all non-target IDs and article text, permitting ONLY eight alias changes plus CRLF-only variation. It records line-numbered original contexts, source-record metadata differences and false human-review flags for qualified reviewers. It rejects unrecognized IDs, changed reading content, missing or inserted evidence, forged verification and altered source records. It never modifies a source, article, crosswalk, commerce state, CMS or public asset. Optional JSON reviewer output is only written to an explicit new local path **outside** the repository.

In a trusted complete checkout containing both frozen Git commits:

~~~sh
python -I preparedness/tools/r152_jerky_alias_gate.py --repo .
python -I preparedness/tools/r152_jerky_alias_gate.py --repo . --report /tmp/fv-r152-historical-jerky-review.json
python -I -m unittest discover -s preparedness/tests -p 'test_r152_jerky_alias_gate.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
~~~

The custody tool returns exit **2** even on successful structural reconciliation. An invalid/missing checkout also returns exit 2 with INVALID_HARD_HOLD. Neither state constitutes a release approval.

**Executed locally:** 54 of 54 isolated adversarial Python tests PASSED, with py_compile passed. The exact Git blob identities for BOTH committed Python files matched the locally tested copies. **Not executed:** authenticated full-checkout native validation/build, full regression, rendered WordPress drafts, independent QD and qualified medical/food-safety review. GitHub Actions must not be manually rerun at additional cost.

## Review decision required

A qualified reviewer must inspect every one of the eight original citation contexts against the actual current NCHFP page and distinct source-support statements, particularly wild-game/pork handling, heating timing and storage windows. Check official USDA FSIS differences; historical practice is not modern safety approval. Preserve the old author-specific ID until a review explicitly resolves the source-record reconciliation. No automatic substitution or safety state upgrade is permitted.

## Other agents and blockers

Seven contributor branch heads checked: Start 2122d856, Shelter 5daeaf2d, Food f911ff7a, Health d5ef5baf, Historical Food 67e116e5, Historical Home 7504a5f0 and Historical Field 4e5caf81. Two still equal frozen pins, four are ahead and one Food branch has diverged; recheck before review or merge. Independent QA #157 remains separate: its medication-language fix needs qualified review; its older full article versions would reduce reading depth/citations. Synthetic fixture PRs #169 and #973 must remain isolated; they move shared-tree test fixtures into temporary copies. Homepage PRs #49/#604 belong to the home lead. Other independent blockers: 58 unresolved tool-source IDs, four same-ID interpretation substitutions, 32 shared-source groups, unreviewed safety guidance, absent native pipeline and QD. No conflict resolution or merge implied.

## Conversion-first Preparedness pilot (UNAPPROVED)

High-intent social topic: household emergency contacts, school pickup and family reunification. Authentic existing free guide: **Household Emergency Plan**, still safety/QD-gated; emergency safety information must remain free. Optional practical resource: **Family Reunification Card**, currently source/print/privacy/mobile-QA gated. Existing genuinely purchasable matching **paid Preparedness SKU not authenticated**; no paid checkout module may be rendered, no item priced speculatively, no retired water freebie, no unwarranted upsell.

**Draft CTA, NOT to publish:** “Make a household emergency contact plan you can practice. Read our free Household Emergency Plan. An optional printable Family Reunification Card can help organize the details; follow current local emergency instructions.”

**Acceptance checklist:** confirm Grok asset_id and platform-permitted link in TASK-008 without changing Grok's posting queue; get Claude-approved exact destination and avoid duplicate URLs; ensure source/QD approval; test phone widths 360 and 390 plus 768 and 1440 px, keyboard and readable print; confirm card remains local/private without transmitting contact details; test download, return path, relevant CTA, accurate disclosures and existing Focus signup. Require founder approval for any public change. If a rights-cleared paid SKU is later verified, test merchant price, delivered file, rights, refunds, fees and independently confirmed orders **before** any commerce CTA; do not call clicks or confirmed leads paid conversions.

**OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER**
- Existing paid Preparedness pack → checkout → no authenticated matching SKU → read-only merchant/rights/delivery verification → **HOLD** → Commerce/Claude.
- Free Household Emergency Plan → reader → source, safety and QD review outstanding → approved staged draft checks only → **DRAFT/NOT RELEASED** → Preparedness/QA.
- Family Reunification Card → usable resource → source IDs/privacy/print untested → stage, review and test → **NOT VERIFIED** → Preparedness/Site QA.
- Grok asset → guide → no verified asset_id/destination → reconcile TASK-008 → **UNVERIFIED** → Grok/Praxxis.
- Orders → net revenue per 1,000 qualified human sessions → no verified paid transaction and 7/30-day session cohort → reconcile merchant settled orders, refunds and fees with source-linked qualified first-party traffic → **NOT COMPUTABLE** → Commerce/Analytics.

No paid services, live release, WordPress/CMS write, homepage/nav change, analytics duplication, checkout activation, merchant/affiliate action, email or social post occurred.
