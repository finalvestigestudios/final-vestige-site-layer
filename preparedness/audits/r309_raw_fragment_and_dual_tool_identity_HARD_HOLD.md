# R309 — Preparedness fragment resolution and dual-tool identity | HARD HOLD

**2026-11-12 UTC · Issues #136 and #820 · DRAFT ONLY; no merge or publication.**

## Browser-correct fragment targeting without weakening strict source policy

The R307 repair decoded `href="#water%2Dsafety"` before matching an HTML ID. That incorrectly rejected the literal `id="water%2Dsafety"` target and could silently choose `water-safety` if both exist. R309 now retains the original fragment and checks **raw HTML ID first**, then strict UTF-8 percent-decoded fallback. `scan()` exposes `resolved_fragment_ids` for deterministic verification. Invalid percent escapes, invalid UTF-8, control encodings, duplicate IDs, unsafe URL schemes and missing targets remain rejected.

The pre-edit R307 parser was independently reconstructed from the archived R305 source plus the authentic PR #2142 patch. Local computed Git blob was exactly `d91b96a9f2ae5d771f001b3d03b2c1224185430a`. Post-fix executed bytes match new committed blob `06b00c46a704c59eb0a4f78360b3a92a43d133e9`. R306, R307 and R308 upstream SHA pins were refreshed **sequentially** to preserve their fail-closed chain. No original manuscripts, source registers, taxonomy, URLs or safety states changed.

## Important correction: the integrated archive really does contain both tools

Previous R308 reporting treated the `family-reunification-card` authored link as potentially broken by inference from the later Shelter contributor branch. A fresh source-file check finds:

| Integrated draft | Body blob | Metadata blob | Status |
|---|---|---|---|
| #104 `family-reunification-card`, privacy-conscious wallet card | `be8698ac5d020476ff649d85813810e2000c6f98` | `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15` | draft; safety pending |
| #102 `reunification-plan`, household planning tool | `3305578369183edb1d427c8f8f8002eaacee420f` | `10cd57dc8d39e366aaef8fd76cc3f8969b8c5348` | draft; safety pending |

Both slugs are present in integrated taxonomy; each has its own body and metadata, and the two integrated article bodies each explicitly link to **#104**. Thus a broken authored target is **not established**. Actual WordPress export destinations and browser rendering remain untested.

However, the additional Shelter follow-up `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` moves the **exact integrated #104 body blob** (`be8698...`) into a file named `reunification-plan.body.html`, while removing the `family-reunification-card` taxonomy/input. This is a concrete cross-branch **identity/renaming conflict**, not authorization to equate the tools. No automatic merge or routing change.

New read-only R309 tool-identity gate pins seven exact integrated blobs, verifies the distinct tool IDs/numbers, pending safety state, both article link tokens, source integrity, no symlinks and predecessor hard hold. It never authorizes publishing.

## Execution truth

- **118/118 isolated Python tests PASS** on the byte-identical committed source/test versions: 82 fragment/browser-target cases, 36 synthetic tool-identity source-integrity cases.
- Python compilation PASS; deliberately incomplete native checkout correctly returns `INVALID_HARD_HOLD` (exit 1).
- The inherited full Python suite, complete authenticated native `validate.py`/`build.py`, 41 actual WordPress draft outputs, independent emergency guidance review, child privacy, no-JS, printing, accessibility, source/QD approval: **NOT VERIFIED**.
- Fresh compare: all seven canonical Claude contributor branches identical to R200, 0 ahead/behind. Extra Shelter continuation +6 commits, follow-up +9 commits. Ten substantive body changes and 12 changed metadata records still need editorial adjudication.
- QA PR #157 open/draft; PR #169 open/draft and still contains a test writing `_dup_test.json` into the source fragment directory. Home lead PR #1689 untouched.

## Conversion-first owner queue

| OFFER → STEP | BLOCKER | CHANGE / ACCEPTANCE | EVIDENCE · OWNER |
|---|---|---|---|
| Authentic Grok family-contact social post → free archive | No verified published `asset_id`, allowed UTM destination/mobile URL | Grok/Praxxis authenticate existing asset and destination in TASK-008; no new post | NOT VERIFIED · Grok/Praxxis |
| Free guide → optional existing #104 card | Fork identity collision; qualified emergency wording, child privacy, print/no-JS/accessibility reviews absent | Preserve both tool IDs and source trails; test actual exports after safety clearance | Source identity BUILT, safety HARD HOLD · Preparedness/QD |
| Free guide → optional paid pack | No independently proven FV-owned/licensed, currently purchasable and deliverable audience-fit Preparedness SKU | Founder/Commerce verify **one existing SKU**, checkout, delivery, rights, refunds before any CTA | NOT APPROVED · Founder/Commerce |
| Qualified sessions → paid orders → realized net revenue | No verified merchant settlements, attributed qualified sessions, fees/refunds | Claude/Commerce reconcile consent-respecting 7-/30-day cohorts; never count clicks as sales | NOT COMPUTABLE · Commerce/Claude |

**Draft free-only copy for future review:** “Make a plan for how your household will reconnect. Start with free official preparedness resources.” No retired water freebie, speculative paid offer, Legacy Triage assumption or unapproved paid CTA.

**Release governance:** No WordPress/CMS/navigation, production site, merchant/affiliate, social, email, analytics, spending, merging or publishing changes. All gates remain **DRAFT / HARD HOLD**. Cross-reference Issue #136 engineering and #820 conversion charter, plus the existing Grok/Praxxis TASK-008 handoffs.
