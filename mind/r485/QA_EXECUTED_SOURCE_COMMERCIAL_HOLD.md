# Mind R485 — executed exact-blob QA / commercial HARD HOLD

**Audit date:** 18 November 2026 (PT). **Branch:** `mind-r485-gorilla-what-experts-miss-commercial-gates-20261118`. **Scope:** new `mind/r485/` folder only; homepage PR #49, Issue #150, canonical Mind PR #172, Dispatch #174 and Jetpack remain unchanged.

## What actually executed

GitHub connector `fetch_file` fetched and confirmed the exact content and blob SHA of the nine branch files below. Deterministic JavaScript/V8 assertions ran against those returned source contents, not screenshots, draft strings or estimated files. After correcting a too-specific expected phrase in the independent validator, **55/55 final assertions passed**, including **6/6 deliberate unsafe in-memory mutations detected**. The first check attempt was **54/55** because a verifier expected the wrong wording for the article's free-access sentence; the underlying article content was correct, and a complete corrected re-run passed. No failed source finding was suppressed.

| Exact committed source file | Git blob SHA |
|---|---|
| `THE_GORILLA_IN_THE_SCAN.md` | `dcdf9c2fd8504d12f183492557c0fa18c1bd249c` |
| `ZEN12_BUYING_GUIDE_A_TEXT_ONLY.html` | `38a79c83fccf6212aa70f098ee190d1b6b2c3f7b` |
| `ZEN12_BUYING_GUIDE_B_OPTIONAL_FILM_CONCEPT.html` | `1b76144e4598dab096b7ed9e4dd26ad4bd2403cb` |
| `ZEN12_OPTIONAL_VIDEO_POSTER.svg` | `31900cc1347d62aab099b69e3e6733ea90b2c558` |
| `ZEN12_OPTIONAL_VIDEO_CAPTIONS.vtt` | `63e1fcf91d42950e8f3e9b6fe947835afdbfb7ce` |
| `MIND_ARCHIVE_SOURCE_ONLY.html` | `c7be07b611b0cbf33c802fa8ee46059d9bc9a665` |
| `CLAIM_SOURCE_PERMISSION_MATRIX.json` | `580c54c4dafaba4809f5d8e59ac59065ba000f91` |
| `OFFER_FUNNEL_CONVERSION_AND_GROK_HANDOFF.md` | `be66a8558760158d3487f7a767f4a2d6e38d243d` |
| `qa.test.mjs` | `a97638a69981a235f6d1801682261d4e3c316a33` |

Checks covered original manuscript length (2,123 space-delimited words), actual primary research URLs and caveats, buyer A/B substantive guidance equivalence, seller-vs-science separation, genuine native disabled merchant control, adjacent FTC commission disclosure, active checkout/affiliate link absence, source-only product facts, six buyer questions, free existing Focus alternative, no duplicated forms/scripts, mobile/focus CSS, original SVG title/description, six caption cues totaling 42 seconds, truthful film-concept labeling, four Mind hub streams with only existing live links, 28 claim decisions, 15 source URLs, 30 held commercial gates, real paid-versus-click accounting and the portable Node test file's presence.

All six deliberately unsafe synthetic inputs were rejected by the matching guard: removal of native disabled attribute; missing adjacent disclosure; injected external script; injected duplicate signup form; injected merchant checkout href; and false assertion that an unencoded film was ready. These were **memory-only tests**, not GitHub modifications or live-site deployments.

## What did not execute

- **Native Node:** `node mind/r485/qa.test.mjs` was authored and committed, but NOT executed in the actual checkout. V8 checks above are not represented as a native Node pass.
- **WordPress:** no Gutenberg import, actual sanitizer pass, draft CMS save, plugin compatibility test or live navigation review.
- **Browser/a11y:** no real Chrome/Firefox/Safari 360/390/768/1440/1920 screenshots, Lighthouse/Core Web Vitals, contrast-measurement, screen-reader interaction or true keyboard traversal test.
- **Film:** original SVG poster, 42-second VTT and full transcript exist; no encoded playable video, voice, licensed footage, hosting, accessible player or actual performance measurement.
- **Commerce:** no affiliate approval, assigned link, SKU, checkout, price, refund terms, paid order, reversal, settlement, commission attribution or visitor A/B test.
- **Jetpack/Dispatch:** existing single list and welcome not modified or subscriber-test exercised.
- **Social:** three candidate topic matches are research-only; no actual Grok asset_id, spoken audio, post URL or rights check confirmed.

## Release hard hold

As of this snapshot, the direct connected Gmail search found the 24 August 2026 Refersion **account pending** message and did not authenticate any later named acceptance. This is a search result, NOT proof of rejection or current portal status. Official Zen12 site descriptions were separately checked at https://zen12.com/about and https://zen12.com/secret/ and separated from independent efficacy. FTC source URLs: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

**Commercial CTA: native disabled. Commercial and editorial outputs: DRAFT ONLY. Verified paid commission: NOT AUTHENTICATED. Net revenue per 1,000 qualified human sessions: NOT COMPUTABLE.**

**Required release owners:** Founder/Commerce — approved payable offer; Mind/editorial — independent claim fact-check and rights; Claude — existing 1p analytics + Jetpack/checkout integration; Site QA — real browser/WP/a11y/security; Praxxis/Grok — actual matching published media IDs; Founder — final publish/merge/deploy decision.
