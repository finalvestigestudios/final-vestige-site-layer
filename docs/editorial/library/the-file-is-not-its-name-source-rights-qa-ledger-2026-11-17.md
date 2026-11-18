# Library release ledger — The File Is Not Its Name (2026-11-17)

**WordPress draft:** #2880; parent Library #77; unpublished; `jetpack_seo_noindex=true`; raw Gutenberg 8,485 characters. Original static WordPress article is committed beside this ledger. Public draft permalink currently returns 404 (expected). Public `/free-resources/` and `/free-resources/research-sources/` independently returned HTTP 200, with unchanged canonical URLs; no production edits.

## Evidence and rights, checked November 17
- [NIST, Secure Hash Standard FIPS 180-4](https://www.nist.gov/publications/secure-hash-standard): authoritative SHA-256 specification; opened and read.
- [NARA, Audio Maximum Capture AUD-P1](https://www.archives.gov/preservation/products/products/aud-p1): preservation checksum and subsequent transfer verification; opened and read.
- [Digital Preservation Coalition, Fixity and checksums](https://www.dpconline.org/handbook/technical-solutions-and-tools/fixity-and-checksums): fixity limitations, multiple copies, manifest retention; opened and read, copyright remains with owner.
- [NDSA, Levels of Digital Preservation](https://www.ndsa.org/publications/levels-of-digital-preservation/): Version 2.1 published March 2026; institutional source available, older /activities/ path redirects.
- [Library of Congress, Data Integrity Management](https://www.loc.gov/programs/digital-collections-management/inventory-and-custody/data-integrity-management/): institutional index supports file-level checksum and audit logging; automated direct read returned 403; ordinary-browser QA required. Link-only.
- [FV Editorial Standards](https://finalvestige.com/editorial-standards/) and [The Library](https://finalvestige.com/free-resources/): live inspected before work.

Original FV explanatory SVG, authored 2026-11-17, included only in standalone HTML review package (not WordPress yet); titled/alt-described and labeled illustrative, not archival. No third-party photo, scan, official logo, audiovisual material or chart was copied. External sources link-only with item-specific rights retained.

## Self-contained offline tool (review release)

Standalone `the_file_is_not_its_name.html`: ~1,924 editorial words, local-only SHA-256 input, known-baseline compare, ten-field printable witness card, .txt receipt export, no network/storage/analytics and a 100 MiB limit. The review package is delivered with the Library Studio run and is **not yet hosted at an FV public URL**.

Offline Chromium layout tests: 320, 390, 768, 1440 px with JS on/off, **8/8** no page horizontal overflow/no JS errors/no network calls; seven labeled inputs. Mocked Crypto.subtle used for functional browser tests (receipt, match/mismatch, unsafe-URL rejection, reset) because browser security policy blocked file:// and localhost navigation. Independent native Node WebCrypto SHA-256 known vector passed. **Do not claim actual secure-origin WebCrypto, WordPress theme or screen-reader acceptance** from this simulation.

## Hard publication HOLD
1. Authenticated production-theme preview screenshots + true WebCrypto on first-party HTTPS; responsive + keyboard + screen reader + print and text-export checks.
2. Validate LoC 403 and all linked source URLs in ordinary-browser conditions.
3. Review mobile 100 MiB memory cap, rights note, accessibility and actual hosted file URL.
4. Enforce `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false` in the **initial** WP publish request. Current connector does not expose these meta fields; default settings alone are not proof.
5. Only then publish draft, insert the smallest Library card/link, and independently check public metadata, links and page rendering.

**No publication, subscriber blast, social post, spend or edits to Preparedness, Investigations, homepage or shared templates.** Grok concept after release only: *“The file is identical. But is the story inside it true?”*
