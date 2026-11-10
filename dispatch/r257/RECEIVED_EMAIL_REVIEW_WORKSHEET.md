# R257 — Private received-email and consent verification worksheet (NOT executed)

**Purpose:** A reviewer template, not a captured delivery. Leave UNKNOWN fields unfilled until evidence exists. Never paste a subscriber email address, unsubscribe token, street address, message source headers, screenshots with personal data, or account credentials into GitHub.

| Gate | Required read-only evidence | Current | Who |
| --- | --- | --- | --- |
| Native Jetpack preview | Exact post/editor preview with sending default OFF and individual sending flag unchanged; record controls and screenshot with no PII. | UNKNOWN / no native preview obtained | Dispatch / Site QA |
| Inbox subject and preheader | Authorized received email sample; capture only redacted screenshot / observed text and exact revision. | UNKNOWN / no send authorization | Dispatch |
| Sender and reply mode | Real delivered sender, not just `from_name`; no-reply cannot serve as opt-out path. | Configured display only | Dispatch |
| Publisher physical postal address | The verified Final Vestige business mailing address visibly present in qualifying email, not seller or Automattic's address. | UNKNOWN | Founder + Site QA |
| Effective unsubscribe | Visible comprehensible action; tested via separately authorized controlled mailbox, including actual effect/opt-out and compliant processing. | UNKNOWN | Site QA |
| Provider email eligibility | Filtered `Email subscription: Subscribed` aggregate; distinguish WordPress.com follower, email-only follower, unconfirmed, suppressed and import counts. No PII. | UNKNOWN, diagnostics 3/3/2 + follower 0/3 | Focus / Claude |
| Double opt-in/welcome | Provider-confirmed transition and actual authorized received welcome containing correct 52-page PDF link. | Welcome CONFIGURED, receipt UNKNOWN | Focus |
| Commercial email permission | Named account acceptance and explicit EMAIL promotion rights, offer/link format/creative rights and product-specific claim review. | UNKNOWN for Zen12 and Total Focus | Mind #171 |
| First-party guide | Approved public URL, correct seller page, no dead CTA, adjacent prospective commission disclosure, accessible mobile. | NOT LIVE / NOT APPROVED | Mind #171 |
| Actual revenue | Merchant source order and payout with fees/refunds/chargebacks linked to qualified-session cohorts, privacy safe. | UNKNOWN; cannot compute | Commerce / Praxxis |

**Protocol:** No form submission, no test subscriber, no sending/publishing, no list access or import, no toggle changes are authorized by this worksheet. First use genuinely read-only WordPress preview, if one can be reached with all send flags unchanged. If preview requires switching on a sending checkbox, STOP. A received-email test requires distinct founder consent for sender, controlled recipient, date and scope; this document does not provide that consent.

**Legal caveat:** Editorial vs commercial content allocation (4:2) is not the FTC's primary-purpose determination. Conservatively review sender, address and opt-out for all six. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

**Privacy:** Store the yes/no result and a redacted evidence reference privately; do not commit personal recipient data to GitHub. Fieldbook PDF availability does not prove subscription; `confirmed_signup` requires the actual provider-confirmed subscribed transition.

**Final campaign state:** HOLD_UNSENT. Only the founder can authorize final delivery after approvals and independent evidence.
