# Preparedness re-review: evidence for the two HOLDs (2026-11-02)

Responds to the independent custody review on PR #584 (comment 6593638055): food PASS, health PASS, hist-food conditional, hist-home HOLD (exact 1798 text not checked), hist-field HOLD (Hastings route wording). **No publication, safety clearance or `may_publish` change is claimed here.** Read-only source checks plus one corrective branch; every item needs the reviewer's own exact-commit check.

## hist-field: the Hastings wording was wrong, and is corrected on a new branch

**What the primary text says** (Internet Archive OCR of the 1845 Cincinnati edition, `GR_1815_djvu.txt`, printed pp. 137-139; OCR is noisy):

- Emigrants "up to this time ... have traveled together, as far as Fort Hall, because of this being the only settlement, in that vicinity, at which they are enabled to procure horses, and provisions."
- "The soda springs, however, will, undoubtedly, be found to be the point, at which the routes will most advantageously diverge ..."
- "The entire distance **by this route**, from Independence, either to Oregon or California, is about twenty-one hundred miles; and the usual time required in performing the journey, to either of those countries, will be found to be about one hundred and twenty days, exclusive of delays ..."

So the 2,100 miles and 120 days are for "this route" in a passage that names the Soda Springs, not Fort Hall, as the point where the Oregon and California routes should part. The article and the `hist-field-ia-hastings-guide` source record said "**by the Fort Hall route**": a misattribution, not OCR noise. Confirmed independently of the reviewer.

**Correction:** branch `fix/preparedness-hist-field-hastings-route-20261102`, commit `5c807fbf455b31f2aac3dfd48b598e096329c236`, one commit on top of the reviewed live head `4e5caf812727953aa45e3bda2d382f2c67b6a09c`. Exactly two files change (3 lines): `pioneer-supply-chains-failed.body.html` and `sources/fragments/hist-field.json`. The new wording uses the guide's own phrase, adds only what the passage states (together as far as Fort Hall; Soda Springs named as the divergence point), and does **not** repeat the OCR's garbled "two hundred miles east of Fort Hall". The source record's `notes` records the correction. CRLF preserved; JSON valid; 36 tests pass; `validate.py` 0 errors, 0 warnings on this lineage. Already in the article and unchanged: the May-12-plus-120-days comparison is labelled "Our arithmetic, not the guide's" with "We do not know that this party relied on that figure"; the Marcy and finding-aid limits are stated. Needs another exact-commit review before hist-field is cleared.

## hist-home: the exact 1798 printing was checked

**Edition identity.** The cited record `https://d.lib.msu.edu/fa/1` is the 1798 printing: "First edition, second printing", Hartford, "Printed for SIMEON BUTLER, NORTHHAMPTON. 1798", 48 pp; the repository's bibliographer's note (Jan Longone) says it "follows word for word the text of the first printing" with some errata corrected. **Caution on the reviewer's corroboration:** Project Gutenberg #12815 is the **1796** Hartford printing (title page: Hudson & Goodwin, 1796), so it corroborates the 1796 text only; it is not proof of the 1798 printing, and the Longone note is a bibliographer's statement, not a collation.

**Access.** The repository's full text is public at `https://d.lib.msu.edu/fa/1/FULL_TEXT/download` (78,092 characters; SHA-256 of the cleaned text I read `87823965c50cfd907daafa2df9bb93ca175edc8c1c718d2ada3a5e5f5da0dff9`). It loaded for plain HTTP requests; the reviewer's environment returned an access-limited page for the item page. The author's own source record states it used the same download.

**Claim by claim** (excerpts from the 1798 text; the article's claims are in `pickling-fermentation-old-recipes` and `root-cellars-cool-storage`):

| Article says | 1798 text | Result |
|---|---|---|
| Potatoes dug before the autumn rains, dried, "kept from frost and dampness", moved from cellar to a dry loft in spring, spread thin and stirred | "All potatoes should be dug before the rainy seasons in the fall, well dryed in the sun, kept from frost and dampness during the winter, in the spring removed from the cellar to a dry loft, and spread thin, and frequently stirred and dryed, or they will grow and be thereby injured for cookery." | supported |
| May-packed butter in the coldest part of the cellar or the ice-house | "...procure it pac'k down in May ... set the pots in the coldest part of your cellar, or in the ice-house." | supported |
| Preserved fruit in a cool, dry cellar | "...then set them in a cool dry cellar." | supported |
| Parsnips kept almost anywhere avoiding heat and frost; richer left in the ground over winter and dug in April, not lasting long after | "they may be kept any where and any how, so that they do not grow with heat, or are nipped with frost ... richer flavored when plowed out of the ground in April, having stood out during the winter, though they will not last long after" | supported |
| Parsley grown in a cask and taken into the cellar for winter (source record) | "...(by slinging a rope around the cask) into the cellar; where, during the winter, I clip with my scissars the fresh parsley" | supported |
| Pickling directions for cucumbers, melons made into "mangoes", barberries, in brine or vinegar; brine strength judged by an egg test | "To pickle or make Mangoes of Melons ... a brine strong enough to bear an egg"; "To pickle Barberries. Take of white wine vinegar and water ..."; "To pickle Cucumbers ... salt and water, strong enough to bear an egg" | supported |
| Green peas kept "until Christmas" in fat-sealed bottles, **no heating step** | "To keep Green Peas till Christmas ... fill them, cover them with mutton suet fat ... cork them, tie a bladder and a leather over them and set them in a dry cool place." No heating is described. | supported |
| A neighbouring direction heats sealed bottles in water | "...put a kettle of water on the fire, and put in the bottles with care ... make a gentle fire till they are a little codled" | supported |
| Brass and bell-metal vessels in cooking and preserving directions; no warning about metal vessels; the words "poison", "verdigris", "copper", "lead" do not occur | brass 1 (a pudding: "strong cloth, brass or bell metal vessel, stone or earthen pot"); bell-metal 3 (that pudding and "a bell-metal kettle or sauce pan" for preserving quinces); pewter 1; poison 0, verdigris 0, copper 0, lead 0 | supported. **Precision note:** the text does say a pot "be clean, well tinned, and free from sand, or grease" (in the vegetable-cooking section). That is a vessel-care instruction, not a hazard warning, but it is worth one clause in the article so "no warning about metal vessels" is not read as "no mention of vessels". Brass appears once and with stone or earthen alternatives. |

**Not covered:** the Wellcome Chadwick record (the reviewer checked it: supports only the narrow catalogue facts); any claim about the book's other pages (the text was searched by keyword and the cited sections read; it was not read cover to cover, as the source record itself says); and, as always, no safety review. The reviewer asked that a person confirm the passages in the printing itself; the text above is the repository's full-text transcription, not a page image, so a transcription error would not show here.

## Still open on the preparedness release

1. Another exact-commit review of `5c807fbf45...` (hist-field) and of the Simmons evidence above (hist-home).
2. hist-food: declare the three `nchfp-jerky` variants (and the third `fsis-power-failure` variant, "shelter") as origin-scoped readings in `sources/crosswalk.json` through the owning workstream's custody process; do not add strings or guess hashes or counters.
3. Re-pin the R14 manifest for the cleared clusters at their exact reviewed diffs (food `f911ff7a65...`, health `d5ef5bafd6...`), then re-run the full integrated fail-closed preflight at the exact new head.
4. A qualified safety review; none exists. Nothing is approved for publication.
