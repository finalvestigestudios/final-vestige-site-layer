# R308 · Shelter follow-up fork and unresolved internal tool identity

**Preparedness Archive only · DRAFT / HARD HOLD · 2026-11-12 UTC.** Integration issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136); conversion decision [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). This dossier compares authenticated GitHub source blobs. It does **not** publish, merge, adjudicate medical/emergency safety or independently approve citations.

## Newly detected parallel Shelter lineage

The seven designated canonical Claude branches still compare **identical (0 ahead / 0 behind)** to frozen R200, including original Shelter `claude/prep-shelter-5e1e0e` at `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`. But that is *not* the entire Shelter history:

| Branch | Exact observed HEAD | Relationship to frozen Shelter |
|---|---|---|
| `claude/prep-shelter-continuation` | `ac8625faf30dd5538fadc31e06cb5a2cea1defae` | 6 commits ahead, 0 behind |
| `claude/prep-shelter-followup-evidence` | `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` | 9 commits ahead, 0 behind |
| Follow-up compared with continuation | same exact HEADs as above | 3 commits ahead, 0 behind |

R307 integrated HEAD: `6a8de471668f37f6dbaffa21d52d0abf6290e55e`. These branches are **additional sibling/descendant source candidates**, *not* substitutes for the seven canonical frozen contributor heads, and no automatic cherry-pick is authorized.

## Authentic sixteen-file comparison

The read-only `r308_shelter_followup_fork_hold.py` pins all 16 paired Git blob IDs and the branch identities. Relative to the later Shelter follow-up:

- **4/16 byte identical:** both files for `home-fire-escape-worksheet` and both for `power-outage-planner`.
- **5/16 CRLF/LF normalization only**, independently observed by retrieving and normalizing both actual versions: `home-fire-escape-plan.body.html`, its metadata, `outage-heat-cold-generators.body.html`, its metadata, `sources/fragments/shelter.json`. A different Git blob **alone** does not imply a changed claim.
- **7/16 substantive/source-or-content changes after newline normalization:** `family-communication-plan` body/metadata (2); `shelter-or-evacuate` body/metadata (2); `reunification-plan` body/metadata (2); `taxonomy.json` (1).
- The tool-body change is materially larger than the two article wording changes. The follow-up tool rewrites card/worksheet presentation and replaces or adds citation identities; **do not infer correctness, safety, accessibility or functional parity without running the actual source/tool and independent review**.

**Specific newly evidenced integration conflict:** In the integrated article bodies `family-communication-plan` and `shelter-or-evacuate`, internal links use `{{link:family-reunification-card|...}}`. In the later contributor branch these two tokens are corrected to `{{link:reunification-plan|...}}`. The integrated taxonomy lists **both** `family-reunification-card` and `reunification-plan` as draft tool slugs; the compared contributor taxonomy instead retains the latter and drops the former. The actual integrated tool payload in this comparison is named `reunification-plan`. A taxonomy placeholder is not an executable or verified published tool. **Verify rendered link destinations/real 41 exports and resolve the canonical identity before publication.** No URLs were renamed in this sprint.

The later follow-up changes two linked article target tokens, while emergency instructions remain surrounded by source/safety review obligations. No finding here settles the 14 frozen-to-integrated article-body differences, 12 metadata changes, hazardous-water Article #7 review, or Tool #104 child privacy / printing / no-JS / emergency-message verification.

## Executable bounded controls

Two added Preparedness-only Python files form an isolated regression gate. The validator requires the exact R307 predecessor blob, inspects 16 integrated file Git identities, rejects changed/absent/symlink source inputs, rejects swapped paired blob IDs and source paths, checks branch identities, enforces existing upstream hard holds, and **never returns a release authorization**. The later branch's bytes were reviewed through the authenticated connector; they were not run locally, nor does the gate claim that remote blob comparison independently proves claim-level accuracy.

**Local byte-identical committed-scope evidence:** 120/120 synthetic adversarial Python tests pass; `python -m py_compile` passes. Local test and implementation SHA-1 Git blob identities match the committed GitHub versions. On an intentionally incomplete local checkout, the native gate returns `INVALID_HARD_HOLD` (exit 1), as designed. Complete authenticated `validate.py`, `build.py`, 41 WordPress draft exports, inherited 1,061 prototype tests, live source link checks and qualified QD/safety/privacy review remain **not executed / not approved**. Container GitHub DNS resolution remains unavailable. Do not call these synthetic tests a native archive PASS.

QA review [PR #157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) remains draft; [PR #169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) still has a `test_register_fragments_cannot_duplicate_ids` test writing `_dup_test.json` into the live source fragment directory despite isolating the other fixture. Do not rewrite the independent QA branch. Homepage lead [PR #1689](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1689) remains untouched.

## Conversion-first owner queue · no fabricated revenue

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Free agency-referenced family emergency plan | Grok asset → existing free `/preparedness/` page | No verified matching published `asset_id`/mobile destination | Grok/Praxxis supply real post URL and authorized `utm_content=asset_id` placement; inspect mobile without release | **NOT VERIFIED** | Grok/Praxxis |
| Free practical printable contact tool | Free guide → optional Tool #104 | Two conflicting internal link slugs, revision fork and no qualified emergency/privacy/no-JS review | Resolve one canonical tool slug; assert render/keyboard/print/privacy/safety with independently approved content | **HARD HOLD** | Preparedness integration + independent QA |
| Optional paid emergency toolkit/pack | Free guidance → checkout | No FV-owned or licensed, rights-cleared, audience-matched, actively purchasable Preparedness SKU with merchant/delivery/refund proof | Founder/Commerce authenticates **one existing SKU** before drafting a paid CTA or conducting checkout acceptance | **NO APPROVED OFFER; NOT LIVE** | Founder/Commerce |
| Purchased product | Qualified human session → verified paid order → net revenue | Merchant receipts/settlements, fees, refunds, qualified sessions and attribution absent | Claude/Commerce reconcile only consent-respecting 7/30-day cohorts; distinct visit, CTA, lead, checkout and paid events | **NOT COMPUTABLE** | Claude/Commerce |

Draft free CTA, pending review: *“Make a plan for how your household will reconnect. Start with free official preparedness resources.”* No gated emergency advice, no old water freebie, no unapproved Legacy Triage upsell, no unapproved paid landing or merchant changes.

**Next allowed work:** run real source/rebuild once authenticated checkout is available, resolve the live-vs-follow-up link/tool identity, obtain independent Tool #104 and highest-risk Article #7/#15 safety assessments, then seek founder-governed release consideration. All publishing, CMS, navigation, measurement, merchant, affiliate, social, email and spending actions remain prohibited.
