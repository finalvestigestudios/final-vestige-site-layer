# Focus Fieldbook — independent hosted in-memory A/B gate (HOLD)

**Purpose:** Close the evidence gap between the local fixture-only correction in [Issue #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) and an actual browser using finalvestige.com's published HTML. This is an **additive read-only QA lane**, independent of Claude's WordPress page-editor work and the earlier [PR #779](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/779). Do not merge as a production fix.

## Scope and safety

- Fetch only the published anonymous HTTPS Focus landing page and GET-only page assets. Do not submit the form, send emails, request subscriber-state URLs, call WP APIs/admin, authenticate, change cookies, write WordPress, or interfere with subscribers.
- Run the existing PR #779 browser preflight as the baseline, asserting the *specific* known SyntaxError in both 390px and 1440px JavaScript-enabled configurations and the previously passed 390px no-JavaScript form anchor.
- In a **new disposable browser context**, intercept the top-level Focus response **in memory only**. Require an exact one-script/two-encoded-operator match and replace those two operations using equivalent nested conditionals. Leave the original CSP and other page content intact. No remote page is edited.
- Re-run both widths; require a clean conditional-gift JS compile and no actual browser syntax errors, one native Jetpack block, resolvable signup anchor, no horizontal overflow, gift initially hidden, and gift revealed after a **simulated DOM class mutation**, which is **not** a real signup.
- Preserve a bounded machine-readable receipt, screenshot evidence, and short-lived CI artifact. A script revision, unexpected plugin change, fetch failure, CSP block, incomplete matrix, or any failed assertion yields **HOLD**. The actual published homepage, navigation, and branded experience remain untouched.

## Run locally

From the repository root, with Python 3.12 and Playwright 1.56.0 plus installed Chromium:

    cd qa/focus_hosted_ab_20261103
    python -m unittest -v test_candidate.py
    cd ../..
    python qa/focus_hosted_ab_20261103/candidate.py --out /tmp/focus-hosted-ab

The regression suite uses only synthetic strings and performs **zero network requests**. The actual browser step performs anonymous GETs and is intentionally fail-closed if the original defect no longer reproduces; that case is a **source re-review**, not evidence that the previous bug returned.

## Not verified by this gate

No real consent/confirmation, delivered welcome email, authenticated recipient journey, PDF bytes, PDF 52-page check, checksum, WordPress editor save/readback, manual accessibility/screen readers, production CSP compatibility after publication, redirects or production deployment. Do not change the Focus query-state business rule tracked in [PR #198](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/198) under cover of this JavaScript-syntax correction. Image rights, homepage accessibility and release governance are separate holds.

**Release status: QA only / DRAFT PR / no merge or deployment.**
