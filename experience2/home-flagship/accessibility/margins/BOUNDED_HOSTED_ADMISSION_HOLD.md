# Hosted Margins correction — bounded CI recovery (RELEASE HOLD)

Date: 2026-11-03. Parent: PR #752 exact `4bdff84e7715fa2cf98e5cc2d30edff201c10838`, stacked on PR #746. Frozen PR #49 must not be changed.

## Observed blocker (not a passing hosted audit)
The original hosted ephemeral-CSS admission, Actions run [41601064751](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41601064751), completed its *source* job successfully but its `live-ephemeral` job was **CANCELLED**. The Chromium probe step began at 2026-11-03 08:09:05Z, was cancelled at 08:33:50Z (~24m45s), produced no JSON artifact and did not identify a viewport/phase. We must not interpret that cancellation as a passing axe or contrast result. The cause of the stall is **not established**; navigation, routing, animation or axe may all be responsible.

## Engineering recovery
The same existing full-hosted anonymous browser/axe test is preserved, with **7 independently bounded subprocess cases**: five viewport widths (320, 390, 768, 1440, 1920), and reduced-motion JavaScript on/off. Each case has a 90-second deadline in a dedicated browser process. The runner prints case start/end progress, records a redacted case failure on timeout or exception, and **writes a complete valid JSON checkpoint after every case** so GitHub Actions can upload evidence even when a later case fails. A missing/duplicated width, absent reduced-motion observation, failed contrast rule, incomplete axe instrumentation or any child timeout is a hard FAIL—not a green release gate. Expanded source tests reject partial and duplicated results.

The workflow's browser-job budget is reduced from 25 to 17 minutes, explicitly passes a 90-second per-case limit, and requires an artifact even on failure. All URL routing safeguards, no-WP-writes policy, hosted non-persistence disclosure and NYPL block remain unchanged. Never store visitor records, raw HTML, node dumps, media binaries or screenshots here.

## Exact release interpretation
A completed *source* job does not establish that any browser case passed. A completed full-hosted candidate test, even if all seven cases eventually pass, **does not** qualify WordPress deployment, persist styles, demonstrate full WCAG 2.2 AA, prove rights for the NYPL Malbone reproduction, or establish field Core Web Vitals. WordPress.com Personal has no native private staging clone; this ephemeral test runs against the **published public homepage with CSS only in test-browser memory**.

## Still required
Independent QD, manual assistive technology, zoom/Safari/physical-device checks, source-specific image rights, publisher authorization, hosted real-user performance, and explicit founder release approval. Keep Focus Fieldbook/Jetpack and all 72 Margins items intact. Do not merge, deploy, edit WordPress page 6, or modify frozen PR #49.
