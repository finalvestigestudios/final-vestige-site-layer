# Canonical release-candidate map (verified against GitHub on 2026-11-02)

Every SHA below was read from the GitHub API or `git rev-parse` on 2026-11-02, not copied from earlier reports. **The release candidate is private, unpublished and fails its own custody gates by design (see 05 and 06).**

## 1. The candidate
| Item | Value |
|---|---|
| Branch | `integration/preparedness-release-candidate-20261101` |
| Base | R61 draft PR #559 head `review/preparedness-r61-two-version-citation-lineage-hold-20261101` @ `bdfd0879` (stack: R48 #483 -> R50 #491 -> R51 #496 -> R52 #503 -> R53 #509 -> R54 #511 -> R55 #516 -> R56 #524 -> R57 #531 -> R58 #538 -> R59 #544 -> R60 #551 -> R61 #559) |
| Adds on top of R61 | merge of the R48 head (rendered QA, QA-F1 phone layout fix); integration of contributor work (shelter + follow-up, Start Here RC, food, health, hist-home, hist-field docs/sources/articles); slug-collision fix; CSS wrap fix; qualified founder-approval records; restored medicine guard; QA runner, simulation and register tooling and evidence under `preparedness/docs/rc/` |
| Head | the commit this document is on; `git log` on the branch is authoritative |
| PR | draft, stacked on #559 (number in the final report) |

## 2. The existing chain (other agents; this session did not author R49-R61 except R48)
| PR | Branch | Head | Base | Purpose | In candidate |
|---|---|---|---|---|---|
| #483 R48 | `review/preparedness-r48-build-newline-determinism-20261101` | `23544eae` | R47 #477 | native tests, deterministic LF builder, triage, readiness matrix, safety register, rendered QA, QA-F1 fix | Yes (merged; two docs kept at R52-pinned bytes, updates saved as `*.F1-UPDATE.*`) |
| #484 R49 | `review/preparedness-r49-figure-source-scope-20261101` | `dffad453` | #483 | source-scoped numeric evidence gate | **No: not an ancestor of the tip.** Not integrated; separate sibling branch |
| #491 R50 ... #559 R61 | see chain above | R61 `bdfd0879` | stacked | safety-exception custody, citation/crosswalk custody, reviewer workbooks, contributor drift docket (R60), two-version lineage (R61) | Yes (base of the candidate) |
| #477 R47 | `review/preparedness-r47-visible-evidence-row-parity-20261101` | `7b19198e` | R46 | visible evidence parity | Yes (ancestor) |
| #521 / #554 | shelter | `ac8625fa` / `6a5998ea` | `claude/prep-shelter-5e1e0e` / #521 | shelter continuation + follow-up evidence | Yes, content integrated (not as PRs) |
| #553 | `claude/start-here-rc` | `2af10621` | `claude/prep-start-bbfeb8` | Start Here release candidate | Yes, content integrated |
| (none) | `review/preparedness-r49-shelter-continuation-reconcile-20261101` | `f5e65e3e` | R48 | my earlier trial reconciliation (HOLD) | **Superseded** by the candidate; keep as history, do not merge (its name collides with chain R49) |

## 3. Contributor branches (frozen pin vs newest) and what the candidate took
| Cluster | Frozen pin (R14/R61) | Newest on GitHub | Integrated? | What changed |
|---|---|---|---|---|
| start | `2122d856` | `claude/start-here-rc` `2af10621` | Yes | 27 added files (kit-builder tool, tool generators, editorial hub, source-audit ledger, tests, browser-QA evidence) plus the `reunification-plan` tool pages (add/add conflict with shelter, resolved per S-6); `three-day-kit`, `go-bags`, `household-emergency-plan`, `preparedness-real-households`, taxonomy, builder hook merged |
| shelter | `5daeaf2d` | `claude/prep-shelter-followup-evidence` `6a5998ea` | Yes | 4 articles rewritten; 3 tools + diagrams + tests + docs added; `shelter.json` 31->45 sources |
| food | `4b009361` | `claude/prep-food-ccdc55` `f911ff7a` | Docs only | only `CLUSTER-food.md` taken; its fixture-test rewrite is superseded by the chain's isolated-fixture tests |
| health | `d2212d0c` | `claude/prep-health-837444` `d5ef5baf` | Docs only | only `CLUSTER-health.md` changed |
| hist-food | `2acf65ca` | `claude/prep-hist-food-b81f19` `67e116e5` | **No (deliberately)** | source-ID retarget needs human decision (S-7) |
| hist-home | `f654e600` | `claude/prep-hist-home-0e0e38` `7504a5f0` | Yes | sanitation, pickling, root-cellar articles; 27->29 sources; 1798 Simmons text recorded |
| hist-field | `a5ce8a62` | `claude/prep-hist-field-9db767` `4e5caf81` | Yes | navigation, pioneer supply chains; 26->28 sources |
Also: `feature/preparedness-archive-v1` @ `ee591e2d` (original lead branch) and `main` @ `77a87635` are unchanged.

## 4. Redundant or superseded
- #484 R49 sibling (not in chain); my R49 reconcile branch (superseded); food and hist-food fixture rewrites (superseded by the chain's isolated fixtures); the earlier R48 doc copies (kept as R52-pinned).
- Other lanes visible in the PR list (Apollo, Dispatch, Mind, Experience 2.0, homepage) are **not** touched by this work.

## 5. Not authorized and not done
Merges to protected branches, WordPress writes, navigation or homepage changes, publication, edits to frozen pins, the independent R20-R31 gates, `crosswalk.json` and `article-evidence-lock.json` in the repository tree.
