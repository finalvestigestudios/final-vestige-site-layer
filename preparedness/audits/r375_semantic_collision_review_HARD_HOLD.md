# R375 — Original Preparedness Source Identity and Reading-Scope Collision Review

**Status: DRAFT / HARD HOLD. Issue #136. Commercial coordination #820 / charter #818. No publication permission.**

## Authenticated upstream custody, checked 2026-11-14

Built directly against R374 draft PR #2525 (`5e2c12bb4a95eb913a3ed3ab6b53c8c30dac6b16`). The Git-blob identities of its two original JSON inventories are pinned in the new gate:

- Objects: `5e7d9a8972872c82b4bc46ac13aab18883d8149a`
- Sources: `24b49f0a423119c2f612455f021669709a3f22b5`

All nine original Claude/Shelter refs were compared with their pinned commits in this run: **9 identical / 0 ahead / 0 behind**. Do not interpret an unchanged SHA as independent safety approval.

**Source collision classification:** 280 source-record occurrences, 203 distinct IDs, 46 repeated source-ID groups. Of the repeated groups, **41 have byte-equivalent relevant source fields**, while **5 contain differing reading-scope or descriptive evidence**. The five human-adjudication IDs are:

| Source ID | Divergent fields | Handling |
|---|---|---|
| `fsis-power-failure` | verified_on, supports, notes | Retain both food and shelter scopes |
| `loc-pioneer-diaries` | publisher, verified_on, supports, notes | Preserve archive reading limitations and date uncertainty |
| `loc-prairie-traveler` | publisher, supports, notes | Preserve historical attribution and read extent |
| `nchfp-home` | supports, notes | Keep modern food vs historical context distinct |
| `nchfp-jerky` | publisher, supports, notes | Require qualified food-safety scope review |

**17 URL groups** are legitimately shared by multiple distinct source IDs, not 17 duplicate article landing routes; do not collapse their citations. The full original `supports` and `notes` evidence and all branch/fragment/blob identities are preserved in `r375_original_semantic_collision_review_HARD_HOLD.json`. **9 divergent Git-object paths** in the four Shelter article body/meta pairs plus source fragment require human diff review; none was auto-selected. **0** original source-record occurrences have `human_link_check=true`; this is not evidence that a link is broken.

The new read-only Python gate confirms each of 280 individual source-origin fragment blob identities against the independently inventoried original Git objects, checks record and alias coverage, blocks source URL scheme/credential/redirection ambiguity, rejects changed source reading text, duplicate IDs and claimed QD/PUBLISH approvals, and returns **exit 2 even for a clean custody match**. There are no modifications to manuscripts, citations, routes, safety states, source register contents, or paid links.

## Verification and release blockers

- **62 new R375 synthetic, adversarial Python tests PASS; 114 combined R374 + R375 isolated local tests PASS**, Python compilation PASS. Tested files will be independently compared to GitHub blob identities before final reporting.
- **Full native `validate.py`, `build.py`, and complete test suite NOT RUN**. Authenticated full checkout unavailable in local runner because GitHub hostname DNS resolution fails.
- **Authentic 35-article integrated manuscript reading depth, 50 WordPress private draft + 50 preview pairs, human link/source verification, child-data/privacy/medical/emergency safety, QD review: NOT CLEARED.**
- Draft QA #157, fixture #169 and dependent fix #2205, homepage lead #1689 remain separate branches and unmerged. #169's existing fixture-writing hazard requires native retest with #2205.
- **No QD PASS.** Every result is an input-custody decision, never publication readiness.

## One high-intent reader → free guide → optional tool → purchase evidence

- **Audience/topic:** family emergency contacts and household reunification. A legitimate already-published Grok video must be independently matched by Praxxis (actual immutable `asset_id`, platform link, hook, publication date and permitted UTM/mobile destination). No matching asset authenticated here.
- **Free public route:** `https://finalvestige.com/preparedness/` ; draft, unposted CTA: **Start With Trusted Preparedness Resources**. Do not gate emergency advice.
- **Optional practical tool:** private Family Reunification Card #104; print/cutout, no-JS, child privacy, full warnings and emergency guidance remain HARD HOLD. Not advertised as live download.
- **Optional paid pack:** NONE AUTHENTICATED as owned, rights-cleared, genuinely purchasable, relevant and deliverable. Founder/Commerce must verify exact SKU, rights, checkout, actual delivery, customer support and refund terms; no invented offer or paid CTA.
- **Measurement:** existing legitimate reporting only; Grok `asset_id`/campaign → qualified-human landing sessions → content-matched CTA → confirmed opt-in (if any) → independently confirmed paid order → fees/refunds → realized 7/30-day net revenue per 1,000 qualified-human sessions. No paid conversion/denominator or net revenue verified. Avoid new scripts, tracking bypasses, visitor identifiers, sales assumptions and misleading urgency.

**Owners:** Preparedness integration/QD source integrity; Claude core website/analytics, Grok production/posts, Praxxis independent asset QA, founder release and commerce. No merge, public publishing, CMS/navigation writes, social/email posting, merchant/affiliate activation, spending or measurement deployment.
