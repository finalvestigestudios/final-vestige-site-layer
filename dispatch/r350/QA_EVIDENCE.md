# Dispatch R350 — independent QA evidence and release decision

**As of 2026-11-14 ~08:31–08:50 UTC.** ALL SIX HOLD_UNSENT. Issues 03/05 additionally HOLD_MERCHANT. No newsletter published, test message sent, subscriber contacted, WordPress mutated, merchant affiliate link activated, PR merged or money spent. This is an offline review branch, not a production or received-email test.

## Source-of-truth read-only input and review

- GitHub original #175 exact current head d57ccdba3aee8f065e143e101c2945f4f3d01647; original six issue manuscripts, manifest, test matched ALL eight independently retrieved Git blob SHAs to prior mounted original archive. Master suite **6/6 PASS native Python**.
- Master #174 and companion #171 plus existing stacked #201 and most recent prior #2444 read before edits. R350 adds only the isolated dispatch/r350 subtree, stacked from #2444 commit ae9905051efd56379e90f694607b36ebe2a19bc9. Frozen homepage PR #49 untouched.
- Authenticated WP 2026-11-14 08:31 UTC: newsletter enabled; automatic emails OFF; full content; reply-to=no-reply; sender display Final Vestige Studios; configured 52-page PDF welcome, actual receipt unverified. Newsletter overlapping counts total 3/confirmed 3/unconfirmed 2; WP.com followers 3/direct-email 0; recipient-eligible inbox count UNKNOWN. Recent sampled send states never_sent_opted_out.
- Live /focus/ has a direct PDF and an instruction to “sign up again” after in-app browser trouble; this is a **potential duplicate-attempt / consent-friction bug, not evidence of actual duplication**. Proposed correction is owner-review only, NOT live.
- Live /dispatch/ offers existing Jetpack form. The page's claim that a welcome email includes the Fieldbook is a promise of configured behavior, not independently established received mail.
- Connected Gmail scoped read found October 25 subscription *confirmation request*, no verified final welcome or named FV Inspire3 email promotion authorization; no subscriber addresses included in this report.
- Seller sites accessed 2026-11-14: https://zen12.com/ (format and seller equivalence advertising); https://hypnosislive.com/mental-skills/total-focus (33 min / 47 MB; one public observed price display, NOT final accepted-link checkout); https://hypnosislive.com/faq (14-day refund with five-session/year caveat). No named account EMAIL rights or payout established.
- Official WordPress preview help: https://wordpress.com/support/newsletter/email-appearance/ . Official FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Existing site editorial principles: https://finalvestige.com/editorial-standards/ .

## Native and exact-source checks

1. Master archived source matched exact GitHub HEAD for all eight source blobs. **6/6 original Python tests pass**.
2. New R350 offline Python source and its fixture were fetched from the correct stacked GitHub branch and independently verified to local byte-identical Git blobs: gate.py = c7389715962850c57812a38ebcd62879f5f48dc8; test_gate.py = 9b817c8dad3e3d2f71fb73547deb74ca68bc80ce; SIX_ISSUE_RELEASE_LEDGER.json = 634b19969951a7559d7f55ff30b7da4abd6e086a. The same source/fixture ran **17/17 PASS native Python unittest** after a clarified settled-sale predicate.
3. **18/18 independent exact-GitHub static assertions** against eight new blobs: original 4:2 allocation, six HOLDs, commercial guide CTAs null, account rights false, eligible counts unknown, no send permission, original parent, disclosed seller-specific risks, HTML landmark/viewport/keyboard focus and no addresses.
4. Offline gate results: HOLD_UNSENT, send_authorized=false; flagged provider category overlap, unknown eligible recipients, unknown FV postal, unknown unsubscribe, unknown received email, absent founder approval, unknown paid settlement and human sessions; repeated original 01/02 editorial URL. Its KPI remains null.
5. HTML is a static accessible review document with main landmark, language, viewport, visible link focus. **No browser screenshot, aXe/Lighthouse score, native Jetpack received email, functional opt-out or commercial checkout verification is claimed.**

## Prioritized next acceptance

| Offer → step | Blocker | Needed evidence | Owner |
|---|---|---|---|
| Zen12 → guide → settled commission | No named EMAIL rights, earning link, guide or actual checkout | Privately verified partner approval; live approved guide; separate independently reported paid commission | Mind/Commerce |
| Focus → provider confirmed signup | Non-additive provider counts and no safe dedup | Provider-authoritative one confirmed_signup event, consent and exclusion of signup_attempts | Claude/Focus |
| Fieldbook → welcome | Configured, no final receipt | Owner-controlled actual received welcome and working direct PDF, only with founder authorization | Focus/Founder |
| Dispatch → compliant recipient | Postal address, footer and unsub unknown | Native preview and founder-authorized genuine inbox opt-out + address proof | Founder/Dispatch |
| Grok source → paid customer | Unqualified views and no settled transactions | Grok asset_id inventory, qualified-human sessions, independently settled orders/fees/refunds | Grok/Praxxis/Claude/Commerce |

**No real customers/orders or A/B comparisons are claimed. Realized net revenue per 1,000 qualified humans remains NOT COMPUTABLE.**

## Correction to avoid overclaiming

The R350 gate returns HOLD by design regardless of local flags. Tests prove it refuses to produce send authorization; they do not prove a live recipient, lawful consent, current merchant approval, a production sales result or that any proposed tracking is deployed. Subject/preheader behavior in the native Jetpack inbox remains unverified.
