# Package F: long-term water storage — DRAFT, NOT PUBLISHED

Prepared 2026-11-02. Status: **draft; do not publish.** Blocker: Preparedness gating (`safety_review.state = "pending"`, no qualified reviewer, `may_publish` false; release candidate #584 on HOLD, see `docs/experience-2.0/IMPLEMENTATION_LEDGER.md`). Nothing from this package was written to WordPress.com.

## Decision: upgrade, do not duplicate
The Preparedness Archive already contains a governed article on this subject:

| Item | Where | State |
|---|---|---|
| `two-week-water-storage` (n=4, section `water`) "Two-week water storage: containers, cleaning and rotation" | `preparedness/content/articles/two-week-water-storage.{body.html,meta.json}` on `integration/preparedness-custody-repair-20261103` (read only; not edited) | `status: drafted / publish: draft`, `safety_review: pending`, `updated/last_checked 2026-10-29`, related: `water-math`, `making-water-safer` |
| Page 85 "The Water Resilience Field Manual" ($2.99 PDF product page) | WordPress.com, **draft** (modified 2026-10-29) | not touched |
| Page 29 "72 Hours Without the Tap" | WordPress.com, **draft** (modified 2026-10-29) | not touched |

Writing a second article for "long term water storage" would create a competing, unreviewed safety page. The right deliverable is an SEO/FAQ layer for the existing article, ready for the owning workstream to merge once review exists.

## What was verified today (2026-11-02)
- CDC "How to Create an Emergency Water Supply": opened live. Page dates: published 16 Sep 2024, updated and reviewed 27 Jun 2025 (page republished 24 Apr 2026). Every figure the article relies on matches: 1 gallon per person per day for 3 days, "try to store a 2-week supply if possible", replace self-filled water every 6 months, observe expiration date on store-bought water, 50°F–70°F, out of direct sunlight, away from gasoline and pesticides, 1 teaspoon unscented bleach (5%–9% sodium hypochlorite) per quart, wait at least 30 seconds, label "drinking water" with the date, container criteria.
- Ready.gov "Water": opened live. "Last Updated: 02/22/2021". Sealed original container, cool and dark, food-grade containers, non-commercially bottled water replaced every six months, at least one gallon per person per day "for several days".
No contradiction with the article text was found. Known cross-source difference (CDC accepts 5–9% bleach; Ready.gov states 5.25–6.0%) is already disclosed in the article and in `sources/register.json`.

## Keyword finding: "long term" is a promise the sources do not make
Searchers for "long-term water storage" usually want to know how many months or years water lasts. The official guidance read today gives **six months for water you fill yourself** and "observe the expiration date" for bottled water. Neither source gives a longer shelf life, and neither covers 55-gallon drums, water preservers, or treating water so that it keeps longer. The existing article says exactly that in its "limits" section. So the upgrade must lead with the honest answer ("official guidance is a rotation cycle, not a shelf life") rather than chase the keyword with claims we cannot source.

**Do not add, unless new sources are opened and reviewed:** years-long shelf-life claims; drum or barrel sizes; preservative or "water preserver" products; storing water collected from rain or the tap without treatment; any numerical dosing beyond the container-sanitizing figure already in the article.

## Proposed upgrade (files in this folder)
- `proposed-meta.json`: title tag, meta description, H1 option, dek, and six FAQ entries with the source ids each answer rests on. All wording is restricted to statements already in the article or re-verified above.
- `faq-schema.draft.json`: matching FAQPage JSON-LD. **Do not inject until safety review passes.** Note: Google restricts FAQ rich results to well-known government and health sites, so no rich result should be expected; the visible FAQ is the useful part.
- Internal link plan (slugs from the archive, all currently unpublished): `water-math` (how much), `making-water-safer` (when stored water runs out), `rain-barrels-and-cisterns`, `three-day-kit`, `household-emergency-plan`. Links to WordPress.com posts already live: none needed; the live site has "The Cisterns Beneath San Francisco" (post 38) and "The Morning San Francisco Lost Its Water" (post 34) as narrative context, **not recommended as links from a safety page** until the archive's tone and review rules are applied.

## Hand-over to the Preparedness workstream
1. Merge `proposed-meta.json` fields into `two-week-water-storage.meta.json` (the file has `title`, `h1`, `dek`, `description`; the FAQ block needs a template decision because the archive renderer's FAQ support was not checked).
2. Run the archive's own validator and gates after the merge (`python -I preparedness/tools/validate.py`), then the R-series custody checks.
3. Safety review by a qualified, named reviewer. Not self-issued.
4. Only then does `may_publish` flip, and then only as part of the planned publication wave, not as a standalone post.

## Rollback
Nothing published, so nothing to roll back. Deleting this folder or the branch removes the package.
