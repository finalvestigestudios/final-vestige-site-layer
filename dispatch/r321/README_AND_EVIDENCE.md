# Dispatch R321 — History-grade witness edition, non-sending review

**Status: HOLD_UNSENT / NOT_ADOPTED.** Branch is based directly on original master PR [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) exact SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`, avoiding the long chained R318–R320 stack. Adds only five `dispatch/r321/` review files. R320 [#2291](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2291), QA #201, prior optional candidates and frozen homepage #49 are not changed. Original founder-approved allocation remains **four editorial / two commercial-draft**.

## Source of truth inspected (2026-11-12/13)

- [GitHub Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), current #175 and #201 PR heads, latest R320 and recent Mind handoffs.
- Authenticated WordPress newsletter read at **2026-11-13 04:35 UTC**: enabled, send-capable, `email_new_posts_by_default=false`, `email_content_format=full`, sender Final Vestige Studios, no-reply, existing 52-page welcome Fieldbook URL. Total/confirmed/unconfirmed **3/3/2** (nonadditive); separate WordPress.com followers **3** and direct-email followers **0**. Actual email-eligible recipients remain **UNKNOWN**. Last five post records `never_sent_opted_out`, not evidence of zero historical sends. Welcome receipt and actual unsub/postal footer/inbox preview **UNVERIFIED**.
- [Live /dispatch/](https://finalvestige.com/dispatch/): published, public page displays native email input and Subscribe control. Editor content's fallback anchor **does not demonstrate** that the public form is broken. [Live /focus/](https://finalvestige.com/focus/): published signup, download and confirmation instructions; downloading the PDF **does not** count as provider-confirmed consent. R320 independently found an untrusted query-parameter gift visibility trigger; Claude owns any production remedy.
- [Editorial Standards](https://finalvestige.com/editorial-standards/): edition provenance, transparent uncertainty, visible commercial independence.
- Grok/Praxxis [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) and [handoff](https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit): Grok owns social publication; Claude owns website/analytics engineering. No queues or assets edited.

## Why this edition was worth writing

Original Issue 02 said 1785 historical testimony raised a problem of proof, but did not show the reader the **specific evidence**. This optional replacement gives a stronger narrative: a signed document or witness report establishes a report, not the mechanism alleged to cause it. It names an **unsuccessful prediction** preserved in Final Vestige's source investigation, adds a clear witness power/consent limitation, and gives readers a practical three-question method for reading claims. A single editorial CTA goes to the existing live Puységur archive. Neither an affiliate link nor a fresh subscription pitch is introduced.

Source check:
- [Wood Library-Museum catalog](https://www.woodlibrarymuseum.org/rare-book/chastenet-de-puysegur-amj-memoires-pour-servir-a-lhistoire-et-a-letablissement-du-magnetisme-animal-1786-suite-des-memoires-pour-servir-a-lhistoire-et-letablissement-du-magnetisme-animal-1785/) identifies the separately issued **1785** London *Suite des mémoires* at 256 pages, and separately lists an 1786 integrated volume.
- [BnF catalog](https://catalogue.bnf.fr/ark:/12148/cb31160297p) identifies the full work as two volumes **1784–1785** (232 and 256 pages).
- [Final Vestige Puységur archive](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) clearly distinguishes 1785 original-edition reference, an **1813** verification facsimile, the Rieux prediction failure, recorded ethical conflicts, and proof-of-document vs proof-of-magnetic-mechanism.
- No untranslated primary-source quotation is invented. The edition's first sentences are editorial framing, **not a historical reconstruction**.

## Deliverables

- `issue02-proposed.md`: full proposed email with subject, preheader, seven body paragraphs, a single specific CTA, source notes, evidence boundary, and deliberate sending stop fields.
- `issue02-proposed.html`: offline review specimen, inline-styled one-column table, descriptive links, one H1, no scripts/forms/pixels/external media. Visible HOLD banner; **NOT** a Jetpack actual preview.
- `issue02-proposed.txt`: plaintext parity; one editorial CTA and bibliographic source links.
- `test_r321.py`: source-controlled Python guard tests for master 4:2 hold, source claims, one CTA, disclosure of release placeholders and no merchant activation.
- This README: research, live provenance, conversion-first decisions and required authorizations.

## Independent QA and limitation

The original master `test_campaign.py` passed **6/6** natively using exact source bytes whose **eight Git blob hashes** were compared to current #175 head. Locally developed R321 artifacts passed **14/14 Python tests** and an **offline Chromium five-viewport sweep at 320, 360, 390, 768 and 1440 pixels** after fixing a small-screen table-width overflow. New committed R321 tests still require an exact-PR-head **native** rerun: local test source and committed test source are not asserted byte-identical here. Do not claim the standalone HTML is a real received email or provider rendering, or that it establishes WCAG/Inbox client conformance. No test email authorized.

## Offer → funnel → blocker → evidence → owner (strict revenue priority)

| Offer/funnel | Blocker | Required change or test | Evidence and owner |
|---|---|---|---|
| Zen12 Premium → vetted guide → paid order | Final Vestige-specific affiliate acceptance, email permission, exact earning link, live authorized guide and checkout terms missing | Mind/Commerce verify agreement, tier-correct guide and disclosed earning URL; founder signs off | **HOLD_MERCHANT** — Mind/Commerce |
| Total Focus → vetted guide → paid order | Same authorization gaps; specific MP3 benefits not independently established | Audit exact product guide against [seller page](https://hypnosislive.com/mental-skills/total-focus), not general catalog | **HOLD_MERCHANT** — Mind/Commerce |
| Focus → new verified lead | Subscriber counts overlap; downloadable PDF and URL-triggered panel are not consent | Privately verify provider confirmation transition, current Dispatch consent/eligibility, welcome receipt and dedup | **UNKNOWN** — Claude/Focus |
| Dispatch → recipient inbox | Publisher address, native unsubscribe and actual Jetpack rendering still unwitnessed | Separate approval for **non-sending CMS draft** and post-specific email OFF preview; do not send a test message | **HOLD_UNSENT** — Dispatch/founder |
| Grok asset → qualified session → paid settlement | Actual asset ID, first-party human join, merchant settled transactions, fees/refunds unavailable | Reconcile canonical TASK-008 attribution, 7/30-day cohorts, independently settled orders | **NOT COMPUTABLE** — Grok/Praxxis/Claude/Commerce |

Public [Zen12 seller page](https://zen12.com/) sells separate Beginner/Advanced six-level packages and Premium twelve-level package. Seller's `12 minutes = hour` benefit is **not independently established**. [Total Focus seller page](https://hypnosislive.com/mental-skills/total-focus) currently displays 33 minutes / 47 MB, $24.44 and advertised 14-day refund; current checkout is unverified. [Inspire3 public affiliate page](https://affiliates.inspire3.com/) describes earning referrals, **not FV-specific permitted email advertising**. No current affiliate approval/rights email was found in targeted connected Gmail searches; absence from that mailbox is not proof the merchant has no account record.

[FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires final-message primary-purpose analysis, accurate sender/subject, valid publisher postal address and functional opt-out for covered promotional emails. All six originally drafted issues remain `HOLD_UNSENT`; 03 and 05 additionally `HOLD_MERCHANT`. This alternative is **not adopted**. It cannot create a true confirmed signup, send email, alter CMS or record a purchase. Gross/net sales, paid conversion rate and **net revenue / 1,000 qualified human sessions** remain **not computable**, rather than zero or fabricated.
