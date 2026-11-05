# R151 — Three-way contributor drift admission, actual 35-article candidate (DRAFT / HARD HOLD)

**Issue:** #136; conversion coordination #820; business charter #818. **Frozen R150 parent:** \`2826612f9caf327dff3ef00b242e4e67a3491200\`. **Date:** 2026-11-05. No original article, metadata, crosswalk, source, safety/route state, live website, WordPress/CMS, navigation, analytics, checkout, merchant, affiliate, email or social change. No source review or independent QD granted.

## Correction of an important prior interpretation

R150 correctly found that **five of seven Claude branch references have drifted** from the source crosswalk (two match, four ahead, one divergent). But moving refs alone do **not** mean all revised article bodies are absent from the frozen candidate. R151 independently fetched **each exact article body three ways**: crosswalk-pinned contributor SHA, current contributor SHA, **and actual R150 candidate SHA**, rather than comparing only moving branches. This uncovered:

| Current contributor article | R150 candidate versus current contributor | Pinned → current source/reading change | Decision |
| --- | --- | --- | --- |
| Pemmican and Dried Meats | Candidate equals **pinned** original | 7 cite tokens changed from \`hist-food-nchfp-jerky\` to \`nchfp-jerky\` in upstream; 46 citations total and reading depth unchanged | **HOLD** source identity and food safety adjudication |
| Pioneer Travel Rations | Candidate equals **pinned** original | 1 identical source-ID substitution; 39 total citations | **HOLD** source identity adjudication |
| Pickling and Fermentation | Candidate equals **current contributor byte for byte** | +365 words and +7 citations since pin | Already contained in candidate; human review still HOLD |
| Root Cellars | Candidate equals current contributor after **CRLF→LF only** | +369 words and +5 citations | Already contained semantically; no overwrite |
| Sanitation Before Germ Theory | Candidate equals current contributor after **CRLF→LF only** | +37 words and +1 citation | Already contained semantically; no overwrite |
| Navigation Before GPS | Candidate equals current contributor after **CRLF→LF only** | 0 word or citation change; other source/markup changes may exist relative to pinned | Already contained semantically; no overwrite |
| Pioneer Supply Chains Failed | Candidate equals current contributor after **CRLF→LF only** | +369 words and +6 citations | Already contained semantically; no overwrite |

**Important distinction:** 5/7 article body revisions are already in the frozen 35-article candidate (one exact, four different only in newline bytes). The remaining **2/7** have a total of **eight citation-ID substitutions**, currently preserved at the frozen IDs. No article substitutions were automatically applied. This corrects the overbroad R150 statement that *none* of seven later article-body revisions had been incorporated. Do not confuse inclusion with qualified review, actual build success or publication safety.

Actual Git file identity / word and citation measurements are immutably specified in \`contributor-three-way.json\` for 21 authentic blobs (7 × three versions) and seven exact contributor branch refs. For identical bodies, the corresponding blob SHA repeats as expected.

## New deterministic fail-closed gate

\`preparedness/tools/r151_branch_admission.py\` checks, in a complete **trusted local Git checkout**:

1. Exact R150 candidate SHA, original crosswalk blob identity and seven frozen contributor pins; each checked remote-tracking branch must equal the manifest head (detects moving branches).
2. Exactly **35 body and metadata pairs** at the frozen candidate and every metadata \`publish=draft\` plus unapproved human safety state.
3. For all seven historical bodies, Git blob hashes for pinned/current/candidate and exact citation count / reading-depth word count. Malformed or hidden source-ID substitutions cannot be disguised by simply preserving total citation count.
4. Exactly one expected upstream byte-identical, four upstream newline-only, and two pinned-original citation-substitution cases. Only CRLF→LF is normalized, **not** HTML, whitespace, source URLs, author-specific readings, or citation sequences.
5. Any drift, missing full checkout/ref, unapproved state or malformed citation fails closed. Even successful structural custody ends with exit **2** / **DRAFT_HARD_HOLD**, NEVER a release pass.

**Built and locally TESTED:** \`python -I -m unittest discover -s preparedness/tests -p 'test_r151_branch_admission.py' -v\` — **81/81 isolated synthetic and adversarial tests PASS**; Python compilation passes. The committed Python/test/blob files were compared with actual locally tested Git object IDs. Actual GitHub triple-source bytes and hashes were independently read via authenticated connector, but **the Python gate was NOT executed against a complete authenticated repository checkout**. Browser/WordPress and native release tests cannot be marked passed.

**Mandatory on a trusted complete checkout** (not executable in the isolated local runtime because GitHub DNS resolves neither Git fetch nor authenticated repository checkout):

\`\`\`sh
python -I preparedness/tools/r151_branch_admission.py --repo . --manifest preparedness/docs/r151/contributor-three-way.json
# Expected exit 2, deliberate hold after evidence report (or INVALID_HOLD if mismatch)
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

Do not silently turn the hard-hold exit code into a CI PASS. R133–R150 prior integrity/source-use gates, 32 shared-source URL groups, missing CDC outage source, high-rise fire citation shifts, medication warning discrepancy and independent QD must also be adjudicated. Independent QA PR #157 and test-fixture PRs #169/#973 remain separate; no automatic merges. Homepage leads PRs #49/#604 remain other agents' territory.

## Optional creator-to-reader draft, no advertising / live activation

**One high-intent audience:** parents/caregivers arranging out-of-area emergency contacts and school pickup/reunification. **Existing free guide:** Household Emergency Plan. **Optional free practical card:** Family Reunification Card (11 source relationships presently unresolved; privacy/print/mobile QA pending). All essential steps remain free, without login, gating or fear claims. **No authenticated FV-owned, rights-cleared, actually purchasable Preparedness SKU has been supplied; do not invent a paid CTA.** Retired water guide stays retired. Existing Focus Fieldbook CTA/email system is separate.

**Unpublished draft contextual CTA:** “Make a household contact plan you can practice. Read the free Household Emergency Plan, then review the optional Family Reunification Card after its source and print checks are complete.”

**Required Grok/Praxxis handoff:** TASK-008 (Drive) must supply one verified social \`asset_id\`, published platform post, exact approved destination, allowed clickable location and UTM values. Neither TASK-008 nor the dated handoff currently provides a verified Preparedness-specific ID. Do not post, modify Grok's content queue, or imply traffic attribution.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Real Preparedness paid pack → confirmed order | Rights-cleared existing buyable SKU, price, merchant terms, checkout/delivery/refunds not verified | Read-only inventory and secure merchant test by commerce owner, then founder approval | **HOLD; no authenticated product or paid sale** | Commerce / Claude / founder |
| Free Household Emergency Plan → reader | Source/medical/safety/QD signoff & native build incomplete | Complete qualified source review and native 35-article validation | **DRAFT; 78 isolated tests do not pass release** | Preparedness / independent QA |
| Guide → optional Family Reunification Card | 11 unresolved source IDs, mobile 360/390, offline/print, privacy and link delivery not tested | Review author-specific source scope, stage device/print/download acceptance checks | **NOT VERIFIED; no public CTA** | Preparedness / Site QA |
| Grok asset → campaign landing | Missing published Preparedness \`asset_id\`/approved URL | Reconcile TASK-008 with Praxxis; no content/posting takeover | **UNOBSERVABLE** | Grok / Praxxis |
| Qualified sessions → CTA → confirmed lead → paid order → refunds/fees → realized net | No paid offer, source-confirmed transactions or qualified-human denominator | Use existing #820 privacy-safe attribution contract and 7/30-day cohorts; avoid duplicate analytics scripts | **Net revenue/1,000 qualified sessions NOT COMPUTABLE** | Claude / Growth / Commerce |

**Acceptance before any actual CTA deployment:** verify the exact Grok asset and matched landing intent; accessible no-gate guide; author-reviewed citations and official source URLs preserved in HTML/print; one correct approved CTA destination; mobile keyboard and touch, 200/400% zoom, privacy-safe card storage, printable/offline legibility; authenticated sellable SKU with rights/pricing/checkout/delivery/refund disclosures if and only if approved; independently verified paid orders rather than outbound clicks. No manufactured scarcity, efficacy or survival claims.

**Release verdict:** **DRAFT / HARD HOLD**, no merge, CMS, homepage, navigation, merchant, analytics, email, affiliate, social or public publishing changes. Human expert source/safety and independent QD remain **NOT APPROVED**.
