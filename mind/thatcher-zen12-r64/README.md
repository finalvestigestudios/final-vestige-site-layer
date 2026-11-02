# Final Vestige Mind & Affiliate Studio — R64 / Thatcher + Zen12 decision-architecture pilot

**Date:** November 1, 2026 (America/Los_Angeles). **Stage:** DRAFT / unpublished / hard hold. **Owner:** Mind & Perception only. **Scope:** `mind/thatcher-zen12-r64/` (new files; no shared code rewritten). **Base:** main at `77a87635eb613ce6de268aee11350fa8242efa0f`.

## Why this sprint is different

Previous Mind drafts explored one research phenomenon at a time. This milestone advances a **single customer decision**: does a short, structured audio offering fit the reader's preferences, and are the effect claims distinguishable from the listing of features? The guide is useful without monetization. It is not a conversion optimization result.

**Main deliverables**

- `investigation.md`: original ~2,145-word science/history investigation into Thompson's 1980 Thatcher illusion, with subsequent 2007/2014/2015 competing interpretations, methodological limitations, an ethically sourced self-made experiment, and the separate Puységur historical-evidence bridge. No product mentions or commercial CTA. Do **not** use or scrape the copyrighted original Thatcher photograph.
- `guide-core.html`: evidence-first, ~1,662-word Zen12-specific buyer guide. Named vendor sales, About, Research, checkout and privacy reviewed. Seller-described twelve-minute sessions, twelve levels, four styles and forty-eight MP3s are explicitly attributed; unsupported hour-equivalence and health claims are **not endorsed**. Addresses commercial objections, a free three-occasion preference test, mobile-number collection, marketed guarantee, possible affiliate information sharing and misleading scarcity.
- `offer-a-text.blocks.html`: WordPress Custom HTML **unpublished** candidate, full guide, native disabled purchasing control, clear prospective commission disclosure, authentic existing Focus/Puységur links.
- `offer-b-video.blocks.html`: **same exact guide** plus original poster, 40-second film transcript, six timed cues and optional film concept. There is **no pretend video element** in the WordPress candidate while the MP4 is unhosted: offline player with actual MP4 and VTT is available separately. No autoplay or remote asset.
- `render_film.py`: original no-external-assets, deterministic 40-second, 540×960/12fps H.264 short renderer for **offline review**; not a vendor endorsement. `film-poster.svg` and `film-captions.vtt` source controlled. Local render verified 480 frames/40.000s and six scenes visually inspected after repairing clipped type and obstructive clock dial. Use only original licensed visuals.
- `mind-hub-noncanonical.blocks.html`: four-stream preview matching the site's published bronze/ivory design, with working published links, never pretending new articles are live. **Authoritative hub PR #172 stays unchanged.**
- `claims-and-release.json`: **48 explicit decisions**, including seller-description boundaries, independent evidence, affiliate permissions and operational release blockers. `source-register.csv`: 21 dated scientific/official/site sources with specific limits.
- `privacy-attribution.mjs`: completely inert, pure-function synthetic aggregator with strict enumerated schema and k≥20 suppression. No IP, referrer, identifiers, cookies, email, beacon, listener, network calls or live reporting. It deliberately throws on attempted outbound activation.
- `verify.test.mjs`: seventeen offline Node tests including adversarial mutation checks. Run `node --test mind/thatcher-zen12-r64/verify.test.mjs` in the complete repository at this exact SHA.

## Official-sales-page message match (not borrowed ad copy)

| Seller audience/objection | Specifically observed named source | Original independent message, not seller proof |
|---|---|---|
| “I have no time” / restless | Zen12 /hnp describes 12-minute sessions | “Twelve minutes is a format, not an efficacy result.” |
| “I cannot meditate properly” | /hnp and /about market hands-off entrainment | “A sound and a claim about what it does are different kinds of evidence.” |
| “What do I receive?” | /hnp lists 12 levels, 4 styles, 48 MP3s | Enumerate **seller-described** deliverables and explain not independently inspected. |
| “Which style suits me?” | /hnp offers guided/music/nature/white noise | Free 3-occasion nonclinical preference exercise before shopping. |
| “Is it scientifically proven?” | /research and /hnp cite broad entrainment claims | Product-specific RCT/equivalence evidence **not established**. |
| “Can I get my money back?” | /hnp promotes one-year guarantee | Attribute seller claim; never claim refund tested. Do not transpose Hypnosis Live's different terms. |
| “Why does checkout need a phone?” | /getstarted shows Cell/Mobile field; /privacy discusses communications | Field observed; requirement and individual sharing **unverified**. |
| “Is the countdown or discount real?” | public checkout displays offer terms and countdown | No quoted price, scarcity, deadline or earnings assumptions. |
| “Can a site promote this?” | Public affiliate recruitment exists | Does **not** establish account-specific acceptance, specific URL, channel rights or swipe licensing. |

**Verified public sources:** https://inspire3.com/ ; https://zen12.com/hnp ; https://zen12.com/about ; https://zen12.com/research ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://affiliates.inspire3.com/ . FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . NCCIH: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety .

**Internal verified anchors** (WordPress authenticated read-only inventory confirmed 61 published posts, 79 pages, actual Puységur archive page ID 1377, Focus page ID 1579): https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/ ; https://finalvestige.com/editorial-standards/ ; https://finalvestige.com/affiliate-disclosure/ . Current historical categories and the existing single Jetpack/Focus funnel remain intact.

## Organic search / TikTok route without invented content

1. **Thatcher illusion / why faces look normal upside down** → original source-led investigation (unpublished; no fake route). TikTok needs original permitted face demo or text/geometry diagram, must never imply a diagnostic outcome.
2. **Face inversion / local versus global features** → 2014 evidence in investigation; offer a sketch-and-consent exercise before any product guide.
3. **Do brainwave audio tracks equal meditation?** → independent buyer guide: measure the claim against an actual comparator, not theoretical audio rhythms.
4. **12-minute meditation for beginners** → free preference protocol and existing Focus Fieldbook; optional buyer guide directly accessible, never forced through a new opt-in.
5. **Puységur / hypnotism source history** → published archive; no suggested efficacy of eighteenth-century magnetic cures.
6. Future entries **change blindness, invisible gorilla, attentional blink, Coué/self-hypnosis, Braid, cocktail party** should link only once their specific posts have founder-approved published URLs. No stale or fabricated internal links.

Proposed structure: TikTok/organic → published historical/science investigation → optional Focus Fieldbook OR direct independent buyer guide → properly disclosed earning link only after approval. The investigative article **must remain commerce-free**, while a separate Tools Under Review section is appropriately labeled.

## Video-vs-text test hypothesis (no guaranteed uplift)

- **A:** full source-led text guide. **B:** identical guide plus original, optional 40-second film. Explicitly avoid changing copy, CTA, disclosure or price between variants.
- **Primary, only after lawful opt-in and separate analytics approval:** eligible outbound-intent rate per anonymized aggregate view, not a claim of actual purchases. Partner conversion reporting can be analyzed separately *only if partner terms and privacy permit*.
- **Secondary:** voluntary film play, Focus Fieldbook navigation, source-link use; do not interpret a click as a sale or as health improvement.
- **No hidden identifiers:** no persistent ID, raw referrer URL, query strings, IP, email or per-visitor event log. Proposed dimensions are only topic, known coarse source, variant and event type. Suppress all groups <20; document resulting measurement limits. Before any real test, review data handling, visitor notice/consent requirements, sample size/power, randomization fairness, accessibility, bot filtering and channel attribution. Current `ACTIVE=false` means **zero collection**.
- On a published candidate, video should be first-party, no autoplay, controls + captions + transcript, poster only fetched initially, `preload="none"`, sane mobile aspect and static no-JS support. Never lazy-load the substantive article copy behind JS.

## Reviewer QA and security checklist

**Known completed from source:** native disabled button, commission wording directly adjacent, no merchant anchor, no external embedded pixels, no forms/scripts/tracking, sourced copy, exact A/B shared core, transcript, VTT continuity, original renderer, standalone original poster, mobile CSS at ≤390 and ≤840, reduced-motion media rule, contrast-aware tones, focus-visible styles, privacy allowlist and fail-closed mutation tests.

**Not tested; remain unverified:** WordPress sanitizer/Custom HTML block behavior on real staging, WCAG 2.2 AA screen-reader run, keyboard/touch at 360/390/768/1440/1920, 200–400% zoom, color contrast measured by tooling, video VTT in a deployed first-party player, Lighthouse/CWV, real publisher partner link, any product experience, refunds, sales, real conversion A/B results, Google Search Console or TikTok performance. Do not treat source/static checks as a full QA pass.

**External content security:** Until authorized, do not hotlink a merchant checkout; when approved, use only merchant-supplied final earning URL without cloaking, no extra redirect chain, and `rel="sponsored noopener noreferrer"` if opened in a new tab. Any change to CSP, WordPress settings, theme, menus or header requires independent site/QA approval.

## STRICT RELEASE HOLD / coordination

Written Final Vestige-specific Inspire3 acceptance, approved tracked Zen12 URL, channel-specific website/social/TikTok/**email** permissions, creative assets rights, current checkout/price/guarantee/privacy check, independent product-claim legal/FTC review, real Site QA/browser/a11y/performance, founder exact-commit sign-off, WordPress release approval and approved video hosting/caption sync are **not established**. No affiliate earning link, paid SaaS, newsletter duplication, merchant contact, CMS write, live navigation change, merge or deployment allowed.

**Cross-lanes:** Homepage PR #49 / art Issue #150 own flagship design; leave them intact. Site QA Issue #126 independently verifies claims/accessibility and may request changes through review comments. Dispatch Issue #174 owns Jetpack draft campaign; this lane owns **presell pages only**, not editing/sending six issues or replacing the existing Focus welcome email. Its separate **email authorization** must be verified, even if website rights arrive first.
