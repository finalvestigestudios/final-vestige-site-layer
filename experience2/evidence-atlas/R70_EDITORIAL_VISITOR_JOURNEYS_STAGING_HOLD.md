# Apollo R70 — source-real editorial visitor journeys (STAGING_HOLD)

Scope: issue #150, Apollo 1 Research Desk + Evidence Atlas. Isolated QA contribution stacked on R67; **not** homepage PR #49, independent Research Desk PR #158, or production WordPress. Nothing in this change publishes media, changes WordPress content/settings, introduces geographic pins, or claims NASA endorsement.

## Concrete improvement

Previous source-custody tests exercised individual filters/mutations but lacked one end-to-end browser journey connecting source-filter intersections, zero-result/reset semantics, native details keyboard access, touch-controlled two-record metadata comparison, download contents, print recovery after filtering, and focus restoration to the original Research Desk. The new tests/browser_r70_editorial_interactions.py exercises that path in real Chromium against the **original SHA-verified R38 Research Desk + built Atlas + actual PHP callbacks** using the existing WordPress-API simulator. It does not substitute hand-written fake source records.

Eight viewport widths (320, 360, 390, 428, 768, 1024, 1440, 1920) × JS on/off = 16 cases. Mobile uses actual Playwright touch tap(), desktop uses click(), and native source disclosures are activated with keyboard Enter even without JS. Forced colors are tested at 390 and 1440, reduced motion at all widths. The runner downloads and checks the complete six-record source export (source URLs, per-record custody, explicit rights-pending and no-endorsement text), verifies all 30 Desk and 54 Atlas custody values survive filtered printing, confirms no image elements or speculative location metadata, and checks all six real NASA source links. It rejects browser errors, outgoing network requests and horizontal overflow. The 390px and 1440px screenshots are captured twice under identical frozen caret/animation conditions and must have identical bytes.

A **separate, narrowly triggered workflow** runs exact-head source and PHP checks, installs fixed Playwright 1.55.0 and axe-core 4.14.0, executes the browser runner and axe WCAG 2.2 AA tagging, then retains a source-scoped receipt/screenshots for review. The same-run axe SHA-256 proves the tested bytes match the downloaded file; it is **not an independently signed distribution**. No claimed axe pass until the exact-head CI run completes successfully.

## Release gate

This runner is **source-real component testing, not genuine installed WordPress/Assembler acceptance**. R68/#634 and follow-on R69 drafts investigate the authentic-CMS bootstrap; that work remains distinct and is not overridden. Outstanding: exact-head CI review for R70, successful authentic WP/Assembler/axe browser gate, NVDA/VoiceOver manual acceptance, independent QD, hosted field CWV, and six individual NASA photo-rights assessments. The S67-19766 catalog association is provisional. Do not merge or deploy absent approvals.
