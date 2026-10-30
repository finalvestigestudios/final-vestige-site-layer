# Cluster notes: `start` (section `start-here`)

Drafted 2026-10-29/30 by the `start` contributor session. All four articles are **drafted, awaiting human review**. None is approved; all are `status.publish: draft` and `safety_review.state: pending`. None is marked `gate: true` in the taxonomy, but they carry medical-adjacent and safety-critical lines (medicine quantities, infant feeding, CO/generator distances, shelter-in-place, pregnancy kit), so they were written and flagged as if gated.

## Articles

| n | slug | Words (resolved body) | Sources cited |
|---|---|---|---|
| 1 | `household-emergency-plan` | ~3,200 | 14 |
| 2 | `three-day-kit` | ~2,900 | 15 |
| 16 | `go-bags` | ~3,200 | 18 |
| 20 | `preparedness-real-households` | ~3,000 | 17 |

## What was verified (fetched live, `maxAge: 0`, on 2026-10-29)

All 26 entries in `sources/fragments/start.json`. `ready-are-you-ready` upgrades the register placeholder. Pages were read through Firecrawl; PDFs were parsed to text. Per-source `supports` and `notes` in the fragment say exactly what was and was not read. Highlights:

* Ready.gov: plan, kit, supply-list PDF, food, evacuation, car, power outages, alerts, financial, people with disabilities (canonical URL `/people-disabilities`), older adults (canonical `/older-adults`), Ready Kids (landing page only), low-and-no-cost graphics collection. `ready-pets` re-read to confirm; cited by id, not redefined.
* FEMA "Are You Ready?" (P-2064, **September 2020**): full text fetched; only the sections cited were read.
* CDC: disability plan/kit/evacuation pages, pregnancy-infants-children kit checklist, infant and young-child emergency list, Prepare Your Health "Stay Connected" and "Prescriptions".
* American Red Cross older-adults page; HHS ACL emergency preparedness page; HUD Exchange multifamily template (first 12 of 79 pages); FEMA housing assistance; USFA high-rise blog.

## Source disagreements (stated on the pages; reviewer please confirm our reconciliation)

| Topic | Sources | Page treatment |
|---|---|---|
| Kit/plan review interval | 2020 FEMA guide, CDC disability-kit, CDC family checklist, Red Cross: every **6 months**. Ready.gov Build A Kit (2026): "every year". CDC disability plan page: review plan every year. | Disagreement box in #1; noted in #2 and #3. Our reconciliation (check contents every 6 months, review the plan yearly) is labeled editorial. |
| Days of prescription medicine | Ready.gov disability: "several days". CDC disability: ≥1 week. CDC family checklist: ≥2 weeks. Red Cross older adults: ≥30 days. CDC Prescriptions: no number. | Table in #2; marked uncertain; no figure chosen. |
| Planning window | FEMA guide "at least 72 hours"; Ready.gov "several days"; CDC water 3 days, goal 2 weeks; FEMA guide water 3, 7 or 14 days by location; Red Cross: stay home ≥2 weeks. | Table in #1; stated as planning windows, not predictions. |
| Mask type | Ready.gov kit: "dust mask". FEMA guide: fit-tested N95s. CDC checklist: "face mask". | Marked uncertain in #2; user told to ask local emergency management. |
| Refrigerated medicine in a long outage | Ready.gov power page: talk to provider about how long a medicine can stay warm; also "discard refrigerated medication if power is out more than a day unless the label says otherwise". | Both quoted in #2; flagged for the reviewer below. |

## Could NOT verify / deliberately not stated

* **No official go-bag list or weight limit** exists in the sources read. Ready.gov's evacuation page points to the kit list. The go-bag content is the kit list plus CDC/Ready.gov items by group; the "portable share" framing is editorial. HUD's "Your Go Bag Checklist" resident handout (in the TOC of the template) was **not read**.
* No source gives a dollar figure for emergency cash, a per-pet food or water quantity, or the cost of a kit. Pages say so.
* No dedicated federal page for **renters** was found; HUD's template is owner-facing. Landlord legal duties, state/local programs, charities, food banks, early-refill rules by state, and whether a renters policy covers flooding were not verified.
* The effectiveness of rehearsing a plan: agencies recommend it; the pages read cite no study. #1 says so.
* The **Ready Kids** sub-pages, the **Take Control in 1, 2, 3** PDF, the Ready.gov caregivers guide, the ACL Medical Information Card, the CDC family checklist PDFs and the "low-and-no-cost" target page were not read.
* Hazard-specific guidance (earthquake, flood, wildfire, hurricane, active shooter) in the FEMA guide was not read or used.
* The Red Cross older-adults page shows no publication date.
* The USFA high-rise item is a 2022 blog post for fire educators. NFPA's page on elevators in fire evacuation was seen only as a search excerpt and **not used**.

## Items for the human safety reviewer (same format as SAFETY-REVIEW-CHECKLIST section C)

| Article | What the reviewer must check | Against |
|---|---|---|
| `household-emergency-plan` | First-hour framing (assess, then stay or change location) is FEMA's; the "first hour" bullet list and the rehearsal ideas are editorial. The "lights-out evening" idea carries a caution for anyone on powered medical equipment: confirm that wording is acceptable. Review-interval reconciliation. | FEMA guide pp. "Basic Protective Actions", "Practice Your Disaster Plans"; Ready.gov plan; CDC disability plan |
| `three-day-kit` | Medicine-days table (we chose no figure). Ready.gov power-page medicine line (discard refrigerated medication after a day unless the label says otherwise) reproduced as published, with a "ask in advance" caveat. Outdoor-only cooking and 20-foot generator/stove/grill distance reproduced from Ready.gov. Wrench/utility line: we limited it to FEMA's "if damaged and told to do so, learn how beforehand". N95 vs dust mask. Budget staging order is editorial. | Ready.gov kit, food, power-outages; FEMA guide; CDC family and disability kits; Red Cross |
| `go-bags` | Infant list and the starred "do not use if you cannot clean" items reproduced from the CDC. Formula guidance (ready-to-feed; bottled or boiled water as last resort). Pregnancy list mentions CDC's emergency birth supplies: reproduced as a pointer to a clinician, **not reviewed clinically**. Pet kit contents. Disability items by condition. | CDC infant checklist; CDC family checklist; Ready.gov pets, disability, evacuation |
| `preparedness-real-households` | USFA shelter-in-place wording (wet towel, stair landing) reproduced with its limits. FEMA eligibility conditions reproduced as published; the page makes no claims about immigration status beyond FEMA's text. Heat paragraph for people on medications and with dementia. Statement that HUD template is owner-facing and only partly read. | USFA high-rise; FEMA housing; Ready.gov disability; HUD template |

## For the lead (tools/tests, not edited by this session)

1. **A test pins the populated sections.** `tests/test_preparedness.py:124` (`test_landing_lists_only_built_articles_and_no_empty_sections`) asserts `populated_sections == ["water", "lost-ways", "field-tools"]`. With these four articles, `start-here` is populated and that test fails. This is the intended outcome of this sprint, but the pin needs updating by whoever owns the tests, and every parallel cluster adds a section the same way. Validator and build pass cleanly; this is the only failing test.
2. **Source `kind` taxonomy.** There is no kind for a non-governmental authority such as the American Red Cross. We used `regulator` as the nearest label and said so in the entry's `notes`. A `nonprofit` kind may be worth adding if the label is ever rendered.
3. **Section hub for `start-here`** is not drafted by this session. The hub should present the first-hour / 72-hours / two-weeks progression (the section blurb already says so); the four articles link to each other and to the existing water guides.
4. **Tools worth building** (not started): a one-page printable household plan / wallet card generator (the `reunification-plan` tool) and a kit-and-go-bag checklist that keeps data on-device.
5. **Related links.** `related` lists only built articles will render; the unbuilt slate items were deliberately not linked from the body.
