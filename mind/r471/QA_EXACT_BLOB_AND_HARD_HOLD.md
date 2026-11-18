# R471 QA source-readback and commercial release gate

**As of 2026-11-18.** This file is part of an **UNPUBLISHED HARD-HOLD draft branch**; this is not production QA approval.

## Execution performed

Using the authenticated GitHub connector, **nine exact committed file blobs** were reread from branch mind-r471-thatcher-illusion-offer-truth-20261118 and verified by provider-supplied content blob SHAs. A deterministic JavaScript/V8 static review ran against the returned remote source text (not a local sketch). **34/34 assertions PASS**; six deliberately unsafe in-memory modifications to disabled buttons, near-CTA disclosure, transcript, poster scripting, held merchant gate, and caption duration were all detected **6/6**.

Source checks covered nine files; 2,398-word original Thatcher manuscript; four primary research/source links and a historical efficacy boundary; both seller-free unpublished offer guides; identical A/B substantive buyer copy; original SVG poster; six consecutive VTT cues ending at 42 seconds; scoped hub and real published links; 25 source-mapped claims; all 33 commerce release gates HOLD; no active merchant link, money claim or signup duplication; mobile CSS, keyboard focus, reduced motion, and truthful attribution/net-revenue rules.

**Important test-harness history:** An initial V8 pass failed two predicates because the harness did not account for valid HTML inline emphasis inside the negative claim and the mandatory SVG XML namespace URL. The authored native regression suite was corrected, exact GitHub files reread and the final modified V8 assertions all passed. This is NOT a claim that a production browser, WordPress sanitizer or native Node suite ran.

### Independent Git object pins (blobs, not final commit)

- Article: 1e7ef7b1865cf95f9a1afad420ca4422589af4d4
- Text guide: e27148f0e3e880561628ab863ee72446dc0c699d
- Optional video guide: 4f951da4262f367dc40d3b174232bc1d9cf9d1b5
- Archive hub: 900542091263173bc83fb2e8446a08b629e7f184
- Original SVG poster: 9670780988f35c91f5363bc430e32263454357af
- Caption VTT: e7b317c913c9498f9d91b828aa962c709998b098
- Product/FTC matrix: 456f359633f0db148ed228a11585baa67bf030a6
- Revenue acceptance: a4bd7972c90fb56c2ffd759c152e57dc75527a4c
- Native test source: 5a944f94c8d9b8d4596be137f7b50fd231d23ddb

## Reproducible native test command

Node 18+ with local repository checkout:

    node --test mind/r471/qa.test.cjs

The **22-case native Node suite is committed but NOT executed** in this run. It must pass on the final commit before any release. The 34 independent exact-blob V8 checks are NOT equivalent to a browser a11y audit.

## No-pass acceptance still required

- Playable 42-second film has NOT been encoded in R471. The SVG poster, timed captions and full transcript are source-only. No playback, soundtrack or hosted-video claims.
- Actual stage/browser viewport captures at 360, 390, 768, 1440, 1920 px, mobile tap, keyboard, screen reader, zoom, contrast and WCAG 2.2 AA: **NOT RUN**.
- WordPress sanitization, plugin/theme behavior, no-JS native site behavior and real performance/CWV: **NOT RUN**.
- Merchant exact current checkout, real publisher approval, website/social/email rights, purchase/refund/settlement: **NOT AUTHENTICATED**.
- Existing Jetpack subscriber confirmation, welcome delivery, unsubscribe and native consent-review: **NOT RUN**.
- Actual Grok public media IDs/asset hooks/link rights: **UNVERIFIED**.
- Real A/B randomization, qualified-human sessions, verified paid orders, independently settled commissions and refund-adjusted net per thousand: **NOT AVAILABLE / NOT COMPUTABLE**.
- No new measurement script, affiliate link, active seller URL in buyer HTML, new list, checkout or live production navigation was created.

## Owner handoff

Founder/Commerce: named partner eligibility, actual SKU, checkout/returns and signed release. Praxxis/Grok: independently authenticate real published asset IDs; no production queue edits. Claude: WP staging/analytics and existing one Jetpack signup verification. Site QA: independent native Node, browser, rights, medical-claim/disclosure and a11y review. Dispatch: only coordinated offer-specific evidence; no newsletter edits.

This QA file records **BUILT** and **exact-blob SOURCE-TESTED**, explicitly not **LIVE**, **MERGED**, **DEPLOYED**, **AUDIENCE A/B TESTED** or **REVENUE VERIFIED**.
