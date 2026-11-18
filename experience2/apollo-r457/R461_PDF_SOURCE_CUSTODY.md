# Apollo R461 — actionable PDF source custody (STAGING / HARD HOLD)

**Issues:** #150 (Apollo Experience 2.0), #820 (qualified traffic → paid conversion), #818 (rights-cleared educator offer).  
**Strict parent:** R460 PR #3031 at \`8c1cecba978176fcc2fc12fba7dc589ca04f0bcb\`.  
**Isolation:** only \`experience2/apollo-r457/\`. Never modify frozen homepage PR #49, Research Desk PR #158, Claude's production/analytics lane or Grok/Praxxis TASK-008.

## Reproduced defect
R460 fixed disappearing cards when printing after a screen filter, but its six printable NASA URLs were **plain text**, not hyperlinks. A real Chrome tagged PDF generated after filtering to "Confirmed homepage (1)" included **zero clickable NASA URL annotations** and only one clickable link to the free FV investigation. This blocks a classroom reader of an electronic PDF from using the printed source trail.

## Implemented code
- Every print-only citation is now an actual HTTPS \`<a href>\` to the already-indexed NASA source URL; no other domains or geospatial inferences are introduced. The existing source acceptance HOLD and individual image-use limitations remain.
- Removed \`aria-hidden=true\` from printable citations; their CSS \`display:none\` prevents duplicate content on screen, while print/PDF receives visible link semantics. No JavaScript required for source custody.
- Added black-underlined, breakable print hyperlinks. Updated CSS SHA-256 integrity pin; fail-open fallback to the unchanged full free Apollo investigation is preserved for corrupted assets.
- Kept one relevant free investigation CTA, no paid CTA, no new signup or analytics. No NASA photos, identifiers, astronaut likenesses or merchandise-rights assertions.

## Verified local QA (2026-11-18)
- PHP lint: PASS.
- \`qa/test_contract.py\`: **26/26** source/security assertions PASS.
- \`qa/browser_qa.py\`: **21/21** offline Chromium checks PASS.
- \`qa/r459_print_qa.py\`: **14/14** print/custody checks PASS.
- \`qa/r460_print_custody_qa.py\`: **45/45** filtered-print regressions PASS.
- NEW \`qa/r461_pdf_link_custody_qa.py\`: **43/43** real Chromium/Playwright checks PASS, widths 320/360/390/768/1024/1440/1920 with JS on/off, filtered screen → complete tagged PDF, restored screen state, touch, reduced motion and forced colors.
- Verified with PyMuPDF, not a DOM link count: each exported PDF has **7 unique clickable URLs** — 6 original NASA references (some generate two annotation rectangles when wrapping) and exactly 1 FV free-investigation link. All six source-text records and provenance/rights warnings remain present. PDFs generated with \`tagged=True\` and normalized fixed metadata; output hashes plus five screenshot hashes reproduce across two runs. Tagged PDF does **not** mean independent screen-reader certification.

## Source and rights custody
- NASA Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — electrical arc most probable initiator, *no single ignition source conclusively identified*.
- NASA 2017 memorial: https://www.nasa.gov/history/apollo-1-crew-honored-in-new-tribute-exhibit/ — retrospective display, not a photograph of the 1967 fire.
- NASA brand / promotional-use rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no NASA endorsement or blanket merchandise clearance. The catalogue link for KSC-20170124-PH_KLS01_0129 and archive-ID attribution for S67-19766 remain unverified, visibly labeled **SOURCE HOLD**.
- No invented Atlas pins or edges.

## Acceptance boundary and conversion-first plan
| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EVIDENCE | OWNER |
| --- | --- | --- | --- |
| Original Apollo classroom dossier → verified paid order | No rights-cleared, merchant-authenticated payable SKU/checkout/fulfillment | No paid CTA or claim; HARD HOLD | Founder / Claude |
| Verified Grok Apollo video → qualified-human landing | No confirmed published \`asset_id\`, allowed destination, human attribution | Maintain controlled destination specification only; UNKNOWN | Grok / Praxxis TASK-008 |
| NASA Atlas → exportable source sheet → free Apollo investigation | R460 PDF lost actionable source links | R461 tagged PDF with 6 genuine NASA links + 1 free CTA; LOCAL PASS / HOSTED HOLD | Apollo / QD |
| Paid confirmed orders → realized net revenue per 1,000 qualified human sessions | No verified orders, merchant fees/refunds, 7/30-day cohort denominator | NOT COMPUTABLE; affiliate clicks and leads never counted as sales | Claude / Commerce |

Hypothesis: a trustworthy, useful classroom source export increases qualified educator progression to the free investigation and, *only after separate commercial approval*, an original educator kit. No confirmed Grok campaign, lead, attributed checkout, affiliate sale, paid order or net-revenue effect is claimed.

**Not run:** approved WordPress staging navigation; genuine axe-core; navigated LCP/CLS; manual screen-reader acceptance; field CWV; exact-head CI/QD. Navigation even to an intercepted fixture was blocked by \`ERR_BLOCKED_BY_ADMINISTRATOR\`, and the trusted axe-core bundle was unavailable in this sandbox. These are explicit HOLD conditions, not passing metrics.

**Governance:** no merge, deployment, WP write, social publishing, analytics installation, merchant/affiliate change, emails, paid services or spending. Founder release approval required.
