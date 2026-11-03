# R88 — Source/citation reuse and human-review work orders (PRIVATE HOLD)

**Issue #136. Preparedness Archive ONLY. Draft branch; do not merge or publish.** This engineering overlay cannot establish source reliability, factual claim support, historical accuracy, qualified emergency/medical safety, or independent QD approval.

## New deterministic engineering

R87 detects citation rank and claim-context ambiguity but leaves thousands of individual citation candidates and repeated source readings requiring human assignment. R88 consumes R87's complete original report, independently replays its historical R86 evidence, and constructs a **lossless, citation-by-citation human reviewer queue** for all 35 article drafts and six tools.

- Each original citation is keyed to its unmodified draft document, original occurrence ordinal, original DOM block SHA-256, literal source ID, and ALL separate source variants. Each variant is identified by (literal contributor origin, exact source ID, original complete-reading SHA-256, exact unmodified URL).
- Stable SHA-256 keys link a source variant across documents without claiming that its URL or content supports any passage. Repeated occurrences remain separate, even when the same original URL or source ID appears again.
- Exact-URL/different-variant clusters are **unresolved source-scope work orders**, never automatically deduplicated sources or authoritative link validation. Case, escape, fragment, path and query differences in literal URLs remain untouched.
- P1/P2/P3/P4 flags only order source, context and citation-review work; they are NOT factual findings, risk scoring, safety verdicts or permission to publish. Empty flags are also not approval.
- The output encloses the complete upstream R87 original, its full R86 historical source/citation bridge and R80 original DOM reading order. The **244 complete source readings** remain preserved in the pinned R80 upstream evidence, not duplicated/truncated by R88.
- Recompute original DOM text fingerprints; reject lost citation occurrences, false source/claim/safety review, duplicate citation identities, altered exact source variants or forged publication state. Each derived report has an independent SHA-256 seal and is verified by reconstruction from the untouched R87 original.
- Optional private CSV exports original citation metadata only, with spreadsheet-formula quarantine; it is never approval intake and is never stored in public website output.

### Run read-only diagnostics

```bash
python -I preparedness/tools/r88_source_reuse_review_workorders.py
python -I -m unittest discover -s preparedness/tests -p test_r88_source_reuse_review_workorders.py -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The original offline build prepares WordPress-ready **private drafts only**. The R88 workflow restricts the PR to exactly four ADD-only files, verifies pinned Git SHA identities, runs R88 adversarial tests and the full native suite, writes any reviewer CSV only to runner-temp and removes it, and never writes CMS, WordPress, navigation, source registers, article HTML, homepage, or public pages.

## Exact coordination SHA snapshot — November 2, 2026 (Pacific)

| Contributor/lane | Exact ref SHA inspected |
| --- | --- |
| Start `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical food `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical home `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical field `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Full 35-article/6-tool RC | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| R87 parent PR #733 | `e3e699532faf549350757084e6db3982a53eb9bc` |
| Independent QA PR #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (DRAFT) |
| Synthetic-fixture QA PR #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` (DRAFT) |
| Separate custody repair | `97921ca5e1f37535c34de95f12c99769a1bcb74d` (not imported) |
| Hastings historical correction | `5c807fbf455b31f2aac3dfd48b598e096329c236` (not imported) |
| Homepage PR #49 | `10495883299d53596992c26a8987f629b2904670` (untouched) |
| Flagship PR #604 | `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` (untouched) |

Independent QA PR #157 is unmerged and is **not human safety approval**. PR #169 isolated `_upgrade_test.json` but its `test_register_fragments_cannot_duplicate_ids` still writes a temporary `_dup_test.json` into the shared source-fragments worktree; this concurrency-risk fixture requires isolation by its owner. All seven contributor branches are preserved as inspected; no historical frozen baseline is silently overwritten. Custody repair and Hastings source changes are not automatically incorporated.

### Mandatory release gate: HOLD

Separate mandatory 13-stage integrity has **not passed**. Historical contributor baseline parity, the 30 source-URL collision groups, 15 safety exceptions, 22 editorial decisions, qualified human validation of consequential advice, actual WordPress/browser accessibility checks and independent QD review are unresolved. This module reports ZERO human source approvals, ZERO claim approvals, ZERO qualified-safety approvals, ZERO independent QD approvals, and `may_publish=false`, irrespective of passing diagnostic tests. No merge, publishing, CMS changes or navigation updates are authorized.
