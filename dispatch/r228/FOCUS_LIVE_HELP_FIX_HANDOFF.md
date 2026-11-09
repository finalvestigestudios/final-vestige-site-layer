# R228 — Confirmed live repeat-signup instruction, correction proposal ONLY

**REVIEW ONLY; DO NOT CHANGE WORDPRESS.** Owner Claude/Focus Issue #129, Dispatch #174, product rights #171, business #820. Parent R227 PR #1710. No homepage PR #49 changes.

Authenticated WordPress read on November 9, 2026 07:40 UTC: Focus page ID 1579 is published; it still tells a user whose in-app browser failed to open the PDF to open this page in Safari or Chrome and **"sign up again"**. Web text at https://finalvestige.com/focus/ separately reproduces this instruction. The instruction is inappropriate for already-subscribed recipients: it can produce repeated form attempts and confuse lead metrics. This is NOT proof of duplicate stored memberships, broken delivery, or any conversion loss.

**Exact proposal for the two affected help sentences (not applied):**

Some social apps use a built-in browser that may not open PDFs. If your browser cannot open the file, open the **download link in your welcome email** in Safari or Chrome. If you already joined The Dispatch, **do not enter your email again**. A visible download button does not establish that your subscription was confirmed; WordPress subscription status is separate.

Use copy review and a narrowly scoped change, not a page rebuild. The live signup JS has previously been demonstrated to reveal the PDF from browser state; do not treat that as an authenticated provider-confirmed email signup. Correct help copy DOES NOT itself fix client-side state or prove delivery. The existing provider welcome specifies the direct 52-page Focus Fieldbook PDF URL; WordPress media ID 1737 is reportedly the asset. Real mobile direct-PDF requests and inbox receipt remain unverified.

**Acceptance for Claude:** verify current revision, replace only exact paragraph, preserve existing single Jetpack list and other page blocks, confirm no other current edits, test Safari/Chrome/in-app browser with consent-safe dummy states, verify a qualified person can use an already-received download link without resubscribing. Never submit a real email or trigger a test send as part of this request. Include accessibility and reduced-motion/readability checks. The Dispatch /dispatch/ page 523's subscription block is a separate first-time opt-in route; provider-rendered fallback markup is not proof of failure in a real client.

**Native regression:** Python 3.13, 10 tests executed on new isolated source, PASS. The checker only flags specific problematic wording and an explicit false confirmation claim; it is not a general consent auditor, and does not process PII.

**Commercial:** Six manuscript originals and 4:2 pilot split untouched; Issue 03 and 05 must retain merchant-email authorization holds, all six remain unsent. No substitute alternates are approved automatically.
