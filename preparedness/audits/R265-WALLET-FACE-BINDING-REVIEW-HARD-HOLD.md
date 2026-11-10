# R265 — binding wallet-card notices to their actual cutout faces (DRAFT / HARD HOLD)

**Lane:** Preparedness Archive, Issue #136. Cross-reference business charter #818 and conversion coordination #820. Base is R264 draft PR #1901, exact `7734b28fe1de2edade208c8a3b3b405c4dde0b73`. Only Preparedness source-review validators, custody and tests changed. No CMS/navigation/social/commerce/analytics/email/write operations.

## Specific defect and exact correction

Independent Praxxis review of R264 found that the original parser collected privacy notes in one global ordered list. Two cautions moved into **Front** in the correct sequence could satisfy its old global list equality even when **Back** contained no privacy warning. It also did not require Front and Back faces to be direct siblings.

R265 keeps the original 35-article / 2,000-citation evidence and authentic Tool #104 frozen. It changes **only the unpublished R264 candidate's safety gate**, not its HTML or any public content:

1. The Front and Back face elements must each be a **direct child of the card** (no nested/wrapped faces).
2. Each privacy paragraph must be a **direct child of a face**, not nested in another container.
3. Every warning is recorded with its nearest actual face owner. Its exact notice and owner must match `Front` then `Back`, one per face.
4. A new pair of explicit receipt predicates (`r265_notice_owners_exactly_front_and_back` and `r265_cutout_faces_are_direct_siblings`) is required **before** the held WordPress draft-export custody pipeline, while the original negative R263 finding remains.
5. R220 authenticates the amended gate by Git object and rechecks it after the audit. This is a source-only guarantee, not print or privacy certification.

## Verified identities and tests

- Frozen R200 original custody manifest: `5822f9dfde21d1f3bdfc26658769d852c639438c`.
- Original Tool #104: `be8698ac5d020476ff649d85813810e2000c6f98` (**unchanged**).
- R264 candidate HTML: `40782ef142edfd348fec53eb6d8a0dc673244dea` (**unchanged**).
- Amended Python gate: `bcfb472f6074721c88876a16e2bd579cf2f20990`.
- Expanded regression suite: `8bbae6cc71d539296a3f1922571d42ded0a7f3ac`.
- Updated R220 custody file: `953292780f14c49fac25a7206b89c6bc255c621a`.
- The code and tests were independently copied into the local isolated Python environment, **each matched the exact committed Git blob byte for byte**, and `python -m py_compile` succeeded.
- **80/80 Python unittest methods executed and PASSED** on the exact matched code/test bytes. Includes 54 inherited source mutants, 8 additional face-owner/placement/nesting mutants, 18 direct positive/negative state checks. Test input is a synthetic original-source witness plus the **exact committed R264 HTML fixture**, not the complete authentic original source tree.
- Seven authentic Claude contributor branch refs independently compared with frozen R200 SHA: **all identical**, ahead=behind=0. Independent QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic fixture PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, homepage lead PR #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0` inspected; none modified.
- Complete authentic R220–R265 Python validate/build, inherited full regression, and 41 held WordPress export pipeline: **NOT EXECUTED**. The local runner cannot resolve `github.com` for an authenticated full checkout. GitHub connector can fetch individual text objects but cannot substitute for a complete checkout or browser render.
- True browser/print-to-PDF, physical cut-and-fold, readability, JS-off and assistive technology, qualified child-privacy review and independent editorial/QD approval: **NOT EXECUTED / NOT APPROVED**.
- All three disputed CDC/Ready.gov original citations, Article #7 chemical guidance and 32 shared-source review groups remain **UNREVIEWED / HARD HOLD**.

## Conversion-first acceptance (draft, no activation)

**One audience and topic:** already-published family emergency contacts/reunification social content, **only if** Grok/Praxxis TASK-008 authenticates a real immutable social asset ID, platform URL, rights/date/source and signed-out mobile tagged destination. Until then **NO VERIFIED ASSET MATCH**. The existing free public `https://finalvestige.com/preparedness/` landing links official agency guidance; it must not imply held Article #15 or Tool #104 is publicly safety approved.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Free public preparedness guidance | Existing published social post → Archive | Asset ID/rights/mobile landing unverified | Authenticate a genuinely published post and its actual route, without producing content | **NO MATCH yet** | Grok / Praxxis |
| Optional printable contact card (free) | Guide → printable | Cutout readability, printing and data minimization unreviewed | R265 deterministic source guard; independent printing/privacy acceptance required | **80 synthetic tests PASS; real print HOLD** | Preparedness / independent QA |
| Existing Legacy Triage PDF (provisional only) | Guide → optional paid pack | Full product, rights, credential-safety handling and founder approval unverified | Audit the existing $19 listing and complete PDF; avoid any checkout CTA until approved | **NOT APPROVED** | Founder / Commerce |
| Legacy Triage (only if approved later) | Optional purchase → delivered PDF | Checkout, refund/fee, fulfillment unavailable | Authorized merchant-side acceptance with no paid test transaction unless approved | **NOT TESTED** | Commerce |
| Approved commercial funnel | Qualified visits → paid orders → realized net revenue | Missing genuine asset IDs, attributable sessions, provider-confirmed orders/refunds | 7/30-day privacy-safe reconciliation, small-sample notes, no duplicate tracking | **NOT COMPUTABLE** | Claude Analytics / Commerce |

All publicly essential safety guidance stays free. Do not repurpose retired water downloads, fabricate creator assets, infer paid sales from clicks, activate affiliate offers, change Grok's queue or set release flags. No verified order, net revenue or paid conversion exists in this evidence record.

**Release decision:** DRAFT / HARD HOLD. No merge, publishing, WordPress/CMS, navigation, social, analytics, merchant, affiliate, email or spending. Founder release authorization and independent source/privacy/QD review still mandatory.
