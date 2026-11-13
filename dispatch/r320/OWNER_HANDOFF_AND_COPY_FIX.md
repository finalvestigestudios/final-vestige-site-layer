# R320 · Conversion blocker and direct owner handoff (review only)
## OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
| Offer / step | Blocker | Proposed isolated change or evidence test | Result as of 2026-11-13 03:38 UTC | Owner |
|---|---|---|---|---|
| Free Fieldbook → trustworthy signup UX | Inline \`?subscribe=anything\` reveals gift although URL is user-controlled | In a separate Claude-owned page draft, remove broad query-driven UI “success”; base gift reveal solely on a **validated** actual Jetpack result; preserve download-by-welcome fallback. QA valid/invalid/error URLs at 320/360/390px and without JS. | **FAIL** for trusted UI state; reproduced from live source offline; no live action | Claude / Focus #129 |
| Focus → confirmed Dispatch lead | PDF visibility, CSS \`is-subscriber\` and query params are not new opt-in | Join private Jetpack unconfirmed→active transition, unique confirmation event, current email-eligibility/consent; R319 verifier is a model only | **UNKNOWN** in production | Claude / Focus #129 |
| Fieldbook → complete welcome | Configured 52-page URL, but no received welcome; remote PDF fetch cache miss | With separate founder authorization, obtain a genuine message + PDF download proof from a consenting owner-controlled account, check PDF pages/content and redacted screenshot | **UNKNOWN**, metadata media #1737 599,946 B, not reader delivery | Dispatch / Founder |
| Dispatch → honest subscription promise | Live copy says updates when published; new-post default OFF and recent five posts opted out | Keep fail-closed OFF; founder decide intentional cadence language for future sends or clarify current promise without sending | **COPY REVIEW NEEDED**, not a request to enable auto-send | Founder / Dispatch |
| Zen12 Premium → vetted guide → paid order | No FV account acceptance, EMAIL rights, issued earning URL or live approved guide | Mind owns actual specific tier, account proof, live guide and merchant terms; no direct earning anchor in email | **HOLD_MERCHANT** | Mind / Commerce #171 |
| Total Focus → vetted guide → paid order | Same authorization; seller performance assertions unverifiable | Review named SKU (33 min, 47 MB), verified partner terms, seller sources, guide before offer | **HOLD_MERCHANT** | Mind / Commerce #171 |
| Grok asset → human session → paid transaction | 3/3/2 subscriber categories overlap; no settled orders or attributable human denominator | Use existing Claude measurement, private consent joins, partner-settled transaction and refunds/fees; zero new tracking scripts | **NOT COMPUTABLE**, no fabricated 7/30d cohorts | Grok / Praxxis / Claude / Commerce #820 |
| Dispatch → received email | No valid FV physical postal footer, working rendered unsubscribe, Inbox preheader or native preview | Explicitly authorized native **Preview email** with send toggle OFF; founder legal address, functional optout and primary-purpose review; do not send test | **HOLD_UNSENT** | Founder / Dispatch #174 |

### Copy repair, not a live edit
**Current /focus/ FAQ:** “If that happens, use the menu to open this page in Safari or Chrome and sign up again. The welcome email also carries the link.”

**Proposed:** “If a social app won't open the PDF, use its menu to open the download link in Safari or Chrome. Already subscribed? You don't need to submit your address again. Once your subscription is confirmed, the welcome email provides the same link.”

**Release note:** This text is a founder-review suggestion only. Does not claim the download is confirmed accessible, that signups have arrived, or that Jetpack's redirect semantics are known. Do not change the UI behavior or FAQ before owner review and approved testing.

### Model boundaries
A browser UI acknowledgment can justify showing a free gift, but **never** count as email subscription. The only proposed \`confirmed_signup\` source is authenticated provider evidence, deduplicated by opaque event and consent scope. The existing list must not be imported, duplicated, or exported. The internal UI specimen is neither a working privacy-compliance control nor a commercial campaign.

Sources: https://finalvestige.com/focus/ ; https://wordpress.com/support/subscribers/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://zen12.com/ ; https://hypnosislive.com/mental-skills/total-focus ; https://affiliates.inspire3.com/ .
