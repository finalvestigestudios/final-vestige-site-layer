# Dispatch R392 verified inputs, decisions, and handoffs

**Release: HARD HOLD; independent draft only; Issue 03 alternative NOT ADOPTED.** Original [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), independent [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and stacked [#2693](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2693) unchanged. No homepage/#49 alterations.

## Authenticated WordPress snapshot, 2026-11-16 03:02 UTC
- /dispatch/ WP page 523: PUBLISHED, email investigation/archive promise, Focus invitation.
- /focus/ WP page 1579: PUBLISHED, 52-page fieldbook, signup plus download reveal; latter is NOT confirmed signup.
- Editorial Standards WP page 17: primary sources, document uncertainty, distinguish commercial relationships.
- Newsletter ON, auto-new-post email OFF, FULL content, From Final Vestige Studios, no-reply. Last five publication records say never_sent_opted_out. Configured welcome includes 52-page PDF link, delivery not verified.
- Subscribers total 3, confirmed 3, unconfirmed 2, WP.com followers 3, direct-email 0. **Pending excluded from totals; none of these counts is actual deliverable inboxes.** No subscriber email data exported.
- New issue worth owner review: /dispatch/ and /focus/ promise ongoing mail while auto-send is OFF; this is not grounds to enable automatic sending, but launch acceptance must check consistency between promise, editorial cadence, and actual opt-in/delivery.

## Exact official merchant claim boundaries
1. https://zen12.com/about explicitly advertises twelve 12-minute levels and four audio types per level, an hour-equivalence claim, brainwave claims and a seller-described 1-year refund. Feature count is a seller listing, not independent effective treatment.
2. https://zen12.com/secret/ shows a route-dependent coupon/promo; price cannot be carried into an FV referred quote, because no account-issued earning URL/checkout is verified.
3. https://inspire3.com/ll/ gives email creative for **Limitless Labs**, a different SKU with required approval. It grants **no** FV Zen12/Total Focus email authorization.
4. https://hypnosislive.com/mental-skills/total-focus: seller lists 33m/47MB Total Focus and seller refund policy, unrelated to Zen12 and insufficient for named FV email rights.
5. https://psychclassics.yorku.ca/James/Principles/prin11.htm primary James 1890 Attention source. **Historical observation is NOT evidence of Zen12 efficacy.**
6. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business: real sender postal address and unsub/opt-out required for commercial messages. Automattic corporate address is not automatically FV postal identification.

## Source-to-revenue contract
- Proposed one `confirmed_signup_v1` per new *provider-authoritative* subscriber confirmation transition; dedupe by opaque provider key, and no email address in repo. WordPress.com users may not always follow identical confirmation-email flows; provider status governs. A download-panel click is not consent.
- Proposed `dispatch_cta_click_v1` on *approved FV guide* only. For non-live guide there is no click event. After approval, standard UTM only if approved by Claude; proposed `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026&utm_content=issue03_zen12`. Do not put unauthorized affiliate tracking on email or invent Grok asset_id.
- Paid purchase only if independently settled merchant commission after refund/fee/chargeback reconciliation. Audited 7/30-day qualified-human sessions required for net revenue/1000. **Currently NOT_COMPUTABLE**, not zero; no genuine figures or A/B evidence.
- One buyer-intent segment HYPOTHESIS: historically minded attention readers who have voluntarily engaged with the Fieldbook and want a modest guided routine. Do not use covert personal profiling or segment to people without verifiable consent. One offer = Zen12 (PENDING all merchant rights).

## Offer → step → blocker → next acceptance proof → owner
| Offer / step | Blocker | Non-live change | PASS evidence | Owner |
|---|---|---|---|---|
| Zen12 / warm-up → paid buyer | No named product/EMAIL partner approval, earning URL, live guide, referred checkout | Keep drafted issue inert; request SKU/channel permission via authorized partner process | Written named acceptance, email-specific approved creative, issued earning URL, Mind-approved publicly live guide, actual referred price/refund | Mind / Commerce |
| Focus / signup → welcome | Eligible recipients and welcome receipt unknown | Private provider-filtered unique eligibility, authorized inbox audit | Redacted provider count, real received welcome and actual downloadable PDF | Focus / Founder |
| Dispatch / email → compliant inbox | Native preview, qualifying publisher address and working unsubscribe unverified | Native **Preview email** with send OFF when safely accessible; no test send | Screenshot native desktop/mobile, valid FV address and opt-out link verified | Dispatch / Founder |
| Grok → attributable net sale | No validated join between social asset→visit→lead→settlement | Independently inspect existing creator asset and privacy-safe source convention | True asset_id, audited qualified human 7/30 cohort, merchant paid settlements and adjustments | Praxxis / Grok / Claude |

## QA scope and limitations
The HTML is an offline illustration, with accessible headings, source links and a non-clickable proposed CTA. It is **NOT** a genuine Jetpack email. Native preheader rendering, physical-address inclusion, unsub behavior, welcome delivery, email-client layout and final copy approval remain UNVERIFIED. All 14 proofs in proof_ledger.json are false. The Node tests are source-controlled and should be executed natively on the exact head. No merchant account access, send, publish, new list, setting change, affiliate activation, spending or merge.
