# Search, internal links and attribution plan — R49 (offline)

**No live route additions.** Proposed future landing slugs subject to site QA and founder release approval only: `/mind/` canonical PR #172; `/mind/rubber-hand-illusion/` investigation; `/mind/zen12-review/` product guide. Do not link readers to them until they are approved and published.

## Organic and short-form acquisition
- Rubber hand illusion: query intent "rubber hand illusion explained", "why rubber hand illusion works", "proprioceptive drift"; 35–40 s original educational teaser: "two brushes, one convincing hand; the 2011 follow-up makes the story stranger." Description cites Botvinick/Cohen 1998 and Rohde et al. 2011; first-party editorial destination once live, no merchant.
- Meditation audio buyer: query intent "Zen12 review", "Zen12 levels", "guided vs nature audio", "does Zen12 really meditate for you"; guide is useful without affiliate activation. No claimed use, no copied ads or bestseller/price claims.
- Follow-up depth: Puységur, ideomotor (Faraday), thought suppression (Coué), attentional blink, Stroop; avoid circular speculative references. Only live destinations initially: /free-resources/puysegurs-animal-magnetism-files/, /focus/, /editorial-standards/, /affiliate-disclosure/.

## Conceptual navigation
Explore/Library -> Mind & Perception archive -> investigative source article -> optional established Focus Fieldbook OR independent tools guide. Product guide -> editorial context, alternatives, seller-attributed features, limits, disclosure, future authorized link. **Do not turn investigative article conclusions into storefront recommendations.**

## Text vs original-film A/B hypothesis (not an experiment yet)
A and B share byte-identical guide HTML. B adds native static poster + full transcript + 40-sec storyboard/captions, no video playback until hosted. Evaluate *reader usefulness* (scroll depth/clicks to independent citations and free resource), *performance* (LCP/CLS/video cost), *accessibility* (keyboard/zoom/reduced-motion/no-JS), *outbound interest* only after partner authorization. No invented conversion rate. If the poster does not improve comprehension or engagement without latency cost, choose text.

## Privacy-safe attribution (HARD OFF)
Proposed, approval-gated aggregate fields: `topic` (rubber-hand / zen12); `variant` (text / film); `sourceBucket` (search / tiktok / internal / direct / other); `action` (article-view / guide-view / focus-link / authorized-offer-link). Do NOT store exact referrer URLs, email, name, mobile, IP, user agent, cookies, purchase tokens, querystrings, account IDs or session IDs. Pure synthetic prototype drops unknown properties, requires an allowlisted schema, suppresses all cells below 20 observations, and refuses collecting real events. Partner aggregate conversions are **not** inferred from clicks. No tracking in published pages unless separately consented and approved.

## Coordination
- Mind editorial/merchant destination owner: Issue #171.
- Site QA and independent a11y gate: Issue #126; noncanonical hub decisions require art lead Issue #150 coordination.
- Dispatch source of truth: Issue #174. Both seller-linked commercial newsletter editions remain on hold; Mind does not edit drafts, sending settings or Jetpack welcome automation.
