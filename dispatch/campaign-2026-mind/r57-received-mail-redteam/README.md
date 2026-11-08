# R57 — Red-team the *received* email proof before anyone trusts it

**STATUS: DRAFT / ALL SIX HOLD_UNSENT / 03 and 05 HOLD_MERCHANT.** This is an isolated Dispatch QA hardening sprint, stacked on **[R56 PR #545](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/545)**, which itself is stacked on the original [six-issue campaign PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) is the Dispatch evidence record; [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) owns product evaluations and first-party pre-sell guides. Do not merge independently into production or touch the frozen homepage PR #49.

## Why this sprint was needed

The previous R56 inspector could **crash when an adversarial .eml contained a malformed IPv6 hyperlink** such as `https://[broken`, because `urlsplit()` raises `ValueError` outside the local seller-domain helper. A deliberately invisible commercial disclosure could also be counted as visible if the email used `opacity:0`, `font-size:0px` or `aria-hidden=" true "`. Finally, the old inspector counted **only visible** HTML anchors as merchant links or unsafe schemes; a hidden, actionable merchant href did not count as an email-route bypass. It overlooked remote image URLs embedded in CSS background properties. These were gaps in a **structural approximation**, not evidence of actual misconduct in any message from Final Vestige. No real received message has been inspected.

The inherited source has now been **surgically patched**, leaving all six canonical newsletter issues, subjects, preheaders, original CTA mix, and commercial hold tokens untouched. The corrections are fail-closed observations, not a promise that parsing the message proves inbox rendering. An actual email client may ignore styles the parser notices or apply external stylesheet rules the parser cannot see.

### Concrete security behavior added

- Malformed URL parsing is exception-safe; an invalid href produces an explicit `MALFORMED_LINK_HUMAN_REVIEW` hold, not a traceback or a logged sensitive URL.
- The scanner now distinguishes **all hrefs** from only **visibly rendered hrefs**: hidden seller/unsafe links still count as potential bypasses, while a hidden unsubscribe anchor does **not** satisfy the visible-opt-out candidate test.
- Conservative visibility checks additionally filter `opacity:0`, `opacity:0.0`, `font-size:0px` or `0%` and whitespace-padded `aria-hidden=true`. A partially transparent element (`opacity:0.5`) is *not* automatically classified invisible.
- External image risk includes ordinary `<img src>` and inline CSS `url(https://...)` backgrounds. These counters never fetch remote resources.
- A new 46-case synthetic unit-test suite probes invalid URLs, malformed unsubscribe anchors, hidden commercial links, invisible disclosures, image loads, sender privacy, source immutability and permanent no-send status.

**Deliberate limitations:** URL and CSS parsing is not a full Gmail/Apple Mail/Outlook rendering engine. Markup candidates do not prove a functional unsubscribe, valid postal address, or an honest actual email sender. Current sender display `Final Vestige` and `no-reply` do not establish authentication, a publisher's physical address or a functioning reply-based opt-out. A parser report is *never* an authorization to send.

## Live source-of-truth checks — 2026-11-02 03:38 UTC (read-only)

Authenticated WordPress site **256784396**:
- Jetpack newsletter ON and technically send-capable; automatic new-post emails OFF; **excerpt** mode; reply-to **no-reply**.
- Welcome template includes the 52-page Seven Day Focus Fieldbook. A configured template does **not** prove actual welcome receipt.
- Aggregates `total=2`, `confirmed=2`, `unconfirmed=2`, `suppressed=0`. [WordPress subscriber guidance](https://wordpress.com/support/subscribers/) explicitly excludes *Not confirmed* from total; these figures **are not additive**. The uniquely consented, email-reachable audience remains **UNKNOWN** until a private admin review of *Email Subscription* and *Not sending (any reason)* statuses. Do not export or reveal addresses.
- `recent_sends=[]` is the diagnostic result for the returned period, **not** proof that no email was ever sent.
- Published [Dispatch](https://finalvestige.com/dispatch/) still emphasizes archive finds and does not mention optional affiliate recommendations near the form; published [Focus](https://finalvestige.com/focus/) has that disclosure. A proposed fix resides in earlier R52 draft PR #517, **not on the live page**. The published [Editorial Standards](https://finalvestige.com/editorial-standards/) require evidence discipline, independent editorial conclusions, and disclosures.

### Named-product copy verification, not a revenue authorization

The actual [Zen12 official offer page](https://zen12.com/hnp) describes 12-minute recordings, 12 levels, four listening modes and tier-dependent packages. Its assertion that a 12-minute track supplies an hour's meditation benefits and automatically produces brainwave or personal outcomes remains **seller advertising**, not product-specific independent proof. No Final Vestige-specific partner acceptance, **email-channel** permission, approved earning link or current checked-out price/refund enforcement has been verified.

The official [Total Focus product page](https://hypnosislive.com/mental-skills/total-focus) describes a **33-minute, 47-MB** recording and promises striking concentration gains. The live page inspected November 2 UTC showed **$2 and $29.95 price points** while an older search-indexed capture showed **different $17.95/$22.95 figures**. This is evidence of **price/capture variation**, not proof of current completed checkout, a stable discount, market price, regional rules, or a price Final Vestige may advertise. The site also **states** a 14-day refund policy; the applicable final buyer terms and enforcement remain unverified. Neither recording should be sold in the newsletter as independently demonstrated to alter focus. Both Issues 03 and 05 remain on merchant hold, and their first-party guide CTAs still lack approved published destinations. Do **not** insert prices into email copy.

Public [Inspire3 affiliate recruitment](https://affiliates.inspire3.com/) is not documentary approval for Final Vestige, nor email-specific creative or tracking rights. Other-product [Limitless Labs promotional material](https://inspire3.com/ll/) does not confer rights to Zen12 or Total Focus.

Relevant official compliance standard: [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). A valid business **physical postal address**, clear ad identification when appropriate, accurate sender and subject, effective opt-out, and compliant opt-out handling cannot be inferred from a self-validating repository test. An ESP's or product merchant's address does **not** substitute for Final Vestige's address.

## Execution and evidence-chain instructions

```bash
# On the exact R57 branch/commit, never the default branch or a synthetic merge ref:
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v

# Separate targeted adversarial set; all inputs are generated locally:
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r57_mime_redteam.py -v
```

Never inspect a real `.eml` without **separately obtained founder authorization** for that specific read, using the existing [R56 private MIME handoff](../r56-mime-evidence/README.md). Do **not** commit any raw email, subscriber address, opt-out token, postal string or sender account secret. Never fetch links while inspecting or test real opt-out functionality without separate authorization. A caller may supply `--source received` but that operator label is **not independent attestation**.

### Proof boundary and remaining blockers

This sprint can produce honest evidence that the parser behaves conservatively against synthetic adversarial samples. It cannot produce genuine Jetpack inbox evidence or legal clearance. Require **(1)** authorized native post-level preview with send checkbox restored OFF immediately, **(2)** separately approved received test MIME, **(3)** Final Vestige's valid actual business postal address, **(4)** visible and functionally verified unsubscribe in received commercial mail, **(5)** privately reconciled distinct eligible audience, **(6)** approved first-party published guide pages, **(7)** written named-product EMAIL promotion permissions and approved tracked earning URLs, **(8)** exact edition, recipient audience and send date founder authorization.

The static reviewer `review.html` is intentionally standalone and non-executing. The structured `observed-evidence.json` is a **read-only decision snapshot**, not live authority or a supplier terms contract. No sends, test-sends, CMS writes, publisher address guesses, new subscriptions, imports, tracker activation, partner contact or WordPress toggles were performed. The original four editorial / two conditional commercial schedule is preserved without publication dates.
