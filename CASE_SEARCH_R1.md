# FVF-10 — Case Search R1

## Repair target

Independent QD found that v1 used diacritic-normalized text for match eligibility but constructed snippets and `<mark>` highlights by applying raw query tokens to the original published string. A valid normalized match such as a decomposed query against composed published text could therefore produce a snippet centered on unrelated text with no visible marked hit.

R1 makes matching, snippet anchoring, and highlighting one normalization-consistent operation.

## Normalization-consistent snippet contract

Case Search still searches only text already published in the current investigation. R1 creates a normalized representation for each indexed record together with an offset map back to the cleaned original published string.

For every query term:

1. the term is normalized with the same NFD + combining-mark removal + lowercase semantics used by the index;
2. term occurrences are found in normalized text;
3. normalized hit offsets are mapped back to exact original-string offsets;
4. the smallest useful multi-term span is selected;
5. the snippet is centered around that real mapped span; and
6. `<mark>` elements wrap the original published characters at those mapped offsets.

The offset map deliberately absorbs a following decomposed combining mark into the preceding base-character range. A query for composed `Café` can therefore visibly mark the original decomposed `Café`, and a decomposed query can visibly mark composed published text.

Multi-term matching remains AND matching. Duplicate normalized tokens are collapsed for deterministic range selection.

## Nondestructive jump state

`Jump to result` now follows the current Site Sprint DOM-state rule:

- scrolling is attempted before existing-node mutation;
- `tabindex="-1"` is added only when the publisher target had no tabindex;
- the feature removes only its own temporary tabindex;
- a pre-owned `fv-case-search-target` class is never removed;
- an originally absent `class` attribute returns to absent after feature-owned highlighting;
- existing/nondefault tabindex and publisher classes survive;
- focus establishment is verified through `document.activeElement`;
- repeated jumps are browser-regressed for state drift.

## Preserved visitor and privacy contract

- All / Story / Sources / Figures scopes
- typed Story / Section / Source / Figure results
- maximum 60 rendered results with total count announced
- browser Ctrl/Cmd+F remains untouched
- native dialog, keyboard result navigation, 44px controls
- 360px, reduced-motion, forced-colors, and print behavior
- no local/session storage, IndexedDB, cookies, analytics, external scripts, fetch/XHR/WebSocket/sendBeacon, or third-party service
- no inferred citations, evidence scoring, or mutation of published narrative/source/figure content

## Deterministic R1 identity

- Payload: `payloads/case-search-wp-block-r1.txt`
- Payload bytes: **19,227**
- Payload SHA-256: **`1e6a14c6cf245154c88b9656a6e58ab1cd852abf9e156ab578fdc01b6ee7efca`**
- Verifier: `tests/verify_case_search_r1.py`
- Workflow: `.github/workflows/case-search-r1-ci.yml`

The browser verifier executes the exact payload and proves:

- decomposed query → composed published text is centered and visibly marked;
- composed query → decomposed published text is centered and visibly marked;
- normalized multi-term AND matches visibly mark every required term;
- absent tabindex/class state is restored after a jump;
- publisher-owned `tabindex="0"` and a pre-owned feature-token class survive;
- repeated jumps do not drift publisher state.

## Delivery boundary

This is a bounded source/build repair successor created from then-current `production`. Green CI is evidence, not independent QD approval and not merge/deployment authority.

If independent QD passes this source/build identity and a governed executable integration is required, the executable successor must be rebuilt from then-current `production`, receive a new frozen executable SHA/package, fresh feature + repository CI, and fresh independent QD before the existing approval/dispatch lane can act. Live destination readback remains mandatory before `IMPLEMENTED + VERIFIED`.

No WordPress mutation, whole-site launch/indexing change, spending/billing, private-user processing, account/permission change, public Scout release, or external commitment is authorized by this artifact.
