# R10 — Canonical corpus and citation safety release gate (DRAFT / HOLD)

**Issue #136; no public publishing, WordPress changes, navigation, subscriber changes, QD PASS or claims of qualified medical/food/water/fire/CO safety clearance.**

## Why this gate exists

R8 binds a subset of each of the 1,959 claim occurrences to a SHA-256 identity. The displayed `inherited_safety_state`, `heading`, `context_excerpt`, and aggregate `inherited_safety_states` are not individually in that request digest. R9's self-report intake deliberately does not grant safety or factual verification authority, but a later reviewer must never mistake a stale/altered report for a canonical source snapshot. R10 regenerates the **complete** report from frozen article bodies, current article metadata and contributor-specific source rows. An optional supplied report must match **every field** of the regenerated report or R10 fails closed, including those fields outside R8's digest.

## Exact-checkout guard sequence

1. Run existing `evidence_freeze.verify(lib)` and `validate.validate(lib)`; reject any reported errors.
2. Require 35 complete draft articles and one draft water planner; require slate/section/track/ordinal parity, unique stable Preparedness routes, no unexpected/missing articles, >=1,800 words per article and >=450 words for planner. Modern guidance cannot acquire a `not-required` safety label.
3. Preserve 224 physical contributor source rows; require 186 distinct literal HTTPS URLs and 30 **unresolved** repeated-URL cohorts. Of 224 rows, **209 have dated, contributor-declared supporting scope and 15 are intentionally unread original base-register placeholders** with no source-support claim. Preserve these 15 explicit undated placeholders rather than misclassifying them as evidence or automatically dropping them. Forbid verified/human-checked markers on unread placeholders, forbid new fragment-level blank claims, and keep exactly 15 until reviewed and deliberately revised. Retain every original reading scope; identical URLs are not interchangeable evidence. Reject malformed, credential-bearing or nonstandard-port URLs.
4. Recompute R8's full expected 1,959-occurrence ledger using the live-in-checkout source rows and exact R8 baseline. Compare any supplied historical R8 report field-for-field; cross-check each claim's inherited safety state and aggregate state counts against current metadata.
5. Pass only regenerated evidence into R9 intake. Reader/reviewer submissions remain self-reports. Reject any non-HOLD or purported human-verification/safety-approval result.
6. Emit only an offline, machine-only HOLD receipt; optional JSON I/O is restricted to direct non-symlink files inside `preparedness/build`. Never transmit private reviewer identities or auto-publish.

## Reproducible commands on a private, authorized **exact checkout**

```bash
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
mkdir -p preparedness/build
python -I preparedness/tools/claim_occurrence_audit.py --json-out preparedness/build/private-r8.json
python -I preparedness/tools/claim_corpus_release_gate.py --report preparedness/build/private-r8.json --json-out preparedness/build/private-r10-HOLD.json
```

The separate `build.py` command generates offline WordPress-*draft*-ready markup, not CMS writes. The R10 gate itself does not build or publish pages.

## Verification scope (October 30, 2026)

**125/125 new synthetic/adversarial Python tests executed locally and passed.** This is an isolated fixture test with synthetic 35+1 documents, shared-source rows and fake R8/R9 entry points. The full private repository Python validation/build/test suite and real 1,959-occurrence execution remain **NOT EXECUTED** due local private-checkout DNS access limitations. Hosted CI and independent QD approval also remain outstanding.

The seven Claude contributor tips were inspected and unchanged: Start `2122d856`, Shelter `5daeaf2d`, Food `4b009361`, Health `d2212d0c`, Historical Food `2acf65ca`, Historical Home `f654e600`, Historical Field `a5ce8a62`. Reviewed independent QA PR #157 (`7d1ae6b8`) and synthetic fixture PR #169 (`e9cd7766`); neither modified. R9 parent PR #232 is `f3a8cf95f4cf92feb573f32cc8e41fc01725b69f`. Homepage PR #49 is `1049588329`, and Experience 2.0 homepage PR #238 is `918155c2`; no homepage work touched.

**Remaining HOLDs:** 30 repeated-URL groups need genuine source-reading reconciliation; no independently documented external source-link checks; qualified safety review of water, food, medication, infant care, generators and carbon monoxide; exact-checkout native validation and build; hosted green CI; independent QD signoff. No historical record claims modern safety merely by being historically documented.