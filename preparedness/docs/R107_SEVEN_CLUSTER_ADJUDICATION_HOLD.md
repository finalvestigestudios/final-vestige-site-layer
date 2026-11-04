# R107 — Seven-contributor Git progression adjudication (Issue #136)

**STRICT PRIVATE HOLD. NOT A SOURCE, HEALTH, EMERGENCY, QD OR PUBLICATION APPROVAL.** This is an additive, read-only engineering review lane following R106; do not alter the R14 frozen Git-object manifest, historical R15 parity gate, source fragments, editorial files, site navigation, WordPress, CMS or existing private release workflow.

## Exact scope and why this exists

R106 fixed the separate full-suite 180-second timeout obstacle by preserving all 13 mandatory tests and setting a 480-second bounded limit **only** for the native unittest step. The unchanged mandatory pipeline then reached `seven_cluster_git_parity` and correctly failed because five original contributor branches advanced beyond the exact historical R14 SHA pins. **A moved tip is not, by itself, loss of content; it is not, by itself, proof that an edit is safe to integrate.**

Independent read-only GitHub comparisons performed November 3, 2026, at the exact pinned R106 references:

| Original contributor | Frozen R14 SHA | Observed HEAD | New commits | Modified preparedness paths | Review surface |
|---|---|---|---:|---:|---|
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | same | 0 | 0 | Frozen one-meta source-use exception still unresolved |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | same | 0 | 0 | Unchanged frozen contributor |
| food | `4b009361277ea1d4617b368f5d45104c7318b284` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | 1 | 2 | Cluster research log + unit test |
| health | `d2212d0ca0750817d3929865d3069835980faf20` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 1 | 1 | Cluster research log |
| hist-food | `2acf65ca3efa9b4b5db7976f379b9ea693be43a4` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 1 | 7 | Two bodies, two meta, research log, source fragment, test |
| hist-home | `f654e600f89c321a480dd8f055be4d13d0673490` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 2 | 8 | Three bodies, three meta, research log, source fragment |
| hist-field | `a5ce8a62f168db05c95232e3eb385dccd0d19e7f` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 1 | 5 | Two bodies, one meta, research log, source fragment |

**Actual 23 modified file paths** in these five advancements: 7 article bodies, 6 article metadata records, 3 complete author-source fragments, 5 cluster research documents and 2 unit-test paths. Exactly 21 are in the original 72 author-scoped paths; 2 tests are outside frozen author scope. These are Git-diff inventory facts, **not** claims that any revised medical/food/water advice is safer, that all body changes are semantic (some may be formatting), or that the revised sources support their claims.

## New private R107 deliverable

`preparedness/tools/r107_exact_branch_progression_adjudication.py` independently runs the original historical R15 checker against **original immutable frozen** refs, then reuses R60's actual Git-object byte and per-path checks to construct a frozen → exact contributor HEAD → frozen integrated reference queue. It:

1. Confirms the source manifest's frozen Git blob and the seven contributor identities (29 original cluster-authored articles, 72 author-scoped evidence files, the single historical `preparedness-real-households.meta.json` exception).
2. Checks the exact new seven contributor refs and separately pinned release candidate; fails on ref movement, missing object, nonexistent branch, invalid path or duplicate identity rather than auto-refreshing a SHA.
3. Requires real Git ancestry for **all seven** frozen → current progressions. Descendancy does **not** grant approval.
4. Uses the R60 real-Git changed-path inventory, independently verifying all original 72 scoped Git blobs; preserves changed files outside the frozen 72-path manifest (including altered tests) visibly in the reviewer queue.
5. Compares every changed author-scoped blob to its exact historical integrated Git blob. Labels `POST_FREEZE_CHANGE_NOT_IN_INTEGRATED`, `CURRENT_DIFFERS_FROM_INTEGRATED_REVIEW`, `CURRENT_EQUALS_INTEGRATED` or `OUTSIDE_ORIGINAL_72_PATH_SCOPE_REVIEW` are **routing states, never source or safety approvals**.
6. Outputs deterministic, reproducible **HOLD** JSON (stdout only; no writes) with explicit review queues for citation-bearing bodies, source-use/safety metadata, fragment source identities and research logs. No "pass" exists for release.
7. Keeps the original R15 gate unchanged and expected to **FAIL CLOSED on moved live refs**. This workorder is an additional resource for human adjudication, not a replacement for R15 or the 13-stage mandatory workflow.

A reviewer must compare original and revised passages and source records at exact objects, verify actual citations, original reading scope, changed safety statuses and the original R14 metadata exception, then independently decide whether and how to integrate. Do not merge, re-pin, publish, or call human review complete on the basis of a generated digest or an ancestry relation.

## Private exact-checkout commands

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r107_*.py' -v
python -I preparedness/tools/r107_exact_branch_progression_adjudication.py --repo-root . --json > "$RUNNER_TEMP/r107-hold-private.json"
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Requires complete Git objects and freshly fetched remote-tracking refs in an isolated trusted checkout. `R60`/Git SHA trust protects against accidental mutated input, **not** a malicious actor with authority to rewrite the entire repository or a trusted human source assessment. The JSON must stay private; it includes paths and recorded Git custody fingerprints, not release approval.

## Coordination and remaining requirements

Read-only independent safety PR #157: `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, draft/unmerged. Independent fixture PR #169: `e9cd7766dac59d47ab467d8945269b9146c2aef5`, draft/unmerged. One remaining `_dup_test.json` source-tree fixture write requires isolation before merge; a separate `_upgrade_test.json` fixture is already isolated. Home lead PR #49: `10495883299d53596992c26a8987f629b2904670`; flagship PR #604: `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; **untouched**.

Apart from moving ref parity, the release still has 30 shared URL groups awaiting human scope/claim verification, 15 safety exceptions, 22 editorial decisions, five unfinished tools, print/browser checks, qualified medical/emergency review and independent QD. The 35-article slate and one complete tool remain **WordPress-ready private drafts only**; no publication, CMS or public navigation change.
