# Research Sources: 90-destination access review
**Final Vestige Studios · Library editorial record · 2026-11-10 (Pacific)**
**Owner:** Library only. **Publication:** HOLD. **Scope:** existing public WordPress #1338 and unpublished repair #2354; no investigations, preparedness, homepage, subscriber/social operations.

## The public problem

A source directory is useful only if its links identify *what is actually there*. A readable institutional landing page is not proof that a record is digitized; a 403 to an automated reader is not proof that a human cannot visit the collection. An image URL is not permission to reproduce the image. This register makes those distinctions traceable across all 90 cards.

The complete machine-readable inventory, source descriptions and rights qualifications are in [the **90-source provenance CSV**](./research-sources-90-provenance-ledger-2026-11-10.csv). On November 10, the remaining **56 entries** marked `not_rechecked_in_this_run` were individually attempted at their primary destinations using a networked textual reader, and their statuses replaced with explicit outcomes, dated notes and follow-ups.

## Evidence classification (90 total)

| Observation | Entries | What it establishes |
| :-- | --: | :-- |
| Destination content or official PDF retrieved in this review / earlier Nov 10 review | **63** | Institutional destination content was readable to the reviewer; not a record-by-record, downstream-link, or rights audit. |
| Institutional content available through an earlier cached institutional crawl | **1** | Indexed/cached content exists, but direct access needs another check. |
| Reader could not fully inspect the destination, or retrieved only an app shell | **26** | Includes anti-bot restrictions, JavaScript apps, redirects, an oversized PDF, and ambiguous error states. **Not classified as dead links.** |
| **Total** | **90** | Every source has an explicitly dated access observation; **26 do not have a directly readable, first-hand destination result.** |

### Priority follow-up queue

- **JavaScript / application-only:** USAspending (#18), National Archives Catalog (#68), NOAA Historical Hurricane Tracks (#73), and NTSB CAROL redirect (#54). Validate search actually works as a visitor and record the destination after redirects.
- **Automated 403/406 / denied-reader cases:** NRC ADAMS (#24), Oversight.gov (#26), Regulations.gov (#28), RECAP (#36), USGS PP1250 (#42), Corps IPET (#51), LOC HABS (#59), Chronicling America (#61), LOC railroad maps (#74), DPLA (#75), Coast Guard Navigation Rules PDF (#86), plus previously logged restrictions in the CSV. These are **not** asserted to be broken browser links.
- **Ambiguous / content-size:** OSTI.GOV (#64; reader 502 while [DOE](https://www.energy.gov/science/scientific-and-technical-information) confirms the service), Smithsonian Open Access (#66; direct reader 404 while [Smithsonian's indexed current page](https://www.si.edu/openaccess) and [FAQ](https://www.si.edu/openaccess/faq) remain available), Veterans History Project (#78; disabled reader), BLM 2009 Surveying Manual (#88; PDF exceeded reader size limit). Recheck with an ordinary browser; do not delete these without evidence.
- **Rights-relevant landmark:** USFA *America Burning* (#49) official PDF has a printed **page II** permission statement that allows the report to be reproduced but **excludes photographs without permission of their owners**. It also contains a **September 1989 USFA statistical update** correcting some figures in the original 1973 report. The first-page date is not a license and later figures do not describe the original 1973 moment. [Official USFA PDF](https://www.usfa.fema.gov/downloads/pdf/publications/fa-264.pdf). This distinction was added to staging #2354 and read back.

### Reusable reader method

```text
LINK FOUND
    |
    +-- Page readable --> identify collection scope --> open exact record
    |                                            --> capture edition/date
    |                                            --> inspect object rights
    |
    +-- App shell / redirect --> test real search in a browser
    |                       --> save query + filters + record ID
    |
    +-- 403/406/502/404 --> distinguish bot failure, server incident,
    |                      removed item, or a genuine missing record
    |                   --> test institutional alternative / human access
    |
    +-- PDF too large --> use institutional detail page + metadata,
                         selective page review, and rights notice.
```

All symbols above are an **original explanatory diagram**, not documentary imagery. No archival scans or third-party photographs are reproduced. Rights belong to the original institutions and, where applicable, to third parties; linked sources are not licensed by Final Vestige.

## WordPress state and release gate

- Public original **#1338**: still PUBLISHED, last modified 2026-11-03T22:12:43 site-local, still shows stale static “60” text.
- Staging repair **#2354**: DRAFT/noindex, last modified **2026-11-10T11:40:20** site-local; exactly **90** cards, **90 unique titles and source URLs**, categories **12 / 24 / 21 / 25 / 8**. The 1973/1989 *America Burning* qualification is saved and confirmed by authenticated readback.
- The supplemental-card rendering repair and previous **45** source editorial refinements remain intact; this session adds **one** substantive textual correction to the staged source card, yielding **46 cumulative** editorial refinements by this tracking convention.
- [Library](https://finalvestige.com/free-resources/), [public directory](https://finalvestige.com/free-resources/research-sources/), and [Editorial Standards](https://finalvestige.com/editorial-standards/) inspected on November 10, 2026.

**Do not publish staging as a duplicate.** Release to existing #1338 only after the independent production-theme browser QA of 320/390/768/1440 widths, **with and without JavaScript**, keyboard/overflow/search/filter checks, and anonymous link/media checks, including the blocked destinations above. Require verified suppression of first-publish subscriber email and Jetpack Publicize; the WordPress connector does not currently expose the requested `_jetpack_dont_email_post_to_subs` and social flags in a first-publish request. No public write is authorized by this research record.

[Coordination #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) · [Site QA blocker #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Promotion belongs to Grok's lane **after** live release; no publishing or social action took place during this audit.

**Verification boundary:** These are editorial/reachability observations on 2026-11-10, *not* HTTP uptime guarantees, a complete audit of every downstream document, legal advice, or a blanket public-domain declaration.
