# R42 — Private per-article evidence review dossiers (RELEASE HOLD)

Issue #136 only. R42 is an isolated, unpublished draft layered on **R41 head `efe1583cf950fb85fa05585dc7e45c16a45b070f`**, not the production or homepage branch.

## Why this exists

R33–R41 protected individual review assignments, full source-reading notes, shared-source variants, CSV custody, receipt chains and historical review evidence. Human editorial and qualified safety reviewers still require an **article-by-article case file** with the exact original citation/source evidence, visible high-consequence priorities, and hard release restrictions.

`preparedness/tools/article_review_dossier_gate.py` transforms the *unaltered, fingerprint-pinned R37 private worksheets* into 36 deterministic HOLD dossiers (35 full draft articles plus one water-planning tool). It does not mutate articles or accept reviewer answers, and is read-only. Every original claim occurrence, contributor-specific source-reading relationship, cross-origin fallback and shared URL card is preserved independently. Multiple source records with the same URL are **not** merged. Shared URL groups with no article citations are kept in an explicit global unreviewed queue.

The result includes private per-article case IDs, exact original citation text/context, codepoint offsets, unabridged source records and original reading explanations as retained in R37, the article's recorded taxonomy safety-gate and status **as metadata only**, and original triage priority **as a work-order hint, never safety approval**.

## Mandatory machine preflight

The existing stage 13 `citation_fallback_review_gate.py` now verifies the 36-dossier parent fingerprint, exact 1,959 claims, 367 source-reading relationships, 43 fallback relationships and 30 global shared-URL source groups, and that no dossier or aggregate packet grants release, medical clearance or QD approval. The seven original contributor branches, article bodies, source inventories and private WordPress drafts are unchanged.

72 synthetic tests include detection of fabricated source safety, missing/duplicated claims, altered citation context or codepoint offset, cross-cluster source ID drift, omitted reading scope/fallbacks, URL conflation, source-record tampering, forged source reading approvals, changed taxonomy, extra/missing worksheet rows, non-matching trust anchors, and all genuine duplicate URL evidence preserved with distinct relationships.

## Threat model and release constraints

- R42 reuses R37/R38 integrity validators; **its trusted R37 manifest fingerprint must come from an independently checked frozen upstream baseline**, not from untrusted imported spreadsheets. The mandatory repository pipeline builds it directly from the original integrated source chain. An external reviewer service must pin the baseline separately.
- Even correctly hashed archival evidence can be outdated, inaccessible, factually wrong, or unsupported. R42 does **not** visit or independently check external URLs, inspect medical credentials, or authorize human safety judgments.
- The private article taxonomy contains historical status labels such as `safety-approved-draft`. R42 copies these labels **only as untrusted original metadata** while forcing `qualified_safety_clearance=false` and every release flag to false. No approval is inferred.
- No source reading depth, unique citation, warning, category, URL, original contributor attribution or source variant is shortened or deduplicated by URL.
- All citations and consequential guidance require independent source verification and qualified food/water/fire/medical review. Rendered-browser and independent exact-head QD review remain open.
- Dossiers contain unabridged research evidence and are PRIVATE. Do not publish them, expose them to public URLs, put them in navigation, or write them to WordPress/CMS. The full publication release remains **HOLD**.
- R39–R41 receipt custody is unaffected; there is no new reviewer identity, signed evidence, durable ledger, or approved human review in R42.

## Execution

On a trusted checkout of this draft branch:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I -m unittest discover -s preparedness/tests -p 'test_r42_article_review_dossiers.py' -v
python -I preparedness/tools/citation_fallback_review_gate.py
```

A green machine pipeline establishes only evidence structure and internal crosswalk completeness. It is **NOT editorial, clinical, safety, QD or publishing clearance**.
