# Apollo 1 Evidence Atlas page: image rights and contextual-use decision sheet

**Status: no row is signed. Every photograph is OMITTED from the first release until a named editor signs its row.** The page ships as text and documents (the Review Board report, the NASA history sources, the chronology, the Research Desk) and stands without any image. This is a project editorial decision sheet, not a legal opinion. Prepared 2026-11-03 for page 2017 / PR #798.

**The homepage Apollo sign-off does not clear these images.** The PR #604 sign-off covered three images in a different presentation. Each row below is a separate decision for this page and the specific use described.

**Basis:** NASA Media Usage Guidelines, https://www.nasa.gov/nasa-brand-center/images-and-media/ (retrieved 2026-10-30): generally not subject to copyright in the United States; editorial use with NASA acknowledged as source and without implying endorsement; clearances may be needed where images include NASA logos or NASA employees and are used as cover art or in promotional content; names and likenesses of deceased astronauts may be controlled by their estates for commercial use. **The page's restriction, kept in the visible text: editorial use only; no promotional, product or merchandise use.**

## How a row is signed (mechanical, tested)

Add an entry to `experience-2.0/page-blocks/image-signoffs.json`:

```json
{"nasa_id": "S67-15717", "editor": "<full name>", "date": "<YYYY-MM-DD>", "contextual_use": "<the exact use approved, e.g. 'Plate in chapter 02, labelled Interpretive, with caption and NASA credit'>"}
```

An entry missing the editor, date or use is ignored (tested). Then `python experience-2.0/tools/build_all.py`, re-write the changed blocks to the draft, re-read the block hashes, and send the new head for review. No other code change is needed. A signed image appears as a plate in its chapter, with its caption, credit, provenance, rights row and (for S67-21294) its Documented label; unsigned images stay out of every part of the page, including the Research Desk card and the classification list.

## Decision rows

Defaults: **Decision = OMIT**. "Editor", "Date" and "Approved use" are blank because nobody has signed.

| # | NASA ID | What it is | Intended use on this page | Credit and record | Identity evidence | Points for the editor | Recommendation to the editor | Decision / editor / date / approved use |
|---|---|---|---|---|---|---|---|---|
| 1 | S67-19766 | Portrait of the three crew members in spacesuits near Launch Complex 34, January 1967. The file is a copy hosted on finalvestige.com (1041x810, WebP) | Context plate, chapter 01; label **Interpretive** (it does not depict the fire) | NASA. https://www.nasa.gov/image-detail/apollo-1-crew-honored/ | The NASA record page gives the caption and "Image Credit: NASA". The identifier appears only in the image file name there; the NASA Image API did not return it. The web copy is not NASA's original file | Recognizable deceased astronauts (estate likeness clause applies to commercial use only). Identity and file provenance are weaker than the other five | **Omit** until the editor has matched the ID to NASA's archive and replaced the copy with the NASA original, or accepts the record page as sufficient | OMIT / blank |
| 2 | S67-15717 | Spacecraft 012 hanging from a crane during processing, 3 January 1967, technicians in view | Context plate, chapter 02; **Interpretive**; caption states it is a processing photograph, not the fire | NASA. https://www.nasa.gov/image-detail/amf-s67-15717/ | NASA Image API match, center JSC, record date 1967-01-03 (verified 2026-10-30) | Workers visible but not featured; no NASA logo issue identified in the data | Lowest risk of the six; **include** if the editor agrees | OMIT / blank |
| 3 | S66-58038 | Prime crew entering the altitude chamber, Kennedy Space Center, 18 October 1966 | Context plate, chapter 03; **Interpretive**; caption states it was taken months before the fire | NASA. https://www.nasa.gov/image-detail/amf-s66-58038/ | NASA Image API match, center JSC, record date 1966-10-18 | Recognizable deceased astronauts in a hatch scene next to a chapter about the fire; the caption makes the date explicit. Sensitivity is editorial, not a rights bar | Editor's judgement on placement; **include** only with the dated caption | OMIT / blank |
| 4 | KSC-20170124-PH_KLS01_0129 | 2017 museum display of the three-part Apollo 1 hatch at the Kennedy Space Center tribute | Context plate, chapter 04; **Interpretive**, labelled a later depiction | NASA / Kim Shiflett. https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129 | NASA Image API match; the record is the NASA Image Library page | Photograph of a NASA-run exhibit; the exhibit signage is NASA's. Credit line must keep the photographer | **Include** if the editor agrees; keep "NASA / Kim Shiflett" | OMIT / blank |
| 5 | S67-21294 | Charred interior of Command Module 012 at Pad 34, 28 January 1967; no people shown | Plate, chapter 05; the only **Documented** photograph (shows the aftermath) | NASA. https://www.nasa.gov/image-detail/amf-s67-21294/ | NASA Image API match, center JSC, record date 1967-01-28 | Post-fatality scene; rights basis standard, but the editor should decide on sensitivity and on placing it at reading level without a content note | Editor decides on sensitivity first; rights look standard. If included, keep the caption's "No people are shown" | OMIT / blank |
| 6 | KSC-20170124-PH_KLS01_0090 | 2017 museum display of the redesigned hatch with on-image text | Plate, chapter 06; **Interpretive** | NASA / Kim Shiflett. https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ | NASA Image API match | **Content conflict:** the exhibit text in the photograph gives 5 seconds for the Block II hatch, while the NASA history article used on this page says three seconds. The page text uses the article | **Omit** for the first release, or include only with a caption that names the exhibit's 5-second figure as exhibit text and not as the page's claim | OMIT / blank |

## What the page does without them

- Chapters render as full-width text with the Research Desk link; the plate, caption and per-image labels are gone, not hidden.
- The rights section states "This release shows no photographs", lists the six NASA photographs as "Photographs not shown in this release" (ID, factual caption, link to NASA's record), and keeps the rights basis and the editorial-use restriction.
- The classification list drops the photographs; the Board report (Documented) and the chronology (Interpretive) remain.
- No claim depended on an image: every claim row cites a NASA text source (see the record).
