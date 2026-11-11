# Apollo R282 — review-custody digest and interactive NASA source catalogue

**DRAFT / STAGING ONLY / HARD HOLD**. Stacked on R281 draft PR #2024 and independent of frozen homepage PR #49, Research Desk PR #158, and production WordPress. Source-of-truth engineering issue #150; conversion coordination #820 and business charter #818.

## Scope and source custody

- Change only `experience2/apollo-r281/apollo-source-experience.php`, its scoped stylesheet and its source-controlled PHP/Playwright gate. This layer adds an **actual text-only source catalogue** with direct NASA links, accessible named controls, source type and explicit record-dependency warnings. It does **not** add photographs, reconstructed imagery, map pins, independent witnesses, tracking or commercial links.
- NASA sources: [mission](https://www.nasa.gov/mission/apollo-1/), [Safety and Mission Assurance](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1), [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Board's most probable electrical arc finding **does not identify a precise ignition site**. These three NASA records are not three independently corroborated eyewitness accounts.
- All curated historical fields, source names/types, dependency descriptions and URLs have one pinned canonical PHP JSON SHA-256 (`268605391a741300d13e487968336040bfe016dd3d6e2165182a5269ecb19d4d`). Edited evidence fails to a NASA-report/free-investigation link fallback rather than displaying unreviewed claims. A hash in the same file is an **accidental content-drift guard, not tamper-proof publication authorization**. Editorial status remains pending, regardless of shortcodes or source integrity.
- NASA [brand](https://www.nasa.gov/nasa-brand-center/) and [advertising](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) constraints apply. Linking to official sources is permitted without implying endorsement; no image or identifiable astronaut media is rehosted, so **media reuse rights are not claimed**. Image gallery awaits actual per-file rights review.

## Reproducible local acceptance

Run from repository root with Python Playwright, PHP 8+, and locally installed Chromium:

```bash
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r281/qa/committed_gate.py /tmp/fv-apollo-r282
```

The executable source-controlled gate renders **actual PHP**, rejects changed NASA destinations/duplicate dates/missing boundaries and unreviewed mutations to historical wording, source type or dependency, then exercises actual Chromium at **320, 390, 768, 1440, 1920px × JS enabled/disabled**. It verifies six native keyboard-operable drawers across two instances, unique IDs, direct source catalogue destinations, the browser Accessibility tree's source-link name, chronology navigation, print-visible source URL and no unexpected browser requests. The source catalogue is usable without JS; touch/reduced-motion and forced-colors contexts are included. See receipt/screenshot SHA manifest in R282 archive.

Local independent executions: **10/10 × 2** real Chromium contexts PASS; PHP source-mutation negatives PASS; screenshot pairs and receipts byte-identical. Original/modified gate's artifact SHA is included in the archive. **Not a claim of genuine axe-core**, independent screen-reader testing, actual browser zoom, installed WP/Assembler, HTTP/CSP, production LCP/CLS or hosted CI. Browser navigation to `data:` and local HTTP is restricted by this runner (`ERR_BLOCKED_BY_ADMINISTRATOR`), so navigation/field performance measurements are intentionally unreported rather than invented.

## Controlled visitor pathway and commerce gate

**Audience hypothesis:** a viewer of an *authenticated already-published* Grok Apollo long-form episode wants primary evidence, then may continue to FV's free original investigation. Proposed flow: `verified_creator_asset_id → public Apollo Atlas (already live, but not the R282 plugin) → NASA source inspection → one free investigation link → separately disclosed, optional Mini Museum buying guide on its own page (only if merchant eligibility and editorial fit verified) → independently confirmed paid merchant transaction`.

The R282 component has **one next action: the free original investigation**. It does not add an affiliate CTA to Apollo narrative. The Mini Museum relationship is a **commercial hypothesis**, not a certified payable merchant relationship; it cannot be presented as revenue without verified sale, refund and fee records. No unique creator Apollo asset/allowed clickable acquisition surface is authenticated by this component. Grok owns creation/distribution; Praxxis independently reviews creator asset; Claude owns analytics, commerce and production implementation; founder approves release. Attribution contract `asset_id/UTM → qualified human session → CTA → confirmed lead if applicable → confirmed merchant purchase → fees/refunds → net realized revenue` for 7/30-day cohorts; unavailable denominator/orders imply **KPI NOT COMPUTABLE**, not zero.

**Release gate:** CI green on exact HEAD, independent editorial/rights approval, independent accessibility including genuine axe-core/screen readers, installed WordPress and CSP/mobile/zoom QA, qualified creator asset & merchant acceptance, founder approval. Draft PR only; no deployment, WordPress settings/content writes, publication, social posts, emails, tracking, affiliate activation or paid services.
