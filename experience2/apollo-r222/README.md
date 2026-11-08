# Apollo R222 — native NASA source drawer (STAGING HOLD)

**Isolated child of Apollo R221 draft PR #1630. Not approved for installation, merge, publication, analytics, affiliate activation or spending.** Relates to Issue #150, revenue governance #820 / charter #818. Does not touch homepage PR #49 or Research Desk PR #158.

## What changed

The source-controlled `build_r222.py` creates a distinct R222 shortcode adapter, HTML fragment, scoped CSS and machine-readable SourceDrawer custody ledger from the **SHA-pinned R217 staging artifact**. Four native HTML `<details>` records now sit immediately between the technical claim trail and the one free original-investigation link. Each record identifies evidence type, date, independently verifiable NASA source URL, what the source can establish and a limitation. Records: Apollo 204 Review Board, S66-58038, S67-15717, S67-21294. No invented coordinates or new photography, JavaScript, registration form or commercial CTA.

The resulting PHP adapter verifies the modified fragment/style and new ledger by SHA-256. Corrupted source records trigger an existing safe fallback to the **free** original investigation. The disclosure uses browser-native keyboard/touch interaction even with JavaScript disabled; existing printable NASA source custody is preserved.

NASA technical source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — most probable electrical arc; **no single source conclusively identified**. NASA media/endorsement rules are separately controlled by https://www.nasa.gov/nasa-brand-center/ . Citations do not confer advertising rights.

## Reproduce locally, without publishing

Provide the exact R217 `dist/` generated artifact from the pinned Apollo ancestry. The builder rejects a nonmatching parent manifest, HTML or stylesheet. Commands:

```sh
python experience2/apollo-r222/build_r222.py --parent /path/to/r217/dist --target /tmp/fv-apollo-r222/dist
python experience2/apollo-r222/qa/source_drawer_browser_gate.py --parent /path/to/r217/dist --builder experience2/apollo-r222/build_r222.py --out /tmp/fv-apollo-r222/qa
```

Requires Python Playwright, PHP and system Chromium at `/usr/bin/chromium`. No network needed or permitted by the test. Test generates the source-controlled implementation from pinned parent inputs, verifies every output hash, exercises normal/printed/late PHP shim paths and source-record corruption fallback, then uses real Chromium for JS ON/OFF, 320/360/390/768/1024/1440/1920 widths, touch/keyboard disclosure, print-custody availability, forced colors, reduced motion and eight hostile DOM mutations. Screenshot hashes should match independently generated runs.

**Verified locally on November 8, 2026:** 14/14 Chromium contexts **twice**, 8/8 negative controls **twice**, 14/14 screenshots byte-identical between runs. Exact GitHub source parity should be checked independently against the executed source. Output manifest SHA-256: `a4fc40dc270684686a879183a7e417bfb6e1d05a40e4e819fed603dc45d130a5`. PHP lint passes. Local PerformanceObserver LCP: approximately 88–100 ms for JS-enabled offline fixtures. Drawer-open layout shifts were user-initiated; **not field CWV**. No axe-core or installed WordPress acceptance was performed.

## Revenue priority and release blockers

**Offer → funnel → blocker → proposed next action → evidence → owner:**

| Offer / funnel step | Blocker | Next controlled action | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Proposed Apollo educator dossier → paid order | No approved rights-cleared sellable SKU, merchant acceptance, delivery or price | Validate real offer before any commercial CTA | HOLD | Founder / Commerce / Claude |
| Grok Apollo long-form → qualified Atlas session | No authenticated published Apollo asset ID / URL | Reconcile TASK-008 without overwriting creator queue | UNVERIFIED | Grok / Praxxis |
| NASA Atlas → free original investigation | Source identity and limitation require usable verification route | Native SourceDrawer before one free CTA | LOCAL PASS ONLY | Apollo |
| Confirmed orders → realized net revenue | No verified customer sessions, orders, refunds or fees | Governed 7/30-day merchant and privacy-safe cohort reconciliation | NOT COMPUTABLE | Analytics / Commerce |

This component is a **trust-and-reading bridge**, not proof of conversion. Product remains a hypothesis. Core free research is never conditional on payment. Do not measure social views or outbound clicks as paid orders.

**Release HOLD:** R198 ancestral source discrepancy, exact hosted CI, installed WordPress/Assembler, genuine axe-core, NVDA/VoiceOver, physical browser zoom, actual external link navigation, field CWV, independent QA and founder signoff. No production writes, social posts, emails, paid services or speculative map pins.