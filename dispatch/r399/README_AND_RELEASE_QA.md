# Dispatch R399 — Native inbox-proof gate, optional Issue 01, and conversion hold

**Master:** Issue #174; companion #171; Focus #129; revenue #820. Stacked on DRAFT #2733 HEAD `17fc7b56ceca39f3d1fb861c6b608994f6ef10ce`. Original six-issue #175 and per-edition guard #201, as well as frozen homepage PR #49, are unchanged.

## Actual delivery

- `inbox_preview_gate.py` audits a **manually saved private RFC822 .eml** offline. Its JSON output contains only aggregate checks; no sender/recipient addresses, subject text, message body, subscriber information, or tokenized unsubscribe URLs are emitted.
- `tests/test_inbox_preview_gate.py` contains 15 adversarial native tests. `PYTHONPATH=. python -m unittest discover -s tests -v` passed **15/15 with exit 0** on Python 3.13.5. The **exact deployed GitHub blobs** for those two files matched locally native-tested git SHA-1: `00ca5bcaaa29b935f62ccd73851edfe20fde242f` and `05d025770b18b8a0c83f920da71cb2faee672391`. No external email was accessed as test input; all MIME cases were synthesized, including an invalid-domain address.
- Optional **Issue 01: The person who changed mid-conversation** is source-led, noncommercial and **NOT ADOPTED**. It supplies a full alternative opening with Simons & Levin 1998 and Simons & Chabris 1999 primary links, distinguishes change blindness from inattentional blindness, and uses one confirmed LIVE editorial CTA to site post 1922. The canonical Issue 01 stays untouched.
- `ISSUE01_CHANGE_BLINDNESS_OFFLINE.html` is a responsive static *review specimen*, not a WordPress native or received email. Markdown is also human-readable plaintext. Do not use this HTML as a send-ready template.

## Reproducible local commands

```sh
PYTHONPATH=. python -m unittest discover -s tests -v
python inbox_preview_gate.py --help
# PRIVATELY, only after the founder separately authorizes received-email evidence:
python inbox_preview_gate.py private-received.eml --edition 03 --subject 'Founder-approved subject' --postal 'Founder-validated physical postal address'
```

The parser can syntactically detect an unsubscribe anchor, postal string, subject, seller-link leakage, seller-disclosure language, HTML/plain parts, research citations and template placeholders. **It cannot verify that an unsubscribe actually works, a postal address is legally valid, a subscriber has opted in, or that WordPress Preview renders correctly.** Presence of `List-Unsubscribe` alone is not a verified visible unsubscribe. All actual proof attestations default false; even if supplied true, the gate returns `REVIEW_CANDIDATE_ONLY` and `send_authorized=false`. It never makes any network request, sends email, modifies WordPress or contacts the list.

## Live read-only verification, November 16, 2026 at 11:46 UTC

WordPress newsletter: enabled; new-post automatic email OFF; full-text content ON; no-reply; sender label Final Vestige Studios. Welcome config references 52-page Focus Fieldbook. Status total=3, confirmed=3, unconfirmed=2 (nonadditive), suppressed=0; **actual unique email-eligible recipients UNKNOWN**. Latest five posts `never_sent_opted_out`. Provider `site_can_send=true` means technical capability, not consent or founder authorization. Native Jetpack Preview email and actual received welcome remain unverified. Targeted connected Gmail search found no exact final Fieldbook welcome or named merchant-email authorization; absence from a search is not proof it does not exist elsewhere.

Published WordPress routes verified: /dispatch/ page 523, /focus/ page 1579, Editorial Standards page 17; Change Blindness post 1922 at https://finalvestige.com/2026/11/02/change-blindness/ . Existing Focus query-string download visibility **is not** an authenticated confirmation event (prior R398 proof).

## Conversion-first, prioritized acceptance

| Offer → funnel | Blocker → change / experiment | Evidence result | Owner |
|---|---|---|---|
| Zen12 → approved guide → paid commission | Obtain named Final Vestige SKU-specific **EMAIL** permission, issued earning URL, genuinely live vetted guide and current referred checkout before testing a reader path | HOLD_MERCHANT, all external permissions remain unverified | Mind / Commerce |
| Hypnosis Live → chosen recording | Decide catalog vs Total Focus SKU; confirm partner approval, promotion rights, actual earning link | HOLD_MERCHANT | Mind / Founder |
| Focus → provider-confirmed lead → 52-page welcome | Decouple public download CTA from opt-in, use provider-authoritative confirmation + dedupe, verify actual welcome receipt | HOLD_CONSENT; no real deliverability evidence | Claude / Focus |
| Dispatch → actual inbox | Founder conducts non-sending WordPress **Preview email** and documents real sender/footer/postal appearance; opt-out test only after independent approval. Offline MIME tool is NOT an email preview | HOLD_LEGAL | Dispatch / Founder |
| Grok asset → qualified human session → vetted offer → paid settlement | Existing asset_id + utm campaign continuity, 7/30-day cohorts and independently settled orders net refunds/fees | Net revenue / 1,000 sessions NOT_COMPUTABLE | Grok / Praxxis / Claude |

**Official sources:** https://wordpress.com/support/newsletter/email-appearance/ (Preview email vs Send test email); https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://hypnosislive.com/catalog ; https://hypnosislive.com/faq ; https://inspire3.com/ ; https://inspire3.com/ll/ (Limitless Labs swipe rights DO NOT confer Zen12 rights); https://doi.org/10.3758/BF03208840 ; https://doi.org/10.1068/p281059 .

**Final release:** Canonical 01–06 remain `HOLD_UNSENT`, commercial 03/05 `HOLD_MERCHANT`, 04 `HOLD_COPY`; optional 01 `NOT_ADOPTED`. Original four-editorial/two-commercial ratio preserved. No emails/test emails, subscriber contacts, imports, WordPress changes, affiliate activation, platform creation, tracking installation, spending or merges. Publisher postal, functional unsub, eligible private audience, real preview, full welcome receipt, merchant rights and paid commissions remain UNVERIFIED. No invented A/B results, engagement numbers, or revenue.
