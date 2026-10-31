# R18 — Trusted-checkout private preflight orchestration (Issue #136)

**Status: DRAFT / HOLD. Nothing may be published.**

## Purpose

R8–R17 added separate source, claim, rendering, article-text and Git-object
integrity checks. Until R18 there was no single fail-closed command that required
the native editorial validator, WordPress draft-only builder, actual unittest
suite, and all the separate custody gates in an explicitly ordered sequence
against one exact checkout. Individual green synthetic results are not a
substitute for validating the complete archive.

R18 adds preparedness/tools/private_release_preflight.py, a fixed-command
local-only orchestrator. It does not repair, rebase, publish, upload, browse,
or write to WordPress. It cannot approve accuracy, source-reading depth,
medical/food/water/fire safety, or an independent QD decision.

## Running on a genuine, complete, clean checkout

From the exact branch/commit you want to test, with all seven Claude
contributor refs fetched under origin/ and the frozen R14 parity manifest
available, run from the repository root:

~~~sh
git rev-parse HEAD
git status --porcelain=v1 --untracked-files=all -- preparedness
python -I -B preparedness/tools/private_release_preflight.py \
  --repo-root "$PWD" \
  --expected-head "$(git rev-parse HEAD)"
~~~

Optional local custody receipt (new file only; no overwriting):
--receipt "$PWD/preparedness/build/R18-PREFLIGHT-20261031-REVIEW.json".

The eleven fixed steps are: native validate.py, draft-only build.py,
the native unittest discovery with >=36 successful tests, R10 canonical
claim corpus, R11 WordPress draft-export byte parity, R12 rendered-citation
parity, R13 uncited-action triage, R14 outbound-link custody, R17 crosswalk
truth, R16 current safety-copy custody and R15 seven-cluster Git-object
parity against the frozen R14 manifest.

Before and after every step, exact HEAD and clean Preparedness working-tree
status are checked. Symlinked tools, manifest, build path and misleading
JSON approvals fail closed. Custody gates must return one JSON object
declaring release_state=HOLD and may_publish=false. JSON proofs are hashed;
the final receipt also hashes each stage's stdout/stderr.

**Success with exit code 0 means only all machine checks executed on that
exact local checkout.** The receipt still says HOLD and may_publish=false.
The git-ignored preparedness/build/ is the only generated directory.
R11 separately rejects stale or extra preview/WordPress draft exports.

## Evidence collected on October 31, 2026

- The new orchestrator's 60 synthetic/adversarial tests passed locally.
- A 715-test synthetic/adversarial collection passed using staged R9–R17
  source packages plus R18; this is NOT the native complete-repository test
  suite. The reconstruction lacks R8 claim_occurrence_audit.py and two
  dependent test modules were excluded. Without those exclusions discovery
  reported 717 tests with two import errors, not a green run.
- The authenticated R17 branch contained 19 Preparedness tools and 21 test
  files; R18 branched from 623ce032ce7ad409bf97d72f4520e14ca5edb14b.
  No original article bodies, source fragments, source crosswalk, taxonomy,
  public frontend or WordPress data were modified.
- Seven Claude contributor heads were rechecked:
  start=2122d856, shelter=5daeaf2d, food=4b009361, health=d2212d0c,
  hist-food=2acf65ca, hist-home=f654e600, hist-field=a5ce8a62.
- QA PR #157 remains draft at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa.
  Synthetic-fixture PR #169 remains draft at
  e9cd7766dac59d47ab467d8945269b9146c2aef5.
  Homepage PR #49 remains separate at
  10495883299d53596992c26a8987f629b2904670.
  Homepage PR #254 remains draft at
  8fa6fc52e034f511b96ae526f4a852e1bd76db04.

## Blockers and release criteria

The isolated runtime cannot resolve GitHub for a private clone, although
authenticated GitHub connector reads succeeded. Thus R18's eleven-step
CLI has NOT run against the actual 35 articles plus water planner on a
complete trusted checkout; native validate.py, draft build.py, complete
native test suite, rendered 36-item parity, and 216 actual Git-blob
comparisons remain unexecuted for R18. No hosted CI pass is claimed.

The existing source census contains 224 rows, 186 literal URLs, 30
unresolved shared-URL groups, 15 duplicate source-ID groups and 15 unread
original placeholders. The 1,959 citation occurrences have not been
independently human verified. One Start-cluster source-use explanation
remains open for human review. The food crosswalk source-head still
records the #169 fixture-head alias rather than the original author-head,
and its discrepancy must remain disclosed.

No human source reading-depth reconciliation, qualified clinical/emergency
safety review, independent QD approval or publishing authorization exists.

**Release remains HOLD even if the preflight eventually passes.** Do not
merge/publish drafts, touch WordPress/navigation or imply that source
integrity alone proves the factual or medical safety of the advice.
