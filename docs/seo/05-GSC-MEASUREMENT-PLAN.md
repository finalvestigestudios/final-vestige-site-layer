# 05 - Search Console before/after measurement plan

No Search Console or Ahrefs figures were available when the change set was prepared, so **there is no baseline number yet**. This plan says what to capture and how to judge it. Nothing below is a prediction.

## Step 0 - make the baseline exist (do before or the same day as the first live change)

1. Confirm the property is verified for `https://finalvestige.com/` (homepage head has no `google-site-verification` meta; DNS or file verification may exist). If not verified, verify it. Impressions cannot be recovered retroactively beyond what Google has already stored for a verified property.
2. Export Performance > Pages and Performance > Queries for the **28 full days before the go-live date** (`web`, all countries, all devices) as CSV. Also export Pages by device (mobile/desktop). Keep exports in `docs/seo/evidence/gsc/` named `gsc-before-<from>_<to>.csv`.
3. Export Indexing > Pages (status counts) and Links > Internal links (top linked pages) the same day.
4. Re-run `tools/crawl_public_site.py` after the change set is live to record titles, descriptions, JSON-LD and internal-link counts (`evidence/crawl-after-<date>.json`).

## Page groups (fixed now so they cannot be chosen after seeing results)

| Group | Pages | Change |
|---|---|---|
| T | the 18 pages + 22 posts with new SEO titles | title only (headline unchanged) |
| D | the 16 pages + 5 posts with new descriptions | description only |
| L | the 8 + 3 posts, 2 guides and 5 case pages with a Related-reading block | internal links added |
| C | all other posts and pages (including page 6, never edited) | control |

## Checkpoints and what to compare

Compare the same weekdays and equal-length windows: **days 1-14 (indexing noise; do not judge)**, **days 15-42 vs the 28 days before**, **days 43-70 vs the 28 days before**.

| Metric (per group, from GSC) | Reading |
|---|---|
| Impressions | Whether the page appears for more queries; expected to move before clicks |
| Average position (impression-weighted) | Movement is informative only for pages with at least ~100 impressions in both windows |
| CTR at fixed position band (use `gsc-ctr-by-position` or the Positions filter) | The cleanest read on title/description changes (group T and D) |
| Clicks | Outcome, but dominated by impressions and seasonality |
| Internal links report: inbound counts for the Failure Chain and Archive Trail guides | Confirms group L was crawled |
| Indexing: pages indexed, "Crawled - currently not indexed" | Watch for new exclusions after body inserts |

## Decision rules (written before data exists)

- A change is "supported" only if group T/D/L moves in the intended direction **and** the control group C does not move the same way in that window.
- A drop in CTR at a stable position for group T after day 15 means the new title lost appeal: roll back that title (rollback values are in the ledger).
- No conclusion before day 42; no conclusion about rankings for any page with fewer than ~100 impressions per window.
- Site age matters: most posts date from 2026-08-16 onward, so impressions are still ramping; the control group, not the pre-period alone, is the comparison.

## When Ahrefs or Semrush access is available

Re-run: competitor overlap for the five domains in `01-COMPETITORS-AND-GAPS.md` (replace the SERP-observed set with a measured one if it differs), content-gap keywords per cluster, and top pages. Record the tool, date, country and the plan limits used.
