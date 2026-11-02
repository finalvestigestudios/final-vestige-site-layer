# Cluster notes: `hist-home` (section `lost-ways`)

Five history articles drafted 2026-10-29/30: #27 `root-cellars-cool-storage`, #28 `pickling-fermentation-old-recipes` (gated), #29 `rain-barrels-and-cisterns` (gated), #30 `water-purification-through-history` (gated), #33 `sanitation-before-germ-theory`. All are `draft`; the three gated ones carry `safety_review.state = pending`. #27 and #33 are not gated in the taxonomy and carry `not-required`, with a note asking for a human read anyway because they contain food-safety and hygiene statements.

Sources are in `preparedness/sources/fragments/hist-home.json` (27 entries, one is the `nchfp-home` placeholder upgrade). Verification method: Firecrawl scrape (maxAge 0) read by the drafting agent; several long pages and PDFs were read through a targeted extraction ("query" format), which returns only the passages asked for. Where that was the case it is stated in the entry's `notes`.

## What was verified (per article)

| Article | Words | Sources cited | Verified this session |
|---|---|---|---|
| root-cellars-cool-storage | ~2,460 | 7 | MU Extension MP562 (full page), NPS Oxon Hill root cellar, Monticello ice house (extraction), USDA FSIS refrigeration (extraction), NPS WWII canning (extraction), NPS Fort Union water (extraction) |
| pickling-fermentation-old-recipes | ~2,430 | 9 | NCHFP home and pickling page (full), LoC catalogue record for Simmons 1796 (extraction), CDC botulism about and home-canned pages (extraction), NPS WWII canning |
| rain-barrels-and-cisterns | ~2,670 | 7 | CDC cistern page (full), CDC rainwater page (full), EPA rain barrels (full), Monticello cisterns, NPS Fort Union, NPS San Juan (extractions) |
| water-purification-through-history | ~2,960 | 14 | Tulchinsky/PMC (extraction), Wellcome Snow map record (full), Snow digitized text (fragments), AIM25 Chelsea Waterworks (full), Oregon slow-sand slides (extraction), Savours/Arctic PDF (extraction), Ayu paper (extraction), CDC chlorine page (extraction) |
| sanitation-before-germ-theory | ~2,660 | 9 | Smith, Medical History 2018 (extraction of opening sections), Chadwick review/Cureus (extraction), CDC handwashing (extraction) |

## Source disagreements and tensions found

1. **Tulchinsky on the pump handle.** The abstract says removal of the handle "led to cessation" of the epidemic; the body of the same chapter says the epidemic was "already declining". The article reports both and does not choose.
2. **EPA rain-barrel page** carries a disclaimer that it is no longer being updated, yet shows a 2026-10-20 modified date. It does not itself say "do not drink"; the drinking caution comes from CDC.
3. **CDC cistern page dates:** published 2024-09-06, updated 2024-04-01, reviewed 2024-08-20 (update precedes publish). Same pattern as other CDC pages in the register.
4. **Jefferson's cisterns:** the Monticello entry says only two reliably held water; Jefferson's own letters say he called them "useless" in 1818. Consistent, but the sand well he planned has no recorded outcome in the text read.
5. **Fort Union cisterns:** the NPS page says they stored water for fire. It does not say whether the water was drunk. The article leaves that open.

## Claims we could NOT verify (and therefore do not make)

* That Hippocrates designed a cloth strainer ("Hippocratic sleeve"), that the Sushruta Samhita prescribes boiling, sand or charcoal filtering, or any Egyptian filtration practice. Only the flower method is reported, by one Ayurveda paper that says no study exists. The only sources surfaced for the rest were web pages of poor quality or Wikipedia, which the brief does not allow.
* The NCBI Bookshelf "Historical Note" in *Drinking Water and Health* (NBK234165): the scraper could not load it (anti-bot block). A retry with a stealth proxy option was declined by the session's safety classifier, and we did not try to work around it. Not cited.
* Wellcome Collection records for Chadwick's 1842 report (works/vgy8svyj) and Blane's *Observations on the Diseases of Seamen* (works/unn6mqpb): HTTP 429 when fetched. Not cited. A later pass could add them.
* The text of the pickling or preserving sections of Simmons's *American Cookery* (1796). Only the Library of Congress catalogue record was read; the extraction of the archive.org full text returned nothing. The article says so and makes no claim about the book's contents.
* Jersey City 1908 as the first US chlorination site: only the CDC statement that US utilities first used chlorine in 1908 is used.
* What period the "thirty four to forty gallons" in the Phipps expedition account refers to. The figure is not repeated in the article.
* The edition and imprint of the digitized Snow book (Internet Archive item b28985266). The article calls it "a digitized copy".
* Any measured data on the water quality of historical cisterns, or on losses in root cellars. None found.

## Items for the human safety reviewer

Same format as `SAFETY-REVIEW-CHECKLIST.md` section C. All three gated articles are `pending`; none is approved.

| Article | What the reviewer must check | Against |
|---|---|---|
| `water-purification-through-history` (gated) | Verdict badge is `context-dependent` with a per-method breakdown (boiling and disinfection validated per CDC/EPA; straining as preparation only; homemade sand/charcoal and plant methods not validated; utility filtration and chlorination validated as regulated systems). **Badge decision: `context-dependent` kept, as chosen in chat on 2026-10-30 (not a safety approval; the human review is still pending).** Check that the page gives no filter design, layers, quantities or doses (Jefferson's sand well is described only in his own short phrases; no dimensions) and that it does not contradict `making-water-safer` or `homemade-water-filters`. Check the Oregon Health Authority training-slide figures (2-4 log removal) are acceptable to cite; they are conditional on proper operation and are from an operator-training deck, not guidance | CDC water-safe and hiking pages, NPS, EPA, Ready.gov; Oregon slides; CDC chlorine page |
| `rain-barrels-and-cisterns` (gated) | Verdict `not-validated` ("do not treat collected rainwater as drinking water"). Confirm the statements are only CDC's, with no dose or table reproduced: the CDC cistern disinfection table is deliberately not reprinted. Confirm the "non-potable restoration" wording about San Juan matches the NPS release. Confirm we may say the EPA page does not itself say "do not drink" | CDC rainwater page, CDC cistern page, EPA rain barrels, NPS San Juan |
| `pickling-fermentation-old-recipes` (gated) | Verdict `not-validated` for old recipes; the page reproduces **no** ratios, acidity values, salt amounts, times or temperatures (the CDC boil-before-eating times for home-preserved foods are deliberately not reproduced). Check wording of the NCHFP rules (tested proportions, uniform acid, do not cut salt in ferments) and the "salt measured by the spoon" editor's inference; check the FSIS wording about traditionally prepared fish (no people named, no generalization). Check the statement "it is a USDA-supported program" and that the NCHFP page cited is the pickling page only | NCHFP pickling page, CDC botulism about and home-canned pages, CDC botulism prevention, FSIS botulism and home-cure Q&A |
| `root-cellars-cool-storage` (not gated) | The temperature and humidity table is reproduced from University of Missouri Extension MP562 as published, for six crop groups. The editor's note that a cellar is not a refrigerator is ours, not either agency's. Ice-house material notes enslaved labor as Monticello does | MU Extension MP562, FSIS refrigeration page, Monticello, NPS |
| `sanitation-before-germ-theory` (not gated) | CDC handwashing steps and the 60% alcohol sanitizer statement; verdict `context-dependent`; the table row calling fumigation "not validated" is our statement (no source evaluates it) | CDC clean-hands page; Smith 2018 |

## Cross-links and shared files

* Cross-linked from this cluster (all existing built guides): `making-water-safer`, `homemade-water-filters`, `water-advisories-explained`, `two-week-water-storage`, `water-math`, `salt-beef-salt-pork-age-of-sail`. The five articles also link to each other.
* No contradiction with the built water guides was intended. In particular `water-purification-through-history` repeats none of their instructions and states that a homemade sand/charcoal filter is not a way to make unknown water safe.
* **Suggested revision-queue item (not edited, per brief):** none required. `making-water-safer` already says it is not describing homemade filters; the new history guide links to it.

## Requests for the lead

* No new component was needed.
* NPS and Monticello interpretive pages are classed `museum`; NPS history articles are not a listed kind. If the lead prefers a separate kind for heritage-site interpretation, five register entries would change.
* `hist-home-oregon-slow-sand` is an operator-training slide deck (state regulator). If the lead judges it too weak for a gated article, the single paragraph that cites it can be rewritten using only the AIM25 archive record.
* No build outputs are committed (hubs, landing and the build report are shared files); the lead's rebuild after merging will pick up these five.

## Self-audit after the first QD review (2026-10-30)

Merged `origin/feature/preparedness-archive-v1` (head ee591e2, merge commit bca18a8; no conflicts). Re-read the brief's "QD lessons". Audited the five articles against the defect classes (a) to (e). Targeted edits only; `status.publish` stays `draft`; `safety_review.state` stays `pending` on #28, #29, #30 and `not-required` on #27, #33. **No article is claimed as QD PASS or approved.**

Commands run from the repo root, with actual results:

| Command | Result |
|---|---|
| `python -I preparedness/tools/validate.py` | 0 errors, 0 warnings |
| `python -I preparedness/tools/build.py` | exit code 0 (build outputs are now git-ignored and not committed) |
| `python -I -m unittest discover -s preparedness/tests -v` | Ran 36 tests, OK; 0 failures, 0 errors, 0 skipped |

**Found and fixed:**
* (e) `water-purification-through-history`: said disinfection came "a few decades" after nineteenth-century filtering; the sources give 1829 (Chelsea filter beds) and 1908 (first US chlorination), roughly eight decades. Reworded. Also softened "the foundation under every modern water rule" (not supported by what we read), "sand filtration did work, and the proof is..." (the sources show modern utility-scale performance, not historical effect), and an unsourced remark that distillation "was valuable in 1773" (now an editor's note saying the sources do not discuss it).
* (c) `water-purification-through-history`: the Phipps distilling quotation was attributed to "the report"; the text we read does not say whose account Savours quotes, so it now says so. The claim that Doctor Irving was "the surgeon Charles Irving" came from a search snippet, not a page we read; reduced to "Doctor Irving". The 1852 Metropolis Water Act requirement (filtering within five miles of St Paul's) rests on one state training deck only; now tagged uncertain with a note that we did not read the Act.
* (c) `water-purification-through-history` and `sanitation-before-germ-theory`: the Wellcome record describes pages 97-120 of the *Cholera Inquiry Committee's* 1855 report to the St James vestry, attributing the map to Snow. We had written "Snow's report" and attributed the report's whole scope to him. Corrected in both.
* (e) `sanitation-before-germ-theory`: "Snow demonstrated, by counting, that water mattered more than air" and "numbers that would undo" miasma were stronger than our sources; reworded to what the cited scholarship says (contaminated water as the key source of the epidemics he studied) and "challenged". The ledger row now says Snow's data linked those cases to contaminated water.
* (b) Source kinds: the four journal articles (`hist-home-ayu-water`, `hist-home-savours-phipps`, `hist-home-smith-naval-hygiene`, `hist-home-chadwick-cureus`) are now `journal` (were `scholarship`). The Tulchinsky book chapter stays `scholarship`. NPS and Monticello interpretive pages remain `museum` (public agency and a house museum, neither a regulator); Monticello is run by a nonprofit foundation, so the lead may prefer `nonprofit` for those three entries, which would not change any article's validation (history pieces still have the Wellcome archive record and RMG museum source in #33; #27 and #30 keep other museum/archive entries) but would need a check on #27 and #29, which rely on Monticello and NPS for their museum-kind source.
* (d) Every fragment entry's `notes` now ends with an exact "Reading depth:" line: FULL (page read whole as markdown) or PARTIAL (read through a targeted extraction; what was and was not seen). Examples: the Snow digitized text was only fragments of the first part; the Smith 2018 article was read to roughly the first 9,000 characters of a 58,000-character extraction; the Oregon deck was 77 slides read through an extraction.

**Checked, no change needed:** (a) no article gives a filter design, layers, dimensions, dose, brine, ratio, acidity value, curing figure or time; the one set of numbers reproduced is the University of Missouri Extension storage chart for produce, labelled as published. #30 states that homemade sand/charcoal filters are not a way to make unknown water safe and links to the built guides; #29 states that rainwater needs testing and treatment before drinking and reproduces no CDC dose table; #28 reproduces no CDC boil times.

**Statements we could not verify to the QD standard (all stated on the pages as unverified, uncertain or not examined):**
* Anything in Simmons's 1796 book about pickling (catalogue record only).
* That Jefferson's sand-filter well was ever built (the Foundation's quoted letter says he had not done it "as yet").
* What period Savours' "thirty four to forty gallons" refers to (figure not used).
* The 1852 Act's five-mile filtering rule, which rests on one state training deck.
* The Chadwick review's claim that sanitary reform reduced cholera and typhoid (one narrative review; tagged uncertain).
* Whether Fort Union's cisterns held drinking water (the page is silent).
* The truth of the 1898 belief that San Juan's cistern water had been poisoned (the release reports only the belief).
* The Wellcome Collection records for Chadwick's report and Blane's *Observations* (HTTP 429; not cited) and the NCBI Bookshelf historical note (blocked; not cited).

**All 27 sources in `hist-home.json` remain `human_link_check: false`.** No page has had a human click-through.

## Update 2026-11-01

* The Wellcome Collection record for Chadwick's 1842 report (works/vgy8svyj) loaded on an ordinary retry (the earlier HTTP 429 was a rate limit). It is now source `hist-home-wellcome-chadwick-1842` (`primary-digitized`, catalogue record only; the 546-image report was not read) and is cited once in `sanitation-before-germ-theory`. The Blane *Observations* record (works/unn6mqpb) was not retried and remains uncited. The source count is now 28; all remain `human_link_check: false`.
* Decision recorded: NPS and Monticello pages stay `museum` (chosen in chat, 2026-11-01).

## Update 2026-11-01 (Simmons text read)

* **The Simmons book text was read, with limits.** The Library of Congress page has no book text and the Internet Archive facsimile is a restricted lending item. The openly readable text is Michigan State University Libraries' Feeding America transcription of the **1798 printing** (Hartford, printed for Simeon Butler, Northampton), not the 1796 edition the Library catalogues. It is recorded as source `hist-home-msu-simmons-1798` (`primary-digitized`; source count now 29). It was fetched by a plain HTTP request for the repository's published full-text file (about 82,000 characters) after a Firecrawl extraction returned only a summary, then searched by keyword and read in the pickle, preserve, cellar and pea passages. It was not read cover to cover. No claim is made that the 1796 printing reads the same.
* **What it added to `pickling-fermentation-old-recipes`:** pickle directions (cucumbers, melons made into "mangoes", barberries) judge brine strength by a household test and give no reason or acidity check; one direction keeps green peas, a low-acid vegetable, in fat-sealed bottles with no heating step described, which contradicts the CDC's statement that pressure canning is the only recommended home method for low-acid foods. The page describes this only as far as needed to say it is unsafe and gives none of its details. Brass and bell-metal vessels appear in cooking and preserving directions with no warning in the transcription; no source we read evaluates that, so the page draws no conclusion.
* **What it added to `root-cellars-cool-storage`:** the 1798 text tells the cook to keep potatoes from frost and dampness through the winter in the cellar, to set butter in the coldest part of the cellar or the ice-house, and says parsnips may be left in the ground over winter. The page notes a difference of emphasis with the Extension chart (dampness versus 80 to 90 percent relative humidity) without reconciling it.
* The words "poison", "verdigris", "copper" and "lead" do not occur in the transcription searched (OCR or transcription errors could hide a word).
* For the reviewer: the pea paragraph in `pickling-fermentation-old-recipes` should be checked to confirm it does not read as instructions.
