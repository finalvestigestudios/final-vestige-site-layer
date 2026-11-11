# Apollo R274 — review custody multi-instance hardening

**Staging only / no WordPress hook / NOT LIVE.** Owner: Apollo Evidence Studio. Coordination: #150 / #820.

## Corrected defects

- The original R273 component emitted the same heading id/ARIA reference when called repeatedly. R274 keeps the original ID on the first panel and uses numbered unique IDs for following instances. It never treats metadata as production release permission.
- Two different NASA source rows previously exposed identical link names to keyboard/screen-reader users. Each link now includes the actual source-row label.
- A syntactically formatted but impossible review date could previously be treated as a *supplied* (not authenticated) receipt. R274 validates calendar dates. Receipt identifiers are still unverified and cannot authorize deployment.

## Source custody

The only NASA source URL used by these two records is https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Review Board identifies electrical arcing as the most probable initiator but no single ignition source conclusively. NASA commercial policy: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . A source link is not commercial-rights clearance. The public https://finalvestige.com/apollo-1-evidence-atlas/ currently shows two distinct **Not yet reviewed** Atlas notices; source-checked claims elsewhere on that page do not sign off Atlas editorial review. Do not silently change those live statuses.

## Reproduce

```sh
php experience2/apollo-r273/qa/logic_gate.php
php experience2/apollo-r274/qa/logic_gate.php
python experience2/apollo-r274/qa/browser_gate.py /tmp/apollo-r274-qa
```

Test outputs: R273 PHP 13/13, R274 PHP 15/15, actual offline Chromium Playwright 10/10 JS/no-JS contexts (320,390,768,1440,1920), plus 5/5 400% root-font/forced-colors/touch/reduced-motion contexts. Browser validates distinct IDs, ARIA references, named source links, native disclosure, links, no commercial link, no network requests, no horizontal overflow, screenshot hashes. The three-instance fixture uses the **actual** R273 PHP. A negative control with the old original PHP demonstrated duplicate IDs; corrected output has unique IDs.

**Not tested:** genuine axe-core (no verified bundle), installed WordPress/Assembler, independent screen reader, actual browser UI zoom, HTTP/CSP, field LCP/CLS, exact-head hosted CI, merchant acceptance or founder release approval. Local HTTP navigation was blocked by administrator networking policy. No field CWV claim.

## Business gate — separate from historical evidence

Proposed route: verified Grok Apollo asset → Atlas → original free investigation → optional, separately disclosed Mini Museum guide → independently verified merchant sale. This component adds **no commercial CTA** and no tracking. Offer eligibility, Grok asset ID, qualified human sessions, authenticated orders, settlement/fees/refunds and realized net revenue all remain unverified. No paid conversion can be inferred from clicks.

| OFFER → FUNNEL | BLOCKER | EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Mini Museum guide → paid order | Affiliate status and settlement unknown | Authenticate merchant records | HOLD | Founder / Claude |
| Grok documentary → Atlas | Published asset_id unknown | Reconcile TASK-008 | UNVERIFIED | Grok / Praxxis |
| Atlas → free investigation | Duplicate IDs and ambiguous source links | R274 browser/PHP regression | LOCAL PASS | Apollo |
| Orders → net revenue / 1k humans | Transactions and qualified sessions missing | Existing analytics 7/30-day cohorts | NOT COMPUTABLE | Claude |

Homepage PR #49 and original Research Desk PR #158 untouched. No deployment, new vendor, WordPress content/settings change, posting or email. Founder approval and independent QA required.
