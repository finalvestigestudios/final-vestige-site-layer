# R372 — Tool #104 printed-card box-model overrun; source-pinned review-only correction

**2026-11-14 PT | Preparedness Archive integration #136 | conversion #820 | charter #818 | DRAFT / HARD HOLD**

## Authenticated source evidence
- Original body Git blob: `be8698ac5d020476ff649d85813810e2000c6f98`; metadata blob: `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`, fetched from R371 GitHub head `ffc1aea7845f26326043795c50457c6cf896647a`.
- The original print CSS gives the **parent card** a border-box height of `2.125in`, but gives each **face** height `2.125in` plus padding `.07in` at top and bottom, with no `box-sizing: border-box` on the face. The face's box is therefore taller than the card boundary.
- A synthetic offline Chromium fixture using this exact original CSS declaration measured a 204px card versus 217.4375px faces; face bottoms overran the card by approximately 14.44px including the card's border offset. This is a CSS/layout risk, **not verified physical printed-paper overflow or disclosure of personal information**.
- R371 places a privacy caution on detachable faces in memory, but its prior browser probe can miss a face extending beyond the *parent* cutline. R372 checks **face versus card** bounds, not just text versus face.

## Review-only code change
- Add `preparedness/tools/r372_card_print_trim_geometry.py`: exact Git-blob and pending/draft source-state pins; deterministic R371 follow-on candidate adding `box-sizing: border-box` to the single original print-face rule in memory; no original source write. Source citation IDs/order, internal links, forms, and R371 warning positions remain unchanged.
- The offline Chromium plus PDF geometry probe uses fake inputs only, blocks all requests, checks 7in × 2.125in parent-card measurements, both faces against parent cutlines, warning visibility/size, content overflow, dynamic 1/4 copies, no-JS fallback and PDF-extracted caution text. Required packages / Chromium must exist; their absence is not a pass.
- Add `preparedness/tests/test_r372_card_print_trim_geometry.py`, 67 new pure and browser/PDF adversarial tests. All release flags are `false`; CLI **always exits 2** to keep the hard hold.

## Observed verification
- **67/67 new exact committed-code tests PASS**, local Python 3. R372 code blob `f2a716a2342949a1d2052439fec2fc6f864cf381` and test blob `320b404fa7eb77fd37be31ea20079647c33a6516` were compared with authenticated GitHub readbacks.
- **418/418 combined local isolated Python tests PASS** (R368 through R372, including multiple R371 suites); compilation PASS.
- Synthetic *pre-remediation* no-JS printed card: `FACE_FOLD_OVERLAP` correctly detected on both faces. In-memory CSS proposal: synthetic no-JS, JS one-copy, and JS four-copy dense print/PDF scenarios had no geometry/test errors and no requests attempted. These **do not** establish true-size physical print fit, full-source browser execution, real child privacy or accessibility.
- **Native complete-checkout validation/build/full canonical tests NOT EXECUTED**: authenticated full repository checkout absent; local GitHub DNS lookup failed. Real 50 private WordPress + 50 preview output pairs NOT VERIFIED; no hosted CI PASS, QD PASS or publication clearance claimed.
- Independent review QA #157 remains separate (expanded safety restrictions); fixture PR #169 still leaves canonical duplicate-source writes unless dependent draft #2205 is accepted and proven. Home lead #1689 untouched. Nine original Claude/Shelter refs compared with prior pinned SHA and all returned `identical` (0 ahead, 0 behind) on 2026-11-14.

## Remaining safety and integration blockers
1. A qualified reviewer must assess **both sides of actual printed and trimmed card**, caution size/readability, safe child-data handling, accessible print controls, and no-JavaScript behavior.
2. Validate the **authentic** R370→R371→R372 candidate against full source, original 35-article/six-tool integrated collection and unresolved source reading scopes/duplicate URL identities.
3. Run native Python validation/build/full tests, private WordPress exports and independent source/medical/privacy/QD review. Keep original drafts pending, no merge or publishing.

## Conversion-first owner matrix

| OFFER → FUNNEL STEP | BLOCKER | DRAFT CHANGE/ACCEPTANCE | EVIDENCE | OWNER |
|---|---|---|---|---|
| ONE authenticated FV-owned Preparedness digital pack → verified paid purchase | Existing legitimate payable, rights-cleared SKU, delivery and refunds unavailable | Verify actual SKU, merchant receipt, accessible fulfillment and refunds **before** drafting paid CTA | **HOLD / no verified order** | Founder / Commerce |
| Free evidence-backed household planning resources → optional private card | Detachable card warning/print, child privacy, citation and QD pending | Test full print/cutout offline, obtain qualified safety/privacy and accessible review | **TESTED SYNTHETIC only / HARD HOLD** | Preparedness / QD |
| ONE already-published Grok family-contact video → free /preparedness/ | Actual immutable published asset_id, hook and mobile link unverified | Independently match one authentic published asset; research-only CTA *Start With Trusted Preparedness Resources* | **UNVERIFIED / no UTM claim** | Grok / Praxxis |
| Qualified human sessions → CTA → confirmed leads → settled orders → net realized revenue | Merchant confirmations, fees/refunds and 7/30-day trustworthy cohorts unavailable | Use existing measurement contract; no new tracking script | **NOT COMPUTABLE**, no paid sale inferred | Claude / Commerce |

**No CMS write, navigation edit, merge, live link change, post, email, script, affiliate activation, merchant activation, payment or QD clearance.**
