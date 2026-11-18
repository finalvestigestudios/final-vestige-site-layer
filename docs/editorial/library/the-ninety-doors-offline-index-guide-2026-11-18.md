# The Ninety Doors: A Portable Research Sources Index

*Final Vestige Studios Library · Research utility / archival-source directory*  
**Inventory inspected:** 18 November 2026 · **Source:** published [Research Sources](https://finalvestige.com/free-resources/research-sources/) (WordPress page #1338, modified 2026-11-03T22:12:43 site-local) · **Release state:** editorial draft, not linked or deployed.

An official archive page is an entrance, not an answer. This is a portable, human-readable and machine-readable **inventory of all ninety cards already present** in Final Vestige's public Research Sources directory. It is for readers building a search plan, preserving a source trail, or doing methodical link maintenance. It does not copy the documents inside the repositories.

## What you can do with it

1. **Start with the research question.** Filter the CSV's `category` column before opening any link. The five families are evidence routes, not grades of reliability.
2. **Name the thing you actually opened.** A gateway, finding aid, catalogue description, edited volume, translated message, scan and underlying record are different citation targets. Preserve its identifier, creator, date and custodian.
3. **Write down the record's parentage.** Two pages at different institutions may point to the same underlying document; keep the originating document or witness separate from the host or edition. A repeated citation is not independent testimony.
4. **Add the missing fields to your own research copy.** Source item ID or call number, record/creation date, URL actually examined, access date, exact page or folio, redactions/edits, rights statement and your remaining uncertainty. Do not overwrite the source directory's metadata.
5. **Verify before reusing.** Clicking a link is not permission to reproduce the linked document or an institutional image. Read item-level notices and request permission when necessary.

## Working example (illustration grounded in official editions)

The [1989 *Foreign Relations* volume, Document 335](https://history.state.gov/historicaldocuments/frus1952-54v10/d335) prints a July 24, 1953 telephone memorandum. The [2018 Iran retrospective, Document 251](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d251) cites this same older publication. Record both institutional appearances, but group them under **one underlying memo** in a witness-family ledger. The published text records a report of presidential clearance; the document itself is not the original presidential authorization. Do not infer that a physical original was examined by this CSV's compiler.

## Field names and limitations

- `id`: stable row label *within this 18 November snapshot* (not a governmental accession number).
- `category`: a Final Vestige editorial browsing family, not an agency classification.
- `title`, `institution_type`, `editorial_abstract`: the Library's existing editorial copy, transcribed from the live WordPress record. Historical counts and descriptions are **not newly verified claims**.
- `source_url`: the destination embedded in the Library card, **not** evidence it currently resolves in an ordinary visitor browser.
- `access`, `reuse_rights`: conservative editorial defaults; neither an intellectual-property determination nor individual rights clearance.
- `source_record` and `catalog_snapshot_date`: evidence of the directory extraction, **not** an inspection date for each external record.
- `source_link_health` / `rights_check_status`: explicit pending states so later researchers cannot mistake a URL extraction for a source audit.

### Snapshot reconciliation

| Family | Cards |
| --- | ---: |
| Declassified & decisions | 12 |
| Accountability & public data | 24 |
| Engineering & disaster investigations | 21 |
| Archives & research systems | 25 |
| Navigation & mapping | 8 |
| **Total** | **90** |

**Extraction QA:** ninety parsed `fv-rs-card` elements, ninety nonempty names, ninety unique title strings and ninety unique HTTPS destinations; no rows missing a description or institution/type. The source page has 60 cards in its initial block and 30 supplemental cards appended by JavaScript. The page's old static text still says 60; its supplemental script also incorrectly labels accountability 23 and archives 26. This dataset describes the **actual stored cards**, not those stale labels. [Tracked release issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788).

## Provenance / last-checked ledger

| Evidence or policy | Role | Read or checked |
| --- | --- | --- |
| [Published Research Sources](https://finalvestige.com/free-resources/research-sources/) · WP #1338 | Primary inventory extracted with authenticated edit-context read; last modified 2026-11-03T22:12:43 | 2026-11-18 |
| [The Library](https://finalvestige.com/free-resources/) | Existing editorial placement and navigation | 2026-11-18 |
| [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/) | Rules for uncertainty, source differentiation and media attribution | 2026-11-18 |
| [US National Archives: citing catalog records](https://www.archives.gov/citizen-archivist/faqs) | Institutional citation elements, repository/custodian, source version and access date | 2026-11-18 |
| [Library of Congress archival description](https://www.loc.gov/librarians/archival-description/) | Finding-aid hierarchy, provenance and access conditions | 2026-11-18 |
| [Society of American Archivists' provenance statement](https://www2.archivists.org/news/2002/statement-of-principles-for-the-custard-project) | Provenance and original-order principles | 2026-11-18 |
| [Library of Congress manuscript permissions FAQ](https://www.loc.gov/research-centers/manuscript/frequently-asked-questions/) | Custody does not establish the Library owns publication rights | 2026-11-18 |

**Rights and media:** all directory titles, abstracts and classification labels were created for the existing Final Vestige site. This new export reproduces only that existing site-authored metadata and official source **links**, not external photographs, scans, maps or institution-owned images. A separate original FV figure accompanies the snapshot. The archive links are not a blanket grant to redistribute source materials. Data reuse outside the studio should preserve attribution and observe applicable rights.

**Release hold:** This is a repository draft, not a WordPress page or a production-ready widget. Real browser verification at 320 / 390 / 768 / 1440 px, keyboard and screen reader behavior of the public directory, all destination URL checks, rights review if images are ever added, and suppressing first-publication email/social notifications are not demonstrated. No live pages, subscribers, or social accounts were changed. This index must not be linked publicly as fully verified until those tests pass.

**Related:** [The Archive Trail](https://finalvestige.com/the-archive-trail/) · [The Black Bar](https://finalvestige.com/free-resources/the-black-bar/) · [The Page That Changed](https://finalvestige.com/free-resources/the-page-that-changed/) · [Editorial Standards](https://finalvestige.com/editorial-standards/).
