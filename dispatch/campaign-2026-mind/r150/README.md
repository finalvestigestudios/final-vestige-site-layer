# Dispatch R150 — Native received-email proof, not another preview

**Status: DRAFT / ALL SIX HOLD_UNSENT / COMMERCIAL #03 and #05 HOLD_MERCHANT.** This isolated work builds on draft PR #1176 and the original six-issue master PR #175. Issue of record #174, commercial companion #171, Focus #129, conversion #820. No WordPress, Gmail or merchant write, no email/test send, subscriber import, social post, new analytics script or paid platform. Frozen homepage PR #49 untouched.

## Why this is different from R140–R149

The team already has six manuscripts, many HTML/plain-text simulations, an offline reviewer, subject/excerpt alternatives, first-click fixture probes, synthetic conversion validators and multiple fail-closed merchant gates. **None is a genuine Jetpack-rendered email received by a person.** The remaining evidence problem is at the *mail provider boundary*, not the copy-editing boundary.

The new `received_mail_audit.py` inspects a locally supplied RFC822 .eml **after** a real, separately authorized email exists. It reads MIME subject, From, text/plain, text/html, links and selected accessibility indicators and returns **only evidence booleans**. It never transmits an email, opens a web link, calls a vendor API, prints any recipient address, displays tokenized links or stores message contents. The code cannot authorize sending: `send_authorized` and `commercial_link_authorized` are always false, including when every synthetic check is true. Owner/provenance attestations remain human input, not cryptographic confirmation. A green synthetic case is **not legal signoff**.

### What we checked today (2026-11-05 Pacific; UTC snapshot ~01:33 on Nov 6)

- Authenticated WordPress Jetpack Newsletter: enabled, auto-email for new posts **OFF**, sender **Final Vestige Studios**, reply-to **no-reply**, email format **FULL**. Five recent published-post records each show `never_sent_opted_out`; this is **not** five email sends.
- WordPress dashboard diagnostic: total **3**, confirmed **3**, unconfirmed **2**, imported in previous 24h **0**. The categories overlap: no valid inference of five people or even three independently eligible and reachable recipients. Don't store addresses or treat WordPress.com followers as active email recipients.
- The 52-page Focus Fieldbook remains configured in the welcome. Configuration is not an actual received welcome, confirmation or downloaded file.
- A connected Gmail read-only check found **one** native WordPress `Confirm your subscription` request dated **Oct 25**. Its RFC822 content did not contain the Focus Fieldbook, did contain an Automattic footer and had no `List-Unsubscribe` header. It is **not** a Dispatch campaign email, does **not** prove double-opt-in completed, and **does not establish** Final Vestige's physical postal address or commercial unsubscribe behavior. No actual identifiers or confirmation tokens are copied here.
- Read-only WordPress public page screenshot service reported ready at 390px for `/dispatch/` and `/focus/`. This does **not** prove that the guest input can submit or that any subscriber confirmed. The REST view self-link discrepancy is **not** a verified guest-browser defect; do not label it broken without real browser DOM evidence.
- Published Editorial Standards page #17 requires primary source checking, visible uncertainty, accurate quotes, corrections and disclosures; this work follows those boundaries.

### How to run (ONLY on evidence legally/operationally authorized for this review)

Install nothing: Python 3.10+ standard library only. To test synthetic, nonidentifying fixtures:

```sh
python -m unittest discover -s r150 -p 'test_*.py' -v
```

Expected native QA baseline **28 passing synthetic tests**. Then, if founder explicitly approves an actual test email (or an already received, authorized campaign email exists), have the recipient **privately** export the RFC822 .eml, and place it outside the repository. Never commit the .eml, a redacted screenshot containing identifiable token URL, subscriber addresses, mail headers or other personal information. Provide the valid **publisher** mailing address securely via environment variable `FV_VERIFIED_BUSINESS_POSTAL_TEXT`, only after the business confirms it.

```sh
FV_VERIFIED_BUSINESS_POSTAL_TEXT='REPLACE OUTSIDE REPOSITORY' \
 python r150/received_mail_audit.py --eml /private/campaign.eml \
 --issue 1 --expected-subject 'The mind is not a camera' \
 --first-party-cta 'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'
```

The command **intentionally exits nonzero** until relevant independent/owner checks are supplied: whether the real email was accessed in an authorized inbox, native opt-in eligibility, actual functioning opt-out, source checking and (for commercial issues) approved product-specific email promotion. Flags are self-reported attestations, not automatic proof; keep opaque evidence references separately in the access-controlled review process, not in the repo. No CLI flag provides release authorization.

## Genuine non-sending WordPress preview protocol

WordPress.com's October 6, 2026-reviewed *Modify the appearance of newsletter emails* guide says `Preview email` becomes visible when the editor's **per-post** “Send this post to subscribers” toggle is ON, and `Send test email` is a separate button. The real preview may therefore require temporarily enabling the **per-post** control in an **unpublished, unscheduled editor draft**; if that would create any chance of publishing or send, STOP and leave preview unverified. Do not turn on the site-wide default, click Send test email, click Publish/Schedule, update a live post or save an armed production draft unless founder explicitly approves that exact action and Site QA devises an isolated procedure. An offline HTML board cannot stand in for the actual native preview. Official: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter/send-newsletter-emails/ .

After a **separately approved** received-email test, inspect desktop and phone display, exact subject, any native inbox preheader, the full-versus-excerpt body, real first-party CTA, display-name identity, footer **after** Jetpack processing, unsubscribe link **functionality**, and the publisher's verified postal address. Keep only boolean and source references in issue #174. A reply-to of no-reply does not itself prove CAN-SPAM compliance.

FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; endorsement disclosures: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . This is engineering QA, not a legal opinion.

## Six-issue conversion review, one primary CTA in each

| Issue | Value promised / destination logic | Intent & release evidence |
| --- | --- | --- |
| 01 (editorial) | First-party perception investigation is more appropriate than duplicate Puységur CTA; R142 alternate candidate remains optional | Source check + true published destination; human approval; no affiliate |
| 02 (editorial) | Historical Puységur evidence, not a hypnosis effectiveness claim | Published case file only; human approval; no affiliate |
| 03 (commercial reserved) | Free twelve-minute observation/meditation routine → optional **Zen12 Premium** independent buyer guide | **BLOCKED** until Mind #171 verifies published exact guide, named affiliate enrollment, specifically **email marketing rights**, earning URL format, vendor terms, adjoining disclosure, human approval |
| 04 (editorial) | Apollo 1 hatch/story record; consequential exact claims must be sourced | Keep an evidence-led history pillar; human approval |
| 05 (commercial reserved) | Three-point audio evaluation checklist → independent **Hypnosis Live Total Focus** guide | **BLOCKED** until named rights, approved guide, current product checkout/refund, attribution, near-offer disclosure; don't confuse with “Hypnotize Yourself” |
| 06 (editorial) | Evidence log and 52-page Fieldbook for an **already subscribed** reader | The original /focus/ may ask them to subscribe again; R142 direct-PDF alternate is optional, not silently approved |

Subject and preheader copy are **editorial proposals**, not native deliverability facts. Current Jetpack post-title-as-subject behavior and separate preheader support still require an actual preview.

## Merchant claim/permission boundaries

Official Zen12 seller page: https://zen12.com/?no-popup=1 advertises **12 levels and 48 MP3s** in Premium; claims that 12 minutes delivers an hour of meditation or induces automatic benefit are **seller representations, not proof**. Hypnosis Live seller page https://hypnosislive.com/mental-skills/total-focus describes an audio recording **33 minutes / 47 MB**; the live retrieved page displayed dollar values differing from older cached search results, so use **no locked price, refund guarantee, urgency or 'works' assertion** without fresh checkout + official policy verification. The fact that a public affiliate portal exists is **not** evidence Final Vestige may use commercial email.

A broad Gmail merchant-approval query returned unrelated promotions and no qualifying named acceptance/authorized email-promotion evidence. Absence of mail is not evidence of rejection; portal approvals remain **UNKNOWN**. The seller's UK address (and Automattic's address on an unrelated confirmation) **do not** satisfy a Final Vestige commercial sender-address requirement.

## Attribution and decision hierarchy

Do not introduce tracking scripts. Preserve Grok-owned social distribution/asset IDs, Claude-owned site instrumentation and Praxxis-owned coordination. One native **confirmed_signup** event can be accepted only from a deduplicated Jetpack provider confirmation with lawful consent provenance; UI success/URL query strings and clicks are never proof. The consent source also must not be conflated with a distinct marketing-email permission. Email CTA URL tagging may be used later only after QA of current analytics rules and no duplicate event counts.

The business conversion metric is **settled net revenue per 1,000 qualified human sessions**, calculated from independently confirmed paid orders/affiliate statements, refunds and fees, not opened emails or CTA clicks. In this snapshot both sessions and settled revenue are **UNKNOWN**, so the KPI is **NOT COMPUTABLE** rather than zero.

## Owner-by-blocker action path

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Fieldbook → guest signup | REST representation suggests self-link but real guest DOM unknown | Signed-out, non-submitting production browser proof at 320/390/768/1440 | **UNKNOWN**; screenshots alone not functional proof | Claude + Site QA |
| Signup → confirmed lead | Total/confirmed/unconfirmed counts overlap; native per-recipient eligibility unavailable | Authorized private provider reconciliation, dedup, unsubscribe/consent status | **HOLD**; no identifiable data in Issues | Dispatch + Claude |
| Confirmed → Fieldbook | Welcome configured but no verified successful receipt | Inspect independently received, authorized welcome and PDF retrieval | **HOLD**; Oct 25 confirmation is not a welcome | Dispatch |
| Dispatch → reader | Full native email MIME/footer, unsubscribe and preheader unknown | Native non-sending preview; later specifically approved received-email check using this tool | **HOLD** | Dispatch + Site QA |
| Zen12 Premium → paid buyer | Email approval, live guide, earning URL and checkout not verified | Source-of-truth authorization + guide QA | **HOLD_MERCHANT** | Mind & Affiliate Studio |
| Total Focus → paid buyer | Same + price/refund variations | Exact-offer rights and terms | **HOLD_MERCHANT** | Mind & Affiliate Studio |
| Paid buyer → net proceeds | No independently reconciled paid transactions or qualified sessions | Payhip/partner settlement vs fees/refunds in 7/30-day cohort | **NOT COMPUTABLE** | Praxxis + Commerce/Claude |

**Release verdict:** four editorial **HOLD_UNSENT**, two commercial **HOLD_MERCHANT_AND_UNSENT**, founder final send approval absent; zero contact, production changes, money spent or emails sent in this sprint.
