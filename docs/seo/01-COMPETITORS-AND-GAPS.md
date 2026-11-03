# 01 - Competitors and gap evidence (2026-11-02)

## Known gap in the evidence: the Ahrefs data was not available

The directive called for Ahrefs `site-explorer` (organic competitors, top pages, keywords) and Search Console data. Every call to the connected Ahrefs MCP on 2026-11-02 returned HTTP 400 `{"error":"Insufficient plan"}` (code -32001):

| Tool | Target | Result |
|---|---|---|
| `site-explorer-organic-competitors` | finalvestige.com, us, subdomains | Insufficient plan |
| `site-explorer-metrics` | finalvestige.com, us | Insufficient plan |
| `gsc-pages` | 2026-08-01..2026-10-31 | Insufficient plan |
| `keywords-explorer-overview` | "apollo 1 fire" | Insufficient plan |
| `management-projects`, `subscription-info-limits-and-usage` | - | Insufficient plan |

Consequences, stated plainly:

- **No keyword volume, traffic, ranking, difficulty or Search Console figure appears anywhere in `docs/seo/`.** None was measured; none was estimated.
- The five competitors below are **SERP-observed, unverified by a tool** (see method). They are a working set, not a ranked list.
- The keyword work can be redone from an Ahrefs/Semrush export or Search Console access supplied by the founder (see `05-GSC-MEASUREMENT-PLAN.md`).

## Method (what "SERP-observed" means here)

Ten web searches were run on 2026-11-02 through the session's web-search tool, one per content cluster the site actually publishes (engineering failures, named disasters, primary-source research, disputed records). A domain counts as a competitor if an **editorial publisher** (not an agency, library or encyclopedia) appeared in the returned results for at least one cluster query. The tool returns 10-20 links per query and says nothing about rank, so this is presence only.

Queries: `engineering disaster case studies what went wrong history` | `Apollo 1 fire hatch opened inward investigation` | `free primary source archives history research guide` | `lost expedition Franklin expedition what the records show` | `historical disasters lessons learned safety failures blog` | `Teton Dam failure 1976 what went wrong` | `Iroquois Theatre fire 1903 locked doors fire codes changed` | `Malbone Street wreck 1918 Brooklyn derailment cause` | `Frank Slide 1903 Turtle Mountain miners rescued` | `long-form history website forgotten disasters engineering failures stories`.

**finalvestige.com did not appear in the returned results of any of the ten queries.** That is an observation about those result lists, not a measurement of rank or visibility.

## The five competitors (SERP-observed, unverified by a tool)

| # | Domain | Seen for query | What was seen | Why it competes |
|---|---|---|---|---|
| 1 | practical.engineering | Teton Dam | Blog post "The wild story of the Teton Dam failure" | Same format (named engineering failure, explained from the record), same subject as our Teton Dam post |
| 2 | smithsonianmag.com | Malbone Street | "The Malbone Street Wreck of 1918" | Editorial history; same subject as our Malbone Street post |
| 3 | untappedcities.com | Malbone Street | Two Malbone Street articles | Local-history editorial on the same events |
| 4 | thecanadianencyclopedia.ca | Frank Slide | "Frank Slide" (several URL variants) | Reference-style coverage of the same event as our Frank Slide post |
| 5 | designnews.com | Engineering disaster case studies; long-form disasters | "When Engineering Fails: 15 Catastrophic Disasters That Changed History" | A roundup hub that ranks for the cluster term; we have no roundup/hub equivalent |

Seen but not counted as competitors (different kind of source): nasa.gov, usbr.gov, gao.gov, damsafety.org, wikipedia.org (primary or reference sources; they are *citations* for our posts, not rivals), university library guides (they dominated the primary-source guide query; relevant to `/free-resources/` and `/archive-shelf/` intent), book listings, forum threads.

## Gap observations (qualitative, from the result lists only)

1. **Entity-first titles.** Competing results lead with the event name (e.g. "Teton Dam Collapses", "The Malbone Street Wreck of 1918"). 22 of our posts have SEO titles of 80-125 characters that put the narrative hook first and the entity late (examples: "The City Kept Moving: Camp Century, Project Iceworm and the Base Beneath Greenland"). Change set A fixes these without touching the headline.
2. **No cluster hub for engineering failures.** A roundup page is what ranked for the cluster term. Our nearest asset, The Failure Chain, had 3 internal links in its content and linked to only one case study. Change set B turns it into the hub (9 worked examples) and links each case study back to it.
3. **Method pages were nearly unlinked from the stories that use them.** Each "the-..." guide had one inbound link from `/free-resources/` in page content (footer/header navigation not counted; see `02-BASELINE.md`).
4. **Inconsistent title format.** 18 pages rendered as "Name – FINAL VESTIGE" (all-caps site name, no custom title) while 104 used "Name | Final Vestige".
5. **Descriptions out of range.** 18 descriptions exceeded 200 characters (will truncate) and 3 policy pages had 29-77 character descriptions.

These are structural fixes that do not depend on keyword volume. What they will do to rankings is unknown until Search Console data exists; see the measurement plan.
