# R451 QA, provenance and commercial hard hold

**2026-11-17 11:xx PT · Mind & Perception · source-controlled DRAFT only.**

## Executed against exact committed GitHub UTF-8 source blobs

An independent read-only V8 source audit fetched the nine committed branch files. **59 / 59 source assertions PASSED.** The initial negative-fixture run detected **11 of 12** deliberate unsafe changes; the 12th fixture had failed to modify its intended source because of backtick-quoted markup. After correcting that fixture (not changing the article, offer copy, or any gate), the negative probe correctly caught the false “affiliate click = sale” statement: **12 / 12 deliberate unsafe synthetic modifications detected**. Do not present this as 12 simultaneously rerun fixtures; eleven passed on the first pass, the corrected twelfth passed separately. The first source audit before fixing two regex false positives had **52 passing, three false-positive failures** (the film's prose mentioned "autoplay" and a naive tracking-regex matched `ref=` inside `href=`). The reproducible committed Node checker was patched to inspect actual elements and tracking parameter boundaries, not harmless written descriptions.

Checks cover 3 HTML documents (language, responsive viewport, noindex/nofollow, one main landmark, no active JS/forms/iframe/video, reduced-motion rule, visible keyboard focus, no remote media); two buyer variants (native disabled purchase control, prospective commission disclosure before and close to button, lack of earning URL/tracking); A/B exact same `<main>` buyer copy; B-only original film concept without autoplay or pretending playback; inert SVG poster; six VTT cues ending at 42 seconds; 4 hub streams, zero duplicate Jetpack form; structured 27-claim/16-source matrix, all **28/28 release gates CLOSED**; a >2,700-word original sourced investigation with historical limits; and first-party UTM/asset_id events segregated from independently confirmed paid order/commission.

**Important scope:** These are *source/static checks*, not actual DOM execution, CSS contrast measurement, native Node execution, live WordPress parsing/sanitization, Lighthouse/CWV, signed-partner validation, encoded film playback, Jetpack delivery, merchant checkout, paid settlement or statistically supported A/B revenue evidence. The committed `check_r451.mjs` is provided for later native Node reproduction but **was not executed in Node**. The raw GitHub branch is not production.

### Exact Git blob IDs verified

| File under `mind/r451/` | Git blob SHA | UTF-8 characters |
|---|---|---:|
| `THE_VOICE_YOUR_EYES_INVENTED.md` | `4f8355d0599abad768a0c5954e550e881871fd88` | 18831 |
| `ZEN12_A_TEXT_ONLY.html` | `47b67731423d1c2dbd2a1de8c1cfa6e281336b53` | 10160 |
| `ZEN12_B_OPTIONAL_FILM_CONCEPT.html` | `406f19912e15d32b1f2c7710561619f123cd9251` | 13114 |
| `ZEN12_42S_POSTER.svg` | `a13a6d7f8d700ec59fbcb71001d00543006a1d40` | 1171 |
| `ZEN12_42S_CAPTIONS.vtt` | `55eb7ae3f5d1956e878841c329fa00f1e3e398d1` | 564 |
| `MIND_HUB_WORDPRESS_SOURCE_ONLY.html` | `68cd36d324ffab27e196a08d5959fd90fea87c7a` | 6099 |
| `CLAIM_SOURCE_PERMISSION_MATRIX.json` | `5f1c9a95158d6259fd407689d6ee64ba9eab8d46` | 9166 |
| `OFFER_CREATOR_REVENUE_ACCEPTANCE.md` | `19f77336b181859792b183526637a56b267e661b` | 9137 |
| `check_r451.mjs` | `a9a954db9310d6ab5e83d2ab133e590fd8198b78` | 3194 |

## Actually consulted source and offer surfaces

- McGurk/MacDonald primary 1976 https://doi.org/10.1038/264746a0
- Mallick/Magnotti/Beauchamp 2015 https://pmc.ncbi.nlm.nih.gov/articles/PMC4580505/
- Original coauthor retrospective https://pubmed.ncbi.nlm.nih.gov/31264593/
- Eye tracking 2015 https://pmc.ncbi.nlm.nih.gov/articles/PMC4437244/
- Sumby/Pollack 1954 DOI https://doi.org/10.1121/1.1907309
- Ingendoh et al 2023 14-study EEG review https://pubmed.ncbi.nlm.nih.gov/37205669/
- History archive https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (live URL cited from Issue #171; the live page was temporarily HTTP 429 on this run; archival interpretation grounded in existing issue/project history, NOT a new successful full-page fetch)
- Existing free Fieldbook https://finalvestige.com/focus/ and Dispatch https://finalvestige.com/dispatch/
- Inspire3 https://inspire3.com/ ; specific Zen12 https://zen12.com/about , https://zen12.com/ , distinct promotion https://zen12.com/secret/
- Exact other product guides https://hypnosislive.com/mental-skills/total-focus and https://brainwaveshots.com/focus-shot
- Public partner portal https://affiliates.inspire3.com/
- FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance

Public seller catalog/promotion contain mutable prices and seller-guaranteed results; these are NOT imported as verified referred prices, compliance evidence, product-specific efficacy or Final Vestige permissions. Public portal general payout advertising is NOT authenticated publisher-specific payout. Consumer marketing email and a Reprogram.ME waiting-list “access approved” subject are not affiliate acceptance.

## Hard NO-GO acceptance

**P0:** No authenticated named FV partner acceptance, approved social/WEB/EMAIL channel, SKU, original authorized URL, permitted creatives, exact referred checkout and returns, purchase report, commissioned settlement or verifiable actual sale. **P0 fallback:** no confirmed payable rights-cleared FV-owned Mind SKU; existing 52-page Fieldbook is free. **P1:** Grok actual posted media IDs, post URLs and mobile-compatible routes unverified. **P1:** no verified Jetpack subscriber receipt and welcome-mail delivery. **P2:** original B film is poster + script + VTT, **not an encoded playable film**. **P2:** no real-browser WCAG 2.2 AA/390px/keyboard performance or WordPress sanitization completed. **P0 revenue metric:** no authenticated human-qualified session denominator or independently confirmed paid/settled net revenue; **net revenue per 1000 qualified human sessions = NOT COMPUTABLE** (not an asserted zero).

All artifacts are **BUILT** (draft branch); only above source probes are **TESTED**; none of these new articles/guides/hub/video are **LIVE**; no new commercial claim is **VERIFIED**. Existing published Final Vestige pages are independent of the draft.

Do not merge, edit live WordPress/navigation/settings, replace the existing Jetpack welcome, send Dispatch, insert affiliate URLs, create a second analytics script, launch social content, spend or deploy before founder approval and independently verified release gates. Preserve homepage flagship PR #49, Issue #150, Mind PR #172, Dispatch #174 and Grok production control.
