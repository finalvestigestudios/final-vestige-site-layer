# Preparedness per-citation source-scope review queue — draft/HOLD

**Owner:** Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136). This document and its code are deliberately limited to unpublished Preparedness Archive content. All 35 long-form articles and the one local water planner remain drafts; **no public WordPress writing, navigation, Focus lead-magnet, or homepage changes** are authorized.

## Why another reconciliation tool?

The existing `sources/crosswalk.json` preserves every duplicated URL, `article-evidence-lock.json` pins article bytes, and the validator blocks unauthorized publishing. They are necessary but do not give a reviewer one easy deterministic view of **which article cited which exact contributor reading**, the claim the author attributed to that reading, the actual source notes and the human checks still missing.

`tools/source_review_queue.py` constructs a complete, stable **article ↔ source-row** ledger. Identifiers include contributor origin, zero-based original source-file row index, source ID and URL; citations are mapped to their contributor's own reading scope or base source, never an unrelated contributor's verified version. It *does not collapse duplicate URLs, copy over a more permissive source check, or erase a contributor's partial reading limitations*. A dedicated section lists every repeated-URL group, the exact original record identities, affected articles and unresolved human scope decisions.

The report is derived only from local original JSON and article metadata; no new factual medical or safety recommendations are introduced. It is **not** a verification of source truth, human link availability or safe advice.

## Exact locked source-corpus baseline

The latest integrated Start contributor revision is `2122d856fce9f64887c16df3d52e64be9f59a55b`. The initial integrated source corpus is pinned by the existing freeze; its eight original source files currently contain:

| Contributor | Distinct recorded source rows |
|---|---:|
| base | 34 |
| Start Here | 27 |
| Shelter | 31 |
| Food | 30 |
| Health | 21 |
| Historical Food | 28 |
| Historical Home | 27 |
| Historical Field | 26 |
| **Total** | **224** |

The connector's read of these eight unmodified JSON files on 2026-10-30 found **209 machine-date-marked records; 15 not so marked; zero `human_link_check: true`; 186 literal unique URLs and 30 groups with repeated URLs**. None of those figures establishes independent source validity. The source **FEMA V-1008 power outage PDF** appears as four separately retained contributor readings (Start, Shelter, Food, Health), including Start's explicitly incomplete pages-read statement.

All **35 original article bodies**, companion metadata, the local water planner, source rows, shared-URL status, owner-map and input-provenance records are left unchanged by this draft PR. The only modifications to existing files are one machine-verified count assertion corrected from 208 to 209 after Start's additional source row, and a stricter **blank/non-text source-use note** rejection; neither approves content.

**Independent connector-level cross-check on the exact draft head:** all 36 body/metadata pairs were read, yielding **367 distinct article–source citation pairs**, **367 matching nonblank article-specific source-use entries, zero missing or extra source-use keys**, and all 35 long-form articles above the 1,800-word minimum (the planner is a shorter separate tool). These are mechanical copy/inventory checks, not an independent source read or a proof of safety.

**Safety-state nuance that must remain visible:** 30 articles/tools are marked `safety_review: pending`, two base articles are marked `approved` by a prior founder response (making-water-safer and salt-beef-salt-pork-age-of-sail), and four non-actionable historical articles are labelled `not-required`. All **36 remain unpublished drafts**. The two earlier founder approvals did not provide item-by-item expert review and are not independent medical/food safety/QD approvals; those articles still have incomplete human link checks and must pass the exact-copy release gates.

## Review workflow

1. Check out **the exact PR head** locally with actual repository access. Do not run on a different branch and report it as this head.
2. Run the frozen-input verifier and the existing validation/build/full test suite:
   ```bash
   python -I preparedness/tools/evidence_freeze.py
   python -I preparedness/tools/validate.py
   python -I preparedness/tools/build.py
   python -I -m unittest discover -s preparedness/tests -v
   ```
3. Build the detailed **offline review queue** without publishing:
   ```bash
   python -I preparedness/tools/source_review_queue.py --output preparedness/build/source-review-queue.json
   python -I preparedness/tools/source_review_queue.py --require-release-ready
   ```
   The second command is **intentionally nonzero**: this tool is for reviewer evidence, never a self-attested QD or safety approval. The `build/` directory is git-ignored. The first command may succeed while all independent human-review gates remain blocked.
4. For each of the **30 shared-URL groups**, inspect all source-file rows independently, their read limits, individual article use statements, source version/date, and real URL/redirect state. Preserve origin-specific differences even if the URL is identical. Resolve only with review evidence, a named reviewer, date and actual scope notes. A superficial canonical URL or one contributor's successful access never qualifies all contributors.
5. For consequential water, infant formula, medication cold chain, fire/generator CO, food temperature/canning and evacuation guidance, require the designated qualified human safety review plus independent QD on **exact frozen copy**. Never treat a saved fingerprint as a human signature.
6. If the editorial and safety reviewers have actually approved, separately obtain explicit founder authorization before **any** WordPress publishing/nav write. All deliverables in this PR are drafts and read-only tooling.

## Test design and current verification

- `tests/test_source_review_queue.py`: **18 synthetic-only negative/positive tests** covering contributor own-scope selection, null/blank source-use notes, duplicate source IDs and URLs, changed row positions, declared/actual crosswalk mismatch, deterministic hash, no-network/no-write behavior and fail-closed output. **All 18 were executed and passed** on the authored identical local module/fixture copies in the Python container on 2026-10-30; full-repository execution is a separate requirement.
- `tests/test_source_review_queue_corpus.py`: **12 additional exact-corpus assertions** for 35+1 inventory, every source row, 209 machine-marked rows, 186 URLs, 30 shared URL groups, four FEMA reading scopes, original source selection and two negative tests against the primary validator. These tests were **added but not yet executable** on a checkout of this private repository in the local container.
- `tests/test_integration_audit.py` source count has been corrected to 209. Its previous expected count of 208 was demonstrably stale after Start's extra FEMA source row.
- The full existing 106-test suite plus **30 new test definitions** is not a 136-test **PASS** until those cases actually execute on this precise head. GitHub-hosted CI and browser/WordPress draft rendering are also outstanding.
- Current expected release status **HOLD**, with all source links still needing human confirmation and no qualified safety/QD signoff.

## Branch interfaces and independence

Stacked on the latest integration safety branch PR #186 (`cde18d7a6a5cb50bbcb445e4d5246d240906baec`), which stacks on PR #179 and the 35-draft integration PR #176. Independent safety QA PR #157 and synthetic food fixture PR #169 are **not closed, merged or silently certified** by this change. All seven Claude contributor lanes were compared against the exact input baseline on October 30; six matched their recorded head SHAs. The Food contributor itself sits one commit before the intentionally integrated food review-fix SHA in PR #169; this is accounted for rather than mistaken for lost content. PR #49 and its homepage release remain untouched.

**No safety claim, publication permit, clinical validation, or QD-PASS can be inferred from a zero structural-error report.**
