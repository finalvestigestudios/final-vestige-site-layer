# R342 · Canonical QA fixture containment / source-custody fence

**2026-11-13 PT · DRAFT / HARD HOLD · Issue #136 · commercial coordination #820 / #818**

This is an additive, read-only/test-only engineering review. No original article, six tool bodies, metadata, source registers, taxonomy, URLs, WordPress/public pages, site analytics, social media, email, or paid offers are changed.

## Material defect and scope

Independent food-fixture QA PR [#169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169), still a draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, moves one synthetic source upgrade into a `TemporaryDirectory` but leaves `test_register_fragments_cannot_duplicate_ids` creating/deleting `ROOT/sources/fragments/_dup_test.json` in the canonical source checkout. This produces a concurrent-reader corruption window even if the test restores its initial bytes. Its dependent remediation PR [#2205](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2205), at `bbcf1859768624c611df4abadc564c18247cf32a`, is unmerged. The isolated new guard is **not** a replacement for merging/reviewing #2205.

The R342 runner hashes original content/sources/taxonomy/templates/assets before and after native tests, validates all **35 article + 6 tool body/metadata pairs**, demands the authentic R341 source witness, and installs a Python audit fence *before* test discovery. It blocks canonical-source write opens, creation, unlink, rename/replace, link/symlink, chmod/chown, utime, truncate, mkdir/rmdir and chdir. Lexical and symlink-resolved paths are both checked. Temporary fixture writes outside canonical source remain permitted. A detected transient write remains **INVALID_HARD_HOLD** even when the final source digest is unchanged. No fabricated QD PASS can result.

## Exact local test evidence

- 166/166 **new** synthetic/adversarial test cases passed on locally executed R342 source.
- 1,259/1,259 **combined reconstructed isolated R331–R342** local Python test cases passed via `python -I -c` with the local archived module root explicitly inserted for discovery.
- Exact source Git blob: `5dc13ad1cb0f37335ff1eb42a2d950f71b9c575f`. Exact test Git blob: `a74140a8af85359d83fb06e32738e83d87aeff67`. Both matched GitHub branch readback.
- Negative control: an incomplete local repository checkout correctly returned **INVALID_HARD_HOLD**; no real source directory was modified.
- The 166-case suite includes 133 discrete write/path/event matrix cases, synthetic genuine 36-test subprocess success, and separate failed subprocess tests for canonical write and rename attempts. A blocked attempted write is *not* evidence that such a write occurred in production.

## Exact original branch and independent QA observations

All seven original Claude cluster heads and two Shelter descendants were compared **live** on 2026-11-13 to the R341 pinned SHA identities; all nine comparisons reported `identical`, zero ahead/behind. Home lead #1689 was also identical at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Independent start-safety QA #157 remained draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, QA #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and dependent #2205 at `bbcf1859768624c611df4abadc564c18247cf32a`.

Retain the **14 Git-object divergences versus 15 separately unresolved original editorial conflicts**, eight R341 human review packets, **17 original Article #15 / Tool #104 claim obligations**, added E335 service-animal/pet/assistance-animal review and subsequent E336 FEMA 2017 form/portable-card sensitive-data provenance question. These are **not** resolved by a QA fixture guard.

## Native run instructions / limitations

From an authenticated complete native checkout use:

```sh
python -I preparedness/tools/r342_canonical_fixture_containment_hold.py --repo-root . --execute-suite
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The audit hook is **Python process-level only**. Native extensions, already-open file descriptors, external subprocesses and malicious low-level code can bypass it. It is an extra safeguard, **not** a real OS filesystem sandbox, claim-to-source validation, reproducible 100-file native WordPress export, CI signal, privacy or emergency safety signoff. Full native checkout remained unavailable in the local test environment owing to GitHub DNS resolution; **no real native validator/build, full site test run, 50 WP + 50 private preview exports, hosted CI or qualified QD was executed in R342**.

## Conversion-first blocker plan (no speculative SKU)

| OFFER | FUNNEL STEP | BLOCKER | SAFE CHANGE / EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| One actual FV-owned Preparedness practical pack | Paid checkout/order | Seller authorization, rights-cleared SKU, delivery, refund terms and real merchant status unauthenticated | Founder/Commerce read-only inventory/terms verification, then separately approved mobile checkout test | NOT VERIFIED; no paid CTA or sale | Founder/Commerce |
| Existing public free agency-reference Archive | Guide and optional printable | Detailed Article #15 / Tool #104 private/held; safety, privacy, claims, source conflicts and native output review unresolved | Qualified adjudication, realistic print/no-JS/privacy/mobile/CTA checks; do not link held tools | HARD HOLD | Preparedness/QD |
| One actually published on-topic family-contact/reunification Grok asset | Permitted social-to-Archive visit | `asset_id`, original post, date and permissible mobile destination not authenticated | Praxxis/Grok verify already-published matching topic in TASK-008 without reassigning creator queue | NOT VERIFIED | Grok/Praxxis |
| Qualified human session → lead → merchant-paid order → net revenue | Measured funnel | Consent/confirmation, qualified denominator, order receipt, fees/refunds not reconciled | Claude/Commerce check provider-origin confirmation and merchant settlement; 7/30-day tiny-sample warnings | Net revenue/1,000 qualified sessions NOT COMPUTABLE | Claude/Commerce |

Only candidate public free destination: https://finalvestige.com/preparedness/ . No retired water freebie or new offer. Explicit founder approval is required for any production CMS, navigation, email, social post, analytics, merchant, affiliate, paid or publication operation.
