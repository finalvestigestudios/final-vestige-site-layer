# R379 — 35-article original Git-object / citation-scope integration gate

**2026-11-14 PT · Preparedness Issue #136 · DRAFT / HARD HOLD · NOT PUBLISHED.**

## Scope and custody

Read-only engine `preparedness/tools/r379_all_article_source_scope_gate.py` and 60 dedicated synthetic/adversarial tests. This extends R374–R378 from selected original objects and Food Article #11 to a deterministic **entire original 35-body / 35-metadata / nine-branch** validation pathway. It uses original blob SHAs, not a silently selected “latest” Shelter version. It checks:

- Original object and branch pins, 35 paired article identities, exactly nine unresolved original path conflicts and no selected original Git blob;
- Every original body variant paired to metadata **from the same branch**, all `{{cite:id}}` markers compared with that article's `source_use` entries, and non-empty article-specific and source `supports` reading scopes;
- Source-owner fragment for the **same contributor branch**, using BASE registry **only as an explicit fallback**, never borrowing a different cluster's source verification;
- Source HTTPS/host sanity, machine-vs-human source-status separation, article draft/safety pending states, relative word-count evidence per original version, and canonical URL duplicates across different slugs;
- Unresolved `{{link:slug}}` links separately as review warnings; no assumption that all source-shared URLs are duplicate *article* permalinks;
- Fail-closed CLI with unconditional **exit 2**, even when machine custody passes. **Machine custody is not a Qualified Domain PASS.**

Pinned original authoritative Git blobs:
- R374 object manifest `5e7d9a8972872c82b4bc46ac13aab18883d8149a`;
- 2026-11-04 article/source owner crosswalk `d62e493a67dedd23e04cfdf3cce762ef933c6bf9`;
- BASE source register `b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77`.

The tool expects a trusted **complete Git object checkout** with all original contributor objects available through read-only `git cat-file blob <SHA>`. It reads no WP credentials and creates no output files. Missing original inputs or objects cause a nonzero hard hold. Original manuscripts, metadata, sources, taxonomy, links and release settings were not changed.

## Local exact-code execution (synthetic, not an authentic integration run)

- New R379 Python adversarial suite: **60/60 PASS**, including 35 distinct per-article unknown-citation injections, source registry fallback, paired branch variants, nine conflict retention, tamper detection, draft/safety gating, depth-warning and duplicate path checks.
- `python -W error -m compileall -q preparedness`: PASS for archived local additive tool/test subset.
- Tested and committed Git blob of new tool: `a743a03ab367188c297e94a0eab3ff4112bd7bed`.
- Tested and committed Git blob of new 60-test file: `218b1637667fe21c08c3341d9ea6a30c886344d9`.
- Read-only native CLI on incomplete local checkout: **exit 2**, manifest missing. Local git clone still blocked by DNS.
- R374, R375, R376, R378 inherited isolated tests independently passed **52 + 62 + 105 + 81**, but R377's separate inherited tests were **not runnable on this partial fixture** (72 fixture-dependent errors). Do **not** report a combined full-native pass.
- Native `preparedness/tools/validate.py`, `build.py`, full repo suite, WordPress-ready authentic 50 draft + 50 preview export pairs: **NOT EXECUTED**. Hosted CI: no accepted success. Independent food, child-privacy, emergency, physical print and QD review: **NOT APPROVED**.

## Independently observed coordination

Original seven Claude cluster HEADs and both Shelter successor HEADs were freshly read from GitHub on this run, all **identical** to R374's exact nine pinned SHAs. QA #157 remains open/draft `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture #169 remains open/draft `e9cd7766dac59d47ab467d8945269b9146c2aef5`. PR #169 still has the canonical-directory `_dup_test.json` write/delete in its unmerged test; separate dependent remediation #2205, open/draft, remains for independent native acceptance. Homepage #1689 remains owner-isolated; no homepage or analytics code included here.

## Business source-of-truth #820 — conversion acceptance, strictly staged

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| One **existing** FV-owned Preparedness digital pack → paid order | No authenticated FV-owned, rights-cleared, payable SKU with tested delivery/refund policy | Founder/Commerce independently confirms actual merchant product, license, delivery, fees/refund route **before** any optional paid CTA | **HOLD:** no SKU or paid order verified | Founder / Commerce |
| Real published Grok **family communication** post → free existing Archive | Actual topic-matched `asset_id`, hook, rights and permitted tappable destination missing | Praxxis QA of ONE already-published asset, Grok controls production; propose existing https://finalvestige.com/preparedness/ only if matched | **UNVERIFIED:** do not invent asset or visitor session | Grok / Praxxis |
| Free household official-source Archive → optional Family Reunification Card Tool #104 | Private card remains child-privacy, print, emergency and accessibility hard hold | Preserve free FEMA/agency links; keep Tool #104 off-page pending QD and print/cutout review | **HARD HOLD**; no new tool download enabled | Preparedness / QD |
| Qualified-human landing → relevant CTA → confirmed lead → merchant-confirmed order → realized net revenue | No authenticated joined campaign sessions, merchant receipts, refunds/fees or 7/30-day cohorts | Claude measures existing approved path only; **no new script**; show missing attribution, tiny-n warnings and distinguish affiliate clicks from sales | **NOT COMPUTABLE** net revenue / 1,000 qualified-human sessions | Claude / Commerce |

Unposted contextual CTA candidate: **“Start With Trusted Preparedness Resources”** → existing free `/preparedness/`. No paid CTA without independently authenticated offer and founder release approval. No retired water offers, unreviewed emergency/medical/food processing advice, misleading claims, private card deployment, tracking, social posts or queue changes.

## Reviewer / next gate

Complete a trusted source checkout with all nine original branches and compare exact HEADs again. Run:

```bash
python -W error -m unittest discover -s preparedness/tests -p 'test_r379*.py' -v
python -I preparedness/tools/r379_all_article_source_scope_gate.py --repo .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The R379 CLI returning 2 is intentional and cannot become a publication permission. Review any source-origin mismatch or 35-article citation errors, R375's five source-evidence differences and R376's nine version conflicts, and physically review Tool #104. Keep original/preview exports private until independent approval. **No merge, CMS, navigation, social, email, analytics, affiliate/merchant activation, spend or public publishing.**