# R318 — PR #169 duplicate-source fixture isolation (DRAFT / HARD HOLD)

Observed 2026-11-12 PT. Preparedness Issue #136, business attribution #820, charter #818. **Do not merge or publish.** This PR is an isolated **dependent** draft against independent QA branch `review/preparedness-food-fixture-isolation-20261030`, not main and not R317.

## Exact provenance
- PR #169 parent HEAD: `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Before this patch `preparedness/tests/test_preparedness.py` Git blob `e80d622c2fd32bf6c9752e375c1208c1d47d8e7c`.
- Updated test blob in R318: `b63e7f4dc9c84a4bef15dd581affe08ac81356af`; first commit `b09865373abd96050367bb060ea773d10d98d49f`.
- Scope: one existing Preparedness test file plus this audit only. No manuscript, source register, evidence fragments, taxonomy, safety/approval states, URL, WordPress output, CMS, commerce or site navigation mutation.
- Independent QA #157: open/draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Homepage lead #1689: open/draft HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`. R317 integration #2199: open/draft HEAD `0335416a3b658f5f626489c428aa61e8890bf90d`.

## Repaired source mutation
The prior duplicate-source test created `ROOT/sources/fragments/_dup_test.json` and removed it with `unlink`. R318 instead copies the Preparedness source tree into a scoped temporary directory, inserts the synthetic duplicate **there only**, and verifies `build.Library(root=sandbox)` rejects the duplicate source ID. A new runtime regression wraps `Path.write_text` and `Path.unlink` while exercising **both** synthetic fixture tests, failing on any write/delete under canonical `ROOT`. The library's verified-source override behavior remains enforced; no source-validation rule is weakened.

## Local execution classification
- Local R317 **existing** isolated suite re-executed from its archived source/test files: `80/80 PASS`; this checks the separate R317 AST sentinel, **not** this PR's full integration.
- Local functional **prototype** of the two R318 fixture methods and new write/delete guard on a disposable synthetic source tree: `3/3 PASS`, Python compilation PASS. These prototypes reproduce the corrected logic but **do not** establish byte-identical execution of PR #2205's entire committed test file.
- Authenticated source Git blob for patched test fetched back and matched `b63e7f4dc9c84a4bef15dd581affe08ac81356af`. Native `validate.py`, `build.py`, full 36+ test suite and 41 WordPress/41 preview outputs were **NOT EXECUTED** because GitHub DNS resolution blocked an authenticated complete checkout locally.
- This parent food branch's older `build.py` blob is `b81f0f7fbf8848ac14e2e6bc072783776c9ec057`, whereas R317's protected builder is `349173d1e1d735eade218d95c7a0a2649c8cccd9`. Their `{{inline-js}}` file-resolution roots differ: the older food version uses module-global `ROOT`, while the current integration builder uses `lib.root`. **Do not blindly merge/cherry-pick across the branches** or treat a copied fixture's JS rendering as production parity.

## Remaining gates
All seven original Claude cluster refs compare `0 ahead/0 behind` to their frozen R200 SHA identities. Shelter continuation is +6 commits and Shelter follow-up is +9 ahead of frozen Shelter; they are not automatically approved. The historical 35-article slate, ten substantive article differences, twelve metadata differences, disputed source records, 41 authentic export pairs, Article #7 hazard claims and Article #15/Tool #104 emergency-dispatch, child privacy, print/no-JS and accessibility require independent adjudication. Human source-link checking and qualified safety/QD remain unapproved. No publication right, safety certification, confirmed paid conversions or realized net revenue is inferred.

## Conversion acceptance (no unapproved paid offer)
- **Candidate topic:** family emergency-contact/reunification. **Free destination:** the already public agency-link Archive `https://finalvestige.com/preparedness/`, pending Grok/Praxxis confirmation of the actual published immutable asset ID, final mobile URL and audience-intent match.
- **Optional free companion:** Tool #104 remains private/unreviewed, no CTA until qualified safety/child privacy/print/no-JS clearance.
- **Optional paid practical pack:** no verified currently purchasable, rights-cleared, deliverable, suitable FV Preparedness SKU; no paid CTA or invented SKU.
- **Funnel accountability:** asset_id/utm_campaign → qualified landing → relevant CTA → consented confirmed lead (if applicable) → independently paid merchant order → fees/refunds → net revenue per 1,000 qualified human sessions (7/30-day cohorts). All commercial figures remain **NOT VERIFIED/NOT COMPUTABLE**.

Founder controls release and spending; Grok owns social posting; Praxxis QA's distribution; Claude owns website/analytics engineering. This PR changes no social queue, metrics scripts, offer status or customer data.
