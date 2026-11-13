# R352 — Preparedness nine-tool plan versus six authored bodies (HARD HOLD)

Date: 2026-11-13 PT. Scope: Issue #136 only, with conversion coordination #820/#818. **REVIEW-ONLY. No merge, WordPress, navigation, public release, campaign, merchant or analytics write.**

## Corrected finding: R351's purported taxonomy mismatch was an audit-model error

A direct GitHub connector read from R351's pinned head \`e03f38a71ac4e0f3ea2e7c63c767b0ef91f24532\` retrieved \`preparedness/taxonomy.json\`, Git blob \`15c547bb3018ac182b12a51036389cfa39a59168\`.

- The authenticated taxonomy contains **35 articles and nine planned tool entries**, NOT a taxonomy of six tools.
- Six entries have \`status=drafted-pending-safety-review\` and source body/metadata pairs: \`water-planner\`, \`home-fire-escape-worksheet\`, \`power-outage-planner\`, \`family-reunification-card\`, \`reunification-plan\`, \`kit-builder\`.
- The other **three are intentionally \`not-started\`**: \`pantry-worksheet\`, \`checklists\`, \`offline-reference\`; they are **not missing drafted bodies**.
- \`kit-builder\` is explicitly in the authentic taxonomy. Therefore R351's earlier account that it was an unlisted replacement for Pantry Worksheet is incorrect. **Do not create, rename, delete, publish or remap any tools based on that false diagnosis.**
- R351's \`audit(..., full=True)\` requires a six-entry \`taxonomy.tools\` inventory; this produces a false release failure against the authentic nine-entry taxonomy. R352 adds an independent typed lifecycle gate; R351's obsolete inventory assumption must be superseded before integration and never treated as qualified PASS.

## Newly verified genuine metadata conflict

The six existing source metadata objects were read individually from the same frozen head. Tool \`n\` labels collide:

| Metadata \`n\` | Authored tools / original Git blob IDs |
|---|---|
| 102 | \`home-fire-escape-worksheet\` (\`397c7d3072fb237b490a5a316c93fc863c101be9\`); \`reunification-plan\` (\`10cd57dc8d39e366aaef8fd76cc3f8969b8c5348\`) |
| 103 | \`power-outage-planner\` (\`8796bba2b323cce096639997002c402bd853e50f\`); \`kit-builder\` (\`e9be8a497df737b36d7d399fccc4a00000ce8eac\`) |

These are **metadata-number collisions**, not automatically duplicate public URLs. Exact reader-visible effect requires inspection of the authentic full builder and exported WordPress draft; no automatic renumbering is approved.

## Engineering gate

\`tools/r352_tool_lifecycle_custody_gate.py\` inspects original article/tool plan roles, nine tool taxonomy identities, exactly six drafted pairs and three unstarted reservations, duplicate metadata numbering, canonical route collisions, source body/metadata identity, safety/publication states, original nine pinned contributor refs, and exact taxonomy + builder Git blobs. It reports only hashes and counts for private draft bodies, no manuscript text, and returns a permanent no-publish/no-QD/no-commerce verdict.

- **95/95 new synthetic Python tests passed** in isolated local execution.
- **257/257 combined isolated R350/R351/R352 Python tests passed**. Compilation passed. Exact GitHub code and test Git object SHA checks required before interpreting this as committed-code execution.
- R352 native Git-audit on the incomplete local tree returned \`INVALID_HARD_HOLD\`, exit 2; complete native validation/build, original 50 WP + 50 preview outputs, hosted CI and qualified safety reviews **NOT EXECUTED/NOT VERIFIED**.
- Earlier independent QA PRs #157 and #169 remain draft; fixture remediation #2205 remains a dependent draft. Reviewer must prevent canonical fixture writes before any native test pass is trusted.
- Original holds persist: 15 contributor conflicts, 17 Article #15/Tool #104 emergency/child-privacy review obligations, 4 competing source IDs and 17 disputed citation occurrences. None cleared here.

## Source and traffic-to-revenue acceptance matrix (strict priority)

| OFFER → FUNNEL | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL evidence | OWNER |
|---|---|---|---|---|
| One **authenticated FV-owned, rights-cleared Preparedness pack** → independently confirmed paid order | No payable SKU, fulfillment, refund rights or receipt authenticated | Privately verify seller listing, payment, delivery, rights and refunds; do not invent a product | HOLD; no paid CTA, paid orders or net-revenue claims | Founder + Commerce |
| Free public Archive → genuinely source-backed family-contact guide → clearly labeled optional tool | Article #15 / Tool #104 are private, claims and child privacy remain unreviewed | Human source/claim and privacy adjudication; 360/390px + print/keyboard and accessible download tests | HARD HOLD; no original detailed advice released | Preparedness + qualified QD |
| Verified Grok published \`asset_id\` → suitable public landing | No independently verified single matching published post/destination | Research-only alignment of real post ID, campaign and \`https://finalvestige.com/preparedness/\` using existing TASK-008, subject to platform link rules | UNVERIFIED; creator queue and posting remain exclusively Grok/Praxxis | Grok/Praxxis |
| Human-qualified landing sessions → relevant CTA → confirmed consenting lead → independently settled paid order → net revenue | Merchant receipts, refunds/fees, provenance and attributable cohorts absent | Reuse authorized events and UTM schema; no duplicate scripts or visitor PII | NOT COMPUTABLE; 7/30-day cohort warnings and net revenue per 1,000 qualified human sessions require independent records | Claude + Commerce |

The public Archive is free and its original detailed emergency procedures remain under safety review. Only candidate free CTA (not deployed): **Start With Trusted Preparedness Resources** → \`https://finalvestige.com/preparedness/\`. Do not promote the retired water freebie, unapproved tool, private content, or any hypothetical paid pack.

## Release and coordination

Correct R351's nine-versus-six misunderstanding in Issue #136; retain the true duplicate-\`n\` review docket. All nine contributor ref comparisons matched their original pinned SHAs at observation (identical, ahead=0, behind=0). Homepage lead PR #1689 independently read as HEAD \`f55c36b6598eec558dd8bb24e4c8988becc51be0\`. No owner branches modified. Submit for independent source/editorial review; **do not merge until full native tests and WordPress dry-run, source checks, safety/privacy signoff and founder-controlled release decision**.
