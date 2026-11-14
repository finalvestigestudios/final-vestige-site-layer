# R364 — Exact Git ref / source-citation release firewall (REVIEW ONLY / HARD HOLD)

**Issue:** #136; conversion-owner handoff #820 and charter #818.
**Frozen source baseline:** R363 draft #2461, commit `02d344d9c1a1e9f68a2bcd6c0ab03859acf78232`.
**Scope:** new additive `preparedness/tools/r364_integrated_release_firewall.py`, adversarial tests, this review memo. No source manuscript, original source register, taxonomy, private WordPress draft, homepage, navigation, analytics, affiliate, merchant, CMS, email, or social edits.

## The new enforcement layer

A direct read-only Git-object comparison of all **35 article + 6 authored tool** metadata/body pairs at pinned original commit and candidate ref:
1. Refuses missing Git objects, malformed or duplicate-key JSON, incomplete 41-document closure, path/slug/number drift and changed source corpus. It reads Git objects via `git show` / `ls-tree`, **never checks out or writes a candidate ref**.
2. Requires draft publication state; preserves editorial state and existing per-document safety states/reviewer evidence. An original `approved` label is **not QD clearance**. In particular, `making-water-safer` and `salt-beef-salt-pork-age-of-sail` retain an explicit "NOT independent safety review" caveat and an unresolved human-review docket.
3. Compares **citation multiplicity per literal source ID**, not merely aggregate citation count; rejects missing or malformed tokens and removed source-use declarations. Modified reading-scope descriptions and new source references require human adjudication.
4. Rejects missing heading anchors, duplicated heading IDs, substantial reading-depth losses (below 95% of the frozen authored body), lost original related links, weakened safety gates or dropped four QA #157 Start Here escalations. Even smaller decreases in reading depth and removed outbound links become explicit human-review items.
5. Refuses a change to any of the eight contributor source inventories or crosswalk without separate QD/source adjudication. Existing crosswalk's **32 URL-alias human-review groups** and **15 repeated source-ID groups** are not silently resolved. A conservative URL alias is not permission to merge contributor reading scopes.
6. Always returns process exit **2**, and `INVALID_HARD_HOLD` or `REVIEW_REQUIRED_HARD_HOLD`, with all approval/revenue booleans hard `false`.

## Exact local test evidence

- **66/66 new R364 tests PASS** using locally executed Python source and test bytes that match committed Git blob IDs: tool `7c1ddd1a51c8087464f090874300c725d58d7272`; tests `696f2ca9a8fbe2ea787a1fbb3cd5d267e307fb4d`.
- Four tests create actual **disposable, synthetic Git repositories** with 35 article + 6 tool pairs and test complete-ref parity, citation removal, source mutation and safety-gate weakening. All these repositories are local fixtures; none contains the actual 41 original manuscripts.
- **585/585 inherited locally re-executed isolated R355–R363 tests PASS**. **651** passing tests across two separate suites. These are **not native full-repo validation/build**.
- `python -I r364_integrated_release_firewall.py --repo-root /mnt/data/nonexistent` -> exit 2, `INVALID_HARD_HOLD`, `AUTHENTIC_GIT_CHECKOUT_REQUIRED`. Python compilation passed.
- The local runtime cannot resolve github.com for a trusted full checkout. Thus the real 41-document R364 Git-object comparison, `preparedness/tools/validate.py`, `build.py`, complete native suite, 50 WordPress-ready draft/50 private preview exports, source-to-render browser checks, physical printing, hosted CI on exact R364 commit and qualified QD/safety checks are **NOT EXECUTED / NOT APPROVED**.

## Independent review and source constraints

Independent QA #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` (unremediated); its dependent fix #2205 at `bbcf1859768624c611df4abadc564c18247cf32a`; home lead #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. All remain independent drafts; neither their approval nor a live release is implied. R363 taxonomy already protects **27 of 35** article safety gates; QA #157's 18→22 observation applies to its separate older branch. Existing 15 editorial conflicts, original source-identity disputes, 17 high-risk Article #15 / Tool #104 obligations and Tool #104 privacy, no-JS, child-card, 911 and print accessibility holds remain.

## Conversion-first handoff — one audience, no speculative paid CTA

**Social intent:** household emergency contacts, school pickup and family reunification. Grok owns actual creative assets and posting; Praxxis verifies them through existing TASK-008. Only a genuinely published `asset_id`, topic fit and approved destination can establish the proposed acquisition link.

**Free destination:** already public `https://finalvestige.com/preparedness/` → its agency-linked "Create a household emergency plan" resource. Proposed on-site CTA (NOT deployed): **Start With Trusted Preparedness Resources**. Emergency resources must remain accessible without a purchase or signup.

**Optional tool:** private Tool #104 is **not approved or available as a public offer**; its cited content, privacy, child-use, print and JavaScript fallbacks require independent review and device proof. Separate editor-held status-only sheets must not be labeled public products.

**Optional paid pack:** no authenticated, rights-cleared, genuinely payable FV Preparedness SKU/merchant receipt, checkout, delivery/refund terms or founder approval established. **NO PAID CTA**. Founder/Commerce to authenticate a specific existing product before mapping an upsell; otherwise maintain free-only guidance.

**Measurement contract (Claude/Commerce):** verified human sessions by published Grok `asset_id` and `utm_campaign` → landing visit → relevant CTA → confirmed lead when applicable → independent merchant paid order → fee/refund-adjusted net revenue. Required KPI: net revenue / 1,000 qualified human sessions, 7/30-day cohorts with tiny-sample caveats; missing evidence is **unknown**, never zero, never a sale inferred from a click. Do not install duplicate scripts or activate analytics without approval.

**Next controlled step:** authenticated source checkout, execute direct Git-object R364 audit against actual full ref and native validation/build; review all 41 source dockets, then independent QD/privacy/source and publisher approval. No merges, CMS writes or production changes authorized.
