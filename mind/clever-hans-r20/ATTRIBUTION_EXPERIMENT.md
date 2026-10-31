# Zen12 offer guide: privacy, A/B design, internal links and release gates
**R20 source-controlled design — NO analytics event endpoint deployed; no live URL, no active video, no merchant CTA.**

## What a fair test actually compares

A = `zen12-pilot-A.blocks.html`: useful standalone evidence-led guide with two clearly disclosed but inactive commerce slots, free twelve-minute alternative, product features, scientific limitations, FAQ and references. B = `zen12-pilot-B.blocks.html`: EXACT same substantive markup, with one additional 42-second optional film module. The film module is explicitly marked **unhosted** and native video is `hidden` with no source; its complete script is readable without JavaScript. **This is not a live A/B test.**

The original 40s first-party Zen12 portrait film referenced in earlier Mind PR #229 is a separate asset. The new 42s Clever Hans concept has only an SVG poster, VTT draft and transcript. No new MP4 exists, and neither asset has been attached to production. Do not claim that the user has watched the new video, that captions are synchronized, or that an offline source check proves production video function.

Before any genuine B test:
- Produce original 42-second film with human-reviewed voice/speech or accurate text-only sequence; finalize complete visual and audio description.
- Host first-party under verified accessible media path; confirm poster and VTT load, proper MIME/cache headers, 0 third-party requests, no autoplay, `controls`, `playsinline`, `preload=none` (no offscreen network download), and first input safe.
- If the film mentions Zen12 or steers toward a purchase, maintain clear **audible and on-screen** disclosure where the endorsement is encountered, even when no earning link is yet live; after activation ensure exact material-connection language and role are truthful. Commercial captions cannot merely hide disclosure in a transcript.
- Synchronize VTT timestamps against finished playback and include an accessible full transcript of spoken and meaningful visual content. Show a real working user-controlled player only after successful playback and accessibility tests.
- Collect baseline Core Web Vitals at 360/390/768/1440/1920; ensure poster is small and network-cost optional. No heavy runtime or paid SaaS. Verify keyboard, 200/400% zoom, reduced motion, accessible contrast, no-JS and WordPress Gutenberg markup.

## Randomization and estimands (future, not activated)

*Hypothesis only:* adding an original optional short film increases qualified **outbound clicks per eligible page presentation** without increasing frustration or network cost. An outcome can go in either direction.

Use a **first-party, anonymous, request-level** random assignment, cryptographically fair server-side if a production approved implementation exists. Do not set cookies, localStorage identifiers, cross-site IDs, fingerprinting data or follow a visitor. Persist only daily aggregate counts of eligible page presentations and approved CTA outbound events per arm/coarse source category. Randomize each eligible page request. Because repeated visits cannot be detected anonymously, **do not claim unique visitors or person-level conversion rates**. This is a page-presentation-level experiment with potential repeat-exposure bias. Avoid sequential peeking and predetermined significance thresholds without enough traffic.

Possible broad source categories only: `tiktok`, `search`, `dispatch`, `internal`, `direct_or_other`, `unknown`. Obtain them from explicitly approved short allowlisted campaign tags or coarse first-party paths. Strip raw referrer URL, IP, UA, phone, email, name, location, account/session ID or full query string **before** any persistence. The `dispatch` category must not capture subscriber IDs or email addresses. No third-party pixel, referral leakage, link cloaking or cross-domain tracking. The upstream webserver will necessarily observe network metadata to serve requests; the analytics feature must not create or retain a separate person-level log. Respect GPC/Do Not Track where applicable, and honor site privacy policy and partner rules.

Consent/legal review determines whether event collection needs an explicit opt-in; the default is **OFF**. Until explicit approval: no source event recorded, no outbound impression/click instrumentation and no affiliate purchase link.

Attribution event schema if approved (in memory before aggregation; never persist individual events):
```json
{"day":"YYYY-MM-DD","arm":"A|B","source":"tiktok|search|dispatch|internal|direct_or_other|unknown","event":"page_presentation|outbound_cta"}
```
Persist aggregated counters only keyed by `day, arm, source, event`, without event timestamps, transaction IDs, IP or user identifiers. Set min-count reporting thresholds for public dashboards to reduce inference from sparse buckets. Clear raw event buffers immediately after aggregation; implement retention before deployment.

**Commercial conversion:** An outbound click is not a sale. Merchant-reported purchases are not measurable until the exact partner reporting/attribution conditions and data processing permissions are supplied. Do not scrape payment confirmations or join customer records. If authorized aggregate merchant sales counts are available, label clearly as merchant-reported and distinguish click counts from transactions; avoid person-level matching.

**Primary outcome candidate:** outbound earning-link clicks / eligible page presentations, only *after* consent/policy/partner approval. Secondary: click on existing free `/focus/` resource, bounce/scroll observational metrics only where privacy-safe and needed. No video-completion surveillance, scroll heatmaps, form-filling trackers, third-party analytics or fake lift.

## Internal-link and navigation plan (not implemented)

1. TikTok factual teaser or search result should land on a future organic historical /mind/ investigation, never an uncontextualized checkout.
2. From the investigation, readers may navigate to existing `/free-resources/puysegurs-animal-magnetism-files/` or `/focus/`. The full text is useful without signup.
3. Proposed `/mind/` hub (already separate PR #172) links four streams; this R20 branch supplies an **independent full hub design candidate** for review, not an overwrite.
4. Only the `Tools Under Review` stream points to proposed `/mind/zen12-guide/` once both pages are approved/published; pending draft contains NO active unpublished path link.
5. Hypnosis Live Total Focus has separate product research and would need its own specific guide/CTA; Brainwave Shots Focus Shot also needs its own. Do not send all Mind traffic to Zen12 as a universal answer.
6. Existing 61 investigation titles and six historical categories remain untouched. The homepage art lead (Issue #150) decides any small portal feature in a separate integration branch; this team does not edit PR #49.
7. Dispatch Issue #174 owns newsletter copies. Share approved eventual canonical guide URL and precise claims only after publishing; do not edit any six draft newsletters, subscriber data or existing 52-page welcome message.

## Merchant/claim release gates

- Written, account-specific Inspire3 affiliate acceptance verified (public sign-up portal is not acceptance).
- Approved exact Zen12 SKU landing URLs, permitted redirects/attribution and explicit allowed social/TikTok/website/email creative and approved-swipes usage verified; no unreviewed HTML scraping or copying.
- Current seller offer page `https://zen12.com/getstarted` rechecked before release: forms, countdown, price/discount changes, returns, support and all seller terms. Price, affiliate payout and urgency remain omitted from public editorial regardless until verified and approved.
- Verify independent evidence relevant to every *specific* health/psychological efficacy claim. Seller's 12min=1hr, automatic entrainment, treatment/anxiety guarantees are not acceptable as FV factual benefits. Evidence matrix dispositions are operative.
- Commercial disclosure on same visible region as **every active earning link**: “If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.” Keep informational commerce sections distinct from historical findings.
- Independent science/accuracy edit, legal disclosures review, staging Gutenberg render, QD/site QA #126 keyboard/AT/performance/security, homepage art #150 visual review, separate explicit founder publication approval and later affiliate activation approval.
- No CMS/navigation/settings edit, merge, deploy, subscription mutation, email send, merchant activation or tracking in this PR. `RELEASE=HOLD`.
