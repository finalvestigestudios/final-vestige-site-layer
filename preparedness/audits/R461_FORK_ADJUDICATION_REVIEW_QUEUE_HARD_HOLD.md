# R461 — Nine-origin author-fork review custody: DRAFT / HARD HOLD

**Scope:** Final Vestige Studios Preparedness Archive source/citation safety integration only. Tracks [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), conversion coordination [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), founder charter #818.

## Exact read-only provenance

- Parent R460 PR #3006 at `bab0465650987641dec0e6545eebd0042c991436`; R460 snapshot Git blob `056d14cd97d29b843d52912383c237b9122e73ef`.
- Snapshot is a Git-blob inventory, NOT article semantics or actual citation-support approval. All seven Claude origins and both Shelter descendants are pinned by R460. QA PR #157, synthetic fixture PR #169, repair PR #2205, Apollo/home #2985, editorial #2789 are separate independent review branches, not merge instructions.
- The 35 candidate body+metadata identities are protected by an SHA-256 checksum computed from the whole original inventory. The reviewer docket also binds the candidate commit and source-file inventory checksum.
- No data are overwritten. Identical literal URLs are not deduplicated: source IDs, reading scopes, citation placements, safety states and disputed claims remain distinct.
- The command emits ONLY `DRAFT_HARD_HOLD` docket JSON. It exits **2 on success and failure alike** so nobody can interpret a structural integrity result as qualified safety or release approval.

## Actual frozen-snapshot article review worklist: 17 distinct slugs

| Article slug | Candidate body original match? | Candidate metadata original match? | Independent original body variants | Human follow-up |
|---|---|---|---:|---|
| family-communication-plan | No | No | 3 | Three Shelter descendants; child privacy, 911/texting and source support |
| home-fire-escape-plan | No | No | 2 | Three Shelter witnesses; human fire-safety and drill review |
| outage-heat-cold-generators | No | No | 3 | Three Shelter witnesses; generator/CO/cold-health advice review |
| shelter-or-evacuate | No | No | 3 | Three Shelter witnesses; official local evacuation guidance |
| household-emergency-plan | No | Yes | 1 | Start Here body change; guidance and source anchors |
| go-bags | No | Yes | 1 | Start Here body change; safety/accessibility wording |
| three-day-kit | No | No | 1 | Start Here article and metadata, source/citation change |
| preparedness-real-households | No | No | 1 | Start Here article and metadata |
| homemade-water-filters | Yes | No | 1 | Shared-baseline body but metadata altered; water claim safety |
| making-water-safer | Yes | No | 1 | Shared-baseline body but metadata altered; water advisory/health |
| salt-beef-salt-pork-age-of-sail | Yes | No | 1 | Shared-baseline body but metadata altered; historical food safety boundaries |
| pemmican-and-dried-meats | No | No | 1 | Historical food manuscript/source scope |
| root-cellars-cool-storage | No | Yes | 1 | Historical home manuscript change, food temp/storage caveats |
| sanitation-before-germ-theory | No | Yes | 1 | Historical home manuscript change |
| pioneer-supply-chains-failed | No | No | 1 | Historical field manuscript and metadata change |
| pioneer-travel-rations | No | No | 1 | Historical food manuscript and metadata change |
| navigation-before-gps | No | Yes | 1 | Historical field manuscript change |

**Four exact source-file Git-blob review groups:** `fragments/hist-field.json`, `fragments/hist-food.json`, `fragments/shelter.json` (3 original versions), and `fragments/start.json`. Their candidate blob identities are not exact originals. This is **not** the separate list of five semantic citation disputes, nine manuscript/source forks, or 17 shared-URL review groups from earlier audits: those are still HOLD.

## Reviewer / native execution instructions

From a trusted checkout containing the FULL original Preparedness source and the R460 pinned snapshot:

```sh
python -I -m py_compile preparedness/tools/r460_origin_branch_blob_crosswalk.py preparedness/tools/r461_adjudication_custody_gate.py
python -I -m unittest discover -s preparedness/tests -p 'test_r461*.py' -v
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r461_adjudication_custody_gate.py --snapshot preparedness/audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json > /tmp/r461_readonly_docket.json
python -I preparedness/tools/r461_adjudication_custody_gate.py --snapshot preparedness/audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json --docket /tmp/r461_readonly_docket.json
```

R461 commands intentionally exit 2 even when the structural docket is correct. Read its JSON `state` for the distinction between `REVIEW_CUSTODY_INTACT_HARD_HOLD` and `PROVENANCE_OR_REVIEW_HARD_HOLD`. Reviewer may change only `review_status` to `EXAMINED_NOT_CLEARED` WITH concrete `finding_note`; QD, source support, safety approval and publication remain false. This DOES NOT grant a route to publish by changing those flags.

No full authenticated native 35-article build/WordPress/private-preview/browser review was run by R461 in the isolated local fixture workspace. No actual medically safe advice conclusion, qualified QD PASS, or real-world source correctness is asserted.

## Conversion-first handoff (strictly research-only)

| Offer → funnel step | Blocker | Change / acceptance evidence | Owner |
|---|---|---|---|
| Existing FV-owned genuinely purchasable Preparedness pack → paid order | No authenticated rights-cleared live SKU, checkout, delivery, refund or settled-order proof | Founder/Commerce verify real inventory and purchase/settlement chain; **NO paid CTA** before acceptance | Founder / Commerce |
| Verified PUBLISHED Grok family-contact/reunification asset → matching free Archive | Public immutable asset_id, actual hook, rights and mobile destination unmatched | Praxxis independently records exact platform/link/date/hook; do not touch Grok's queue or invent UTM | Grok/Praxxis |
| Free source-backed household guide → optional free printable Tool #104 | Article #15 sources, child privacy, 911/text messaging, printing/accessibility not approved | Only draft CTA: **Review the official household emergency checklist**; verify mobile destination and qualified safety first; keep Tool #102 separate | Preparedness/QD |
| Qualified human sessions → CTA → confirmed lead (when relevant) → confirmed paid order → net revenue | No authenticated merchant sales, refunds/fees, attributed sessions or buyer cohort | Reuse existing Claude-approved consent/UTM schema; 7/30-day cohorts and tiny-N warnings. Net revenue/1,000 qualified sessions **NOT COMPUTABLE** | Claude analytics / Commerce |

Founder retains spending/posting/production release approvals. Do not add retired water freebies, dubious upsells, duplicate trackers, public posts or email. No site navigation or WordPress writes, no social/merchant/affiliate activation. Preserve all existing offer statuses and source audit.
