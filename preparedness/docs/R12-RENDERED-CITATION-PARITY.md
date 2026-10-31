# Preparedness Archive — R12 rendered citation parity (DRAFT / RELEASE HOLD)

Tracks Issue #136. This work is **additive**, on top of the R11 draft export custody branch. It is not a review of the accuracy of the cited evidence, a medical or food/water safety assessment, or permission to publish.

## Distinct failure mode closed

R8's source crosswalk and claim-occurrence queue bind 1,959 source token occurrences and 367 article–source relationships to the original **unpublished** article bodies. R11 checks whether exported WordPress HTML and preview bytes exactly match the existing renderer. However, if the *renderer itself* mislabels a reference, reorders source IDs, omits a citation, strips reading-scope warnings, or creates a broken accessibility link, a byte-identical export can still be wrong. R12 independently compares source tokens to their actual rendered anchors and bibliography.

`tools/rendered_citation_gate.py` checks each DRAFT article and the planning tool using the R8 parser, independent of the renderer's own token resolver. It enforces exact visible citation-occurrence counts, first-use source numbering, unique bibliography IDs, `href` targets, accessible labels, HTML-escaped original source titles/URLs, the `rel=noopener` marker, article-specific source-use notes, contributor reading-scope caveats, visible unresolved shared-URL warnings and explicit pending human source-link verification. All 36 draft entries, 1,959 citation occurrences and 367 distinct article-source uses are frozen as revision-specific baseline quantities. The manifest is deterministic, HOLD-only and contains no publish capability. The source URLs themselves are not contacted; no claim support is independently verified.

## Trusted-checkout execution order

From repo root, on the exact R12 head with the complete private repository and working Python 3:

```bash
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/claim_corpus_release_gate.py
python -I preparedness/tools/draft_export_custody.py
python -I preparedness/tools/rendered_citation_gate.py --receipt preparedness/build/r12-rendered-citations-HOLD.json
```

The R12 CLI runs the source evidence freeze, native validator, R10 canonical corpus check and R11 draft-export custody readback again before the new audit. It writes only when `--receipt` explicitly requests a private file directly within `preparedness/build`; it never calls a CMS, publishes a page, or changes navigation. Treat all rendered HTML as draft-only and continue the independent review process.

## Locally executed verification and remaining blockers

`python -I -m unittest discover -s . -p 'test_rendered_citation_gate.py' -v` executed **70/70 passing tests** in a synthetic fixture, including 47 distinct targeted HTML mutation attacks, as well as positive and crosswalk/receipt baseline cases. This **does not** constitute a real 36-item build run: the runtime cannot clone the private repository (`github.com` DNS resolution fails). The full native validator/build/whole-repo test suite, actual R12 processing of 1,959 citations, hosted CI, independent QD, expert hazard advice review and all human source-link checks remain **NOT EXECUTED / NOT APPROVED**.

The existing 30 groups of multiply-used source URLs remain explicitly unresolved. The metadata's historical human/editorial safety labels must not be mistaken for per-claim or clinical approval. There is no source merging, no modification to all 35 article texts, no WordPress draft creation through the CMS, no published pages, no homepage changes, and no false QD PASS.
