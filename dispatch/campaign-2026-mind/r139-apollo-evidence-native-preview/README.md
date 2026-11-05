# Dispatch R139 · Apollo 1 editorial proof + Jetpack-native non-sending handoff

**Status: DRAFT / HOLD_UNSENT.** Source-controlled review only; proposed child of [R138 draft PR #1098](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1098). Master campaign [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), safety [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), coordinating [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind offers [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Frozen homepage #49 unaffected.

## Material new work (not a new campaign, not a send)

1. `issue04-optional.md` is original, evidence-checked **historical** alternative for the existing Apollo 1 editorial position. Specific credible story + free investigation-reading exercise + one first-party action to the **verified published** Apollo post ID 434 at `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`. No unverified 14-second duration, no invented eyewitness story, no unsupported exact electrical ignition site. NASA review board was unable to identify the precise source, yet identified preventable conditions. This alternative is **not approved to replace** the PR #175 manuscript.
2. `issue04-offline-email-review.html` and `issue04-offline-plain.txt` preserve substantive email content, primary CTA, separately labeled NASA source URLs, inclusive typography, and prominent hard-stop publisher-address/unsubscribe placeholders. They are **offline mockups**; they are not Jetpack email preview evidence, email-client rendering, a received email, or proof of usable footer. No remotely hosted images, trackers, forms, or scripts.
3. `source-and-gates.json` is a machine-readable claims/URL/hold ledger with 4 editorial + 2 reserved-commercial issue mapping and all-false release attestations. It preserves native WordPress counters as **overlapping categories**; no subscribers, sender addresses or contact information.
4. `guard-r139.cjs` and `test-r139.cjs` check source/claim honesty, campaign proportion, the single first-party action, documentation links, explicit commercial holds, unsafe markup and fake net-revenue flags. They do **not** send, schedule, post, modify subscribers or grant release.

## Important verified product behavior: native Jetpack is not a standalone custom-email scheduler

According to current [Jetpack Newsletter documentation](https://jetpack.com/support/newsletter/), subscriber newsletters are generated when **new POSTS** are published, not when a PAGE is published or an existing post edited. The editor's **per-post** newsletter control governs sending; preview is distinct from a real test email. [Customize the Newsletter](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/) describes a **350-character** auto-excerpt and user-supplied excerpts in one configuration; [WordPress.com newsletter settings](https://wordpress.com/support/newsletter-settings/) describe a **55-word** default in another. The actual rendered result depends on site configuration/editor, so both numbers are **models**, not evidence of a genuine Final Vestige email.

Crucially, the native excerpt includes Jetpack's **Read More** button to the *new newsletter post*, not the separate historical article URL in Issue 04's manuscript. Therefore *CTA truly absent from the excerpt text* is not equivalent to *no link anywhere in a real email*; it is a **different, extra-click journey**. A founder-approved **per-post full-text preview** is the most direct way to evaluate whether the single investigation CTA and source context can survive. Do not change global default `excerpt` or activate per-post sends without separate founder approval.

Native WordPress read-only evidence on 2026-11-05 **14:30 UTC**: site ID 256784396, `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, send-capable, last five posts `never_sent_opted_out`; welcome with the promised 52-page Fieldbook configured. Counters `total=3, confirmed=3, unconfirmed=2, imported_last_24h=1` **are nonadditive**, and **do not establish actual recipients, consent, or provenance of imported activity**. `subscribe_modal_enabled=false` is a sitewide setting; it does not establish if the embedded subscribe block works in a signed-out visitor DOM. Page /dispatch/ ID 523 and /focus/ ID 1579 were read only, as was Editorial Standards.

**Critical live Focus follow-up:** The currently published /focus/ page's original JS still includes the equivalent of `if(q){if(bad.indexOf(q)<0){show();}}`. Arbitrary non-denied `?subscribe=...` values can therefore show the download-success panel. The proposed fix exists in prior unpublished draft [#1079](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1079); do **not** create another competing production patch here. **Owner: Claude/Site QA; status: observed in WordPress editor content, not signed-out real DOM reverified in this run.** This is a consent/truthful-status risk, *not* evidence of new confirmed subscribers. The source-controlled R139 copy does not depend on this behavior.

## Six-slot operational handoff without subscriber contact

| Existing slot | Native first-party intended destination | Status / downstream click truth |
|---|---|---|
| 01 perception editorial | Published Puységur archive URL in #175 | No native email preview; do not assume unique recipients |
| 02 Puységur editorial | Same Puységur archive URL | No native preview |
| 03 Zen12 Premium | Vetted Mind guide URL NOT LIVE/APPROVED | HOLD_MERCHANT; require named acceptance, explicit email marketing rights, exact partner link/claims, guide/terms, customer consent boundary |
| 04 Apollo 1 editorial | WordPress post 434, `/2026/08/20/the-hatch-opened-inward-apollo-1/` | Destination verified published; alternative copy still not approved; native email CTA not previewed |
| 05 Hypnosis Live **Total Focus** | Exact SKU vetted guide URL NOT LIVE/APPROVED | HOLD_MERCHANT; not separate *Hypnotize Yourself*. Seller lists 33 mins/47 MB; display price differs by session and is not approved for buyer promise |
| 06 Focus evidence log | Published `/focus/` | Page exists; native signup and delivery not proven |

The primary *business* target is conversion, not publication volume. Honor actual sequence: **identified Grok asset (when supplied) → qualified first-party session → relevant landing/page CTA → native confirmed subscription transition (if applicable) → independently verified settled merchant order/commission or owned product sale → refunds/fees → realized net revenue**. A WordPress impression or signup click is not a sale. Use `utm_medium=organic_social`, `utm_content=<actual unique asset_id>` on Grok links **only when Grok/Praxxis and Claude validate destination and consent**. For a future approved email, `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_04_apollo` is a **proposed** non-PII tag; it has not been added to any live URL. No invented asset IDs or tracking scripts.

## Prioritized conversion-first handoff: offer → step → blocker → change → test → owner

| Offer → funnel step | Blocking evidence | Concrete experiment/change | Pass/FAIL evidence status | Owner |
|---|---|---|---|---|
| Fieldbook → confirmed lead | Published Focus query status can show success in unconfirmed states; native consent unverified | Merge only after independent review of existing #1079 fix and signed-out flow; reconcile native Subscribed status privately | **LIVE SCRIPT OBSERVED / REAL BROWSER UNKNOWN** | Claude + Site QA |
| Promise → Fieldbook receipt | Welcome configuration not evidence of actual inbox; PDF asset registered but not confirmed retrieved/52-page open | Authorized post-confirmation received welcome + PDF download inspection; no test send without approval | **NOT VERIFIED** | Dispatch + Claude |
| Dispatch newsletter → actual reader CTA | Excerpt mode changes direct CTA to Read More; real email appearance/footers unknown | On a **separately approved existing unpublished POST**, use native Preview email; compare actual excerpt and per-post full-text if available; do not publish or test-send | **SUPPORTED BY DOCUMENTATION, NOT VERIFIED LIVE** | Dispatch + Site QA |
| Zen12 / Total Focus → verified buyer | Named acceptance, email rights, right SKU, live guide and checkout/returns unknown | Mind Studio source-of-truth contract/eligibility audit before future email link | **HOLD_MERCHANT** | Mind Studio #171 |
| Legal promotional email → authorized reader | Final Vestige postal address/operational opt-out unknown | Privately attest publisher address and check native footer; only later, with separate approval, real received email | **NOT VERIFIED** | Dispatch + site owner |
| Grok/session → realized net revenue | No reconciled qualified-human denominator or paid transactions | 7/30-day cohort measurement with orders, fees/refunds, suppress duplicate paid events | **NOT COMPUTABLE** (not zero) | Praxxis + Claude #820 |

## Immediate specific non-sending approval sequence (future only)

1. Founder/editor separately approves an **existing WordPress unpublished post** to be used as preview surface; do not create one automatically. Keep `Send this post to subscribers` OFF by default and never publish during QA.
2. Privately reconcile actual native email-subscription status and unexpected `imported_last_24h=1` flag. Confirm WordPress.com-account vs standalone-email confirmation paths; do not export address lists.
3. Open Jetpack **Preview email** in editor only when authorized; record desktop/mobile screenshots, presence of direct or Read More CTA and how excerpt/full text behaves, visible disclosure/legal footer. Offline HTML/Node passing tests alone cannot certify this.
4. Founder separately approves any test email and destination. Until then no send of any kind. A genuine received message would be tested with the existing [R138 non-sending receipt harness](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1098); no new duplicate harness is needed.
5. Only after named affiliate acceptance, same-SKU guide publication and founder campaign go-ahead can slots 03/05 be reconsidered. **All six remain HOLD_UNSENT** until every relevant gate passes.

### Primary evidence

- NASA [Apollo 1 / AS-204](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) and [Apollo 204 Review Board report, HTML](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — board findings and ignition uncertainty.
- WordPress [Jetpack Newsletter](https://jetpack.com/support/newsletter/), [newsletter customization/excerpts](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/), and [WordPress.com native settings](https://wordpress.com/support/newsletter-settings/).
- FTC [CAN-SPAM compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) and [Endorsement FAQs](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Address + functional opt-out remain unresolved; source link in HTML is not proof.
- Exact sellers [Zen12 Premium](https://zen12.com/hnp), [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus): merchant representations not independent performance evidence. Named Final Vestige partner approval remains unverified.

**Original campaign ratio 4:2 preserved. No WordPress, checkout, analytics, affiliate, subscriber, social or publication writes. No emails sent, including test emails.**
