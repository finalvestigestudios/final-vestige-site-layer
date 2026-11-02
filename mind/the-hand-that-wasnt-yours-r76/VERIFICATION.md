# Mind R76 verification ledger — November 2, 2026

## Repository scope
Branch `feature/mind-rubber-hand-ownership-zen12-r76-20261102` originates from `main`. Only newly created paths under `mind/the-hand-that-wasnt-yours-r76/`; original homepage PR #49, lead art Issue #150, canonical Mind hub PR #172, Site QA #126, Dispatch #174, live WordPress and Jetpack were not modified. PR is DRAFT, no merge or deploy.

## Authenticated read-only site baseline
WordPress.com site Final Vestige `finalvestige.com` on Nov 2: 61 published investigation posts, 79 published pages. Read published page #1377 Puységur's Animal Magnetism Files: 153 archived source rows / 16 case dossiers; read published page #1579 Focus Fieldbook and its one existing signup. This branch contains no CMS writes, new list, merchant click activation or altered welcome message.

## Exact executed proof
- Source-controlled `tests.mjs` fetched from GitHub head and executed through a JavaScript-compatible V8 adapter: **15 of 15 test bodies passed**. This is the actual committed test logic, **NOT a native Node test run or hosted CI**. One early source-scoped regex encoding issue was corrected and fully rerun.
- Independently evaluated the exact same fetched GitHub source with **43 of 43 targeted checks passed**: A/B substantive guide parity, authentic native disabled button, near-link commission disclosure, zero active merchant URL anchors, no forms/iframes/scripts/autoplay/hosted video, accessible transcript, responsive/reduced-motion/focus styling, historical/editorial references, explicit false/null partner permissions, categorical-only disabled instrumentation, six caption cues from 0 to 40 seconds.
- Executed eight intentional adversarial changes against exact committed tests; **8 of 8 detected**: fake CSS-disabled purchase button, erased commission disclosure, active merchant checkout anchor, extra signup form, A/B guide mismatch, enabled tracking, scientific investigation replaced by unsourced copy, and captions cut to 39 seconds. These are local synthetic mutations, not live site attacks.
- Local native Python `verify_media.py`: **PASS**. Independent `ffprobe` observed **H.264 40.000 seconds, 540x960, 12fps, 480 frames**; 6 VTT caption cues, poster 540x960, contact sheet 810x960. MP4 **134,724 bytes**, SHA256 `0971888654b6ff48b0757a1df5a34b2e46e102c67accd418148b74c990bc317f`. The executed local renderer Git blob `e48feb39539aa8b1b6d9bfa48d9007b16a5396f0` matches exactly the GitHub committed file. Local VTT Git blob `e31127c52e277a7f3fc5258a645026151a308459` matches GitHub.
- Real local Chromium review-player checks, using data-injected original local content because direct local `file://` navigation returned `ERR_BLOCKED_BY_ADMINISTRATOR`: 360, 390, 768, 1440 and 1920 CSS viewport widths **PASS** for absence of horizontal overflow, accessible player controls, optional no-autoplay source and complete transcript. Media metadata loaded at 40.000s. This is **not** evidence of live WordPress rendering, real end-user caption/voice assistive technology, or a hosted video.
- Offline ZIP integrity checked and passed; media binary stays in offline review package, not WP or GitHub. ZIP SHA256 `01dcc29888abfb78781b0ec4eff6a4e8f12e0531a7be7e19ce0a0c3646c1a3ea`. No production analytics or conversions measured.

## Evidence classes
The 20 source URLs and 39 claim/permission decisions in `claim-source-matrix.json` distinguish primary scientific research, seller descriptions and legal terms, publisher live pages, government FTC/health guidance and unverified partner conditions. The buyer guide quotes no commission, price, false urgency or unsupported mental-health/wealth guarantee. Specific terms include manual post-90-day PayPal refund possibility, optional phone/SMS warnings, and possible sharing of buyer name/email/products with affiliate. No purchaser-data feed authorized.

## Unresolved release verification
- Native `node --test` on exact PR head and hosted GitHub Actions check.
- Separate editorial line-by-line research verification, merchant checkout and terms freshness recheck, FTC independent claims review.
- Real WordPress Gutenberg sanitizer/staging previews; 360/390/768/1440/1920 screenshots; keyboard, touch, reduced motion, no-JS screenreader/WCAG 2.2 AA; mobile typography/contrast; Lighthouse and p75 CWV.
- Optional first-party video upload, hosted poster and caption synchronization; inspect real 40-second playback across devices.
- Written Final Vestige-specific Inspire3 acceptance and named Zen12 exact earning URL; WEBSITE/TIKTOK/EMAIL permissions, approved creative/copyright and purchaser-data rights; founder explicit publication sign-off.
- Any A/B conversion benefit remains untested; attribution currently OFF and synthetic only.

**No live CMS, subscriptions, newsletter, menu, settings, purchaser tracking, merchant links, deployment or merge.**
