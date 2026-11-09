# R236 / 2026-11-09 — Conversion-first source and eligibility adjudication

## Operational result
New work is confined to this isolated source-only branch from original PR #175. The alternate Issue 05 is a proposal; it does not replace the founder's original copy or alter the four-editorial/two-commercial allocation. No new list, platform, post, merchant URL, or email.

## First required check FINALLY completed — ORIGINAL Python suite, not a surrogate
The exact current PR #175 HEAD is `d57ccdba3aee8f065e143e101c2945f4f3d01647`, unchanged as of this run. All eight necessary GitHub file contents (6 issue Markdown, manifest, original Python test script) were fetched individually from that head and materialized locally without using a complete checkout. Each file was verified *byte-for-byte* using Git's SHA-1 blob algorithm before execution:

| Path | Git blob SHA |
|---|---|
| issues/01-the-mind-is-not-a-camera.md | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| issues/02-before-hypnosis-had-a-name.md | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| issues/03-the-twelve-minute-question.md | `aeeef34efea0cc281f69901488e4501fea851245` |
| issues/04-the-hatch-and-the-spark.md | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| issues/05-before-you-press-play.md | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| issues/06-the-evidence-log.md | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |
| manifest.json | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| tests/test_campaign.py | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |

Native command executed in local Python: `python -m unittest discover -s tests -p 'test_campaign.py' -v`. **6/6 passed**, 0 errors, 0 failures. This is the FIRST actual native execution of the exact unchanged original test source and exact original input files in the research record. It remains an *offline unit test*, not native WordPress sending, rendering, merchant permission or live buyer evidence. A conventional full GitHub checkout was unavailable because container DNS did not resolve github.com; Git blob verification established exact content identities nonetheless.

## Live read-only 2026-11-09 16:38 UTC
- WordPress Newsletter: enabled; `email_new_posts_by_default=false`; email format FULL; `reply_to=no-reply`; founder Fieldbook welcome configured; `site_can_send=true` but does **not** mean permission to send.
- Counts: total=3, confirmed=3, unconfirmed requests=2, suppressed=0; these are **non-additive**, not five or necessarily three emailable people. Recipient eligibility still unverified, no private subscriber records exposed.
- Five latest published posts in Jetpack recent-sends each show `never_sent_opted_out`; these prove *those posts* were not mailed, not end-to-end welcome delivery.
- /dispatch/ ID 523, /focus/ ID 1579, /editorial-standards/ ID 17 remain published. Focus copy still tells existing readers to “sign up again” after an in-app browser PDF issue. Proposal R228 exists, not deployed.
- No genuine Jetpack received-email preview or welcome MIME, Final Vestige postal address or working unsub verification. No emails sent or tests authorized.

## Offer → funnel step → blocker → change → pass/fail evidence → owner
| Offer / funnel | Blocker | Specific change/experiment | Evidence | Owner |
|---|---|---|---|---|
| Total Focus / reader to interested buyer | Original Issue 05 names broad catalog rather than exact product; cold link to not-live guide | Proposed exact-product 33-minute alternate, distinguish clinical hypnosis literature from untested retail audio; invite to ONE vetted warm-up guide only | **DRAFT** alternative; source assertions pass, never sent | Dispatch + Mind |
| Total Focus / qualifying guide to commerce | Named FV affiliate admission, EMAIL permission, issued earning URL, final checkout price/refund and approved live guide unknown | Obtain actual partner terms in source-of-truth account; Mind chooses authorized page and links | **HOLD_MERCHANT** | Mind |
| Focus / confirmation | Counters nonadditive and download UX mistaken for consent | Authenticate provider email-subscription states and deduplicate confirmations; don't log email PII | **NOT VERIFIED**; counts only | Claude/Focus |
| Subscriber / email inbox | Post-bound Jetpack rendering, footer postal/unsub and reply-to behavior not validated | Authorized unsent WordPress draft native Preview email; distinct later authorized received-test check | **HOLD**; no draft or email created | Dispatch/Site QA |
| Dispatch CTA / warm-up | Guide not live; subscriber mind intent untested | One intent-matched editorial guide after partner approval, not a generic second signup form | **HOLD** | Mind/Dispatch |
| Guide / paid order | No reconciled paid conversion or qualified session denominator | Independently reported paid commission minus refunds/fees matched to source-tagged warm-up sessions; 7/30-day cohorts | **NOT COMPUTABLE** | Commerce/Praxxis |

## Offer claim boundaries, sources and commercial terms
- Seller product page https://hypnosislive.com/mental-skills/total-focus : 33-minute/47-MB MP3 listed; broad promised concentration and “brain reprogramming” are **merchant marketing**, not established product-specific efficacy. Listed prices can vary and are **NOT** verified paid totals.
- Seller FAQ https://hypnosislive.com/faq : instant MP3 download statement, 14-day refund request and five-session annual refund maximum as **seller-described conditions**; final checkout and enforcement NOT checked.
- NIH https://www.nccih.nih.gov/health/hypnosis : research concerns specific clinical contexts and has limitations; does not prove Total Focus effective for workplace focus.
- FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking : disclosure visible near recommendation/link; unsub/postal/true sender and subject still governed by https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Partner-issued Final Vestige EMAIL rights, commercial landing URLs, guarantee, seller creative usage, current prices, refunds and commission status are **NOT VERIFIED**; no links activated.

## Attribution, consent, sales
- Proposed source-tagged **first-party warm-up landing** convention (not deployed): `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_mind_pilot_2026&utm_content=issue05_total_focus`, only on a vetted Final Vestige guide, not on a placeholder or merchant URL. No duplicate measurement script. Session qualification requires anti-bot filtering and affirmative consent where appropriate.
- `confirmed_signup` only on authenticated provider confirmation transition, deduped by opaque provider subscription ID; a PDF-button reveal, `subscribe=` URL, email entry or Reader follow cannot count.
- `paid_conversion` only on independently reported settled order/commission net of refunds and fees; CTA clicks or tracked outbound URLs are not sales.
- KPI: `1000 * realized_net_revenue / qualified_human_sessions` with 7/30-day cohorts, if denominator > 0 and reconciled. **NOT COMPUTABLE** with current evidence. Tiny sample: no A/B inference.

## Release status
All six original issues **HOLD_UNSENT**. Issues 03 and 05 additionally **HOLD_MERCHANT**. The optional R236 issue 05 variant is **NOT ADOPTED**. Final campaign approval required for any draft creation, test send, publication, schedule or recipient contact. Homepage priority and frozen PR #49 untouched.
