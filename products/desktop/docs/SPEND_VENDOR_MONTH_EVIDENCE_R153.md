# Labs R153 — SpendMap cross-category physical source-line custody (DRAFT / RELEASE HOLD)

R152's vendor/month gross charge and credit totals span multiple categories but the preexisting **source_rows** CSV field only cited records for the current category bucket. Thus a +150 Parts and -140 Services report could display 150/140 gross totals on Parts with source_rows=2, without mentioning the Services credit at physical line 3.

Three **additive, repeated** fields before the R152 monthly-gross columns now clarify the source universe:
- vendor_month_evidence_rows: at most **32 physical CSV record start-line numbers**, across all categories for one normalized vendor/month, sorted **numerically** and semicolon-delimited.
- vendor_month_evidence_count: exact number of underlying records (including zeros, charges and credits).
- vendor_month_evidence_omitted: exact number not shown because of the navigation limit. **If nonzero, the visible lines do not constitute complete evidence**; inspect the original SHA-256-bound input.

The original source_rows remains *category-only*; neither vendor/month values nor the repeated references should be summed across categories. Multiline CSV records use their true physical start lines. The summary uses bounded nsmallest(32) for index generation, avoiding quadratic audit navigation output on 200k-row imports; the importer still enforces its original byte/row limits.

No change to Decimal-safe monetary logic, source digest, original input bytes, normalization-collision reviews, mixed-sign review signals, privacy, no-overwrite, premium licensing or compliance decisions. This evidence is review navigation only, **not** a signature, refund match, fraud finding or approval.

Verification: 25 synthetic end-to-end cases, strict fixed-inventory zero-skip gate in products/desktop/scripts/safe_unittest_r153.py. Run normal Python and python -OO with PYTHONPATH=products/desktop on Ubuntu and Windows. All four combinations must pass on the exact commit; native packaging is separate from real physical Win11 acceptance.

**HARD RELEASE HOLD:** All six desktop apps are unreleased pending independent Win11 46-observation accessibility, genuine Defender/EDR review, signing, authenticated premium distribution, QD review and founder authorization. No production merge, binaries or public download links.
