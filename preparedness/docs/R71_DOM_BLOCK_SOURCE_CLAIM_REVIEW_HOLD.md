# R71 — Complete candidate DOM-block ↔ citation ↔ source-reading review ledger (PRIVATE HOLD)

**Issue:** #136. **Exact additive parent:** R70 draft PR #626 at
`c42c2c32291442ddce91d33b039785f7adce22f3`. **Separate read-only release
candidate:** PR #584, `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.
This is an internal editor/reviewer instrument, not publishing authorization or a
claim of expert-verified, medically safe or actionable emergency advice.

## Why R71 exists

The prior custody chain preserves all original 35 articles plus the original
water-planning tool (1,959 original citation occurrences), seven frozen Claude
contributors, the separate 35-article/six-tool release candidate (2,173
candidate citations), 244 unabridged candidate source records, and source/URL
identities that must **never** be merged merely because their citation IDs or
URLs match. R69 flagged 599 topic-related DOM blocks without a citation in
*that same block*. The number is **not** 599 unsupported claims.

R71 makes that inventory genuinely reviewable: for **every** candidate DOM
text block, including those with and without topic keywords, it preserves the
entire text, exact block identity, source-document pointer and citation edges
at their Unicode offsets. Each local citation is joined to its origin-scoped
source identities, *exact unnormalized URL variants*, and the SHA-256 of the
complete unabridged research reading. All 244 source readings are conserved
again **once per source**, including uncited ones; different research
readings remain separate. A reverse source→document/block index makes reused
sources easy to locate without implying that repetition is corroboration.

Blocks without a same-block citation may list an adjacent block's citation
*ordinal* as a navigation hint. **These are NEVER support edges.** Same-block
citations also remain **NOT_REVIEWED**, not proof of claim support. Topic
signals are deterministic regex triage, not safety diagnoses.

## Fail-closed boundaries

The pure R71 reconciler verifies the R69/R70 sealed report fingerprints and
parent edge, 35+6 draft documents, 244 unabridged distinct (origin,ID)
readings, all 2,173 citation occurrences, per-document and per-block
fingerprints, Unicode offsets, source and URL variants, complete text and
R69 topic/no-local-citation classifications. A citation cannot disappear or
switch source scope while retaining a nominally valid outer report seal.
Malformed or spoofed human/QD/safety statuses cause a hard hold.

The derived CSV is for **private human triage only**, not Gutenberg import,
WordPress publishing, automatic safety status, or evidence of source-link
verification. Spreadsheet formula-lead neutralization is applied to exported
untrusted text. No external URL is opened, source passage fetched or DNS
resolved by this code. No reviewer-note import or approval mechanism exists.

## Commands on an exact read-only checkout

    python -I -m unittest discover -s preparedness/tests -p test_r71_rc_dom_block_source_review.py -v
    python -I preparedness/tools/r71_rc_dom_block_source_review.py
    python -I preparedness/tools/r71_rc_dom_block_source_review.py --task-csv-stdout > /private/r71-block-review.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The hosted workflow separately pins the exact R70 base, all seven contributor
SHAs, the separate RC SHA, and an **exact four-file additive** diff. The CSV
is created only in a private runner temporary directory, not uploaded as a
public artifact. Run results are **machine checks only**.

## Independent QA / handoff boundaries

Checked exact current GitHub SHA comparisons on 2026-11-02:

| Component | Exact observed head |
| --- | --- |
| Start | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| RC #584 | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| Independent safety QA #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` |
| Synthetic-fixture QA #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` |
| Homepage #49 | `10495883299d53596992c26a8987f629b2904670` |
| Flagship #604 | `5f87f1b0a48ed2f17ecca49a60c44a482ca530de` |

Independent #157 edits for electrical drills, refrigerated medication,
taxonomy/Red Cross status and publish-gate tests were examined; independent
#169 test-only isolated synthetic source-upgrade edits were examined. Neither
is merged or borrowed as human source-safety approval. No changes were made
to either branch, the homepage lanes, historical contributor work or the RC.

## Release remains HOLD

The mandatory `seven_cluster_git_parity` gate still fails on five
diverged frozen contributor baselines. Other blockers: 206 historical
human-link obligations; zero of 244 RC human link checks; original 30/RC 32
shared-URL groups; 43 fallback relationships; 15 unresolved safety exceptions;
22 independent candidate editorial/founder decisions; review of consequential
medicine, water, food, generator/fire and emergency advice by qualified
reviewers; actual WordPress/browser/assistive-technology QA; and independent
QD approval on the exact proposed publication head.

**Never call isolated green Python tests a complete 13-stage release PASS.**
No source/crosswalk rebaseline, publishing, CMS/WordPress write, menu change,
branch merge, public asset update or assertion that unreviewed advice is safe.
