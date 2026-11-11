# R281 — Authentic Source-Register Repair and Full Source-Surface Gate

**Scope:** Preparedness Archive only; source/citation custody. **DRAFT / HARD HOLD / NO MERGE / NO PUBLISH**. Based on exact R280 commit `72042a9b2e32a654af73a465e84f81f0b74a7ef2`. Work item #136; business coordination #820.

## Reproduced genuine-source blocker

The authenticated R276 custody manifest (Git blob `b8c7c6df0dca62b04b01abc5671b7083ad9cb61e`) contains seven `sources/fragments/*.json` source-origin rows **and** the root `sources/register.json`. R280's `check_manifest` erroneously required **all eight** origin rows under `sources/fragments/`. This would reject the genuine frozen manifest, irrespective of whether every manuscript byte matched. Earlier synthetic tests used eight invented fragment paths and did not expose the issue.

R281 pins the exact authentic origin roster and repairs the isolated synthetic fixtures to match it. No genuine original file, original manifest, citation, slug, article body, article metadata, tool or exporter was modified.

## Additional previously unprotected real source

A fresh authenticated R280 repository directory listing shows `sources/article-evidence-lock.json` at Git blob `2dc41fccad6f1272f0a9d9585b6c10c760dcb08c` / 18,593 bytes. This file was not included among the original 96 custody entries. R281 additionally pins this source and scans the entire `sources/` directory, not merely `sources/fragments/`, rejecting unregistered JSON/JSONL/YAML/CSV/TSV data (including nested/case-variant additions), symlinks and nonregular filesystem entries. Authenticated evidence set: **96 original manifest entries plus 1 independently pinned source**; **10 expected source-data files**, comprising 8 registered origins, 1 crosswalk and 1 evidence lock.

## Executed checks, exact code identities and limitations

- **146/146 isolated Python unittest cases PASS**, including prior R279 and R280 suites and new R281 root/nested-source adversarial cases. `python -I -m compileall` PASS.
- Committed gate Git blob: `567205e1132a83a52296f5b6d3fa3b7066b703d9`.
- Committed repaired R279 tests: `527c9ea0eb0ffc1cd2e10f78e88384a0f533f4d3`.
- Committed repaired R280 tests: `05574e505075374d7d10321ec8e929139a3727f3`.
- Committed new R281 tests: `39ceeea7d07d85de57325a1735a60e008b2f048d`.
- **NOT RUN:** authentic complete-tree gate, native `python -I preparedness/tools/validate.py`, native build, full inherited repository suite, 41 WordPress-ready draft exports. Local GitHub DNS prevents checkout. Synthetic suite PASS **does not imply** authentic-tree or QD PASS.
- 7/7 current Claude cluster refs freshly compared equal to their R200 frozen SHAs; 17 integrated historic article differences still require substantive review.
- Independent QA #157 remains draft; synthetic fixture QA #169 remains draft, with previously documented source-directory test isolation concern; homepage lead #1689 remains independently owned.
- **Human review HOLD:** 32 shared-source URL groups, 15 duplicate source IDs, 3 disputed CDC/Ready.gov citation occurrences, Article #7 chemical-contamination guidance and Article #15 / Tool #104 child-information privacy, physical print and accessibility.

## Conversion-first business boundary

Audience: household emergency-contact / reunification planners. Only existing public free Archive `https://finalvestige.com/preparedness/` is a possible current destination. Authentic published Grok asset ID/date/rights and signed-out mobile link are **not authenticated**; owner Grok/Praxxis TASK-008. The existing Legacy Triage PDF remains a **provisional** paid candidate: full rights, exact offer suitability, customer checkout, delivery/refund, fees and founder release approval **NOT VERIFIED**. No CTA, checkout, posting or new metric script activated. Verified net revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE**, not zero.

**No false independent QD PASS. No publication, WP/CMS, navigation, social, email, affiliate, merchant, analytics or spending changes.**
