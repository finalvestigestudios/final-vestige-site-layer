# Preparedness R233 — Frozen Editorial Hub Input Custody (2026-11-08 PT)

**Issues:** #136 engineering and safety; #820 conversion evidence; #818 founder charter. **Release state:** BUILT / 67 ISOLATED TESTS PASS / NATIVE NOT EXECUTED / DRAFT_HARD_HOLD. Never interpret this gate as permission to publish, medical/food/water advice approval, human source sign-off, independent QD PASS, merchant approval, or verified sales.

## Independent QA discovery and engineering fix

The dated Praxxis/Grok handoff independently identified a specific R232 dependency gap: authenticated `preparedness/tools/build.py` at Git blob `349173d1e1d735eade218d95c7a0a2649c8cccd9` reads optional `content/hubs/<section>.body.html` at lines 528–542. R232 reconstructs landing/hub outputs with that builder but did not freeze the editorial input bytes or presence. A changed input with matching regenerated HTML, or a newly added editorial input with matching hub HTML, could therefore satisfy byte-for-byte renderer replay. This is a modeled custody failure, **not** a confirmed live compromise.

**R233 fixes the consumed-source boundary without editing the protected producer:**

- Independently observed at R232 base HEAD `2b686cffda69c125e8f1ab1f1b8a647dd6be6778`: `content/hubs/` contains EXACTLY `start-here.body.html`, Git blob `e1e749169a58e35a32c1d48ee8c46c209630965b`. The absence of all other files is itself frozen.
- New read-only `tools/r233_hub_input_custody_hold.py` freezes directory membership and Git-blob identities, rejects missing/extra names, symlinks, untrusted directory replacement, binary drift, or altered existing text. This is separate from R232 generated-output comparison.
- R220 loads the new module directly from authenticated bytes at Git blob `668c74c1672d86e4defad5e14a95ab1924ca6aa2`, calls it immediately **before** R232's `audit_auxiliary_exports`, then calls it again **after** R232 reconstructs and compares all landing/hub drafts. It also checks the module's Git identity at post-render completion. If a cluster adds or changes a hub file, this must enter a new reviewed source pin instead of being silently accepted.
- All previous R221–R232 article, tool, source, route, review and 82 export gates remain in place. No source/citation, article/metadata, taxonomy, slug, safety label, generator, WordPress, merchant, CTA, tracking or analytics change was made.

## Actual executed test evidence

`python -I -m unittest discover -s /mnt/data/fv_r233/preparedness/tests -p 'test_r233*.py' -q` → **67/67 PASS**. Python compilation of exact locally executed R233 module and tests → PASS. Executed Git blob identities match newly committed GitHub files:

- Module: `668c74c1672d86e4defad5e14a95ab1924ca6aa2`
- Test: `e95a24d7763b94a71b9c0d36aa2c8b3cf2be1f47`

Tests cover one non-authorizing HOLD baseline, the immutable pin, Git blob framing, positive/negative state controls, changed hub input with regenerated matching HTML, newly added hub with matching regenerated HTML, absent/symlinked directory and file, malformed manifests, **32 file-content mutations** and **18 added-file membership mutations**. All data are synthetic and only written into temporary directories. They do **not** independently exercise the authentic `build.py` or full 35-article integration; R220 orchestration has been source-reviewed, not run end-to-end.

**NOT EXECUTED:** trusted complete native checkout, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full `python -I -m unittest discover -s preparedness/tests -v`, R220 native 35+6 manifest/reconciliation audit, 82 original article/tool exports plus landing/hub outputs, independent editor/source and qualified safety review. Local GitHub DNS could not resolve `github.com`; connector read/write access is NOT a substitute for complete native execution.

## Current independent checkpoints

- All seven original contributor heads still match frozen R200 manifest: start `2122d856`, shelter `5daeaf2d`, food `f911ff7a`, health `d5ef5baf`, hist-field `4e5caf81`, hist-food `67e116e5`, hist-home `7504a5f0`; none modified here.
- Independent QA PR #157 draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture PR #169 draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Both are separate, unmerged, and not overridden.
- Homepage lead review #1689 draft HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0` left untouched.
- Remaining source problems: Article #7 two CDC source-use occurrences; Article #20 one Ready.gov source-use occurrence; seven historical source-ID conflicts; Article #20 medical-power restoration assurances and household access planning require qualified, source-specific adjudication. No disputed source endorsed.

## Conversion-first, ONE provisional candidate, NO new offer activation

**High-intent topic:** out-of-area family contact and locating emergency records. **Free destination:** the existing `https://finalvestige.com/preparedness/` official resource links; original 35 article drafts are not approved public URLs. **Optional candidate under evaluation:** publicly listed `Legacy Triage` ($19 PDF, `https://payhip.com/b/n1RhV`); seller page calls it a personal/financial and estate/incapacity toolkit, not a disaster-response kit. Ownership authorization, product privacy/account credentials handling, fit, secure delivery, checkout, refunds and actual sales are NOT VERIFIED; no direct Preparedness upsell is approved.

**Draft CTA, NOT for release:** “Choose an out-of-area contact, then write down where your family can find its essential documents. Start with free official emergency-planning resources.” The cited official guidance remains free without signup.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (DRAFT ONLY) | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing Grok asset → public Preparedness free guidance | No authenticated published post, asset_id, destination or privacy-safe qualified-human denominator | TASK-008 reconcile published platform URL, date, exact content, creator rights and final mobile URL; use permitted UTM only after approval | **UNVERIFIED** | Grok / Praxxis |
| Public resources → 35 original long guides | Native corpus build, citations and human safety checks incomplete | Run full trusted validation and source-level editorial acceptance; preserve depth and canonical routes | **HARD HOLD** | Preparedness / independent QA |
| Free official guide → optional Legacy Triage | Seller/rights privacy, purchase fit and disclosure unverified | Inspect entire PDF, document secure account-access guidance; confirm commerce ownership and only then propose optional, clearly labeled estate-documents placement | **NOT APPROVED** | Founder / Commerce |
| Optional digital product → checkout → delivery | Merchant checkout, refund rules, mobile UX and fulfillment untested | Consent-based authorized end-to-end order/delivery verification; no speculative sales | **NOT TESTED** | Commerce |
| Qualified sessions → confirmed orders → refunds/fees → net | No trusted matched denominator, confirmed paid orders or transactions | Reconcile 7/30-day merchant cohorts, disclose small sample limitations, compute net revenue / 1,000 qualified human sessions only with actual orders | **NOT COMPUTABLE** | Analytics / Commerce |

No merchant activation, email, social post, new tracking script, paid service, CMS/nav write, homepage change, or public release. Grok owns content distribution; Praxxis research/QA; Claude core site engineering; founder retains release/spend approvals.

## Required continuation on complete checkout

Verify the branch HEAD and all seven frozen refs; execute isolated 67 tests, entire existing >=36 suite, native `validate.py`, native `build.py`, `python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness`. Capture stdout/stderr and hash/output inventories. Compare 35 original texts and metadata against the seven source branches, all 41 canonical draft records, every evidence link and safety classification, original reading depth, 82+ landing/hub HTML files and their customer-visible citations. Finish independent source/qualified safety review before any QD or publish consideration. **HARD HOLD continues even if machine checks pass.**
