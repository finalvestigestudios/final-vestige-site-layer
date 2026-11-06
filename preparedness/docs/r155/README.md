# Preparedness R155 — Family Reunification source-scope observation (DRAFT / HARD HOLD)

**Parent:** R154 draft PR #1166, exact commit `d0b4a82c739df8d07a14b18cc0f86c61359885cc`. **Owned lane:** Issue #136; conversion coordination #820 / charter #818. Read-only engineering; no WordPress write, no source-register edit, no crosswalk change, no publication, independent-QD approval, affiliate activation, email or paid offer.

## Genuine progress: inspect all eleven Family Reunification Card sources

On **2026-11-05** the eleven original registered URLs from the R149 source-use dossier were individually submitted to a browser retrieval. The separately committed JSON observation docket retains the exact original IDs, URLs and a narrowly framed finding for each; it does **not** set `human_link_check` to true.

| Retrieval observation | Sources | Result |
|---|---:|---|
| Readable, narrow claim supported in retrieved page text | 3 | CDE California school plans; CDC chemical emergency evacuation (hazard-specific); CDC reunification |
| Readable, source-scope/context concerns | 2 | Colorado Office of School Safety; NCMEC CyberTipline |
| HTTP 403 to automated retrieval | 6 | FEMA, FCC, four Ready.gov pages |

**Material source-scope discrepancy:** The currently retrieved [Colorado Office of School Safety reunification index](https://oss.colorado.gov/reunification) has a link to an Adams 14 video and advises waiting for school instructions in its video description. The register attributes *bring photo ID and a pen / limit calls and texts* to that page, but those phrases were not found in the retrieved page text. They may exist in linked media or another source; a reviewer must substantiate them or narrow/remove the attribution. The original citation and source text remain untouched.

**Material context limitation:** The linked [NCMEC CyberTipline page](https://www.missingkids.org/gethelpnow/cybertipline) displays the 24-hour hotline but primarily addresses online child exploitation. A reviewer should select a more context-appropriate reunification source if the page is used for broader emergency reunification advice; do not depict CyberTipline as a general disaster-reunification web form.

**Supported *limited observations*, not human safety approval:** [CDE](https://www.cde.ca.gov/ls/ss/vp/cssp.asp) has explicit reunification recommendations; [CDC chemical evacuation](https://www.cdc.gov/chemical-emergencies/response/evacuation.html) says to avoid going to separated children/loved ones until officials deem it safe **in that specific hazard**; [CDC reunification](https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html) discusses emergency contacts, meeting places and contact cards. The review must distinguish a textual match from whether advice is complete or suitable for a particular family/school.

**Blocked is not broken:** Retrieval returned 403 for `https://www.fema.gov/fact-sheet/reunification-support`, `https://www.fcc.gov/reports-research/guides/tips-communicating-emergency`, `https://www.ready.gov/evacuation`, `https://www.ready.gov/plan`, `https://www.ready.gov/plan-form`, and `https://www.ready.gov/get-tech-ready`. No 404, link-death, source correctness or source-approval conclusion follows. In particular, the privacy/storage promise attributed to the Ready.gov plan form is **not independently verified**, nor are current SMS command instructions from the Ready.gov tech page. Only an authorized qualified reviewer may resolve these.

## Deterministic integration

`preparedness/tools/r155_family_source_observation_gate.py` pins the original R149 docket Git blob `e63aaaa35bcb5c4378f05ae45a07cc8cfc5c070c`, imports the pinned R149 validation source `a2b896e579e66399d6c4253242d577ee9083bda7`, and re-runs the R149 live-body/source-custody comparison in a trusted full checkout. It accounts for the eleven source identities and **sixteen** citation occurrences without changing any source. The CLI requires an exact eleven-row observation set and refuses approvals, replacement URLs, inconsistent findings, missing claims, missing source records, and forged link checks. The CLI exits **2 on both a consistent DRAFT_HARD_HOLD and invalid input** so it cannot be mistaken for an independent QD release pass.

On a trusted disposable repository checkout (do not run against live WordPress):

```bash
python -I preparedness/tools/r155_family_source_observation_gate.py --repo . --report /tmp/fv-r155-family-source-report.json
# expected exit 2: read JSON status, do not interpret exit 2 as source safety approval
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The 65 new isolated synthetic/adversarial Python tests run locally using the matching source and observation JSON. They do not perform independent URL checks and do not establish full-repository pipeline success. The native suite, generated draft WordPress content, mobile/print QA, qualified source review and QD remain unverified. No draft is authorized for publishing.

## Conversion-first contract (one audience, no invented SKU)

**Audience/intent:** households with school-aged children who need emergency contact and reunification planning; only a *proposed* Grok topic, not an authorized content assignment or verified posted asset. **Free source-backed destination (pending QA):** Household Emergency Plan. **Optional practical resource (pending QA):** Family Reunification Card; personal details must remain on-device and printing/download behavior needs privacy/accessibility review. **Optional paid next step:** **HOLD**—no currently purchasable, rights-cleared FV-owned matching Preparedness toolkit and usable Payhip delivery confirmed; do not add paid CTA or label an offer available.

Draft-only CTA (never publicly deploy without approval): **“Make a family contact plan before an emergency. Read the free Household Emergency Plan. After source and privacy review, use the optional printable Family Reunification Card.”** Avoid implying source approval, a final live URL, automatic data storage, third-party privacy or safety guarantees.

Acceptance sequence for Claude/Site QA: Grok/Praxxis TASK-008 supplies an **actual** immutable `asset_id`, published post URL, platform-native allowed link placement and exact proposed destination; verify landing semantic match, page availability, source citations, 360/390/768/1440px accessibility, form-free reading, card privacy/printing, outbound resource behavior, and offer relevance. Revenue events must remain separately reconciled: qualified-human campaign sessions → genuine CTA clicks → confirmed leads (if collected) → settled merchant orders less fees/refunds. Report **net revenue per 1,000 qualified human sessions** only once both numerator and denominator are authenticated; 7/30-day tiny-sample flags are mandatory. No verified media ID, confirmed lead, merchant transaction or net revenue is supplied by this docket.

## Reviewer decision gates

1. Verify Colorado's exact photo-ID/pen/call-limiting source location or narrow the source support record under independent review.
2. Determine whether NCMEC CyberTipline is acceptable as hotline verification and secure a better reunification reference where needed.
3. Manually inspect the six restricted pages; verify any privacy and SMS-command claims independently.
4. Reconcile the eleven source interpretations with the original citation occurrences and the existing 75-task R154 triage; log qualified reviewer name, date, source excerpts and decision **outside** this observational docket.
5. Run full native validation/build/regression and WordPress draft rendering from authenticated checkout, then independent safety review and QD. All 35 article drafts remain HOLD; the existing live `/preparedness/` overview is separate.

**GitHub coordination:** Issue #136 (source/source-scope decisions), #820 (revenue attribution only), independent QA PR #157, fixture isolation PRs #169/#973, homepage PRs #49/#604. No modification to their owned work.
