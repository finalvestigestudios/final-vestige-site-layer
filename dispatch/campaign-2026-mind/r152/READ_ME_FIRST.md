# Dispatch R152 — Source-to-subscriber attribution bridge (UNSENT / NON-PRODUCTION)
**2026-11-05 PT | Master #175 | Prior safety #201 | Stacked R151 #1190 | Dispatch #174 | Focus #129 | Mind #171 | Revenue #820**
**No scripts deployed, tracking pixels added, WordPress content/settings changed, emails scheduled or sent, subscribers read/exported, affiliate links published, or social content posted.**

## Decision: no verified subscriber-to-customer path exists yet
A Grok URL with UTM query parameters may prove **which link was prepared**, not that a human visited, that someone subscribed, or that someone purchased. Existing Jetpack read APIs surface aggregates, **not a trusted before→after native confirmation transition with consent and source linkage**. There is no lawful or reliable method to infer a particular person from source tags alone. This module intentionally produces NULL for actual qualified sessions, newly confirmed leads, settled orders and net revenue.

### What this sprint independently re-read
- **Live Jetpack newsletter status** as-of **2026-11-06T03:29:48Z**: total 3, confirmed 3, unconfirmed 2, suppressed 0, paid 0, imported last 24h 0. Five recent WordPress posts are `never_sent_opted_out`; site_can_send=true is a capability, **not a campaign send**.
- **Live settings** as-of **2026-11-06T03:29:50Z**: newsletter enabled; new-post auto email **OFF**; format **full**; sender **Final Vestige Studios**; reply-to **no-reply**; 52-page Fieldbook welcome configured, receipt unverified.
- **Separate followers API** returned WordPress.com=3, legacy email=0, comment=0, partial=false. They cannot be added to `total=3`; `email=0` does **not** prove zero deliverable addresses. Provider `Email subscription` status is required.
- Published **/dispatch/** page #523 last modified Oct 29 has native Jetpack Subscribe block; an authenticated rendered API representation earlier showed an apparent self-link. **Guest-browser functional result remains unknown** (stored block is not a real browser submission).
- Published **/focus/** page #1579 last modified Nov 5 retains native Subscribe block. Its inline `fvf-gift-v2` JavaScript reveals the free-book success panel for **any nonempty `subscribe` query string except five known negatives**, or when CSS class `is-subscriber` appears. That is not reliable proof of double opt-in or email eligibility; do not instrument `confirmed_signup` from panel display or URL parameter.
- WordPress Editorial Standards page #17 requires source provenance, visible uncertainty, human validation of AI-assisted claims, and separation of financial relationships from findings.
- Master #175 original **six Python tests passed natively** against original 8 files byte-identical to exact immutable PR #175 SHA (Git blob SHA confirmed). All six manuscripts remain untouched. R151 contains separate native eligibility count safeguards and cannot be replaced by these URL-only checks.

### Exact measurement convention
**Grok-owned asset link (proposal, not an actual Grok post):** `https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=perception_pilot_2026_11&utm_content=yt_change_001`
**Dispatch email link (proposal, not a delivered CTA):** `https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_02`

Only four standard UTM fields are permitted. Destination must be on **finalvestige.com**, HTTPS, with no credentials, third-party host, token fragments, email addresses, subscriber IDs, extra user-identifying query parameters, tracking redirects or unsafe paths. Restrict `utm_source` and `utm_medium` by channel and require one immutable Grok `asset_id` per actual published creative. The example `yt_change_001` is **synthetic only**; Grok remains owner of actual IDs/links and posting. Real URLs and platform-specific bio-link constraints must be checked with Grok TASK-008 before use.

**Source vs consent separation:** Creator visit and email click are separate attribution contexts. A later email click legitimately has `utm_source=dispatch`; do not overwrite or merge with an earlier YouTube/TikTok source without an explicitly authorized, proven first-party correlation. Never collect email address or raw Jetpack subscriber tokens in UTM, source logs or GitHub. If the existing WordPress/analytics architecture cannot retain native confirmation provenance, report `confirmed_signup=UNOBSERVABLE` and retain only aggregate visits/clicks, with clear limits. Do not add new analytics scripts or paid tools.

### Six-issue email CTA routing decision (four editorial / two reserved commercial)
| Issue | Identity | Proposed email source | Current canonical first-party CTA | Gate |
|---|---|---|---|---|
| 01 | Editorial/perception | `issue_01` | Puységur (duplicates #02); optional direct change-blindness correction exists in #1126 | HOLD_UNSENT |
| 02 | Editorial/history | `issue_02` | Existing published Puységur files | HOLD_UNSENT |
| 03 | Reserved commercial Zen12 Premium | `issue_03` | Independent buyer guide **NOT LIVE/APPROVED** | HOLD_UNSENT + HOLD_MERCHANT |
| 04 | Editorial/Apollo | `issue_04` | Existing Apollo investigation; subject time precision must have primary source | HOLD_UNSENT |
| 05 | Reserved commercial Hypnosis Live Total Focus | `issue_05` | Independent buyer guide **NOT LIVE/APPROVED** | HOLD_UNSENT + HOLD_MERCHANT |
| 06 | Editorial/Fieldbook | `issue_06` | Existing /focus/ signup creates duplicate subscriber friction; direct PDF alternate in #1126 | HOLD_UNSENT |

No UTM link is automatically inserted into existing mail, and no CTA target is silently replaced. Merchant-product guides belong to Mind #171, not Dispatch. Existing author-approved replacements are **not** presumed.

### Revenue priority and correct cohort math
**Net revenue per 1,000 qualified human sessions** = 1000 × (independently reported, settled, attributable gross proceeds − actual refunds − payment/partner fees) / verified qualified unique-human sessions in a defined 7- or 30-day cohort. If any required source, settlement proof or denominator is absent, the KPI is **NULL / NOT COMPUTABLE**. An outbound click, a checkout start, a WordPress reported follower, a PDF download, a Jetpack post notification, or a paid merchant website **cannot** stand in for an actual purchase.

## Offer → Funnel → Blocker → Next change/evidence → Owner
1. **Fieldbook → confirmed lead:** Email eligibility and consent source unknown. **Read-only** WP Subscribers view: inspect aggregate `Email subscription` status, obtain lawful before/after proof without moving addresses; **FAIL / UNKNOWN**, Dispatch + Claude/Site QA.
2. **Fieldbook → PDF:** Welcome configured but no actual receipt. Search existing authorized inbound sample, confirm PDF URL read safely; **UNKNOWN**, Dispatch.
3. **Dispatch → guest visitor:** Page source contains native block but real signed-out guest form remains unproven; test browser without submitting; **UNKNOWN**, Claude/Site QA. The Focus success-panel parameter is **NOT** confirmation.
4. **Issue → inbox:** Full-content mode, hard-stop postal/unsubscribe placeholders, no actual received campaign; use native WP **Preview email only**, not *Send test email*; **HOLD**, Dispatch/Claude.
5. **Zen12 / Total Focus → guide → customer:** Named FV acceptance, specifically email-channel rights, approved earning links, exact-product current checkout/refund terms, and live buyer guides remain missing. Official merchant claims are seller statements, not independently validated efficacy. **HOLD_MERCHANT**, Mind #171.
6. **Purchases → settled revenue:** No merchant-reported FV orders or qualified-human source data. **NULL**, Commerce/Praxxis via #820.

### CAN-SPAM & source grounding
FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — commercial primary-purpose determination, honest header/subject, accurate promotional nature, **valid FV physical postal address** (Automattic's confirmation footer does not qualify), and functioning unsubscribe with processing. Both a compliant actual Jetpack renderer and independently verified recipient rights remain mandatory. A no-reply address is **not** by itself a functioning opt-out.
WordPress https://wordpress.com/support/subscribers/ and https://jetpack.com/support/newsletter/ — native status semantics, full-vs-excerpt rendering, and preview vs **actual** test-send distinction.
Official exact products: https://zen12.com/?no-popup=1 (seller: 12 levels, 48 MP3) and https://hypnosislive.com/mental-skills/total-focus (seller: 33 min, 47 MB). No prices or medical/cognitive promises are established for FV's commercial email by those sales pages. Affiliate permission cannot be inferred from public https://affiliates.inspire3.com/ .
**Commercial approval states: FALSE. All six remain HOLD_UNSENT.**
