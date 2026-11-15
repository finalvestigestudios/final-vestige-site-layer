# Apollo Experience 2.0 / R394 — Human-visible proof and 400%-text fit

**Draft-only, no deployment or WordPress writes.** Scope: Apollo QA and candidate CSS, not homepage PR #49, separate Research Desk PR #158, or Grok/Praxxis creator ownership. Base is R393 PR #2669. Coordination: #150, #820, #818.

## Reproduced failures, actual tested source

The R393 staging graph inspector checked text, exact source destination, card geometry, `display`, `visibility`, and `aria-hidden`, but did not check ancestor opacity/clip, offscreen horizontal positioning, keyboard focusability or link pointer access. In real Playwright Chromium loaded from the reviewed local PHP-generated gallery fixture, **12 deliberately concealed/disabled source or CTA cases were accepted by R393 and rejected by R394**. Examples include `opacity:0` on the whole proof gallery, publication link or CTA; blocked NASA link pointer events; inaccessible publisher/CTA keyboard focus; `aria-disabled`; clipped CTA; an offscreen source index; and text hidden with font-size zero. This is an inspector-level enhancement, not an assertion that installed WordPress was actually affected.

At **320px with root font forced to 400%**, the original R384 stylesheet also reproduced **8px of document horizontal overflow**. A separate scoped candidate CSS patch eliminated the overflow in the local fixture without shrinking font size, removing source content or adding JS. This stylesheet is **NOT loaded by the live gallery or the staging harness**; it requires QA/editorial/engineering review and approved integration with the reviewed CSS hash before any staging rollout. Do not silently update the R384 asset checksum.

## Implementation (five files)

- `qa/visibility_custody.py`: read-only DOM inspector; preserves all R393 exact NASA source/topology checks, adds 34 human-visible controls including two publisher links, six source-index links, three rail links, six cards, six native disclosures, six NASA links and the sole free-investigation CTA.
- `qa/staging_gate.py`: R392/R393 compatible staging entry point; verifies inherited harness includes one semantic-verifier call in each JS and no-JS browser context. Fails closed if calls disappear. Same strict URL/HTTPS/GET/HEAD/WebSocket, stylesheet SHA, axe-core pinning, screenshots, output evidence and no-production boundary as inherited harness.
- `qa/test_visibility.py`: actual Chromium (page.set_content) ten contexts 320–1920, no-JS, touch, reduced motion, forced colors, 400% root-font, baseline/after overflow proof, and 12 mutations verified to bypass R393 and fail R394.
- `assets/root4x-overflow-candidate.css`: **candidate only**, not automatically installed, style-scoped to the gallery's mobile layout.
- `qa/package.py`: deterministic fixed-timestamp local evidence ZIP with per-file SHA-256 manifest.

## How to reproduce locally

From the full `final-vestige-site-layer` checkout containing the parent R377, R392 and R393 source:

```sh
python experience2/apollo-r394/qa/test_visibility.py
python experience2/apollo-r394/qa/package.py
```

The fixture used is `experience2/apollo-r393/QA/local-php-fixture.html`, regenerated under existing PHP contract for actual review; the local fixture included in the QA archive matches the reviewed source snapshot, SHA-256 in results. No external network is necessary for the local test.

**Executed in this run:** 85/85 local Chromium assertions; 10/10 contexts; 12/12 deliberate R393 bypasses detected by R394; 400%-root-font overflow reduced **8px -> 0px**. Five screenshots (320, 1440, no-JS, root4x-before and after). Local PerformanceObserver samples recorded per context in JSON; not hosted LCP/CLS or field CWV. Network `page.goto()` to local HTTP was independently attempted and failed with `ERR_BLOCKED_BY_ADMINISTRATOR` in this environment; real network/CSP and installed WordPress remain unverified. Genuine pinned axe-core is **not available** locally; no axe result is claimed.

## Approved staging command (does not authorize it)

```sh
python experience2/apollo-r394/qa/staging_gate.py \
  --url https://APPROVED-STAGING-HOST/apollo/ \
  --approved-staging-host APPROVED-STAGING-HOST \
  --axe-script /reviewed/axe.min.js --axe-sha256 REVIEWED_SHA256 \
  --output-dir /tmp/apollo-r394-readonly
```

**Release HARD HOLD:** approved installed WordPress/Assembler staging, actual browser HTTP/CSP and CSS SHA, reviewed genuine axe-core, independent screen-reader and native browser zoom, exact-HEAD hosted CI, QD and founder authorization. No paid service, media/license claim, invented map pin, WordPress write, production merge, social publishing, commerce modification or tracking installed.

## NASA source and rights

The six evidence questions are supported by only two publications. Original Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . Later 102 *deliberate* Command Module fire tests: NASA retrospective dated February 14, 2018, https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . The tests occurred December 1967–February 1968, after the January 27, 1967 fire; the original specific initiator was not conclusively identified. NASA media guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/ . No imagery or logos are reproduced here and linking is not commercial media licensing or endorsement.

## Conversion-first owner map (hypothesis only)

**Offer:** Apollo classroom evidence kit for history/science educators (a proposed B2B segment in #818, not a verified payable SKU). **Funnel:** Grok-approved Apollo film with inventoried immutable asset_id/UTMs → source-backed Apollo gallery → one free long-form investigation CTA → a separately approved, licensed, real educator kit only after merchant checkout and delivery are verified. **Blocker:** product rights/license, payable SKU, checkout and source-attributed purchase cohort absent. **Change:** R394 guards that human-visible proof and next action aren't silently hidden, plus candidate 400% mobile fit. **Evidence:** local PASS, installed staging NOT TESTED; no lead, order, paid affiliate conversion, net revenue or commercial uplift claimed. **Owner:** Apollo QA for inspector; Claude for website/analytics and merchant; Grok for social and posting; Praxxis for creator QA; founder for release/spending approvals. Key KPI net revenue per 1,000 qualified human sessions and 7/30-day cohorts is **not computable** without qualified sessions, confirmed paid orders and net settlement/refund data.
