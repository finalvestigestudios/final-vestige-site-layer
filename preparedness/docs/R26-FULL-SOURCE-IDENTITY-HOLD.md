# R26 — source identity parity and unabridged citation evidence (Issue #136)

**DRAFT ONLY / HOLD / may_publish=false.** No WordPress write, navigation, public publishing, qualified medical or emergency-safety review, source-claim factual verification, completed human crosswalk review, or independent QD approval is implied.

## Finding and scoped correction

The R25 mandatory citation-review gate compared the renderer's selected source against the frozen contributor variant by `_origin` **only**. A substituted row from the same contributor—changed URL, publisher, verified date, title, reading scope or safety-approval-looking metadata—could pass that equality check. This is a concrete *machine provenance* ambiguity, not evidence of an actual article having an incorrect source.

R26 updates the **already mandatory thirteenth preflight stage** (`citation_fallback_review_gate.py`), with no changes to its step order, other gates or the pinned GitHub Actions workflow:

- Check canonical JSON identity of the **entire rendered source row** against the independently selected contributor source variant. Compare types, not merely the contributor label. A source variant's `id` must match its citation ID.
- Preserve **the complete original source record** alongside the original unabridged `supports`, `notes`, article-specific `source_use`, URL, origin and existing reviewer-context excerpt. A SHA-256 digest of the canonical source record protects it from silent metadata substitution.
- Provide original article HTML and article-specific `source_use` SHA-256 hashes plus the **zero-based Unicode codepoint offsets** of every occurrence of each `{{cite:...}}` token, so reviewers can return to the full claim context in the original unchanged article rather than relying on a clipped excerpt.
- Require valid calendar dates for `verified_on`; a date matching `YYYY-MM-DD` but impossible on the calendar must fail.
- Keep the original 35-article + water tool census and 1,959 citation-occurrence / 367 relationship / 43 base fallback / 30 shared URL group **frozen structural contract**. Preserve `release_state=HOLD` and false publication/review authority markers.

This **does not** make the original URLs true, extend the reading depth of a contributor, reconcile duplicate URLs or certify that any passage supports any emergency instruction. The full source record is retained for human examination, not promoted to an approval.

## Independent coordination (2026-10-31)

The seven original Claude branches compared *identical* (ahead 0 / behind 0) with their frozen contributor commits: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `4b009361277ea1d4617b368f5d45104c7318b284`; health `d2212d0ca0750817d3929865d3069835980faf20`; hist-food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`; hist-home `f654e600f89c321a480dd8f055be4d13d0673490`; hist-field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.

Independent QA PR #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and synthetic-fixture PR #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) remain separate drafts. Their actual modified filenames and safety/test patch contents were inspected. Do not overwrite newer Start medical/electrical wording with #157; do not equate #169's test-fixture head with the food contributor's original commit. Homepage PR #49 (`10495883299d53596992c26a8987f629b2904670`) and flagship PR #254 (`8fa6fc52e034f511b96ae526f4a852e1bd76db04`) were checked and left untouched.

## Executed evidence, not release authorization

On the local reconstructed R16–R25 engineering subset plus R26, `python -I -B -m unittest discover -s preparedness/tests -p test_r26_exact_source_identity.py -v` executed **74/74 R26 tests**, including 47 same-origin source-substitution mutations, 15 impossible-date cases and 12 evidence/digest and safety-contract tests. The inherited R25 suite executed **63/63 passes**. An available reconstructed suite excluding the R14 outbound-link module, whose production dependency was absent locally, collected **725 tests: 723 passed, 2 skipped**. The full unadjusted reconstructed suite produced an import error for absent `outbound_link_custody.py` and is *not green*.

Git clone of the complete private checkout fails with `Could not resolve host: github.com`. The native `validate.py`, `build.py`, complete repository tests, full 13-stage preflight and live WordPress draft export remain **unexecuted on this exact R26 checkout**. Prior GitHub Actions runs failed before step execution; an Actions green check is not asserted.

## Publication prohibition and remaining human work

Resolve the 30 shared-source reading-depth groups, 43 base-source fallbacks, 1,959 citation occurrences, food provenance alias and one Start metadata source-use discrepancy. Independently verify accessible links and claim support; secure qualified emergency/medical review and independent QD approval. No article, tool, source register, crosswalk, taxonomy, CMS, home, nav, or website production edits are authorized by this patch.
