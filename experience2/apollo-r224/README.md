# Apollo Experience 2.0 / R224 — retrospective chronology custody (STAGING HOLD)

Isolated child of R223 draft PR #1642 (Apollo Issue #150; commercial priorities #820/#818). No homepage PR #49 edits, no Research Desk PR #158 edits, no production or WordPress writes.

## Implemented

R223 had four dated ChronologyRail stops through January 28, 1967. R224 adds a fifth, **April 1967 (month precision)** for the retrospective Apollo 204 Review Board report, without conflating the January 27 accident with the later investigation. The native no-JS entry links back to the existing SourceDrawer and to the original NASA Review Board, labels uncertainty explicitly, offers a >=44px report-source target and adds no new checkout, geography, JS, tracking or imagery.

New SHA-256-pinned `chronology-report-custody.json` records source/date roles, uncertainty and rights boundaries. Source, URL-crosswalk and HTML mutations fall back safely to the original FREE investigation.

NASA controlling source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — the Board's most probable initiator was an electrical arc; no single ignition source was conclusively identified. NASA advertising/nonendorsement guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . The historical citation does not create promotional rights. No NASA media was added. **April 1967 is month precision, not an asserted day of publication.**

## Exact rebuild / QA

Pinned input R223 distribution manifest: `60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e`.

```bash
python experience2/apollo-r224/build_r224.py --parent /path/to/generated-r223-dist --target /tmp/apollo-r224-dist
python experience2/apollo-r224/qa/chronology_browser_gate.py --parent /path/to/generated-r223-dist --builder experience2/apollo-r224/build_r224.py --out /tmp/apollo-r224-qa
```

Generated R224 manifest SHA-256: `28a393405a86742b190cd7af83518d9d1eac9b3b68882176cc5e7726a5064693`.

Executed source-controlled builder Git blob `047b3bf236267fe2f0f5b659f953f5999ed611eb`; exact source-controlled QA Git blob `0e2cc58b18c625a663982285d7221de41b54fba4`. PHP lint/normal/late fallback and three custody mutations PASS. Two independent Playwright/Chromium runs: 14 contexts per run (7 widths 320–1920 x JS on/off), native keyboard/touch SourceDrawer, in-page report-source navigation, print, simulated CSS zoom 200%, no overflow or unauthorized scripts/geo pins, 14/14 byte-identical screenshot hashes.

**Limitations:** genuine axe-core NOT EXECUTED; screen readers NOT TESTED; actual browser zoom NOT TESTED; HTTP browser navigation blocked by administrator; WordPress/Assembler staging NOT TESTED; hosted CI/QD, R198 ancestry reconciliation and founder authorization OPEN. Local fixture performance is not field CWV. No release.

## Offer → funnel → gate

Audience: history educators and primary-source readers from a **not-yet-verified published Grok Apollo video**. One relevant action stays `Read original investigation` (free, no signup). Proposed educator dossier is NOT a rights-cleared SKU or purchasable offer. Grok owns production/distribution; Praxxis checks creator attribution; Claude owns analytics/commerce; founder approves release. Required metrics remain qualified human sessions by actual published asset ID → article CTA → verified product checkout → independently settled orders/fees/refunds → realized 7/30-day net revenue per 1,000 qualified sessions; all commercial results currently UNKNOWN. No paid CTA, script, affiliate activation, social post, email or spending. **DO NOT MERGE/DEPLOY.**
