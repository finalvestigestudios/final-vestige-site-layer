# Dispatch R381 — exact-source QA and no-send release verdict

**Review time:** 2026-11-15 07:31–08:00 PT (current automation run). **Owner:** Dispatch #174, merchant coordination #171. New optional Issue 03 is NOT_ADOPTED. Base draft #2631 exact parent SHA `8905ab971df0b088dede4410ab78e76f83088ede`. Do not merge into frozen homepage PR #49.

## Ordered source-of-truth reads
1. GitHub Issue #174 and latest comments, #171 and latest Mind R400 response, original six-edit master draft PR #175 and verification guard PR #201. Stacked parent PR #2631 inspected before branch creation.
2. Authenticated WordPress `wpcom_jetpack_newsletter.status` (2026-11-15T15:32:59Z) and `get_settings` (15:33:00Z). Newsletter enabled, site can send, auto-post-email OFF, full text, from Final Vestige Studios, no-reply, actual configured 52-page Fieldbook welcome. Five recent post notifications have `never_sent_opted_out` statuses; **not** a lifetime zero-send audit. `total=3, confirmed=3, unconfirmed=2` are not additive and do not define 5 recipients. Actual unique receiving inbox count UNKNOWN.
3. Live WordPress /dispatch/ page 523, /focus/ page 1579 and Editorial Standards page 17 read-only. /focus/ contains original Jetpack signup, 52-page PDF link and script showing gift panel on client query/class state. A gift panel is not evidence of confirmed consent.
4. Existing Grok/Praxxis TASK-008 and coordination Drive documents read-only; no social asset IDs or production tasks reassigned.
5. Targeted connected Gmail lookups for actual affiliate acceptance/product-specific EMAIL permission and Fieldbook welcome. One October 25 WordPress confirmation message found; **not** receipt of welcome and not a merchant approval. No positive named affiliate EMAIL rights surfaced; searching is not proof that no agreement exists.
6. Direct seller https://zen12.com/ and https://zen12.com/getstarted, official NIH https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety , digitized 1890 James source https://psychclassics.yorku.ca/James/Principles/prin11.htm , FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business , WordPress https://wordpress.com/support/newsletter/email-appearance/ .

## Independently executed first-mile original suite **before new content**
Master PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` unchanged. Eight manuscript/manifest/Python-test files compared by `git hash-object` against exact live GitHub Git blob SHA: **8/8 MATCH**. Mounted R372 archive supplied the local bytes and was not trusted before SHA matching. Native Python `python3 -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v`: **6 tests PASS, 0 failures**. This confirms exact campaign contents, not the entire branch graph.

## New code and reviewer QA
- **29/29 directly executed V8 reference cases PASS** on the *same function declarations* emitted to `proof_gate.mjs`. Cases exercised fail-closed release, the distinct Apollo 1 source gate, 03/05 SKU/EMAIL/guide gates, bad attestations, provider-only signup deduplication, non-email Reader/PDF exclusion, unknown recipients, revenue missing/zero denominator and duplicate/refunded/unfinalized orders.
- **21/21 in-runtime static checks PASS** against nine exact source files freshly fetched from GitHub **after writing**: source links; 4:2 slot mix; all six original HOLD statuses; all-false attestations; legitimate WordPress count interpretation; unknown eligible inboxes; null net revenue; no hidden active affiliate CTA; disabled offer/disclosure; HTML `lang`, responsive max-width table, no `<script>`, `<form>`, `<iframe>`, `<img>` (no pixel or third-party scripts); no deceptive seller-as-proof language.
- Each of nine new files had a nonempty 40-character Git blob SHA returned from GitHub. All new source files located under `dispatch/r381/`; original letters, site, other agents' materials and frozen PR #49 left untouched.
- **Committed `test_proof_gate.mjs` is authored but has NOT been executed with native Node**; the 29 V8 cases above are direct in-runtime tests, not a substitute for native Node, browser or hosted CI. **No Jetpack Preview email, Send test email, received welcome, actual opt-out test, real merchant checkout or paid conversion test was run.** No invented A/B/click/revenue.

## High-priority conversion-first decision record
| OFFER → FUNNEL | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL | OWNER |
|---|---|---|---|---|
| Zen12 → optional issue03 → Mind buyer guide → paid commission | No named publisher acceptance, SKU EMAIL rights, affiliate earning URL, approved live guide or referred checkout | Source-led, no-pressure optional copy + free baseline; one **disabled** guide CTA and adjacent disclosure | **HOLD_MERCHANT** / copy reviewer PASS, buyer path NOT LIVE | Mind Studio / Commerce / founder |
| Focus → provider confirmed signup | `?subscribe=unconfirmed` and visible PDF not confirmation; confirmed count not equal receiving inboxes | Only provider-authoritative `confirmed_signup_v1`, dedup opaque ID | Contract offline PASS; real integration UNKNOWN | Claude / Focus |
| Welcome → active reader | Configured welcome is not received welcome | Private permitted receipt/PDF acceptance | UNVERIFIED; no actual test send | Focus / founder |
| Dispatch → compliant inbox | Unknown native subject/preheader, qualifying postal address and functional unsubscribe | Native **Preview email** read-only when available, later separately authorized receipt/opt-out | NOT TESTED; no email sent | Dispatch / founder |
| Grok source → qualified reader → merchant settlement | No independent real asset IDs, qualified-human sessions, settled orders, fees/refunds | Join privacy-safe 7/30-day cohorts using existing first-party instrumentation | Customer retail checkout price is never counted as Final Vestige revenue; no real data; net revenue per 1k **NOT COMPUTABLE**, not zero | Grok/Praxxis; Claude/Commerce |

## Founder release gates still closed
All six original editions `HOLD_UNSENT`; 03/05 `HOLD_MERCHANT`; 04 `HOLD_COPY`; R381 optional 03 `NOT_ADOPTED`. Founder has authorized draft production ONLY, not contact or send. Need real provider consent, correctly rendered business footer/opt-out, native email preview, merchant account/email rights, live independent guide, actual checkout, and final approval. Until then no broadcast, no test message, no WordPress writes, no paid service, no links activated, no merge/deploy.

No email addresses, business secrets, subscriber PII or tracking tokens included.
