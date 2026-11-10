# EX2 Page 6 — Chromium Accessibility-Tree & Conversion-Path Custody (2026-11-10)

**Status: DRAFT / RELEASE HOLD.** This branch is stacked only on draft PR #1900 (parent `57260311a4bb714557cb7f77efdb616575198759`). PR #49 at `10495883299d53596992c26a8987f629b2904670` remains frozen. No WordPress CMS writes, merging, deploying, social posting, subscriptions, emails, affiliate activation or spending are authorized by this work.

## Why another test, and what is different

The existing tests cover DOM presence, computed visibility, touch target sizes, responsive reflow and CSP. They do **not** prove the browser exposes a usable accessibility name for the important links and controls. The new `verify_page6_ax_semantics.py` directly reads Chromium's CDP **Accessibility.getFullAXTree** and targets the exact Focus rail node using **DOM.querySelector + Accessibility.getPartialAXTree**. It checks the keyboard path to the CTA without changing source markup.

This test is deliberately separate from axe. It does not claim WCAG 2.2 AA certification or simulate Jetpack subscription confirmation.

## Source custody

Input: the existing `tools/experience-2/compose_page6_flagship.py`, sourcing the 11 immutable archival HTML/CSS/JS files at `experience2/home-flagship/`. The composer verifies the Git blob SHA of each file and rejects drift. An independent 2026-11-10 authenticated GitHub read of PR #1900 confirmed **11/11** expected archive source blob identities matched its exact HEAD.

The injected shell is explicitly labeled **SIMULATED WP HEADER — NOT ASSEMBLER**; network requests are aborted. All artwork and content are the current, unchanged EX2 files.

## Browser evidence and negative tests

A source-equivalent local run using system Chromium and Playwright (before this script was uploaded to GitHub) passed **14/14** combinations of 7 viewports (320, 360, 390, 768, 1024, 1440, 1920 CSS pixels) × JS on/off, with reduced-motion. It also correctly rejected all **3/3** adversarial cases:

1. Emptying the Focus rail link's visible name.
2. Hiding the Focus rail link with CSS while preserving its HTML.
3. Emptying the named investigation link in the opening evidence section.

For each positive browser case, the test checks accessible names of interactive controls, a named and visible Focus rail link reachable within 15 Tab presses, its canonical `https://finalvestige.com/focus/` target and minimum 44 CSS pixel height, 7 chapter anchors, meaningful fallback with JS disabled, and alt text for the 3 archival images. It fails on browser JS errors or root horizontal overflow. This does **not** establish whether images load successfully.

**Independent post-upload exact-commit CI/QD has not run.** The local script was source-equivalent, not a clean checkout of the new commit. Do not call this a production, hosted, axe, or WordPress acceptance pass.

## Conversion / public-site parity finding

The **WordPress REST rendered Page 1579** read on 2026-11-10 exposes the Jetpack subscription block as a link pointing to the same page, which on its own is inconclusive. A separate, **live-public** read of `https://finalvestige.com/focus/` on the same date exposes an **email-address input and a "Send me the fieldbook" button**. Thus the REST representation alone should **not** be used to assert the public form is absent. This closes the *representation mismatch* question, **not** the functional subscription confirmation gate.

The Focus page also contains a concealed post-signup download area and a direct link to the existing complete 52-page PDF. The gift-state vulnerability/repair candidate is already owned by PR #1681; do not duplicate or deploy it. No test subscriber was created, no welcome email sent, no paid order or affiliate outcome inferred.

**Commercial measurement owner remains Claude** via #820. Grok owns social asset IDs and source/UTM delivery under TASK-008; this branch adds no tracking scripts.

## Media source review (metadata ONLY)

- Apollo 1: WP media **473**, NASA image **S67-19766**, WebP, recorded **78,346** original bytes, crew alt text, NASA credit.
- Franklin Victory Point note: WP media **474**, JPEG, recorded **466,043** bytes, 1847/1848 message, a **scan of an 1869 printed reproduction**, Wikimedia Commons public-domain marking per site caption, museum object at Royal Museums Greenwich **HSR/C/9/1**.
- NYPL Brooklyn Rapid Transit 1903 map: WP media **1258**, JPEG, recorded **5,553,669** original bytes, source described as NYPL Digital Collections / US public domain; smaller responsive derivatives are available in WP metadata.

These values were read from connected WordPress media metadata, **not actual HTTP transfer observations or independent rights determinations**. Do not substitute metadata for proof of image loading or rights clearance.

## Release hold

WordPress site list `environment=all` again exposes **only production site 256784396**. The site is on WordPress.com **Personal**, where the native Business/Commerce staging clone is unavailable; the included `wpcomstaging.com` address is not a separate staging site. Isolated WordPress Playground remains the no-subscription path, but WordPress Core / Assembler execution could not be launched in the current network-restricted environment.

**Still required:** genuine isolated WordPress/Assembler render, actual media HTTP bytes, working native Jetpack confirmed subscriber flow with authorization, axe + manual WCAG 2.2 AA / screen-reader review, touch and native 200% browser zoom, Lighthouse lab and field CWV measurements, independent QD and exact-SHA CI, and founder visual/release approval.

**Offer → funnel step → blocker → change/test → evidence → owner:** Existing free 52-page Fieldbook → evidence-led homepage to Focus CTA → uncertain screen-reader naming / keyboard access → CDP AX plus keyboard gate → 14/14 local positives, 3/3 correctly failed negatives, no commercial result → interim homepage engineer; hosted signup/measurement remain Claude/Jetpack and founder release approval.

No new design chapters, affiliate links or sales claims introduced.
