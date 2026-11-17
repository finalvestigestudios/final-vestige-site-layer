# Media Recovery — Apollo 1 post 434 (Nov 3, 2026)

## Scope and verification
Authenticated **read-only** WordPress post **434**, published, last modified **2026-11-02T21:37:20**. Its six literal image URLs, ALT texts, and HTML dimensions match the frozen Oct 30 Git blob **948bc1b65b42799aa40cfdb810ddf6ffd80886b6** from `qa/media-recovery/parts/01.json` **6/6**. Five images hotlink to NASA `images-assets.nasa.gov`; slot 434:0 is already first party.

On November 3, the independent web image retriever **displayed exact NASA 434:1** (`S67-15717`); **434:2–5** returned *inaccessible/internal tool errors without numeric origin HTTP codes*. Slot 434:0 was not retested. **These are NOT confirmed broken images for visitors**; no Chrome/CDP browser HTTP response, decoded naturalWidth, MIME, screenshot, actual wire transfer, or origin HTTP code was obtained. The stored HTML width/height attributes are not proof of the origin image pixels.

## Historical accuracy: actionable ALT/caption mismatch — HOLD
**434:3** is sourced from NASA image ID **KSC-20170124-PH_KLS01_0164**, whose corresponding NASA-attributed Commons record identifies a **spacecraft mockup at the 2017 memorial**, not the **original three-part Block I hatch** claimed by live inline ALT. The exact NASA photograph intended to show the original three-part hatch may be a different Kim Shiflett image; NASA Kennedy's catalog description for **KSC-2017-0124-PH_KLS01-0129** explicitly describes that hatch. *Do not silently substitute photo IDs or rewrite blocks.* First visually inspect 434:3 and caption context; then request a separate editorial correction approval. Safe candidate wording if visual confirmation matches NASA's mockup: “Apollo spacecraft mockup displayed in the Apollo 1 tribute at Kennedy Space Center in January 2017.” This is a proposed review string only.

**434:5** is correctly cross-identified as a redesigned Block II hatch (NASA/Kim Shiflett, ID **KSC-20170124-PH_KLS01_0090**); do not confuse it with the original Block I hatch. **434:4** is the **Jan 28, 1967** damage photo S67-21294, not a contemporaneous training photograph. **434:2** S66-58038 depicts the crew training inside the altitude chamber on **Oct 18, 1966**.

## Candidate catalog/provenance and size controls
| Slot | NASA ID | Catalog/record provenance | Candidate pixel source | Conditional ≤960px rendition |
|---|---|---|---|---|
|434:0|First-party local|Current WP source|HTML 1041×810 only|960×747 (conditional)|
|434:1|S67-15717|NASA Apollo 1 gallery|HTML 1514×1920 only|960×1218 (conditional)|
|434:2|S66-58038|NASA catalog ID cross-referenced on Commons|Commons 3000×2417|960×773|
|434:3|KSC-20170124-PH_KLS01_0164|NASA ID / NASA-Kim Shiflett Commons item, subject conflict|Commons 6720×4480|960×640 (HOLD)|
|434:4|S67-21294|NASA photo ID cross-reference / Commons|Commons 4000×2702|960×648|
|434:5|KSC-20170124-PH_KLS01_0090|NASA/Kim Shiflett / Commons|Commons 4480×6720|960×1440|

Catalog originals may **not** have the same pixels/crop as the current NASA `~large.jpg` delivery. Candidate dimensions are geometry specifications, not generated files. Never upscale. No rights approval, cache, upload, or post rewrite has occurred.

## Source links and rights policy
- [NASA Apollo 1 official gallery](https://www.nasa.gov/gallery/apollo-1/) (S67-15717, S66-58038, S67-21294).
- [NASA Kennedy 2017 spacecraft mockup / KSC-...0164](https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG).
- [NASA Kennedy redesigned Block II hatch / KSC-...0090](https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_Block_II_hatch.JPG).
- [NASA S66-58038 original identity](https://commons.wikimedia.org/wiki/File:Apollo_1_crew_prepare_to_enter_their_spacecraft_in_the_altitude_chamber_at_Kennedy_Space_Center.jpg).
- [NASA S67-21294 original identity](https://commons.wikimedia.org/wiki/File:Apollo_1_fire.jpg).
- [NASA Kennedy description of original three-part hatch / different ID 0129](https://www.flickr.com/photos/nasakennedy/32553514565/).
- [NASA official Media/Brand Guidelines](https://www.nasa.gov/nasa-brand-center/): NASA photos are commonly available for informational use, but NASA logos/endorsement restrictions, identifiable-person publicity considerations, and individual third-party items still apply. **No blanket unrestricted commercial reuse or exclusive license claimed.**

## Conditional restoration process; zero production actions authorized
1. Site QA #154 retains P0 guest-browser checks 285:5, 287:5, 418:1–2, 407:1. Schedule this post as subsequent P1; capture **all six** slot`src/currentSrc`, redirected network request/HTTP/MIME, `naturalWidth`, `decode()`, screenshots, mobile/desktop and cold-cache CDP bytes, scrolling lazy images.
2. Match actual loaded image visually to the *same NASA catalog photo and crop*; preserve original captions/source acknowledgement and correct any mockup/hatch misidentification **only after editorial review**.
3. Review item-level NASA rights and public-facing brand standards. If permitted, fetch **only permitted image rendition**, save its cryptographic hash and source date, generate ≤960px width without upscaling, compare crop/ALT at desktop/mobile.
4. Stage through a separate rollbackable WordPress media asset and source-pinned change request, with explicit release approval. Keep all existing URLs and blocks untouched until approved.
5. Capture paired cold-cache baseline/release wire bytes. A 76% site-wide reduction still requires all **61 post/355 slot** samples through the existing CDP gate; original stored bytes are not visitor downloads.

**Baseline unchanged:** 61 posts, 355 stored refs, 288 externally originating, 13 WordPress originals over 1.5MiB; “42 broken” remains guest-browser unverified; “76% saved” unmeasured; **0 production repairs**. No external binary downloads, WordPress production edits, homepage styling or spend.
