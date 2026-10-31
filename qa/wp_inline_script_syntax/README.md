# WordPress rendered inline JavaScript syntax guard (offline QA)

**Scope:** A read-only, offline test for JavaScript *syntax* in the `content.rendered` field from an authenticated WordPress REST page. This is not a crawler, deployment, sanitizer override, browser simulation, or permission to edit production.

## Why

On 2026-10-31, published `/focus/` (page 1579) returned a valid **saved** script from `context=edit`, but `context=view` returned the first inline classic script with `&&` encoded as `&#038;&#038;` in two occurrences. A V8 syntax-only compile of the rendered script raised `SyntaxError: Invalid or unexpected token`; the saved script passed. A second inline script (`fvf-signup-anchor-v1`) passed in both views. This is a **confirmed inconsistency in the authenticated rendered REST representation**, not a verified browser defect. Actual anonymous HTML, browser console, form state, and email delivery still need checking.

The affected first script controls the conditional visibility of the post-signup PDF gift; it does **not** prove the native Jetpack subscription block is broken. Do not claim a subscriber failure or remove the gift without real browser testing.

## Run

On a local workstation with Node.js 20 or 22 (no third-party dependencies):

```sh
node --test qa/wp_inline_script_syntax/check.test.mjs
node --check qa/wp_inline_script_syntax/check.mjs
node qa/wp_inline_script_syntax/check.mjs --rest /path/to/redacted-wp-rest-page.json
node qa/wp_inline_script_syntax/check.mjs --html /path/to/rendered-content.html
```

The REST JSON must contain `content.rendered` (or `data.content.rendered`). The check compiles, but does **not execute**, inline classic JavaScript. It excludes JSON-LD, import maps, modules, and external scripts, which require separate tests. It does not fetch URLs, submit signup forms, or expose the input HTML. Exit: 0 if no classic-script syntax errors, 1 if errors, 2 if invalid input.

## Production/editor handoff — do not apply from QA lane

Have Claude re-fetch latest page 1579 revision and independently inspect actual logged-out HTML/console before deciding on a minimal content change. If confirmed live, remove bare ampersand operators within that first inline script (e.g., replace `if (c && condition)` with equivalent nested `if (c) { if (condition) { ... } }` constructs) **without** changing the subscription form, the PDF URL, or the separately tracked `subscribe` query-value predicate. Re-check both REST and real browser, anonymous mobile signup, actual confirmation and welcome email, 52-page PDF bytes and SHA-256. All site writes remain subject to explicit approval and QD/Decision Queue.
