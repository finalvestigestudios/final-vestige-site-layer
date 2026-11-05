# P0 — verify the actual anonymous visitor's Fieldbook opt-in, not merely its link

2026-11-05 · **DRAFT / HOLD** · Companion to homepage conversion PRs #1082, #1089 and #1094. Base #1094 `9f4c0b118ef6793b9fd416c87a7ccdc91a634737`. Issue #150 and conversion charter #820.

## Why this is now a material release gate

Read-only WordPress Page **1579** on 2026-11-05:
- The edit-context Gutenberg source contains the correct `<!-- wp:jetpack/subscriptions {...} /-->` block, configured with the action **"Send me the fieldbook"**, and preserves the 52-page free offer, privacy/consent wording and PDF location.
- The **view-context rendered REST representation**, however, contains a button-like `<a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a>` inside `.wp-block-jetpack-subscriptions`, **not a rendered email input or HTML form**.
- These two WordPress API representations are **not evidence of a broken anonymous frontend**, because block output can depend on server request context, visitor identity or client-side hydration. They **are evidence that checking the Gutenberg block's mere existence or an apparently actionable "Send" link is insufficient**.
- WordPress screenshot-link generation returned `ready` for 390px and 1440px public `/focus/`, but the returned link alone does **not** establish whether a guest email field or successful signup was actually rendered.

Homepage Page 6's live source, including the 72 Margins entries and in-page Focus links, was inspected read-only. No changes to either WordPress page.

## Source-controlled gate

Run in a disposable, network-capable, unauthenticated browser environment with Chromium and Playwright installed:

```bash
python -m unittest -v experience2/home-flagship/qa/release-candidate/test_focus_guest_gate.py
python experience2/home-flagship/qa/release-candidate/focus_guest_gate.py --live-guest --output /tmp/fv-focus-guest
```

The second command makes **GET-only browser navigation to the exact public `https://finalvestige.com/focus/`**. It does not fill or submit email, create a subscriber, run analytics or change CMS. It checks the rendered guest DOM at 320/390/768/1440 with reduced motion. Admission requires a labeled, visible email input inside the actual Jetpack form, a visible submit action, both >=44px, a clean initial field, no horizontal overflow, and no self-link *instead* of an email form. Screenshots at 390 and 1440 plus machine-readable boolean receipts (no email values) are produced locally. Missing/unreachable network is **FAIL/HOLD**, never PASS.

To check `/focus/` in a network-isolated environment, use **synthetic fixture tests**, not a claimed live pass. Actual Chromium fixture testing: four positive widths passed and eight deliberate negative examples correctly rejected, including the same self-link-only pattern seen in the REST view. During development two false positives were uncovered for CSS-overridden `hidden` controls and corrected with explicit hidden/inert checks.

## What this DOES NOT prove

It does not submit a Jetpack form or prove email delivery, double opt-in, PDF fulfillment, subscriber counts, sales, attribution, legitimate visitors, Accessibility Conformance or field CWV. Rendered REST output is **not equivalent** to anonymous public HTML. Full JavaScript/no-JavaScript, actual WCAG 2.2 AA, native 200% zoom, WordPress/Assembler integration and live guest request still need independent acceptance before release. The local execution environment blocked all browser navigation with `net::ERR_BLOCKED_BY_ADMINISTRATOR`, so the live guest command **failed closed at all four widths**; the fixture tests are the only Chromium PASS.

## Offer → funnel step → blocker → experiment → evidence → owner

**Offer:** existing free 52-page Seven Day Focus Fieldbook. **Step:** high-intent homepage CTA → actual anonymous Focus opt-in. **Potential blocker:** API rendered subscribe button is a self-link with no email field, which could fool source-only tests. **Change:** fail-closed real guest-form browser acceptance, no production change. **Current evidence:** 4 responsive positive + 8 hostile offline Chromium cases pass; WordPress REST `view` difference source-confirmed; **actual anonymous frontend NOT VERIFIED**. **Owner:** homepage QA for read-only browser gate; Claude for Jetpack/attribution remediation *only if the guest browser reproduces it*. Grok/Praxxis acquisition unchanged.

**Commercial outcome:** confirmed subscribers, paid orders and net revenue **not verified**. Primary KPI remains verified net revenue per 1,000 qualified human sessions. This gate tests a necessary leading funnel step, not commercial success.

No new assets, historical claims, product promises, merchant URLs, scripts, instrumentation, subscriptions or spending. Original Franklin archival folio, Focus Fieldbook, 72 Margins and frozen PR #49 unchanged. **No merge/deployment/WordPress writes approved.**
