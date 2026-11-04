# EX2 no-JS Margins per-record visibility admission — isolated QA, release HOLD
Date: 2026-11-04 PT. Parent: PR #912 at exact base `592670f911c05660e43c90d42a4b89eb0d7a49f1`.

## Proven false-positive hole
Previous anonymous no-JavaScript test counted 72 records and inspected **only the first** record's computed opacity/position. Any later record could be CSS-hidden, zero-height, absolute, or inside an aria-hidden/inert/transparent ancestor while passing the current contract. This is consequential because the existing homepage must preserve 72 **readable** historical fragments, not merely their text in the DOM.

## Implemented isolated verification
- Compute each record's own box, display, visibility, opacity and position, and traverse ancestors for CSS-hidden, opacity, `hidden`, `inert` or `aria-hidden=true`; require all 72 to remain normally positioned and readable.
- Fail closed on each record index; never output 72 public text strings or detailed DOM diagnostics in the summarized run result.
- Two additional Node tests: mutation of each record in 72 positions and six adverse visibility states.
- Existing exact-text parity, 7 widths, anonymous first-screen Focus, axe and local temporary-page cleanup remain unchanged. No marketing claims, tracking, live WordPress writes, plugin changes or affiliate activations.

## Locally executed evidence (2026-11-04)
- `node --check` for both updated helper and tests: PASS.
- `node --test test_guest_render_source_contract.mjs`: **8/8 PASS**; 72 per-record mutations and 6 explicit malformed record checks rejected.
- Actual headless Chromium with `javaScriptEnabled=false` on an **isolated synthetic 72-fragment HTML fixture**, 390×844: intact baseline PASS; display:none, opacity:0, hidden ancestor, position:absolute, zero-size, aria-hidden ancestor: **6/6 rejected**.
- This controlled browser case verifies the DOM probe works in a real no-JS Chromium browser. It is **NOT** WordPress/Assembler staging evidence and contains no historical claims, real subscribers, or production data.

## Remaining release blockers
Exact-head isolated WordPress/Assembler full-document guest browser test still must execute; prior runner jobs at SHA `592670f911c05660e43c90d42a4b89eb0d7a49f1` failed before first step. Known serious desktop Assembler navigation axe finding is **not cleared**. No physical 200% zoom, independent QD, rights approval, measured Lighthouse/CWV, WordPress.com host parity, paid conversion or founder release approval. WordPress.com Personal lacks native staging; no plan upgrade proposed.

OFFER → free 52-page Focus Fieldbook; FUNNEL → anonymous reader → historically accurate Margins/observer CTA → landing page; BLOCKER → no-JS records beyond first could be invisible while gate passed; CHANGE → 72 independent visual/ARIA state checks; PASS → local Node and isolated Chromium, FAIL/UNKNOWN → real WP full-page axe; OWNER → homepage QA (this change), Claude attribution/commerce, founder release.
