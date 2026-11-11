# Final Vestige Library — The Word Under the Ink
**Research / provenance / release ledger. Checked 2026-11-11. Status: editorial RELEASE CANDIDATE — NOT PUBLISHED.**

## Editorial gap and reader outcome
This original, free illustrated resource answers a specific problem: a manuscript word, name or abbreviation is ambiguous, and a researcher needs a reproducible method to prevent a plausible interpretation becoming an invented exact quotation. It treats *glyph evidence*, transcribed words, competing readings and historical interpretation as separate records. Distinct from published *The Quote That Crossed a Language* (translation), *The Paper Witness* (object material), and draft #1836 *The Name That Did Not Match* (catalog authority/identity).

## Completed self-contained release, not hosted in GitHub or WordPress
- `The_Word_Under_the_Ink.html`: ~3,100 textual words; original accessible 4-stage vector evidence ladder; 7-step workflow; institutional convention comparison; one explicitly **fictional typeset excerpt**, not a historical document; browser-local 14-field Uncertain Word Witness, native JSON export and print. No external assets or telemetry.
- `Uncertain_Word_Witness_Field_Card.pdf`: 3-page illustrated print method/worksheet/sources; 11 clickable institution+FV links; 3 pages rendered and visually inspected.
- `Provenance_Rights_and_Access.csv`: 11 source/rights/coordination records (8 institutional + 3 FV/internal), with item-level qualifications and last-check state.
- Local `build.py`, `qa.py`, 8 standalone Chromium screenshots at 320/390/768/1440 with and without JS, SHA256 manifest, README, and release ZIP. Artifacts are in the originating Studio conversation sandbox, **not deployed on the website, and not hosted in this repository**.
- Final standalone HTML SHA-256: `d859e7b58f023ce78d1ac8401c139e013515eec17ff8b96c4db99fab39eadac6`.
- PDF SHA-256: `372ceb513aab79266e2337b8515af7d1cc037dfcd302e7bc617feeb5520c772b`.
- Complete ZIP SHA-256: `21d2ef7197d7c992e1f46f936dd08fa1b9bab0f5198b533ab3a9adfda8783998` (ZIP CRC PASS).

## Source and rights ledger — accessed 2026-11-11
| ID | Institution, official URL | Relevant evidence / caveat |
|---|---|---|
| S01 | [NARA Transcription Tips](https://www.archives.gov/citizen-archivist/transcribe/tips) | Preserve literal spelling; compare scribal letterforms; mark `[illegible]`. Direct HTML. |
| S02 | [NARA Get Started](https://www.archives.gov/citizen-archivist/get-started-transcribing) | Catalog OCR imperfect; account to contribute; direct HTML. |
| S03 | [NARA Contribution Policy](https://www.archives.gov/citizen-archivist/resources/tagging-policy) | NARA review date 2026-08-05, public contributions and IP/privacy terms; direct HTML. |
| S04 | [Smithsonian How to Transcribe](https://transcription.si.edu/instructions/transcribe) | Distinct `[[?]]` / `[[candidate?]]` and special project rules; direct HTML. |
| S05 | [Smithsonian Historic Handwriting](https://transcription.si.edu/instructions/specialized/handwriting) | Comparison with same hand; abbreviations; linked real manuscript example; original images **not copied**. Direct HTML. |
| S06 | [Library of Congress By the People](https://ask.loc.gov/crowd/faq/401448) | Volunteer transcription/review improves accessibility. Direct HTML. |
| S07 | [UK National Archives Palaeography](https://www.nationalarchives.gov.uk/education/resources/palaeography/) | Indexed institutional guide states 1500–1800 English source coverage, but its archived interactive portions no longer work; direct open returned 403. **Ordinary-browser recheck before relying on details.** |
| S08 | [NARA Copyright and Permissions](https://www.archives.gov/research/still-pictures/permissions) | U.S. government public domain ≠ all items held by NARA; third-party rights possible; direct HTML. |

No institutional photos/scans/seals/figures have been rehosted or reproduced. All artwork, example text, original programming and worksheet are Final Vestige Studios 2026. Linked objects' actual rights and access remain institution/item-specific. No claims of first-hand viewing individual physical manuscript leaves.

## Local QA and defect corrected
Chromium `page.set_content` render on exact standalone HTML at **320 / 390 / 768 / 1440px**, JS on and off: **8/8 PASS**, no horizontal document overflow or page JS errors. 14 form fields labeled; source anchors are HTTPS, no external scripts, iframes or images; figure SVG has title/description and comparison table is keyboard focusable. Native browser Blob JSON download, saved payload content and reset passed; malicious-looking HTML-shaped strings remained inert data. **QA discovered and fixed a reset bug** caused by the button id `reset` shadowing `form.reset`; changed to `HTMLFormElement.prototype.reset.call(form)`. The local PDF rendered three pages without observed collision; all 11 link annotations present. These results **do not** demonstrate WordPress production theme, anonymous page access or third-party source link health.

## Release HOLD — cannot yet publish
1. Obtain actual WordPress **current-theme** screenshots/keyboard/print checks at 320/390/768/1440 with inspectable pixels. Site screenshot service currently returns mshots URLs but no inspectable bytes; standalone screenshots are not a substitute.
2. Confirm S07 and the internal /free-resources/the-quote-that-crossed-a-language/ source in an ordinary browser; the latter returned automated HTTP 429 but is in the public Library index.
3. First-publish safeguards `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false` must be enforceable in the actual publishing request. The WordPress connector does not expose those meta keys; site default email OFF is not sufficient proof.
4. Only after clearance, create scoped Library child page under #77, validate public URL/SEO/canonical/crosslinks and download media hosting, then make one guarded Library card addition. Do not touch public Research Sources #1338 or staging #2354 (priority #1788), homepage, Preparedness, Investigations or Grok accounts.

**Possible Grok clip after public release only:** “One name in the letter. Two possible readings. Can the ink decide?” Use FV original illustrative diagram; no simulated archival image presented as genuine. No social activity, subscriber emails or spending in this run.
