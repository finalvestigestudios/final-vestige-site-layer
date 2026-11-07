# EX2 homepage → Focus lead signal integrity | 2026-11-07
**REVIEW-ONLY · NO PUBLISH/INSTALL/MERGE · COMMERCIAL SIGNAL HOLD**

## Scope and exact source
- Parent: draft PR #1407 at commit `d73f04156c645f6169b44598873dec0ce8f4be3f`; frozen #49 unchanged at `10495883299d53596992c26a8987f629b2904670`.
- Read-only WordPress.com API inspected published homepage Page **6** (modified 2026-11-05T12:07:24) and published **/focus/** Page **1579** (modified 2026-11-05T17:44:02).
- Homepage candidate retains seven chapters, 72 Margins and five `https://finalvestige.com/focus/` anchors; source-only CTA testing was completed in #1407. This PR adds **no** candidate markup, instrumentation, offers or production changes.
- Source fixture `focus_gift_source_20261107.json` contains **only** the 587-character `<script id="fvf-gift-v2">` content extracted from Page 1579. SHA-256 of the exact script: `f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7`. No email, cookies, subscriber data, PDF payload or credentials.
- Page 1579 contains a `jetpack/subscriptions` block and separately labels consent for The Dispatch. This establishes the block's presence, **not** form delivery or a confirmed subscriber.

## Verified conversion-signal ambiguity
The published `fvf-gift-v2` client script unhides a PDF download message when `?subscribe=<nonempty value>` is present unless the value is one of five excluded strings. It can also unhide the message based on the container's `is-subscriber` CSS class. **Neither a visible gift message, a query value, nor a PDF click proves Jetpack confirmed a subscriber.**

Repro without any site navigation, form submission, or subscriber creation:

```bash
node experience2/home-flagship/playground/focus_signal_audit.mjs
```

Seven local Node sandbox controls PASS: plain visit (hidden), arbitrary `?subscribe=made_up_value` (visible), invalid_email (hidden), blocked (hidden), `is-subscriber` CSS class (visible), class mutation (visible), and no-JavaScript arbitrary query (hidden). An independently executed JavaScript V8 replay of the **fetched GitHub fixture** also reproduced all seven expected states. These are **exact-script sandbox observations**, not live browser/Jetpack acceptance. Replaying untrusted state does not establish a security breach; the PDF is a free lead magnet and the behavior may be deliberate UX. It does establish that using **download visibility as confirmed lead attribution would be invalid**.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
- **Offer:** free 52-page Seven Day Focus Fieldbook; no merchant conversion claim.
- **Step:** evidence-led homepage → five contextual /focus/ anchors → Jetpack signup → independently confirmed subscriber → later verified paid order.
- **Blocker:** visible success/download state could be mistaken for a confirmed signup, inflating the founder's leading conversion KPI; no authoritative click → confirmed lead → order reconciliation has been demonstrated.
- **Change:** commit a byte-pinned, safe seven-control negative-test artifact and a conversion-acceptance decision. No production script change.
- **Evidence:** script SHA, read-only Page 6 and 1579 WordPress source, seven passing sandbox controls, no forms submitted, no network access.
- **Owner:** Claude for Jetpack/attribution/event semantics (#820); independent QA for test and acceptance; interim homepage for the CTA source path. Grok/Praxxis maintain campaign asset IDs without changing their posting queue.

## Required decision before declaring acquisition/conversion success
1. **Do not** count `?subscribe`, `is-subscriber`, gift visibility, or `focus_pdf_click` as a confirmed email lead. Confirmed Jetpack subscription status is a distinct authoritative observation, if accessible; count unknowns as unknown.
2. Have Claude inspect the actual Jetpack success/error contracts and the intentional immediate-download UX in a private isolated test environment. If the download should be openly available, label it clearly rather than implying a completed signup. If reserved for a successful form action, use an approved authoritative success signal; a client-side query parameter alone is insufficient. The founder must approve any production change.
3. Retain an accessible no-JS signup/download explanation; do not break or replace the 52-page Fieldbook, existing consent, email delivery, and privacy policy.
4. Before marketing claims: read-only actual Jetpack confirmation reconciliation, approved/consented test path, mobile+keyboard+axe check, authorized host-specific QA, verified **paid** orders and fees/refunds. Do not create test subscribers or send marketing without permission.
5. Commercial KPI remains **realized net revenue per 1,000 qualified human sessions**. It cannot be calculated from the present evidence. The 7/30-day cohort and Grok asset_id tagging belongs to #820; no new tracking code here.

## Integration and release status
Source-only browser screenshots in #1407 cannot qualify genuine WordPress/Assembler. WordPress.com Personal has no separate native staging clone. Local Playground runner #1399 remains blocked by unavailable npm/theme hosts; the new fixture does not change that. Actual WordPress QA, axe/WCAG 2.2 AA, host-specific Lighthouse/CWV, real image response bytes, CI and QD on exact SHA, and founder approval are **OPEN**.

**RELEASE DECISION: HOLD.** This finding is for conversion measurement and UX acceptance, not license to rewrite the live Focus page or launch new acquisition links.
