# R95 — Full Original DOM / Link-Attribute Custody (PRIVATE HOLD)

**Issue:** #136. **Branch:** review/preparedness-r95-complete-dom-attribute-custody-hold-20261103. **Parent:** R94 3db0e16eea0cfb4e61c304759a92e7ef669a8067. **Scope:** additive tooling, additive tests, this reviewer protocol and one private workflow. **No public/CMS/navigation/homepage write.** The branch is for draft review only.

## Why R95 exists

R93 verifies every original citation-to-source ID/URL at the rendered source-list and inline-marker layer. R94 protects original editorial reading depth and script bytes. **Neither comparison alone binds every originally authored HTML attribute and element to its exact rendered location**. A draft could keep the same words and source citations while introducing a different hyperlink destination, a hidden display:none warning, a tracking ping, an event handler or a zero-text iframe. R95 addresses that transport-integrity gap; it is not an accuracy or safety certification.

## Exact method and fail-closed invariants

1. Read only existing original article/tool body files and their immutable contributor-scoped source registries; preserve the 35-article/6-planned-tool distinction.
2. Independently expand only the three documented literal author tokens (cite, link, inline-js) without calling the builder's token resolver. Cites are removed for the original DOM witness; the generated citation superstructure is ignored only within the actual rendered .pa-body. R93 independently verifies those markers and original source-use evidence.
3. Generate ordered HTML event sequences including **all element starts/ends, attributes, authored link targets, comments and text**. Attribute names are sorted for deterministic order while preserving values; text entities are decoded equally on both sides; adjacent text events are coalesced around removed citation markers. Comments and zero-text elements are not silently discarded.
4. Compare the original event sequence byte-for-byte after canonical JSON serialization. Fail on any inserted/removed/moved tag, link reassignment, altered attribute (href, rel, ping, onclick, style, aria, id, class, form target), injected invisible markup, lost copy, or swapped claim/link association. Detect duplicate HTML attributes and incomplete/duplicated .pa-body wrappers.
5. Preserve the author's treatment of a planned-but-unwritten article: a link token whose target has no complete draft body must be plain text, never an invented clickable URL.
6. Independently rerun R94's original-reading-depth check and R93's exact source/citation check against the **same 36 actual private drafts**. Do not reclassify 41 historical research/reviewer packets as 41 importable WordPress files.
7. Return a canonical SHA-256 sealed reviewer manifest. Full per-document witnesses print only when explicitly requested with --private-json-stdout; the default command omits them. Every row says HOLD, NOT_REVIEWED and may_publish=false.

This is a **transport preservation gate only**: even a matching rendered body can contain inaccurate or dangerous original guidance, a broken URL, a misleading citation or an unreviewed historical method. Retaining markup is not human source verification, qualified medical/emergency safety review, browser accessibility testing, independent QD pass or publication authorization.

## Native read-only diagnostics

Run on an **exact pinned checkout**, never in a shared mutable contributor worktree:

    python -I -m unittest discover -s preparedness/tests -p test_r95_dom_attribute_custody.py -v
    python -I preparedness/tools/r95_dom_attribute_custody.py
    python -I preparedness/tools/r95_dom_attribute_custody.py --private-json-stdout > /tmp/r95-private-review.json
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The build writes only **local, private WordPress-ready draft files** to preparedness/build/; it never invokes WordPress APIs or CMS writes. The same commands are exercised by the R95 PR-triggered private GitHub workflow. Verify that the R95 event-sequence manifest and SHA seal are stable across two clean runs before any review decision. Never replace a failed test with a skip, weaken URL/safety gates, or claim QD PASS.

## Frozen inventory, not a release claim

The prior R94 accepted evidence records **35 original articles + 1 actual tool draft = 36 private draft bodies**, with **6 planned tools** (5 lack a complete importable draft pair). R94 proved **4,032 editorial blocks**, R93 separately matched **1,959 citation occurrences**, and the historical seven-cluster research crosswalk retains **41 reviewer packets / 2,173 original historical citation occurrences**, many not identical to a current draft representation. These counts are **inputs to recheck**, not a substitute for a successful R95 exact-head execution.

R95 does not collapse distinct URL-sharing source identities or alter the 30 unresolved URL-collision groups. It never changes publisher safety states, source metadata, original article bodies, historical witness snapshots or QA approvals. All original reading scopes and evidence remain intact.

## Independent coordination / blockers

- Independent QA PR #157 is a separate unmerged Start Here draft. Safety wording and classification still require qualified review.
- Synthetic-fixture PR #169 is a separate unmerged Food test-only draft. Its _dup_test.json fixture remains a shared-worktree mutation on that branch; R95 does not import it or mark it resolved.
- Parallel R92 PR #766 retains its distinct literal-URL provenance workorders and unresolved source-variant mismatch. R95 builds on R94, not R92; no R92 change is silently rebased here.
- Homepage #49 and Experience 2.0 #604 remain entirely outside this scope.
- The mandatory 13-stage machine integrity was **FAILED/INCOMPLETE** on R94. A successful private R95 diagnostic is not a substitute. Five historical contributor-branch deltas, 30 unresolved literal URL collisions, 15 safety exceptions, 22 editorial decisions, qualified emergency-guidance assessment, human link/claim review, actual WordPress/browser accessibility testing and independent QD remain unapproved.

**Release state: HARD HOLD.** No merge, release, WordPress draft import, navigation change, or public publishing is authorized by this work.
