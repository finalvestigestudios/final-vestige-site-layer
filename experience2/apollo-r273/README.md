# Apollo R273 — transparent editorial review custody (DRAFT / HARD HOLD)

Independent Apollo Experience 2.0 staging lane, coordinated in #150 and #820. Parent: R272 PR #1966. Original Research Desk PR #158 and frozen homepage PR #49 are untouched.

## Public trust problem verified 2026-11-10

The existing, public https://finalvestige.com/apollo-1-evidence-atlas/ displays two "Atlas review status: Not yet reviewed." entries: the Apollo 204 Review Board report and the four recorded markers. Its Research Desk separately uses claim-level "verified" badges. Claim-level source checking is not proof that the separate Atlas editorial review has occurred. Do not silently rewrite these public statuses, direct a Grok campaign there as editor-approved, or claim the R273 preview is live.

Read-only capture: public-observation.json. Retrieval was text extraction, NOT a raw HTTP capture, installed WordPress run or production Playwright session.

## Isolated, nonactivating staging improvement

- review-custody.php renders a truthful, accessible two-record source-review disclosure. Missing/invalid review receipts display "Editorial review pending". Even supplied receipt metadata **never** authorizes release: data-fv-review-ready remains false.
- assets/review-custody.css provides dark museum-style, keyboard focus, forced colors, reduced-motion, responsive layout and accessible native HTML details without JS.
- qa/logic_gate.php checks 13 fail-closed states, NASA links, disclosure, no paid URLs, injection-resistant fixed source mapping and unchanged free investigation CTA.
- qa/browser_gate.py invokes actual PHP preview output. It passes 320/390/768/1440/1920px with JS enabled/disabled, keyboard disclosure, Chromium CDP accessibility names, horizontal overflow and deterministic screenshots.
- qa/render.php is a standalone CLI-only preview fixture, NOT a registered WordPress plugin, publishing shortcode or theme hook. No production WordPress, Jetpack, GA or affiliate writes.

Reproduce: php experience2/apollo-r273/qa/logic_gate.php ; python experience2/apollo-r273/qa/browser_gate.py /tmp/r273-qa

**Not tested:** independent axe-core, screen reader, installed WordPress/Assembler, live HTTP/CSP, actual browser UI zoom, field LCP/CLS, exact-head CI, signed editorial review and founder release acceptance. R273 is staged, not published. No sources are commercially endorsed by NASA, and no new NASA asset permissions have been asserted.

## Offer → funnel → blocker → experiment → evidence → owner

| Offer/funnel | Blocker | Experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Disclosed Mini Museum guide → purchase | Affiliate eligibility and paid settlements unverified | Authenticate partner merchant acceptance, orders/refunds/fees | COMMERCIAL HOLD | Founder / Claude |
| Grok Apollo documentary → public Atlas | Published Apollo asset_id and eligible placement not independently verified | Reconcile shared TASK-008; Grok retains posting | UNVERIFIED | Grok / Praxxis |
| Public Atlas → free Apollo investigation | Two "Not yet reviewed" notices on already public page | R273 truthful review-custody preview; editorial signoff before changes | LOCAL TESTED; NOT LIVE | Apollo / Editor |
| Confirmed purchases → net revenue | No authenticated merchant sales or qualified sessions | Compare 7/30-day confirmed cohorts, net revenue/1,000 human sessions | NOT COMPUTABLE | Claude analytics |

Primary official NASA source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

## Release governance

Do not merge or deploy until independent editorial acceptance of each status, rights review, genuine accessibility/WordPress acceptance, CI on final SHA, measurement and approved merchant verification, and founder authorization. No posts, CMS writes, commercial or analytics activations, emails or spending performed.
