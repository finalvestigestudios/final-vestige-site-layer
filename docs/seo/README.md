# docs/seo - competitor-inspired SEO program (2026-11-02)

Branch `feature/seo-competitor-implementation`, cut from `feature/experience-2-living-archive-sprint5` @ `9a74ecda`.

| File | What it is |
|---|---|
| `01-COMPETITORS-AND-GAPS.md` | Five SERP-observed competitors (unverified by a tool) and gap observations. **Ahrefs returned "Insufficient plan" for every call; no keyword, traffic, ranking or Search Console number exists in this folder.** |
| `02-BASELINE.md` | Live-site baseline from a 140-URL crawl and a read-only wp-admin snapshot |
| `03-INTERNAL-LINK-MAP.md` | Clusters, hubs and exactly which pages link where; what was deliberately not done |
| `04-CHANGESET-DIFFS.md` | Exact before/after of every change (generated) |
| `SEO_IMPLEMENTATION_LEDGER.md` | What was applied, hashes before/after, public-site verification, rollback (generated) |
| `05-GSC-MEASUREMENT-PLAN.md` | Search Console before/after plan with groups and decision rules fixed in advance |
| `evidence/` | Crawls before and after, pre-edit snapshot, change set, execution results, verification |
| `tools/` | `crawl_public_site.py`, `build_changeset.py`, `build_ledger.py` |

Pre-edit raw post/page bodies (rollback copies) are outside the repo: `Projects/fv-release-backups/seo-2026-11-02/`.

Rebuild: `PYTHONUTF8=1 python docs/seo/tools/build_changeset.py` (from the snapshot), then after applying, re-crawl and `build_ledger.py`.
