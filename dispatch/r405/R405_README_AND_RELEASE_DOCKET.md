# Dispatch R405 | Conversion proof without fabricated sales — UNSENT / UNMERGED

**2026-11-16 18:34 UTC authenticated read-only evidence.** Owner [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); merchant [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); welcome/consent [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); aggregate revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter #818. Founder's canonical six-issue [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) exact current head d57ccdba3aee8f065e143e101c2945f4f3d01647; original per-edition controls [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6; parent [R404 PR #2765](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2765) 85f8fcefd7a15d84bceb4e739d196c02d8cb9ef6. This R405 tree contains new proof reduction/verification; it does **not** replace the six manuscript bodies, modify live pages, activate merchant links, merge or send.

## Why this lane matters commercially

A click is not a sale; a Jetpack subscription request is not a confirmed eligible recipient; a checkout view is not paid commission. Under the founder's priority ordering, a trusted report of **net realized revenue per 1,000 qualified human sessions** is the key decision signal. With **no audited qualified-human denominator** and **no paid merchant settlements**, publishing even "$0" or computing an EPC is misleading: result must be NOT_COMPUTABLE. A merchant's public "60%+" and "EPC $1+" on its affiliate landing page are seller advertising, **not** Final Vestige earnings.

R405 introduces executable \`revenue_proof.py\`, with native \`test_revenue_proof.py\`. It rejects unsourced pageview/click-as-sale substitutions; requires actual declared provenance for audited sessions and paid orders; refuses duplicates, bad cohort dates, mixed currency, incomplete refunds/fees and PII-like identifiers; separates 7/30-day audited cohorts; and **always returns HOLD_UNSENT**. **Important:** source kind/proof reference validation is structural only. It cannot authenticate a forged export or issuer signature, and a passing synthetic test must never be reported as live paid performance. The first real implementation requires human reconciliation of genuine independently issued export/report records by Commerce + Claude, not merely a string that says "merchant_paid_settlement".

### Run the tests, safely

\`PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_revenue_proof\` from dispatch/r405. A deliberately fictional positive control exists only in test code, never in a real campaign report. The no-evidence case returns NOT_COMPUTABLE and null net USD, rather than asserting there were zero sales. The standalone reducer is neither a production analytics tag nor a merchant integration, and makes no network calls.

### One credible subscriber-to-customer path (unscheduled)

**Hypothesis:** A historically curious viewer arriving through a verified Grok Mind-related asset may be willing to try the free 52-page Focus Fieldbook and later evaluate a relevant, *independent* Zen12 review, if they requested Dispatch and really confirmed opt-in. Nothing about using the Fieldbook obliges purchase or contact.

1. Grok owns and QA's the real published platform asset. Pass only the **actual** immutable \`asset_id\` in \`utm_content\` alongside \`utm_source\` (platform), \`utm_medium=organic_social\`, \`utm_campaign=mind_pilot_2026_11\`; no invented asset, no credentials or email IDs. Claude owns session/landing analytics and bot filtering.
2. Reader lands on the existing source-based investigation or /focus/ and voluntarily sees the single existing Jetpack subscribe flow. Do **not** count download, \`?subscribe=\`, \`after_signup\`, a form submit or an email confirmation request as \`confirmed_signup_v1\`. Only independent provider-authenticated subscription confirmation with opt-in eligibility and one-time dedup key can count; keep the key server-side and privacy-safe.
3. The configured welcome includes the 52-page Fieldbook, but no actual receipt has been authenticated. Only with explicit authorization may a controlled end-to-end test verify confirmation, welcome receipt, PDF accessibility and opt-out; no test email was sent in R405.
4. The **original four editorial / two commercial-review-pending mix remains unchanged**. Issue03 has one prospective guide CTA, issue05 another, both dead placeholders until Mind independently verifies offer eligibility, named affiliate EMAIL permission, issued URL, approved buyer guide, exact referred terms, and founder approval. Never activate partner links or insert quote prices based on public sales pages alone.
5. A sale is recognized **only** by an independently issued **paid** order/commission report matched to authorized campaign and real source cohort, minus verified refunds, reversals and fees. Seven- and thirty-day cohorts use actual event records, not fake A/B tests with three dashboard subscribers.

### Current provider-of-record snapshot — 2026-11-16 18:34 UTC

| Read-only source | Exact result | What it cannot prove |
|---|---|---|
| Jetpack newsletter status | subscriptions 3 total, 3 confirmed, 2 unconfirmed, 0 suppressed, 0 paid, 0 imports last 24h; \`site_can_send=true\`, \`send_blockers=[]\` | Not 5 unique people and not 3 independently email-eligible receiving inboxes |
| Jetpack follower stats | 3 total: 3 WordPress.com, 0 direct email, 0 comment; \`partial=false\` | Cannot be added to subscriptions total or infer external-email deliverability |
| Newsletter settings | subscriptions ON; \`email_new_posts_by_default=false\`; full content; \`reply_to=no-reply\`; \`from_name=Final Vestige Studios\` | Does not prove a genuine received commercial email, verified unsubscribe, or FV postal address |
| Jetpack recent posts | Last five shown \`never_sent_opted_out\`; counts null, no dispatch timestamps | Does not prove any Dispatch issue reached an inbox |
| Welcome settings | Contains actual 52-page PDF URL and claims free access | Does not prove delivery or attachment/download usability for a confirmed subscriber |
| Gmail read-only search | One 2026-10-25 subscriber **confirmation request**, no authenticated welcome receipt; no Inspire3/Hypnosis/Zen12 publisher-account acceptance or named EMAIL permission located | Absence in searched mailbox alone cannot establish no other merchant agreements exist |
| /dispatch/, /focus/ | Published signup pages inspected via authenticated WordPress connector; existing Jetpack forms | Does not supply a provider-signed \`confirmed_signup_v1\` event |
| Editorial Standards | Published /editorial-standards/ reviewed Aug 23 2026; calls for primary sources, open uncertainty, financial disclosures | Does not independently clear seller claims |
| Native WordPress "Preview email" | **NOT performed**; no supported non-sending preview access through available connector | Offline R404 HTML/plaintext samples cannot substitute for Jetpack's actual DOM/layout or legal footer |

**Site platform permission is not campaign permission.** A \`site_can_send=true\` diagnostic is a provider switch, not the founder's authority to email.

### Copy and link decision on the original six

| Issue | Editorial / commercial | Actual single primary CTA path | Status and important deficiency |
|---|---|---|---|
| 01 | Editorial | Published Puységur archive | Duplicates 02 destination; optional R399 alt exists but **not adopted** |
| 02 | Editorial | Same Puységur archive | Distinct editorial progression needed; R401 alternative **not adopted** |
| 03 | Commercial candidate (Zen12) | **NONCLICKABLE** approved-guide placeholder | **HOLD_MERCHANT**; seller claims not proven outcomes; no email rights or verified buyer guide |
| 04 | Editorial | Published Apollo 1 investigation | **HOLD_COPY**; "Fourteen seconds" clock ambiguity; R400 sourced optional **not adopted** |
| 05 | Commercial candidate (Hypnosis Live) | **NONCLICKABLE** approved-guide placeholder | **HOLD_MERCHANT**; catalog-vs-Total Focus SKU and dynamic pricing, merchant rights unknown |
| 06 | Editorial | Published /focus/ | Already in configured welcome; useful review utility but limited incremental conversion step |

**Current subjects** are 24, 26, 37, 44, 41, 40 characters respectively; preheaders 80, 68, 75, 65, 60, 61. These are draft values, not inbox-proven: WordPress uses the eventual post title as email subject. As a result, the campaign has no verified preheader implementation. Preserve research links and one primary CTA per issue; remove internal \`[[...]]\` compliance placeholders only **after** source-backed footer sign-off.

### Required independent handoffs in strict conversion priority

| Offer → funnel step | Blocker | Change / next experiment | Acceptance evidence | Owner |
|---|---|---|---|---|
| **One selected real paid Zen12 offer** → guide → verified paid commission | No FV-named partner acceptance/email terms/link/current referred checkout/settlement | Mind obtains issued referral terms and evidence of allowed editorial EMAIL promotion; test exact SKU/checkout and guide without production activation | Authenticated acceptance/permissions and permissioned payout evidence, **HOLD** | Mind #171 / Founder Commerce |
| Existing Focus Fieldbook → confirmed, eligible Dispatch lead | Counts conflict, query-unlock tracking, no actual welcome delivery | Claude proposes provider-source dedup; consent-bound server event; authorized end-to-end confirmation proof | Private provider record, one \`confirmed_signup_v1\` per real confirmation, received welcome and accessible PDF; **HOLD** | Focus #129 / Claude |
| Dispatch → legal email recipient | Publisher postal address, opt-out and actual Jetpack rendering unproven | Founder approves valid FV mailing address; non-sending native editor preview; functional unsubscribe verification via authorized process | Actual preview + address/opt-out evidence and editorial sign-off; **HOLD** | Founder / Dispatch |
| Grok asset → qualified-human session → net paid order | Actual asset cohort and independent merchant settlement missing | Do not add tracking scripts. Align existing analytics spec and real session source with paid transaction reference | Audit human-filtered session export + paid settlement/refund/fee reconciliation; **NOT_COMPUTABLE** | Grok/Praxxis/Claude #820 |

### Official references and release conditions

- Jetpack actual preview vs test email: https://wordpress.com/support/newsletter/email-appearance/ ; WordPress uses post title for subject https://wordpress.com/support/newsletter/send-newsletter-emails/ . Genuine preview requires native editor, which has not been opened.
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — truthful headers/subject, valid *Final Vestige* postal address, prominent opt-out, timely honoring of opt-outs; the **Inspire3 London address is not Final Vestige's**. The fact Jetpack supplies a standard unsubscribe in other emails does not establish the actual generated commercial issue renders and functions correctly.
- FTC endorsement relationships: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — near-CTA disclosure in both HTML and plaintext.
- Merchant original product: https://hypnosislive.com/mental-skills/total-focus (seller-represented 33 minute / 47 MB; highly variable retrieved checkout pricing, ranging from older cached $17.95 to another snapshot $24.44 and other promotional variants; never use a cached price as current referred total). Actual merchant program https://affiliates.inspire3.com/ advertises payout terms generally, **not FV named approval**, nor per-email permission. Exact Zen12 seller page/affiliate creative must be authorized on the account before quote.
- Site https://finalvestige.com/editorial-standards/ ; canonical homepage priority #150, frozen #49 untouched.
- Grok/Praxxis existing TASK-008: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit ; handoff: https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit . **Read-only coordination only; do not touch Grok's task queue.**

### Release verdict

**NO SEND. NO TEST EMAIL. NO CMS WRITE. NO NEW LIST. NO ALTERNATE ISSUE ADOPTION. NO PAID LINK. NO MERGE.** All canonical six \`HOLD_UNSENT\`; 03/05 \`HOLD_MERCHANT\`, 04 \`HOLD_COPY\`. Marketing attribution and revenue remain NOT_COMPUTABLE—not zero. Owner acceptance evidence must be independently sourced before the founder decides final campaign creative/audience/times.

Native local tests (not hosted CI): canonical six test methods **6/6 pass**, and new R405 isolated proof gate **25/25 pass** under Python 3.13.5; local Git SHA hashes of the original eight match PR175 exact current head, and R405 code/tests hashes were matched against GitHub. A valid test fixture is **synthetic**, not merchant data. Genuine Jetpack preview, email client, live checkout, provider consent, actual customer and browser QA: **not performed**.
