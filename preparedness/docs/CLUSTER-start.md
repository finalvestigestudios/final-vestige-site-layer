# Cluster notes: `start` (section `start-here`)

Drafted 2026-10-29/30 by the `start` contributor session; revised 2026-10-30 after the independent QD hold on commit 10f58fed. All four articles are **drafted, awaiting human review**. None is approved; all are `status.publish: draft` and `safety_review.state: pending`. Nothing here claims a QD pass.

## Articles

| n | slug | Words (resolved body, approx.) | Sources cited |
|---|---|---|---|
| 1 | `household-emergency-plan` | 3,270 | 14 |
| 2 | `three-day-kit` | 3,430 | 16 |
| 16 | `go-bags` | 3,490 | 18 |
| 20 | `preparedness-real-households` | 3,260 | 17 |

Every article still has several regulator-kind sources (Ready.gov/FEMA, CDC, USFA, HHS ACL, HUD, FEMA) and none relies on a nonprofit to meet the "modern piece needs a regulator/extension source" rule. The validator confirms it.

## Outstanding human verification (important)

**All 27 sources in `sources/fragments/start.json` have `human_link_check: false`.** No human has opened any of these links to confirm they resolve to the page we describe. That remains to do.

**The `start-here` hub (`hub-start-here`) is auto-built from the four articles** by `tools/build.py`. It was not written or reviewed by this session. It must not be published as site navigation until a human has reviewed it.

## How much of each source was actually read

A fetched page is not necessarily a read page. This is the honest account. "Read in full" means the whole returned text was in front of the author and the cited statements were checked against it.

| Source id | Method / date | Read |
|---|---|---|
| `start-ready-plan`, `start-ready-kit`, `start-ready-food`, `start-ready-evacuation`, `start-ready-car`, `start-ready-power`, `start-ready-alerts`, `start-ready-financial`, `start-ready-disability`, `start-ready-older-adults`, `ready-pets` | Firecrawl, `maxAge: 0`, 2026-10-29 | Main page text read in full |
| `start-ready-supply-list` (2-page PDF) | Firecrawl, 2026-10-29 | Read in full; PDF carries no date |
| `start-ready-low-cost` | Firecrawl, 2026-10-29 | Collection page of graphics; English graphic caption read; the page it points to (`ready.gov/low-and-no-cost`) **not fetched** |
| `start-ready-kids` | Firecrawl, 2026-10-29 | Landing page only; sub-pages **not read** |
| `ready-are-you-ready` (FEMA, Sept 2020, 36 pp.) | Firecrawl, 2026-10-29 | **Partly read.** Contents list, introduction, protective actions, financial preparedness, Make a Plan through Prepare Your Critical Documents, Practice Your Disaster Plans (all in full), plus keyword-located passages in the power-outage, flood and renters-insurance sections. Hazard-by-hazard sections otherwise **not read** (roughly 80% of the text was not read line by line). |
| `start-cdc-disability-plan`, `-kit`, `-evacuate`, `start-cdc-family-kit`, `start-cdc-pyh-connected`, `start-cdc-pyh-prescriptions` | Firecrawl, 2026-10-29 | Main page text read in full. Linked activity sheets and PDFs **not read** |
| `start-cdc-infant-checklist` | Firecrawl 2026-10-29; re-read in full 2026-10-30 via web-fetch | Whole page; the two-page PDF version **not read** |
| `start-redcross-older-adults` | Firecrawl, 2026-10-29 | Main text read in full; the linked checklists and booklet **not read**; page shows no date |
| `start-acl-emergency` | Firecrawl, 2026-10-29 | Main text read in full; linked tools (cards, emPOWER, Eldercare Locator, DIAL) **not opened**; page carries a noindex tag |
| `start-hud-multifamily-template` | Firecrawl, 2026-10-29 | **12 of 79 pages** (introduction, disclaimer, table of contents, first sections). Pages 13-79 **not read**. Not used as evidence of any legal duty. |
| `start-fema-housing` | Firecrawl 2026-10-29; re-read 2026-10-30 in the browser pane | Main content in full (about 6,250 characters). The linked Individual Assistance Program and Policy Guide **not read** |
| `start-usfa-high-rise` | Firecrawl 2026-10-29; re-read in full 2026-10-30 by direct download | Whole page text |
| `start-fema-power-sheet` (FEMA V-1008, Dec 2023, 34-page file) | Direct download with curl + `pdftotext`, 2026-10-30 (Firecrawl had no credits) | English pages 1-2 read in full. Pages 3-34 gave no extractable text (probably translations as images) and were **not read** |

Commands used on 2026-10-30 because Firecrawl credits ran out: `curl -sSL` of the PDF and USFA page into a scratch folder; `pdftotext -layout -f 1 -l 3`; the Claude browser pane for fema.gov (curl was blocked with HTTP 403); and a `web-fetch` agent for the CDC infant page (the agent's report was checked against the earlier Firecrawl text).

## Source disagreements (stated on the pages; reviewer please confirm our reconciliation)

| Topic | Sources | Page treatment |
|---|---|---|
| **Refrigerated medicine after an outage (P1-1)** | FEMA 2020 guide: "If the power is out for more than a day, discard any medication that should be refrigerated, unless the drug's label says otherwise." Ready.gov power-outages web page (updated 2026-06-04) repeats a discard instruction. **FEMA's newer December 2023 fact sheet (V-1008):** "Replace refrigerated medications if the power is out for a day or more, unless the drug's label says otherwise. Call your doctor or pharmacist if you depend on refrigerated medications that have been at room temperature. Only use the medicine until you have a new supply." | `three-day-kit` now follows the newer wording, puts the prescriber/pharmacist instruction first, says never to stop, discard or ration a needed medicine on the page's authority, and states the discrepancy between the two FEMA documents. We could not establish which FEMA document is meant to govern. |
| Food above 40°F in an outage | FEMA 2020 guide and Ready.gov food and power pages: two hours or more. FEMA 2023 sheet: refrigerated food above 40°F "for more than 4 hours". | Both stated in `three-day-kit`; reader told to use the shorter time when unsure (editorial). |
| Kit/plan review interval | 2020 FEMA guide, CDC disability-kit, CDC family checklist, Red Cross: every 6 months. Ready.gov Build A Kit (2026): every year. CDC disability plan page: review plan every year. | Disagreement box in #1; noted in #2 and #16. |
| Days of prescription medicine | Ready.gov disability: "several days". CDC disability: at least 1 week. CDC family checklist: at least 2 weeks. Red Cross: at least 30 days. CDC Prescriptions: no number. | Table in #2; no figure chosen. |
| Planning window | FEMA guide "at least 72 hours"; Ready.gov "several days"; CDC water 3 days, goal 2 weeks; FEMA guide water 3, 7 or 14 days; Red Cross: at least 2 weeks. | Table in #1; labeled planning windows, not predictions. |
| Mask type | Ready.gov kit: "dust mask". FEMA guide: fit-tested N95. CDC family checklist: "face mask". | Marked uncertain in #2. |

## QD corrections made on 2026-10-30

* **P1-1** `three-day-kit`: removed the blanket "discard refrigerated medication" instruction; reconciled the 2020 and 2023 FEMA wording as above; added a "ask your prescriber or pharmacist first" box; added interim-use and replacement planning questions.
* **P1-2** `household-emergency-plan`: the "lights-out evening" now reads as a simulated outage using nonessential lights and devices; the refrigerator and freezer, smoke and carbon monoxide alarms, sump pumps, security and all medical or safety-critical equipment stay on; "Do not switch off the main breaker as a drill."
* **P1-3** untouched by us: the lead gated the modern items. `publish` stays `draft`, `safety_review` stays `pending`.
* **P2-5** `start-redcross-older-adults` is now `kind: nonprofit`. No other Red Cross, AHA or AARP entry exists in the fragment.
* **P2-6** `go-bags`: infant acetaminophen carries an explicit caution (no unsupervised dosing; age, weight, label and pediatrician direction); the CDC's six starred items are listed exactly, with the CDC's own wording on ready-to-feed vs powdered formula and cleanability, checked against the live page; the pregnancy items are now context only (emergency birth supplies named as a CDC item, with no instruction, no clinical review, and a pointer to the provider and emergency number). `three-day-kit`: the carbon-monoxide wording now gives the 20-foot figure from both Ready.gov and FEMA's 2023 sheet with an explicit "not a promise of safety / follow the maker's instructions" qualification. `preparedness-real-households`: the USFA shelter-in-place wording is marked fire-only and building-specific, with "call 911 first and follow the dispatcher".
* **P2-7** `preparedness-real-households`: removed the RAD claim and any inference about landlord duties from the HUD template; the page now says plainly that it is unverified, that 12 of 79 pages were read, and that no legal or program requirement is claimed. The FEMA eligibility conditions are dated to the page's own "last updated July 29, 2026" and marked as changeable.
* **P2-8** this file; `source_use` and the fragment's `notes` updated to match.

## Statements we could not verify to the QD standard

* Everything the FEMA 2020 guide is cited for beyond the sections listed as read above (the guide's hazard sections were not used).
* `start-ready-low-cost`: wording comes from graphic captions, not a full web page.
* `start-ready-alerts`: the claim that Ready.gov pages are offered in many languages rests only on the language menu printed on the pages; no page in another language was read.
* `start-acl-emergency`: the description of HHS emPOWER comes from ACL's text, not from the emPOWER site; the Eldercare Locator and Disaster Distress Helpline numbers are as printed on the ACL page and were not independently called or checked.
* The Ready.gov and CDC pages carry their own dates; "reviewed" dates were copied as shown, and the CDC infant page lists a reviewed date earlier than its published date.
* Our comparisons ("Ready.gov's web page has not been updated to match the 2023 sheet") rest on the pages as read on 2026-10-29; the pages may have changed since.
* No source gives a dollar amount for emergency cash, a per-pet water or food quantity, or the cost of a kit; none is stated.
* Landlord legal duties, HUD program rules (including RAD), state emergency-refill laws, whether a renters policy covers flood, immigration-related details of FEMA eligibility beyond FEMA's printed text, local charities and food banks: **not verified**.
* The effectiveness of rehearsing a plan: the agencies recommend it; we found no study cited.
* The 8-pounds-per-gallon figure used in `preparedness-real-households` is carried over from the existing `water-math` article, which gives it as its own arithmetic.
* Editorial statements (labeled "Editor's note") are not source claims and need the reviewer's judgment: the first-hour list, rehearsal ideas, budget staging order, the portable-share go-bag framing, the review-interval reconciliation, the "use the shorter food time" advice, and the questions-to-ask table.

## Items for the human safety reviewer (SAFETY-REVIEW-CHECKLIST section C format)

| Article | What the reviewer must check | Against |
|---|---|---|
| `household-emergency-plan` | First-hour framing is FEMA's two-step opening; the bullet list after it, and the rehearsal ideas, are editorial. Confirm the simulated-outage drill wording is safe as written. Review-interval reconciliation. | FEMA 2020 guide; Ready.gov plan; CDC disability plan |
| `three-day-kit` | Refrigerated-medicine box and the two-FEMA-documents box (quote accuracy, "follow the newer wording" choice). Medicine-days table (no figure chosen). Food-time discrepancy (2 h vs 4 h). 20-foot carbon monoxide wording and qualifications. Wrench/utility line. N95 vs dust mask. | FEMA V-1008 (Dec 2023) pp. 1-2; FEMA 2020 guide; Ready.gov kit, food, power-outages; CDC; Red Cross |
| `go-bags` | Infant acetaminophen caution; the six starred items; formula wording; the pregnancy "context only" box; pet kit contents; disability items by condition. | CDC infant checklist; CDC family checklist; Ready.gov pets, disability, evacuation |
| `preparedness-real-households` | USFA fire-only box and the shelter-in-place sentences as paraphrased; the HUD paragraph (no legal claim, 12 of 79 pages); FEMA eligibility text and the "conditions change" note; heat paragraph for people on medications and with dementia. | USFA high-rise blog; FEMA housing page; Ready.gov disability; HUD Exchange template |

## Validation record (run from the repo root after merging `origin/feature/preparedness-archive-v1` at ee591e2)

| Command | Result |
|---|---|
| `python -I preparedness/tools/validate.py` | 0 errors, 0 warnings |
| `python -I preparedness/tools/build.py` | exit 0 (the generated `preparedness/build/` output is now git-ignored) |
| `python -I -m unittest discover -s preparedness/tests -v` | Ran 36 tests; 36 ok; 0 failures; 0 errors; 0 skipped; exit 0 |

No test, tool, asset or `taxonomy.json` was edited.

## For the lead

1. Firecrawl credits ran out on 2026-10-30; the follow-up checks used curl/pdftotext, the browser pane and a web-fetch agent, as listed above. A second pass with Firecrawl (or a human) would give a cleaner audit trail, especially for `start-fema-power-sheet`.
2. A human link check is needed for all 27 sources (`human_link_check: false`).
3. The auto-built `start-here` hub needs review before it is used for navigation.
4. The two tools named here were built in the second sprint (below).

## Second sprint (2026-11-01): release-candidate work

Branch `claude/start-here-rc`. Full detail: `docs/QD-REVIEW-PACKET-start.md` and `audit/start-here/`.

* **Source audit.** `audit/start-here/verify_sources.py` re-fetched 30 sources and checked anchor phrases for 63 sourced claims (69-row matrix including 6 editorial rows). 61 confirmed; C21b (FEMA 2020 "at least 72 hours") needs a human. `human_link_check` stays `false` for all 29 sources in `start.json`.
* **New source** `start-fsis-emergency-food` (USDA FSIS) to separate the 4-hour (closed refrigerator) and 2-hour (food held above 40 F) conditions. Page-stated date: "Last Updated Jul 30, 2013" (the text may have been revised without the date changing).
* **Wording changes.** Medicine box and the two-FEMA-documents box in `three-day-kit` are neutral and give no instruction about any medicine; the "follow the newer wording" and "use the shorter food time" editorial lines were removed.
* **Built:** Household Emergency Plan Builder (`reunification-plan`), Emergency Kit and Go-Bag Planner (`kit-builder`), editorial hub (`content/hubs/start-here.body.html`).
* **Worked examples** (invented, labeled) added to each article. Not source claims; reviewer please confirm none reads as an instruction.
* **Lead-owned files touched:** `taxonomy.json` (two tool rows gated and retitled) and `tools/build.py` (optional editorial hub hook). See the packet.
* **Results:** validate 0/0; build exit 0; unittest 58 run, 58 ok, 0 skipped; node tool tests pass; browser QA 366 checks, 0 failed (Edge 156 via Playwright). Not covered: axe-core, screen reader, installed WordPress, physical printing.
* **QD status: PENDING.** No pass is claimed.
