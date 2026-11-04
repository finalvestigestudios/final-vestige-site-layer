# R109 — Citation neighborhood custody / reviewer-only evidence (Issue #136)

**PRIVATE WORKORDER. Drafts only. RELEASE HOLD. No safety, factual, source, or independent QD approval. No public writes.**

## Why the R108 crosswalk needs an additional gate

R108 reports changes in *counts and identities* of article citations across the seven changed article bodies identified by R107. A contributor can keep exactly one `{{cite:source-id}}` before and after a revision while changing a statement from a cautious, qualified description into an unsupported directive. Git blob custody, identical source IDs, and unchanged citation totals do not show that the same source supports the revised sentence.

R109 adds a deliberately conservative **same-ID citation neighborhood diff**. It parses article HTML into paragraph/list/table/heading text contexts, normalizes formatting whitespace, and compares **SHA-256 fingerprints of the text surrounding each source marker** between frozen and current Git blobs. Same source IDs and counts with changed text contexts generate reviewer queue entries. Changed warning context and citations embedded in comments, attributes, hidden elements, scripts and styles are independently reported. It does not output paragraphs, private research notes, numerical emergency formulas, or supposed source accuracy judgments.

### Safeguards

- Re-run the R107 seven-branch exact-commit ancestry/workorder and R108 Git-OID verified source crosswalk before reading article revisions; compare their frozen and current bytes against the original recorded Git object IDs. Neither R109 nor any reviewer may silently re-pin historical contributor SHAs.
- Report unchanged citation identity but changed text context separately from citation-ID adds/removes and changes in occurrence count.
- Keep HTML comment/attribute/script/style/hidden-text markers separate from text-model-visible citations. Detect malformed citation markers and obviously unbalanced HTML as review warnings.
- Detect changes in scoped warning-text fingerprints, including warnings wrapped in a parent container.
- Preserve text-free result format, with deterministic sort order and non-signature SHA-256 checksum; do not infer editorial, medical, or factual approval.
- Cap per-body size, contexts, and citation volume, reject bad UTF-8, and keep all outputs private to the review checkout.
- Non-article paths remain in R108's 23-file source/metadata/research/test queue. R109 only adds deeper inspection of the seven changed article bodies; it **does not** claim all 35 articles are fact-checked.

### Deliberate limitations

Python's `HTMLParser` is **not a browser renderer or computed-style engine**; project/theme CSS, content inserted by JavaScript, screen reader behavior, HTML repair by browsers, and responsive/print presentation still require actual browser/accessibility review. Text context hashes are *review prompts*, not proof that any source supports a claim. This does not replace the R14 source-collision review (30 shared-URL groups), 15 safety exceptions, 22 editorial decisions, five incomplete tools, qualified emergency/medical review, original R15 mandatory parity, or independent QD. The historic R15 parity must remain FAIL CLOSED while contributor heads are ahead of the frozen manifest.

### Exact checkout verification

```bash
python -I -m compileall -q preparedness/tools/r109_citation_context_custody.py preparedness/tests/test_r109_citation_context_custody.py
python -I -m unittest discover -s preparedness/tests -p 'test_r109_*.py' -v
python -I preparedness/tools/r107_exact_branch_progression_adjudication.py --repo-root .
python -I preparedness/tools/r108_source_citation_change_impact_crosswalk.py --repo-root .
python -I preparedness/tools/r109_citation_context_custody.py --repo-root .
python -I preparedness/tools/r109_citation_context_custody.py --repo-root . --json > /tmp/r109-PRIVATE.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

**Local isolated synthetic tests:** 80/80 passed (Python stdlib, no checkout, no network, no article-source edits). **Repository-wide 9,000+ regression and exact Git crosswalk results on this branch are NOT verified** until an exact-head hosted runner executes; any zero-step GitHub Actions failure is a dispatch blocker, not a PASS.

## R109 review protocol

For each changed article, take R107's original and current contributor Git objects, then R108's changed-source-ID and `source_use` associations, then R109's citation-neighborhood drift. For every revised paragraph or safety statement, reviewers must inspect the accessible primary/regulatory source within the claim's specific scope, record source date and their own review date, and independently decide if the emergency guidance is fit for publication. Identical hashes cannot automatically count as confirmation; new, changed, or moved citations must not overwrite original author-specific evidence. Preserve the original article draft pending review.

## Coordination / boundaries (checked November 3, 2026)

Seven Claude cluster refs and the separate release candidate remain at the pinned 12-branch SHA set in the private R109 workflow. Start Here QA PR #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and food-fixture PR #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) are open drafts and unmerged. **Independent PR #169 still contains a tree-writing `_dup_test.json` test**, although the *R108 integration tree's own* `test_preparedness.py` already uses an isolated temporary sandbox; this discrepancy must be resolved by the owner of that independent PR, not assumed merged. Homepage PR #49 (`10495883299d53596992c26a8987f629b2904670`) and flagship PR #604 (`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`) are coordinator-only references and must remain untouched.

**Release disposition: HOLD.** No WordPress writes, navigation changes, merges, public publishing, or QD PASS.
