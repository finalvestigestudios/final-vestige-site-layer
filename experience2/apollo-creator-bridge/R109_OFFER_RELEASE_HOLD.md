# Apollo R109 — evidence-bound offer preflight (isolated staging only)

**Status:** BUILT + hermetic unit TESTED; genuine merchant acceptance, WordPress/Assembler browser QA, new Playwright/axe/LCP/CLS, release, revenue and Grok publication **NOT VERIFIED**. **HOLD** even when all metadata checks show "reviewed".

## Why this is the next highest-value Apollo task

Business charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818) and canonical conversion/attribution issue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) establish paid orders and realized net revenue as the top priorities. Current isolated [Apollo R108 evidence bridge](./README.md) has an honest free classroom exercise, but **no independently verified matching sellable Payhip SKU**. Adding a buy link or collecting an "interest" event and calling it a customer would manufacture commerce evidence. R109 therefore builds a standalone, **no-network, non-authorizing seller preflight** before touching further page UI.

Files:
- \`offer_preflight.py\`: strict offline JSON contract, HTTPS Payhip canonical product-link syntax validation, audience fit, integer-cents currency check, six explicit source/document review statuses and SHA-256 evidence receipts. Duplicate keys, unknown keys, arbitrary customer/credential fields, query-string tracking, counterfeit Payhip hosts, future review timestamps and missing hashes fail validation.
- \`offer_template.json\`: **synthetic non-operational fixture** with a non-existent/unverified-looking SKU and URL; **do not navigate or reuse** as a production link; illustrative minimum price is **not an advertised or validated price**. Every check is pending.
- \`test_offer_preflight.py\`: 15 standard-library adversarial tests including an intentionally fully self-attested document that still cannot approve checkout or publish.

Running from repository root:
\`\`\`bash
python -m unittest discover -s experience2/apollo-creator-bridge -p test_offer_preflight.py -v
python experience2/apollo-creator-bridge/offer_preflight.py experience2/apollo-creator-bridge/offer_template.json
\`\`\`
The template must output \`STAGING_HOLD_REVIEW_REQUIRED\`, \`metadata_checks: 0\`, six unreviewed requirements, \`can_publish: false\` and \`can_enable_checkout: false\`. \`reviewed\` is only a metadata marker, **not external authentication**. The validator **never** emits an authorization to publish, activate checkout, advertise a price, claim orders or compute revenue.

## Owner-controlled evidence collection, no invented sales

**Claude + Growth/commerce owner** first retrieve seller-origin records for the *actual* matching Apollo teacher SKU: exact canonical Payhip listing, price/currency, individual-rights and original-pedagogy licence chain, tested download fulfillment, refund/terms, known processor fees and settlement status. **Independent editorial/QD** review NASA source custody, the still-provisional crew-photo identity and published post 434's six media images. **Founder** explicitly approves a *separate* exact checkout destination and any promotion; hashes of screenshots or internal notes alone never confer authority. Do not put customer identities, secrets, order receipts, API keys or attribution PII into repo manifests or issues.

**Grok** owns any future long-form/Shorts asset, immutable asset ID, captions and actual distribution; **Praxxis** independently audits that via TASK-008 Drive. Current Grok priority is Rosenhan; Apollo is merely a future concept, not a posted or scheduled asset. **Apollo** owns source-grounded site experience and independent QA, without modifying [frozen homepage PR #49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) or [original Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158).

## One responsible funnel and fail-closed release gate

For future *approved* Apollo long-form audience (educators grades 6–9 interested in primary-source reasoning): **Grok asset ID/UTM → currently published Apollo investigation → optional free evidence exercise → separately verified relevant offer (ONLY after seller/rights/price/fulfillment/founder checks) → Payhip independently confirmed order → refunds/fees → net realized revenue.** No generic Mind/Focus or unrelated product sales button in Apollo history. The R108 page has exactly one contextual primary free-exercise CTA and no merchant link. No new tags/trackers/scripts/forms/lead lists or customer emails.

The decision record to #820 must distinguish qualified human sessions, on-site CTA clicks, confirmed opt-in leads, independently verified paid orders, and refunds/fees. Paid rate and net revenue per 1,000 qualified human sessions are **N/A until both genuine merchant and site denominators are sourced**. Review 7-day/30-day cohorts with tiny-sample warnings and platform attribution limits.

| Priority | OFFER → STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| P0 | Existing relevant Apollo teacher SKU → buyer | Matching sellable product, rights, delivery, accepted terms and price unverified | R109 metadata preflight + *independent* merchant and rights review before any offer URL appears | 15/15 offline tests PASS; **real seller/merchant proof MISSING** | Claude/Growth; founder approval |
| P1 | Free source exercise → qualified resource action | No approved Grok Apollo asset_id or real attributed human campaign | Preserve R108 one contextual free CTA, confirm external campaign identity when proposed | R108 source-contract 21/21 previously passed; **new browser/UTM evidence NOT TESTED** | Apollo QA; Grok/Praxxis |
| P2 | Visit → checkout → paid order | No seller-origin linked order/refund/fee record | Actual checkout/success/delivery and refund path acceptance on governed staging only | **NOT OBSERVABLE**; no revenue claimed | Claude + Site QA |
| P3 | Research trust → visitor relevance | Six NASA photo-specific reuse checks pending; crew portrait ID provisional; post 434 differs | Independent rights/provenance review without copying imagery to paid offer | **HOLD, 0/6 independent clearance** | Apollo/editorial/QD |

## Test scope and release boundary

The 15 local tests and exact GitHub file-blob checks validate **this offline offer contract only**, not real browser accessibility or NASA media rights. New R109 WordPress browser, Playwright, axe, repeated LCP/CLS and hosted Core Web Vitals are **NOT EXECUTED**. R108's previously unexecuted real-browser QA remains the next source-specific task once actual test artifact access/CI runners are reliable. No performance budget was weakened and no synthetic tests are represented as live conversion. Direct checkout tests require merchant permission and founder approval; do not create test customers/orders simply to satisfy engineering.

**STAGING HOLD.** No merge, WordPress production writes, paid services, affiliate activation, customer emails, social posts or frozen homepage changes authorized. Source of truth: Apollo [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).
