# Apollo Experience 2.0 R397 — source-custody + stylesheet-delivery admission

**Review-only; code BUILT, local PHP/Chromium TESTED; NOT installed WordPress, NOT LIVE, NOT verified commerce. Production HARD HOLD.** Proposed additive `experience2/apollo-r397/` alternative staging loader, stacked on R396 (#2688). Never activate R395/R396/R397 together. No main branch, homepage PR #49, Research Desk #158, editorial WordPress content, Grok/Praxxis Drive TASK-008, merchant accounts, analytics or social posts changed.

## Reproduced issue and fix

R396's `fv_r396_records_are_reviewed()` protects nine source data fields but **omits** `context_role`, which appears in the six-record canonical custody ledger. It also allows unexpected extra fields. `qa/reproduce_r396_gap.php` proves the R396 PHP guard accepts a changed context_role and an inserted `affiliate_checkout` attribute. This is a loader acceptance gap, **not proof the original R384 validator or live content is compromised**. The same witness confirms R396's staging eligibility can succeed with already-registered stylesheet handles in a WP stub; actual third-party handle behavior is a WordPress integration risk, not an installed-stage exploit claim.

R397 requires equality of all **ten** ledger fields in each of six ordered records, with no unexpected keys. It explicitly enforces the Board-report link on five questions and NASA's post-fire retrospective on the sixth. It gates prepaint CSS on a true boolean enable flag, WordPress staging environment, approved page slug, entire SHA-256-pinned ledger, exact local base and responsive stylesheet bytes, absence of registered/enqueued handle collisions, and both `plugins_url` results being same-origin HTTPS URLs with a strictly reviewed path shape. It rejects modified hosts, ports, credentials, queries, fragments, encoded traversal and unreviewed stylesheet destinations. Its one-pass delivery decision reuses exactly the validated URLs, rather than querying `plugins_url` twice after validation. It uses PHP 7.4-compatible string operations.

**Remaining engineering limit:** PHP's local file checksum does not authenticate network-delivered stylesheet bytes; real HTTPS responses/redirects/CSP/cache/CDN filters need installed-staging acceptance, with genuine axe-core and independent screen readers. The WordPress stubs simulate WordPress functions; they are not a WordPress installation. URL normalization of the one `../` sibling path must be independently tested with the actual WordPress `plugins_url` filter configuration. Unknown installed paths fail closed.

## Actual executable tests

From the repository checkout:

```sh
php -l experience2/apollo-r397/staging-delivery-guard.php
php experience2/apollo-r397/qa/reproduce_r396_gap.php
php experience2/apollo-r397/qa/contract.php
php experience2/apollo-r397/qa/enable.php
python experience2/apollo-r397/qa/browser.py
python experience2/apollo-r397/qa/package.py
python experience2/apollo-r397/qa/package.py # SHA-256 should be identical
```

PHP exercises every exact field for every record, unlisted commercial attribute, missing retrospective label, wrong chronology/order, no opt-in and explicit opt-in, registered handle collisions, site environment/page, URL filtering and CSS byte identity. Playwright runs **actual headless Chromium** against the reviewed local fixture using `page.set_content`, not browser HTTP navigation. It checks 320–1920px, no-JS, keyboard native disclosures, source navigation, touch, reduced motion, forced colors, fourfold *root font* scaling, print custody, local fixture LCP/CLS observations and overflow. The package locks the local source, test source, screenshots and JSON results with deterministic archive bytes.

**Not tested:** actual installed WordPress/Assembler, real browser HTTP/HTTPS/caching/stylesheet bytes/CSP, independently supplied genuine axe-core, NVDA/VoiceOver, native 400% browser zoom, field Core Web Vitals/INP, exact-head hosted CI or real merchant/paid attribution. Local fixture LCP/CLS are **not** production Web Vitals and cannot be generalized.

## Source and conversion custody

- Five questions reference [1967 NASA Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); the specific original ignition source was not conclusively identified.
- Sixth question references [NASA February 14, 2018 account](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) of **102 deliberate Command Module test ignitions from December 1967 through February 1968** — not evidence of the original 1967 ignition's exact source.
- No NASA image, insignia, third-party archival material or paid CTA is added. [NASA media rules](https://www.nasa.gov/nasa-brand-center/images-and-media/) restrict NASA marks, some third-party imagery, identifiable-person commercial use and implied endorsement; this research does not grant licenses.
- One quiet visitor next step only: `[Read the existing free Apollo 1 investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/)`, after NASA evidence and limitations, not embedded in the fatality narrative. Atlas remains curated text/chronology, with **zero invented geo pins or inferred map edges**.

## Controlled funnel / non-advertising hypothesis

**Grok-owned Apollo long-form, only once a posted immutable asset_id and allowed link are independently verified → NASA-backed Evidence Gallery → free Apollo investigation → independently verified paid educator lesson/dossier, if and only if founder authorizes a real, rights-cleared, checkout-tested SKU.** Primary high-intent segment: 7–12 history/science educators evaluating a source-criticism exercise. Separate free source evidence from optional original pedagogy (timeline analysis, primary-source evaluation and teacher notes); do not repackage NASA public files as proprietary rights.

Hypothesis: more reliable source custody and working mobile disclosure navigation improve reader trust and qualified progression, but **no paid uplift is observed or claimed**. Proposed consent-aware measurement only through Claude's existing/approved instrumentation: unique permitted social `utm_content=asset_id`, `utm_campaign`, qualified-human landing → free CTA → confirmed opt-in if used → merchant-confirmed purchase → gross minus refunds/fees. For 7/30-day cohorts report `net revenue × 1000 / qualified human sessions` only when numerator/denominator are verified; otherwise **NOT COMPUTABLE**, not zero. No new pixel or duplicate tracking script.

### Owner/gate decision

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| One existing FV paid product matched to educators, **not yet authenticated** | Verified paid order | SKU rights, terms, price, fulfillment, refunds, checkout and settled orders unavailable | Founder/Claude independently verify an already sellable product before a purchase CTA | HOLD; no paid sales claimed | Founder / Claude Commerce |
| Grok Apollo film (not confirmed live) | Qualified campaign landing | immutable asset_id, published link and opt-in context unavailable | Praxxis independently review Grok's owned post, Claude assess UTM within existing analytics | UNVERIFIED | Grok / Praxxis / Claude |
| Evidence Gallery | Free article CTA | Source guard accepted altered `context_role` and style handle collisions | Additive read-only guard and adversarial QA | Local PHP/Chromium PASS; WP HTTP/axe pending | Apollo QA / QD |
| One approved educator offer | Paid order → realized net | No verified customers, order/settlement/refund/fee data | Hold paid CTA; reconcile 7/30-day merchant evidence | NOT COMPUTABLE | Founder / Commerce |

**Release gate:** independent QD, actual WP staging with exact HTTP asset digest, browser security, genuine axe, screen-reader/mobile zoom, CI green on exact HEAD, founder explicit approval. No merge/deploy/WordPress updates/paid services.
