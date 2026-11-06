# R176 — Isolated Native Integration Preflight (DRAFT / HARD HOLD)

Preparedness Archive issue #136; conversion coordination #820/#818. Stacked on exact R175 PR #1301 head aff6e0c10dcc6844c320af4f6e7a6f3c1b7e2217. Adds only two Python files and this reviewer record. No source article, original source record, homepage, WordPress, navigation, analytics or commerce change.

## Purpose

R176 is the missing whole-pipeline native QA orchestrator: it makes source-checkout verification reproducible without modifying the original 35 articles or converting structural checks into an independent QD approval. It stages the Preparedness corpus into a disposable folder, first checking a paired 35-article census, absence of symlinks, presence of source register/crosswalk, taxonomy and R151/R161 pinned evidence. It computes an input SHA-256 inventory, executes genuine Python validate, build, full unittest discovery, then R174 rendered source/citation and R175 editorial-link gates against exactly generated draft exports. Source manifests are checked before and after.

The runner requires zero validator errors; 35 or more draft WordPress and preview files; 36 or more actually executed tests (skips subtracted); R174 35 articles / 2,000 citation occurrences / 385 article-specific sources; R175 35 articles; both review gates must report DRAFT_HARD_HOLD, return expected exit 2 and verify byte-for-byte export. Positive safety, qualified-source, independent-QD, commercial or publish approval flag is a FAIL. It emits structured per-step evidence, test counts, manifest digest and hashes of stdout/stderr rather than full raw logs. It **always exits code 2**, even when structural checks pass. It does not run CMS writes. Staging is contamination reduction, not an OS security sandbox; use only trusted checkout code.

### Complete trusted checkout execution

    python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300

Read JSON state and all five checks, not shell exit code alone. Never hide exit 2 with shell fallthrough or count structural DRAFT_HARD_HOLD as a qualified safety/QD PASS.

## Evidence and limitations

Local py_compile PASS. Local Python unittest discovery of the exact committed R176 test file: **65/65 passed, zero skips/failures**. The checks include an **actual five-subprocess execution** on a fabricated 35-article, 40-test synthetic repository; a genuine negative run with only 35 tests; and 48 mutated source/approval/status/receipt cases that were rejected. Both remote Git blobs match locally tested source/test bytes. These are diagnostic tests, not authentic public safety decisions.

The authentic repository cannot currently be cloned locally: git ls-remote on Nov 6 returned Could not resolve host: github.com. Therefore full original 35-article validation/build, full repository suite, real R174/R175 output checks, WordPress staging browser/printing/privacy and independent QD were **not executed**. No invented passing result.

All seven Claude Preparedness branches compared IDENTICAL, zero ahead or behind, to exact pins: Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Food f911ff7a655de8d81535ea86ec3d65a49ee76648; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2.

Independent safety PR #157 at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa, synthetic fixture PR #169 at e9cd7766dac59d47ab467d8945269b9146c2aef5 and follow-up #973 remain separate. Homepage PR #1300 b03ced998272a8dec5a70c5f6a48b31d54fe6599 remains untouched. Prior 75 source adjudications, 32 shared-URL interpretation groups, 11 Family Card decisions and 10 jerky citation claims remain human-review hold; some overlap. NCHFP/FSIS dispute, food and medical safety, print/privacy and QD remain outstanding. Historical accuracy is never current safety approval.

## ONE audience, ONE authentic free draft, paid pack gated

Audience: caregivers preparing emergency school pickup, family contacts and reunification. Original source-backed free guide: Household Emergency Plan, proposed /preparedness/start-here/household-emergency-plan/ (NOT LIVE, ungated DRAFT/HOLD). Optional free practical Family Reunification Card also DRAFT/HOLD until human source, real-browser privacy/printing and accessible mobile checks. No genuinely purchasable, rights-cleared matching FV Preparedness SKU, complete downloadable pack, merchant acceptance, refunds or authenticated order was found. Therefore **no enabled paid CTA**; no unapproved product. Existing /focus/ Fieldbook remains the subscriber freebie; retired water offer must not return.

Unpublished CTA candidate after qualified approval: “Plan how your household will reconnect after an emergency. Read the free Household Emergency Plan.” Grok/Praxxis TASK-008 lacks an authenticated published Preparedness asset_id / post URL / destination / right-to-use record. Preserve Grok's original creator queue and Mini Museum-first conditional pilot. Do not activate this draft link.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Owned FV paid pack → paid order | Rights-cleared live SKU, checkout, delivery and refunds missing | Commerce independently verifies listing, pack, license, full checkout and refund/fee policy **before** CTA | HARD HOLD, no paid order verified | Commerce / Claude |
| Household Emergency Plan → free reader | Original safety/source/QD and native build outstanding | Run R176 on trusted original checkout, then independent safety review and staged browser checks | 65 synthetic tests PASS; original NOT RUN | Preparedness / Site QA |
| Free guide → Family Card | Privacy, printing, mobile and 11 source decisions unresolved | Staged 360/390/768/1440 tests using synthetic data | HARD HOLD | Site QA |
| Grok media → appropriate guide | No authenticated creator asset_id / post URL / permitted CTA | TASK-008 creator-owned mapping; no queue edits | UNVERIFIED | Grok / Praxxis |
| Qualified session → confirmed paid net revenue | No human-session count, paid merchant record, fees/refunds | 7/30-day consent-safe source + asset_id/UTM → landing → CTA → confirmed lead (if any) → authenticated settled order and net after refunds/fees; mark small samples | NOT COMPUTABLE | Claude / Commerce |

Landing/checkout QA must match actual creator promise and source-backed free guide, keep emergency instructions free of gates, preserve disclaimers, check accessibility/CTA on mobile, and test genuine merchant fulfillment/returns before a release. Clicks, unconfirmed leads and affiliate outbound are not purchases. Net revenue per 1,000 qualified human sessions is unavailable without confirmed numerator and denominator. No duplicative measurement scripts.

**FINAL: BUILT / LOCALLY SYNTHETICALLY TESTED / DRAFT / HARD HOLD. No public publishing, CMS, navigation, site analytics, affiliate activation, social post, email or spending.**
