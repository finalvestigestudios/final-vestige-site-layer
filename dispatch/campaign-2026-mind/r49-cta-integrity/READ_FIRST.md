# Dispatch R49 — canonical CTA and preview repair (SOURCE ONLY)

**HOLD_UNSENT — NOT A RELEASE CANDIDATE.** Canonical six editions in PR #175 are intact. The already-reviewed 4:2 issue mix remains 01/02/04/06 editorial and 03/05 commercial-review-pending. No WordPress writes, newsletter sends, preview/test sends, subscriber exports, merchants contacted, tracking, payment links or homepage changes were authorized or performed.

## Actual defect found: a green test suite validated a stale fixture

The preexisting R48 suite reported 719 passing Python checks, but the R201 readiness tests compared the CTA evidence ledger against their *own copied manifest fixture*, rather than against the original canonical `manifest.json`. The fixture and ledger agreed with one another while disagreeing with the founder's original campaign. Consequently, the rendered six-edition board described a different destination and outdated preheaders even though structural tests were green.

**Four source-truth divergences identified on the exact 2026-11-01 R48 head:**

| Issue | Original canonical source | Old R201 copied fixture / preview | R49 resolution |
| --- | --- | --- | --- |
| 01 primary CTA | `https://finalvestige.com/the-missing-caption/` | Wrongly linked the Puységur dossier | Restore The Missing Caption: authenticated WordPress published page **1122** |
| 01 preheader | “A stranger changed mid-conversation. The evidence lesson starts in the archives.” | “What an old record can teach us about the difference between seeing and knowing.” | Restore exact canonical copy |
| 02 preheader | “In 1784, a young man slept and spoke. His witness drew a startling conclusion.” | “The eighteenth-century witnesses who left behind a problem of proof.” | Restore exact canonical copy |
| 05 preheader | “A free three-minute check, then a clearer look at the claims.” | “Three questions that matter more than an impressive promise.” | Restore exact canonical copy |

This is **not** a change to any of the six submitted manuscripts. The copy was already correct there. R49 repairs the derived fixture, source ledger, and static internal review-board text. Issue 01's correct source trail now points to the published photographic-evidence guide and the 1998 Simons/Levin field experiment rather than pretending Puységur is the source of that story.

## Evidence gathered (Nov 1, 2026 ~19:35 UTC, read-only)

Authenticated WordPress site 256784396 confirms: **The Missing Caption** (page 1122), **Puységur’s Animal Magnetism Files** (page 1377), **The Hatch Opened Inward** (post 434), **Focus Fieldbook** (page 1579), **Dispatch** (page 523) and **Editorial Standards** (page 17) are published. The original Issue 01 manuscript itself links to /the-missing-caption/.

Jetpack Newsletter: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `featured_image_in_email=true`, `post_date_in_email=true`, `reply_to=no-reply`. The configured welcome copy links to the complete 52-page Focus Fieldbook. **Delivery/receipt are NOT established**. `recent_sends=[]` is **not** proof of zero lifetime sends.

The aggregate counters remain `total=2`, `confirmed=2`, `unconfirmed=2`: **inconsistent/nonadditive; unique consent-eligible readers unknown**. Connected Gmail read-only searches on Nov 1 found a 2026-10-25 *Confirm your subscription* message, not a received final welcome/newsletter or written merchant permission. Do not log any subscriber identities or confirmation tokens in this repo.

A separate `verified_routes.json` records page IDs, permissible first-party CTAs and all-false attestations. Its four "published" claims refer **only to existing editorial pages**, not to campaign posts, commercial guides, mail or affiliate offers.

## What R49 added beyond fixing copy

`cross_layer_gate.py` compares original manifest → copied fixture → CTA ledger → all six actual Markdown manuscripts → offline review board. It explicitly catches mismatched subjects, preheaders, link destinations, mismatched issue types, accidental affiliate activation, legal-placeholder removal, missing near-offer disclosures, and unsafe publication state. It verifies only **internal consistency**. It is a hard-OFF, read-only auditor: a zero-drift result **never changes HOLD_UNSENT**.

`tests/test_r49_canonical_source_integrity.py` adds original-source and adversarial checks specifically designed to expose the former fixture-agrees-with-fixture false positive. Use `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` and `python -I dispatch/campaign-2026-mind/r49-cta-integrity/cross_layer_gate.py` on the **exact submitted PR head**; independently inspect GitHub Actions job checkout and final status. Previous green runs do not substitute for current-exact-head execution.

The existing static review board is an **OFFLINE, INTERNAL** visual, not a WordPress email, native subscriber preview or permission to publish. Its updated text remains unsent.

## Actual commercial-route status

Issue 03: proposed Zen12 independent warm-up guide under companion Mind #171 / draft PRs #489/#495 is NOT published or approved as a CTA destination. Issue 05: Hypnosis Live Total Focus independent guide is also NOT live/approved. Both issue manifests deliberately retain `[[APPROVED_*_WARMUP_GUIDE_URL_REQUIRED]]` and `merchant_affiliate_url=null`. Do not silently replace them with seller websites or optional alternate letters.

Official merchant evidence:
- `https://zen12.com/hnp`: seller advertises 12-minute sessions, 4 listening styles, Premium 12 levels/48 MP3s, Beginner 6 levels/24 MP3s, one-year seller refund language, and “1 hour in 12 minutes”/brainwave efficacy claims. These latter claims are NOT independently demonstrated product results. Current checkout/refund applicability and email rights remain unverified.
- `https://hypnosislive.com/mental-skills/total-focus`: seller lists 33-minute, 47-MB audio, a temporarily displayed $2 vs $29.95 price, 14-day seller guarantee language, and strong concentration/brain “reprogramming” claims. Do NOT quote fluctuating prices or refunds as final checkout terms, or treat advertised efficacy as proven.
- Public `https://inspire3.com/ll/` materials are for **Limitless Labs**, not signed Final Vestige authorization to market Zen12 or Total Focus by EMAIL. None of the consumer promo messages found in connected Gmail establish approval.

## Real-world go/no-go remains outside this branch

For **every** edition, a true release requires founder signoff for exact content/audience/date and verified delivery workflow; a genuine received Jetpack email (including real HTML/plaintext and headers), sender identity, Final Vestige's **own valid physical mailing address**, a clearly functioning unsubscribe mechanism, privately reconciled opt-in eligibility and accurately rendered custom excerpts/full-post route. An Automattic or seller postal address cannot stand in for the sender's address.

For **03/05**, separately require written Final Vestige-specific affiliate acceptance and **email marketing permission**, link format, product and current checkout/refund accuracy, independently sourced efficacy boundaries, approved published first-party buyer guides and conspicuous near-offer disclosures. One pilot remains **4 editorial : 2 commercial**, not six sales messages.

FTC CAN-SPAM guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . Real received email and legal review outrank the number of passing software tests.

## Ownership / safety

Owns only Dispatch branch assets, references Issue #174 and product companion Issue #171. The flagship homepage (Issue #150) and frozen PR #49 are never modified. Optional candidate manuscripts from later R-series remain OPTIONAL, founder did not approve substitutions. No costs, new accounts, sending/list/contact actions, public website content changes or preview/test emails were executed.
