# Apollo R351 — Source fallback quarantine and independent HTTP/browser QA

**DRAFT / STAGING RESEARCH / NOT LIVE.** Stacked on R350 PR #2424, base commit b303fdc0a1d8c3b8e2e59fc3c57b426dce52b490. Issues #150, #820 and #818. No changes to frozen homepage PR #49, Research Desk PR #158, Grok/Praxxis TASK-008 or Claude's production engineering.

## Defect addressed

R350 protected the links paired with 13 reviewed editorial records, but the empty-data fallbacks in R347 Source Index and R348 Source Custody still contained unconditional, direct NASA HTML anchors. When a required record module was unavailable, those links bypassed the reviewed source-custody policy. R351 removes the bypass: historical context remains readable and a review-required message appears, without an unverified source link. It does not indicate NASA's original reports are unreliable. The one existing free editorial continuation remains unchanged.

Healthy rendering still identifies 13 evidence references across eight distinct NASA pages, NOT 13 independent documents. There are no new NASA photographs, source-rights claims, geo pins, analytics, affiliate links, purchases or other commerce.

## Reproducible checks

From repository root with PHP, Python Playwright and Chromium:

    php -l experience2/apollo-r347/source-index.php
    php -l experience2/apollo-r348/source-custody.php
    php -l experience2/apollo-r351/qa/http_entry.php
    python experience2/apollo-r351/qa/check.py
    php experience2/apollo-r349/qa/preflight.php
    python experience2/apollo-r350/qa/test.py
    python experience2/apollo-r350/qa/regression.py

R351 copies the candidate into an ephemeral directory and removes first a chronology module and then the Source Index, proving missing-source fallbacks withhold all NASA hrefs. A local PHP HTTP server produces real response headers checked by Python urllib, including CSP without unsafe-inline scripts and nosniff. Server-rendered content retains exactly one free-investigation continuation.

**Browser HTTP/CSP not verified:** this environment denies Chromium navigation to localhost and mocked domains (ERR_BLOCKED_BY_ADMINISTRATOR), including intercepted navigation. Playwright checks therefore inject equivalent PHP-rendered HTML and local CSS/JS through set_content. This is valid real Chromium DOM/keyboard/touch/no-JS/print testing but NOT browser enforcement of HTTP/CSP or installed WordPress acceptance. Contexts: 320px with 400% root text, 390px no JS, 768px touch, 1440px and 1920px. Outputs under QA include screenshots, PDF and JSON. No genuine axe-core, Firefox/WebKit or independent screen reader was executed.

## Release gates

Installed WordPress/Assembler/Jetpack/reusable-block and CDN acceptance, browser HTTP/CSP transport, independent accessibility, hosted CI at exact HEAD, NASA media/likeness/third-party rights check, editorial review, published Grok asset ID, verified rights-cleared payable educational SKU and founder/QD release permission remain open.

## Conversion-first experiment

Audience: evidence-oriented viewers of a Grok-produced Apollo 1 long-form film. Path: authorized documentary → NASA Evidence Atlas → one existing free Apollo 1 investigation → separate, approved educator offer ONLY after authentication. Hypothesis: visible custody and graceful failure reduce trust friction; commercial impact unmeasured.

| OFFER | FUNNEL | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Apollo educator evidence product | Paid order | Payable, rights-cleared SKU and checkout unverified | Hold purchase CTA; verify fulfillment, payment, rights | BLOCKED | Founder / Claude |
| Grok Apollo documentary | Qualified landing | Published asset ID and landing URL unverified | Coordinate URL/UTM mapping through TASK-008 | UNKNOWN | Grok / Praxxis |
| Existing free investigation | Evidence-to-editorial | Empty-source fallbacks bypassed custody | Quarantine fallback links, preserve editorial action | LOCAL PASS; no uplift measured | Apollo |
| Settled merchant purchase | Net revenue/1,000 qualified sessions | Sessions, paid orders, refunds, fees not reconciled | Consent-aware #820 measurement contract, no duplicate scripts | NOT COMPUTABLE | Claude / Commerce |

No unapproved live changes, postings, email, spending or payment activation.