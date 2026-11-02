# Exact-source offline CSP browser gate — DRAFT

**Purpose:** Close the gap between testing a representative seven-chapter fixture and testing the actual Experience 2.0 GitHub checkout with its real six CSS and four JavaScript files. This script is read-only and does not install any WordPress plugin or change the live homepage.

## Reproduce

From repository root with Python Playwright and Chromium available:

```bash
python -I experience2/home-flagship/qa/release-candidate/verify_csp_exact_browser.py \
  --root experience2/home-flagship \
  --expected-head "$(git rev-parse HEAD)" \
  --output /tmp/fv-ex2-canonical-browser
```

The executable `CHROMIUM_PATH` defaults to `/usr/bin/chromium`. This refuses a mismatched SHA, modified tracked source assets, missing/duplicate CSS or JS tags, and markup with source delimiter injection. It assembles **exact source bytes** for Chromium `set_content()` using a nonce-authenticated **meta CSP** patterned after the existing private-preview PHP renderer. Scripts run at the document tail, preserving the existing `defer` execution order. It deliberately aborts external network/image requests.

Seven responsive widths (320–1920px) verify the actual 7 chapter targets, 6+4 inlined assets, no horizontal overflow, no CSP/page errors and 4 live interactions: art direction, Franklin evidence selection, dated chronicle lens, Observer frame B. No-JS must keep all three evidence cases and both observer records readable, while hiding nonfunctional controls. Two adversarial cases ensure an unnonced injected inline script is blocked and that a wrong nonce blocks flagship enhancements while keeping historical evidence visible.

## What was actually run before this PR

The longer independent local test `/mnt/data/fv-home-offline-csp/verify_exact_csp_browser.py` already passed the same seven viewport/interaction scenarios plus three negative controls against a **representative** sealed homepage fixture, with Chromium 144, via meta CSP. A user-facing ZIP of its test code and JSON report was created. **The script committed here was not separately executed on the canonical checkout prior to upload; that is the point of the exact-head gate.** It must be executed and reviewed on the exact GitHub branch head before any release decision.

## Always HOLD release

`set_content()` with CSP meta is not WordPress network-header enforcement, iframe authentication, cookie/nonce round-trip, actual source image loading, usage rights, Safari, axe/WCAG 2.2 AA, real Lighthouse or p75 Core Web Vitals, hosted CI or independent QD approval. No CMS writes, merges or production deployments are approved. Complements existing PR #250 and PR #238 without modifying their test files or PR #49.
