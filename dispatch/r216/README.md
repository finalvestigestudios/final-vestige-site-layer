# Dispatch R216 — surgical copy-consent fixes (REVIEW ONLY, NO WORDPRESS WRITE)

**Scope:** source-exact, offline proposed copy corrections for LIVE WordPress page 523 `/dispatch/` and page 1579 `/focus/`. Read from authenticated WordPress API on **2026-11-08**. Two tiny replacement strings, no post/template/plugin/CSS edits, no new list, no altered form, no URL/UTM change.

## Verified problem → proposed remediation
- **Dispatch** currently describes investigations/archive finds and the 52-page Fieldbook, but **omits the optional affiliate-commission expectation immediately beside its Subscribe control**, unlike Focus. Proposed replacement puts “occasional clearly disclosed recommendations ... may earn ... a commission” in the prominent paragraph before the actual Jetpack Subscribe block. That is a consent-transparency improvement, not retroactive proof of subscriber opt-in.
- **Focus** currently tells a person whose in-app browser cannot open a PDF to “sign up again.” That is a duplicate-intent risk, not evidence of duplicate confirmed leads. Proposed replacement directs them back to original download/email link instead of re-submitting the subscription form.
- Both changes are mere **review candidates**. Claude/Focus owns actual page production; founder authorizes all live edits.

## Technical contract
`consent_copy_contract.cjs` accepts only the exact page ID, slug, authenticated modified timestamp and exactly one original Gutenberg source anchor. It refuses stale versions, missing/duplicate anchors and already applied strings. The output is an in-memory transformed string; no WordPress writes, no network access. Verified on the **actual WordPress Gutenberg raw content** during this sprint, including strict reversible equivalence, unchanged Subscribe block, anchor and link counts. Local `node --test` fixture tests are separate and cannot claim live signup delivery.

## Release blockers (no sending)
Current Jetpack settings at **2026-11-08 19:36 UTC**: newsletter ON, auto-send new posts OFF, email format FULL, 52-page Fieldbook URL configured in welcome, sender Final Vestige Studios, reply-to no-reply. Counters total=3/confirmed=3/unconfirmed=2 **nonadditive**; exact eligible email recipients unknown; 5 recorded latest sends were opted out. A 2026-10-25 confirmation message in the connected mailbox does not prove final welcome receipt. Actual provider-filtered eligible recipients and welcome delivery need authenticated evidence.

Issue 03 Zen12 and 05 Total Focus remain **HOLD_MERCHANT**: named FV Inspire3 approval, specific email marketing permission, issued earning URLs, approved published pre-sell guides, actual checkout/refund/settlement terms not established. Zen12 12 levels/48 recordings is merchant copy; the 12 minutes = one hour benefit is an unverified merchant claim. General commercial FTC rules require truth in header/subject, valid publisher physical postal address and functional unsubscribe (not Automattic's address) in commercial email. A static source specimen is NOT Jetpack received-message proof.

**Campaign status:** #175 original six manuscripts untouched; #201 readiness unchanged; four editorial/two commercial preserved; all six HOLD_UNSENT; no actual paid orders, 7/30-day qualified-human sessions, settlement/refunds or net/1000 verified.

## QA acceptance request (owner: Claude / Focus)
Review proposed language, obtain founder permission for the two page changes, independently re-fetch source to verify unchanged timestamps/anchors, visually check desktop/390px/mobile accessibility and copy at the form; perform no new subscriber signups. Re-run exact source evaluator. Actual campaign delivery tests, merchant approval and revenue instrumentation belong to separate gates.

References: GitHub Issue #174, Focus #129, Mind #171, conversion #820; FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; WordPress native preview governance https://wordpress.com/support/newsletter/email-appearance/ ; merchant https://zen12.com/hnp .
