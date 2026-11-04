# R110 — Adjacent uncited caveat custody (Issue #136)

**PRIVATE REVIEW WORKORDER — STRICT RELEASE HOLD.** No source, medical, qualified safety, or independent QD approval. No public publishing, CMS, navigation, merge or production write.

## Newly identified review gap

R109 identifies when the text *inside a citation-bearing paragraph* changes while the source ID stays the same. But a contributor can keep a citation-bearing paragraph byte-for-byte identical and quietly delete or reverse the **separate uncited paragraph immediately before or after it**. This can turn a qualified claim into an apparent unconditional instruction without changing either the citation count or its R109 neighborhood fingerprint.

R110 adds a **read-only, deterministic, SHA-256-only, reviewer-only** cross-paragraph context signal. For each citation occurrence, it records fingerprints of up to two uncited neighboring text blocks on each side, stopping at a section heading, cited block, or section boundary. Section-heading fingerprints and warning-class/role presence are also monitored. It flags changing uncited context and warning presence/length, but exports no article paragraph text and cannot infer factual truth or medical safety.

## Engineering contract and boundaries

- Independently reconstruct R109's human-review workorder and R107's exact historical/current contributor branch lineage. Before analyzing a changed body, re-read both exact Git blobs and match original/current Git object IDs.
- The 23 contributor-file changes in five advanced branches remain R107/R108 human-review items. R110 augments only the **seven changed article bodies**; it is not a merge of revisions or a full verification of 35 articles.
- Text fingerprints are **not signed**, not a source-support verdict, and not author/medical/QD approval. Original author-specific `source_use` records, 30 shared URL groups, 15 safety exceptions and 22 editorial decisions remain subject to humans checking the actual primary/regulatory documents.
- The scope is deliberately conservative: text-model HTMLParser is not CSS/JS computed visibility, cannot prove print accessibility, does not follow references to external advice, and cannot infer what a reader would interpret. All changed advice requires separate source/qualified safety review even when hashes are equal.
- Strictly no original article body, registry, source fragment, taxonomy, canonical route, safety status, 13-stage mandatory release workflow, website, homepage, navigation, or WordPress changes. All original drafts remain private.
- Reject invalid UTF-8 and >2MB bodies; cap blocks/citations; do not include article prose, sensitive reading notes, or safety recommendations in diagnostics. Both changed and unchanged cases remain `may_publish=false`.

## Exact checkout commands

```bash
python -I -m compileall -q preparedness/tools/r110_uncited_caveat_custody.py preparedness/tests/test_r110_uncited_caveat_custody.py
python -I -m unittest discover -s preparedness/tests -p 'test_r110_*.py' -v
python -I preparedness/tools/r107_exact_branch_progression_adjudication.py --repo-root .
python -I preparedness/tools/r108_source_citation_change_impact_crosswalk.py --repo-root .
python -I preparedness/tools/r109_citation_context_custody.py --repo-root .
python -I preparedness/tools/r110_uncited_caveat_custody.py --repo-root . --json > /tmp/r110-private-not-approved.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

**Verification disclaimer:** A separate local scratch implementation passed **82 synthetic/adversarial tests** under Python 3.13. These do not establish exact GitHub-head regression, native validation, draft build, source quality, or qualified safety signoff. Require fresh exact-head CI; if jobs dispatch with 0 steps, mark **UNVERIFIED**, not PASS. Original R15 historical parity must continue failing closed until 23 changed contributor items and associated evidence receive independent adjudication. No repinning as a shortcut.

## Human reviewer handoff

Review R107's 23 changed paths and R108's author-scoped source IDs/reading scopes, then R109's own-paragraph citation drift and R110's separate adjacent uncited caveat drift, side-by-side with original and revised prose. Inspect whether removed qualifiers, separately positioned advisories, changed section headings, or warning-state changes alter the reasonable interpretation of emergency advice. Verify each affected claim against primary/regulatory source readings and record source date, reviewer, review date and qualified safety decision OUTSIDE these automated outputs. Keep `human_source_review=NOT_REVIEWED` until that occurs. A zero-drift result does **not** mean the content is safe or accurate.

## Cross-agent coordination

On Nov 3 2026 (America/Los_Angeles), verified the seven contributor branch SHA refs, separate Preparedness RC, independent QA drafts #157 / #169 and homepage PRs #49 / #604 against GitHub. All 12 matched their R109 pinned commits. PR #157 still carries candidate Start Here safety wording (unmerged); PR #169 still has a shared-source-tree `_dup_test.json` write despite its separate `_upgrade_test.json` being sandboxed; do not treat either as landed. Homepage PRs unchanged. Issue #136 remains authoritative.

**Final decision: HOLD.** Original 35 article drafts and one complete tool unchanged/unpublished; five planned tools unfinished. Actual browser/print checks, claim-specific independent review, qualified medical/emergency guidance review, complete 13-stage mandatory integrity, and independent QD still required.
