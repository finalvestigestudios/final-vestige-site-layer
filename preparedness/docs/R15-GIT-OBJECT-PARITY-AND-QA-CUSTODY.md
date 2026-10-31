# Preparedness Archive R15 — seven-cluster live Git object gate

**Issue #136 | DRAFT / HOLD | may_publish=false**

R14 documents 72 SHA-1 Git blob pairs for the **29 cluster-authored article bodies + metadata**, and seven cluster notes / seven source fragments. Until R15, that R14 JSON was an unexecuted assertion. R15 independently checks the contributor commit object, frozen R13 integration object and current integration HEAD object for each of those 72 paths (216 checks total). The validator reads Git objects, checks seven current remote contributor refs, rejects symlinks, unexpected paths, missing articles or fragments, stale metadata, and any source/reading-depth file drift. It always emits HOLD; it does NOT validate medical safety, source content, external links or facts.

## Exact coordination, October 31, 2026

The seven contributor branches were read via the authenticated GitHub Git-ref endpoint. Their observed heads are:

| Branch | SHA |
|---|---|
| claude/prep-start-bbfeb8 | 2122d856fce9f64887c16df3d52e64be9f59a55b |
| claude/prep-shelter-5e1e0e | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 |
| claude/prep-food-ccdc55 | 4b009361277ea1d4617b368f5d45104c7318b284 |
| claude/prep-health-837444 | d2212d0ca0750817d3929865d3069835980faf20 |
| claude/prep-hist-food-b81f19 | 2acf65ca3efa9b4b5db7976f379b9ea693be43a4 |
| claude/prep-hist-home-0e0e38 | f654e600f89c321a480dd8f055be4d13d0673490 |
| claude/prep-hist-field-9db767 | a5ce8a62f168db05c95232e3eb385dccd0d19e7f |

R14 HEAD: d5c14e58e309d2a831fe77fd7f7a1d94594ba332.
Preparedness integrated 35-article baseline: c8df99cc661e518e93e58e1cc1ea3d7256f58643.
Homepage integration (read-only coordination): 43285edee1604b873bf09bfcc0fb7eb0be90f79d.
The seven contributor histories remain graph-diverged from integration; content parity does not imply Git ancestry.

### Outstanding single provenance difference

The START cluster's preparedness-real-households.meta.json has contributor blob a0c3a09143a825560b5a5ed79d857b7402bfa295 and integrated blob ba840917f34634ccd634c488eeca4a8a6b3a8fe2. Authenticated content retrieval confirmed the only changed top-level key is source_use: the integrated record added a Ready.gov source-use scope explanation. This remains NEEDS_HUMAN_DIFF_REVIEW. The original article body is unchanged. The new gate does not auto-accept this discrepancy.

### Independent QA proposals inspected but not merged

**PR #157** is a draft at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (base 10f58fed1ba808056813064ca5f9680589db8da1). The actual patches replace risky household main-breaker drill language, improve product-specific refrigerated-medication advice, set the four Start Here taxonomy gate flags, update a source fragment and add tests. Candidate improvements still need independent source / safety review and integrated native testing; the large taxonomy diff is largely reformatting, so do not blindly cherry-pick.

**PR #169** is a draft at e9cd7766dac59d47ab467d8945269b9146c2aef5 (food base 4b009361277ea1d4617b368f5d45104c7318b284). It isolates source-upgrade tests inside a temporary copied fixture and uses a synthetic unverified citation rather than an evolving real source. It has not run native CI on that exact head. Do not merge or count as QD PASS.

## Trusted checkout validation command

Fetch all seven exact contributor refs and the frozen R13 commit into a trusted private checkout. Then run:

    python -I preparedness/tools/cluster_git_parity_gate.py --repo-root . --manifest preparedness/docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json --current-integrated-sha <CURRENT_R15_COMMIT_SHA> --receipt /tmp/fv-r15-HOLD.json
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The first CLI only audits Git provenance and records a local HOLD receipt. The latter three commands remain independently required. If historical contributor objects or remote tracking refs are missing, fail closed, fetch exact refs, and rerun. Never infer PASS from a fixture result.

## Verification and release blockers

**Locally executed:** 88 R15 tests, and 545 R10–R15 tests, all passed. The R15 test suite exercises a temporary real Git repository, symlink rejection and 68 independently mutated synthetic graph records. Local source/test Git blobs were compared to uploaded GitHub blobs.

**Not executed:** complete native validation/build, live 72-object Git CLI, real 35-article citation safety suite and hosted CI. This container cannot resolve github.com or api.github.com to obtain the private full repository checkout. Six integration-owned articles and the separate water planner remain outside this cluster-specific graph; native corpus R10–R14 gates still cover them.

**HOLD:** 30 shared-literal-URL groups require human reconciliation; 15 original unread base-source placeholders remain unread; all 1,959 citation occurrences / 367 article-source relationships require appropriate independent evidence review. Qualified review remains needed for consequential water, food, medication, infant, fire, generator and carbon-monoxide instructions. No publishing, WordPress/CMS changes, navigation changes, or QD approval in this branch.
