# Apollo R221 — true mobile pinch and evidence-route custody gate

**STAGING HOLD — NOT LIVE OR INSTALL-APPROVED.** Child of isolated Apollo R220 PR #1623. No modifications to homepage PR #49, Research Desk PR #158, WordPress, creator channels, analytics, paid offers or payment systems. Relates #150, #820, #818.

## Implementation
This commit introduces a Python Playwright/Chromium staging acceptance suite with byte-pinned source inputs. It checks actual keyboard skip-link focus transfer, native touch and keyboard disclosure, printed source answer guide, the existing 44px+ free original-investigation CTA, no-JS and JS rendering, complete NASA source-ID-to-URL custody, external host/query restrictions, and the absence of invented map coordinates or active content. Eight malicious DOM mutations are required to fail (changed NASA destination, spoofed checkout, invented geo, embedded script, duplicate ID, hidden CTA, missing anchor, unapproved attribution query).

At 320px and 390px, the script uses Chrome DevTools Protocol Emulation.setPageScaleFactor(2) and asserts visualViewport.scale=2. **This verifies mobile page/pinch scaling; it is NOT actual Ctrl+Plus desktop browser zoom or native device/browser acceptance.** Responsive coverage is 320/390/768/1440/1920 in JavaScript-enabled and disabled contexts. No new public tracking or commercial CTA is introduced.

## Exact-source reproduction
Workspace prerequisites:
- r220/qa/semantic_gate.py Git blob e948d6a273b3d565b2126a4bc4dc4d39c4c580d8
- r219/qa/mobile_gate.py Git blob 99e4ee33e69ddeee011b33b25ab6c54fef8c8e89
- apollo-r217/build_r217.py Git blob 769b574c14a37220d522e37ceaea01044630e3e7
- R216 dist/manifest.json SHA-256 a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128
- R217 dist/manifest.json SHA-256 90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72
- Python Playwright, PHP and local /usr/bin/chromium, no network or CMS access.

Execute the new Python script in this directory with --workspace pointing at the pinned-source workspace, and --output pointing to an empty evidence folder. Default first runs the R220 parent gate (26 Chromium contexts); --skip-parent only runs the separate R221 ten-context regression, and explicitly records no parent execution for that invocation.

**Observed November 8, 2026:** Local R220 upstream receipts and screenshots were generated, but the combined invocation timed out while starting R221; do not count the combined end-to-end run as PASS. Two independent R221 --skip-parent invocations passed 10/10 browser contexts and 8/8 adversarial mutation probes each, and all 10 screenshot hashes plus JSON receipts were identical between runs. The *exact R221 executable* matches this GitHub file's blob SHA, checked after upload. The page contains only the original free investigation CTA; no verified paid product/attributed sales.

## Conversion-first decision table

| Offer -> funnel | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Proposed Apollo educator dossier -> paid order | No approved sellable rights-cleared SKU, pricing, checkout or fulfillment | Independently validate merchant offer, rights, delivery before any paid CTA | BLOCKED | Founder/Commerce/Claude |
| Grok Apollo film -> qualified Atlas arrival | No verified published Grok asset ID/post URL | Reconcile TASK-008, do not invent attribution | UNVERIFIED | Grok/Praxxis |
| Atlas NASA evidence -> free investigation | Keyboard/touch navigation, source spoofing and link tampering | R221 DOM custody + actual pinch test | LOCAL PASS | Apollo |
| Paid order -> net revenue per 1,000 qualified sessions | Missing merchant confirmations, fees/refunds, consent-safe unique session denominator | Seven/thirty-day verified cohort audit using existing governed analytics | NOT COMPUTABLE | Analytics/Commerce |

Flagship remains Apollo 1: Grok long-form (once actually published) -> Apollo source-led Atlas -> original free investigation -> *hypothetical* educator dossier after separate rights and merchant approval. No unrelated commerce inserted into tragedy context.

## Release blockers and claims boundary

R198 source ancestry discrepancy, genuine axe-core (library unavailable), actual desktop browser zoom, NVDA/VoiceOver, WordPress Core/Assembler staging, external URL navigation/CDN/CSP, production LCP/CLS/INP, hosted exact-head CI, independent QA, verified creator asset, founder approval, product rights and merchant-confirmed sales remain open. Previous local-fixture LCP/CLS is NOT production CWV. No new NASA imagery or endorsement rights are claimed. The Apollo 204 Review Board remains the primary technical source; photographs document other aspects and do not conclusively identify the ignition source.

**No production deployment, WordPress content/settings writes, creator changes, affiliate activation, spending or commercial claims.**
