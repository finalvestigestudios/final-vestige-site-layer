# R87 — Rank-only citation matches are not claim identity (PRIVATE HOLD)

**Issue #136 · Preparedness Archive only · never publish this evidence packet.** No merges, homepage/nav/CMS/WordPress changes, human source check, medical safety finding, or QD PASS is authorized or implied.

## Engineering problem and bounded change

R86 conserves the entire 35-article + six-tool release candidate and aligns 29 contributor-authored article histories to RC citation occurrences by literal source-ID and occurrence rank. **Rank is a reconciliation key, not evidence that a revised citation points to the same factual claim.** Inserting/removing a citation of the same ID can shift the remaining alignments while keeping literal IDs and URLs unchanged.

R87 adds a separate read-only reviewer overlay with four concrete types of alerts:

1. Repeated identical source IDs within one article: **a position-based join cannot independently prove the same claim remains associated**.
2. Historical addition/removal of a citation of the same source ID, including **unpaired historical records**: all related rank-aligned citations require human review.
3. The complete historical citation container text, exact token, or visibility scope cannot be observed verbatim in the corresponding R80 original DOM block: this is a **scope-review cue**, never a claim of factual error.
4. R80 action/quantity lexical triage: preserve the human-review priority without asserting the advice is unsafe, safe, medically verified, or sufficiently supported.

All 41 complete original documents, their original DOM reading order, source variants (literal URLs, distinct origins and research readings), the 1,768 historical comparison identities, and every unmatched record remain embedded in the newly sealed report. The overlay does not normalize source URLs, modify article prose or duplicate/merge sources. This additive module **independently replays the R86 original report from its unabridged original documents and historical comparison rows**, rather than accepting a digest alone. The normal live path first runs R86's pinned upstream reconstruction from Git objects. Mutation, false-approval and re-sealing tests exercise both stages.

**Interpretation:** Review flags are leads for qualified editorial/source experts, not confirmed unsafe medical guidance, erroneous citations, or reasons to change official emergency instructions automatically. A citation appearing in the same paragraph as an instruction is not proof of support. An empty cue list is not a safety clearance.

## Usage — private, offline, read-only

```bash
python -I preparedness/tools/r87_rank_ambiguity_claim_scope_gate.py
python -I -m unittest discover -s preparedness/tests -p test_r87_rank_ambiguity_claim_scope_gate.py -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Optional `--private-csv-stdout` emits metadata only (slugs, literal source IDs, citation ordinals, cue names, `NOT_REVIEWED`), with spreadsheet-formula quarantine. It is neither approval intake nor an output for public publication. Do not check in reviewer exports, source records, citation dossiers or rebuilt output.

## Exact coordination references — 2026-11-02 Pacific

| Lane | Pinned branch HEAD |
| --- | --- |
| Start | `claude/prep-start-bbfeb8` — `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `claude/prep-shelter-5e1e0e` — `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `claude/prep-food-ccdc55` — `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `claude/prep-health-837444` — `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical food | `claude/prep-hist-food-b81f19` — `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical home | `claude/prep-hist-home-0e0e38` — `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical field | `claude/prep-hist-field-9db767` — `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Full slate release-candidate PR #584 | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| Independent safety QA PR #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; **DRAFT** |
| Synthetic fixture QA PR #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5`; **DRAFT** |
| R86 immutable parent PR #726 | `3796b8eca20b56bb49ac880f1dc848194de243bc`; **DRAFT** |
| Separate custody repair | `integration/preparedness-custody-repair-20261103` — `97921ca5e1f37535c34de95f12c99769a1bcb74d`; newly advanced, **NOT imported** |
| Homepage PR #49 | `10495883299d53596992c26a8987f629b2904670`; untouched |
| Flagship PR #604 | `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; untouched |

## Independent QA and mandatory release HOLD

PR #157 remains an independent draft: safety wording, taxonomy and fixtures cannot be assumed approved without qualified review. PR #169 isolated the `_upgrade_test.json` fixture, **but `test_register_fragments_cannot_duplicate_ids` still writes `_dup_test.json` under the shared source-fragments working tree**; PR #169's new head does not solve that issue. Owner coordination requested; R87 does not edit either PR.

The separate custody-repair branch advanced by one commit from `30101ba5` to `97921ca5` modifying `pioneer-supply-chains-failed.body.html` and `sources/fragments/hist-field.json`. This additional evidence remains outside R87 until independently compared and reviewed.

**BLOCKERS: mandatory 13-stage release integrity is not green; the historical five-branch Git parity conflicts persist; human source/URL checking and 30 shared-URL collision groups unresolved; 15 safety exceptions; 22 editorial decisions; qualified review of consequential emergency advice; actual WordPress/browser accessibility and QD approval absent.** No publication or WordPress/CMS/nav write is permitted. This report is a deterministic engineering review queue, not medical or emergency-safety clearance.
