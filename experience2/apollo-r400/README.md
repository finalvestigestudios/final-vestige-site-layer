# Apollo Experience 2.0 R400 — read-only installed-staging browser QA (DRAFT / HARD HOLD)

**Isolated QA-only work under `experience2/apollo-r400/`.** Stacked exclusively on R399 #2704. Does not edit homepage PR #49, Research Desk #158, other Apollo source/loader files, WordPress content/settings, analytics, Grok/Praxxis TASK-008, merchant pages, social or email. No merge or deployment approved.

## Why this sprint exists

R399 runs meaningful native-PHP stubs and real Chromium via `page.set_content`, but those **do not verify installed WordPress**, actual delivered stylesheet bytes, response CSP, HTTPS redirects or genuine axe-core. R400 adds a separately invokable browser acceptance runner that **defaults to doing nothing** until a fixture or a specifically approved staging URL is provided. This is QA tooling, not a live visitor experience or staging installation.

Its browser interception rejects all non-GET/HEAD methods, hosts outside the one expressly authorized HTTPS staging origin, redirects, and attempted WebSocket requests. It blocks service workers and downloads, validates two reviewed canonical CSS responses against fixed SHA-256 digests, and requires a delivered CSP header. Its DOM gate checks six Apollo evidence cards, six NASA source citations, two *distinct* NASA publisher links, three chronology destinations, six keyboard/touch-native disclosure controls, exactly one free-investigation CTA and zero horizontal overflow at 320–1920 px. It saves deterministic-named Chromium screenshots and sanitized JSON receipts (no query tokens in reports).

**Cautions:** a read-only browser client cannot certify server-side behavior on GET routes; staging server policy must separately prohibit mutations. This gate may intentionally HOLD when a required WordPress asset, CSP header or authentic axe-core resource is missing. The local sandbox may block network navigation; `ERR_BLOCKED_BY_ADMINISTRATOR` is a blocker, never a successful staging acceptance. The harness does not replace independent NVDA/VoiceOver, native 400% browser zoom, QD, hosted exact-head CI, or founder release approval. It cannot by itself verify human qualification, orders or revenue.

## Reproduction

```bash
python -m unittest discover -s experience2/apollo-r400/qa -p 'test_gate.py' -v
python experience2/apollo-r400/qa/staging_browser_gate.py \
  --fixture experience2/apollo-r393/QA/local-php-fixture.html \
  --out experience2/apollo-r400/QA
```

The second command is **fixture-only**. It must report `PASS_LOCAL_FIXTURE_ONLY`, not staging. Local companion evidence: 7 browser contexts passed on the reviewed PHP-generated fixture; genuine axe-core was not available to run, CSP and HTTP stylesheet bytes were not tested. The Python guard/unit tests were executed on a **locally authored equivalent implementation**, not on GitHub's byte-identical committed Python source; exact-head CLI/CI remains an explicit release blocker.

## Future approved staging-only command (not executed)

```bash
python experience2/apollo-r400/qa/staging_browser_gate.py \
  --url https://APPROVED-STAGING-HOST/apollo-1-evidence-atlas/ \
  --host APPROVED-STAGING-HOST \
  --axe /independently-reviewed/axe.min.js \
  --axe-sha256 INDEPENDENTLY_VERIFIED_EXACT_SHA256 \
  --out experience2/apollo-r400/QA/installed-staging
```

Do not substitute a guessed staging URL. The authentic axe-core file must be independently obtained, licensed, reviewed and SHA-256 pinned; placeholder or fake axe is not acceptable. No unreviewed staging activation or paid service is authorized.

## Provenance, rights and one conversion path

Five evidence questions point to the [1967 NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); the last points to [NASA's later flammability tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/). The Board found a probable electrical arc but did not conclusively identify the particular ignition source. The later 102 deliberate tests were *not* the original 1967 fire. No NASA photograph, logo, invented Atlas map pin or speculative relationship was added. Archive hosting does not license a commercial image or imply endorsement.

Candidate, **not launched**: independently verified Grok-posted Apollo long-form asset → provenance-led gallery → the [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) (the only page CTA) → optionally later, after rights, educator demand, checkout and fulfillment verification, an approved teacher evidence kit. Grok owns content and posting, Praxxis independently reviews creator material; Claude owns merchant and attribution implementation; founder controls production and release. No actual Grok post URL, unique asset_id, qualified human sessions, paid merchant orders, refunds or fees were independently supplied; **realized net revenue per 1,000 qualified humans cannot be computed**.

| Offer → step | Blocker | Change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Rights-cleared teacher kit → purchase | Sellable SKU/checkout/delivery/rights not verified | Withhold paid CTA | HOLD; no claim of orders | Founder / Claude |
| Grok documentary → qualified landing | Published asset ID/UTM not verified | One relevant creator-to-gallery candidate | UNKNOWN | Grok / Praxxis |
| NASA gallery → free investigation | Installed WordPress/browser acceptance missing | R400 default-off GET-only staging QA | Local fixture PASS; installed staging HOLD | Apollo QA / QD |
| Confirmed sales → net revenue | Merchant settlement, refunds, fees and 7/30-day human cohorts missing | Use existing #820 attribution contract; no duplicate scripts | NOT COMPUTABLE | Claude / Commerce |

Follow [Apollo issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [commercial measurement #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), and [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). **Release HARD HOLD**, with QD, installed staging, genuine axe, independent screen readers, performance, hosted CI and founder signoff outstanding.