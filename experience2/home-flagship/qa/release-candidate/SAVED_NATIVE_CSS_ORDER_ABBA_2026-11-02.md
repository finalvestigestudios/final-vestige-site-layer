# Same-runtime saved-Gutenberg CSS-order ABBA qualification — 2026-11-02

**DRAFT / HOLD. No production changes or founder release approval.** This experiment stacks exactly on #704 at \`124b71128c64f89d29999cd3efdaf00628c8fe03\`. Frozen #49 and the Apollo/Mind lanes remain untouched.

## Why this exists

The existing separate-run saved-page mobile 390px Chromium measurements are **3,804 / 3,872 ms** (#699, CSS after the main markup) and **3,224 / 3,276 ms** (#704, unchanged CSS moved before the hero), under 4× CPU, 150 ms latency, ~1.6 Mbps and disabled cache. The later run also measured worse FCP and desktop LCP and slight CLS. Different CI jobs can have different runtime variability, so these two pairs **cannot establish CSS parse order as the cause**. The earlier private-renderer Lighthouse results do not measure the saved native page.

## Actual same-runtime experiment

The exact committed PR #704 CSS-first Gutenberg block remains the **only release candidate**. An adversarial helper derives a temporary second variant strictly by moving that identical single \`<style>\` block from before the opening chapter to immediately before the existing first \`<script>\`. After removing that stylesheet, the two full blocks must be byte-identical; the script payload, actual archival image URLs, chapter order, evidence copy, Focus CTA and existing no-JS fallback do not change.

After the existing seven-chapter draft passes raw Gutenberg byte-readback, 5-width axe/interactions, no-JS and historical-photo network identity, the same isolated local WordPress site updates **that one disposable draft** in **A/B/B/A** order:
- A: CSS-first (existing candidate);
- B: CSS-after-markup (derived comparison);
- B: repeat CSS-after-markup;
- A: repeat CSS-first.

Each variant is independently read back from the local WordPress REST page editor, then actually served by WordPress/Assembler at the same draft preview endpoint. The existing Chromium CDP lab runs **two mobile cold-cache profiles** and a desktop profile for each position. Observer injection has been made idempotent so repeating the lab cannot multiply CLS observers. The helper also takes a 390px opening-screen screenshot for each position and restores the exact original candidate in \`finally\` even if diagnostics fail. The parent test then deletes the disposable draft.

All receipts are privacy-filtered. \`GUTENBERG_SAVED_CSS_ORDER_ABBA.json\` includes exact source SHA, version hashes, eight mobile LCP samples, FCP, response times, CLS, LCP element class (no body text, URLs or cookies), per-version median, and an explicit HOLD. Per-position native CDP receipts and four mobile screenshots are separate files in the same CI artifact. No visitor/user, Jetpack subscriber, production database or WordPress.com setting is copied. **Do not publish private browser URLs, editor state, credentials or full HTML**.

## Acceptance and interpretation

The exact-source Python tests must prove one stylesheet, unchanged editorial/rights source under relocation and fail-closed transformation. The ephemeral real-WP job must establish: byte-identical saved content for both variants, 7 chapters, same case/source identities, valid PerformanceObserver measurements, and successful restoring/deleting of the draft. Missing, altered, NaN/invalid or incomplete samples are **failures**, not implicit green performance claims.

Because this is one ABBA sequence, it reduces run-to-run server differences but **does not establish statistical significance, causal proof, or host parity**. Evaluate FCP, LCP, CLS and responseEnd together. If early CSS consistently beats late in both pass pairs, with comparable response times, that supports retaining the candidate for further optimization; if inconsistent, reject the supposed 15% advantage and investigate document latency / CSS / font/layout separately. Neither outcome changes the **RELEASE HOLD** without an actual <=2.5s mobile budget pass across the required trials and remaining independent release gates.

## Rights and operations

This diagnostic adds **no new media**, no map reproduction, no affiliate CTA, no Blue Corridors asset, and no historical claims. Apollo and Franklin original photo identities remain subject to their separate final rights sign-off; the unverified NYPL map capture stays omitted. Existing 72 Margins, Jetpack signup, and the 52-page Focus Fieldbook belong to page 6 and are **never modified by the isolated lab**.

WordPress.com Personal **cannot create a native one-click staging clone**. Disposable WordPress/Assembler is valid developer QA, not evidence of WordPress.com-hosted redirects, Jetpack behavior, Safari, real UI zoom, screen readers, physical devices or production p75 CWV. Independent QD, rights approval, hosted compatibility and founder exact-SHA release approval are still missing.

This branch is an **experiment only**; do not merge, install, stage on production, change page 6, or modify frozen PR #49.
