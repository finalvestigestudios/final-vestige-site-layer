# Final Vestige implementation ledger

Single current record of workstreams, so work is not duplicated and release attempts do not conflict.
**Last updated 2026-11-02.** Facts below were read from GitHub, the live site, or run locally on that date; nothing is inferred.

## Production status

**LIVE (2026-11-02): the Experience 2.0 flagship homepage** replaced the old Studios hero on page 6; verified anonymously on finalvestige.com. Record: `PR604_LIVE_RELEASE_RECORD.md`. The paragraph below is the state *before* the release and is kept for history.

**Reconciliation (2026-11-02, later):** page 6 block 1 is the approved replacement (SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`, 108,155 B), independently confirmed by ChatGPT; the anonymous public re-verification was re-run and is identical to the first record. PR #604 stays open, draft and frozen at `bdf01b4a3e`; the corrected performance record was posted to it as an addendum (comment 6594692945). **Performance policy (founder decision):** the binding benchmark is real throttled mobile LCP at or below 2.5 s (about 1.9 s measured; 4.58 s was a proxy figure, 8.4 s is Lighthouse `simulate` on the live page; see `PR604_MOBILE_LCP_FOLLOWUP_DIAGNOSIS.md`); non-block optimization proceeds in a separate PR, one measured reversible change at a time, without disabling instrumentation.

**Release: FREE EBOOK in the active header (2026-11-03, ~06:55Z).** Live edits to two template parts, authorized by the founder's production directive: `assembler//header` (the active header; the saved menu ID 5 is not used by it) and `assembler//fv-archive-index-overlay` (the mobile/tablet menu). Desktop at 1280 px and wider: a gold "FREE EBOOK" pill in the primary navigation before Dispatch (`/focus/`). Narrower: a full-width gold-outlined strip under the header ("FREE EBOOK / The Seven Day Focus Fieldbook"), plus a "Free Ebook" entry in the overlay's Primary list. Both are hidden on `/focus/`. Pre-change rendered header saved as `fv-release-backups/header-rendered-pre-ebook-2026-11-02.html` (29,749 chars, SHA-256 `be2a2d48bec897048f0e0c324ad4cd2c2bfbdcb8ba3775140040eac2898ca301`); WordPress keeps template-part revisions. Verified on the live site: only the intended additions differ from the backup (cursor block and icon script byte-identical, 2,094 added CSS characters), no horizontal scroll at 360/390/768/1024/1279/1280/1440/1920, pill 113x32 px at 1280 and up, strip 62 px at 390, keyboard reaches the pill in 12 Tabs with a 2 px focus ring, axe on the header at 1440 reports 0 violations, the overlay link opens `/focus/`, no CLS. Rollback: delete the added `wp:navigation-link` (class `fv-nav-free-ebook`), the `fv-ebook-strip-wrap` group and the appended CSS block in the header, and the "Free Ebook" link in the overlay (or restore the previous revision).

**Sitemap recheck (2026-11-03, 14:38Z): the five 2026-11-02 posts are still NOT in `sitemap-1.xml`.** Provider: Jetpack Sitemaps (`jetpack-16.4-beta`), index `/sitemap.xml`, advertised in `robots.txt`; the module rebuilds on WP-cron every 12 hours. `/sitemap.xml` (x-ac MISS, so read from origin) still lists `sitemap-1.xml` with lastmod 2026-11-03T01:48:13Z and `image-sitemap-1.xml` with 01:51:06Z, so no rebuild has been stored since that build, about 50 minutes past the expected 13:48Z. `sitemap-1.xml` has 124 URLs (x-ac STALE at the edge), newest lastmod 01:48:13Z, none of the five posts. `news-sitemap.xml` (generated on request) does list all five. The posts have correct canonicals and no noindex. Not purged, not toggled. A cron run that has not fired yet is the likely reason (WP-cron runs on site traffic); recheck again later or request indexing in Search Console. No Search Console access was available.

**Sitemap and FREE EBOOK follow-up (2026-11-03, 14:54Z).** `sitemap-1.xml` fetched with x-ac MISS (fresh from origin, not the edge cache) still has 124 URLs, newest lastmod 2026-11-03T01:48:13Z and none of the five posts, so the stored sitemap really has not been rebuilt (it is not only a stale edge copy). The WordPress.com site tools available to this session expose no operation to read the WP-cron schedule or to trigger a Jetpack sitemap rebuild (only settings, newsletter, backup, scan, monitor and similar), and the in-app browser is blocked by a human-verification check that was not bypassed; so the overdue cron event could not be inspected and no supported refresh could be invoked from here. Nothing was purged or toggled. Open item for the site owner: wp-admin cron check or a Search Console indexing request. FREE EBOOK navigation re-verified publicly (home at 390/768/1280/1440, a post at 390/1440, mobile overlay link to `/focus/`, keyboard 12 Tabs with focus ring, axe 0 violations on the header): task closed.

**BLOCKED: hosted GitHub CI (2026-11-03, noted 15:10Z).** Jobs are not starting on any workflow: annotation "recent account payments have failed or your spending limit needs to be increased"; 13 jobs across 6 workflows blocked since 14:37:15Z, last executed success 14:27:59Z. Evidence and the owner checklist are in `GITHUB_ACTIONS_BLOCKER.md`. Owner action: GitHub billing, then re-run on the exact reviewed commits. No pushes are being made to avoid more blocked runs.

**RESOLVED: hosted GitHub CI (2026-11-03, ~15:58Z).** Cause was the Actions budget at 100% (billing page screenshot); the founder raised the budget. Re-run on PR #798 head `40c891e9c5c0c400606644307ffa7d8d6be30a18`: both `verify` check runs (pull_request run 41667870123 and push run 41667853565, attempt 2) completed success with all steps executed. That is hosted CI on that exact head; it is not independent review, and page 2017 is still a private draft.

**Preparedness repair (2026-11-03):** branch `integration/preparedness-custody-repair-20261103` at `6a6c63bc86c9fbb08f1e0c9a7ccac7618e6a20e5` (pushed, #584 untouched). `validate.py` 59 to 0 errors; local suite 93 to 68 failing names (54 Windows-environment); real `private_release_preflight.py` still fails closed at step 3. Nothing published, `may_publish` false. Open human decisions: three-day-kit medication wording, start and shelter files matching no reviewed contributor head, a successor census for the 35+1 gates and R23, a named qualified reviewer, hist-field ref map, hist-food readings. Wave 1 candidates (non-actionable history, after independent review): `navigation-before-gps`, `pioneer-supply-chains-failed`.

**Before the release: nothing from this directive was live.** Live homepage (page 6) read 2026-11-02 through the WordPress.com connector: `modified 2026-10-30T09:14:14`, `content_hash 7afdb933d2ec68fd993ef015c97a6eb9edfe0576`, 6 top-level blocks, block hashes identical to the lock tokens in PR #604's rollback plan. The proposed change would still apply cleanly. It has **not** been applied.

## Decision: canonical homepage = PR #604 (flagship), not PR #49

| | PR #49 Assembly homepage | PR #604 flagship |
|---|---|---|
| State (2026-11-02) | open, base `production`, head `1049588329`, `verify` **failure**, `deploy` skipped | open draft, base `production`, head `368399842d`, `verify` success, `chromium` skipped |
| Mechanism | Site Layer plugin plus page content, deployed through the governed bridge | One `page-sections.replace` on page 6 block 1; CSS and JS inline; no plugin, theme or navigation change |
| Preserves | its own sections | blocks 0, 3 (native Jetpack Dispatch), 4, 5 byte-for-byte; 72-item Margins strip; Focus links |
| Rollback | bridge redeploy | restore two hash-verified original blocks, or the 2026-10-30 revision |

#604 already consolidates #550 (see its `CONSOLIDATION_MATRIX.md`). Choosing #604 avoids shipping two sets of scripts, and avoids the unrelated `main`/`production` histories. #49 and #550 are left untouched (not closed or merged) pending an owner decision.

## Why the homepage is not published (exact, from `ACCEPTANCE_MATRIX.md` section D)

Founder design approval is granted and is not the blocker. Three P0 items remain and cannot be self-certified:

1. **QD acceptance of the exact final SHA by a named human.** No `FVSL-QD-PASS` exists and I will not issue one. A fresh-context automated review of an earlier head exists (`INDEPENDENT_REVIEW.md`); the package itself states it is not QD.
2. **Authenticated WordPress.com render of the exact 108,152-byte block** (B5-B7): needs a signed-in browser. B1-B4 (inline style/script/noscript survive; hazard characters stored byte-for-byte; page 6 untouched) already pass on draft 1902.
3. **NASA item-specific reproduction sign-off** by a named editor (`IMAGE_RIGHTS_REGISTER.md`).

P1 still open: mobile LCP is above 2.5 s in the stricter lab modes (about equal to today's page, with about half the bytes); no screen-reader, Safari/iOS or real-device testing.

**What would unblock it fastest:** (a) you personally review the exact SHA and record QD in the PR, or name a reviewer; (b) sign in to WordPress.com in the in-app browser so the exact block can be rendered on draft 1902; (c) a named editor signs the three-image register. Then the apply step, verification and rollback in `RELEASE_AND_ROLLBACK.md` take minutes.

## Development status

| Workstream | Branch / PR | Exact commit | Tests | Status | Next |
|---|---|---|---|---|---|
| Experience 2.0 Sprint 5 (design system, Apollo 1 companion, Research Desk, Atlas model, plugin) | `feature/experience-2-living-archive-sprint5`, draft PR #485 | `9508c9dc` | `run_all.py`: 83 tests, 33 live URLs, 50 hero regions; hosted CI green on push and `pull_request` | integration candidate, not installed | independent QD; WordPress staging; dynamic block |
| Flagship homepage | `release/homepage-flagship-candidate-20261102`, draft PR #604 | **`bdf01b4a3e`** (was `368399842d`) | hosted `verify` green; local WordPress + Edge QA reproduced by a second session (`INDEPENDENT_REPRODUCTION.md`); independent ChatGPT review of the previous head: **HOLD, `FVSL-QD-PASS: NO`** | HOLD: fresh exact-head review, authenticated WordPress.com render, NASA named sign-off | request re-review of `bdf01b4a3e`; see `PR604_RELEASE_RECORDS.md` |

**Update (later 2026-11-02):** the reproduction found a real WCAG 2.2 AA defect the original keyboard check could not see (the flagship skip link rendered behind the site header when focused). Fixed with one CSS value; the package changed to 108,155 bytes, SHA-256 `506aa8d9...`, SHA-1 `8c0dd5c3...`. All approvals bound to `368399842d` / `d73124ab...` are void for the new head. Not published; page 6 unchanged.
| Preparedness release candidate | `integration/preparedness-release-candidate-20261101`, draft PR #584 | `ddb3528ba6` | machine integrity **failing** | HOLD | see root cause below |
| Preparedness R76 source impact | PR #668 | `06593b2ee8` | integrity failing; `source-impact-private-only` success | HOLD | same root cause class |
| Shelter follow-up evidence | PR #554 | `6a5998ead9` | no checks | draft, QD pending | merge order with #584 |

### Fixed this session (my own PR)

The PR #485 `pull_request` run failed on a race the push run did not hit: after closing the source drawer, focus returned to the wrong opener because browsers restore focus during their own close steps, in an engine-dependent order relative to the `close` event. Fixed in `9508c9dc`; five consecutive local runs and full suite pass; both CI events pass.

### Preparedness #584: root cause of the failing integrity gate

Reproduced locally by running `python -I preparedness/tools/validate.py` at `ddb3528b`:

```
ValueError: duplicate source id 'fsis-power-failure' is not documented in source crosswalk
```

`fsis-power-failure` (same URL, USDA FSIS "How do you keep food safe during a power failure?") is defined **three** times: the base register (placeholder), `fragments/food.json` (verified 2026-10-29), and `fragments/shelter.json` (verified 2026-11-01). The loader requires every redefinition of a verified source to be declared exactly in `sources/crosswalk.json`; that group declares only `base` and `food`. The `shelter` reading is substantively the same text (4 hours refrigerator, about 48 hours full freezer, 24 hours half full) with a different `title` and a later `verified_on`.

The design intent ("preserve every original record; never merge their claims") means the correct repair is to **declare the third variant in the crosswalk group** with its source file and row index, plus an honest note that it is a third independent reading with matching content. It is not to delete the shelter record and not to relax the check.

**Why I did not apply it:** the fix edits `crosswalk.json`, a 109 KB evidence file that other gates hash and that carries reviewer fields; the branch belongs to another workstream; and it is a PRIVATE HOLD branch. Editing it from here risks invalidating frozen evidence. It should be made by that workstream (or with their go-ahead), then re-run `validate.py` to see whether further duplicates surface. Even with this fixed, `may_publish` stays false: the R-series gates and the qualified safety review are separate, and no safety approval exists.

### Publication waves

No preparedness page was published. The archive is not cleared for any wave: the machine gate fails, consequential citations are under review (R76), and there is no qualified safety review. Wave 1 (landing, Start Here, household plan) is the right first release once the crosswalk fix and its dependent gates pass; it must not wait for Wave 2 or 3 material.

## Growth status

Baseline read from the live site on 2026-11-02 (read-only):

| Item | Finding |
|---|---|
| Redirects | `http://` and `www.` both 301 to `https://finalvestige.com/` |
| Homepage head | one `h1` ("Find what others miss."), one `main`, canonical `https://finalvestige.com/`, `robots: max-image-preview:large`, OG title/description/image/type/url present |
| Structured data | Organization, ImageObject, WebSite (with SearchAction), Person on the homepage |
| Images | 0 of 7 missing `alt` |
| Analytics | `gtag`/Google Tag Manager and `stats.wp.com` present |
| Search Console | no `google-site-verification` meta on the homepage; verification may be by DNS or file, so this does **not** show it is unverified. Needs confirmation in Search Console. |
| robots.txt | allows all but `/wp-admin/`; lists `sitemap.xml` and `news-sitemap.xml` |
| Sitemaps | `sitemap.xml` (200) indexes `sitemap-1.xml` and `image-sitemap-1.xml`; `news-sitemap.xml` (200) lists the homepage only; `wp-sitemap.xml` is 404 (expected) |

Not done: competitor research, keyword packages A-F, Evidence Atlas integration into a live investigation, Dispatch and conversion journey test, Search Console and analytics review. No SEO, ranking or traffic number was measured or invented. The Semrush figures in the directive are the founder's and were not re-verified.

## Blockers

| Blocker | Evidence | Attempted | Continuing independently |
|---|---|---|---|
| Homepage QD, signed-in render, NASA sign-off | `ACCEPTANCE_MATRIX.md` section D; live page unchanged | verified live hashes; confirmed procedure still applies | atlas/experience work, preparedness diagnosis |
| Preparedness integrity gate | `ValueError` above, reproduced at `ddb3528b` | root-caused to one undeclared crosswalk variant | proposing the change to the owning workstream |
| Qualified safety review of preparedness | no approval exists in the repo | none: cannot be self-issued | Wave 1 scoping |
