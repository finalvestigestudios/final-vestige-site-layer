# R52 QA / evidence execution ledger — November 1, 2026

## Exact state
- GitHub branch: feature/mind-change-blindness-zen12-verified-r52-20261101
- Scope: mind/change-blindness-zen12-r52/ additions exclusively; compare main...branch required before review; no merge/deploy/CMS writes.
- Exact commit/head: record in issue #171 AFTER last QA record commit, to avoid self-referential SHA claims.
- Full native Node / hosted CI: **NOT RUN / NOT VERIFIED**. Reproducible source tests committed as verify.test.mjs.
- No WordPress write, Jetpack subscriber operation, extra signup, newsletter sends, merchant links, click telemetry, or checkout activation.

## Actually executed checks
- 14 committed source blobs re-fetched from authenticated GitHub branch, inspectable against intended paths.
- 81/81 independent V8 source + safety assertions passed using actual committed files. Tested 4 consumer surfaces for zero merchant anchors, scripts/forms/iframes/autoplay/trackers, focus-visible, reduced motion; A/B exact same 14,573-char guide core; proper disabled controls with adjacent disclosure; article scientific citations and no seller brand; 53-row matrix; six 0–40s VTT cues; privacy evaluation and 10 synthetic invalid inputs; n=19 suppression/n=20 allowed; six unsafe mutations identified.
- Original Python renderer **locally executed** with Pillow + ffmpeg: 40.000 sec, 540×960, H.264, 12fps, 480 frames, 106,739 bytes. MP4 SHA256 a3f2ddd48f6cba32a186e33cca9fc0c818112df4f183b9faec2f1156a9090662. Render source Git blob SHA237665734e2ade8480dbb64812e68c80ee25a37f equals local git hash-object. Original six-scene contact sheet viewed, poster inspected.
- Offline reviewer ZIP: five file entries; zip.testzip passed; VTT six timed cues ending at exactly 40.000; HTML5 review preview uses controls, playsinline, preload none, captions and full transcript, no autoplay.
- Merchant sources (exact official catalog, Zen12 offer, About, Research, Premium checkout), FTC guidance, 2023 systematic review, real published Puységur and Focus pages, 61 posts + 79 pages catalog reviewed read-only.

## Not tested / hold
- Browser layout at 360, 390, 768, 1440, 1920; 200% zoom and screen readers; CSS sanitization within real WordPress editor; real optional video playback/caption-sync; real LCP/CLS/INP/Lighthouse; hosted CI; conversion data.
- Seller partner acceptance/channel permissions/true earning link; current checkout/refund/privacy terms; product-specific clinical evidence; QA/art and founder release approval.
- Film is kept offline; B production has static HTML fallback and transcript only. DO NOT imply the on-page video is already live.
- No dates, rates, commissions, pricing or product effectiveness invented. All substantive efficacy assertions withheld.
