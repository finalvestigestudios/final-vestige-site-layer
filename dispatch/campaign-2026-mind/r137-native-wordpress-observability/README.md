# Dispatch R137 — native WordPress diagnostic truth, import-counter reconciliation and conversion release gate

**2026-11-05 12:32–13:00 UTC. DRAFT / READ-ONLY / ZERO SEND.** Owner: Dispatch Campaign Studio, Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Conversion charter [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); exact-product permissions owned by Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).

**Master manuscripts:** [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), original six files, 4 editorial/2 merchant-reserved; independent readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201). This branch stacks on [#1085](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1085) at `54c4e41dcbfb452f1f18d02e2268d4bb907916b3`. Do **not** merge/publish this stacked work as a production release; do not touch homepage PR #49.

## 1. NEW, independent native account evidence (November 5, 2026)

Authenticated **read-only** WordPress `newsletter.get_settings` and `newsletter.status`, site blog ID 256784396, responded respectively at **12:32:30 UTC** and **12:32:36 UTC**. Sanitized evidence is in `2026-11-05-aggregates.json` (no subscriber addresses).

| What was inspected | What native WordPress actually returned | What it does NOT prove |
| --- | --- | --- |
| Newsletter enabled | `subscriptions=true`, `site_can_send=true` | Consent, recipient reachability or an actual send |
| New-post email | `email_new_posts_by_default=false` | Newsletter campaign sent (it was not) |
| Email body | `email_content_format=excerpt` | That a specific CTA/disclosure is preserved in recipient inbox |
| Subscriber diagnostics | total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**, paid **0** | Five distinct people, 3 valid email recipients, 3 newly confirmed leads or opt-in provenance |
| **New diagnostic flag** | `imported_last_24h=1` | Who initiated any import, whether a migration/self-signup counted as imported, a consent defect or any wrongdoing. **Investigate privately against native administrative activity**; our agents did not import addresses this run. |
| 5 recent post-email statuses | All `never_sent_opted_out` (IDs 1926/1924/1922/1920/1917) | Any inbox delivery, click or conversion |
| Welcome configuration | 52-page Fieldbook download URL present; sender Final Vestige; reply-to no-reply | Actual welcome receipt or working subscriber download |
| Media library read-only | PDF asset **1737**, `application/pdf`, **599,946 bytes**, filename matches configured welcome URL | HTTP download success, 52 readable pages or subscriber receipt |

**Interpretation:** WordPress's total/confirmed/unconfirmed fields must NOT be summed. Imported-last-24h is a new counter to reconcile; it is **not** permission to access, export or modify subscribers. The user has not authorized a newsletter platform change, a list import, or test messages. An existing WordPress.com account may follow a different confirmation path than a new external email address, so don't require a separate email confirmation for every legitimate status or claim a confirmed account equals a delivered welcome.

**Live source checks:** `/dispatch/` (WP page #523) and `/focus/` (#1579) remain published, and `/editorial-standards/` (#17) continues to require evidence-first reporting and commercial independence. The serialized Jetpack Subscribe block may project as same-page link; without signed-out rendered DOM it is *not* evidence of a broken form. R136's read-only browser probe remains available, but actual navigation previously returned NOT_TESTED_LIVE. A status screen or URL query alone is never proof of a new confirmed signup.

## 2. New software: aggregate-only, fail-closed reporting

`wp_status_audit.py` operates on the two native **read-only** response objects, never calls a service or stores any addresses, and emits only sanitized counts/statuses. Strict checks reject malformed, cross-site, non-read-only, negative, boolean-as-integer, missing-timestamp and incomplete inputs. Data containing personal addresses or titles is intentionally not copied to the result.

`test_wp_status_audit.py`: **28/28 native Python 3.13.5 unit tests PASS**, including the nonadditive counts, import-counter warning, privacy redaction, false revenue, all-six HOLD, invalid input, full-vs-excerpt, and prior sent-state failure. Both files have been committed independently to GitHub and read back by Git blob SHA; test locally with:

```sh
cd dispatch/campaign-2026-mind/r137-native-wordpress-observability
python -m unittest -v test_wp_status_audit
```

The original master PR #175's six Python tests were also independently rerun from the byte-identical archived source at original SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`: **6/6 PASS**. These are source-level offline checks, **not** hosted CI, live Jetpack rendering, checkout testing, subscriber eligibility, or receiving-mail evidence.

**Limit:** Test-count success cannot clear a production gate. This audit deliberately returns unknown for confirmed_signup events, eligible recipients, paid orders, welcome receipt and net revenue per 1,000 qualified human sessions.

## 3. Highest-value next operational checks: consent → helpful editorial → verified purchase

| Offer → funnel step | Blocker | Proposed change / experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Focus Fieldbook → confirmed lead | `total=3/confirmed=3/unconfirmed=2` plus `imported_last_24h=1` are ambiguous | Inspect native subscribed-email status filtered privately; compare self-signup/account-linked/import origin and double opt-in where applicable, only aggregated results shared | **NOT VERIFIED**; never expose addresses; dedupe each `confirmed_signup` by native transition (not clicks or count diff) | Dispatch + Claude |
| Focus → received Fieldbook | Welcome link configured; media asset exists; receipt/HTTP/PDF not proven | Authorized read-only inbox proof and direct download/content checks (no sending test without explicit founder approval) | **CONFIGURED, NOT RECEIVED**; PDF media id1737 is metadata only | Dispatch QA |
| Dispatch → useful reader action | Native excerpt may truncate CTA/disclosures in all six originals | Inspect actual Jetpack preview in WordPress editor; compare full/excerpt *without saving/changing settings*; inspect links, subject, plain text, legal footer at mobile widths | **NOT TESTED IN ACTUAL EMAIL**; synthetic model does not clear | Dispatch/Claude |
| Exact Zen12 Premium → buyer | No named acceptance, email permission, approved earning link or approved live first-party guide | Mind obtains written source-of-truth permissions, verifies exact sale page, terms, right-to-promote-by-email, and guide; then Dispatch verifies one appropriate CTA | **HOLD_MERCHANT**; merchant claims not independent findings | Mind #171 |
| Exact Hypnosis Live **Total Focus** → buyer | `Hypnotize Yourself` is a distinct SKU; merchant display price varied between visits | Keep Total Focus 33min/47MB separate from Hypnotize Yourself 44min/61MB; verify actual checkout/refund, approved same-SKU presell, email authorization | **HOLD_MERCHANT**; don't quote fixed price in emails | Mind #171 |
| Qualified Grok asset → realized net revenue | No independently reconciled paid affiliate conversions or attributable settled orders | Use approved `asset_id` UTMs via Grok→Focus→Dispatch, first-party CTA events and independently settled orders/refunds/fees; 7- and 30-day cohorts | **NOT COMPUTABLE**; no A/B significance claims with tiny list | Claude + Praxxis #820 |

## 4. Footer, claims and permissions — explicit release restraints

1. Confirm actual visible sender identity, honest subject/preheader, recognizable promotional purpose, **valid Final Vestige postal address** and functioning unsubscribe/opt-out on the *received commercial email*. Automattic's own address in a platform confirmation is **not** Final Vestige's physical address.
2. A first-party independent guide may contain an approved affiliate link only after Mind verifies **named partner acceptance**, **email-channel permission**, **earning link format**, **product-specific terms**, and **near-link commercial disclosure**. A general footer disclosure is insufficient when a qualifying offer is presented.
3. Zen12's audio-duration equivalence and brainwave claims and Total Focus's concentration claims are **merchant representations**; no unsupported efficacy, medical, financial or personal-result claims. Note Zen12's free-audio signup may create a *separate seller newsletter relationship*.
4. Confirm the five recent post notifications remained opt-out; do not toggle, publish, contact subscribers, schedule posts, bulk import or send test email without founder's specific final campaign approval.
5. Remember campaign allocation: 01/02/04/06 editorial, 03 Zen12 commercial-reserved, 05 Total Focus commercial-reserved. All six **HOLD_UNSENT**; 03/05 **HOLD_MERCHANT** too. No alternative copy replaces the approved draft without an editorial decision.

**Official reference pages:** [Editorial Standards](https://finalvestige.com/editorial-standards/); [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business); [FTC Endorsements](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking); [Zen12](https://zen12.com/); [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus); [FV affiliate disclosure](https://finalvestige.com/affiliate-disclosure/).

**Revenue decision:** No verified paid sales or qualified-human denominator available. This sprint produces evidence discipline and a new import-origin diagnostic, not revenue or a live improvement.
