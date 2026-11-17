# Apollo R431 — source-custodied evidence notebook (DRAFT / HARD HOLD)

**Ownership:** independent Experience 2.0 Apollo issue [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); cross-reference conversion program [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business charter #818. Creator TASK-008 remains Grok/Praxxis owned. No change to frozen homepage PR #49, homepage branches, Research Desk PR #158, or their release queue.

## New source-controlled implementation

Opt-in staging-only shortcode: `[fv_apollo_evidence_notebook_r431]`. Requires `FV_R431_ENABLED === true` and an **integer** `FV_R431_STAGING_PAGE_ID` equal to the current queried page ID, plus WordPress environment `staging`. Otherwise the shortcode emits a **plain link to the existing free Apollo investigation**. Never enable this plugin in production or add to existing WP pages without governance.

The notebook **uses the actual unmodified R430 worksheet**, which in turn verifies and renders the actual R429 NASA evidence chronology. R431 checks these two reviewed R430 Git blob identities before requiring source, and R430 verifies R429 identities:

- `experience2/apollo-r430/staging-educator-case-lab.php`: `11a30d871bb0c5840aa3ee8932e12a6068b50cd3`
- `experience2/apollo-r430/assets/educator-case-lab.css`: `be6880577faed2453f5633a3718fce8dedf9ac3b`
- inherited R429 PHP: `c604bccf9873688ec1d9b64187d1a9a7fdcf89ac`
- inherited R429 CSS: `15942f8ef27d82695c8d2af8bdc8a807396da33e`

Rejects missing, changed or symlinked source and preloaded untrusted parent render functions; drops gracefully to the original free article. No additional NASA images, unverified location pins, speculative map edges, new content claims, third-party analytics, emails, forms, account creation or paid merchant links.

**User experience:** the three cited educator prompts are readable and printable with JavaScript disabled. On successful JS enhancement, users can count draft answers, copy cited notes via the browser's clipboard (with denied/unavailable fallback), save only **on demand** an original `.txt` notebook that includes their answers, the actual questions and three official NASA source links, and print filled answers using a print-only text mirror. No data is submitted, cookie-tracked, persisted to localStorage, or silently transmitted to the website. The download and OS clipboard/print functions are user-initiated; remind users that resulting local artifacts may persist on their device.

Source custody and chronology: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (exact spark not conclusively identified, electrical arc most probable); [NASA 2018 flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) (102 **later** deliberate ignitions in Dec 1967–Feb 1968); [NASA media/brand guidance](https://www.nasa.gov/nasa-brand-center/). This is **not** a NASA-endorsed or commercially licensed NASA-media product.

## Reproducible local tests

Start from a complete checkout of exact R430 base `d4544e42c043958832ba292ac0bdc0bac5b35fc6`, plus this new directory. Dependencies: PHP CLI, Python 3, Playwright Python and `/usr/bin/chromium` (same tooling as prior Apollo R&D). Run:

```sh
php -l experience2/apollo-r431/staging-evidence-notebook.php
python experience2/apollo-r431/qa/test_contract.py
python experience2/apollo-r431/qa/browser_qa.py
python experience2/apollo-r431/qa/package_evidence.py
```

`test_contract.py` checks exact source blobs, release gate, source claims, link count, input controls, mutation and symlink rejection. `browser_qa.py` first attempts **real loopback HTTP navigation**; in this runtime Chromium returned `ERR_BLOCKED_BY_ADMINISTRATOR`. It therefore tests the **actual inherited PHP-rendered HTML** offline with `page.set_content`: widths 320, 360, 390, 768, 1024, 1440, 1920, multiple instances, keyboard, touch, no-JS, 200% text, forced colors, reduced motion, print mirrors, live counter, `.txt` download, simulated clipboard success and unavailable fallback. Offline screenshot/DOM tests are **not** installed WordPress staging, genuine page navigation, axe-core, navigated LCP/CLS, or field Core Web Vitals. `package_evidence.py` makes timestamp-zeroed, sorted-path, deterministic ZIP and source hashes; CI on the committed SHA remains a separate gate.

To conduct genuine installed WordPress staging QA, run `qa/staging_acceptance.py` with **founder-approved exact HTTPS staging URL/host** and a **locally reviewed SHA-256-pinned axe-core source file**, capture real navigation, axe and local lab LCP/CLS. Script FAILS CLOSED if conditions are missing. Independently validate keyboard/touch/screen readers and QD on exact GitHub HEAD. Field p75 requires real-user eligible measurement, not one Playwright run.

## Conversion-first plan (not a claim of success)

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Original Apollo educator lesson kit (candidate, **not approved sellable SKU**) | educator → paid order | verified IP/rights, price, checkout, fulfillment and settlements absent | no paid CTA until true verification | HOLD: no sale evidence | Founder + Claude |
| Grok-approved Apollo long-form | published asset → qualified page visit | actual post URL, immutable `asset_id` and qualified human session attribution unverified | inherit exact allowlisted R429 UTM only when provided; don't invent IDs | R429 contract source-tested, **NO attributed sessions** | Grok + Praxxis + Claude |
| Free Evidence Atlas → original investigation | research → trusted next step | visitor needs reusable source-grounded notes | R431 private cited notebook with one inherited free article CTA | PHP/local Chromium PASS; WP staging HOLD | Apollo QA + independent QD |
| Confirmed customers | paid order → net realized revenue per 1,000 qualified sessions | receipts, fees, refunds, CRM and qualified denominators missing | cohort scorecard once first-party/merchant receipts are verified | NOT COMPUTABLE, no simulated commercial success | Claude + Commerce |

Single relevant visitor path: **approved Grok Apollo film → source-backed free Research Desk/Evidence Atlas → notebook → existing full free investigation → founder-approved original paid educator product if and only if verified**. This is a hypothesis about high-intent educators, not a claim of commerce. Do not insert an unrelated affiliate link into the archival narrative.

## Strict remaining gates

- Existing R417 source/archive discrepancy unresolved; QD reconciliation needed.
- Exact staging HTTPS host and approved axe-core unavailable in this execution environment; independent axe WCAG 2.2 AA, keyboard, touch, screen-reader and local navigated LCP/CLS **NOT PASS**.
- Exact-head CI and independent QD review unverified; no release or merge.
- No confirmed Grok post or attributed human sessions, verified Payhip paid SKU, merchant-confirmed affiliate conversion, or realized net revenue.
- No approval to deploy, edit WordPress, publish social posts, send email, modify measurement scripts or spend.
