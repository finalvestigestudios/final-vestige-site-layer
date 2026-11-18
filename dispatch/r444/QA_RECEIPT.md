# Dispatch R444 — executed QA and release evidence

**Date:** 2026-11-18 PT. **Scope:** source-only new files in `dispatch/r444/`; stacked on draft PR #2979, master PR #175 and controlling Issue #174. No changes to any original campaign manuscript, WordPress object, homepage PR #49, Mind owner guide, subscriber record or actual email.

## Exact-source proof
- Fetched original eight campaign assets at **PR #175 original SHA** `d57ccdba3aee8f065e143e101c2945f4f3d01647`, verified all eight returned concrete Git blob SHAs. Re-executed the **six substantive Python guard conditions** in independent V8 against the exact returned files: **6/6 PASS**. This run **did NOT run native Python**. Earlier R434 native Python receipt remains in the prior stacked review.
- GitHub readback of all six R444 assets on `review/dispatch-r444-change-blindness-revenue-audience-20261118` returned stable blob SHAs. 15/15 independent V8 source-level assertions PASS against readback content. Initial case-sensitive heading comparison failed on plaintext's intentional uppercase headings; corrected to case-insensitive structural comparison, then **15/15 PASS**. It was an assertion bug, not a source change. `review.test.cjs` is committed as a reproducible native-Node acceptance fixture, but **was not natively executed** in this run; do not misrepresent that as native test evidence.
- Source SHA inventory at final pre-QA head:
  - `ISSUE01_UNADOPTED.md` `c4d1cd241f3cc03b6e3525799b8012822ddc75cd`
  - `ISSUE01_OFFLINE.txt` `894b174504e3ca6c40a9b419d30938a3b18302a1`
  - `ISSUE01_OFFLINE.html` `b0ef77f7dbb353ee578bcb0235a3843c108c5514`
  - `CLAIM_AND_CTA_LEDGER.json` `a1d65d2a86e1d0b617946323c02a99337a00d2ec`
  - `SUBSCRIBER_TO_REVENUE_WITNESS.md` `f6a090a35a04a6e64fd8bc733af6122bb6912af1`
  - `review.test.cjs` `8b1b4968960ca7e2cdd368b604c44ac845286e59`

## Editorial / visual acceptance
- New Issue01 **515 body words**, single honest subject (47 chars), research-led preheader (103 chars), distinct first-party CTA to **published WordPress post #1922** `https://finalvestige.com/2026/11/02/change-blindness/`. First issue no longer duplicates Issue02's Puységur CTA in this **unadopted** alternative.
- Sources: [Simons & Levin 1998 DOI](https://doi.org/10.3758/BF03208840), [Rensink/O'Regan/Clark 1997 DOI](https://doi.org/10.1111/j.1467-9280.1997.tb00427.x), [FV Editorial Standards](https://finalvestige.com/editorial-standards/). Constrained claim scope: about half detected substitution only in the study's first experiment; flicker effect under its reported conditions; neither proves recording efficacy or generally unreliable witnesses.
- Full plaintext and mobile-width table-based HTML have the same complete textual sections, references, subject/preheader and main CTA. HTML has `lang=en`, inline styles, presentation table, no script/form/image/iframe and visible hold/placeholders. **Actual browser viewport screenshots, email-client rendering, real WordPress native Preview, and inbox delivery were NOT performed.** A static local HTML review is not evidence that Jetpack will render it this way.

## Live WordPress and consent classification (read-only)
- Authenticated 2026-11-18 ~09:34 UTC provider: newsletter total=3 / confirmed=3 / unconfirmed=2 excluded / suppressed=0 / paid=0, `site_can_send=true`; five most recent post notifications = `never_sent_opted_out`; automatic new-post email OFF; full email format and existing 52-page Focus Fieldbook welcome configured.
- Email-subscriber listing = **3 records** with status `Subscribed` and email_subscriber=true. Private identifiers suggest publisher/operator-associated records, not verified independent external acquisition. No PII was copied into the source. A provider eligibility stock is not a new `confirmed_signup`, an inbox delivery, a paid order or an active customer.
- `/dispatch/` currently implies email on post publication although five observed publications had no email. Copy correction needs founder/site owner approval; not touched.

## Partner and FTC releases: all FAIL CLOSED
- Official seller: [Zen12 ordinary](https://zen12.com/), [Zen12 promotional variant](https://zen12.com/secret/), [Hypnosis Live FAQ](https://hypnosislive.com/faq). Seller-offered formats, refund policies, prices and reported claims **are not** Final Vestige account-specific promotional rights. **Partner acceptance, EMAIL channel permission, earning URL, creative approval, current checkout terms, settled conversion report = NOT VERIFIED**.
- [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires valid publisher physical postal address and functional opt-out for qualifying commercial email, as well as nondeceptive headers/subjects. No actual Final Vestige mailing address or rendered Jetpack unsubscribe was verified. [FTC endorsements](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) requires material connection disclosures at the relevant recommendation. R444 has **no merchant link**.
- No native Jetpack Preview, received Fieldbook welcome, test email, externally verifiable new subscriber transition, merchant approval, fulfilled checkout or settled order was observed. **The four editorial/two reserved commercial allocation remains unchanged**, with Issue03=Zen12 and Issue05=Hypnosis Live. All six HOLD UNSENT and no final approval.

## Revenue answer
The program still lacks both audited qualified-human sessions and independently documented paid settlements net of fees/refunds. Net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**; do not say it is zero and do not use click metrics as sales.

### Owner release handoff
- **Dispatch/Founder:** choose (or reject) R444 Issue01 alternative; native Jetpack Preview, consent/received-email witness, FV physical postal + functional unsubscribe required *before* any founder-approved delivery.
- **Mind/Commerce:** named email permission and exact Zen12/Hypnosis Live SKU/link/guide/refund/settlement proofs. No implied approval from ordinary sales pages.
- **Focus/Claude:** genuinely new deduped `confirmed_signup`, recipient/welcome verification in privacy-safe manner; distinguish operator-associated test records.
- **Grok/Praxxis/Claude #820:** source-tagged qualified human sessions and only independent net settled sales after refunds, no extra tracking scripts.

**Release verdict: HOLD UNSENT / UNMERGED / NO CMS WRITES / NO SEND OR TEST SEND / NO MERCHANT ACTIVATION / NO SPEND.**
