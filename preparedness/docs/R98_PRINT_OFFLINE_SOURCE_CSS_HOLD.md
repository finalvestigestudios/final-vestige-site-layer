# R98 — Print/offline source and safety-review CSS custody | PRIVATE DRAFT HOLD

**Issue:** #136. **Base:** R97 final `e64b7f009a044332d5b66b02781e4eaafbfa5763`. **Scope:** four new additive engineering files only. No edits to the 35 article bodies, historical readings, original sources, metadata, taxonomy, WordPress, public pages, homepage, or navigation.

## Why this exists

R93–R97 verify that 1,959 rendered citations, 4,032 original editorial blocks, 20,217 original HTML DOM events, visible source/review shell, 36 canonical draft routes and JSON-LD records retain their intended structure. None establishes *actual CSS rendering*, especially printing and offline viewing.

The existing scoped `preparedness/assets/preparedness.css` has `@media print` rules. It prints outbound link URLs using `attr(href)`, but also deliberately hides ancillary interface elements, including the water planner's `.pa-tool` calculator. A preserved source citation is not useful to a printed reader if CSS conceals the source, its reading scope, or the safety caveat. The archive must not silently equate HTML conservation with print readability.

## R98 implementation

`r98_print_source_visibility_custody.py` performs **read-only conservative static inspection** of the original CSS and re-runs R97 → R96 → R95 → R94/R93 actual 36-draft rendering/integrity chain. It rejects malformed CSS braces/comments, escaped selectors that could bypass an ASCII comparison, unscoped rules, unknown at-rules, external stylesheet imports/URL fetches, unexpected hidden elements, source-footnote/report concealment, masks, clipping, transparent text, collapsed evidence, offscreen transforms, disabled pointer interactions, and missing/changed print external-source URL annotation.

A tiny explicit allowlist covers existing `[hidden]` card/filter states and the *known* six printed-only ancillary exclusions. **This allowlist is not a safety approval.** The print-hidden `.pa-tool` water planner is surfaced as a named review workorder, rather than concealed by a green static check. Any expansion of this exception list requires deliberate engineering and qualified review. Existing citation anchor text, source scope, warning states, and original research records are never rewritten or deduplicated.

All reports are SHA-256-sealed and explicitly contain `release_state: HOLD`, `may_publish: false`, `human_source_claim_review: NOT_REVIEWED`, `qualified_emergency_safety_review: NOT_REVIEWED`, `independent_QD: NOT_REVIEWED`, and `actual_browser_print_check: NOT_REVIEWED`.

## Test plan and validation (pending exact-head runner evidence until linked)

1. `python -I -m unittest discover -s preparedness/tests -p test_r98_print_source_visibility_custody.py -v`: hundreds of isolated synthetic suppression attacks plus real CSS read-only baseline; no shared-tree fixture.
2. `python -I preparedness/tools/r98_print_source_visibility_custody.py --private-json-stdout`: real corpus source/HTML/metadata chain and CSS analysis, deterministic integrity seal, no CMS.
3. `python -I preparedness/tools/validate.py`: original evidence/status validation. Known pre-existing source-URL collisions remain open.
4. `python -I preparedness/tools/build.py`: WordPress-ready *offline/private drafts only*; this does not create or publish pages.
5. `python -I -m unittest discover -s preparedness/tests -v`: full suite (well above 36 tests).
6. Independent **13-stage mandatory release integrity** remains a separate, non-overridden gate.

## Explicit risk / limitations

- Static stylesheet parsing is not a substitute for WordPress theme inheritance, actual CSSOM/computed style, print-preview checks, PDF accessibility, screen readers, or mobile/Safari/device testing.
- `.pa-tool` is currently omitted from print output. The qualified reviewer must decide whether that hides warnings, calculation limitations or outputs that require a printable alternative. No automatic replacement is made here.
- Source links and article claims are not independently verified. A correct rendered URL can still be stale, wrong, inaccessible, or out of scope.
- Historic five-cluster provenance differences, 30 URL collision groups, 15 safety exceptions, 22 editorial decisions, source claim reviews, qualified water/food/medical/emergency guidance review, the PR #169 fixture race, and independent QD remain unresolved.
- **No QD PASS, clinical/medical-safety claims, approval of old guidance, publication, or live CMS/nav operation.** All R98 diagnostics are release-HOLD evidence for Issue #136, not permission to launch.
