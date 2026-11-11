# Apollo R287 — primary-record chronology correction (staging HARD HOLD)

Parent: R286 draft PR #2053, exact parent SHA `bccec12c8cb647883d003bd4892a396e70dfa169`. Independent Apollo-only lane; homepage PR #49 and Research Desk PR #158 untouched. **No WordPress deployment, editorial approval, merchant activation, analytics alteration, or content publication.**

## Reproduced historical error

The R286 January 28 plate incorrectly stated that NASA **established** the Apollo 204 Review Board on January 28. The Board's first-hand institutional history says the Board was established on **January 27, 1967** and convened on **January 28**. Its dated proceedings document the first general session and Launch Complex 34 site inspection on January 28.

Sources (NASA-owned historical records, linked rather than reproduced):
- https://www.nasa.gov/history/Apollo204/narr.html — narrative of Board history, January 27 authorization and January 28 convening.
- https://www.nasa.gov/history/Apollo204/proceed.html — original Board proceedings of January 28, site visit and discussions.
- https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — primary full Board report; initiator not conclusively identified.
- https://www.nasa.gov/nasa-brand-center/ — guidelines on links, endorsements, images and trademarks.

The replacement Jan 28 EvidencePlate now states *convened* and *visited Launch Complex 34*, explicitly distinguishes it from establishment, and uses the **1967 primary Board proceedings** as its source rather than a later NASA Safety and Mission Assurance summary. The source gallery contains the updated provenance record. The source-list count stays three (one record per date); no location/map pins, archival photographs, agency imagery or commercial uses were added. Source integrity digest is recalculated for this staging-only corrected copy; editorial approval remains pending and historical accuracy must be independently reviewed before release.

## Reproducible verification (local only)

From a fresh extraction, run:

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
php experience2/apollo-r287/verify_board_chronology.php
php experience2/apollo-r285/verify_preflight.php
php experience2/apollo-r286/verify_bounded_preflight.php
python experience2/apollo-r281/qa/committed_gate.py QA/Browser
python experience2/apollo-r285/verify_print_export.py QA/Print
python experience2/apollo-r287/build_archive.py QA R287.zip
```

`verify_board_chronology.php` tests 14 conditions: date and event semantics, Board primary source, integrity mutation rejection, pending review, non-commercial rendering, single free CTA, accessible native source navigation and no imagery/map pins. The unmodified R286 PHP must fail `board_meeting_jan_28`; this is the pre-fix negative control. Inherited browser regressions cover Chromium at 320, 390, 768, 1440 and 1920 CSS px, with and without JavaScript, native keyboard source round-trips, touch, reduced motion, forced colors, enlarged text, no network requests and no overflow. Printed PDFs at 390 and 1440 retain four unique source/free URLs and eight actual clickable annotations. Capture receipt and screenshots; rebuild archive twice for binary reproducibility.

**Limitations:** This is offline Chromium `set_content` + a simulated WordPress API. Browser navigation to HTTP/file URLs returned `ERR_BLOCKED_BY_ADMINISTRATOR` in the execution environment. Genuine axe-core, installed WordPress/Assembler, NVDA/VoiceOver, independently verified accessibility, browser HTTP/CSP, p75 LCP/CLS/INP, hosted CI, and cross-channel verified revenue remain untested. Offline performance observations may not be reported as field CWV. Do not release without independent editorial approval, accessible staging acceptance, CI and founder authorization.

## Business conversion custody

Verified Grok published Apollo asset (none confirmed) → Evidence Atlas source inspection → **one free Apollo investigation CTA** (`https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`) → optional separate approved buyer-fit guide → independently verified paid order (fees/refunds accounted). Mini Museum affiliate acceptance and commissions are unverified; do not insert a merchant CTA into the Apollo narrative. KPI: verified net revenue per 1,000 qualified-human sessions in 7/30-day cohorts, not views or clicks. Grok owns social; Praxxis independently reviews creators; Claude owns production analytics; founder controls release/spend.
