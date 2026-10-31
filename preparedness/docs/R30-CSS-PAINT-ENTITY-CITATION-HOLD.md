# Preparedness Archive R30 — HTML entity and CSS paint custody (DRAFT / RELEASE HOLD)

Issue #136 · stacked on exact R29 `dd9fbf8453091a6e4d7f7980d1b50663dd44eb06`.

## Security-relevant gap closed

The mandatory R25 citation-to-source gate previously checked visible raw `{{cite:id}}` tokens and common inline concealment. It could still count citations obscured by CSS paint/clipping/geometry, or miss source-like text formed by HTML character-reference decoding. R30 rejects common inline clipping/masking/filtering, transparent alpha colors, zero dimensions/line-height/zoom, negative-position offsets, dynamically computed CSS expressions on relevant visibility properties, and entity-encoded citation tokens that a browser can display but the raw renderer may not resolve. These are conservative HOLD states, not claims that every rejected style is always invisible.

Original citation ID multiplicity and Unicode codepoint positions are unchanged. Same-origin contributor source records, original reading-depth statements, base fallbacks, 30 shared URL groups, unresolved safety states and article bytes are not touched. This change modifies the existing already-mandatory citation scanner, not the preflight step count.

## Test scope and precise limitations

- New local synthetic R30 cases: **121 passed**, including reject/allow, escaped CSS, entities and source-offset invariants.
- All locally reconstructed R25–R30 tests: **456 passed**. Python compilation passed. Results apply only to available reconstructed files, not to a full private checkout.
- A static HTMLParser is not a browser. External stylesheets, classes, media queries, Shadow DOM, JavaScript state, responsive clipping and computed visibility remain **UNVERIFIED**. Additional QA in a rendered browser is mandatory.
- `validate.py`, `build.py` and `private_release_preflight.py` require a complete trusted repository checkout. Git DNS failures and unassigned-hosted-CI jobs remain blockers. No WordPress build, source factual validation or clinical clearance is claimed.

## Strict release rule

`release_state=HOLD`, `may_publish=false`, `human_source_review=pending`, `qualified_emergency_safety_review=pending`, `independent_QD_approval=pending`.

The full 35-article slate, one water-planner draft, 1,959 citation occurrences, 367 relationships, 43 base fallbacks and 30 shared-source URL review groups remain draft evidence requiring appropriate human verification. Unresolved contributor-provenance discrepancy remains **NEEDS_HUMAN_DIFF_REVIEW**. No claims of medically safe advice, no CMS writes, no navigation/public changes, no publishing, no merges.
