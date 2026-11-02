# R78 — Zen12 evidence-first pilot: preregistered A/B hypothesis and acceptance plan

**Status: UNPUBLISHED / HARD HOLD.** No release permission, live page or merchant link. Founder priority: a text-only independent buyer guide (A) vs the same complete substantive guide plus an original optional 40-second historical-perception educational film (B). **This is not a claim of higher conversion.**

## Hypothesis and treatment isolation
- Null: no meaningful difference in qualified outbound intent between A and B. Alternative: optional film may improve comprehension, trust or interest, but could also decrease them.
- The complete `zen12-guide-core.html` is included byte-for-byte in both full Gutenberg HTML candidates. Same title, notes, free exercise, source paragraphs, prospective commission disclosure and genuinely disabled CTA; only B adds the separate figure/transcript. A remains useful without video.
- Film and offer are **not** causal evidence of each other: B explicitly says the door study is not a Zen12 demonstration. Silent original art, six scene timing cues, no participant likeness, no copied advertiser media.
- Do not select the “winner” post hoc, report lift from impressions alone, or silently roll out B because it looks richer.

## Media & performance
- Offline film actually rendered: H.264, portrait 540×960, 12 fps, exactly 480 frames / 40.000s, 106,216 bytes; video SHA256 `c4983447e6acf6e57835f46d6dd2eecc4fefa6c6ee05ebff874a1b16a2a6dff9`.
- Local review ZIP SHA256 `a3aa2777ea78660761cb346895ff01eed331c219796c5d9d35cc11b3deb5312f`. Six original scene PNGs created by local `render_door_film.py`. Offline renderer SHA256 `5a80d5348b1d2bf4582a8072b0d9b8890a36872a4f37016c107f142dbaf41ed4`. Offline ZIP includes exact renderer, MP4, poster, captions, and no-JS HTML5 player.
- **Source control includes the exact caption source.** The complete renderer is also committed at `render_door_film.py`; exact Github blob SHA `f5801f4172a69559ce4bb029e5709b3c6a8d4c2e` was checked against the local executed renderer's Git blob. The filmed MP4 remains OFFLINE, not hosted or committed.
- Unpublished landing page B deliberately does **not** include a broken video tag or pretend that an MP4 is hosted. It contains an accessible original conceptual poster and full transcript. Playback requires approved first-party host with real URL and independent synchronized VTT verification, `controls`, `preload="none"`, no autoplay and no third-party origin.
- Proposed weight budgets (not measured against live WordPress): poster ≤45KB, MP4 ≤250KB, VTT ≤2KB, no autoplay or preloading. Measure mobile LCP/INP/CLS under representative throttling before approval.

## Preregistered outcomes (not live)
1. Primary: **qualified outbound intent only** (not actual purchases), by anonymous coarse channel and A/B when authorized.
2. Guardrails: source comprehension (separate non-collecting usability survey), disclosure noticeability, scroll usability, no-JS access, drop-offs, external-link correctness, Focus fieldbook path intact.
3. A/B assignment: propose a server-side stateless experiment with strictly allowed categorical cohorts only if privacy/consent approvals permit. Do not set browser identifiers, read IP/URLs with PII, or use paid SaaS. Without stable assignment, views are not independent people; do not call differences causal.
4. Minimum aggregation: suppress report groups fewer than 20 in the **disabled synthetic demo**. That threshold is an engineering precaution, not an authorization or a differential-privacy guarantee.
5. Analysis: preregister calendar interval, minimum sample size, exact inclusion criteria, guardrail thresholds, and uncertainty intervals **before** real enrollment. No p-value or lift absent genuine events. Seller conversion must come only from lawful authorized partner reporting; clicks alone are not orders.

## A11y/UX/security release checklist
- At 360 / 390 / 768 / 1440 / 1920 px: no horizontal overflow; proper text resizing at 200%; headings and landmarks; readable focus rings; color contrast; touch targets ≥24×24 CSS px (prefer 44–48); no interactions hidden behind hover.
- Keyboard through source links, native `details` transcript and any future `video controls`. Test VoiceOver/NVDA; ensure visible captions AND full transcript. Reduced motion. No-JS preserves all decision information.
- WordPress block-sanitizer inspection: no lost `disabled`, `details`, or disclosure; no unexpected theme CSS collisions, duplicated landmarks or broken source citations.
- Referrer/PII: do not start collection. No `fetch`, beacons, cookies, localStorage, third-party pixels, signup boxes, affiliate redirects, dynamic link cloak, cross-domain trackers or arbitrary user identifiers.
- FTC: disclosure immediately before earning CTA in each variant, truthful untested-product description, no seller testimonial lifted, no health/wealth promises. Separate investigation and commercial guide by page and headings.
- External links need a final manual audit, including partner-target approval, `rel=sponsored nofollow noopener` if appropriate, safe new-tab behavior if used, and no accidental merchant action while disabled.
- Before publication, confirm affiliate acceptance, *Zen12-specific* authorized earning destination, website/TikTok/email channel rights, creator licenses, current terms and checkout, purchaser-data policy, source claims, staging accessibility and explicit founder release permission. All remain false in matrix.

## Internal-link/navigation map (no live link to unpublished material)
- TikTok/organic search: "the door study," "change blindness," "did you notice the person swap" → article **only after publication**; never send traffic to a 404.
- Article → original 1998 study and optional Puységur archive; research context first.
- Hub → four streams; known live Puységur and Focus only. Link new article and buyer guide only after their respective approval and live existence.
- Buyer guide → NCCIH/2023 EEG review/editorial standards/affiliate disclosure; optional `/focus/` link preserving one list; disabled merchant CTA until authorization.
- Dispatch #174 remains independent: no newsletter manuscript edit, no email send, no alteration to Jetpack excerpt mode or welcome message. Commercial excerpt links stay NULL.

## Actual completed vs outstanding
**Completed:** 2,034-word door investigation, ~1,484-word Zen12 visible guide, two HTML variants, noncanonical Mind hub, 39 evidence/rights decisions and 22 source URLs, 35 source-controlled native Node tests, disabled synthetic-only attribution, six-scene 40s offline film, VTT captions, offline review player.
**Outstanding:** native Node execution on actual source in a clone; hosted GitHub Actions; actual WordPress staging rendering, keyboard/screen readers; hosted MP4+VTT sync; A/B assignment and traffic; merchant written rights; privacy buyer-data determination; independent claims/legal review; explicit founder publication authorization. No real analytics or conversions exist from this pilot.
