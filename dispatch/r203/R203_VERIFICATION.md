# R203 independent verification record — 2026-11-07 PT / 2026-11-08 UTC

## Provenance and scope
- Original **PR #175 HEAD** `d57ccdba3aee8f065e143e101c2945f4f3d01647` remains unchanged. This run obtained its nine current changed paths from GitHub, retrieved source SHA from GitHub at that exact head, and cross-checked 8 blob identities of earlier locally preserved original campaign files. Original README is not in the preserved zip, so it is not among the 8 byte-matched files; its current GitHub SHA was retrieved. No test/data substitution.
- Executed original **native Python** `python -m unittest discover -s <original-campaign>/tests -v` on the preserved verified source tree: **6 tests, 6 passed, exit 0**. Python 3.13.5; Git original head unchanged.
- Current **R203 GitHub source** independently fetched by exact branch ref after corrections; 9 new file blob identities recorded in connector response. `qa_r203.cjs` exported validator executed against those exact fetched strings in a **V8/CommonJS-compatible harness**, 45/45 source assertions pass; six deliberate source mutations rejected: removed FAQ refund ceiling, activated affiliate earning link, invented merchant email permission, fabricated net revenue, invented email-eligible subscriber count, activated placeholder CTA. Initially a refund regression mutation escaped via a source-link slug false-positive; the regex was corrected and all six mutation cases retested. **This is not native Node execution or hosted CI.**
- Static HTML reviewer has `<html lang=en>` / semantic headings and landmarks, inline styles, textual disclosure, no external images/scripts, and no active offer links. **No genuine Jetpack preview, received email, real device/browser render, functional optout, or inbox MIME QA took place.**

## Sources read
- WordPress authenticated newsletter status and settings: 2026-11-08T06:32:21Z–06:32:22Z. `subscriptions=true`, default auto-new-post=false, format=full, sender Final Vestige Studios, reply-to=no-reply, counters total3/confirmed3/unconfirmed2/suppressed0. No recent actual dispatched newsletters in returned five-item report (`never_sent_opted_out`). Confirmed count ≠ exact deliverable count; received welcome unverified.
- Existing live WordPress page IDs: /dispatch/ #523 (modified Nov 5), /focus/ #1579 (modified Nov 5), /editorial-standards/ #17 (last modified Sep 9). Read-only.
- Merchant pages fetched November 7/8: https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://affiliates.inspire3.com/ . Material source nuance: Hypnosis Live item-page **14-day** advertised refund versus FAQ **max five sessions annually**. Seller returns unverified. No independently verified item-specific benefit or affiliate acceptance.
- WordPress native preview docs https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter-email-design/ ; FTC legal guide https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Bounded connected Gmail read-only merchant-approval search found no qualifying Final Vestige-specific Inspire3 acceptance/email permission; a generic “Application Approved” message was unrelated to affiliate marketing. This bounded negative result does not establish absence from portal or other inbox. No recipient addresses or sensitive message text retained in repo.

## Release classification — no guessing
- Original 6 issues remain `HOLD_UNSENT`; #03/#05 `HOLD_MERCHANT`.
- Merchant authorization, approved account-issued earning URL, approved live guides, exact validated checkout and refund terms, subscriber-eligible filtered aggregate, final Fieldbook welcome receipt, FV business mailing address, actual received Jetpack MIME, functional unsubscribe and founder final send approval are **NOT VERIFIED**.
- Realized net revenue/1000 qualified human sessions = **NOT_COMPUTABLE**, not zero.
- **No WordPress writes, blog posts, email/test sends, subscriber contacts/imports, newsletter settings changes, affiliate activations, purchases, analytics scripts, Grok social posts, paid accounts, merges, or frozen homepage PR #49 edits.**

## Offer → step → blocker → change → pass/fail → owner
- Total Focus → buyer research → refund summary was incomplete → compare product page with actual FAQ and add five-session ceiling to optional reviewer candidate → **PASS source/copy QA; FAIL merchant authorization / paid path** → Dispatch/Mind #171.
- Zen12 → qualified guide → no partner email right, issued link or approved public guide → require account-bound documents and verified destination → **HOLD** → Mind #171.
- Focus → consent → browser success and nonadditive counters don't prove provider-confirmed subscription → provider-filtered, deduplicated aggregate and state-transition review → **NOT VERIFIED** → Claude/#129.
- Dispatch → delivery → no actual native preview/received MIME, FV postal line or tested optout → founder-authorized no-send preview first, then explicitly authorized controlled email QA only if approved → **HOLD** → Dispatch/Site QA.
- Purchase → realized net → no verified paid transaction / qualified human denominator → merchant settlement+refunds+fees vs source cohort → **NOT COMPUTABLE** → Commerce/Praxxis #820.
