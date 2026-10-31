# R18 / Sperling and Zen12: Source, UX, A/B, privacy, and release protocol
**Owner:** Mind & Affiliate Studio, Issue #171 · **Current date:** 31 October 2026 · **Status:** UNPUBLISHED / HOLD  
**Branch:** `feature/mind-sperling-zen12-offer-integrity-20261031-r18` (new isolated branch from main, never from frozen homepage work).

## Workstream boundary
This directory contains an original source-led investigation, independent Zen12 buyer guide, exact-offer presell text candidate A, identical-content video candidate B, evidence matrix and tests. It is not a live WordPress page, not a launched experiment, not an authorized affiliate offer. Homepage flagship PR #49, homepage art owner #150, Mind hub PR #172, Site QA #126 and Dispatch #174 are not edited by this branch. No homepage assets, menus, CMS settings, Jetpack signup, welcome sequence, email subscriber records, newsletter campaigns, analytics settings, paid SaaS, publisher trackers, merchant purchase links, merges or deployments are touched.

## Editorial research and product-specific alignment
Sperling (1960) used controlled letter exposures, unpredictable partial-report cues and trained observers. An original static grid on the article page **illustrates**, not replicates or diagnoses, this effect. The original 1960 PDF and later scholarly context are linked in the source matrix. Puységur is a historical comparison about the evidentiary status of accounts, never a claim that his cases and Sperling's observers studied a shared mechanism.

Exact Inspire3 official catalog: https://inspire3.com/  
Exact Zen12 description: https://zen12.com/about  
Exact Zen12 product checkout: https://zen12.com/getstarted  
Merchant free-audio/newsletter path, for *research only*: https://zen12.com/welcome

We checked official product audience/format motivation, 12 levels, ~12-minute recordings, four styles, advertised 48 MP3s, bonuses and seller headphones/driving guidance. The product checkout inspected October 31, 2026 shows a countdown/discount-style presentation and requests contact details including mobile number. Those volatile terms/price/timer are **not** used as persuasive urgency or a quoted price. Refund eligibility and support are unverified. The buyer's guide addresses objections around format, audio accessibility, privacy, refund, price and evidence honestly. The exact seller URLs appear only in reviewer-facing Markdown/JSON (not clickable in public-facing pilot HTML).

The public-facing buyer recommendation is not "Zen12 is clinically proven to reduce anxiety or improve cognitive performance." It is: a structured choice of short audio files *might be convenient for someone who already wants that format*. General meditation RCTs and binaural-beat research do not support claiming Zen12-specific efficacy or equivalence to an hour of practice. No firsthand testing, savings, medical/wealth guarantees, commission amounts, merchant approved creative or promotional rights is asserted. FTC disclosure is plain-English **immediately adjacent** to a disabled button. Actual links remain absent until account-specific approval and earning URL are verified.

## Navigation and internal links: proposed, NOT deployed
Organic/TikTok factual teaser of the 1960 partial-report method -> published investigation when approved -> existing published Puységur historical archive, existing /focus/ Fieldbook and separate Zen12 guide -> merchant only if written approval and final publisher signoff permit. A future /mind/ hub in *separate PR #172* will group perception/attention, history of suggestion, free reflection and evidence-led tools. Site /explore/ could eventually link to hub only through its own separately approved release; do not assume /mind/ exists. Historical live /the-missing-caption/ may supply a contextual image-witness bridge without editing that page. Never change the site's six historical taxonomy categories merely to accommodate commerce.

## Fair A/B hypothesis: text vs optional original forty-second film
**A:** Fully useful, accessible, styled text guide, product formats, independent evidence, free routine, FAQ, FTC plain-language near-button disclosure, disabled CTA, full 40-second script transcript. No video, no JavaScript.

**B:** *Exactly identical* written product and source guide, plus one original small portrait video element. In this branch, B contains a **hidden**, visibly labeled as unhosted first-party native video slot with a proposed 540×960 `<video controls playsinline preload="none" hidden>`, manually initiated playback after future activation, poster, and English `<track kind="captions">`. There are deliberately `REVIEW_ONLY_` relative file references because film/poster/captions are not hosted; the hidden element is NOT production-ready and cannot be represented as functional. Its full transcript remains visible/available without JS, media, a consent gate or playback. No auto-play, sound surprise, external player or third-party pixels.

Existing *separate PR #229* previously produced a 40-second original silent 540×960 H264 portrait film. Previously reported binary SHA-256: `c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc`; poster `cce9065e7f4f53a34baefa628ad82af509a31f696b6e55f120d8645a6565b6e3`. R16 reported separate isolated Chromium fixture tests; **this R18 branch does not contain, fetch, rehash, host or independently play the film**. The final film's spoken words do not exist (it is silent); its **visual transcript/captions** require detailed parity/synchronization review before the B experience can be made visible or published. The R18 textual storyboard is an original updated concept, not proof that the previously rendered film displays identical wording.

Research hypothesis: adding short optional original video may help comprehension, trust or voluntary outbound engagement, **but may also harm performance, distraction or perceived credibility**. No experiment launched; conversion lift, CTR, sample size or statistical significance remain unknown. Predeclare metrics and stop rules before collection. The primary future conversion metric, if authorized, can be *approved outbound merchant clicks / eligible consent-compliant page visits*, not actual purchases. Actual sales require merchant-confirmed transaction reporting, subject to terms.

## Privacy-safe future outbound attribution (currently DISABLED)
No pixel, cross-domain tracking, user IDs, fingerprint, cookies, localStorage, email/hash, IP address, full referrer, precision location, billing data, external embed or URL query capture in either draft. No server log changes. If partner terms, privacy rules and founder approval permit a future measurement, prefer first-party coarse event counts only:
- `entry_channel`: fixed enumerated source classes `search-mind | tiktok-perception | internal-history | direct-other`, not raw UTM/referrer text or social handles.
- `article_id`: fixed content slug (not user-assigned).
- `variant`: A or B only after genuinely random, privacy-respecting exposure assignment.
- `event_type`: page view, voluntary film play, approved outbound CTA; aggregate only after minimum cell threshold.
- Reject query data and free text, opt-out signals, repeat-sensitive sessions, and reporting that could reveal individual traffic. No per-user click IDs. No collection enabled here.
- Store no claimed sale when event is merely an outbound click; only authorized merchant reporting can confirm sales.
- Baseline KPIs before launch: no invented performance uplift; monitor media bandwidth/real LCP and CLS, scroll attention and accessible completion. Pre-register decision rule and stopping thresholds, avoid optional stopping and p-hacking.

## Release checklist / independent review queue
1. **Partner:** written account-specific Inspire3 approval, exact commissionable Zen12 SKU, authorized earning URL, permission for brand creative/swipe, social/TikTok and independent opted-in email promotion, terms on referrals, link attributes and disclosure. All currently UNKNOWN, no activation.
2. **Research:** independently verify primary-page details from Sperling's original 1960 scan; check 2016/2025 context, 2024 mindfulness review, 2023 binaural EEG paper and FTC. Review final seller checkout immediately before any publication, product FAQ, privacy, refund, optional audio accessibility and supporting files; no unsourced health efficacy or urgency.
3. **WordPress:** Site QA #126 stages Custom HTML, confirms markup retained and not stripped by Gutenberg; test at 360, 390, 768, 1440 and 1920 px; real Chrome/Safari/Firefox/mobile, NVDA/VoiceOver, keyboard, touch, focus, headings, captions, forced colors, prefers-reduced-motion, 200–400% zoom, no JS; run real Lighthouse/CWV/CLS/LCP/bandwidth and offsite links. Screen-reader and mobile visual testing are not yet completed.
4. **Film:** independent verify hosted **first-party exact** MP4/poster/VTT file integrity and visual legibility, correct timed transcript/caption parity (not just same general message), visible manual/native play controls, Safari/VoiceOver/NVDA playback/captions and first-party performance; ensure no broken placeholder src or accidental media preload. B stays hidden until this is done.
5. **Attribution:** tracking OFF pending explicit terms/privacy approval; validate strict event fields, GPC/DNT where applicable, minimum-group aggregation and suppression tests in an isolated branch. No sale inferred from a click.
6. **Governance:** separate scientific editorial/claims review, art direction Issue #150 visual review only, Dispatch #174 source-only handoff without touching its six unsent campaigns, and explicit founder approval for each live CMS publish, menu entry, offsite affiliate CTA and analytics. Hosted GitHub CI must be checked rather than assumed green. **No merge or deploy on this sprint.**

## Reviewer handoff
**Site QA #126:** audit static and browser a11y, disclosure proximity, disabled CTA, hidden unhosted video, text/film parity, print/no-JS, contrast, checkout claim integrity.

**Art lead #150:** evaluate restrained charcoal/ivory/bronze typography and micro-exhibit treatment independently. No changes to homepage PR #49, no requests to modify frozen release candidate.

**Dispatch #174:** optional future source-led Sperling editorial topic, no links to unpublished /mind/ or this pilot and no commercial email copy until verified email promotional authorization. Existing Jetpack Focus welcome remains intact.

**Founder/editor:** proof/read the 2,300+ word investigation and 1,800+ word buying guide, assess whether a historic sensory-memory article connects naturally to a meditation offer; remove the offer entirely if that connection feels forced. Preserve reader value without purchase.

## Reproducibility
Run `node mind/sperling-zen12-r18/qa.cjs --mutation` in an ordinary Node checkout. The test suite will perform source guard checks and inject harmful regressions. V8 readback audit execution is separately recorded in `TEST_EVIDENCE.md`; it is not a full Node/hosted-CI claim.
