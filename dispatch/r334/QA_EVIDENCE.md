# Dispatch R334 — exact-source and native QA evidence (2026-11-13 PT)

Owner #174. Base PR #2366 exact `aad7f67fa5250675ce18d4b807db0eb0b0976744`. Separate additive branch `dispatch-r334-mail-consent-to-revenue-audit-20261113`; no original six-issue source, homepage #49, Mind #2368 or WordPress site files changed.

## Work executed and independently checked

- **First:** Read actual GitHub Issues #174/#171/latest comments, original PR #175, independent #201, latest parent #2366; authenticated WordPress Newsletter status and settings and the published /dispatch/, /focus/, Editorial Standards. Also read Grok/Praxxis TASK-008 through the native Google Drive document connector without editing it.
- Original master #175 exact commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`: all eight Git blobs re-fetched and matched the archived eight verified source files. Native Python `unittest discover` **6/6 PASS** on that byte-identical master source.
- New `consent_revenue_gate.cjs` at Git blob `57cc0da78543b8cf4e5242eb5ca0ea859d68eb29` and `consent_revenue_gate.test.cjs` at `86cdd68b558c262aa9aaf7ef6e39cd38795abf62` verified against `git hash-object` of local native-executed files; **37/37 native Node tests PASS**. Tests cover synthetic opt-in vs attempted signup, consent-scope confusion, deduplication, source-asset UTMs, anti-bot candidate counts, merchant settlement/refund integrity, no paid-sales inference from clicks, PII rejection, and immutable NO_SEND/NO_POST/NO_AFFILIATE statuses. An initially detected false-positive PII key name was fixed before GitHub commit; all tests then passed.
- All ten new GitHub source files read back; **20/20 final committed-source structural/claim/safety checks PASS**, including HTML `lang`, viewport, semantic H1, email-safe presentation table, plain/HTML disclosure, no scripts, no merchant-purchase/affiliate links, no active guide CTA and all-false proof attestations.
- A first-pass guard **caught active direct seller source hyperlinks in the reviewer HTML** despite unverified email rights (19/20 source checks). HTML and plaintext were separately hardened, then all **20/20** final checks passed. The official seller URLs remain in the internal source dossier, *not as an active email CTA*.
- Reproducible local QA archive contains 37 native Node cases, 6 native original Python cases, exact two Git blobs, and a fuller local offline reviewer variant. Other locally prepared copy/reviewer files **differ** from final GitHub files (seller-link hardening); GitHub is the canonical new edition. Actual inbox rendering NOT tested; a local Chromium attempt timed out and cannot count as browser QA.

## Authenticated WordPress read-only status 2026-11-13 17:36 UTC

Newsletter enabled/send-capable; auto-new-post emails OFF; full post body format; From display `Final Vestige Studios`, reply-to no-reply, 52-page Fieldbook welcome CONFIGURED. Subscriber dashboard **total=3 / confirmed=3 / unconfirmed=2** overlapping. Actual recipient eligibility and completed welcome receipt are **not verified**. Five recent post records `never_sent_opted_out`, not lifetime zero sends.

Private Gmail search (no addresses/tokens exported) found an October 25 WordPress confirmation **request** and consumer Inspire3 marketing mail, not a completed Fieldbook welcome or account-specific affiliate email marketing acceptance.

Official source alignment: [Zen12 seller](https://zen12.com/) states 12 levels/48 MP3 and makes hour-equivalence efficacy advertising claims that this draft does **not** present as scientific facts; [free audio signup](https://zen12.com/gift) is a separate merchant newsletter; [Inspire3 affiliate portal](https://affiliates.inspire3.com/) is public recruitment, not proof of FV email-channel rights. [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires a valid publisher postal address and functional opt-out; [FTC Endorsement FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) requires clear commission disclosure. Actual merchant purchase/refund/delivery terms and current checkout not independently validated.

## Release and KPI

**All six original editions HOLD_UNSENT. Commercial #03/#05 HOLD_MERCHANT. Alternative R334 #03 NOT_ADOPTED.** 14 proof conditions begin false. Even forged `verified:true` receipts cannot turn on sending in the guard. Actual paid orders, confirmed leads, qualified-human sessions, settled commissions, refund-adjusted net and net revenue per 1,000 are `null` / NOT COMPUTABLE. Synthetic tests are not business results.

No real/subscriber email or test email sent; no WordPress post/settings write, list import/export, social publication, analytics deployment, affiliate activation, purchase, merge or spend.

**Owner next:** Zen12 Premium → approved guide → settled sale: partner account/email rights/issued link/guide and terms = HOLD (Mind/Commerce); Focus → confirmed lead: private Jetpack receipt, eligibility, dedup and welcome = UNKNOWN (Claude/Focus); Dispatch → received email: authorized Jetpack proof, legal FV address/unsub and founder approval = HOLD (Dispatch/Founder); Grok → qualified session → paid order: real published asset IDs, legitimate attribution and merchant settlement = NOT COMPUTABLE (Grok/Praxxis/Claude/Commerce).
