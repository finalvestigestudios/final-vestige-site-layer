# R290 — exact citation-occurrence identity and readable claim-context custody

Issue: #136. Commercial coordination: #820 / charter #818. **DRAFT / HARD HOLD.**
Branch: `automation/prep-r290-exact-occurrence-identity-hard-hold-20261111`
Base: R289 PR #2034, `68f157d4dcedc705234217e8a730e58fd967d6a7`.
This review branch does NOT merge, publish, alter original manuscripts, change any URL, activate a merchant, or certify a source.

## Reproduced defect and bounded repair

An equal-count false match can survive R288 and R289:
`<span hidden>{{cite:a}}</span><p>{{ci<b>te:a}}</b></p>`

The raw literal occurrence is hidden; a different visible marker is assembled across markup.
R288 can join the visible fragments into a marker, while R289 can count the hidden literal,
making the totals agree without matching **the same source occurrence**.

This patch updates R289's read-only Python scanner to bind literal source ID + exact raw
start/end character span to a reader DATA node. It rejects nonreader literal markers,
attributes/comments posing as citations, and markup/HTML-entity-assembled tokens.
The ledger now excludes hidden prose and decodes ordinary HTML entities for source
context fingerprints (for example, `&times;` → × and `&amp;` → &).
This is a mechanical audit only: real rendered CSS, external stylesheets, assistive
technology, source factual support and medical safety are NOT verified.

## Executed local evidence, NOT full repository evidence

- Exact committed R288, patched R289, and R290 test source bytes checked by Git blob SHA.
- R288 regression **56 PASS**, R289 regression **68 PASS**, new R290 **51 PASS**:
  **175/175 PASS; zero skipped/failures/errors** in one local execution.
- Python compilation passed for these five local gate/test files.
- `python -I tools/validate.py` and `python -I tools/build.py`: NOT EXECUTED
  (authentic full checkout unavailable; those files are absent locally).
- Full inherited repo tests and 41 WordPress draft exports: **NOT EXECUTED / NOT VERIFIED**.
- No independent QD PASS, qualified safety/privacy approval, source-scope verdict or release approval.

## Frozen contributor comparison (fresh current SHA checks)

All 7 contributors matched the original R200 frozen SHAs exactly, ahead=0, behind=0:

| Cluster | Branch | R200 SHA |
| --- | --- | --- |
| Start | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Historical food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent QA PR #157 remains open/draft, based on the original Start branch.
Independent fixture PR #169 remains open/draft. One fixture was migrated into a
`TemporaryDirectory`, but `test_register_fragments_cannot_duplicate_ids` in the
same current test file STILL writes a source fragment in the actual `ROOT` tree;
the remaining isolation problem belongs to independent QA, not this branch.
Home PR #1689 remains separate and untouched.

## Human safety/source holds (unchanged)

35 historical articles, six tools, 21 three-way historical discrepancies,
32 shared-source URL groups, 15 duplicate source ID groups, three disputed agency
citations, Article #7 chemical-water risk and Article #15/Tool #104 child-information
privacy/print/accessibility review remain **HARD HOLD**.

## Conversion-first experiment — not an approved live campaign

One candidate audience: family emergency-contact/reunification planners.
A verified, already-published Grok asset ID, date, rights, actual link destination and
consented campaign parameters remain **NOT VERIFIED** through TASK-008.
Existing public free archive: `https://finalvestige.com/preparedness/` (do not
link held article/tool drafts). Proposed CTA copy for future review only:
“Start with official household emergency-plan guidance — free, no purchase required.”
No new lead form and no retired water freebie.

One provisional paid pack: Legacy Triage, **NOT VERIFIED** rights-cleared, suitable,
currently purchasable, deliverable, refundable or founder-approved. No paid CTA.
Acceptance path requires: signed-out mobile organic asset link → correct free guide →
optional labeled practical resource (privacy/accessibility approval) → exact relevant
existing paid pack's verified purchase/checkout/fulfillment → fees and refunds →
merchant-confirmed **net** paid order. Never count clicks or leads as sales.
Seven-/30-day net revenue per 1,000 qualified-human sessions: **NOT COMPUTABLE**.

NO social posts, CMS/navigation changes, email sends, affiliate/merchant activation,
analytics script, purchase or spending. Grok retains creator/posting and TASK-008
ownership; Claude retains production engineering; founder retains release approvals.
