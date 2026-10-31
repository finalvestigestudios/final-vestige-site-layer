# Preparedness R8 — claim-level citation occurrence custody (DRAFT / HOLD)

Issue #136. Parent PR #219 at a0692000bf6e7b2740fdf283023c0296a0f05a92. No CMS operations.

## Purpose

R7 verified 367 distinct article/source relationships for 35 unpublished articles plus one unpublished water-planning tool. One article can cite the SAME source multiple times for different factual propositions. A single broad source_use note cannot prove that every sentence invoked by that citation is supported by the actual referenced source section. This is a source-review coverage risk, not an assertion that a particular article is false.

R8 adds tools/claim_occurrence_audit.py, an offline deterministic **every inline citation occurrence** review queue. It uses an HTML parser for visible text, preserving the nearest semantic paragraph/list item/table cell/context instead of silently flattening nearby articles. Every request binds the original frozen article evidence fingerprint, full body SHA256, inline occurrence ordinal, specific contributor physical source row key, URL, original contributor support/reading limitations, article source-use note, paragraph-level context excerpt and full hash. Editing a claim, an article, a contributor's support or reading scope, or an article-specific note makes existing request identities stale. Long blocks are marked explicitly as excerpts and retain the full hash. Source rows and literal shared URL groups are never merged.

The parser rejects invisible cites in comments, attributes, script/style/template/noscript, orphan citation-only blocks, missing use notes, foreign contributor source rows, duplicate routes and identity conflicts, non-draft publish state and unknown safety states. It records the inherited metadata state but marks EVERY claim PENDING_INDEPENDENT_HUMAN_CHECK, even where metadata had a founder-marked "approved" or historical "not-required" state.

The baseline requires **36 draft objects, 367 distinct article/source pairs, 224 physical source records and 30 shared-URL groups**. It measures total inline citation OCCURRENCES from the actual checked-out source; no count was guessed. Every output remains RELEASE HOLD, may_publish=false, verified_citation_claims=0, reviewed_claim_occurrences=0. Human review of original external documents/dated sections and qualified safety review remain prerequisites.

## Exact-head reproduction

From repository root:

    python -I -m unittest discover -s preparedness/tests -p 'test_claim_occurrence_audit.py' -v
    python -I preparedness/tools/claim_occurrence_audit.py --json-out preparedness/build/private-claim-occurrence-queue.json --csv-out preparedness/build/private-claim-occurrence-queue.csv
    python -I preparedness/tools/evidence_freeze.py
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Private build directory must exist. Without --out, CLI prints only HOLD summary. Exports are restricted to files directly inside preparedness/build; symlinks/traversal/nested paths rejected and CSV formulas escaped. No WordPress writes, publication, nav, homepage, newsletter or permissions changes.

## Test results and release limits

**80/80 Python synthetic tests executed locally and passed** using the exact source and test file bytes committed to PR R8, covering claim spans, hidden or stale citations, source origin/metadata drift, safety fail-close, deterministic digests and export security. Still not executed against the complete 35-article GitHub checkout; local Python container cannot DNS-resolve the private repository. GitHub source readback and independent checks need to be done at exact PR head. No hosted CI, human URL inspection, clinical/food/CO/water review, WordPress staging, or QD PASS. Publication remains HOLD.

The integration is additive-only: no modification to original 35 article bodies/36 metadata/source fragments, seven Claude clusters, existing source review/discrepancy pipeline, QA PR #157, fixture PR #169, homepage or WordPress site. Source/citation verification and separate founder authorization remain outstanding.
