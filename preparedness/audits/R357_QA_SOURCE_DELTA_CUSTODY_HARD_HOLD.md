# R357 — Independent QA source-delta custody: PR #157, #169, #2205

2026-11-13 PT · Preparedness Issue #136 · conversion Issue #820 · charter #818

**DRAFT / HARD HOLD / NO PUBLICATION / NO MERGE AUTHORIZATION.**

## Scope and identity
- Isolated stacked draft from R356 PR #2422 exact head `0e18cb92f25962bbd08d1ebe5341afd4f36844f1`.
- Read-only new `preparedness/tools/r357_qa_boundary_hold.py` and 56 synthetic adversarial tests, plus this audit; original Preparedness bodies, metadata, source fragments, taxonomy, QA branch contents, WordPress and producer assets unchanged.
- QA #157 exact base `10f58fed1ba808056813064ca5f9680589db8da1`, head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (draft/open). Changed five Preparedness files, including two article bodies, start source fragment, taxonomy and tests.
- Synthetic-fixture QA #169 exact base `4b009361277ea1d4617b368f5d45104c7318b284`, head `e9cd7766dac59d47ab467d8945269b9146c2aef5` (draft/open). Changed one test file.
- Dependent fixture repair #2205 exact base `e9cd7766dac59d47ab467d8945269b9146c2aef5`, head `bbcf1859768624c611df4abadc564c18247cf32a` (draft/open). Changed one test file and a separate audit.
- Nine original Claude/Shelter refs read from authenticated GitHub refs in this run and compared to R350 frozen pins: **9/9 unchanged**. Homepage lead #1689 draft/open exact HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`; no homepage engineering changes.

## Actual independent QA #157 source comparison (authenticated source files, not synthetic)
- Household emergency plan: body 22,928 → 23,031 characters; approximate parsed words **3,157 → 3,164**; citation occurrences **57 → 57**; heading anchors unchanged.
- Three-day kit: body 21,330 → 21,647 characters; approximate parsed words **2,840 → 2,877**; citation occurrences **68 → 68**; heading anchors unchanged.
- `start.json`: only `start-redcross-older-adults` **kind** and **notes** changed. This corrects a misclassification of the American Red Cross as a regulator; does **not** independently verify emergency medical claims or count as QD review.
- Taxonomy: **35 → 35** slated article identities. Four start-here articles had safety gate **false → true** (`household-emergency-plan`, `three-day-kit`, `go-bags`, `preparedness-real-households`). This is a substantive safety tightening rather than formatting only; preserve it for qualified reviewer adjudication. Do not blindly cherry-pick across contributor branches.
- These checks establish limited custody, not line-by-line medical safety, correctness of source claims, clinical advice, live click-through or approved publishing.

## New deterministic engineering guard
The R357 native adapter reads locally available pinned Git commit objects without modifying a checkout, compares only exact changed-path allowlists, requires base/head SHA identity, checks two body drafts for reading-depth retention (minimum 92%), citation occurrence non-loss, anchor and link preservation, and no new unreviewed inline scripts. It compares source IDs, URLs, support text and verification flags; it records source-category changes for human review. It detects semantic taxonomy changes, and requires isolated temp copy evidence for synthetic fixture QA. Every result is either `QA_REVIEW_REQUIRED_HARD_HOLD` or `INVALID_HARD_HOLD`; **no publish/merge/QD/sales success state exists**. The source snapshots are hashed; private draft text is not emitted.

PR #169's revised upgrade fixture uses a disposable `TemporaryDirectory` and `copytree`. Dependent PR #2205 fixes a separate duplicate-source test that previously wrote and unlinked a fixture in canonical `ROOT/sources/fragments`; its proposed runtime guard against canonical writes is still unmerged and not native tested. Also, #2205 documents older food-builder `inline-js` lookup behavior differing from the integration builder: do not assume export parity.

## Exact testing and unavailable gates
- New exact local implementation/tests: **56/56 PASS**, Python compile PASS. Committed file SHA-1 Git blobs to match local executed bytes:
  - source `edcf5224e1aaa46c80b1686fdb61d508e5699a1f`
  - tests `1aec9065334c25df4a4a35c0c937d00a3d0e4327`
- Separately re-executed prior local code: R355 **59/59 PASS**, R356 **52/52 PASS**; combined **167 isolated tests** (not a full-native suite).
- Local container DNS could not resolve github.com for a complete Git clone. Native R357 on the incomplete local directory returned `INVALID_HARD_HOLD`, exit 2. Full nine-branch native validation/build, source crosswalk and authentic 50 private WordPress + 50 private preview exports were **NOT RUN**. No hosted CI success, qualified source/QD, browser/network/print, or merchant-sales evidence.
- Historical **15 editorial conflicts**, **17 Article #15/Tool #104 high-priority safety/privacy reviews**, **four disputed source identities**, and unresolved tool-number collisions remain open. No false safety PASS.

## Conversion-first acceptance (#820/#818)
| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One existing FV-owned Preparedness pack (only if actually payable and rights-cleared) | Paid order | No independently authenticated SKU, terms, checkout, delivery, refunds | Verify merchant and fulfillment before drafting any paid CTA | **HOLD / NO VERIFIED PAID ORDER** | Founder/Commerce |
| Official public household emergency planning resource | Free guide → optional practical printable | Article #15/Tool #104 child-privacy, no-JS, medical source and print holds | Qualified review and accessible manual fallback; do not expose private tool | **HARD HOLD** | Preparedness/QD |
| Published Grok family-contact social asset | Landing visits | No independently authenticated published `asset_id` and permitted mobile URL | Read-only Praxxis cross-check in existing TASK-008 | **UNVERIFIED** | Grok/Praxxis |
| Qualified human visits → lead → merchant-confirmed purchase → net revenue | 7/30-day revenue/1,000 sessions | No confirmed merchant receipts or matched consenting attribution | Use approved existing measurement only; distinguish clicks from paid orders | **NOT COMPUTABLE** | Claude/Commerce |

Public free-only candidate: https://finalvestige.com/preparedness/ . Draft CTA for editorial review only: **Start With Trusted Preparedness Resources**. Not deployed. Retired water freebies and unapproved offers remain excluded.

## Release disposition
**OPEN / DRAFT / HARD HOLD**. No merge, production publishing, CMS/nav change, social production/queue/post, email, analytics scripts, affiliate/merchant activation, new spend or QD clearance. Next: obtain authenticated full native checkout, run R357 against the pinned original Git objects and native 100-file private build; qualified editor/source reviewer to adjudicate the #157 safety gates and source classification before any cherry-pick.
