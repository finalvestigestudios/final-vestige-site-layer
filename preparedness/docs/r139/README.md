# R139 — Independent 35-article reading-depth and citation census (DRAFT / HOLD)

**Scope:** Final Vestige Preparedness Archive **#136 ONLY**, founder conversion coordination #820 and business charter #818. Stacked on R138 PR #1057 at immutable SHA `5ea94442b56ec040e8846d784032d38200cd7dae`. **No publishing, merging, CMS writes, menus, analytics, affiliate activation, products, email, social posts or spending authorized.**

## Actual content inspection, not synthetic-only

On 2026-11-05, all 70 article files (35 real HTML body files and 35 metadata files) were read directly via the authenticated GitHub connector at the exact immutable R138 SHA. Counts were taken from the full source text without modifying a single article:

- **35/35 DRAFT articles**; 35/35 exact source-use keysets match the distinct citation IDs in the article body (no missing metadata reading scopes).
- **2,000 actual citation-token occurrences** across the 35 article bodies; **385 article-specific source-use bindings**.
- **Approximately 104,715 prose words** across all 35 articles under a Unicode-aware strip-HTML-and-citations counter. This is deliberately an estimate; it is not the same algorithm as existing editorial word-count tooling and is **not** a readability or safety claim.
- Historical safety labels: **29 pending, 4 not-required, 2 previously marked approved**. Those two historical labels do **not** constitute independent emergency-safety or QD approval, and must not be upgraded. The corpus remains HOLD.
- The smallest three draft articles by this approximate counter are `two-week-water-storage` (1,904), `water-advisories-explained` (1,910), and `homemade-water-filters` (1,951). Shorter depth is a **review priority**, not an instruction to pad content.
- No article citation/metadata mismatch was found by this focused API inspection. This finding **does not** verify individual source relevance, live links, 32 source-group interpretations, accessible rendered citation visibility or medical/food/electrical safety.

The new machine-readable census freezes the per-article actual observed approximate counts; the 75% word-count floors are a **gross truncation tripwire**, not a quality score. **R133's existing exact 80-file Git blob custody remains mandatory and runs first**; R139 never replaces, weakens, or re-baselines it.

## What is BUILT / TESTED vs NOT VERIFIED

New additive files: `docs/r139/article_depth_census.json`, `tools/r139_article_depth_gate.py`, `tests/test_r139_article_depth_gate.py`. No modification to article bodies, source registers, crosswalk, safety states, taxonomy, WordPress builder or release controls.

**Locally TESTED:** `python -I -m unittest discover -s preparedness/tests -p 'test_r139*.py'` — **116/116 synthetic/adversarial tests pass**, testing each of 35 article entries against independent depth loss, citation loss and unauthorized publication, plus baseline structural and approval-forgery cases; Python compilation passes. The API reads independently inspected all 35 real articles, but that is **not** a native R133/R139 integrated PASS.

**NOT VERIFIED:** Native full 35-article R139 execution, the original `validate.py` and `build.py`, complete repo regression suite, WordPress draft build, complete rendered visual/mobile QA, hosted CI, independent qualified safety/source reviewers and QD. Local git clone remains blocked by DNS resolution; historical GitHub Actions jobs failed before runner steps, not as code test results.

Trusted checkout commands:
```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r133_snapshot_gate.py --root .
python -I preparedness/tools/r138_cross_lane_reconciliation.py --root .
python -I preparedness/tools/r139_article_depth_gate.py --root .
```
Any missing dependency, unchanged historical HOLD, outdated source or failed custody must keep the release blocked; do not infer publish authority from test success.

## Contributor / independent QA reference audit

Compared the seven canonical frozen contributor SHAs against the live branches at 2026-11-05: Start Here `2122d856` and Shelter `5daeaf2d` are identical; Food diverges `e9cd7766` vs `f911ff7a` (2 files); Health is ahead 1 commit `d2212d0c` → `d5ef5baf` (1 file); Historical Food is ahead 1 `2acf65ca` → `67e116e5` (7 files); Historical Home is ahead 2 `f654e600` → `7504a5f0` (8 files); Historical Field is ahead 1 `a5ce8a62` → `4e5caf81` (5 files). Historical Food's eight jerky source-ID changes remain under S-7 and must not be auto-merged.

Independent **PR #157** remains draft at `7d1ae6b8` (electrical-drill and refrigerated-medication wording need qualified review). Synthetic-fixture **PR #169** remains draft at `e9cd7766`; its remaining shared-directory write has a separate follow-up **PR #973** at `4d40996a`. Homepage #49 `10495883` and #604 `bdf01b4a` remain outside this branch and were not changed.

## Conversion-first Preparedness acceptance / proposal (no offers activated)

**ONE high-intent audience:** parents/caregivers planning school pickup, emergency contacts and family reunion. Proposed existing **free** destination: Household Emergency Plan (currently unpublished draft HOLD). Proposed optional practical **free** resource: existing Family Reunification Card printable, pending source, privacy, print and mobile QA. A matching currently purchasable, rights-cleared FV paid Preparedness SKU has **not** been verified, so **no paid CTA, Payhip checkout or price may be staged as live**. Retired water products must not be resurrected.

**Draft-only CTA copy (no live deployment):** “Make your household contact plan. Read the free Household Emergency Plan. After review, you may also download a printable Family Reunification Card to complete privately.” **Do not put an email gate on emergency-safety information.** Any future paid practical pack must be relevant, optional and authenticated by Growth/Claude using real Payhip product ID, merchant title, price, rights, fulfillment and refund evidence. Until then paid action = HOLD.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Owned paid Preparedness pack (not selected) | Offer → confirmed purchase | No verified matching live SKU, rights or working merchant fulfillment | Authenticate listing, price, checkout, download delivery and refund policy before any paid CTA | **FAIL / HOLD: product unverified** | Growth / Claude / founder |
| Free Household Emergency Plan | Social → landing/read | Article source and emergency-safety review pending | Qualified review, safe source links, prominent useful content, mobile 360/390/768px and no signup wall | **DRAFT / NOT VERIFIED** | Preparedness / independent QA |
| Existing family-reunification printable | Guide → optional download | Download, personal-data handling, printing and phone layout untested | Local-only input where feasible, no tracking of household details, 2-page print and large-text checks | **NOT TESTED** | Preparedness / Site QA |
| Grok/Praxxis TASK-008 | Actual social asset → guide | No authenticated Preparedness asset_id, permalink or platform-approved URL | Grok supplies existing published asset ID and rights; Praxxis QA; map asset_id/utm_campaign to approved page; do not assign content | **UNVERIFIED** | Grok / Praxxis |
| Merchant and attribution | Verified paid order → net | Qualified sessions/attributed paid orders/refunds/fees unavailable | Tie unique asset → human qualified session → CTA → confirmed order → fees/refunds; 7/30-day tiny-sample caveats | **NOT COMPUTABLE** | Growth / analytics |

**Release remains DRAFT / HOLD**, including source adjudication of 32 groups and all outstanding high-consequence medical/electrical/food/water instructions. “Approved” historical metadata is **not** QD PASS. This report does not authorize production release or commercial activation.
