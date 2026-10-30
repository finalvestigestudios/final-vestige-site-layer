# Focus Fieldbook — scroll-to-signup anchor repair (review only)

## Independently verified CMS finding

On October 29, 2026, WordPress published page **1579** (`/focus/`) contained five lower-page CTAs linking to `#subscribe-blog`. Both the editable block content and the WordPress rendered-content view expose **no element with `id="subscribe-blog"`**. The native `wp:jetpack/subscriptions` block is present and the founder successfully tested signup and welcome-email delivery. A browser-side Jetpack enhancement might generate the missing anchor after initial rendering; that is **not independently verified**, so this is a *high-confidence CMS anchor gap / suspected visitor-scroll defect*, not a proven failed real-browser click.

The correct repair must be idempotent and must not change the subscription mechanism.

## Proposed implementation

`focus_signup_anchor_wp_block.html` is a single Gutenberg `core/html` block with a small inline script. When the public page loads:

1. It looks for the Focus landing-page root `.fv-focus`.
2. It leaves any existing `id="subscribe-blog"` untouched.
3. Otherwise, when the actual `.wp-block-jetpack-subscriptions` element exists, it inserts a zero-text, noninteractive `<span id="subscribe-blog">` immediately before the widget.
4. A user clicking any existing `href="#subscribe-blog"` CTA can then navigate to that exact block using ordinary browser fragment behavior. Deep links containing that fragment are scrolled to the newly added target on initialization.
5. If the page or widget is unavailable, it fails closed without creating a fake form.

**No event listener for form submission; no network requests, data collection, cookies, or storage.** It does not force-enable WordPress-logged-in email fields.

## Test evidence

Run locally:

```bash
node --test qa/site/test_focus_signup_anchor.cjs
```

**10 / 10 Node tests passed locally**, covering form-preserving insertion, existing-target and missing-widget cases, DOM-ready timing, direct-fragment navigation, idempotence and prohibition of form/network/persistence behavior.

Committed source/test Git blobs match the exact locally tested files:

- `focus_signup_anchor_wp_block.html`: `430074db5d2128dbba776b584c400a7c7099f98c`
- `test_focus_signup_anchor.cjs`: `ed31cd9f1346685ca7d937a853a525100ffeb438`

Unit tests are not browser acceptance tests.

## Safe installation — requires separate WordPress edit approval

- Refresh WordPress page 1579's sections and confirm the live content still has `href="#subscribe-blog"`, exactly one native Jetpack subscription block, and no existing `id="subscribe-blog"` or `fvf-signup-anchor-v1` script.
- Use the already supported `page-sections.insert` operation with `expected_modified` + `expected_content_hash` to append this *one* top-level `core/html` block after the existing group and autofill CSS block. **Do not rewrite the 30KB page, form, or newsletter configuration.**
- Verify it remains a published page with exactly one subscription widget, and that the new script appears once.
- In a logged-out desktop and mobile browser, click a lower-page CTA and check that the signup widget, not the end of the document, is scrolled into view. Check direct `/focus/#subscribe-blog`, keyboard activation, normal signup/welcome delivery, and signed-in Jetpack form behavior.
- If the native Jetpack visitor experience already supplies the target, this patch should no-op. If it is not needed, do not deploy it merely because it exists as a draft.
- Preserve the prior approved autofill contrast fix `fv-focus-autofill-fix-v1`.

No production changes are included in this PR. All changes are additive under `qa/site/`, separate from homepage redesign PR #49 and the Preparedness Archive issue #136.
