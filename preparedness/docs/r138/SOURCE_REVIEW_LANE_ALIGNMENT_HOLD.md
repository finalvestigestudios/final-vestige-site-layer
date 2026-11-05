# R138 — source-queue ↔ author-dossier reconciliation (DRAFT / HOLD)

Scope: Preparedness Archive #136, conversion coordination #820 and business charter #818. This is a **read-only, draft-only** audit stacked on R137 PR #1049 exact parent `5a0dfe1067440d7607394ae85b9c2cb6f21b7014`. Nothing here authorizes publishing, merges, CMS writes, navigation, analytics, payment/affiliate activation, social posting, or paid services.

## Problem closed by the proposed gate

R135 human-worklist source tasks are built from **cited** source variants in rendered article passages. R137 independent author-scoped dossiers include **all registered variants**, including those not cited in an article. Both represent the same 32 historical shared-source groups, but indexing conventions differ: R135 uses the crosswalk's original group sequence, while R137 sorts by normalized URL. A future reorder or register change could silently associate a human review with the wrong group if joined by numeric index alone.

R138 binds the two independent, custody-gated outputs using exact triples **(origin, source ID, literal URL)**, never fuzzy URL equivalence or a guess based on group number. It requires that all 32 cited-source tasks map bijectively to 32 distinct author dossiers, the cited identities match exactly, each group's citation occurrence count and affected article set agree, and all uncited author variants remain visible as unreviewed source records. It independently checks 35 unique DRAFT/HOLD article slugs, 2,000 citation occurrences, 244 source rows, 80 frozen Git blobs, 202 literal URLs and 201 conservative aliases. The resulting report has both original and sorted group indices and input SHA-256 fingerprints, with all publication/safety/QD/merchant gates explicitly false.

The new bridge **does not adjudicate source claims, verify URLs as safe or current, authenticate human reviewers, permit advice to be regarded as medically safe, or publish WordPress drafts**. The R133 custody gate is executed by both upstream input generators before any reconciled report is produced.

## Running on a trusted complete checkout

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r138_cross_lane_reconciliation.py --root .
```

The last command invokes R133→R134→R135 and independently R137, enforcing immutable Git-blob custody and structural author-source parity. If dependencies or complete data are missing, it exits **2 with HOLD**, never with a substitute approval. Output is a local JSON review aid; it must not be deployed or used as a publishing gate pass. Do not commit locally completed reviewer identities or sensitive family planning details.

## Current evidence / limitations (2026-11-05 PT)

- **TESTED in isolated local synthetic fixtures:** 120/120 R138 unit/adversarial tests passed via Python `-I` unittest discovery; `py_compile` passed. Negative tests separately mutate all 35 article publication states, all 32 shared-source group citation counts, both input approval flags, loss/duplication of variants, exact URL source identities, author reading scopes, article membership, source-census counts and release labels. These are not real-archive execution or qualified content review.
- **Direct GitHub source inspection at R137 parent:** 32 crosswalk groups and 75 registered variants. The crosswalk's original order and URL-sorted order presently agree (0 numeric differences); the bridge protects against future order drift. This observation only verifies the **crosswalk JSON**, not R138's runtime against all 35 articles.
- **NOT TESTED:** full real-candidate R133–R138 execution, native validate/build, complete repository test suite, WordPress draft export, browser/mobile QA, merchant checkout, qualified source/safety adjudication, independent QD or hosted Actions. Complete authenticated checkout is not available in this execution environment (GitHub DNS failure). Historical Actions jobs have failed before a runner executes; no CI PASS is asserted.
- **Outstanding source decisions:** 32 shared-source groups, historical jerky source-ID collision S-7, and independent QA #157's electrical-drill/medicine wording. PR #169 synthetic-fixture isolation remains separate from follow-up draft #973; no QA PR merged by R138. All five advanced/diverged Claude branch deltas require manual three-way review; do not auto-merge or overwrite seven-cluster work.

## Commercial conversion: one high-intent audience, no fictional offer

**Audience:** family communication, child/school pickup, caregiver reunification; **proposed free destination:** existing Household Emergency Plan, currently DRAFT/HOLD pending source/safety review. Optional existing family-reunification printable remains DRAFT and must be tested at mobile/print/privacy sizes. **No matching, authenticated, rights-cleared, paid Preparedness SKU/checkout or verified Grok Preparedness asset ID has been established.** The retired Water Resilience products must not be reintroduced.

| OFFER | FUNNEL STEP | BLOCKER | PROPOSED CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Existing paid practical Preparedness pack, **unselected** | paid-order confirmation | no verified currently sellable matching SKU | audit Payhip product ID, ownership/right to sell, price, active checkout, download, refunds, payment/fees with merchant records; only then approve a specific optional pack | **HOLD/UNVERIFIED**; no checkout test | Growth / Claude / founder approval |
| Household Emergency Plan | free guide entry | draft source and emergency-safety HOLD | complete qualified source/safety review, native validation, legible evidence and 360/390/768px reader QA | **DRAFT / NOT VERIFIED** | Preparedness / independent QA |
| Grok family-reunification asset | social → landing | real published asset ID and approved destination unverified in TASK-008 | Grok/Praxxis supply exact post URL, immutable asset_id, platform linking route, rights and current publish state; do not change queue or scripts | **UNVERIFIED** | Grok / Praxxis |
| Optional existing printable | guide → download | mobile, privacy and print QA incomplete | visible optional CTA only after release; no personal details transmitted, no gate on emergency guidance; verify 360/390px, printing and download | **NOT TESTED** | Preparedness / Site QA |
| Rights-cleared paid pack (only once verified) | product CTA → merchant checkout | SKU, fulfillment, disclosure and measurable acceptance unknown | QA truthful destination and price, disclosures, checkout, delivery and refund flow at mobile sizes, no fabricated urgency | **HOLD** | Growth / Claude / Site QA |
| Paid order → realized net revenue | attribution and 7/30-day reporting | no merchant order/refund/fee record linked to qualified sessions | reconcile approved asset UTMs → qualified sessions → CTA → actual merchant-confirmed orders → refunds/fees; do not treat CTA clicks or leads as sales | **NOT COMPUTABLE** | Growth / analytics owner |

No public CTA, sales claim, email send, offer activation, tracking script, or website change is authorized by this research.

## Reviewer acceptance

Review the exact current contributor SHA differences and both independent QA PRs first; keep separate source variants and unreviewed human review states; execute full command chain on a trusted checkout; compare R138 JSON mapping with original source crosswalk, checking all 32 groups and representative source passages; obtain qualified food/electrical/medical reviewer decisions where applicable; independent QD must evaluate the final exact package and founder approves any production release. Until then: **DRAFT / HOLD**.
