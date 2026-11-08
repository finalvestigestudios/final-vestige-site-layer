# R18 editorial and source audit — Apollo 1, Issue 04

**2026-10-31. DRAFT / HOLD_UNSENT.** Master #175; Dispatch issue #174; companion Mind issue #171. This revision changes only Issue 04's narrative and derived preview pair; it leaves all six subjects, all preheaders, the four-editorial/two-commercial split, legal release gates, and other editions intact.

## Why this edit matters
The previous version compressed the accident into a 17-second frame, then catalogued hazards. The revised issue makes its own central evidentiary distinction explicit: **the interval between the first recorded crew report and the end of the final radio transmission is not the time-to-death or a precise instant of fire ignition**. It also shows *how* investigators separately combined the primary radio timeline, hazardous test conditions, and a qualified ignition inference. This is a deeper, more useful email and a stronger reason to read the existing historical investigation.

## Primary-source trace (checked October 31, 2026)

| Draft claim | Source and pinpoint | Claim treatment |
| --- | --- | --- |
| First final S-band transmission 23:31:04.7–23:31:10 GMT; second 23:31:16.8–23:31:21.8 | NASA hosted Apollo 204 Review Board, "Data Analysis", "S-Band Transmissions", https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ | 23:31:21.8 − 23:31:04.7 = 17.1 s; **radio window**, not time of death/ignition. |
| Final transmission garbled; multiple interpretations/speakers not definitive | Same NASA board report, "Voice Transmission" analysis | No definitive quotation or speaker assigned in the email. |
| 100% oxygen at 16.7 psia and combustible material near ignition possibilities | Apollo 204 Review Board, findings 1–2, https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html | Exact specification; stated test conditions, not general flight conditions. |
| Electrical arc most probable; no single ignition source conclusively found | Apollo 204 Review Board finding/determination 1 | Probability expressly distinguished from proof. |
| Inward-opening hatch and inability to open quickly under pressure | NASA's Apollo 1 safety case account, https://sma.nasa.gov/sma-disciplines/accllp/apollo-1 and NASA timeline | Avoids suggesting hatch was single cause. |
| Free, factual CTA | Existing published Final Vestige investigation https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ | One primary destination, no merchant or not-live page. |

## Copy / deliverability constraints
- Maintains original subject **Seventeen seconds. A much longer explanation.** and preheader; no surprise subject switch or urgency.
- Original story-led opening, three original inquiry lenses (clock / conditions / conclusion), a single onsite content CTA, explanatory original NASA references.
- No direct paid links, medical claims, money claims, invented personal usage, or AI visual evidence.
- All legal placeholders intentionally remain unsendable: sender identity, legitimate business address, unsub must be verified in a real Jetpack email.
- WordPress currently reports `email_content_format=excerpt`, new-post automatic emails OFF. Static HTML/plaintext files are editorial-only previews; they are **not Jetpack MIME or proof that the complete edition will be emailed**. Preheader rendering also unverified.
- The WordPress total=2 / confirmed=2 / unconfirmed=2 counters may be consistent since pending confirmations are excluded from total; actual email-eligible recipient count still unknown.
- The offer #03/#05 must remain HOLD_MERCHANT: exact Inspire3 affiliate approval, permission to promote by email, link and guide publishing, current terms not verified.

## CI forensics
The parent #287's GitHub Actions run 41194125156 (job 124516737712) failed with no job steps returned (`steps=[]`) and the job log endpoint reported `404 BlobNotFound`. Run created 10:46:44Z and updated 10:46:49Z (five seconds). Those observations indicate the failure was *very early*, but do **not** prove a GitHub billing, runner, permissions or YAML cause. Do not change shared workflow without runner/UI annotation evidence. Local full campaign tests and deterministic preview regeneration are separately verifiable and must not be described as hosted green.

## Release decision
**ALL SIX HOLD_UNSENT.** Issue 03 and Issue 05 additionally HOLD_MERCHANT. No publishing, sending, test mailing, subscription changes, link activation, merchant contact, live WordPress changes or homepage PR #49 edits. Founder must explicitly approve final campaign before a send.
