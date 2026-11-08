# Apollo Evidence Atlas R210 — one source test, one action (DRAFT; STAGING HOLD)

**Scope:** isolated `experience2/apollo-r210/`, stacked on exact R209 HEAD `19a561ab5b3afd3924a2f1a36e9bc0f07447663e`. Does not modify homepage PR #49, Research Desk PR #158, live WordPress, users, campaigns or checkout.

**Reader change:** The R209 source comparison and earlier R202 reading laboratory had duplicated the same three classroom prompts. R210 removes only the older duplicate, adds a navigable **Source test** anchor to the established page header, deletes its obsolete CSS, and fixes a discovered print defect where the closed answer guide was omitted from Chromium print output. No new source claims, media, geographic pins, JavaScript dependencies or commercial controls. Eight NASA source disclosures, four chronology items and the single free original-investigation CTA are preserved. The visitor-facing experience is less repetitive and has a clearer route from long-form video to evidence and the original investigation.

**Source custody:** source-audit.json is generated from the actual HTML, records exact NASA links, report vs event dates, a rights-use boundary, a confirmed *free editorial* CTA, and an explicit unverified Grok asset ID and unapproved product state. It does **not** claim to have checked live link HTTP status, cleared imagery for marketing, or verified purchases. NASA original Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; damage photo S67-21294: https://www.nasa.gov/image-detail/amf-s67-21294/ ; NASA advertising guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Attribution/endorsement restrictions require separate review for any product.

**Reproduce with R209 staging output archive** (R209 source archive's `dist/` or independently built equivalent):

```sh
export FV_APOLLO_R209_DIST=/absolute/path/to/R209/dist
python3 experience2/apollo-r210/build_r210.py
php -l experience2/apollo-r210/dist/fv-ex2-apollo-r210.php
python3 experience2/apollo-r210/qa/gate_r210.py /tmp/apollo-r210-qa
# Optional strict axe test. Supply authentic axe-core dist (not a stub):
FV_AXE_JS=/path/to/axe.min.js python3 experience2/apollo-r210/qa/gate_r210.py /tmp/apollo-r210-axe --require-axe
```

Builder fails closed on modified R209 hashes. It emits PHP/CSS/HTML/JS with pinned SHA-256, deterministic source audit and manifest. The browser suite tests PHP normal/late/print, closed-disclosure print answer visibility, real Chromium at 320/360/390/768/1440/1920, keyboard focus/Enter, touch disclosure, JS off, reduced motion, forced colors, horizontal overflow, screenshots, fixture LCP/CLS and nine negative mutations. **Browser `set_content` fixture is not installed WordPress, live-site navigation, or field CWV; remote and localhost navigation are blocked in the execution environment.** Genuine axe cannot be declared PASS without the real library, and NVDA/VoiceOver/real pinch/zoom/QA remain open.

**Commercial pathway:** Grok YouTube long-form (published asset ID *unverified*) → Apollo Atlas → R210 source exercise → **Read original investigation** (free) → hypothetical separately-approved 45–60-minute teacher-ready evidence dossier. No approved Apollo SKU, priced order, rights-clearance manifest, merchant acceptance or actual purchase exists in this lane; do not insert a sales CTA. Hypothesis: a less repetitive, directly source-linked learning path improves qualified investigation clickthrough; purchase conversion and net revenue per 1,000 qualified human sessions remain **not computable** until source-of-truth sessions and merchant orders are accessible. No new tracking code; Claude/#820 owns approved measurement, Grok owns content/distribution, Praxxis creator QA, founder controls release. Tests of visits are not orders.

**Hard hold:** An R198 source archive differs from the canonical GitHub builder (canonical Git blob `57ef73d5719662a1b3647536a0eace5fb65bac4a`, inherited archive `2e09257cbd0b32a93f2e7e034a84685d93ed93f5`). This R210 builder verifies only the R209 dist snapshot SHA `8365d42571fc54d36950e8ce2d8cae4ef36503fd300ef7cc8f5e9f4a2181cb91`, not full GitHub ancestry. WordPress/Assembler theme and shortcode lifecycle, actual NASA/CTA browser navigation, genuine axe-core and assistive-technology QA, hosted exact-head CI, founder/independent approval and commercial rights review are **not yet passed**. Do not merge, publish, activate or promote.
