# FV EX2 / first real-host visual baseline and exact Page 6 source reconciliation
Date: 2026-11-06 (PT) · **READ-ONLY / DO NOT MERGE OR DEPLOY**

## Provenance and scope
- WordPress.com connected account: production-only site `256784396`; no authenticated staging clone. Plan remains Personal, so official WP.com staging is not available.
- Real WordPress homepage Page **6**, `context=edit`, last modified `2026-11-05T12:07:24`: **150,710 source characters**; real WordPress API `context=view` rendered-content response: **171,183 characters**. These are API content strings, **not a full anonymous browser DOM or transferred bytes**.
- Exact review source: `experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json` at parent `ba8c757c7a02080d54c488674016342e75bf6832`, blob `600d687bac69539b884bd16625723f79a35d8314`. Embedded MU-plugin is 135,159 chars, isolated HTML nowdoc 50,400 chars.
- Frozen PR #49 exact head remains `10495883299d53596992c26a8987f629b2904670`; **untouched**.
- No live content, Jetpack, theme, navigation, database, subscriber, analytics, affiliate or paid-service write.

## Genuine WordPress.com screenshot capture receipts (live baseline, not candidate)
These are **WordPress's screenshot service captures of public finalvestige.com**. The connected capture API returned `status=ready`, `capture_shows=site`, `site_visibility=public` for each URL. They are not substitutes for inspected Playwright frames, axe, performance or WordPress Playground snapshots. `vpw` is the capture viewport, `w=1200` is the returned image width. The links request fresh captures.

| Actual route | Browser viewport | Read-only screenshot |
|---|---:|---|
| homepage | 320px | [Live Page 6, 320](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=320&vph=2400&w=1200&requeue=true) |
| homepage | 360px | [Live Page 6, 360](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=360&vph=2400&w=1200&requeue=true) |
| homepage | 390px | [Live Page 6, 390](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=390&vph=2400&w=1200&requeue=true) |
| homepage | 768px | [Live Page 6, 768](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=768&vph=2400&w=1200&requeue=true) |
| homepage | 1440px | [Live Page 6, 1440](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=1440&vph=2400&w=1200&requeue=true) |
| homepage | 1920px | [Live Page 6, 1920](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2F?vpw=1920&vph=2400&w=1200&requeue=true) |
| Focus offer | 390px | [Real /focus/ visitor destination](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffocus%2F?vpw=390&vph=2400&w=1200&requeue=true) |
| Focus offer | 1440px | [Real /focus/ desktop](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffocus%2F?vpw=1440&vph=2400&w=1200&requeue=true) |
| current hero destination | 390px | [Real /blog/ mobile](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Fblog%2F?vpw=390&vph=2400&w=1200&requeue=true) |

**Limitation:** the image files could not be brought into the isolated local browser runtime; therefore **screenshot content has not been visually judged**, and no side-by-side visual score, timing or mobile layout clearance is claimed. The links let reviewers inspect real visitor screenshots without modifying production.

## Exact source reconciliation performed against the connected WordPress API and GitHub
- Published **72/72** `span.fv-margin-strip__item` texts match the Blueprint's 72 public-only records after whitespace normalization. This was rechecked against the current November 5 edit source, not assumed from PR #1232.
- Both the live Page 6 editor source and Blueprint contain **all seven required chapter destination IDs**. The WordPress API *rendered content* response also contains all seven and 72 Margins elements. This is *WordPress content rendering evidence*, not authenticated theme/browser execution.
- Live editor content has **four** `img` elements (Apollo, Franklin, the still-rights-pending NYPL map capture, and the Focus cover). Isolated preview has **two** historical image elements (Apollo and Franklin). That difference is intentional and must not be erased by a blanket copy/sync.
- Live hero secondary action: **Read the investigations → /blog/**. Preview hero secondary action: **Explore the free 52-page Focus Fieldbook → /focus/**. Primary **Enter the evidence room** remains preserved. The preview also includes the mobile masthead Focus route; live doesn't share that preview treatment.
- Live page contains the Jetpack subscription block. The candidate explicitly does **not** import Jetpack configuration, users, subscribers or production signup data. The public `/focus/` Page **1579**, last modified `2026-11-05T17:44:02`, has its own live Jetpack subscription block with button text **Send me the fieldbook** and visible confirmation copy. This source check does not establish deliverability or confirmed subscriptions.
- Preview includes the isolated reduced-motion remedy from draft #1062, but the historical live source still contains the hide-all-but-first CSS rule. No live remediation occurred.
- The NYPL image capture is quarantined from review pending its precise rights statement (see #1237). Apollo and Franklin images remain editorial, without merchant endorsement.
- Direct source checks also confirmed the preview's pinned Assembler install folder, MU-plugin preview-only page guard, and five-step local import Blueprint. **Actual WordPress Playground execution was not performed**.

## New source-controlled local gate
`node experience2/home-flagship/playground/verify_page6_review_parity.cjs <PAGE6_PUBLIC_EDITOR.html> <BLUEPRINT.json> [PAGE6_PUBLIC_RENDERED.html]`

Requires two locally provided **public-content-only** files; it performs no authentication, outbound requests, mutations or copying of live site private records. It fails closed on missing chapter, altered or missing historical records, wrong Assembler folder, missing page guard, NYPL image mistakenly imported, Jetpack block cloned, missing conversion CTA, missing reduced-motion review patch or incomplete rendered response. It prints its own `qualified:false` and `wordPressRuntimeTested:false` flags. **Never interpret a green source gate as a release permit.**

Native Node regression fixture (8 cases) was exercised locally. The exact committed Blueprint was separately compared with real connected Page 6 in the authenticated read-only tool: all 72 items agree. This does **not** assert an end-to-end native WordPress staging pass.

## Conversion acceptance, owners and decision
**OFFER** existing free 52-page Focus Fieldbook → **FUNNEL** social asset `asset_id` → evidence-rich home → contextual signup CTA → independently confirmed subscriber → verified order/refund/fee → net revenue.

**BLOCKER:** Source parity and first-party live screenshot receipt are now established, but preview-as-WordPress, small-screen legibility and anonymous signup proof remain unqualified.

**CHANGE/EXPERIMENT:** Preserve the historical primary CTA; review the alternative contextual Focus CTA against the public `/blog/` baseline (separate PR #1201). Do not activate any tracking or send test emails.

**PASS EVIDENCE:** nine real-host WordPress screenshot capture receipts (not inspected frames), WordPress editor/rendered API structural checks, 72-record parity, eight local regression tests.

**FAIL/UNKNOWN:** actual isolated Assembler render; private preview safety; 320–1920 screenshots of **candidate**; genuine axe WCAG 2.2 AA; keyboard/touch/no-JS/reduced/200% zoom; selected `currentSrc` and transferred image bytes; lab Lighthouse/field CWV; subscriber confirmation; attributable sales; QD and exact-SHA green CI. **RELEASE HOLD**.

**OWNERS:** Homepage/independent Site QA: visual, accessibility, privacy and rights. Claude: attribution, Jetpack/checkout integration, production release. Grok/Praxxis: `asset_id`-consistent audience acquisition and QA, no queue changes. Founder retains merge, production release, publish and spending approvals.

**Safety:** Do not sync databases from a developer clone to production, install the review plugin on production, merge a stack, upload new assets or treat `vestigefinal-tezws.wpcomstaging.com` as separate staging. Personal-plan WP.com has no native clone. Offline public-content-only WordPress Playground is the remaining free integration path.