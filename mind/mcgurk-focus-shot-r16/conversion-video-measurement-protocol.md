# R16 conversion engineering: accurate product positioning, original Zen12 film, privacy-off test

**Owner:** Mind & Perception, GitHub Issue #171. **State:** HOLD / UNPUBLISHED. **No WordPress, Jetpack, navigation, homepage PR #49, hub PR #172, or newsletter Issue #174 edits.**

## Seller precision is more persuasive than recycled mind-training hype

The catalog at https://inspire3.com/ lists several distinct products. **Brainwave Shots Focus Shot** is the exact SKU examined in this sprint: https://brainwaveshots.com/focus-shot . The seller specifies 15- and 30-minute recordings, two additional no-ambient-mix versions, a quick-start video, 12/18-Hz alternating pulses in its advertised full protocol, ambient sounds and brown noise. The precise usage and safety FAQ at https://brainwaveshots.com/faq describes the mechanism as **isochronic tones**, with an express claim that headphones are unnecessary and safety cautions including epilepsy. These are official seller descriptions, not verification of delivered signal or effectiveness. The cognitive/attention outcomes on the seller page are promotional assertions, not independent product-specific evidence.

**Zen12 is a separate offer** with twelve levels, twelve-minute meditation periods and four audio formats; source: https://zen12.com/about ; checkout reference: https://zen12.com/getstarted . Its claimed “one-hour equivalent” benefits are not established for the specific commercial recordings. Do not copy one SKU's format, headset needs, testimonials or study claims into the other SKU's warm-up page.

Public Inspire3 affiliate portal https://affiliates.inspire3.com/ is informational only. It does not establish this account's acceptance, product eligibility, current tracking code, authorized creatives, social or opted-in email rights. Earning href stays NULL. No merchant checkout appears as a clickable hyperlink in the unpublished HTML. The offline evidence ledger may contain official seller reference URLs for research.

## Reader journey

1. A factual source-oriented TikTok/organic hook asks why video can alter a heard sound; a cited McGurk investigation explains the audiovisual result without turning it into therapy.
2. The investigation links directly to published first-party Puységur archive and existing published Seven Day Focus Fieldbook. The latter continues using its single existing Jetpack opt-in.
3. A clearly distinct “Tools Under Review” commercial panel explains exact Brainwave Shots Focus Shot format, isochronic-versus-binaural evidence limitations, free alternatives, risks and specific buyer objections. Its CTA is visibly DISABLED and has contextual potential-commission disclosure.
4. Later, and only after QA and partner authorization, a separately approved published guide may present an authorized SKU earning URL with disclosure immediately near the link. Never force subscription as a condition of reaching editorial evidence or product guide.
5. Do not advertise unreleased /mind/ URLs as live; coordinate future Explore navigation only with homepage art and Site QA owners.

## Existing finished ORIGINAL Zen12 media: inspection, not an embed

The earlier offline production asset from [PR #229](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/229), commit dfffe093fcfcff6760cf6aeb981c788b2b10e23d, remains **UNHOSTED**. The files in this conversation were inspected at a file/stream level, not browser-playback certified:

| Asset | Duration | Size | SHA-256 |
| --- | --- | ---: | --- |
| Portrait H264 MP4 540 x 960 | 40.000 s | 155,763 bytes | c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc |
| Landscape H264 MP4 960 x 540 | 40.000 s | 149,680 bytes | eb4a3f7e7d95ce5a6ff1ba08c83e66a4f7cc94cb1e3784bd51a330650c41ab00 |
| Five-cue captions.vtt | 0–40 s | review bundle | 5924d265a8081acbef9d1599a012bae75e71096e4f60e2f17511e96a5422785d |

Original posters and full transcript are in the review ZIP. The films are silent graphics; a caption file alone may not provide equivalent information for nonvisual users. Keep the **full visual transcript below** the film with time-stamped descriptions. Confirm portrait lettering at small viewports and timecoded track playback with actual browser/AT before B becomes eligible.

The optional film is **a test hypothesis**; its existence does not establish that video increases conversions or that Zen12 works. No fake player, placeholder broken URL or media autoplay. No third-party host or paid SaaS.

## Honest text-versus-video pilot

**Research question:** When the guide is genuinely live and eligibility is cleared, does a short OPTIONAL original explanatory film improve informed guide engagement compared with exactly the same complete text guide?

**A = text only.** Full substantive Zen12 guide: original researched story, clear seller format, proof limits, useful no-cost demonstration, objections, FTC disclosure near inactive/then-authorized CTA, published Focus route. A visitor must be able to use the page without watching anything.

**B = same text plus optional film.** Exactly the same text, headings, buyer qualifications, CTA position, navigation and offer disclosure as A. Add only the original 40-second portrait film beneath the first substantive evidence paragraph. Native controls, manual playback, playsinline, preload=none, a locally hosted approved poster, tested native VTT, and a full visible or expandable on-page transcript accessible without JS. Do not change other elements; otherwise the comparison has multiple causes.

If any binary, caption, poster, hosting right or test fails, B should not be available and A remains the useful standalone guide. The film must not be a requirement to view any offer, source, no-cost exercise, or Focus resource.

**No persistent experiment assignment yet.** An A/B split by cookie, persistent browser ID, third-party tracking or device fingerprint conflicts with this workstream's privacy objective. If the existing stack cannot do short-lived server-side aggregate bucketing and measurement without sensitive data, first run a consented human usability evaluation or noncausal self-selection comparison labeled as such. Repeated visitors can appear in both arms, and any aggregate totals will be *pageview* level, not independent participants.

**Outcome definitions (proposed only):** (i) evidence/source link click and existing Focus navigation by page views before commerce authorization; (ii) authorized merchant outbound click per eligible page view only AFTER partner acceptance and measurement/privacy review; (iii) any sales solely from documented partner reporting, not from click approximations. Do not invent conversions. Time windows, variants, denominator definitions and possible self-selection and repeat-visit biases are mandatory in reports. With low or unknown traffic, do not claim uplift, statistical significance or a winning arm.

**Privacy default OFF:** no analytics beacons, cookies, IP addresses, email addresses, user agents, hashed IDs, full referrer paths, query strings, raw purchase/order IDs or session joins. If later approved, keep only coarse categories such as TikTok / organic / internal / direct / other, variant A or B, day, and aggregate count; never send identifiable click event to a third-party collector. Respect GPC/privacy requirements and any required consent. Inspect actual GDPR/CPRA applicability before enabling.

Default gates: experiment_enabled false; affiliate_outbound_enabled false; analytics_enabled false; approved_purchase_href null; hosted_film_url null. No new tracking endpoint, subscription form, email automation, server vendor, or ad pixel in this sprint.

## Proposed native video pattern (review-only; nonfunctional without approved real assets)

The exact guide must render **text first**; code below is not inserted into live CMS and must only be rendered after approved first-party URLs, captions and accessibility QA exist.

    <figure class="fv-film">
      <video controls playsinline preload="none" width="540" height="960"
             poster="[APPROVED_FIRST_PARTY_POSTER_URL]">
        <source src="[APPROVED_FIRST_PARTY_VIDEO_URL]" type="video/mp4">
        <track kind="captions" srclang="en" label="English"
               src="[APPROVED_FIRST_PARTY_CAPTIONS_URL]" default>
        Read the complete visual transcript below if this video is unavailable.
      </video>
      <figcaption>Original optional 40-second evidence overview; no Zen12 efficacy claim.</figcaption>
    </figure>
    <details><summary>Full visual transcript</summary>
      [FULL_REVIEWED_TIMECODED_VISUAL_TRANSCRIPT]
    </details>

Native controls must be operable via keyboard and touch; equivalent information must be available without JavaScript, without media loading, and with captions/transcript. Do not use autoplay, third-party video embeds, intrusive controls, signup gates, performance-heavy JS, auto-loading video or unsupported product guarantees.

## Engineering and security gates for independent QD

- Review the exact final edited HTML in WordPress staging. Gutenberg may strip unsupported markup; source-only tests cannot substitute.
- Verify 360, 390, 768, 1440, 1920 widths, touch target dimensions, keyboard/focus/reading order, 200/400% zoom, WCAG 2.2 AA contrast and visible nonreliance on color, reduced motion, forced-colors and no-JS.
- Check with real browser that no full-page horizontal overflow, unscrollable disclosure, inert fake controls, empty heading, duplicate ID or broken internal fragment exists.
- Recheck source studies against exact quotes/statistics and all merchant specification/FAQ text on publication day. Reject any extrapolation from binaural studies to the seller's isochronic protocol.
- Baseline Core Web Vitals and network waterfall; video must not fetch MP4 until voluntary click. Inspect LCP poster behavior and cumulative layout shift against A.
- Disallow script, iframe, event-handler, form, hidden field, merchant/affiliate href, checkout redirect, beacon, pixel, ID or tracker. Do not load merchant creative or open direct seller page for unapproved users.
- Verify a plain-English near-CTA commercial disclosure stays legible in every variant. Link must remain disabled while account-specific approval/rights remain unknown.
- Independently verify existing Focus form in public no-submit state. No duplicate list; Dispatch welcomes and previous Focus email untouched.
- Ask art lead #150 ONLY for visual coordination on eventual small Mind portal; do not modify flagship PR #49.
- Give Dispatch #174 source notes, SKU alignment and HOLD state only; no email draft edits or sends.

## Review and release ledger

Open: written Inspire3 account acceptance, exact eligible Focus Shot and Zen12 SKUs, approved earning URLs, actual social/creative and opted-in email promotion terms, approved filmed assets and hosting, independently vetted physiological claims, precise checkout/refund terms, Site QA #126 browser/WordPress tests, founder separate publishing and commerce go/no-go. **No CMS write, affiliate activation, tracking, newsletter send, PR merge or deployment is authorized by this draft.**
