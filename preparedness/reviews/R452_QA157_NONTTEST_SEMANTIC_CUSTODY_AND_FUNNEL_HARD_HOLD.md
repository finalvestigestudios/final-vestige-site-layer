# R452 — QA #157 four non-test changes: semantic custody, no merge (HARD HOLD)

2026-11-17 PT. Scope: Preparedness Archive #136; revenue governance #820/#818.
Engineering is **draft-only**. Read-only comparison of authenticated QA #157 HEAD
`7d1ae6b8ef93d10cfb6810987672360885e9c1aa` against R451 parent
`05fdcf58c981967d26c16a30c9bf961b3e0dcdec`.
PR #157, fixture #169, dependent repair #2205 and all original contributor branches remain unchanged.

## What was actually inspected
Four original non-test QA #157 paths and their current R451 counterparts were
fetched directly from GitHub by commit SHA, with exact per-file Git blob identities
pinned in `preparedness/tools/r452_qa157_semantic_custody.py`.
They are **not** blindly cherry-picked:

| Four QA #157 non-test files | QA #157 blob | R451 blob | Read-only conclusion |
|---|---|---|---|
| `content/articles/household-emergency-plan.body.html` | `6407a31a882211e62c00f4e07ec7dc4d5abf99c6` | `f81cd43516e8295104230412f18776919148f905` | R451 retains prohibition on main-breaker outage drills, protects smoke/CO alarms and medical loads; wording differs, needs qualified editorial review |
| `content/articles/three-day-kit.body.html` | `f578cdbae602c1ad58a9237c8dea0fd74c99f7da` | `933f38ff3cd55a241cf9b392014fc52d4961e84f` | R451 has pharmacist-led interim-use/replacement advice and CDC source marker; wording differs, needs clinical review |
| `sources/fragments/start.json` | `d5a5087042381227d840675d9eb08ddc375d21e8` | `96140d6d1872588e5d20d9052445c9157e88934d` | All 26 QA source IDs preserved among 29 candidate IDs; zero URL/publisher reassignment; Red Cross correctly tagged nonprofit; individual reading-depth changes remain for human adjudication |
| `taxonomy.json` | `d20ff18bc6f243e08796c0505981979a10fca2d9` | `15c547bb3018ac182b12a51036389cfa39a59168` | All 35 slugs, titles, track, section, status and ordinal identities identical; 22 QA review gates versus 27 candidate gates; no safety gate demotion |

**Important integration finding:** QA #157's taxonomy is older and would revert
five later safety gates from true to false if merged as a wholesale replacement.
The five candidates with *stronger* R451 gate coverage are:
`water-math`, `two-week-water-storage`, `pantry-rotation`,
`family-communication-plan` and `warnings-radios-offline-maps`.
These are editorial QA protections, not qualified safety approvals. Preserve all
five; never overwrite R451 taxonomy with the older QA #157 file.

## Deterministic gate
`r452_qa157_semantic_custody.py` accepts only complete
sets of the four original QA and current candidate file bytes supplied in
separate local roots. It requires exact original Git object SHA matches,
duplicate-JSON-key rejection, unique source IDs and article slugs, unchanged
source URLs/publishers, nonempty reading scope, four explicit Start Here gates,
no demoted review gates, no article URL/status drift, household main-breaker
protection, and pharmacist-directed refrigerated-medicine contingency planning.
The script **never** changes article bytes, taxonomy, source fragments, WordPress,
navigation, commerce or branch tips. It always reports `DRAFT_HARD_HOLD`.

**Local test receipt:** Python compilation PASS and 92/92 new synthetic
`unittest` test methods PASS; exact new committed Git blobs match
local executed source/test files (R452 Git blobs to be recorded in #136).
The 87 adversarial methods include per-article status and URL substitutions,
source reassignment, unsafe text removal, and weakened human-review gates.
These synthetic tests do **not** execute the exact GitHub QA/R451 snapshots
inside Python, because there is no authenticated complete local checkout.
The GitHub-connector-based structural comparison above **did** read all eight
original file contents independently. Native build/export/browser tests remain
NOT EXECUTED; 70 authentic article exports remain unavailable.

## Release and commercial acceptance (priority order)
OFFER: a verified existing FV-owned, payable, rights-cleared Preparedness pack
has **not** been authenticated. No invented product, pricing, checkout or paid CTA.
FUNNEL: an actually published, rights-cleared family-contact Grok asset ID (not
yet verified) -> existing free official-agency references at
https://finalvestige.com/preparedness/ -> proposed free-only
"Review the official household emergency checklist" link to
https://www.ready.gov/plan -> **optional** Tool #104 only after qualified
emergency/child-privacy/print-accessibility review; Tool #102 remains separate.
BLOCKER: missing true asset ID, topic fit, mobile destination, confirmed paid SKU,
rights/delivery, fees/refunds, actual merchant-confirmed order and attributed
qualified-human sessions. CHANGE/EXPERIMENT: **draft only** validate mobile
link/readability, honest creator/source intent match, consent and merchant checkout
delivery before any approved live test. PASS/FAIL EVIDENCE: source-only safety
checks structural PASS, paid funnel NOT VERIFIED, net revenue per 1,000 qualified
human sessions NOT COMPUTABLE. OWNER: Preparedness/QD (safety), Grok/Praxxis
(creator asset and independent QA), Claude/Commerce (approved attribution and
checkout), founder (product/release/spend approvals).

Unresolved R397 source disputes 5, variant forks 9, shared literal-URL review
groups 17. Source roster 35 articles / 203 source IDs / 280 occurrences /
181 literal URLs (original R448 pinned docket, not a new QD claim).
No qualified safety review, medical safety assertion, QD PASS, paid sale,
public publication, CMS write, analytics deployment, affiliate activation,
new creator task, social post, email or spending.
