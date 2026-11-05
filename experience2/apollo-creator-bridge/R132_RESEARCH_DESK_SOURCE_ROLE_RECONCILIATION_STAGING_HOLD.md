# Apollo R132 — Research Desk six-record source-role reconciliation (STAGING HOLD)

**2026-11-04 Pacific · Independent Apollo lane · Scope: source-controlled editorial review only**

## Source custody / exact upstream
- Original Research Desk PR [#158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) at commit `250d7f05a4de037e73826dcf0cfaef0ec4c29383`; original template Git blob `403d128c57b9bc82dac7c619651689070edef86c`. **UNCHANGED.**
- Base Apollo R131 commit `cebfd51726901063c5adbd70c39d2f49ad70ae2e`. Frozen homepage PR #49 and all Claude/Grok branches untouched.
- `r132_research_desk_source_role_review.html` is a review-only derivative of the exact PR #158 six-card template. Blob `c5b4b59c1443f63fc3b4a24da04d8abb8e32b76a`. It is not a WordPress shortcode or a published page.
- `r132_research_desk_source_role_gate.cjs` is a read-only release-custody gate (blob `5c299bde3fbed77bf22e3a2c3c81a55317b71581`) with explicit photo dates, source roles, original URL allowlist, no new merchant CTA, and a `--upstream /path/to/ledger.html` source Git-blob check.
- `test_r132_research_desk_source_role_gate.cjs` is a native-Node test **source file** (blob `849e2019d46a35ba4fa38633bd56fdb2cef0989e`). CI/native Node execution remains outstanding. Tests are run using a V8 Node-compatible module/assert mock with real committed sources; not equivalent to Node/CI or full-page browser QA.

## Six explicit corrections proposed for Research Desk integration
1. **Record 01 — crew:** Catalog number `S67-19766` is an **unverified association** in the linked NASA page, not a proven photo ID; January 1967 day unknown. Photo cannot prove the test cabin conditions.
2. **Record 02 — oxygen:** January 3, 1967 spacecraft photo cannot measure oxygen composition or 16.7 psia. The Apollo 204 Review Board is the technical source.
3. **Record 03 — instrument chronology:** October 18, 1966 rehearsal photo cannot independently establish January 27 sensor timestamps; Review Board is the source.
4. **Record 04 — hatch:** NASA photo `KSC-20170124-PH_KLS01_0164` is a **January 24, 2017 retrospective display** (NASA/Kim Shiflett), not an image of the 1967 test. Board substantiates hatch findings.
5. **Record 05 — ignition:** January 28, 1967 post-fire photo does not uniquely prove a specific ignition initiator; Board reports the specific initiator could not be conclusively established.
6. **Record 06 — redesign:** `KSC-20170124-PH_KLS01_0090` is another **2017 retrospective display**, not an engineering test measurement. Board and NASA institutional sources substantiate redesign history.

The review retains the six original NASA image-detail URLs, historic narrative, native `<details>`, free original-investigation link and progressive search. It adds a visible evidence-type disclaimer plus one visible, dated, rights-qualified source-role disclosure to each card; the disclosure is in unhidden HTML and therefore survives **no-JavaScript**. Each card calls the photographic link **visual context** and calls the Apollo 204 Review Board technical support where that report is provided. No photo binary, inferred map coordinate, new form, tracking script, new checkout or marketing CTA is included.

NASA primary technical authority: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/

NASA media and advertising guidance: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

**Important:** NASA generally allows many factual educational/media uses but places limits on implied commercial endorsement and identifiable-person advertising. Source metadata and official links are *not* individualized commercial-use adjudications. All six photographs remain **INDIVIDUAL_REVIEW_REQUIRED**, and no reuse/endorsement clearance is claimed.

## Exact-source testing and limitations
- Committed candidate audited: **PASS**, 6/6 source roles, 6/6 photo links, 14 allowlisted links, no media/form/script added, rights gate **0/6**, release gate **STAGING_HOLD**.
- **14/14 tests PASS** using V8 with Node-compatible `require`, assert and crypto *mocks* over exact GitHub commit files. Ten mutation failures were also directly observed before writing the test suite; the native test suite includes 14 named cases covering rights, dates, source swaps, unverified checkout insertion, duplicate cards, no-JS and upstream drift. Neither mocked cryptographic verification nor V8 execution is an independent native Node pass.
- Full-page Chromium navigation **BLOCKED** in this execution environment: fresh Playwright probe on 2026-11-04 Pacific returned `ERR_BLOCKED_BY_ADMINISTRATOR` for `data:`, `file:`, and local `http://127.0.0.1` navigations. Real 320/360/390/768/1440/1920 browser matrix, full-page Playwright, axe-core, authentic LCP/CLS, screenshots, PDF, no-JS/browser/zoom/touch/keyboard and real screenreader acceptance are **NOT EXECUTED** on this review HTML.
- Test command on a permitted Node checkout: `node --test experience2/apollo-creator-bridge/test_r132_research_desk_source_role_gate.cjs`. Read-only audit: `node experience2/apollo-creator-bridge/r132_research_desk_source_role_gate.cjs --upstream /path/to/pr158/templates/ledger.html`.
- Deterministic artifact in GitHub is the exact review HTML Git blob plus this source-only gate; no browser screenshots or CI completion are represented as created.

## Integration/release decision
**HOLD.** Editorial owner and Research Desk maintainer should review all six proposed source-role captions against NASA pages, then port approved portions into a *new separately governed* PR or a controlled follow-up to PR #158. No modifications to PR #158, production WordPress, homepage #49, Grok tasks, publishing, merchant settings, or analytics are authorized by R132. Hosted WordPress/Assembler theme/shortcode asset QA and founder approval remain mandatory.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER
|Priority|Offer → step|Blocker|Change/experiment|Evidence|Owner|
|---|---|---|---|---|---|
|P0|Existing FV educator-compatible paid SKU → merchant-confirmed order|No independently verified matching Payhip SKU, rights, price, acceptance, fulfillment, fee/refund record|Read-only merchant inventory/checkout audit; **do not activate purchase CTA**|**BLOCKED / NOT VERIFIED**|Claude/Growth + founder|
|P1|Grok future Apollo long-form → original investigation → free source exercise|Research Desk's photo IDs were visually conflated with technical evidence|Six-card source-role review, source allowlist and independent editorial gate|**BUILT / source-tested**; Grok Apollo asset is not verified published|Apollo + Research Desk reviewer|
|P2|Free exercise → approved relevant paid casefile|No approved casefile/merchant proof|Withhold checkout; retain free primary CTA and technical source proof|**NOT ACTIVATED**|Founder/Claude|
|P3|Verified order → realized net revenue/1000 qualified human sessions|No approved asset_id / observed campaign denominator / merchant-confirmed order linkage|Reuse #820 privacy-safe campaign specification for 7- and 30-day cohorts|**NOT COMPUTABLE**, not 0; tiny-sample warning applies|Claude/Growth|

Commercial success cannot be inferred from pageviews, printed worksheets, outbound clicks or the source audit. Existing business charter #818 and attribution #820 remain authoritative. Grok owns the video script/posting; Praxxis owns creator QA; Apollo owns this isolated in-site evidence reconciliation.
