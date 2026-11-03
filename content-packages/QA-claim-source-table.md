# QA: claim-to-source table for live posts A–E

Prepared 2026-11-02 for the founder, at the request of the Experience 2.0 implementation session. Branch `feature/content-packages-a-f`, PR #734 (draft). **No live post was edited.** Corrections found are listed in section 4 for approval.

## 1. How to read this
- **Scope:** every statement in each live post that carries a number, date, name, attribution or quotation, grouped by claim. Pure connective prose, our own design statements (for example the demo's 300/100 ms timing) and internal links are not listed.
- **Snippets** are 15 words or fewer and were extracted *mechanically* from the source text saved during research (pattern match, word count enforced), so they are not retyped. Typographic quotes are normalised to straight quotes, and two PDF extraction artefacts remain as in the text layer (row C18 shows "I sec" for "1 sec"; rows B15, B28 and B33 come from a PDF whose font encoding drops word spaces, shown re-spaced with letters matched).
- **Method column:** `R` regex match on saved source text · `M` text copied from a parsed source opened in the session (Firecrawl PDF parse) · `M+d` as `M`, and the letters were also matched against a local decode of the same PDF · `C` Wikimedia Commons API field · `X` absence check.
- **Verdicts:** SUPPORTED (snippet states the claim); PARAPHRASE-OK (claim restates or combines what the source says; the gap is stated); UNVERIFIED (no opened source states it; those resting only on Wikipedia are tagged **WIKIPEDIA-ONLY**); NOT SUPPORTED (a source contradicts it; none found).

### Sources used
| Key | Source | Opened as |
|---|---|---|
| AK | Akçura 1935 (Wikisource transcription) | full text of the 1935 English edition via Wikisource |
| DU | Dutch, "The Piri Reis Map" (Wayback 2013) | archived page, full |
| MC | McIntosh 2000, publisher description (archive.org item page) | publisher description only; book lending-restricted (UGA Press page, fetched separately, carries the same blurb and "Published: 2000-07-07") |
| HG | Hapgood, archive.org item page | archive.org item page only (title); full text not readable |
| WP | Wikipedia "Piri Reis map" (secondary) | full page, used only to locate references and to audit what it alone supports |
| JO | Jolly (Firecrawl PDF parse) | full 12-page PDF through the Firecrawl PDF parser |
| NAT | Nature Communications 2023 article page | full article page |
| FLK | Rensink flicker demo page | full page |
| FR | Freestone et al. 2007 (Firecrawl PDF parse) | full PDF through the Firecrawl PDF parser; quotes copied from that output |
| BM | British Museum record H_1958-1202-1 (page metadata) | collection page metadata (og:description) via Firecrawl |
| FSH | Freestone et al. 2007 Springer page | Springer landing page (metadata) |
| DEC | Freestone et al. 2007 PDF (local decode, digits lost) | local pdftotext decode (loses digits and word spaces; used for letter cross-checks) |
| SAX | Sax et al. 2008, J. Archaeol. Sci. (PDF) | full 20-page PDF, via a third-party-hosted copy with identical bibliographic data |
| R97 | Rensink, O'Regan, Clark 1997 (author PDF) | full PDF |
| S98 | Simons & Levin 1998 (Springer PDF) | full PDF (Springer) |
| PM05 | Simons & Rensink 2005 (PubMed abstract) | abstract |
| PM99 | Simons & Chabris 1999 (PubMed abstract) | abstract |
| RP | Franklin commission report, 1785 transl. (Gutenberg #78413) | full text |
| PDR | Laukaityte, Public Domain Review 2018 | full essay |
| FAK | Final Vestige draft post 1358 (first-party) | our own draft post 1358, read through the WordPress.com connector |
| C | Wikimedia Commons file pages (licence, credit, description) | API calls during this run |

## 2.1 Post A: https://finalvestige.com/2026/11/02/piri-reis-map/ (ID 1917)

| # | Claim in the post | Source · locator | Verbatim snippet (≤15 words) | M | Verdict | Note |
|---|---|---|---|---|---|---|
| A1 | Drawn at Gallipoli in Muharram 919 AH by Piri ibn Haji Mehmed, "known as the nephew of Kemal Reis" | AK · Inscription IV | “known as the nephew of Kemal Reis, in Gallipoli, in the month of muharrem” | R | SUPPORTED |  |
| A2 | 919 AH converts to 9 March–7 April 1513 | AK · Inscription IV (editors' gloss) | “between the 9th of March and the 7th of April of the year 1513” | R | SUPPORTED | Conversion is the 1935 editors' own. |
| A3 | Rediscovered in the Topkapı Palace in 1929, found by museum director Halil Edhem Eldem | AK · Intro §1 | “discovered by B. Halil Etem Eldem, Director of National Museums, in 1929” | R | PARAPHRASE-OK | Source spells the name Etem; common usage is Edhem. |
| A4 | Discovery happened while the palace was being turned into a museum | AK · Intro §1 | “when the Palace of Topkapu was being turned into a museum” | R | SUPPORTED |  |
| A5 | Examined with the visiting German orientalist Paul Kahle | AK · Intro §1 | “examined this map together with Professor Kahle, the German orientalist” | R | PARAPHRASE-OK | "visiting": source says Kahle was "then a visitor in Istanbul" (same sentence group). |
| A6 | Kahle announced it at the Eighteenth Congress of Orientalists, Leiden, September 1931 | AK · Intro §1 | “XVIII th Congress of Orientalists, which met in September 1931 at Leyden” | R | SUPPORTED |  |
| A7 | Newspapers called it the "map of Christopher Columbus" | AK · Intro §1 | “gave the name of "map of Christopher Columbus"” | R | SUPPORTED | "soon" is our gloss. |
| A8 | The publishing society calls the views attached to that label "erroneous and misleading" | AK · Intro §1 | “views that were erroneous and misleading” | R | SUPPORTED | Society = Turkish Historical Society (publisher of the 1935 edition). |
| A9 | Presented to Selim I in 1517 | AK · Intro §3 | “in 1517, when in Egypt, personally presented it to Selim I” | R | SUPPORTED |  |
| A10 | Presented in Cairo (Bahriye quotation) | AK · Intro §5, Bahriye quotation | “presented this map to the late Sultan Selim Han in Cairo” | R | SUPPORTED |  |
| A11 | Selim had just conquered Egypt | AK · Intro §3 | “Selim I., the Conqueror of Egypt” | R | PARAPHRASE-OK | "had just" is inferred from the 1517 date. |
| A12 | Kitab-ı Bahriye is Piri Reis's work on navigation | AK · Intro §1 | “work on navigation, "Bahriye"” | R | SUPPORTED |  |
| A13 | The Bahriye is the "later" sea-book (completed after the map) | WP · Wikipedia, History | “completed in 1521” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY. Akçura gives no date for the Bahriye. Proposed fix in section 4. |
| A14 | Map is drawn in colour on parchment | AK · Intro §3 | “The map, which is in colours, is drawn on parchment” | R | SUPPORTED |  |
| A15 | Surviving piece is part of a larger world map | AK · Intro §3 | “is part of a large-scale map of the world” | R | SUPPORTED |  |
| A16 | Marginal notes torn along the eastern edge | AK · Intro §3 | “marginal notes on its eastern edge” | R | SUPPORTED |  |
| A17 | Source list: about twenty charts and mappae mundi | AK · Inscription VI | “From about twenty charts and Mappae Mundi” | R | SUPPORTED |  |
| A18 | Eight "Jaferiye" charts and one Arabic map of India | AK · Inscription VI | “from eight Jaferiyes of that kind and one Arabic map of Hind” | R | PARAPHRASE-OK | Source says "Hind"; article renders it "India". Also in the source: the Arabs name these charts Jaferiye. |
| A19 | Four recently drawn Portuguese maps | AK · Inscription VI | “from the maps just drawn by four Portuguese” | R | SUPPORTED |  |
| A20 | A map by Columbus | AK · Inscription VI | “a map drawn by Colombo in the western region” | R | SUPPORTED |  |
| A21 | He reduced them all to a single scale | AK · Inscription VI | “By reducing all these maps to one scale” | R | SUPPORTED |  |
| A22 | Columbus called "a Genoese infidel" | AK · Inscription V | “a Genoese infidel, his name was Colombo” | R | SUPPORTED |  |
| A23 | Spanish king gave Columbus ships | AK · Inscription V | “the Bey of Spain gave him two ships” | R | SUPPORTED |  |
| A24 | Kemal Reis held a Spanish prisoner who sailed three times with Columbus | AK · Inscription V | “he had been three times to that land with Colombo” | R | PARAPHRASE-OK | Inscription says "slave"; editors' intro says "prisoner". |
| A25 | Piri Reis relays the prisoner's account of the route | AK · Inscription V | “First we reached the Strait of Gibraltar, then from there straight south and west” | R | SUPPORTED |  |
| A26 | Coasts and islands taken from Columbus's map | AK · Inscription V | “coast and islands on this map are taken from Colonbo's map” | R | PARAPHRASE-OK | Article says "Caribbean coasts"; source says shores of Antilia / the islands. |
| A27 | Piri Reis nephew of Kemal Reis, one of the Turkish admirals; later an admiral (supports FAQ "naval commander", "sailor") | AK · Intro §6 | “one of the Turkish admirals in the Mediterranean” | R | SUPPORTED |  |
| A28 | McIntosh: Columbus material from the Second Voyage (1493–1496) | MC · Publisher description | “draws instead on the Second Voyage of 1493-1496” | R | SUPPORTED | Publisher blurb only; book not read. |
| A29 | …and not the Third Voyage, as some earlier scholars thought | MC · Publisher description | “Reis map embodied Columbus's Third Voyage map of 1498” | R | SUPPORTED |  |
| A30 | McIntosh rejects the Antarctica-as-ancient-evidence reading | MC · Publisher description | “refutes the popular misinterpretation that Reis's depictions of Antarctica are evidence of either ancient civilizations” | R | SUPPORTED | Same blurb on the UGA Press page. |
| A31 | McIntosh, The Piri Reis Map of 1513, University of Georgia Press, 2000 | MC · Archive.org metadata | “Publication date 2000” | R | PARAPHRASE-OK | Publisher from the UGA Press page (site name "Georgia Press", "Published: 2000-07-07"), fetched separately. |
| A32 | Hapgood's book is titled Maps of the Ancient Sea Kings | HG · Archive.org item title | “Maps of the ancient sea kings : evidence of advanced civilization in the ice age” | R | SUPPORTED | Book not readable (lending-restricted). |
| A33 | Hapgood concluded part of the South American coast was a misplaced, ice-free Antarctica | JO · Jolly, Hapgood section | “really a misplaced section of Antarctica, shown without ice” | M | SUPPORTED | Jolly text via Firecrawl PDF parse. |
| A34 | Jolly: Hapgood stacked unproven assumptions | JO · Jolly | “Hapgood operated by concatenating unproven assumptions.” | M | SUPPORTED |  |
| A35 | Credited ancient knowledge when matched; blamed the mapmaker when not | JO · Jolly | “he credited ancient wisdom” | M | PARAPHRASE-OK | Companion text: "the sixteenth-century mapmaker must have misinterpreted his sources or made a copying error". |
| A36 | That makes the idea impossible to test | JO · Jolly | “It is an approach that makes his hypothesis unfalsifiable” | M | SUPPORTED |  |
| A37 | Jolly published in Skeptical Inquirer, vol. 11 | JO · — | (no journal name or volume appears in the opened text) | X | **UNVERIFIED** | UNVERIFIED. The journal and volume came from a web-search summary, not from text opened. Correction proposed. |
| A38 | East Antarctic Ice Sheet has origins about 34 million years ago | NAT · Abstract | “The East Antarctic Ice Sheet (EAIS) has its origins ca. 34 million years ago” | R | SUPPORTED |  |
| A39 | That study is from 2023 in Nature Communications | NAT · Article header | “Published: 24 October 2023” | R | SUPPORTED | Journal name from the URL pattern (s41467) and site; page header. |
| A40 | Dutch: marginal notes show 16th-century origin | DU · "The Marginal Notes" | “pretty conclusively show the map is entirely 16th century terrestrial in origin” | R | SUPPORTED |  |
| A41 | Dutch: beyond southern Brazil the coast matches neither South America nor Antarctica well | DU · "Beyond that, though" passage | “It doesn't match either South America or Antarctica very well” | R | SUPPORTED |  |
| A42 | Steven Dutch is a geoscientist at University of Wisconsin–Green Bay | DU · Page header | “Steven Dutch, Natural and Applied Sciences, University of Wisconsin - Green Bay” | R | PARAPHRASE-OK | "Geoscientist": from a search-result excerpt of his homepage ("Professor Emeritus (Geoscience)"), not from the archived page. |
| A43 | Jolly: southern continent drawn differently across maps; long-standing belief in one | JO · Jolly, Finaeus section | “the varying shape of Terra Australis on maps both before and after the Finaeus map” | M | PARAPHRASE-OK | Jolly's example is the Finaeus map; article generalises to "sixteenth-century maps". Also in Jolly: "conform to ancient belief in a southern continent". |
| A44 | Language of the notes is Turkish (alt text: "Ottoman Turkish") | DU · "The Marginal Notes" | “the language on the map is Turkish, not Arabic” | R | PARAPHRASE-OK | "Ottoman" is our gloss. |
| A45 | 1935 Turkish Historical Society edition, Istanbul; author Yusuf Akçura | AK · Title page | “Published by Türk Tarih Kurumu (Turkish Historical Society)” | R | SUPPORTED | Year and place from title-page lines. |
| A46 | Caption: Topkapı Palace Museum Library; public domain | C (File:Piri reis world map 01.jpg) · Commons credit + licence fields | “Library of Topkapi Palace Museum” | C | SUPPORTED | Licence field: Public domain. |
| A47 | Caption: Cantino planisphere, Biblioteca Estense, Modena; public domain | C (File:Cantino planisphere (1502).jpg) · Commons credit + licence fields | “Biblioteca Estense Universitaria, Modena” | C | SUPPORTED |  |
| A48 | Caption: "Modern scholars use charts of this kind as comparison points for the Portuguese material Piri Reis says he used" | WP · Wikipedia, Analysis | “Portuguese source maps would have been similar to surviving maps like the 1502” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY. In no primary source opened. Proposed fix in section 4. |
| A49 | Alt text: Cantino map shows "the line dividing the Spanish and Portuguese zones" | C (File:Cantino planisphere (1502).jpg) · Commons description | “Cantino planisphere” | C | **UNVERIFIED** | UNVERIFIED. Commons text does not mention the line. Proposed fix in section 4. |
| A50 | "After that, the map disappears from the record. Nobody knows what Selim made of it." | WP · Wikipedia, History | “It is unknown how Selim used the map, if at all” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY. Akçura does not say this. Proposed fix in section 4. |
| A51 | FAQ/body: Kitab-ı Bahriye = "Book of the Sea" | WP · Wikipedia, History | “Kitab-ı Bahriye” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY gloss of the title. Proposed fix in section 4. |
| A52 | Popular claims include proof of a vanished civilization | MC · Publisher description | “evidence of either ancient civilizations or extraterrestrial visitation” | R | PARAPHRASE-OK | "vanished civilization" paraphrases "ancient civilizations". |
| A53 | "The Columbus map itself has not survived / is lost" (body, FAQ, uncertainty list) | WP · Wikipedia, lead | “an otherwise lost map by” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY. No opened primary or scholarly source says the Columbus map is lost. Proposed fix in section 4. |
| A54 | "The missing two-thirds" (only about one third survives) | WP · Wikipedia, lead | “Approximately one third of the map survives” | R | **UNVERIFIED (WIKIPEDIA-ONLY)** | WIKIPEDIA-ONLY fraction. Akçura supports only "part of a large-scale map" with torn eastern notes. Proposed fix in section 4. |

## 2.2 Post B: https://finalvestige.com/2026/11/02/lycurgus-cup/ (ID 1920)

| # | Claim in the post | Source · locator | Verbatim snippet (≤15 words) | M | Verdict | Note |
|---|---|---|---|---|---|---|
| B1 | First appeared in print in 1845; early history and findspot unknown; Rothschilds acquired it soon after | FR · Introduction | “The Lycurgus Cup is first mentioned in print in 1845” | M | SUPPORTED | Companion text: "the early history of the cup is unknown (as is the find spot)". |
| B2 | Reflected light: opaque greenish-yellow, jade-like | FR · Introduction | “in direct light it resembles jade with an opaque greenish-yellow tone” | M | SUPPORTED |  |
| B3 | Transmitted light: translucent ruby | FR · Introduction | “it turns to a translucent ruby colour” | M | SUPPORTED |  |
| B4 | A late Roman vessel in the British Museum | FR · Introduction | “This late Roman cut glass vessel is extraordinary in several respects” | M | SUPPORTED | Museum location: BM record (B9). |
| B5 | Acquired from Lord Rothschild in 1958 with National Art Collection Fund help | FR · Introduction | “from Lord Rothschild in 1958 (with the aid of a contribution from” | M | SUPPORTED | Fund name in the next line of the source: "National Art Collection Fund". |
| B6 | Cage cups or diatreta; openwork joined by bridges | FR · Introduction | “Roman vessels known as cage cups or diatreta” | M | SUPPORTED |  |
| B7 | Cage cups generally dated to the fourth century AD | FR · Introduction | “Cage cups are generally dated to the fourth century A.D.” | M | SUPPORTED |  |
| B8 | Probably only 50–100 examples known | FR · Introduction | “probably only in the region of 50-100 examples are known” | M | SUPPORTED |  |
| B9 | This cup's scene is more elaborate and better preserved than the other figurative cage cups | FR · Introduction | “none of these is as elaborate or as well preserved as the Lycurgus Cup” | M | SUPPORTED |  |
| B10 | Scene: King Lycurgus of the Edoni in Thrace killed by Dionysus and his followers | FR · Introduction | “King of the Edoni in Thrace at the hands of Dionysus and his followers” | M | PARAPHRASE-OK | Source: "A man of violent temper, Lycurgus attacked Dionysus". |
| B11 | BM record: green and red glass drinking-cup, Lycurgus scenes | BM · Page metadata (og:description) | “Drinking-cup; glass; green and red; covered with various scenes representing the death of King Lycurgus” | M | SUPPORTED | Registration 1958,1202.1 is in the URL and in the Freestone figure captions. |
| B12 | Silver-gilt rim band and foot | BM · Page metadata (og:description) | “rim mounted with silver-gilt band of leaf ornament, plus silver-gilt foot” | M | SUPPORTED |  |
| B13 | Height 16.5 cm with modern mounts, diameter 13.2 cm | FR · Figure 1 caption | “Height: 16.5 cm (with modern metal mounts), diameter: 13.2 cm” | M | SUPPORTED |  |
| B14 | Freestone, Meeks, Sax, Higgitt, Gold Bulletin 40 (2007) 270–277 | FSH · Springer article page | “Published: December 2007 Volume 40 , pages 270–277 ( 2007 )” | R | SUPPORTED | Authors from the same page. |
| B15 | Authors at the British Museum and Cardiff University | DEC · Title block of PDF (squashed text) | “Cardiff School of History and Archaeology” | R | PARAPHRASE-OK | Verified on the squashed local decode; also "The British Museum" affiliation. |
| B16 | Body of Lycurgus cut from glass more violet in transmitted, more yellow in reflected light | FR · "Colour" section | “more violet in transmitted light and more yellow in reflection” | M | SUPPORTED |  |
| B17 | Glass behind figures hollowed or bored out so light passes through similarly | FR · "Colour" section | “has been hollowed or bored out” | M | PARAPHRASE-OK | Purpose clause paraphrases the next sentence of the source. |
| B18 | TEM: metal particles typically 50–100 nm | FR · Analysis section | “typically 50-100 nm in diameter” | M | SUPPORTED |  |
| B19 | Silver:gold about 7:3, about 10% copper | FR · Analysis section | “a ratio of silver to gold of about 7:3, containing in addition about 10% copper” | M | SUPPORTED |  |
| B20 | Dichroic effect caused by colloidal metal | FR · Analysis section | “the dichroic effect is caused by colloidal metal” | M | SUPPORTED |  |
| B21 | Debate whether the cup was glass; optical behaviour made it hard to believe | FR · Introduction | “seemed impossible, with the technical knowledge of ancient glass-working at the time” | M | PARAPHRASE-OK | Source says it "seemed impossible" to produce such an effect; "some people doubt" = initial debate over whether it was glass. |
| B22 | Mineralogist concluded it was glass (not opal or jade) | FR · Introduction | “concluded that it was made of glass (rather than opal or jade)” | M | SUPPORTED | Dr G.F. Claringbull, Keeper of Mineralogy, BM (Natural History). |
| B23 | X-ray diffraction confirmed in 1959 | FR · Introduction | “later confirmed in 1959 by X-ray diffraction” | M | SUPPORTED |  |
| B24 | Romans coloured glass with metals; opaque reds/browns with copper | FR · Context section | “opaque red and brown glasses were produced by the addition of copper” | M | SUPPORTED |  |
| B25 | Slag/dross by-products may explain discovery of the effect | FR · Context section | “oxidised by-products of metallurgical processes ("dross", "slag" etc)” | M | SUPPORTED |  |
| B26 | Other possibilities including accidents with gold-leaf decoration | FR · Context section | “accidents in the production of glasses with gold leaf decoration” | M | SUPPORTED |  |
| B27 | Inability to control the process: few such glasses, even fewer survive | FR · Conclusion | “the inability to control the colourant process meant that relatively few glasses” | M | SUPPORTED |  |
| B28 | Understanding of how this glass was produced is unclear | DEC · Context section (squashed local decode) | “understanding of the production of this glass is unclear” | R | SUPPORTED | Letters-only match: the local PDF decode drops spaces. |
| B29 | Corning replica blank, 1960s | FR · Cutting section | “The Corning Glassworks produced a replica of the blank in the 1960s” | M | SUPPORTED |  |
| B30 | Blank walls about 15 mm thick | FR · Cutting section | “must have had walls about 15 mm thick” | M | SUPPORTED |  |
| B31 | Tool marks suggest rotary abrasion and polishing | FR · Cutting section | “suggest the use of rotary abrasion and polishing” | M | SUPPORTED |  |
| B32 | Paper takes evidence as cutting and grinding, not moulding | FR · Cutting section | “cutting and grinding rather than moulding of soft glass” | M | SUPPORTED |  |
| B33 | Another researcher (Lierke) argued diatreta were moulded | DEC · Cutting section (squashed local decode) | “were not formed by cold cutting of glass blanks but by moulding” | R | SUPPORTED | Researcher not named in the article; source names Lierke. |
| B34 | Study calls it the outstanding example and a unique record | FR · Conclusion | “The Cup is the outstanding example of this technology in every respect” | M | SUPPORTED | "unique record" in the following clause. |
| B35 | A nanometre is a billionth of a metre | FR · — | (definition; no source cited or opened) | X | **UNVERIFIED** | UNVERIFIED as sourced. Common-knowledge definition with no citation. Proposed fix P11 in section 4 (low risk). |
| B36 | Photos by Chappsnet, CC BY 4.0 (two images) | C (File:Front of 4th century CE Roman Lycurgus Cup, British Museum (1958,1202.1).jpg) · Commons licence and author fields | “CC BY 4.0” | C | SUPPORTED | Second image checked in the same way. |
| B37 | "Puzzling people since it first appeared in print in 1845" | FR · Introduction | “first mentioned in print in 1845” | M | PARAPHRASE-OK | Inference from first-print date plus the early doubt about whether it was glass. |
| B38 | Most cage cups are decorated with simple lattices of linked circles | FR · Introduction | “Typically these openwork "cages" comprise a lattice of linked circles” | M | SUPPORTED |  |

## 2.3 Post C: https://finalvestige.com/2026/11/02/change-blindness/ (ID 1922)

| # | Claim in the post | Source · locator | Verbatim snippet (≤15 words) | M | Verdict | Note |
|---|---|---|---|---|---|---|
| C1 | Flicker study: Rensink, O'Regan, Clark; Psychological Science 8, 368–373 (1997) | FLK · Researcher's publication list | “Rensink RA, O'Regan JK, and Clark JJ (1997). To See or Not to See” | R | SUPPORTED | Journal, volume, pages: "Psychological Science , 8 :368-373" on the same page; author PDF carries the same volume/pages but no year. |
| C2 | Each image 240 ms, each blank 80 ms | R97 · General Method | “Each image was displayed for 240 ms and each blank for 80 ms” | R | SUPPORTED |  |
| C3 | Each image shown twice before switching (A, A, A', A') | R97 · General Method | “Note that each image was presented twice before being switched” | R | SUPPORTED |  |
| C4 | Gray blank field between images | R97 · General Method | “gray blank fields placed between successive images” | R | SUPPORTED |  |
| C5 | 48 colour photographs of real-world scenes | R97 · General Method | “same set of 48 color images of real-world scenes” | R | SUPPORTED |  |
| C6 | Changes: appear/disappear, colour, position | R97 · General Method | “color, location, or presence/absence” | R | PARAPHRASE-OK | Order and wording differ. |
| C7 | Ten naive observers per experiment | R97 · General Method | “Ten naive observers participated in each experiment” | R | SUPPORTED |  |
| C8 | Central/marginal interest defined by five naive observers, three or more vs none | R97 · General Method | “central interests (CIs) were defined as objects or areas mentioned by three or more observers” | R | SUPPORTED | Five observers and "none" for marginal interests are in the sentence before and after. |
| C9 | Marginal-interest changes: mean 17.1 alternations (10.9 s); some >80 (50 s) | R97 · Experiment 1 | “an average of 17.1 alternations [10.9 seconds]” | R | SUPPORTED | "over 80 alternations [50 seconds]" in the same paragraph. |
| C10 | Central-interest changes: mean 7.3 alternations (4.7 s) | R97 · Experiment 1 | “an average of 7.3 alternations [4.7 seconds]” | R | SUPPORTED |  |
| C11 | Without blanks: 1.4 alternations (0.9 s) | R97 · Experiment 1 | “only 1.4 alternations [0.9 seconds] on average” | R | SUPPORTED |  |
| C12 | Observers pressed a key when they saw the change | R97 · General Method | “press a key when they” | R | SUPPORTED |  |
| C13 | Conclusion: attention is the critical factor; blanks swamp local signal | FLK · Researcher's own page | “Our findings indicate that the critical factor is attention” | R | SUPPORTED | Also R97: "The flicker caused by the blank fields will swamp the local motion signals". |
| C14 | Researcher's page offers flicker examples to view | FLK · Researcher's page | “Examples that can be viewed or downloaded” | R | SUPPORTED |  |
| C15 | Door study: Simons & Levin, Psychonomic Bulletin & Review 5(4), 644–649 (1998) | S98 · Header | “Psychonomic Bulletin & Review 1998. 5 (4). 644-649” | R | SUPPORTED |  |
| C16 | Cornell University campus; experimenter with a map asked directions | S98 · Exp 1, Method | “campus of Cornell University” | R | SUPPORTED | Also: "carrying a campus map asked unsuspecting pedestrians for directions". |
| C17 | Door passed after 10–15 seconds of conversation | S98 · Exp 1, Procedure | “talking for 10-15 sec” | R | SUPPORTED |  |
| C18 | Door blocked view for about one second | S98 · Exp 1, Procedure | “blocked the pedestrian's view for approximately I sec” | R | SUPPORTED | Source text reads "I sec" (OCR of "1 sec") in the PDF text layer. |
| C19 | Experimenters differed in clothing and height (about 5 cm); voices distinguishable | S98 · Exp 1, Procedure | “differed in height by approximately 5 cm” | R | SUPPORTED | Voices: "Their voices were also clearly distinguishable". |
| C20 | 15 pedestrians | S98 · Exp 1, Method | “A total of 15 pedestrians were approached” | R | SUPPORTED |  |
| C21 | Only 7 of 15 noticed | S98 · Exp 1, Results | “only 7 ofthe 15 pedestrians reported noticing the change” | R | SUPPORTED |  |
| C22 | Noticers were students of about the same age (20–30); non-noticers older (35–65) | S98 · Exp 1, Results | “all students of roughly the same age as the experimenters” | R | SUPPORTED | Age ranges: "(approximately 20~30 years old)" and "(approximately 35-65 years old)". |
| C23 | Those who missed it were surprised | S98 · Exp 1, Results | “were quite surprised to learn” | R | SUPPORTED |  |
| C24 | Exp 2: construction-worker clothing, 12 student pedestrians | S98 · Exp 2, Method | “all 12 pedestrians who participated in Experiment 2 were from the younger age group” | R | SUPPORTED |  |
| C25 | 4 of 12 noticed when asked if anything unusual | S98 · Exp 2, Results | “only 4 of the 12 pedestrians in Experiment 2 reported noticing the switch” | R | SUPPORTED |  |
| C26 | Three more claimed to have noticed but could not describe differences | S98 · Exp 2, Results | “could not accurately describe any of the differences” | R | SUPPORTED | "An additional 3 subjects" in the preceding sentence. |
| C27 | Authors' explanation: category ("construction worker") rather than individual features | S98 · Exp 2, Discussion | “she quickly categorized the experimenter as a construction worker” | R | PARAPHRASE-OK |  |
| C28 | Conclusion: attention alone does not suffice, even in the real world | S98 · General Discussion | “Attention alone does not suffice for change detection, even in the real world” | R | SUPPORTED |  |
| C29 | Detection likely needs effortful encoding of distinguishing features | S98 · General Discussion | “successful change detection probably requires effortful encoding” | R | SUPPORTED |  |
| C30 | "Only half of the pedestrians detected the change" (8 of 15 missed) | S98 · Abstract | “Onlyhalf of the pedestrians detected the change” | R | PARAPHRASE-OK | Article: "7 of 15 noticed, so 8 did not"; intro says "half … did not notice" (8/15 = 53%). |
| C31 | 33 percent figure | S98 · Exp 2, Results | “33%” | R | SUPPORTED | Source: "detected it only 33% of the time in Experiment 2". |
| C32 | Authors considered social-demand and distraction objections | S98 · General Discussion | “One potential objection to our results derives from the pragmatics of the interaction” | R | SUPPORTED | Distraction objection: "Another possible objection is that the task of giving directions distracted subjects". |
| C33 | Social demands seemed to increase reports of the switch, not decrease them | S98 · General Discussion | “the demands of the situation seem biased to increase reports of the switch” | R | SUPPORTED |  |
| C34 | Ongoing work examining distraction | S98 · General Discussion | “ongoing experiments using a different type of interaction” | R | SUPPORTED |  |
| C35 | 2005 review: change blindness is a failure to see large changes | PM05 · Abstract | “the striking failure to see large changes that normally would be noticed easily” | R | SUPPORTED | Also: 2005, Trends Cogn Sci 9(1):16-20 in the PubMed citation line. |
| C36 | 2005 review: counterintuitive nature produced confusions about inferences | PM05 · Abstract | “its counterintuitive nature has also engendered confusions about the kinds of inferences” | R | SUPPORTED |  |
| C37 | Authors of the 2005 review: Simons and Rensink | PM05 · PubMed page | “Simons” | R | PARAPHRASE-OK | Author byline verified on the PubMed page; citation fixed by the page title "Change blindness: past, present, and future". |
| C38 | 1999 Gorillas: without attention we may not perceive objects ("inattentional blindness") | PM99 · Abstract | “without attention, we may not even perceive objects ('inattentional blindness')” | R | SUPPORTED |  |
| C39 | Noticing an unexpected object depends on similarity and task difficulty | PM99 · Abstract | “the likelihood of noticing an unexpected object depends on the similarity of that object” | R | SUPPORTED | Task difficulty: "how difficult the priming monitoring task is" in the same sentence. |
| C40 | Gorillas paper is Perception 28, 1059–1074 (1999) | PM99 · PubMed citation line | “1999;28(9):1059-74” | R | SUPPORTED |  |
| C41 | "Two classic experiments from the 1990s" | FLK · Publication list + S98 header | “Clark JJ (1997)” | R | PARAPHRASE-OK | 1997 (C1) and 1998 (C15). |
| C42 | Change typically goes unseen when an eye movement, film cut, blank or interruption intervenes | R97 · Intro of R97 | “saccade” | R | PARAPHRASE-OK | R97 discusses saccade-based change blindness; S98 General Discussion lists motion-picture studies. Combined paraphrase. |

## 2.4 Post D: https://finalvestige.com/2026/11/02/mesmerism/ (ID 1924)

| # | Claim in the post | Source · locator | Verbatim snippet (≤15 words) | M | Verdict | Note |
|---|---|---|---|---|---|---|
| D1 | Mesmer moved to Paris by 1778 after falling into royal disfavour in Vienna | PDR · "Mesmerising Science", section on Mesmer's career | “By 1778, having fallen into considerable royal disfavour, Mesmer moved to Paris” | R | SUPPORTED |  |
| D2 | Paris physicians refused him a licence; he partnered with licensed physician Charles Deslon | PDR · same | “denied him a medical license, he partnered up with the respectable and licensed Charles Deslon” | R | SUPPORTED |  |
| D3 | Deslon: personal doctor to the king's brother | PDR · same | “personal physician to the brother of King Louis XVI” | R | SUPPORTED |  |
| D4 | Practice among upper-class patients in Vienna | PDR · same | “treating mostly upper-class women” | R | PARAPHRASE-OK | Article says "upper-class patients"; essay says "mostly upper-class women". |
| D5 | Theory: imperceptible magnetic fluid pervading the universe; disease from abnormal flow | PDR · same | “a special kind of imperceptible magnetic fluid pervaded the universe” | R | SUPPORTED |  |
| D6 | First magnets, later hands or other objects worked just as well | PDR · same | “simply using his hands or other objects was just as effective” | R | SUPPORTED |  |
| D7 | Session: patients, tub, iron rods, rope, mirrors, music, ending in a "crisis" | PDR · Opening scene | “Patients, mostly women, are sitting around a large wooden tub” | R | PARAPHRASE-OK | Rope, mirrors and music are in the next sentences of the same paragraph; crisis in the last. |
| D8 | Crisis of hiccups, sobs, coughing and fainting | PDR · Opening scene | “nervous hiccups, hysterical sobs, cries, coughs, spitting, fainting, and convulsing” | R | SUPPORTED |  |
| D9 | Franklin appointed head of the royal commission | PDR · same | “Franklin was appointed as head of the royal commission” | R | SUPPORTED |  |
| D10 | Mesmer's description of the agent: a fluid universally diffused | RP · Report, Mesmer's definition | “It is a fluid universally diffused” | R | SUPPORTED | Continues "the vehicle of a mutual influence". |
| D11 | King named four physicians of the Paris faculty on 12 March 1784 | RP · Report, opening | “on the twelfth of March 1784, four physicians of the faculty of Paris” | R | SUPPORTED |  |
| D12 | …to examine "the animal magnetism practised by M. Deslon" | RP · Report, opening | “the animal magnetism practised by M. Deslon” | R | SUPPORTED |  |
| D13 | Five Academy members added: Franklin, Le Roy, Bailly, de Borie, Lavoisier | RP · Report, opening | “messieurs Franklin, le Roy, Bailly, de Borie, Lavoisier” | R | SUPPORTED | Preceded by "five members of the royal academy of sciences". |
| D14 | One commissioner died and was replaced by Majault | RP · Report, opening | “M. Borie having died in the commencement of the business” | R | SUPPORTED | Replacement: "his majesty appointed M. Majault" follows. |
| D15 | Report dated Paris, 11 August 1784 | RP · Report, close | “Paris, the 11th day of August, 1784” | R | SUPPORTED |  |
| D16 | Signed by Franklin, Majault, Le Roy, Sallin, Bailly, d'Arcet, de Bory, Guillotin, Lavoisier | RP · Report, close | “B. FRANKLIN, MAJAULT, LE ROY, SALLIN, BAILLY” | R | SUPPORTED | Remaining names follow in the same line. |
| D17 | Report is a 1785 English translation published in London (J. Johnson) | RP · Gutenberg header | “Original publication: London: J. Johnson, 1785” | R | SUPPORTED |  |
| D18 | Seven patients from the lower class at Franklin's house in Passy | RP · Report, Passy trials | “Seven of these were assembled at Passy, at the house of Dr. Franklin” | R | SUPPORTED | "lower class": "we chose them out of the lower class" in the preceding sentence. |
| D19 | Fourteen sick persons: five felt an effect, nine none | RP · Report, summary of trials | “Of fourteen sick persons five only appeared to feel any effect from the operation” | R | SUPPORTED | "nine felt no effect at all" follows in the same sentence. |
| D20 | A commissioner with headache and cold feet derived no benefit | RP · Report, summary of trials | “derived no benefit from the magnetism” | R | SUPPORTED |  |
| D21 | Trials with a magnetiser named Jumelin | RP · Report, blindfold trial | “M. Jumelin having applied his hands” | R | SUPPORTED |  |
| D22 | Blindfolded woman: sensitivity "perfectly established" | RP · Report, blindfold trial | “The sensibility of this woman being perfectly established” | R | SUPPORTED |  |
| D23 | Once blindfolded, effects no longer matched where magnetism was directed | RP · Report, blindfold trial | “the phenomena no longer answered to the places towards which the magnetism was directed” | R | SUPPORTED |  |
| D24 | With bandage on and no operation, same effects | RP · Report, blindfold trial | “experienced all the same effects, though no operation was performed” | R | SUPPORTED |  |
| D25 | Apricot tree test: boy about twelve; tree in Franklin's orchard | RP · Report, tree experiment | “an apricot tree was fixed upon in the orchard of Dr. Franklin's garden” | R | SUPPORTED |  |
| D26 | Boy blindfolded and made to embrace four untreated trees | RP · Report, tree experiment | “presented successively to four trees upon which the operation had not been performed” | R | SUPPORTED |  |
| D27 | Two minutes at each tree | RP · Report, tree experiment | “for the space of two minutes” | R | SUPPORTED |  |
| D28 | At the fourth tree, about 24 feet from the treated tree, he fell into a crisis and fainted | RP · Report, tree experiment | “at the distance of about twenty four feet from the tree which had” | R | SUPPORTED | "he fainted away" in the same sentence. |
| D29 | Commissioners: crisis had no physical external cause | RP · Report, tree experiment | “the crisis was therefore the effect of no physical or exterior cause” | R | SUPPORTED |  |
| D30 | Sham treatment: woman told Deslon had come to treat her; a commissioner impersonated him | RP · Report, Passy sham | “She was persuaded that M. Deslon had been brought into the room” | R | SUPPORTED | Impersonation: "the third to personate M. Deslon". |
| D31 | She had films over her eyes; a bandage was used | RP · Report, Passy sham | “had films over her eyes” | R | SUPPORTED |  |
| D32 | Crisis within three minutes with shuddering, hand-striking, stamping | RP · Report, Passy sham | “At the end of three minutes the patient began to feel a nervous shuddering” | R | SUPPORTED |  |
| D33 | Commissioners in an adjoining room heard it through a closed door | RP · Report, Passy sham | “heard the stamping of the feet and the clapping of the hands” | R | SUPPORTED |  |
| D34 | Paper partition: seamstress "Mademoiselle B." known to be sensitive | RP · Report, paper-partition trial | “a sempstress by profession” | R | SUPPORTED | "whose sensibility to the magnetism was well known" follows. |
| D35 | Magnetised for half an hour in the way Deslon prescribed | RP · Report, paper-partition trial | “was accordingly magnetised during half an hour” | R | SUPPORTED | "in conformity to the rules taught by M. Deslon" in the same sentence. |
| D36 | Nothing for thirty minutes; had a crisis in three minutes at Passy | RP · Report, paper-partition trial | “at Passy she had fallen into a crisis in the course of three minutes” | R | SUPPORTED | "without any effect for thirty minutes" in the same passage. |
| D37 | Later, openly treated against the theory, she reacted within three minutes (dejection, suffocation, hiccup, chattering teeth) | RP · Report, paper-partition trial | “In three minutes however she felt a sensation of dejection and suffocation” | R | SUPPORTED |  |
| D38 | Conclusion: shown by "decisive experiments" | RP · Report, conclusion | “having demonstrated by decisive experiments, that the imagination without the magnetism produces convulsions” | R | SUPPORTED | Snippet 14 words. |
| D39 | "absolutely destitute of proof" | RP · Report, conclusion | “the existence of the fluid is absolutely destitute of proof” | R | SUPPORTED |  |
| D40 | Concluded unanimously | RP · Report, conclusion | “concluded with an unanimous voice” | R | SUPPORTED |  |
| D41 | Symptoms due to compression, imagination, imitation | RP · Report, conclusion | “to the compression, to the imagination called into action” | R | SUPPORTED | Imitation: "propensity to mechanical imitation" follows. |
| D42 | Crises potentially harmful; watching them dangerous | RP · Report, conclusion | “the repeated action of the imagination employed in producing the crises may be hurtful” | R | SUPPORTED |  |
| D43 | "real or pretended" sensations | RP · Report, Passy trials | “real or pretended” | R | SUPPORTED |  |
| D44 | Essay: trials were blind; suggestion as a rudimentary placebo control | PDR · same | “suggestion would then represent a rudimentary placebo control condition” | R | SUPPORTED | Attributed to the essay in the article. |
| D45 | Essay: two reports in 1784, one public, one secret for the king | PDR · same | “one public and one secret, only for the eyes of the king” | R | SUPPORTED |  |
| D46 | Essay: secret report concerned moral danger, male magnetiser and female patients | PDR · same | “the magnetiser is, as a rule, a man, and his patients are mostly women” | R | SUPPORTED |  |
| D47 | Essay: animal magnetism marked the beginnings of hypnosis and psychological suggestion | PDR · same | “animal magnetism marked the beginnings of hypnosis and psychological suggestion” | R | SUPPORTED |  |
| D48 | Essay author Urte Laukaityte, 20 November 2018 | PDR · Byline | “By Urte Laukaityte” | R | SUPPORTED | Date: "Published November 20, 2018" on the same page. |
| D49 | Puységur described a trance state called artificial somnambulism and defended animal magnetism in a 1784 memoir | FAK · Draft post 1358 | “circulated a memoir defending animal magnetism after official scientific scrutiny” | M | PARAPHRASE-OK | First-party draft only (not an external source). "artificial somnambulism" appears in the Routledge title the draft cites. See section 3 note. |
| D50 | Mesmer, eighteenth-century physician, "Franz Anton" | PDR · Essay text | “Franz Friedrich Anton Mesmer” | R | PARAPHRASE-OK | Essay gives the fuller name "Franz Friedrich Anton Mesmer". |
| D51 | Image: Wellcome Collection engraving, CC BY 4.0 | C (File:"Le Baquet de Mesmer" Wellcome M0006352.jpg) · Commons licence field | “CC BY 4.0” | C | SUPPORTED |  |

## 2.5 Post E: https://finalvestige.com/2026/11/02/crystal-skulls/ (ID 1926)

| # | Claim in the post | Source · locator | Verbatim snippet (≤15 words) | M | Verdict | Note |
|---|---|---|---|---|---|---|
| E1 | Study: Sax, Walsh, Freestone, Rankin, Meeks, J. Archaeol. Sci. 35 (2008) 2751–2760 | SAX · Header | “Journal of Archaeological Science 35 (2008) 2751-2760” | R | SUPPORTED | Author list in the byline of the same page. |
| E2 | Authors at the British Museum and the Smithsonian | SAX · Affiliations | “Department of Anthropology, Smithsonian Institution” | R | PARAPHRASE-OK | Also British Museum (Sax, Meeks), Cardiff (Freestone), Kingston (Rankin); article says "scientists at BM and Smithsonian". |
| E3 | BM skull carved from a single block of rock crystal | SAX · Introduction | “made from a single block of rock crystal in the British Museum” | R | SUPPORTED |  |
| E4 | About 15 cm high, 13.5 cm wide, 21 cm deep | SAX · Fig. 1 caption | “c. 15 cm high, 13.5 cm wide, 21 cm deep” | R | SUPPORTED |  |
| E5 | Bought from Tiffany & Co., New York, November 1897 | SAX · Introduction | “purchased from Tiffany and Company, Union Square, New York, in November 1897” | R | SUPPORTED |  |
| E6 | Kunz: Vice President of Tiffany's; mineralogist | SAX · Introduction | “George Frederick Kunz, Vice President of Tiffany's” | R | SUPPORTED | "a mineralogist of considerable standing" in the following sentence. |
| E7 | Kunz wrote to the Keeper (Charles Hercules Read) recommending the purchase | SAX · Introduction | “had written to (Sir) Charles Hercules Read, Keeper” | R | SUPPORTED |  |
| E8 | Kunz's 1890 book: skull brought from Mexico by a Spanish officer before the French occupation | SAX · Introduction | “was brought from Mexico by a Spanish officer sometime before the French occupation” | R | SUPPORTED | Attributed to Kunz in the article. |
| E9 | …sold to an English collector, at whose death it passed to Boban, then Sisson | SAX · Introduction | “at whose death it passed into the hands of E. Boban” | R | SUPPORTED | "and then became the property of Mr. Sisson" follows. |
| E10 | Kunz admitted little was known of its history | SAX · Introduction | “Little is known of its” | R | SUPPORTED | Page break after "its"; the next page opens "history and nothing of its origin" (checked in the PDF text). |
| E11 | Boban opened shop in Mexico City in 1885 and displayed the skull as unique, no provenance | SAX · Section 3 (Boban) | “Boban returned to Mexico City and opened a shop” | R | SUPPORTED | "pieza unica en el mundo" and "without details of provenance or date" follow. |
| E12 | Boban and Batres (inspector of monuments) tried to sell it to the Museo Nacional | SAX · Section 3 | “the inspector of archaeological monuments” | R | SUPPORTED | Sentence continues: "attempted to sell the skull as an ancient Mexican artifact". |
| E13 | It was not considered ancient; assumed modern European glass | SAX · Section 3 | “was assumed to be modern glass from Europe” | R | SUPPORTED |  |
| E14 | Batres denounced Boban, who moved to New York to sell his collection | SAX · Section 3 | “Batres then denounced Boban, who hastily moved to New York” | R | SUPPORTED |  |
| E15 | Dec 1886 newspaper: sold at auction to a Mr Ellis of Tiffany's | SAX · Section 3 | “the skull had been sold at auction to a Mr Ellis” | R | SUPPORTED | New York Times, 19 December 1886, per the paper. |
| E16 | Archive note shows Kunz involved in that purchase | SAX · Section 3 | “establishes that Kunz was also involved in the purchase” | R | SUPPORTED |  |
| E17 | Two years later Californian businessman Sisson bought it; bankrupt within ten years | SAX · Section 3 | “Mr Sisson, a Californian businessman, bought the carving” | R | SUPPORTED | "Within 10 years, Sisson was made bankrupt" follows. |
| E18 | Boban also sold three other rock crystal skulls, now at Quai Branly | SAX · Section 2 | “involved in the sale of three other rock” | R | SUPPORTED | "crystal skulls … currently in the Musée du Quai Branly" follows. |
| E19 | Quai Branly holds the other best-known skull | SAX · Introduction | “Quai Branly, Paris, and the present study” | R | SUPPORTED | Preceding sentence: "The two best-known examples of these artefacts are in the collections of the British Museum, London, and the Musée du Quai Branly". |
| E20 | SEM of silicone moulds of tool marks | SAX · Section 2 | “impressions of features of interest were made with silicone moulding material” | R | SUPPORTED |  |
| E21 | Securely dated Mesoamerican goblet and beads show no wheel marks | SAX · Abstract | “show no evidence of lapidary wheels” | R | SUPPORTED | Subject: "A Mixtec rock crystal goblet and a group of Aztec/Mixtec rock crystal beads". |
| E22 | …worked with stone and wood tools charged with abrasives | SAX · Abstract | “worked with stone and wood tools charged with abrasives” | R | SUPPORTED |  |
| E23 | Textual evidence for early colonial Mexican lapidary work supports this | SAX · Abstract | “Textual evidence for Mexican lapidary techniques during the early colonial period” | R | SUPPORTED |  |
| E24 | Both skulls carved with rotary wheels | SAX · Abstract | “the two skulls under consideration were carved with rotary wheels” | R | SUPPORTED |  |
| E25 | BM skull: hard abrasives such as corundum or diamond | SAX · Abstract | “worked with hard abrasives such as corundum or diamond” | R | SUPPORTED |  |
| E26 | Smithsonian skull: carborundum (silicon carbide) traces by XRD | SAX · Abstract | “traces of carborundum (SiC)” | R | SUPPORTED |  |
| E27 | Silicon carbide first synthesised at the end of the nineteenth century | SAX · Section 4.1 | “first synthesized at the end of the nineteenth century” | R | SUPPORTED |  |
| E28 | Bonded wheels (e.g. SiC in ceramic) available since the mid-twentieth century | SAX · Section 4.1 | “Wheels of bonded materials, such as silicon carbide grit in a ceramic matrix” | R | SUPPORTED | Sentence continues "have been available since the mid-twentieth century" (hyphen breaks across a PDF line). |
| E29 | BM quartz formed in mesothermal metamorphic setting (greenschist facies) | SAX · Abstract | “mesothermal metamorphic environment equivalent to greenschist facies” | R | SUPPORTED |  |
| E30 | Suggests quartz from Brazil or Madagascar, far outside pre-Columbian trade | SAX · Abstract | “obtained from Brazil or Madagascar, areas far outside pre-Columbian trade networks” | R | SUPPORTED |  |
| E31 | BM skull rejected as modern in Mexico in 1885 | SAX · Abstract | “rejected as a modern artefact by the Museo Nacional de Mexico in 1885” | R | SUPPORTED |  |
| E32 | Conclusion: BM skull worked in Europe in the nineteenth century | SAX · Abstract | “the British Museum skull was worked in Europe during the nineteenth century” | R | SUPPORTED |  |
| E33 | Smithsonian skull probably made shortly before its 1960 purchase in Mexico City | SAX · Abstract | “probably manufactured shortly before it was bought in Mexico City in 1960” | R | SUPPORTED |  |
| E34 | White quartz blocks available in Mexico and the US | SAX · Abstract | “large blocks of white quartz would have been available from deposits in Mexico” | R | SUPPORTED |  |
| E35 | Smithsonian skull is a larger white quartz skull, donated | SAX · Abstract | “another larger white quartz skull, donated recently to the Smithsonian Institution” | R | SUPPORTED |  |
| E36 | Skulls the subject of popular books, articles, documentaries | SAX · Introduction | “numerous popular books, articles and documentary films” | R | SUPPORTED |  |
| E37 | Skulls offered as genuine pre-Columbian antiquities | SAX · Abstract | “purchased in 1897 as an example of genuine pre-Columbian workmanship” | R | PARAPHRASE-OK | Paper title: "purportedly pre-Columbian". Article says "several have been offered". |
| E38 | Wheel-cut striations and cuts at teeth and mouth fit wheel-cutting | SAX · Fig. 1 caption | “consistent with rotary wheel-cutting” | R | SUPPORTED |  |
| E39 | The paper does not mention the Mitchell-Hedges skull | SAX · Whole paper (absence check) | (absence check: Mitchell appears 0 times) [Mitchell count in extracted text: 0] | X | SUPPORTED | Absence check run on the full extracted text; count shown in the snippet cell. |
| E40 | Label text: "late 19th century AD" | C (File:Crystal Skull at the British Museum.jpg) · Commons description | “Late 19th century AD” | C | SUPPORTED | Description quotes the museum label: "Rock crystal skull. Late 19th century AD. Purchased from Tiffany and Co." |
| E41 | Image: Vassil, CC0 | C (File:Crystal Skull British Museum 26072013 05.jpg) · Commons licence and author fields | “CC0” | C | SUPPORTED |  |

## 3. Wikipedia in piri-reis-map, and JSON-LD

### 3.1 Role of the Wikipedia link in post 1917
The post's Sources list says Wikipedia was “used to locate the references above and for the Topkapı location”. In practice:
- It was read to find Akçura, McIntosh, Dutch, Jolly, the Nature paper and the Commons image. Each of those was then opened directly, and the claims about them are tied to them above.
- The sentence in the Sources list about “the Topkapı location” is inaccurate: the body says the map was *found* in the Topkapı Palace (Akçura, A3–A4); the museum-library credit in the image caption comes from Commons (A46), not Wikipedia. Proposed fix P8.
- **Six claims in the live post rest on Wikipedia alone** and are marked above: A13 (the Bahriye is “later”), A48 (Cantino caption), A50 (“disappears from the record; nobody knows what Selim made of it”), A51 (“Book of the Sea”), A53 (the Columbus map “is lost”), A54 (“missing two-thirds”). A49 (Cantino alt text) is unverified for a different reason: nothing opened describes the image.

### 3.2 Is any Wikipedia-only claim left?
**Yes. In post 1917, 6 rows remain** (A13, A48, A50, A51, A53, A54). Posts 1920, 1922, 1924 and 1926 contain no Wikipedia-sourced claim: B, C, D and E cite none, and the one Wikipedia-derived idea considered during drafting for D and E (Commons description wording) is a Commons field, tagged C. This corrects the earlier statement (in `a-piri-reis-map/evidence.md` and in the hand-off) that Wikipedia-only claims had been removed from the article text.

### 3.3 The two JSON-LD blocks on each post
Each live post carries two blocks: (1) the site's own graph (Person, Article, BreadcrumbList) and (2) the FAQPage we added. Checked by fetching each live URL and parsing the blocks.
- **Site graph:** the Article node holds headline and description copied from our SEO fields, plus author, publisher and dates. The descriptions contain no claim that is not in the body (A: 1513 chart, Columbus, Antarctica; B: green/ruby; C: door experiment, “half missed” = 8 of 15, C30; D: 1784 commission, Franklin; E: 2008 study, two skulls).
- **FAQPage:** 20 answers checked against the visible FAQ and against the body text before the FAQ. Each JSON answer equals the visible answer (differences: A answers 1–2 omit typographic quote marks and a trailing space). Tokens in an answer that do not occur in the body before the FAQ:

| Post | Answer | Token(s) only in the FAQ | Source for it | Verdict |
|---|---|---|---|---|
| A | Did Piri Reis use a map by Columbus? | “Colombo” (the inscription's spelling) | Akçura inscription VI (A20) | SUPPORTED; body says “Columbus” |
| A | Who was Piri Reis? | “Book” (of the Sea) | Wikipedia only | **UNVERIFIED (WIKIPEDIA-ONLY)**, A51 |
| B | Where is the Lycurgus Cup now? | “London” | Freestone et al. title page (“The British Museum, London”) | SUPPORTED; city not in body text |
| D | Who investigated Mesmer's claims in 1784? | “Jean-Sylvain”, “Antoine”, “France” | PDR essay (full names) and the report's title (“King of France”) | SUPPORTED; first names and country not in body text |
| C, E | all other answers | none | — | no extra claims |

No numeric claim appears in a FAQ answer that is not also in the body.

## 4. Proposed corrections (not applied; for approval)
Edits are to the post body unless stated; where a FAQ answer is changed, the JSON-LD answer must be changed with it. Text is shown as stored in the post.

### Post 1917 (piri-reis-map)
- **P1** (rows A13, A50)
  - Before: `The same edition quotes Piri Reis’s later sea-book, the <em>Kitab-ı Bahriye</em>, saying he presented the map to Sultan Selim I in Cairo, where Selim had just conquered Egypt in 1517. After that, the map disappears from the record. Nobody knows what Selim made of it.`
  - After: `The same edition quotes Piri Reis’s sea-book on navigation, the <em>Bahriye</em>, saying he presented the map to Sultan Selim I in Cairo, where Selim had just conquered Egypt in 1517.`
- **P2** (rows A53)
  - Before: `The Columbus map itself has not survived, so the claim can only be tested against the fragment.`
  - After: `We did not find the Columbus map in any source we opened, so the claim can only be tested against the fragment.`
- **P3** (rows A53)
  - Before: `Scholars have argued over which voyage that map reflects, and the map itself is lost, so the question can only be argued from the fragment.`
  - After: `Scholars have argued over which voyage that map reflects, and no copy of it appears in the sources we opened, so the question can only be argued from the fragment.`
- **P4** (rows A53)
  - Before: `If his note is right, information from a Columbus map survives only because he copied it.`
  - After: `If his note is right, information from a Columbus map is preserved in his copy.`
- **P5** (rows A53 (FAQ and JSON-LD))
  - Before: `The Columbus map itself is lost.`
  - After: `We could not find the Columbus map he cites in any source we opened.`
- **P6** (rows A54)
  - Before: `<strong>The missing two-thirds.</strong> The eastern part of the world map is lost, along with whatever it said.`
  - After: `<strong>The rest of the world map.</strong> The surviving piece is part of a larger world map and its eastern marginal notes are torn, so whatever the rest showed is unknown.`
- **P7** (rows A48, A49 (caption and alt text of the second image))
  - Before: caption: `The 1502 Cantino planisphere, a Portuguese chart. Modern scholars use charts of this kind as comparison points for the Portuguese material Piri Reis says he used. Biblioteca Estense, Modena, via Wikimedia Commons. Public domain.` alt: `The 1502 Cantino planisphere, a Portuguese world chart on parchment showing the Atlantic coasts of Europe, Africa and the Americas, with the line dividing the Spanish and Portuguese zones.`
  - After: caption: `The 1502 Cantino planisphere, a Portuguese world chart shown for comparison only. Piri Reis does not name his Portuguese sources. Biblioteca Estense, Modena, via Wikimedia Commons. Public domain.` alt: `The 1502 Cantino planisphere, a Portuguese world chart, Biblioteca Estense, Modena.`
- **P8** (rows A51 and 3.1 (FAQ, JSON-LD, Sources list))
  - Before: `He also wrote the <em>Kitab-ı Bahriye</em> (Book of the Sea).` and, in Sources, `used to locate the references above and for the Topkapı location. A secondary summary, not a primary source.`
  - After: `He also wrote the <em>Kitab-ı Bahriye</em>, a work on navigation.` and `used to locate the references above. A secondary summary, not a primary source.`
- **P9** (rows A37)
  - Before: `David Jolly, reviewing Hapgood’s method in <em>Skeptical Inquirer</em>,` and in Sources `“Was Antarctica Mapped by the Ancients?” <em>Skeptical Inquirer</em>, vol. 11 (issue and date not printed in the extract we could read)`
  - After: `David Jolly, reviewing Hapgood’s method in an article from the Center for Inquiry’s archive,` and `“Was Antarctica Mapped by the Ancients?” (Center for Inquiry archive PDF; journal, issue and date not printed in the extract we could read)`
- **P10** (rows A42 (optional))
  - Before: `Geoscientist Steven Dutch, writing against the claim,`
  - After: `Steven Dutch of the University of Wisconsin–Green Bay, writing against the claim,`

### Post 1920 (lycurgus-cup)
- **P11** (row B35, optional)
  - Before: ` A nanometre is a billionth of a metre.`
  - After: delete the sentence (no source was cited for it; the fact itself is not in dispute).

### Post 1924 (mesmerism)
- **P12** (row D49, optional tightening; verdict was PARAPHRASE-OK from our own draft)
  - Before: `Mesmer’s follower the Marquis de Puységur described a trance state he called artificial somnambulism, and defended animal magnetism in a memoir that same year.`
  - After: `The Marquis de Puységur, a follower of Mesmer, defended animal magnetism in a memoir the same year; the modern English edition of that memoir is titled with the phrase “artificial somnambulism.”`

Posts 1922 (change-blindness) and 1926 (crystal-skulls): no corrections proposed.

## 5. Counts

| Post | Claims checked | SUPPORTED | PARAPHRASE-OK | UNVERIFIED | of which WIKIPEDIA-ONLY | NOT SUPPORTED |
|---|---|---|---|---|---|---|
| A (1917) | 54 | 34 | 12 | 8 | 6 | 0 |
| B (1920) | 38 | 32 | 5 | 1 | 0 | 0 |
| C (1922) | 42 | 36 | 6 | 0 | 0 | 0 |
| D (1924) | 51 | 47 | 4 | 0 | 0 | 0 |
| E (1926) | 41 | 39 | 2 | 0 | 0 | 0 |
| **Total** | **226** | **188** | **29** | **9** | **6** | **0** |

Plus 20 FAQ answers compared with the body and with the visible FAQ (section 3.3): 1 further Wikipedia-only token (“Book of the Sea”, already counted as A51).

## 6. Limits of this QA
- Verdicts test each claim against text that was opened during research. They do not re-read the sources independently of that work, and SUPPORTED for Freestone and Jolly rows relies on the Firecrawl PDF parse (the Freestone letters are cross-checked against a second decode, but digits are not).
- McIntosh and Hapgood are cited through the publisher description and through Jolly; the books were not read.
- The Gutenberg text is a 1785 English translation; no French original was opened.
- Image-content claims (what an image shows) were checked against Commons metadata only, not by viewing every image; rows that depend on that are marked.
