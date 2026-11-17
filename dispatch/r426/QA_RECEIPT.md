# R426 authoring QA — 2026-11-17

- Canonical PR #175 Git blob IDs verified for all eight campaign source/test files, unmodified; **6/6 native Python tests passed** independently using the exact Git blob identities in the local R422 archived proof copy.
- Static authored-source JS checks passed for both proposals: one operational CTA, expected NASA/first-party source links, subject and preheader length, no merchant earning URLs, no image pixels, no forms/scripts, accessible email table structure, unresolved legal placeholders present.
- New committed `test_r426_offline.cjs` requires native execution from exact committed GitHub files in CI; source-level JS authoring checks alone are **not** a native Node run and not a genuine Jetpack Preview.
- No browser, real inbox, partner contract or commerce settlement was observed. Neither candidate is approved to replace the original issue.

Source-check results:

- Issue 04: subject 47 chars; preheader 102; HTML links 4 (one editorial CTA plus evidence sources); email send HOLD.
- Issue 06: subject 53 chars; preheader 89; HTML links 3 (one editorial CTA plus evidence sources); email send HOLD.

Critical unverified gates: named Inspire3 email permission, issue 03/05 approved live guide URLs, FV postal address, unsubscribe rendering, subscriber identity deduplication, actual received welcome and real native Jetpack preview. Value KPI remains not computable.

## Independent final-GitHub source QA

After writing, all 10 files were fetched from the actual R426 branch with their Git blob identities. Initial 29-predicate V8 static review found 28 passing and one **invalid QA predicate**: it counted the two clearly labeled Final Vestige evidence-source URLs in Issue 06 as extra operational CTAs. That was a test-definition defect, not a link defect. An independent stronger eight-check pass examined the exact first link as the editorial action, marked its styling distinctly, and confirmed every remaining link appears in labeled sources across Markdown and text. **8/8 corrected CTA/source checks passed.** No links were removed to silence the test. Text previews were separately corrected to contain an explicit HOLD_UNSENT marker before final verification. The committed offline Node test source has **not** been executed natively on the complete R426 GitHub tree; claims are limited to in-isolate exact-fetched static checks and prior native master Python results.
