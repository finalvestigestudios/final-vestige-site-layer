# Mind Studio R109 — Independent Editorial + Zen12 Consolidation Pilot
**DATE:** 2026-11-03 (Pacific)  
**RELEASE:** HARD HOLD / NO CMS / NO ACTIVATION.  
**Branch:** `feature/mind-attentional-blink-zen12-consolidation-r109-20261103` (branched from `main` at `77a87635eb613ce6de268aee11350fa8242efa0f`)  
**Ownership:** Mind & Perception ONLY. PR #172 remains authoritative Mind hub; PR #49 and Issue #150 remain art/homepage owner territory; Dispatch Issue #174 remains Dispatch owner territory.

## Delivered
1. `investigation-attentional-blink.md`: original long-form noncommercial investigation, Raymond et al. 1992 → lag-one sparing → spatial shift and emotion → 2007 intensive meditation findings, accurately limited to intensive training, not Zen12. Links only to already-published Final Vestige context. Proposed slug `/mind/attentional-blink-half-second/` is not live.
2. `zen12-independent-decision-guide.md`: original long-form merchant-specific buyer decision resource based on official /hnp, /about and /getstarted product copy. Contrasts 12-min/12-level/4 styles/48-MP3 full-course seller descriptions with independent science. Free preference experiment, real objections, privacy/guarantee/consumer information, neutral no-buy alternatives. Proposed slug is NOT live.
3. `zen12-offer-variant-a.html` and `zen12-offer-variant-b-video-concept.html`: two complete, self-contained Gutenberg *Custom HTML offline review* variants with identical core buying content. A is text-only. B adds entirely original lightweight CSS poster, accessible transcript, static optional 40-second storyboard. **B is NOT yet a playable MP4**. Neither uses JavaScript, a form, iframe, video src, external asset, cookie, tracking event, or active seller URL. Native disabled button + adjacent *prospective* plain-English affiliate disclosure in both. Responsive columns, high contrast, keyboard focus styles, reduced-motion support and live existing internal links.
4. `mind-hub-noncanonical-draft.html`: four-stream Mind Archive mockup, no live routes to draft items, not a replacement for PR #172. Art lead may inspect but must not alter PR #49.
5. `claim-source-release-matrix.json`: 21 named primary/merchant/regulatory/FV records; 32 explicit claim/use decisions; 26 fail-closed release gates. **New find:** exact Inspire3 Terms of Sale now readable at https://inspire3.com/terms/ . Zen12 one-year guarantee; for card payments refunded after 90 days, manually via PayPal; seller says downloadable MP3/PDF files may be tagged with identifiable buyer details; phone number may result in SMS marketing. No claims that refunds were tested, that buyers were actually tagged or that texts were sent. Prior 'Terms endpoint inaccessible' blocker RESOLVED at source access, but recheck and contractual permissions still needed.
6. `synthetic-attribution.cjs`: code-backed, offline-only categorical page/source/offer-intent counts with strict schema and reject-extra-fields, valid ISO calendar days, <20-per-cell suppression, no PII/unique tracking, both live and purchase collectors permanently throw.
7. `pilot.test.cjs`: 26 reproducible tests. `film-40s-storyboard.md` and `film-40s-caption-concept.vtt`: original 40s six-scene concept, six contiguous cues and full visible transcript; no MP4 or web hosting claims.

## Evidence and tests actually executed
- Authenticated read-only GitHub fetched 7 exact committed source blobs (pilot tests, module, A/B HTML, hub, claims JSON, VTT).
- **26/26 exact committed test bodies executed and passed in V8 with Node-compatible assert, fs/path, node:test adapters**. This verifies: A/B identical core, disabled/no merchant URL, near-button disclosure, no scripts/iframes/forms/false media, four-stream hub, accessible static fallback, complete VTT, 21 source references, 26 CLOSED gates, source ID linkage, strict no-PII synthetic event schema, calendar validation, <20 suppression and 20 threshold, 0 purchase/live collection.
- An initial 24/25 diagnostic failure identified mismatched **test wording**, not a product defect; corrected and re-executed 25/25, then added Terms verification test and passed **26/26**.
- **Native Node was NOT executed on the exact committed repository**: container Node exists, but direct GitHub clone failed due DNS restriction. Reproduce in a workspace: `node --test mind/review-r109-attentional-blink/pilot.test.cjs`. No claim of CI or browser checks passing.
- Site search via authenticated WordPress **read-only** verified live links for Puységur (1377), Focus (1579), Change Blindness (1922), Mesmerism (1924). It found no live attentional-blink page. This run performed NO WordPress writes.

## Founder conversion question: evaluate without claiming uplift
**Primary hypothesis:** Does offering a truly optional, self-hosted 40s explanatory video *in addition to identical buyer guidance* improve informed offer intent without harming source comprehension or mobile performance compared with guide alone?

- Only after all gates: approve one canonical product guide, original playable MP4 and first-party VTT/poster, browser a11y and real CWV budget; then choose a fair assignment method that respects privacy and consent. Both A and B must keep the same copy, disclosure, offer and CTA position; only optional film element differs.
- Recommended informational guardrails: source-link activation, FAQ comprehension, page abandonment, and *aggregate* intent-click rate on validated exposure denominator. A self-selected traffic split is not a randomized A/B experiment; do not invent uplift, buyers, or sales. Cell threshold of 20 is disclosure minimization, not statistical power.
- Do not send unique event payloads, IP, click IDs or purchasers to the R109 synthetic code. Real implementation requires separate privacy review and founder authorization. Prefer approved first-party aggregate counts without third-party pixels; no paid SaaS.
- Do not add an extra signup or edit the existing Focus/Jetpack welcome sequence. Dispatch Issue 03/05 remain HOLD_UNSENT and merchant-specific even if these draft guides look strong.

## Current hard blockers / next accountable actions
- Merchant/legal: authenticated Final Vestige Inspire3 partner acceptance, product/channel-approved earning URL and affiliate creative rights, permission to promote through website/TikTok/**email**, written assurance affiliate reporting excludes all personally identifying purchaser data. Public affiliate portal/sign-up and published commission advertising do not prove specific acceptance.
- Publisher: founder selects a *single canonical* Zen12 guide from proliferating R97–R109 drafts; no automatic merge of near-duplicates; align PR #172 before adding live nav/hub.
- Evidence: exact claims review against independent studies and merchant source snapshots; current Terms of Sale can now be independently reopened but actual refund fulfillment remains untested.
- QA: Issue #126 browser WCAG 2.2 AA, keyboard/screen reader, 360/390/768/1440/1920 checks and Lighthouse; native Node CI; security source-link lint; video build, first-party MP4/VTT sync and render only if B chosen.
- Release: no merge, live CMS/menu/settings/Dispatch/Jetpack write, live checkout or tracking until founder separately approves release; PR should stay draft.

## Required coordination
- #126 Site QA: review claims/disclosure adjacent to disabled CTA, static media transparency, responsive and keyboard contrast, privacy stub, current vendor Terms.
- #150 homepage art direction: share editorial 'half-second' feature idea only; do not edit flagship branch/PR.
- #174 Dispatch: offer-guide draft and legal Terms reference are **not** release approval; 03 and 05 remain unsent/merchant HOLD; no canonical live URL exists yet.
