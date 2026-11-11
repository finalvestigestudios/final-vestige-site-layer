# Dispatch R281 — Independent Inbox/Consent Evidence Audit (DRAFT / NOT RELEASED)

**Owner:** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). **Partner gate:** [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). **Lead ownership:** [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129). **Business contract:** [Conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). **Stack:** new isolated R281 branch from R280 PR #2045 HEAD 56b99dc80fb32fa9d98001a2f00c022203050cd6. Original campaign PR #175 is unchanged; PR #49 remains frozen.

## What actually changed

R280 correctly refuses to turn a syntactically plausible email into sending permission. Its offline MIME tool, however, labels material as *visible* without recognizing common markup that intentionally hides content. It gathers a link from every anchor independently of whether the anchor itself is visible or whether an opt-out phrase labels that link. It recognizes postal-address *shapes*, not the publisher's address ownership. The last distinction was explicitly acknowledged by R280, but the others need independent rejection tests before relying on its structural output.

The separate **R281 reviewer** adds testable, fail-closed safeguards, without rewriting R280:
- Checks publisher-address *candidates* in BOTH HTML visible-text approximation and plaintext; never confuses this with publisher-address ownership.
- Rejects hidden/obscured evidence: HTML hidden attribute, aria-hidden, inline hidden style including CSS comment obfuscation, template/noscript and embedded style sheets. Any inline CSS is flagged for manual real-render review; this is deliberately conservative.
- Requires opt-out label text on the same visible clickable anchor; a URL containing "unsubscribe" elsewhere is not enough.
- Restricts opt-out *candidate* HTTPS origins to exact known site/WordPress hosts; rejects misleading subdomains, URL credentials, unusual ports, placeholders and non-HTTPS. New verified Jetpack opt-out hosts must be deliberately added only after observed evidence.
- Rejects unsafe active markup and attachments; does not extract or return sender address, reader address, message content, subject text or raw URLs.
- All evidence and approval booleans stay FALSE even if the synthetic MIME's structural checks are green; there is no auto-authorize path.

**Crucial limitation:** The Python HTML parser is NOT an email-client renderer, its CSS model is incomplete, and its candidate-origin allowlist is intentionally restrictive. It may reject legitimate Jetpack markup. A native editor preview and authorized real received-email inspection are still mandatory before any sender/legal/visibility finding. The tool is research QA, not a release gate replacing the founder or counsel.

## LIVE read-only WordPress evidence — 2026-11-11 13:36 UTC

- Jetpack newsletter enabled; sendable capability TRUE but **new-post auto-send FALSE**, individual-post toggle still independently matters. Full-content emails; sender display "Final Vestige Studios"; no-reply behavior; welcome message contains the **52-page Seven Day Focus Fieldbook** PDF URL.
- The diagnostic snapshot: total **3**, confirmed **3**, unconfirmed requests **2**, suppressed **0**, recent five posts all explicit never-sent-opted-out. This is **not** a total historical send ledger.
- Independent followers endpoint: WordPress.com **3**, email **0**, comment **0**, partial=false. Do NOT add the counters or infer current email-eligible people; provider recipient-level email eligibility remains **UNKNOWN**.
- /dispatch/ #523 and /focus/ #1579 remain published and were read without writes; published Editorial Standards #17 demands evidence-first claims, source accuracy, AI not a source, conflict-of-interest disclosure and visible corrections.
- Connected Gmail targeted searches found an **October 25, 2026 confirmation request** from WordPress, **not** a confirmed welcome-email delivery or Fieldbook receipt. Searches did not establish Final Vestige-specific affiliate acceptance/email-channel rights. Consumer marketing messages from Inspire3 or Hypnosis Live are NOT affiliate authorization.
- Native Jetpack **Preview email** is documented for the editor, including with sending disabled; its execution is NOT verified. Actual received MIME, real effective opt-out, publisher-specific mailing address and Fieldbook click/download remain **NOT VERIFIED**.

## Official seller alignment — never convert this into approved copy

**Issue 03 / Zen12:** The exact vendor page https://zen12.com/getstarted describes twelve levels and 48 MP3 files, with seller-marketing claims and changeable checkout promotions. These are not evidence of product-specific effectiveness, current Final Vestige-approved price, earnings URL, permitted email channel, or an issued presell guide. The vendor's separate free-audio signup is **their** consent relationship, not a Dispatch subscription.

**Issue 05 / Hypnosis Live Total Focus:** https://hypnosislive.com/mental-skills/total-focus describes a 33-minute, 47 MB recording and makes concentration/brain-enhancement claims. Its observed price displays have varied, and the refund FAQ imposes qualifications. Do not describe its advertised claims as independently demonstrated, promise stable pricing, or activate any link without exact authorized merchant evidence.

The Mind/affiliate owner must supply publisher-specific acceptance, explicit permitted affiliate email channel, approved exact tracking URL, written offer eligibility, a vetted LIVE warm-up guide and dated terms/refund check. Only then can any partner-related release evidence be marked verified. Both #03 and #05 remain HOLD_MERCHANT.

## CAMPAIGN integrity

Original PR #175 holds six issues: **4 editorial (01/02/04/06)** and **2 optional commercial placements (03/05)**. No new opt-in list, no extra send, no cadence/scheduling changes. Editorial issue #04's original subject mentions fourteen seconds but does not say what those measure. NASA's Apollo 204 record identifies approximately 14 seconds from first fire indication to cabin rupture, NOT ignition time or duration to death. R280's corrected alternate remains NOT_ADOPTED.

Under the FTC's primary-purpose rule, do NOT presume all four editorial messages are legally exempt merely because they are labeled editorial. For any commercial message verify non-deceptive headers, actual sender postal address, conspicuous opt-out, unsubscribe operationality, marketing disclosure, and 10-business-day opt-out honoring. Jetpack may supply some footer material, but this remains unverified by an inbox view. Official FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Release state — ALL FALSE, every issue remains UNSENT

| Evidence needed | Current | Human/source owner |
| --- | --- | --- |
| Provider-confirmed eligible recipient count + consent provenance | UNKNOWN | Focus/Claude, private authenticated provider |
| Original welcome actually received + public Fieldbook PDF fetched | NOT VERIFIED | Focus/Dispatch, authorized non-sending evidence |
| Native Jetpack desktop/tablet/mobile email preview | NOT EXECUTED | Dispatch, editor with sending disabled |
| Real received MIME legal footer and functional opt-out | NOT VERIFIED | Founder-authorized test only (no send authorized) |
| Valid **Final Vestige** postal mailing address | NOT VERIFIED | Founder/business owner |
| Partner acceptance, **EMAIL** permission, one earning URL | NOT VERIFIED | Mind/Affiliate #171 |
| Two approved LIVE pre-sell destinations | NOT VERIFIED | Mind/Affiliate #171 |
| Paid transactions / refunds / fees / settled net | NOT ESTABLISHED | Commerce; external account reports |
| Founder approval for final copy, exact audience, dates and send | NOT GRANTED | Founder |

No link or email send is authorized by an automated lint pass. No synthetic test, plugin settings read, marketing email, or checkout view can supply the missing account-specific evidence.

## Small-sample, one-offer revenue specification (proposal only)

1. Grok owns factual public post and immutable creator asset_id; use existing UTM convention from #820: utm_source=platform, utm_medium=organic_social, utm_campaign=approved-analytics-owner-value, utm_content=asset_id. **Mind's conflicting mind_pilot_2026_11 vs mind_proposed_2026_11 remains UNRESOLVED; don't choose silently.**
2. Focus captures one **confirmed_signup** only on a provider-verified subscription transition with appropriate consent, not on form attempts or clicks alone. An already-verified WordPress account may be confirmed without a new email-click; dedupe reactivations and exclude bounced, suppressed, paused and opted-out accounts. Do not expose subscriber identities in aggregate reports.
3. Once a newsletter is separately authorized, its **one editorial CTA** may carry privacy-safe utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_pilot_2026_11, utm_content=issueNN_destination. These are **naming proposals, not live tagged URLs**; preserve cross-channel source where consent and actual analytics allow.
4. Segment only on verified consent / voluntary reader intent, never on inferred health or other sensitive characteristics. An approved affiliate-guide click is not a paid sale.
5. Require actual merchant-confirmed paid order, then subtract recorded refunds, commissions/fees, and report net receipts. KPI = 1000 × realized net revenue / qualified human sessions for each 7/30-day cohort **only when both inputs are independently valid**; otherwise **NOT COMPUTABLE**, not zero. With a tiny subscriber population, report descriptive raw outcomes only—no A/B significance.
6. If Zen12 eligibility never verifies, do not move Issue 05 into its reserved space or activate an unapproved internal store SKU by default. Editorial-only alternatives remain subject to founder approval and legal/inbox gates.

## Conversion-first ownership board

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / TEST | PASS/FAIL evidence | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 → vetted guide → earning link | No named partner email rights / link / live guide | Signed account evidence and clicked public guide | **HOLD**; none evidenced | Mind #171 |
| Focus → subscriber → welcome | Counters disagree and actual delivery unobserved | Provider recipient-state read and existing authorized mailbox search (no new test subscriber) | **HOLD**; only confirmation request found | Focus #129 / Claude |
| Dispatch → inbox | Footer may be hidden/not publisher-owned | Native preview; independently authorized real received MIME later | **STRUCTURAL TESTED / INBOX NOT TESTED** | Dispatch #174 |
| Dispatch → guide CTA | Two current commercial placeholders | Approve actual live guides; source-tag one CTA after release | **HOLD** | Mind #171 / Dispatch |
| Merchant paid order → realized net | No settled sale evidence | Independent merchant statement with refunds and fees | **NOT COMPUTABLE** | Commerce #820 |

No production writes, subscriber imports, mail, test messages, WordPress settings, affiliate activation, spending or Grok posts are authorized or performed in R281.
