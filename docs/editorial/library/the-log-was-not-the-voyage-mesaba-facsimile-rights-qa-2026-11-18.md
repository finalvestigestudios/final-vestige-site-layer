# The Message Was Not the Delivery — original 1912 report facsimile audit

Owner: Final Vestige Studios Library / draft #2893, child of Library #77. Checked **November 18, 2026**. Status: **DRAFT / QA HOLD / DO NOT PUBLISH**.

## What changed this run
A new 14,088-character source-confrontation supplement was saved to the existing page #2893, with one original, labeled SVG illustrating **document lineage** (not a supposed radio-log facsimile), a three-witness comparison, two timestamp conventions, a 10-field printable provenance receipt, responsible link-only treatment of the historic scan, and a source-and-rights note.

- [Original addendum source](the-log-was-not-the-voyage-mesaba-original-report-facsimile-audit-2026-11-18.html)
- [Reconciled original guide](the-log-was-not-the-voyage-message-not-delivery-2026-11-17.html)
- [WordPress draft](https://finalvestige.com/wp-admin/post.php?post=2893&action=edit)
- [Original nine-page release manifest](the-log-was-not-the-voyage-nine-page-release-manifest-2026-11-18.md)

The original November 17 guide had said the 1912 report's images could not be inspected via the Library of Congress research URL. That remains an accurate statement about **that particular site and earlier attempt** but became misleading after finding an independent institutional copy. Its opening limitation and LOC source note were narrowly corrected to point readers to the inspected Memorial University facsimile. The separate source addendum now distinguishes the contemporary *published conclusion* from the missing original shipboard wireless message, and the typed modern hearing transcripts from the physically inspected print edition.

## Primary-source and access ledger

| Record | Issuer / custodian | Relevant location | Access checked | Qualification |
|---|---|---|---|---|
| *Shipping Casualties (Loss of the Steamship Titanic)*, British command paper Cd. 6352, 1912 | British Wreck Commissioner, His Majesty's Stationery Office; digital host Memorial University Digital Archives Initiative | [Full institutional scan](https://dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf), printed pp. **27–28**, PDF pp. **31–32** | November 18, 2026; page images **visually inspected** | A contemporaneous printed government inquiry report, **not** the original handwritten wireless slip; OCR text of the scan has apparent errors, so image view controls exact wording |
| Stanley H. Adams inquiry evidence | British Wreck Commissioner's Inquiry (1912); modern transcription Titanic Inquiry Project | [Day 21, questions 22022–22058](https://www.titanicinquiry.org/BOTInq/BOTInq21Adams01.php) | November 18, 2026; web transcription readable | Sending and operator acknowledgment described; original physical stenographic sheets not inspected; simplified operator transcript identified as paraphrase |
| Joseph G. Boxhall inquiry evidence | British Wreck Commissioner's Inquiry (1912); modern transcription Titanic Inquiry Project | [Day 14, questions 16920–16927](https://www.titanicinquiry.org/BOTInq/BOTInq14Boxhall01.php) | November 18, 2026; web transcription readable | Firsthand testimony of no known message during bridge watch, not omniscient proof of all knowledge aboard |
| British commissioner's published conclusions | British government (1912); digital transcription Titanic Inquiry Project | [Messages received](https://www.titanicinquiry.org/BOTInq/BOTReport/botRepMessages.php) | November 18, 2026; compared to institutional scan | A secondary typeset digital text for navigation; controlling copy for this run is Memorial's scanned original printing |
| Institutional rights/access help | Memorial University DAI | [Rights/OCR help](https://dai.mun.ca/help), [about DAI](https://dai.mun.ca/about) | November 18, 2026 | DAI describes items as CC BY-NC-ND; the report images are **linked**, not copied, cropped, modified or embedded. For redisplay / reuse beyond linking, assess item-specific rights with the holding institution |
| LOC description of U.S. Senate edition | Library of Congress | [LOC record](https://www.loc.gov/item/2025847774/) | November 18, 2026; direct research retrieval **HTTP 403** | This is a second edition/location; its scan images remain uninspected and should not be represented as checked |

### Historical claims after audit
- British inquiry report: received in the Marconi room at **9:40 p.m.** on April 14, 1912; captain did not acknowledge receipt; commissioner concluded captain did not receive the message. This is a published inference drawn from the inquiry's evidence, not direct proof of the slip's placement.
- Adams later testimony: his transmission entry gives **7:50 p.m. New York time**. Keep the historical clock descriptions separate; do not silently convert or claim precise equivalence.
- No contemporary individual wireless slip or signed bridge receipt has been inspected. Do not make the popular dramatic claim that an operator **put it under a paperweight** as if it were verified here.

## Rights and visual ledger
- **Original source document**: *Shipping Casualties*, 1912, British government / HMSO; digital scan hosted by Memorial University Digital Archives Initiative, original URL above. **No imagery from the institutional scan was downloaded into the publication, reproduced, modified, or used as a decorative backdrop**.
- **Original diagram**: Final Vestige Studios, 2026; author/rights holder Final Vestige Studios; explanatory SVG composed for this addendum, title and description plus caption and explicit non-facsimile note. It depicts three documentary layers and labels unexamined original radio paperwork. No AI-generated documentary imagery.
- **Other media**: none embedded. All third-party source material link-only.
- **Rights detail**: Memorial DAI help states CC Attribution–NonCommercial–NoDerivs for hosted items; historical public-domain status and repository reproduction conditions should not be conflated.

## API and structural QA
- GitHub source creation committed as `aee01c11be9246bb70897fbfadc2162b38b2fe5a`; correction to original source committed as `d98767e8ac277cd8dfaf95fd69ff84650825bc90`.
- WordPress inserted a single `core/html` block by index with optimistic `content_hash` / modified tokens; source reconciliation replaced only its original `core/html` block, also with block-hash optimistic guard.
- Authenticated page #2893 independent readback: **draft**, parent 77, `jetpack_seo_noindex=true`, three top-level blocks, 33,177 serialized characters, exact new GitHub block present, original guide's revised source block present. Save warnings: none.
- Structural audit of full page: **10 element IDs / 10 unique**, no unresolved internal fragments, no empty href, no JavaScript href, new SVG title and description present, responsive CSS breakpoint at 640px, print CSS present, no external images copied.
- Source links: Memorial report and rights pages accessible; Titanic Inquiry Project Adams/Boxhall/report transcripts accessible; FV Research Sources and Editorial Standards available. The Archive Trail returned transient HTTP 429 from unauthenticated web research, while authenticated WordPress rendered-page check showed **HTTP 200**.
- Public rendered WordPress readback: `/free-resources/` **200** with established metadata; unpublished `/free-resources/ship-logbook-message-chain/` **404**, correctly inaccessible to anonymous readers.
- Outstanding: live authenticated production-theme screenshots at 320 / 390 / 768 / 1440; keyboard + screen-reader assessment, real print receipt tests, complete full outbound link sweep, and first-publication `_jetpack_dont_email_post_to_subs=true` / `jetpack_publicize_feature_enabled=false` enforcement. Connector still lacks guaranteed write/read control for those fields.

## Release decision
**HOLD.** All public Library paths and existing navigation remain unchanged. No paid asset, subscriber email, social promotion, merge or live publication. Shared issue #1589 and Research Sources #1788 remain separate workstreams. Optional Grok angle after verified publication: “A wireless operator said it was acknowledged. The surviving report says the captain never saw it. Here are both documents.”
