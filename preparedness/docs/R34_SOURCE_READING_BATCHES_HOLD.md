# R34 — Source-reading review batches (DRAFT / HOLD)

**Owner:** Preparedness Archive integration, Issue #136. **Release:** HOLD; no public publishing, CMS, navigation, production homepage changes or QD PASS.

## Why this exists

R33 produced 1,959 prioritized *citation-occurrence* work items. R34 adds a second, independently fingerprinted **human reviewer batch index** with one distinct card for **each of the 367 original article/source-use relationships**. A card retains the complete source record selected by its original contributor, its full reading-depth `supports` and `notes`, its full article-specific source-use explanation, source URL and origin, and every original citation offset/context from that relationship. All content remains unchanged and unapproved. This is a custody/workflow organizer, **not** a verdict on source accuracy or safety.

- Frozen machine input totals: **35 articles**, **1 water tool**, **1,959 citation occurrences**, **367 source-use relationships**, **43 cross-cluster fallback relationships**, **30 shared-URL groups requiring human review**.
- Default reviewer batches: at most **12 relationships** per batch; estimated 31 batches when 367 cards are intact. No citation is dropped or collapsed; repeated URLs coordinate reviewer work **without** merging distinct contributor readings.
- Source and article-specific use are verified against frozen UTF-8 SHA-256 identities. Reviewer-card and batch IDs use canonical JSON SHA-256, with the output fingerprint bound to **both** the original R25 packet and the R33 occurrence queue.
- Strict negative authority flags and all-pending states are enforced. Machine verification timestamps do **not** count as independently checked citations, source reading equivalence, medical safety clearance or editor/QD approval.
- The gate is invoked inside R25's existing mandatory private stage 13, immediately after R31's review index and R33's occurrence queue. A missing/symlinked gate fails closed. The R34 tool additionally supports private stdout-only `--format summary|json|ndjson`; it writes nothing.
- The 30 shared-URL groups count comes from the frozen **global source crosswalk**. Only shared URLs actually cited in the 367 use relationships appear in R34's coordination tracks. Those tracks must not be represented as a complete adjudication of all global groups.

## Test / approval matrix

**Local synthetic:** 95 tests passed with `python -I -m unittest discover -s preparedness/tests -p 'test_r34_*' -v`, including citation/source tampering, false authority, fingerprint substitution, Unicode, duplicate-URL separation, fallback drift, missing original notes, missing relationships/claims, invalid offsets and batch-size bounds. These tests use an artificial 4-citation, 2-relationship fixture, **not** the 35-article release corpus.

**Required hosted:** Native `python -I preparedness/tools/validate.py`, private `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, and all 13 mandatory preflight stages on the exact pull-request head. A successful workflow is machine/structural evidence only.

**Human release blockers:** editorial verification of claims/links and source scopes; 30 shared-URL review groups; 43 fallbacks; consequential emergency/medical guidance by qualified reviewers; rendered/browser QA; independent QD decision. **All remain outstanding.**

No original contributor body, metadata, source, taxonomy, crosswalk, safety state or reading-depth record is edited by R34. Safety QA PR #157 and synthetic-fixture PR #169 remain independent drafts; this branch is stacked on R33 rather than merging them. Homepage is outside scope.
