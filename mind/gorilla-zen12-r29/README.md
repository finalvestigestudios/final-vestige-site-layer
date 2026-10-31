# FV Mind & Affiliate Studio R29 — Source-controlled draft / HARD HOLD

**31 October 2026 · Owner: Issue #171 only · No CMS or merchant activation.**

## Original deliverables

1. `investigation.md` — 2,065-word original, research-linked historical/scientific investigation *The Gorilla Was Never Invisible*, including original 1999 conditions, 2010 sequel, 2013 radiologist study, 2005 attentional-goals research, Puységur method bridge and free exercise. No commercial recommendation.
2. `investigation.wp.html` — styled Gutenberg-ready HTML for editorial review, **not CMS published**. One malformed-link issue found during source QA and corrected before this PR was prepared.
3. `zen12-guide-a.wp.html` — approximately 1,542-word independent text-only guide built against exact public Inspire3/Zen12 descriptions, offers, objection handling, payment-field observation, free practice, scientific limitations and disabled disclosed CTA.
4. `zen12-guide-b.wp.html` — A's entire substantive copy unchanged, plus optional original 40-second poster/transcript concept; **not** a rendered/hosted playable film.
5. `zen12-40s-poster.svg`, `zen12-captions-draft.vtt`, `film-protocol.md` — original poster geometry, draft caption timings, transcript, storyboard, no-autoplay and low-bandwidth production requirements.
6. `mind-hub-alternative.wp.html` — polished no-JS responsive /mind/ source candidate organized into four streams, independent of existing hub PR #172 and homepage PR #49. Links to real published evidence/Focus only; no merchant buttons.
7. `claim-evidence-permissions.csv` — 51 discrete evidence and permission entries with public source URL, status, caveat and release gate.
8. `navigation-test-plan.md` — SEO routes, correct internal links, one Jetpack/Focus welcome preservation, controlled A/B and security/accessibility acceptance.
9. `privacy-off.cjs` — OFF-by-design synthetic first-party events (no network or browser hooks); rejects PII/raw referrers/timestamps and suppresses aggregate cells below 10.
10. `qa.cjs` — reproducible source-level guards, A/B copy lock, source checks, disabled CTA/near-disclosure verification, no external merchant href, accessible video-concept constraints and deliberately unsafe mutation rejection.

## What was independently inspected on 31 October 2026

**Live WordPress read-only:** Production still has 61 published investigations (titles/excerpts reviewed), live original Puységur Animal Magnetism Files page #1377 (source dossier corpus), existing Seven Day Focus Fieldbook #1579 (the only Jetpack download/subscription route), existing affiliate disclosure #14 and theme Assembler presets. The entire body of all 61 posts was **not** audited.

**Primary/scholarly source trail:** https://doi.org/10.1068/p281059 (original 1999 publisher abstract); https://doi.org/10.1068/i0386 (2010 follow-up); https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/ (2013 expert observers open primary manuscript); https://doi.org/10.1037/0033-295X.112.1.217 (attentional set review); https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/ .

**Exact merchant sources:** https://inspire3.com/ (product catalog), https://zen12.com/ (distinct Beginner 6 levels/24 MP3, Premium 12/48, Advanced final 6/24 and merchant-advertised one-year money-back), https://zen12.com/about (four listening styles), https://zen12.com/getstarted (observed Premium checkout name/email/mobile/postal/payment fields and seller-advertised benefits). Live dollar numbers, bonuses, timers, savings and refund enforceability were intentionally **not** reproduced or certified; a visible mobile field is **not** proof that it is required. Public https://affiliates.inspire3.com/ contains self-reported commercial claims and signup/login, not proof of account acceptance, authorized SKU links, traffic/email permissions, approved creative library, or specific terms. No authenticated approved swipe or creative pack was available to inspect.

**Regulatory/safety:** https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking (near-link clear commission disclosure); https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance (product health claims require adequate support); https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety (research on classes of meditation, not independent verification of Zen12). No medical, psychological, wealth or compressed-one-hour claims endorsed.

## Executed test evidence — precise limitations

On exact committed file readbacks using the GitHub connector, `qa.cjs` was evaluated in isolated JavaScript V8 with deterministic `fs/path` shims: **98 assertions passed**, including **10 deliberate unsafe regressions detected**. `privacy-off.cjs` `selfTest()` passed **34 synthetic assertions**, with `ENABLED === false`. Tests discovered and corrected a broken Markdown-link conversion, a JavaScript quote, and overstrict prose assertions. Native Node CLI execution in a full checkout, actual WordPress sanitize/staging, hosted CI, manual keyboard/screen-reader, true WCAG 2.2 AA, cross-device layout, Core Web Vitals and video master/caption synchronization remain **NOT DONE**. Reproduce locally:
```bash
node mind/gorilla-zen12-r29/qa.cjs
node mind/gorilla-zen12-r29/privacy-off.cjs
```

## Editorial/commercial state and handoffs

No purchase URL, merchant authorization, tracking tag, actual video, user analytics, sale, price, discount, paid SaaS, email form or CMS post was created. Both guide candidates carry a conditional earning disclosure immediately before the **disabled** non-navigating control. One pre-existing Jetpack/Focus subscriber path is preserved, including its existing welcome message. The article contains no commercial recommendation. Mind hub PR #172 remains independent. Homepage flagship PR #49 and Issue #150, Site QA #126 and Dispatch Issue #174 were not modified. Dispatch keeps all six campaigns HOLD_UNSENT; commercial #03/#05 remain HOLD_MERCHANT.

**HARD HOLD / approvals required:** account-specific written Inspire3 acceptance and permitted website/TikTok/email promotion; approved exact tier-specific earning link, terms and creatives; current checkout/refund/privacy/support verification; independent claim review; accessible actual original first-party video with synchronized captions if B; Site QA #126 staging and security/WCAG/Lighthouse; homepage art consultation #150 without overwrites; Dispatch copy coordination #174 only; explicit founder approvals for publication, tracking, affiliate activation, navigation, release and any sending.

**No live WordPress CMS/navigation/settings, Jetpack, homepage, email lists, newsletter campaigns, product links, analytics, merchant accounts, merge or deploy were modified.**
