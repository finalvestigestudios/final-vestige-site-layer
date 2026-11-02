# Mind & Perception R74 verification / 2026-11-02

## Executed and confirmed
- Authenticated **read-only** WordPress: Puységur published page **ID 1377**; original Focus page **ID 1579**; published post list **61**. Existing Focus Jetpack form and welcome untouched.
- Merchant sources reached **2026-11-02**: https://inspire3.com/ ; https://zen12.com/hnp ; https://zen12.com/about ; https://zen12.com/research ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://affiliates.inspire3.com/ . Seller marketing is not scientific substantiation or named acceptance. FTC references available through official URLs in README.
- Investigation **1,761 whitespace-separated words**; independent buyer guide **1,613 whitespace-separated words** (includes HTML markup). Original material; no hands-on product use.
- Claim ledger: **19 registered source references, 46 decisions**; includes supported background claims, seller descriptions, explicitly unsupported benefits, unverified permissions and release restrictions.
- **34/34** exact GitHub-source **committed Node test bodies** executed in a V8 compatibility harness; no failures after fixing one initial weakness: a `class="disabled"` mutation was not correctly caught by the initial regex. Test strengthened to require the **actual native disabled attribute**; on rerun **5/5** adversarial policy mutations were caught: fake-disabled CTA, absent disclosure, unauthorized merchant anchor, extra email form, A/B guide drift. V8 execution is **not** a native `node --test` run.
- A/B candidate substantive guide core byte-identical; B has original inline SVG poster + six VTT cues + complete no-JS transcript. Both have genuine disabled HTML buttons and proximate prospective commission disclosures. No active merchant links, form, scripts, hosted media or analytics.
- Original OFFLINE video rendered from `render_film.py`: **40.000 s, H.264, 540×960, 12 fps, exactly 480 decoded frames**, file **95,575 bytes**; MP4 SHA256 `fbedff8f76002f50217541a1bd14daafd1dbe29ccd4e4b043f4c0ae7063b8e95`. Renderer Git blob `4f88a09ec0ba6124c19b3af73bda2803e05cf714` **exactly equals local `git hash-object`**. Captions Git blob `6301365b3ed7abf0cfbab2d49bf4890438db89de` equals local. Six scenes visually reviewed in actual contact sheet; ZIP integrity passed. Offline review ZIP SHA256 `6a8ad902aeec0b1a373c7f7b3eba2c34c9474442930bec3015e66a6527f58c42`.
- Offline Chromium `page.set_content()` markup/layout checks across **360, 390, 768, 1440, 1920 px**: **5/5** viewport assertions passed (no horizontal overflow, native controls attribute, captions track present, preload/poster and autoplay OFF). **Not** actual hosted playback/track sync or WordPress rendering. Browser direct localhost navigation failed with `ERR_BLOCKED_BY_ADMINISTRATOR`; explicit limitation preserved.
- No CMS content, nav, Jetpack, newsletter, visitor telemetry, affiliate/merchant access, checkout or deployment mutated.

## Not executed / independent hard gates
Native Node execution on committed exact SHA; GitHub Actions CI; WordPress staging sanitizer; front-end responsive and 200/400% zoom; color contrast quantitative audit; screen-reader/keyboard-only review; hosted MP4 and true synchronized captions; Lighthouse/CWV; authorization and channel-specific written partner rights; customer experience/refund fulfillment; actual conversion and affiliate-sales measurement; founder-approved publication.

## Reproduce after checkout
```sh
node --test mind/the-second-number-r74/tests.mjs
python mind/the-second-number-r74/render_film.py
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=codec_name,width,height,avg_frame_rate,nb_read_frames -show_entries format=duration,size -of json mind/the-second-number-r74/the-second-number-40s.mp4
```
The video generator requires Pillow, ffmpeg and a suitable DejaVu font. Video is not committed as a binary and may vary slightly in bytes with encoder versions; metadata and content design are reproducible.

## Release decision
**HARD HOLD**: no verified Final Vestige-specific Inspire3 approval, approved exact Zen12 partner link or channel/creative permissions. Text-only A versus guide+film is **an experiment hypothesis** only. Preserve untouched PR #49 and #172, art issue #150, Site QA #126, Dispatch #174, original Focus/Jetpack welcome. No live WordPress writes, merchant activation, emails, analytics or merge.
