# Apollo R155 — Source custody + exact-template Chromium AX/CWV laboratory (STAGING HOLD)

Scope: #150 (Apollo), #820 (conversion contract), #818 (charter). Proposed draft based on R154; **PR #158, homepage PR #49, production WordPress, analytics, commerce, Grok/Praxxis content and creator queues remain unchanged**.

## Implemented
`r155_exact_template_ax_cwv_lab.py` is a real source-controlled Playwright/Chromium extension of R154. It verifies exact PR158 template/CSS Git blob identities and R153 replacement JS before rendering the **six complete original cards**. R155 adds six-width Chrome DevTools Protocol accessibility-tree inspection (searchbox, six expandable records, original investigation CTA), no extraneous checkout link, no invented geo coordinates, all six evidence limitations and field-label presence. It collects **offline** PerformanceObserver last-LCP entries and layout shifts after installing a page using Chromium set_content; reproducible screenshots and SHA-256 are emitted. Network routes are blocked, no CMS or merchant writes.

Local **Chromium 144.0.7559.96**: **174/174 checks passed**, at 320/360/390/768/1440/1920. Two browser runs: all **6 PNG SHA-256s were identical**. The 6 offline layout-shift sums without recent input were all **0**; recorded last-LCP observer entries vary (approximately 96–264 ms in the first run). These are **not** production LCP/CLS or statistically meaningful p75 CWV readings; there are no live theme, image, font-network, cache, real-user interaction or visitor/network conditions. Browser security policies block URL navigation; this runner uses set_content and must not be described as page navigation acceptance.

All 174 checks are source-bound offline only. **axe-core was unavailable, so automated WCAG acceptance is NOT COMPLETE.** CDP AX-tree inspection is useful but does not substitute axe-core, manual screen-reader audits, keyboard-device, WordPress shortcode/theme/Jetpack integration, production INP/LCP/CLS, or authenticated checkout QA. Exact-head CI and independent QD/founder release approvals remain necessary.

Reproduce from a checkout of this PR (never run production writes):

```bash
python -m py_compile experience2/apollo-r155/r155_exact_template_ax_cwv_lab.py
python experience2/apollo-r155/r155_exact_template_ax_cwv_lab.py \
  --template experience2/research-desk/templates/ledger.html \
  --css experience2/research-desk/assets/source-ledger.css \
  --js experience2/apollo-r154/r153_source_ledger_compat.js \
  --extra-css experience2/apollo-r154/r153_source_ledger_compat.css \
  --out /tmp/apollo-r155-first
# Optional: --axe /reviewed/local/axe.min.js; incomplete axe is a failure, not a pass.
# Re-run into /tmp/apollo-r155-second and compare both SHA256SUMS files.
```

Repository R155 Python blob: `816a5c3ab8ec8667d2e11452585de0541d34d8ea`. R154 exact input blobs: template `403d128c57b9bc82dac7c619651689070edef86c`, CSS `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`, replacement JS `3610ec8f68fc0332db04bcfa5c368574818e9866`. **Do not co-load** the original PR158 source-ledger.js and the R153 replacement.

## NASA link-to-claim custody: six independent NASA catalog pages inspected November 5, 2026

All six linked NASA image records have retrievable official NASA pages; **a NASA image page is not automatically direct evidentiary proof of the accompanying historical interpretation.** The Research Desk also separately links the Apollo 204 Review Board report, which is a primary historical research source. This is a conservative editorial source audit, not photo-rights clearance.

| Evidence | Linked NASA image and actual NASA page subject | Custody action before publication |
|---|---|---|
| 01 / S67-19766 | [Apollo 1 Crew Honored](https://www.nasa.gov/image-detail/apollo-1-crew-honored/) depicts the crew during training. The linked page does **not** display the claimed `S67-19766` photo identifier. | **MISMATCH:** reconcile exact image catalog ID or label photo as general crew context; separate countdown evidence from image. |
| 02 / S67-15717 | [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/) records January 3, 1967 spacecraft mating preparations, **not** cabin-pressure/oxygen measurements. | Label *contextual photograph*; cite Review Board primary text for 16.7 psia oxygen claim. |
| 03 / S66-58038 | [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/) depicts October 18, 1966 altitude-chamber crew training, **not** the January 27 instrument chronology. | **MISLEADING SOURCE ALIGNMENT:** separate illustration from chronology evidence, cite primary Board timeline explicitly. |
| 04 / KSC-20170124-PH_KLS01_0164 | [2017 Apollo tribute](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/) showing a museum mockup / hatch display. | Label retrospective interpretive display, not 1967 contemporaneous hardware measurement. |
| 05 / S67-21294 | [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/) depicts the fire-damaged spacecraft interior, Jan 28, 1967. | Contextual aftermath photo; **cannot establish the single ignition source**. Retain Review Board uncertainty. |
| 06 / KSC-20170124-PH_KLS01_0090 | [2017 Apollo tribute](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/) describes the redesigned hatch displayed at the tribute. | Appropriate retrospective illustration, but engineering assertions need primary historical technical text. |

Primary historical reference: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . No NASA image or NASA seal has been licensed/cleared here for paid merchandise or commercial promotional endorsement; rights review remains open.

## Conversion-first gate

High-intent audience: secondary educators viewing an approved Grok Apollo long-form/Shorts asset (asset_id and live post **unverified**). One appropriate existing trust pathway: Grok source-aware historical video → Apollo Atlas/Research Desk → **Read original investigation**. Paid educational dossier remains **hypothetical**; do not activate it until SKU, actual checkout, delivery, rights, refund terms and founder permission are verified. No unrelated affiliate CTA and no new measurement script.

Hypothesis only: accurate source differentiation and trustworthy accessible navigation improve downstream purchase qualification. Measure under existing #820 contract: asset_id/UTMs → qualified-human session → editorial CTA → confirmed lead if any → merchant-confirmed paid order → fees/refunds → realized net revenue per 1,000 qualified sessions (7/30-day cohorts, tiny-sample warnings). Current attributable orders, qualified referrals and realized Apollo revenue remain **unverified**.

**Release gate: HOLD** pending correction/clarification of NASA image-to-claim alignment (especially 01 and 03), exact WordPress staging/browser/axe/manual screenreader acceptance, p75 CWV evidence, independent QD, approved matching offer and founder approval. No production deployment approved.
