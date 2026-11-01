# Lady Be Good — seven-source official custody and visual-integrity findings (2026-10-31)

**Post:** [278, They Walked Beyond the Search](https://finalvestige.com/2026/08/19/they-walked-beyond-the-search-lady-be-good/). WordPress read-only `posts.get(context=edit)` returned published article last modified **2026-08-21T00:32:59**. Exact source URL and complete ALT agreement: **7/7** against frozen `qa/media-recovery/parts/04.json`. All seven sources are externally hosted. No production writes or images downloaded.

## Authoritative crosswalk

| Slot | Independent institutional evidence / identification | Proposed derivative | Rights |
|---|---|---|---|
| 278:0 | DoD-hosted `070125-F-0000Z-099` photo identifier; no corroborated photo catalog page. | Cannot calculate until dimensions verified | HOLD |
| 278:1 | [U.S. Air Force museum 2000572755](https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000572755/) lists exact VIRIN `050606-F-1234P-012` for nine crewmen. | Unknown source pixels | HOLD |
| 278:2 | [Air Force museum 2000572753](https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000572753/) identifies `050606-F-1234P-014`, and [Commons file metadata](https://commons.wikimedia.org/wiki/File:0000050606-F-1234P-014.jpg) documents **1800×1192 original → 960×636** without cropping or upscaling. | **960×636 conditional** | HOLD |
| 278:3 | [U.S. Army Quartermaster Museum September 2012](https://qmmuseum.army.mil/explore/artifact-of-the-month/2012.html) identifies recovered 1942-made Model 1910 canteen; exact photo binary unverified. | Unknown source pixels | HOLD |
| 278:4 | [NARA Toner diary photos 342-B-ND-075-4-163133AC / 163134AC](https://unwritten-record.blogs.archives.gov/2017/06/16/lost-and-found-the-story-of-lady-be-good-and-her-crew/) are **different archival alternatives**, not demonstrated equivalent to private-host diary image. Do not substitute without visual verification. | Unknown | HOLD |
| 278:5 | [NARA attachment 111-C-17240](https://unwritten-record.blogs.archives.gov/2017/06/16/lost-and-found-the-story-of-lady-be-good-and-her-crew/111-c-17240/) confirms same hosted filename but not article's specific described scene. | Unknown | HOLD |
| 278:6 | [U.S. Air Force museum 2000554420](https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000554420/) exact VIRIN `060530-F-1234S-041` describes a **tail view of the wreck with C-47 recovery aircraft in background**; current ALT describes **personnel working around** the wreck, without official support. | Unknown | HOLD |

**P0 editorial visual-integrity correction, not applied:** for **278:6**, after checking the actual image crop, proposed ALT: “Tail of crashed B-24D Lady Be Good in the Libyan Desert, with a C-47 recovery aircraft in the background.” For **278:3**, the Quartermaster exhibit does not explicitly document a find point on the “crew’s desert trail”; neutral location wording would be more supportable. Proposed ALT changes are recommendations only and require separate approval.

**Actual retrieval observations:** an independent web retriever returned **403** for exact current DoD source **278:0** and **502** for exact Army museum JPG **278:3**. These are **retriever failures only**, not FinalVestige.com logged-out browser/image failures; do not add them to 42. No real site guest HTTP status, `currentSrc`, decoded `naturalWidth`, transferred bytes or screenshots were observed. The reported **42 broken** and **76% image-weight reduction** remain unverified, and existing 13 Media Library originals over 1.5 MiB are separate original-storage metrics.

**Rights:** USAF official museum pages label three matching VIRIN photos public domain and cleared for release, with image-credit, recognizable-person and nonendorsement caveats. The DoD-only photo, U.S. Army museum photograph, NARA attachment and private diary-page reproduction each require individual review. Every ledger rights field remains **HOLD**; no image is cleared for a WordPress cached copy. No unsupported exact-binary matches or SHA-256 are claimed.

**Future cache release gates (not executed):** documented actual browser broken-source evidence; same historical photo and crop; catalog ID and applicable photo permission/credit; inspect source visually, SHA-256 record, source dimensions, `min(960px, actual width)` without upscale/crop; separately stage WordPress Media Library item with responsive sizes; non-destructive preview; repeat same-content mobile/desktop CDP image byte and LCP/CLS comparisons. No bulk scraping, hotlink bypass, homepage design changes, Gutenberg rewrites or spend.

**Machine-readable source:** `qa/media-recovery/lady_be_good_278_primary_20261031.json`; strict source/rights/geometry validator and adversarial Node tests alongside. Site QA #154's classifier remains untouched.
