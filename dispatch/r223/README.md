# Dispatch R223 — six source-bound Gutenberg post-body specimens (UNSENT)

**REVIEW ONLY: HOLD_UNSENT for six, additional HOLD_MERCHANT for 03/05.** This package is NOT a newsletter launch, an import of subscribers, a WordPress draft, or a verified Jetpack email. Do not paste these into production or schedule/send any email.

## Source / conflict safety
Source is latest staged Dispatch draft PR #1670 at exact SHA `11f77e2998af06b7450bf67ca144fdc481455606`, not the original October 30 manuscript SHA. Original six-copy PR #175 and review gate #201 remain intact; R222 commercial alternatives are not substituted. All new files are isolated under `dispatch/r223/`. Frozen homepage PR #49 and unrelated engineering/social work remain untouched. See GitHub Issues #174 (Dispatch), #171 (Mind), #129 (Focus) and #820 (conversion).

**New functional deliverable:** six Gutenberg-compatible paragraph/list **post-body SOURCE specimens**, plus six plaintext companions. They are derived from the current six manuscripts, preserving substantive original copy and citations; source hashes and subject/preheader/CTA mapping are in `SOURCE_QA.json`. Each contains prominent no-publish/no-send flags. The subject is captured as the proposed WordPress **post title**, since Jetpack uses post title for the email subject. The intended preheader is deliberately a **visible opening deck**, not a claim that actual inbox preview metadata works. WordPress adds its own surrounding email layout: offline code cannot reproduce the recipient's actual MIME, subject presentation, legal footer, or client rendering.

In the generated specimens, seller URLs appearing as source citations are *non-clickable text references*; no merchant earning link is active. Editorial citations may remain linked. Both commercial guide URLs are still unresolvable placeholder tokens. These examples are NOT WordPress-sanitizer tested, although they use basic Gutenberg paragraph/list comments and no active scripts, forms or custom CSS.

## Genuine read-only WordPress observation — November 9, 2026 02:30 UTC
Jetpack Newsletter enabled; site_can_send=true but **automatic new-post emails OFF**. Sender name Final Vestige Studios; reply_to=no-reply; email_content_format=full; include featured image in email=true; post date included; newsletter categories OFF. The five recent WordPress posts have send flag false; no delivered newsletter verified. Welcome template still links the 52-page Focus Fieldbook; **actual received welcome unknown**. Provider totals: total subscribers 3, confirmed 3, unconfirmed requests 2. Separate followers: WP.com 3, email-only 0. These counts are nonadditive and do not identify actual eligible recipients; no subscriber email addresses were read or disclosed.

Live /dispatch/ page ID 523 still describes the investigations and Fieldbook, but has no near-form commercial expectation disclosure. /focus/ ID 1579 already mentions occasional commissions but uses client-side subscription-status presentation: a browser's success state cannot authenticate provider confirmation. R216/R218 have separately proposed corrections; this PR does not modify them. Editorial Standards page 17 requires original records, inference boundaries, and commercial independence.

## Exact buyer / conversion decisions
Zen12 Premium remains **a provisional future offer**, not a verified currently usable earning opportunity. Its official seller page advertises twelve progressive levels, four listening styles and a Premium package described as 48 MP3s. The 'twelve minutes equals one hour' and other efficacy statements are **vendor representations**, not product-specific independent proof. Total Focus's public page lists a 33-minute, 47-MB recording and displayed $24.44/$29.95 on fresh direct retrieval while an older indexed result gave $17.95/$22.95; neither is a verified checkout. Its FAQ qualifies the fourteen-day guarantee with a maximum of five sessions refunded annually. All prices, bundles, tax, refunds, approved creatives, affiliate acceptance, emailed promotions rights and account-issued earning URLs require partner evidence before use.

Mind #171 owns named merchant approval, explicit email channel permission, current terms, verified account links and **published, vetted** independent buyer guides. Dispatch owns newsletter copy, consent and received-email QA. Grok/Praxxis own social creation and TASK-008; Claude owns production analytics/page changes; the founder alone approves sending and expenditures.

## Non-sending reviewer / testing procedure
1. Compare each Gutenberg specimen and TXT with its current Markdown source. Re-run source identity checks if manuscript SHA changes.
2. Verify one editorial CTA and sources; never activate commercial issue 03 or 05 guide CTA until the *actual* guide is live, merchant EMAIL rights are verified and creative/claims/terms are approved.
3. Verify subscriber eligibility and deduplicated `confirmed_signup` through provider-authoritative record/status transitions. Do not infer subscription from a Fieldbook download, browser query parameter, comment notification or follower count. Do not store subscriber addresses in analytics.
4. Only after a **separate, specific founder approval** consider a protected WordPress-native preview: WordPress documentation states the Preview email control appears when the per-post subscriber-send toggle is ON. This is a potentially hazardous editor state; do not use it, publish, schedule, save live drafts or send a test email without explicit permission.
5. Inspect an actually delivered, separately authorized email: correct sender, visible publisher postal address (NOT vendor/Automattic address), functioning unsubscribe, HTML and plaintext legibility. Preserve unsubscribe for at least 30 days and process opt-outs within 10 business days per FTC.
6. The founder approves each final creative, recipients and exact schedule as a distinct last step. Even passing tests never grants sending rights.

**Measurement acceptance:** one privacy-safe Grok `asset_id` / `utm_source` / `utm_campaign` / `utm_content` → unique qualified-human session → relevant offer CTA → provider-confirmed deduplicated opt-in (if used) → actual approved guide → independently reported settled paid transaction or partner-paid commission → refunds/fees → realized net revenue per 1,000 qualified-human sessions. Seven- and 30-day cohorts only with observed data. Current KPI **NOT COMPUTABLE**; visits, clicks, signups and merchant checkouts must never be labeled paid orders.

## Source QA and limitations
Sixty-eight source-derived checks passed in isolated JavaScript V8 as six manuscripts were converted; `SOURCE_QA.json` records each manuscript blob. **Native Python/Node execution, genuine Gutenberg/Jetpack rendering, browser WCAG checks, actual delivery/unsubscribe, merchant checkout, affiliate approval and independent paid sales were NOT tested or verified.** The hold banners and legal placeholders intentionally make specimens nonpublishing.

### Source-of-truth references
WordPress email/post subject: https://wordpress.com/support/newsletter/send-newsletter-emails/
WordPress preview toggle: https://wordpress.com/support/newsletter/email-appearance/
WordPress subscriber caveats (reviewed 2026-11-04): https://wordpress.com/support/subscribers/
FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
FTC earnings disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
Exact merchant claims: https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq

**OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER:** Zen12 → Issue 03 / guide → Missing merchant EMAIL rights and published guide → Prepared source-only Gutenberg specimen, no live link → source PASS / merchant HOLD → Mind. Focus → subscriber → Client display and provider confirmation differ → Provider-deduped `confirmed_signup` proposed → real eligibility UNKNOWN → Claude/Focus. Subscriber → welcome → No authenticated received message → Provider/inbox evidence required → NOT VERIFIED → Dispatch/QA. Dispatch → recipient → No actual legal footer/Jetpack email → authorized received-message QA after founder approval → NOT TESTED → Dispatch/QA. Subscriber → paying customer → No independent paid orders/eligible-session denominator → 7/30-day reconciliation → KPI NOT COMPUTABLE → Commerce/Praxxis.
