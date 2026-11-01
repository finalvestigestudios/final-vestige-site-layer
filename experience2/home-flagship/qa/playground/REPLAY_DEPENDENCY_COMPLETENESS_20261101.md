# Complete-home HTTP replay dependency audit — 2026-11-01

Status: DRAFT / RELEASE HOLD. Parent PR #482 SHA 0d19ae726f6ff1e5a867dd175104e6863fdb1c07. Only isolated QA source changes. No homepage, archival folio, WordPress page 6, theme, plugins, subscription, or frozen PR #49 changes.

## Original two false PASS cases (reproduced against exact parent)
1. Captured CSS contained a background-image url("/assets/UNVERIFIED.svg"). Its bytes were never captured; Chromium aborted the request, but the previous seven-width receipt reported PASS.
2. An external iframe loaded https://unapproved.example/external. Chromium aborted it; the previous receipt nevertheless reported PASS.

These synthetic reproductions reveal test-coverage weaknesses; they do not allege that production WordPress contains either resource.

## Code changes
- Audit linked CSS, inline style tags and inline style attributes for uncaptured url() dependencies and @import. Allow data: and local #fragment references only. Fail closed rather than silently omit fonts/imagery.
- Reject uncaptured embeds, picture/media elements, and speculative preload links.
- Preserve linked stylesheet media conditions when inlining into the offline replay; print styles no longer apply globally by accident.
- Log any network requests aborted by Chromium across seven widths, the no-JS page, and the 720px zoom *proxy*. A request now fails the acceptance predicate, with its URL and resource type in the receipt.
- Add 12 positive and adversarial tests, including immediate and delayed dynamic-script fetch() calls verified with Chromium 144. A bounded 450ms observation period plus post-screenshot checks prevents the reproduced 260ms delayed-fetch false PASS; it is not a guarantee against arbitrarily later network activity.

## Executed local verification
Combined 65 inherited sealed-staging tests + 7 inherited HTTP-replay tests + 12 new tests = **84/84 PASS**, November 1, 2026. Test inputs used a genuine localhost HTTP server, actual Chromium 144.0.7559.96, and synthetic 1-pixel GIFs. Widths exercised: 320/360/390/768/1024/1440/1920 CSS pixels. The two former false positives were separately reproduced before the patch. Source files were verified against their Git blobs, not only a textual test transcript.

Command from the home-flagship QA directory: python -m unittest discover -s . -p 'test_*.py' -q

**Important:** No actual WordPress/Assembler installation was executed. No original Apollo, Franklin or NYPL image bytes or reproduction rights were authenticated. This cannot certify WCAG/axe, real Lighthouse/Core Web Vitals, 200% *browser zoom*, Safari, production CSP/cookies, Jetpack delivery, or WordPress.com hosting behavior.

## Remaining staging acceptance
WordPress.com Personal has no separate native staging clone. Continue free isolated Playground/local WordPress staging with the approved Assembler theme. Metadata currently identifies Apollo #473 (78,346 bytes), Franklin #474 (466,043 bytes), NYPL #1258 (5,553,669 bytes), but image-transfer bytes and item-specific rights still need independent checks. Do not commit uncontrolled asset binaries or private site data.

If actual WordPress emits uncaptured font, CSS, image or embedded resources, fail with a specific missing-dependency report; extend authorized, fingerprinted capture rather than weakening the acceptance gate. Complete native WordPress browser, keyboard/touch/no-JS, mobile, axe WCAG 2.2 AA, Lighthouse, source rights, QD/CI and founder visual/release gates remain open.

## Lane coordination
The seven-chapter experience remains the flagship; no extra chapter or affiliate merchant pitch. Frozen PR #49 is unchanged. Apollo PR #158 and Mind/Perception Issue #171 are separate. Do not conflate exact SHAs of CSP PR #252, Franklin hero PR #254, and the staged private WordPress chain. No merge, production installation, deployment or publication occurred.
