# EX2 Page 6 atomic conversion review — 2026-11-08 UTC

**Status: REVIEW ONLY / RELEASE HOLD.** This is an offline composer unifying **existing** draft PR #1529 (hero) and PR #1542 (Dispatch cadence/consent). It introduces NO additional chapter, new paid product, affiliate earning URL, collection script, user data, live CMS write or deployment. Target base is #1542 at \`e11cf3b65b14de0edc214871693d6b9d45669877\`; frozen #49 at \`10495883299d53596992c26a8987f629b2904670\` remains untouched.

## Authenticated production read / source custody

Read-only WordPress \`context=edit\`, November 8 2026 UTC: **Page 6** is published, modified \`2026-11-05T12:07:24\`; **Focus Page 1579** published, modified \`2026-11-05T17:44:02\`. These are *real public production sources*, not synthetic fixture assumptions. Page 6 has 7 chapter destinations, 72 margins, 4 image elements (Apollo, Franklin, NYPL and Focus cover), 4 contextual Focus destinations and one Gutenberg Jetpack subscriptions block. Its hero secondary CTA still says **Read the investigations** and leads to \`/blog/\`; the near-form heading still says **One email a week**, in conflict with the Focus consent's publication-dependent delivery copy. The small Dispatch disclosure remains 10 px.

The existing authenticated read in PR #1529 pinned Page 6 raw content SHA-256 \`685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b\`. This is a prior custody pin, **not** a hash recomputed from the current connector response in this sprint. The native Node CLI recomputes this hash and **refuses** any mismatch. It also requires both matching timestamps and source anchors.

Authenticated in-memory read-only combination this sprint found all **five old anchors exactly once**, none of the replacements already present, and confirmed a strictly reversible proposed change. Inventory after composing: seven chapters unchanged, 72 Margins unchanged, four images unchanged, Jetpack block unchanged, Focus links **4→5**. No actual WP write. This direct V8 review used the pinned hash as an adapter; it is not equivalent to executing the native Node SHA admission against exported bytes.

## What is actually proposed

1. Keep **Enter the evidence room** as dominant historical CTA; point only its secondary companion to the established free 52-page Focus Fieldbook. Preserve all original investigation links elsewhere.
2. Make Dispatch cadence truthful: **New investigations, delivered when we publish.**
3. Put possible-commission and Privacy Policy disclosures beside the existing form.
4. Raise disclosure type from **10px, heavy letter-spacing** to **14px, regular** in both inline CSS and Gutenberg block metadata.
5. Return a local-only review HTML file plus machine-readable HOLD receipt, with a strict fail-closed source/marker check and a byte-for-byte reversal proof. Do **not** treat the HTML as an approved deploy payload.

## Test evidence and limitations

- An exact-source algorithm was exercised in isolated V8 on synthetic fixtures: **1 positive case and 16 deliberate source/consent/inventory mutations rejected**. The five-change composition was separately applied in memory to freshly read authenticated Page 6 and Focus source: **all anchors matched and the reverse comparison succeeded**. The two committed files provide native Node regression reproduction.
- **Not yet verified:** native Node running on exact exported authenticated Page 6 + Focus JSON; full WordPress/Assembler rendering; Jetpack genuine confirmation and delivery; PR #1451 Focus query-spoof correction in real WordPress; first-party and CDN archival-media response bytes; independent axe/WCAG 2.2 AA; Lighthouse/field CWV; exact-head CI/QD; founder visual and release sign-off.
- This is a **composition and conflict-resolution milestone**, not a new visual design, field performance test, successful lead, or proven paid conversion.
- Local reproduction: \`node --test experience2/review/test_atomic_page6_review.cjs\` then \`node experience2/review/atomic_page6_review.cjs --home <authenticated-page6-edit.json> --focus <authenticated-page1579-edit.json> --out <new-local-review.html>\`. The output must not exist already. Do not commit raw exports, active subscriber data, credentials, cookies or received confirmation emails.

## Archival rights and byte gate

Connected WP media metadata identifies NASA Apollo #473 (78,346 bytes), Franklin reproduction #474 (466,043 bytes), and NYPL-edited Brooklyn transit map #1258 (5,553,669 original bytes, responsive derivatives). Those are **metadata**, not network transfer metrics. The public home includes the NYPL image; private Playground candidate has excluded it. Official NYPL BRT research guide lists the Street Railway Journal [1903] map, and the Digital Collections item rights statement indicates a U.S. public-domain belief with no determination for other countries, but the exact on-site derivative **has not been cryptographically/image-source matched** to the NYPL item; image provenance and the site's global audience require final editorial/rights review. Do not replace or delete live material in this PR. Source: https://libguides.nypl.org/nyc-rail-transit/brt and https://old-digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0 and https://www.nypl.org/research/collections/digital-collections/public-domain

## Offer → Funnel step → Blocker → Experiment → Evidence → Owner

**Offer:** free Focus Fieldbook, not a claimed paid sale or treatment. **Funnel:** qualified Grok asset_id/UTM visit → archival homepage → voluntary contextual Focus CTA → independently verified Jetpack subscriber → separately merchant-confirmed purchase/cleared commission → refunds and fees → realized net revenue. **Blocker:** hero currently diverts secondary intent; near-form promise/disclosure are misleading/weak and Focus signup success can be spoofed. **Experiment:** combined hero CTA and truth-in-subscription presentation, with no collection changes or new vendor. **Evidence:** five source anchors exact and reversible in authenticated in-memory read, 17 isolated V8 checks with 16 mutation rejections; **zero real leads/orders asserted**. **Owner:** interim homepage QA/code; Claude owns Jetpack/attribution and merchant backend; Grok controls content IDs/production/posting; Praxxis independently validates TASK-008; founder controls release.

The decision KPI remains **realized net revenue per 1,000 qualified human sessions**, 7/30 day cohorts and tiny-sample warnings, **NOT COMPUTABLE** without consent-respecting actual sessions and paid order/fee data. Do not infer a sale from outbound clicks or email subscription UI.

## Release governance

Hold publication and merging. Native WordPress.com staging is unavailable on the verified Personal plan; use a free **isolated** WordPress Playground / local WordPress with Assembler for integration. This is not the same infrastructure as live WordPress.com and cannot certify Atomic/Jetpack host-specific behavior. Honor frozen PR #49, existing production Page 6, Focus ebook and 72 Margins. No new subscriptions or paid tools. A release decision requires independent QA, exact-source/rights verification, actual browser and CWV evidence, and founder approval.
