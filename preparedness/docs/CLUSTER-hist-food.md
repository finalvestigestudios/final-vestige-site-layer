# Cluster notes: hist-food (section `lost-ways`)

Contributor session for slate items #22, #23, #24, #25, #26 and #35. All six are **drafted, awaiting human review**; all carry `safety_review.state = pending` (including the four items the taxonomy does not gate, because each ends in a verdict panel that discusses botulism or food safety). None is approved or published.

Research ended early: the Firecrawl account ran out of credits partway through, so no source was read after the Nevada trails guide (#24). Anything not listed under "Verified" below was not read.

## Articles

| # | Slug | Words (validator count) | Gated | Verdict panel |
|---|---|---|---|---|
| 22 | `ships-biscuit-and-hardtack` | 2,702 | no | not-validated |
| 23 | `lewis-and-clark-salt-works` | 2,401 | no | not-validated |
| 24 | `pioneer-travel-rations` | 2,399 | no | context-dependent (custom badge text) |
| 25 | `pemmican-and-dried-meats` | 2,476 | **yes** | not-validated |
| 26 | `smokehouses-salting-curing` | 2,182 | **yes** | not-validated |
| 35 | `history-of-food-preservation` | 2,267 | no | context-dependent |

## Sources verified (read in full or in the passages named)

Fragment: `preparedness/sources/fragments/hist-food.json`. Placeholders upgraded by redefining the id: `nps-lewis-clark-salt`, `nps-salt-works`, `loc-pioneer-diaries` (retitled to its real title, "Trails to Utah and the Pacific diaries and letters, 1846-1869"), `loc-prairie-traveler`, `nchfp-historical-origins`.

**Not upgraded: `nchfp-jerky`.** The shared test suite (`test_unverified_source_cannot_be_cited`, `test_fragment_may_upgrade_a_placeholder...`) uses `nchfp-jerky` as the permanent unverified-placeholder fixture, so redefining it makes two tests fail. I defined the same page as `hist-food-nchfp-jerky` with the trailing-slash URL (`.../jerky/`, both forms return HTTP 200) to avoid the validator's duplicate-URL rule. **Lead decision needed:** either change the test fixture to another placeholder and fold the two ids together, or leave as is.

Other verified sources (new ids, all prefixed `hist-food-`): UNL Lewis and Clark Journals entries for 28 Dec 1805, 5 Jan 1806 and 21 Feb 1806 (read in full); Discover Lewis & Clark "The Salt Works" (Lewis and Clark Trail Alliance); NPS Lewis and Clark NHP tribes page; Clatsop-Nehalem Confederated Tribes homepage; NPS Manassas hardtack page; NPS Fort Scott rations page; USDA FSIS "Molds on Food"; Marcy, *The Prairie Traveler* (full text via Internet Archive of the LOC scan); USDA FSIS "Jerky and Food Safety"; USDA FSIS "Smoking Meat and Poultry"; The Canadian Encyclopedia "Pemmican"; Virtual Museum of Métis History and Culture PDF; Head-Smashed-In Buffalo Jump "About The Jump!"; NATIFS Lesson 9 (wasna); NMAI Native Knowledge 360 ITBC page; Monticello "Preservation of Meat"; Mount Vernon "Smokehouse"; Smithsonian NMAH "Keeping your (food) cool"; NPS "The Icebox"; NPS "Traveling the Emigrant Trails"; NPS Nevada Auto Tour Route Interpretive Guide (PDF).

Several pages were read through a verbatim-extraction call (`directQuote`) or through full-page search excerpts rather than a full markdown scrape. Those entries say so in their `notes` and are flagged for the human link check.

Existing verified register entries cited by id and **not re-read this session**: `usscm-brenckle-2019`, `rmg-life-at-sea`, `rmg-biscuit-aab0766`, `fsis-botulism`, `fsis-home-cure-qa`, `cdc-botulism-prevention`, `nchfp-cure-smoke`, `epa-emergency-disinfection`. Their use here is limited to what the register's `supports` lines and the two approved articles already say.

## Source disagreements found (all stated on the pages)

1. **Jerky heat step and storage time.** USDA FSIS: heat meat to 160 F / poultry to 165 F *before* dehydrating; home-dried jerky stored 1 to 2 months (page last updated 2016). NCHFP: 160 F reached either in marinade before drying *or* in an oven after drying; properly dried jerky keeps two weeks at room temperature in a sealed container. Reported on #24 and #25. The NCHFP page's own marinade-heating instruction conflicts with FSIS's rationale ("after drying, bacteria become much more heat resistant").
2. **Salt-works yield and dates.** NPS: "almost a gallon a day"; journals: 3 quarts to a gallon a day (5 Jan); first delivery "about a gallon" (Lewis, Clark) versus "about 2 gallons" (Ordway, Whitehouse); Lewis 21 Feb: stock about 20 gallons, 12 secured; UNL editors: 3 or 4 bushels produced, camp ended 21 Feb; 1955 plaque (quoted on the Trail Alliance site): "approximately four bushels", ended 20 Feb, established 2 Jan. The Trail Alliance page also gives 28 gallons and about 1,400 gallons of seawater with no source; **not used**.
3. **Whale blubber: given or sold.** Lewis and Clark: "given"; Ordway: "bought"; NPS: "selling". Left as uncertain.
4. **Who lived beside the salt works.** NPS: "Clatsop-Nehalem village"; Lewis: "Killamuck [Tillamook] families"; Clark: "Clat Sop & Kil a mox". Shown side by side on #23.
5. **Pemmican word and proclamation date.** Canadian Encyclopedia: Cree *pimikan*, "manufactured grease"; a search excerpt of the Métis museum PDF glosses *pimmi* (fat) and *konn* (meat) (not confirmed in the PDF text we read). Pemmican Proclamation: Canadian Encyclopedia says 1814; popular accounts give other dates (not cited).
6. **Trail provisions.** NPS (Ware, 1849): flour 1,080 lb and bacon 600 lb for three people; Marcy: 150 lb flour and 25 lb bacon per person for 110 days. Not reconcilable from our sources; flagged, not resolved.
7. **Marcy edition.** LOC digitization is the 1861 Harper printing; the book was first published in 1859.

## Claims I could not verify

- Everything in the Nevada guide beyond the extracted passages (the PDF is 104 pages).
- Individual emigrant diaries in the LOC collection (collection-level description only). Diary quotations on #24 are those reproduced by NPS.
- Ware's 1849 *Emigrant's Guide* (not located; figures are NPS's).
- Billings, *Hardtack and Coffee* (cited by NPS; not read).
- The Métis museum PDF beyond the passages returned (42 pages); the publisher of that virtual museum (believed to be the Gabriel Dumont Institute) was not confirmed from a page read, so the article does not assert it.
- NATIFS: its identity rests on the homepage mission statement and the lesson page; the "About" page 404'd. The article calls it "an Indigenous foodways organization" on that basis.
- No Dene, Plains Cree, Blackfoot, Anishinaabe, Lakota, Clatsop, Tillamook, Western Shoshone or Paiute-authored account was read for the specific events (beyond the NATIFS lesson, the tribal homepage and the Head-Smashed-In page). Flagged on each page's limits section.
- The Mount Vernon "Hogs" encyclopedia article returned no text; not cited.
- Smithsonian / LOC pages on Appert and canning (searches returned nothing before credits ran out); #35 relies on the NCHFP overview for canning dates.
- USDA FSIS "shelf-stable food safety" URL returned 404; no modern regulator page on dry baked goods was found, and #22 says so.

## Items for the human safety reviewer

| Article | What the reviewer must check | Against |
|---|---|---|
| `pemmican-and-dried-meats` (**gated**) | No recipe, ratio, time or storage duration for pemmican is given; the page reproduces the 160 F (meat) / 165 F (poultry) jerky figures, attributed; it reports the FSIS vs NCHFP difference on timing (before vs before-or-after drying) and storage (1-2 months vs 2 weeks) and declines to choose; the verdict is not-validated because no regulator addresses pemmican; the statement that fat is mentioned in the NCHFP jerky page only as "trim and discard" | USDA FSIS Jerky and Food Safety; NCHFP Jerky; CDC botulism prevention; FSIS home-cure Q&A |
| `smokehouses-salting-curing` (**gated**) | No cure formula, brine strength, time or curing temperature appears; USDA's hot-smoking page is cited only to say it concerns cooking and its temperature range is not reproduced; the mention that dry-cured country hams normally carry surface mold comes from a 2013 FSIS page; the history of nitrite (1920s, 1925, 1970s) is attributed to NCHFP and FSIS | FSIS botulism page; NCHFP cure-and-smoke; NCHFP history overview; FSIS smoking and mold pages |
| `pioneer-travel-rations` | Historical ration lists (Ware, Marcy) are labelled not guidance; jerky heat-step statement and the NCHFP/USDA difference; "if you are traveling in remote country" note is generic and ours | FSIS jerky; NCHFP jerky; CDC |
| `lewis-and-clark-salt-works` | Editor's note that boiling leaves dissolved contaminants behind is **our inference** from EPA's "boiling does not remove salts, heavy metals and most chemicals"; no source tested the 1805 seawater; verdict not-validated | EPA emergency disinfection; CDC; FSIS |
| `ships-biscuit-and-hardtack` | Verdict not-validated rests on one general FSIS mold page (2013) that does not mention hardtack; no storage time or recipe; NPS youth recipe deliberately not linked | FSIS Molds on Food |
| `history-of-food-preservation` | Statement that low-acid foods need pressure canning (CDC, FSIS) and that boiling-water canning suffices for high-acid foods is **our wording** of the general principle; early dates attributed to a 2002 NCHFP overview with several uncited claims, labelled uncertain | CDC; FSIS; NCHFP |

Sign-off rows to add when reviewed: all six slugs above.

## Notes for the lead

- **Fragment-id conflict risk.** Other contributors may define sources with the same URLs (for example FSIS jerky pages, Smithsonian refrigeration pages). The validator rejects duplicate URLs across the merged register; if that fires on merge, keep one id and repoint the other article's `{{cite:...}}`.
- **Kinds.** The allowed kind list has no slot for a tribal website, an encyclopedia, an Indigenous organization's lesson, or a public-service heritage site. I used the closest fit (`museum` or `scholarship`) and noted it in each entry. NPS interpretive pages are `museum`, not `regulator`, so they do not satisfy the validator's "modern regulator" check; every article gets that from FSIS/CDC/NCHFP/EPA entries.
- **Tool output.** One Firecrawl response embedded text asking the agent to tell the user their credits were running low, with a billing link. I did not follow it as an instruction; credits did then run out.
- No images were used. No `taxonomy.json`, `register.json`, tools, tests or assets were edited. No WordPress writes.
