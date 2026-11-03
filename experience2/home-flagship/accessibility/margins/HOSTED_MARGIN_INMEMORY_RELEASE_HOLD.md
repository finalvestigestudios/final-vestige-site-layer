# Final Vestige Experience 2.0 — hosted in-memory Margins A/B admission

**DRAFT / RELEASE HOLD. No WordPress writes, merges, deployments, subscriptions or CSS publication.**

## Why this exists
The complete published homepage on WordPress page ID 6 (read-only on 2026-11-03, `publish`, modified `2026-11-02T17:48:13`) includes 72 Hidden in the Margins records and the seven-chapter flagship. PR #739 found a serious animated text color-contrast issue against the real hosted site at 390px and 1440px. PR #746 provides a minimal contrast-safe stylesheet, but its browser study used a *synthetic* 72-slot fixture and could not show whether the CSS is safe on the *actual complete hosted page*.

This companion intentionally **does not duplicate the candidate CSS**: it loads `margin_strip_contrast_safe.css` from PR #746, fetches the anonymous public site in Playwright, observes baseline axe for the site-shell strip, inserts the same CSS **only into the current browser document**, then reruns a fail-closed visual/contrast matrix. This is not a public edit, staging plugin or real staging deployment.

## Source/baseline custody
- Frozen homepage v1 PR #49: `10495883299d53596992c26a8987f629b2904670`. Untouched.
- Real public site: `https://finalvestige.com/`, WordPress page ID 6; original published modified field `2026-11-02T17:48:13`. Current anonymous rendering can change independently of this branch; record the timestamp with each interpretation.
- Parent PR #746: `a48286a0cd1a0fded4ace726d4ac4db4397e1c78`; existing in-memory candidate CSS is copied from that exact commit through Git ancestry, not reconstructed.
- Existing source-grounded hosted accessibility study: PR #739 at `d826255828e993e7711fe2014831872999b8543d`.
- Existing hosted structural/image bytes audit: PR #731 at `2dbf41cd7366eecb31af3b9fdee6f7433bdd71a0`.
- Issue #150 remains the flagship charter; the published image-specific NYPL Malbone reproduction conflict is **not resolved** by this work.

## New browser acceptance
- Anonymous GET-only Chromium, five viewport widths 320/390/768/1440/1920. Every non-GET is denied. WordPress page source or subscriber data are never saved. NYPL candidate image paths are blocked from transfer.
- Exact count of **72 original published** Margin fragments and one seven-chapter flagship container; source drift fails closed.
- Actual live computed styles for 8 representative phases including 355/360-second wraparound, 40 phase/viewport combinations. Exactly one visible sharp, fully opaque fragment with at least 4.5:1 computed color contrast and no horizontal overflow required.
- Pinned axe-core color-contrast rule against **actual hosted site shell** before and after browser-local insertion at 390px and 1440px. Missing axe or candidate violation fails closed. The baseline automated result is observational, because CSS animation sampling can be timing-dependent. Axe unresolved/incomplete rules must be reviewed manually.
- Reduced-motion first-fragment fallback with JavaScript enabled AND disabled at 390px.
- Adversarial in-script source tests: non-GET & excluded image URLs, malicious CSS injection, absence/incompleteness of observations, wrong record count, non-finite colors, low-opacity contrast, axe violation and release HOLD.
- A JSON artifact includes *counts, color ratios, rule IDs, outcome and limits only*: no archival image bytes, raw historical text, HTML, screenshots, selector dumps, cookies or visitor data.

## Local commands
```sh
python experience2/home-flagship/accessibility/margins/probe_hosted_margin_override.py --self-test
python -m pip install 'playwright==1.56.0'
python -m playwright install chromium
npm install --prefix /tmp/fv-ex2-axe --no-save --ignore-scripts 'axe-core@4.10.3'
python experience2/home-flagship/accessibility/margins/probe_hosted_margin_override.py \
  --axe-source /tmp/fv-ex2-axe/node_modules/axe-core/axe.min.js \
  --output HOSTED_MARGINS_CANDIDATE_HOLD.json
```

## Release gate and limitations
This is **read-only public-host CSS simulation**, not production CSS or WordPress.com staging. An in-memory patched DOM can establish whether selectors match and render safely, but it **cannot certify** authenticated WordPress edit persistence, theme CSS ordering, CSP deployment, Jetpack subscriber submissions, host-specific cache, physical touch/Safari, NVDA/VoiceOver or field Core Web Vitals. It cannot establish image rights or authorization for the already published site revision. CSS is never injected into any other visitor's session. Independent QD and human WCAG 2.2 AA review are required. No merged deployment or production write is permitted without a new exact-head approved release decision.

**Before publishing any patch:** reconcile the source-rights/authorization issue, do human accessibility checks at 200% zoom and on mobile physical devices, retest the complete actual hosted page and obtain the founder's specific approval. Keep Focus Fieldbook, native Jetpack signup, all 72 Margins records and the existing seven chapters untouched.

This PR is for testing an already-existing site-shell fix, not new chapters, new affiliate marketing or artwork.
