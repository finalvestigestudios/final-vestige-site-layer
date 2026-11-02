# R78 — Preparedness Document-First Citation / Source Review (PRIVATE DRAFT; HOLD)

Issue #136. **Machine-only editorial/reviewer crosswalk. Never publish or merge without independent review.**

R78 is an additive layer on the exact immutable R77 draft head `377d5f7d1c2e9a64943268562750cf8d468bd917`. The separate 35-article/six-tool release candidate remains PR #584 `ddb3528ba6494dada1fa1c3a142ce746e3a67706` and is not edited. R78 cannot grant any human source-link check, claim-support finding, safety approval, independent QD PASS, CMS write, navigation change, public rendering result, or publication permission.

## Why this layer

Earlier R72–R77 work built source-first and citation-first inventories. The editorial handoff also needs a **document-first, original reading-order work packet**: one card per draft with every unabridged DOM text block, every local citation occurrence and all **origin-scoped** source variants, plus a referenced complete preserved R77 evidence tree. A passage with citations must not be described as proven safe or supported, and a missing same-block citation is a candidate for review rather than a confirmed defect.

The code independently reconstructs each document's 1-based citation ordinal sequence, exact raw source IDs, original block hashes, complete block order, origin-scoped URL/source-reading identity, original temporal review cues and explicit NOT_REVIEWED states. It detects possible draft URL collisions after percent-decoding, case folding and trailing slash normalization rather than assuming different raw strings imply different URLs. Such a collision **fails closed**; the script never rewrites a URL or redirects any page.

The sealed, deterministic result nests **the complete unabridged R77 parent evidence**, including historical readings and original-to-candidate provenance; no source is merged by same URL, same ID, similar date or equivalent-looking source. A one-way, formula-neutralized CSV provides document-level *review workload routing*, never an importer of editorial decisions. Passages without local citations remain visible alongside their full text and complete surrounding document; reviewer priority is not a clinical risk score.

## Expected exact-machine baseline (must be rerun on HEAD)

| Custody item | Frozen expected count |
| --- | ---: |
| Article drafts / tool drafts | 35 / 6 |
| Distinct unabridged source readings | 244 |
| Individual citation occurrences | 2,173 |
| Citation/source-variant edges (not distinct claims) | 2,359 |
| Complete DOM text blocks | 4,070 |
| Shared-URL source-identity groups | 32 |
| Repeated-ID source-identity groups | 15 |
| Lexically flagged action/quantity review blocks | 1,068 |
| Lexically flagged action/quantity blocks without same-block citation | 347 |
| Independently reviewed/cleared source, claim, safety, QD items | **0** |

The 347 uncited review candidates are **not** declared wrong, unsupported or unsafe. Unchecked links, ambiguous source scope, live source quality and emergency guidance cannot be cleared through machine citation adjacency.

## Additive file scope and reproduction

Only four files are permitted in this R78 stack:

1. `preparedness/tools/r78_document_citation_review_matrix.py`
2. `preparedness/tests/test_r78_document_citation_review_matrix.py`
3. `preparedness/docs/R78_DOCUMENT_CITATION_REVIEW_HOLD.md`
4. `.github/workflows/preparedness-r78-private-tests.yml`

On an exact R78 checkout, execute:

```sh
python -I -m unittest discover -s preparedness/tests -p test_r78_document_citation_review_matrix.py -v
python -I preparedness/tools/r78_document_citation_review_matrix.py
python -I preparedness/tools/r78_document_citation_review_matrix.py --private-review-csv-stdout > /tmp/r78-document-review.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The isolated test module contains **83 individual checks** (41 different complete-document reading-order cases and 42 other custody, URL-alias, approval-forgery, temporal, collision, CSV and citation conservation assertions). Their existence is **not proof they ran**. Record the exact CI/head outcome before asserting tests passed. All build outputs remain offline, WordPress-ready drafts only.

## Independently verified current GitHub refs, 2026-11-02

| Workstream | Exact head SHA |
| --- | --- |
| Claude Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Claude shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Claude food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Claude health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Claude historical food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Claude historical home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Claude historical field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Separate release candidate PR #584 | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| Independent Start Here safety QA PR #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` |
| Independent synthetic fixture PR #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` |
| Homepage lead PR #49 | `10495883299d53596992c26a8987f629b2904670` |
| Experience 2.0 flagship PR #604 | `368399842de1bd4fc02598571c0fa29eb5ad279c` |

PR #157 is a five-file safety wording/taxonomy/source/test correction, not merged or cleared. PR #169 is a one-file synthetic fixture correction, not merged; separate `test_register_fragments_cannot_duplicate_ids` still creates `_dup_test.json` in a shared source tree (potential parallel-run race). Do not modify those owners' branches without their coordination. Homepage and flagship workstreams were checked read-only and remain outside this task.

## Mandatory release integrity remains CLOSED

R77 diagnostic suite was green on its own exact head; **separate mandatory 13-stage release-integrity check failed** at `seven_cluster_git_parity`. Five historical contributor baselines diverged from their frozen provenance. No R78 result changes that. Outstanding independent gates include 206 original human-link obligations, **0/244** candidate source links human-checked, 30 original / 32 candidate duplicate URL scope decisions, 43 fallback source relationships, 15 safety exceptions, 22 RC editorial decisions, actual WordPress/browser/print/screen-reader QA, qualified review of consequential water/food/medical/fire/CO instructions, and exact-head independent QD.

**Release state: HOLD. No publication, no CMS, no homepage, no site navigation, no WordPress edits, no source modifications, no merge, and no claim that emergency instructions are medically safe.**
