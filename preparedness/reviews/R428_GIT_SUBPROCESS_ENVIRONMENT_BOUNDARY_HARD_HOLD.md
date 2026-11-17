# R428 — Git query environment custody: read-only safety handoff (Issue #136)

**DRAFT / HARD HOLD. This is NOT article review, medical/food/emergency safety approval, independent QD, native build, or release authorization.** Scope: Preparedness source/citation integration only.

## Demonstrated defect before patch
In an isolated disposable Git fixture based on the exact R427 validator source, the caller set `GIT_TRACE` to an external trace file while passing a nominally clean `env=` to `closure()`. The R427 guard returned `execution_input_closure_ok: true`, yet Git created an **18,015-byte trace outside the repository**. This contradicts the former read-only claim and demonstrates that the Git subprocess inherited the real OS environment instead of the checked Python-review environment. No user/production repository or private file was involved.

## Change (stacked directly on R427)
- Update `preparedness/tools/r427_execution_closure_gate.py` to strip inherited `GIT_*` selectors from Git subprocess environment, pin no-lock/no-system/no-global Git configuration, prevent lazy fetch, disable local `core.fsmonitor` and untracked-cache invocation, and require no interactive prompts.
- Explicitly HOLD when supplied audit environment includes unapproved Git selectors, index/worktree/object overrides, trace/Trace2 writers, injected config slots, external diff or SSH command overrides. Limited benign Git environment keys remain permitted to avoid CI false positives. This prevents an apparent structural-green receipt from contaminated Git process settings.
- Add `preparedness/tests/test_r428_git_env_sandbox.py`: synthetic disposable local-repository test matrix of 40 untrusted Git variables, trace file creation, wrong index/worktree/repository, Git config injection, and local fsmonitor command side effect. All tests enforce no publication, sale, or qualified safety approval.

## Test evidence, exact code files
- **57 new tests PASS** in one local Python run, 11.068 seconds.
- **174 tests PASS together** (57 new + 64 R427 inherited + 53 R426 inherited) in one separate combined local run, 27.338 seconds; Python compilation PASS.
- The two exact committed source/test Git blobs were fetched back and matched the locally executed bytes: updated tool `365b9cb12e5ff1de783bb0dfeda30f68dcc35bac`; new test `442662837dfa148eb4d9a0a522a0a69dbc1953ed`. These are **synthetic local tests only**, not a native repo-wide suite or build.
- The prior prepatch red-team trace file is direct observation, not a remote production failure claim.

## Still missing / release blockers
1. Actual complete trusted nonshallow checkout with R397 docket, nine original contributor refs, original manuscripts and 35 authentic WordPress plus 35 private-preview export pairs; full native `python -I preparedness/tools/validate.py`, `build.py` and `unittest discover` not run.
2. Qualifying source-to-claim and original-manuscript fork adjudications, human link checks, qualified food/water/emergency/medical/child privacy review, real WordPress/browser/mobile/print QD; pending independent PRs #157 and #169 (remediation #2205 separately unmerged). No automated validator can create QD PASS.
3. Hosted GitHub Actions for R427 showed FAILED and zero job steps; cause unconfirmed. R428 hosted CI must be independently checked.
4. No independently verified purchasable, rights-cleared FV Preparedness SKU, merchant fulfillment/refund evidence, verified Grok family-contact post `asset_id`, or revenue receipts. No paid CTA or conversion claim is authorized.

**No merge; no WordPress/CMS, navigation, public publication, social scripts/posts, email, tracking, merchant/affiliate activation or spending.** All 35 article identities, source/citation records, historical fork candidates, safety states, URLs, and contributor branches remain untouched by this change.
