# Corrections log, content packages A–E

Applied 2026-11-02 (site time 22:02–22:04) on the founder's standing approval relayed by the implementation session, after `QA-claim-source-table.md`. Method: each change was a single-block replacement (`post-sections.replace`) locked to the post's current `modified` time, `content_hash` and the target block's `block_hash`, read immediately before the write. Top-level block counts did not change. Every write returned no content warnings.

Principle used: correct from evidence, keep the uncertainty. Where a claim had no source the text now says what the opened sources *do* establish, labels inference as inference, and states honest absences ("the edition does not say…", "we found nothing in our sources saying…").

## New evidence obtained for these corrections
| Evidence | Where | Verbatim (≤15 words) |
|---|---|---|
| Columbus's map not found as of 1935 | Akçura 1935 (Wikisource), conclusion | "His claim to have used Columbus' map, which until now has not been found" |
| Remaining parts of the map lost | Akçura 1935 | "torn away and lost" |
| Torn along the eastern edge, "in half" | Dutch (Wayback 2013) | "originally a world map which was torn in half along the eastern edge" |
| The Bahriye describes the 1517 presentation (so postdates it) | Akçura 1935, Bahriye quotation | "presented this map to the late Sultan Selim Han in Cairo" |
| Work on navigation named "Bahriye" | Akçura 1935 | "sketches from Piri Reis' work on navigation, \"Bahriye\"" |
| No statement about the map's whereabouts 1517–1929 | Akçura 1935 introduction (full text searched) | absence check: no sentence on whereabouts |
| Jolly's journal and issue | Skeptical Inquirer's own issue PDF, cover | "Vol. XI No. 1/Fall 1986" |
| Cantino chart description | Wikimedia Commons file description | "depicts the world, as it became known to the Europeans after the great exploration voyages" |
| Dutch's affiliation | Dutch page header | "Steven Dutch, Natural and Applied Sciences, University of Wisconsin - Green Bay" |
| McIntosh publisher/date | UGA Press page (fetched), og:site_name "Georgia Press" | "Published: 2000-07-07" |
The McIntosh book itself was **not** downloaded or read (lending-restricted copy); claims about it still rest on the publisher description.

## Post 1917 (piri-reis-map)
Tokens before first write: modified `2026-11-02T20:48:54`, content_hash `087bd41bbb4e66433ac377d82eeebbfe81fa5d7c`. After last write: modified `2026-11-02T22:03:48`, content_hash `2049decfed3eec105714f3efa9214ba018ef7a8b`. Top-level blocks: 27 before, 27 after.

| # | QA rows | Block | Before | After | Class |
|---|---|---|---|---|---|
| 1 | A13, A50, A51 | 5 | The same edition quotes Piri Reis’s later sea-book, the *Kitab-ı Bahriye*, saying he presented the map to Sultan Selim I in Cairo, where Selim had just conquered Egypt in 1517. After that, the map disappears from the record. Nobody knows what Selim made of it. | The same edition quotes Piri Reis’s sea-book on navigation, the *Bahriye*, saying he presented the map to Sultan Selim I in Cairo, where Selim had just conquered Egypt in 1517. Because that passage describes the presentation, the book itself was written after 1517. The edition does not say where the map was between 1517 and its rediscovery in 1929. | documented fact + labelled inference + documented absence |
| 2 | A53 | 9 | …The Columbus map itself has not survived, so the claim can only be tested against the fragment. | …The 1935 edition notes that Columbus’s map, which Piri Reis claims to have used, “has not been found,” so the claim can only be tested against the fragment; we found nothing in our sources saying it has turned up since. | documented fact + stated limit of research |
| 3 | A48, A49 | 10 | alt: …with the line dividing the Spanish and Portuguese zones. caption: …Modern scholars use charts of this kind as comparison points for the Portuguese material Piri Reis says he used. | alt: The 1502 Cantino planisphere, a Portuguese world chart showing the world as Europeans knew it after the first voyages to the Americas, Africa and India, with a vertical line near the left edge. caption: …Piri Reis says he used four recently drawn Portuguese maps but does not name them; this chart is shown only as an example of the period’s Portuguese charts, not as one of his sources. | scholarly claim removed; illustrative use stated; image content checked by viewing and Commons description |
| 4 | A37 | 11 | …reviewing Hapgood’s method in *Skeptical Inquirer*, describes… | …in *Skeptical Inquirer* (Fall 1986), describes… | now verified |
| 5 | A42 and A43 | 13 | Geoscientist Steven Dutch… Jolly adds that sixteenth-century maps varied widely in how they drew a southern continent… | Steven Dutch of the University of Wisconsin–Green Bay… Jolly adds that the southern continent was drawn with varying shapes on maps both before and after the Finaeus map… | paraphrase tightened to the source |
| 6 | A53, A54 | 14 | …and the map itself is lost, so the question can only be argued from the fragment. / **The missing two-thirds.** The eastern part of the world map is lost, along with whatever it said. | …and the 1935 edition says that map “has not been found,” so the question can only be argued from the fragment. / **The rest of the map.** Akçura says the remaining parts were “torn away and lost.” Dutch reads the torn eastern edge as the map having been torn in half. How much is missing is an inference from the tear, not a documented figure. | documented fact + attributed interpretation + uncertainty kept |
| 7 | A53 | 15 | If his note is right, information from a Columbus map survives only because he copied it. | If his note is right, the fragment preserves information from a Columbus map that, in 1935, had not been found. | conditional kept, dated |
| 8 | A53 | 20 (FAQ) | …The Columbus map itself is lost. | …The 1935 edition says Columbus’s own map “has not been found.” | as above |
| 9 | A51 | 24 (FAQ) | He also wrote the *Kitab-ı Bahriye* (Book of the Sea). | He also wrote a work on navigation, the *Bahriye*. | gloss removed; Akçura wording |
| 10 | A37, A42, A51, Wikipedia role | 25 (Sources) | Jolly: “vol. 11 (issue and date not printed…)”; Dutch “a geoscientist’s…”; Nature “(2023)”; Wikipedia “…and for the Topkapı location. A secondary summary, not a primary source.” | Jolly “vol. 11, no. 1 (Fall 1986)” with link to the journal’s own issue PDF; Dutch “a point-by-point critique”; Nature “(24 October 2023)”; Akçura bullet names the “has not been found” / “lost” statements; Wikipedia “used to locate the references above. A secondary summary, not a primary source; no claim in this article rests on it alone.” | citations made exact |
| 11 | FAQ-to-body match | 26 (JSON-LD) | FAQ answers 2 and 4 as before; typographic quotes dropped | answers regenerated from the corrected visible FAQ text (identical wording, typographic quotes kept) | schema matches body |

## Post 1920 (lycurgus-cup)
Before: modified `2026-11-02T20:50:12`, content_hash `c61b8530eb57d834814d8d09849e13cde83d7e38`. After: modified `2026-11-02T22:04:04`, content_hash `02525f8f39cc22533480c1c5f4ece85506e3f8ca`. Blocks 25 → 25.

| # | QA row | Block | Before | After |
|---|---|---|---|---|
| 12 | B35 | 8 | …caused by this colloidal metal. A nanometre is a billionth of a metre. | …caused by this colloidal metal. (sentence removed: uncited definition; 50–100 nm remains sourced to Freestone et al.) |

## Post 1924 (mesmerism)
Before: modified `2026-11-02T20:52:58`, content_hash `3d8f41cf528f27baf08ed4170079006f76834198`. After: modified `2026-11-02T22:04:16`, content_hash `6c22e567c9848fd9bc7893c57282563c8cb6a563`. Blocks 33 → 33.

| # | QA row | Block | Before | After |
|---|---|---|---|---|
| 13 | D49 | 22 | Mesmer’s follower the Marquis de Puységur described a trance state he called artificial somnambulism, and defended animal magnetism in a memoir that same year. | The Marquis de Puységur, a follower of Mesmer, defended animal magnetism in a memoir the same year; the modern English edition of that memoir carries the phrase “artificial somnambulism” in its title, naming the trance-like state he reported. |

## Posts not changed
1922 (change-blindness) and 1926 (crystal-skulls): no corrections were warranted by the QA. 1922: modified `2026-11-02T20:51:39`, content_hash `5ff50b4a0571a69beca449fee71acf8e19d17f09`, 30 blocks. 1926: modified `2026-11-02T20:54:10`, content_hash `b097f1ad3460780efabad87f24a7d2af57256eda`, 26 blocks.

## Block-count note for insertion work
Counts are top-level *sections* as returned by `post-sections.list`. In posts 1917, 1920 and 1924 some `<h2>` headings were published without block comments, so they are classic content outside the section index; in 1922 and 1926 headings are blocks. Insert by re-listing sections and using the fresh tokens, never by an index recorded here.

| Post | Sections | modified | content_hash |
|---|---|---|---|
| 1917 piri-reis-map | 27 | 2026-11-02T22:03:48 | 2049decfed3eec105714f3efa9214ba018ef7a8b |
| 1920 lycurgus-cup | 25 | 2026-11-02T22:04:04 | 02525f8f39cc22533480c1c5f4ece85506e3f8ca |
| 1922 change-blindness | 30 | 2026-11-02T20:51:39 | 5ff50b4a0571a69beca449fee71acf8e19d17f09 |
| 1924 mesmerism | 33 | 2026-11-02T22:04:16 | 6c22e567c9848fd9bc7893c57282563c8cb6a563 |
| 1926 crystal-skulls | 26 | 2026-11-02T20:54:10 | b097f1ad3460780efabad87f24a7d2af57256eda |

## Post-change verification (anonymous fetch of each live URL)
HTTP 200; exactly one Article, one FAQPage and one BreadcrumbList per post; all source text blocks present (A 42/42, B 38/38, C 38/38, D 40/40, E 31/31); FAQ JSON-LD answers equal the visible FAQ text for every question. Repo files `article.html` for A, B and D were updated to the live text.
