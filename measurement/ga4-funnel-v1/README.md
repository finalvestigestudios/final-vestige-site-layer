# Final Vestige: Conversion Signals v1 — STAGING / NO DEPLOY

Linked governance: [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).
Owner intent: measure **real business conversions**, never equate traffic, click, email form, or redirect with revenue.

## Source and deployment boundary
- The browser script \`fv-conversion-events.js\` is a **candidate**, not wired into the PHP production entrypoint, theme, Site Kit, WPCode or WordPress.
- No new Google tag, GA4 property, cookies, SDK, outbound endpoint, visitor IDs, storage, or payment capture. It calls \`gtag('event', name, params)\` only if the **already approved** Google tag exists.
- It must **not** be activated until Site Kit's actual GA4/GTM/consent state and duplicate-event behavior are confirmed on production-like staging. A GTM-only configuration without the global \`gtag\` interface will silently no-op.
- Event parameters use only fixed enums \`fv_page_group\` and \`fv_offer\`. The source does not transmit emails, affiliate tracking IDs, full paths, link URLs, query parameters, user IDs, or referrers.
- One delegated \`click\` and one delegated \`submit\` handler, single-inclusion guard, no DOM modifications, no \`preventDefault\`, no conversion pixel of our own.

## Event contract and truth rules

| Event | Trigger | Truth boundary |
|---|---|---|
| \`fv_focus_entry\` | Internal click to /focus/ | Visit intent, not signup |
| \`fv_article_to_resource\` | Article click to /focus/ | Navigational action, not signup |
| \`fv_subscribe_submit_attempt\` | Jetpack subscribe form submit on /focus/ | Attempt, NEVER confirmed subscriber |
| \`fv_fieldbook_pdf_click\` | Click known Focus PDF | Click, not successful download |
| \`fv_affiliate_outbound\` | AWIN merchant referral clicked | Click, NEVER order/commission |
| \`fv_checkout_handoff\` | Payhip link clicked | Outbound navigation, NEVER checkout started or purchase |

GA4's standard UTM parameters are the canonical campaign attribution. Do **not** emit a redundant \`campaign_landing\` or rewrite internal links. \`purchase\`, \`generate_lead\`, and \`confirmed_signup\` must NOT be inferred from these events.

Currently allowlisted: AWIN short links, Payhip links, Final Vestige /focus/ and the exact Fieldbook PDF. Unknown AWIN offers are labelled \`other_awin\`. No partner sale is claimed.

## Test and release plan

1. Run \`node --test measurement/ga4-funnel-v1/test-funnel.cjs\` on the exact candidate SHA. The draft logic has also been checked in an isolated fake-DOM harness.
2. Read current WPCode, Site Kit, Burst, Jetpack and GA4 properties and avoid duplicate tags, duplicate enhanced-measurement outbound \`click\` events and redundant form trackers.
3. Privacy/consent and CA/EU jurisdiction checks; validate permitted events under existing Google-tag consent rules. No IP/email/visitor-level data appended.
4. Staging browser: 360, 390, 768, 1440px; keyboard/touch; JS off; CWV and network-event inspection. Confirm clicking links does not delay merchant handoffs or download delivery.
5. GA4 DebugView/Realtime: inspect per-event dispatch once and fixed enums; verify source/medium/campaign from standard Grok UTMs; check no event if no Google tag.
6. Test one authorized real Jetpack double-opt-in separately, without fake subscribers; compare confirmed count in Jetpack admin. Never infer confirmed signup from submit.
7. Get Awin and Payhip **authenticated merchant reports** for conversion, refunds, fees and paid commissions. No simulated purchases or invented revenue.
8. QD review exact release SHA + independent approval + sanctioned deployment; afterward confirm live event arrivals/rollback. This PR is not itself permission to deploy.

## Grok UTM convention (organic only)

\`utm_source={youtube|tiktok|instagram|facebook}\`
\`utm_medium=organic_social\`
\`utm_campaign={mind|history|preparedness}_pilot_2026_11\`
\`utm_content={platform_asset_id}\`

Use identifiers, not titles, email addresses, personal information or unverified ROI claims. Do not change affiliate link parameters or attach UTMs to internal site links.

## Weekly scorecard (verified / unknown kept separate)
- Date range, inbound campaign, qualified human sessions (definition and evidence), landing/topic, engagement, unique CTA clicks, Fieldbook submission attempts, **confirmed Jetpack subscribers**, Awin outbound, Payhip handoff, partner-verified gross orders, net settled commissions, refunds/fees, product hours, evidence/confidence and anomalies.
- **Revenue per 1,000 qualified sessions** = verified net revenue / qualified human sessions * 1000, only when both numerator and denominator are verified.
- As of Nov 10, 2026, click and sale attribution has not been validated. Jetpack view spikes show views-per-visitor anomalies; a page view is not a human session.

## Rollback
Because this source is not loaded, no production rollback is needed now. After an approved future release, remove only its script registration and verify other Site Kit/Jetpack functions remain unchanged.
