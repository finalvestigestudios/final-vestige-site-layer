# R455 QA / release receipt

**DRAFT / commercial HARD HOLD.** All source-controlled assets under `mind/r455/`. This is a review-only, isolated GitHub branch. No deployment, CMS write, affiliate activation, consumer A/B test, external email, social post or expenditure.

## Executable checks committed
- `node --test mind/r455/*.test.mjs` is intended for native Node 20+; see `SOURCE_CLAIM_AND_RELEASE_GUARDS.test.mjs`.
- Release hard-stop for every one of 28 matrix gates, missing approval and earning URL, invented paid order, literal active merchant URL, duplicate lead form and forced playback.
- Equal main text A/B so the video is the *only* conceptual treatment difference; no claim of statistical power or actual test assignment.
- Check that the SVG is inert with title/description and the six WebVTT cues span 42 seconds. This is not evidence that an encoded video plays or is WCAG compliant.
- Test that affiliate disclosure is adjacent to a natively disabled button, not merely aria-disabled.
- No duplicate analytics scripts or opt-in forms. Respect consent and existing first-party script owner.
- Read-only source assertions and synthetic mutations may detect bugs but cannot replace actual browser, site QA, current authorized checkout or merchant reconciliation.

## Human review needed before release
1. Accurate independent product-specific claim substantiation, not generic hypnosis studies.
2. Founder approval, named publisher permission, authorized SKU, permitted channel, issued earning URL, live checkout and returns.
3. Native Node/hosted CI executed and passing on final exact commit.
4. Browser at 360/390/768/1440/1920; screen reader, keyboard, reduced-motion, no-JS, security headers and Lighthouse/CWV.
5. WordPress paste/sanitizer and exact existing route link audit.
6. Original encoded accessible 42-second video (optional, no autoplay) with tested caption sync, playback, poster and transcript.
7. Existing Jetpack confirmed opt-in/welcome/delivery without replacing messages or creating duplicate signup.
8. True paid conversion/settlement/refund/fee reconciliation and qualified human denominator.

**BUILD/TEST/LIVE/VERIFIED distinctions:** Source files BUILT in PR. Any run-specific executed checks and exact SHA must be reported in Issue #171; this draft README is not evidence of having run them. Playable video, browser validation, WP saved draft, merchant approval, paid conversion and revenue are NOT LIVE/NOT VERIFIED.
