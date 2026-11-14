# R373 · Preparedness Tool #104 PDF card-pair custody · 2026-11-14 PT

**Status: DRAFT / HARD HOLD. Scope: Issue #136.** This is read-only, additive engineering, not a request to release the original tool, approve emergency advice, or write to WordPress.

## New risk and scope
R372 verifies browser DOM face geometry and counts warning text in a PDF. Neither establishes that the **front and back of an individual detachable card remain on the same printed PDF page**, nor that every intended copy survives without duplication. A PDF can have the right total number of warning strings while one fold-over pair is split across sheets.

R373 adds an **offline generated-PDF pairing check**. For synthetic test cards only, each front/back pair receives a unique nonsensitive marker. PyMuPDF looks for exactly one of each marker, requires both on one PDF page, rejects unsafe-edge placement, missing/duplicated/unexpected IDs, malformed/oversized PDFs, and count drift. Offline Chromium prints 1–4 synthetic card copies with JS disabled; all external requests are blocked.

**Limit:** Unique markers are injected into a *synthetic test fixture*, not the authentic Tool #104. This does NOT establish authentic user-field fidelity, human print trimming, font legibility, screen reader behavior, printer margins, or qualified child-privacy review. No real personal/contact data were used. PDF search and a simple 18-point test margin are proxies only.

## Exact source and custody
- Parent R372 draft PR #2515 HEAD `a1a9440977172286b33c1cd6ce160111f099d125`, preserved untouched.
- Original private Tool #104 body Git blob `be8698ac5d020476ff649d85813810e2000c6f98`, metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`; editorial drafted, publication draft, safety pending. The R373 review function checks these pins and refuses drift.
- No article, source register, citation token, publisher claim, safety status, HTML manuscript, canonical URL, navigation, CMS, product, or live analytics change.
- R373 CLI **always exits 2**. All merge, publication, safety, commerce, and QD approval booleans are false.

## Executed checks (local isolated source, not native suite)
- New R373 **56/56 Python tests PASS** including 32 generated missing/duplicate/edge/page-split cases and offline Chromium actual synthetic PDF outputs for 1, 2, 3 and 4 copies.
- R368–R373 combined **474/474 isolated tests PASS** (inherited R368–R372 = 418); Python compilation PASS.
- GitHub connector code/test blob identities must match locally executed files before reporting exact committed-code verification. Hosted CI is not a PASS.
- Native `python -I preparedness/tools/validate.py`, `build.py`, and canonical full suite **NOT EXECUTED**: local GitHub DNS prevents authenticated full checkout. Real 50 private WP + 50 preview pairs **NOT EXECUTED**. No independent physical print/QD review.

## Contributor and separate QA custody
Nine pinned contributor refs compared against live named branches on 2026-11-14: Start 2122d856, Food f911ff7a, Health d5ef5baf, Historical Field 4e5caf81, Historical Food 67e116e5, Historical Home 7504a5f0, Shelter 5daeaf2d, Shelter Continuation ac8625fa, Shelter Followup 6a5998ea — **nine identical, ahead 0/behind 0**. Source-register reading scopes and 35-article reconciliation remain human-review holds.

Independent PR #157 HEAD `7d1ae6b8` retains additional safety restrictions; PR #169 HEAD `e9cd7766` still has the duplicate-source canonical fixture concern; dependent #2205 HEAD `bbcf1859` proposes sandbox isolation; home #1689 HEAD `f55c36b6` remains outside this lane. All separate drafts, none merged.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER
1. **One existing FV-owned Preparedness paid pack → verified purchase:** no confirmed FV-owned rights-cleared payable SKU, legal claims, delivery/refund terms, or merchant receipt → Founder/Commerce to authenticate before paid CTA. **HOLD.**
2. **Already-public free household emergency-plan resource → optional Tool #104 card:** privacy/cutout/page pairing/child safety under review → retain public free authoritative resources; R373 synthetic PDF pair gate only → **56 local tests PASS / authentic HARD HOLD**, Preparedness/QD.
3. **Published Grok family-contact asset → `/preparedness/`:** no independently confirmed immutable asset ID or matching approved hook/UTM → research-only TASK-008 check by Grok/Praxxis, no creator queue edits. **UNVERIFIED.**
4. **Qualified sessions → relevant CTA → verified lead (if applicable) → paid order → refunds/fees → net revenue:** attributable merchant orders and 7/30-day verified human cohorts absent → existing Claude measurement contract, no duplicate script → **NOT COMPUTABLE**, Claude/Commerce.

Draft unposted free CTA: **Start With Trusted Preparedness Resources** → https://finalvestige.com/preparedness/ . Preserve all free emergency instructions; no retired water freebie or unapproved product. No purchase, email, creator post, deploy, CMS or WordPress write, navigation edit, tracking installation, merchant action, spending, or false QD PASS.
