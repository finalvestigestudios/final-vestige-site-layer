# R93 — Troxler fading / Zen12 pilot (HARD HOLD)
New isolated editorial and conversion review package. **No live site, Jetpack, Dispatch, tracking, merchant or homepage changes.** Created November 3, 2026.

## What this adds
- `investigation.md` original source-led Troxler fading investigation. Do not insert affiliate recommendations into it.
- `zen12-guide.md` independent full purchasing guide with vendor vs science separation.
- `zen12-A-text.blocks.html` fully usable text-only Gutenberg Custom HTML candidate.
- `zen12-B-film.blocks.html` identical main guide with a STATIC optional 40s film poster/transcript, no autoplay or broken player.
- `film-poster.svg`, `film-40s.vtt`, `film-storyboard.md`, `render_film.py`: original source-controlled film assets and reproducible renderer. The locally rendered MP4 is an offline review artifact, **not hosted or published**.
- `mind-hub-noncanonical.blocks.html`: source for PR #172 comparison only, not another live hub.
- `evidence-and-permissions.json`: 20 URLs, 34 claim decisions, 24 disabled release gates.
- `privacy-attribution.mjs`: disabled synthetic-only categorical analytics contract.
- `test-r93.mjs`: offline native Node test source. NEVER load it on the website.

## Guardrails
No clickable merchant domain in variants (even as a “source”), no active earning link, no third-party iframe/pixel, no JS/audio/video request, no second newsletter form. The prospective CTA is a *native disabled button* with conspicuous adjacent disclosure. Any future real link must be allowed by actual Final Vestige-specific merchant approval and FTC rules; do not automatically replace button.
- Exact seller researched: https://inspire3.com/ and https://zen12.com/hnp, /about, /research, /getstarted, Inspire3 privacy and affiliate recruitment on November 3, 2026. **Public recruitment ≠ account-specific acceptance.**
- Never describe 12 minutes = 1 hour, instant stress relief, improved health, guaranteed focus, neuroscience outcome, payouts/prices or merchant refund as independently established.
- A vs B is an accessibility/creative **hypothesis**, not a measured conversion lift. Current variant B is poster/transcript only; an original 40.000-second MP4 has been rendered offline, but first-party hosting, synced browser captions and release approval remain outstanding.
- Real traffic measurement held. Suppression threshold at 20. No cookies, PII, hashed email, query strings, purchase IDs, pixels, third-party analytics or inferential sales.
- Preserve canonical PR #172, Issue #150, flagship PR #49, published Puységur and Focus pages; no CMS/settings/Dispatch writes.

## Internal links / organic intent
Organic/TikTok: “Look at the cross. What happens to the ring?” → independent Troxler investigation (unpublished) → existing Change Blindness → published Puységur for evidentiary method → optional existing Focus Fieldbook → independent Zen12 guide when approved. Do not link an unpublished document from public site. No new top-level category until owner review.

## Release/QA checklist
1. Editorial checks: verify every scientific citation/quote and the 1804 source caveat; correct all visual claims from real screenshot; independent review.
2. Gutenberg stage: desktop 1440/1920 and mobile 360/390/768; native WordPress styles, no-JS, keyboard/screen-reader/zoom, contrast, reduced motion; scope CSS.
3. Video B: original 40.000-second render exists offline (540×960, 12 fps, 480 frames, H.264). First-party upload only after rights and release permission; verify VTT caption sync and native controls without autoplay; Core Web Vitals/Lighthouse check.
4. Confirm Inspire3 partner terms, exact product creative, permissions and accepted tracked link; update evidence ledger; transparent link near disclosure.
5. Independent Site QA, homepage art review, Dispatch coordination. No merge/deploy or WordPress edit until founder approval.

Run tests: `node --test mind/the-periphery-disappeared-r93/test-r93.mjs` in a full checkout. GitHub connector current environment is isolated from native checkout; JavaScript-compatible V8 assertions can be executed separately, but are not Node CI.
