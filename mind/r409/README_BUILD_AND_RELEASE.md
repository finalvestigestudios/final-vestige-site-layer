# Mind R409 — review-only build, media and release
**2026-11-15 | HARD HOLD**

This PR is an isolated Mind workstream continuation, **not** an authorization to publish or activate an affiliate offer. It deliberately does not edit WordPress CMS/settings, homepage PR #49, canonical Mind PR #172, Issue #150's art, Dispatch Issue #174's email drafts, or Grok's queue.

## Artifacts
- 1,794-word independent source-linked buyer investigation covering suggestion experiments, Puységur, actual Zen12/Total Focus/Focus Shot seller offers and refund/price limitations.
- A text-only Zen12 guide; B identical substantive copy + original optional 42-second **silent** video source, poster, six timed captions, complete on-page transcript, native controls, `preload=none`, no JS/third-party host.
- `MIND_ARCHIVE_WORDPRESS_REVIEW_SOURCE.html` is a source-only proposed /mind/ page, **not** a WordPress CMS draft or published route.
- 30-claim / 16-source matrix and **28 commercial release HOLD gates**.
- Creator→article→Focus→optional vetted offer map and privacy-safe business acceptance.

## Reproducible media
`python3 -m pip install Pillow` (if Pillow isn't already available; do not use a paid service).
`python3 mind/r409/render_original_video.py` (requires local ffmpeg + DejaVuSans font). Produces `zen12_42s_original_silent.mp4` in the same folder. All artwork and text drawn programmatically; no sourced images, footage, vocals, or licensed stock. Video is **silent**, not a narrated human voice. Caption track displays the six original on-screen statements and is redundant to the visible in-page transcript. Local QA render on 2026-11-15 was 42.000 seconds, H.264 320×180, 42 frames, 9,784 bytes. If media bytes are not included in this PR, source build is required before page preview and video server QA; do not call it "video playable on GitHub" before the binary is present.

Verify locally: `node mind/r409/verify.mjs`; `ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,nb_frames -of json mind/r409/zen12_42s_original_silent.mp4`.

## Additional required QA — not interchangeable with source assertions
- Real browser: test 360/390/768/1440/1920, 200% zoom, keyboard/screenreader, contrast, focus rings, touch, reduced motion, no-JS, no horizontal overflow, transcript/captions.
- Actual deployed media: same-origin H.264/MP4 content-type/range support, no preload until requested, no auto playback; B fails to load video unless renderer output is deployed alongside HTML.
- WordPress sanitization and editor theme integration: source-only HTML is not itself a saved CMS draft.
- Site links, Focus actual provider confirmation and welcome delivery, consent/privacy/campaign attribution.
- Exact named Inspire3 approval, specific Zen12 permitted channel + creative + URL + checkout/return terms, and settled commission; no activation otherwise.
- Payable rights-cleared *existing* FV-owned Mind SKU, if any, requires Commerce proof; do not infer from web free products.
- Actual monetization outcomes: **NOT COMPUTABLE** pending verified orders, refunds, fees, and qualified human sessions.

## A/B and commercial claim limits
A/B test is a **hypothesis**, not a predictor of lifts. No causal claims about product effect. One common seller-specific guide, no invented experience or price, no commission URL or event pixel. Keep the free reader choice visible and allow navigation directly to the guide without subscribing. Founder approval, QA signoff and Commerce approval needed for any live release.
