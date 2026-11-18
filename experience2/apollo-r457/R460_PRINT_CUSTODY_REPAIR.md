# R460 | Complete printable NASA source custody after filter — staging-only

## Baseline defect reproduced

On R459, selecting the "Confirmed homepage (1)" filter makes five cards `hidden` in DOM. The old print stylesheet includes `.fv457 [hidden]{display:none!important}`. Switching to print media **still showed only one card**, and none of the six source URLs was visibly printed because they reside behind closed native `<details>`. A seemingly complete classroom research handout could therefore omit five source records.

## Isolated change

- Print media overrides *only the filtered card* `[hidden]` visibility; all six source records always print, without changing screen filter selection or adding JavaScript.
- Each card gains a print-only plain-text NASA source URL, current evidence check, and warning that commercial image-use permission has **not** been established. These are inaccessible duplicates on screen and visible on paper; ordinary interactive `<details>` source links remain unchanged.
- A print notice communicates completeness and the catalogue/ID acceptance HOLD. Screen users see no duplicate citations or print notice.
- CSS SHA-256 pin in PHP updated to `68405e2d0a1c1cae2522cb103ce25b23c7fa801b95ad41d4458b373627bb75cd`; JS remains unchanged. Corrupted stylesheet or script continues falling back to the original free investigation.

## Executed local QA

- PHP 8.4.24 syntax lint: **PASS**.
- Existing source/security tests `python -m unittest discover -s qa -p 'test_contract.py' -q`: **26/26 PASS**.
- Existing baseline Chromium suite `python qa/browser_qa.py`: **21/21 PASS**.
- R459 print/source hold suite `python qa/r459_print_qa.py`: **14/14 PASS**.
- NEW real Chromium regression `python qa/r460_print_custody_qa.py`: **45/45 PASS**. Widths 320/360/390/768/1024/1440/1920 with JS enabled and disabled. A JS filter is applied, then all six record cards, all six printable NASA references, the always-visible rights acceptance HOLD and black-on-white print ink are verified. Switching back to screen restores the original filter. Touch, forced colors, reduced motion and five screenshot widths passed.
- Five local reproducible print screenshots and JSON receipt are generated under `QA/r460/`. Run the QA scripts in the checked-out worktree; do **not** claim this as hosted staging acceptance.

Real Chromium `page.set_content` of PHP-rendered HTML is **not** navigation to WordPress. **HOLD_NOT_RUN**: hosted WordPress, independently checked axe-core, navigated LCP/CLS, manual screen-reader acceptance, field CWV, exact-head CI/QD, source-ID mapping acceptance and commercial NASA media clearance.

## Commercial and release contract

**OFFER:** proposed original Apollo educator dossier (**no verified payable SKU**). **FUNNEL STEP:** verified Grok documentary → NASA Evidence Atlas → source-custody classroom printout → one original free investigation link → *only after separate approval*, a genuine merchant product. **BLOCKER:** R459 printed only the filter-selected subset; publication, commerce, image rights and human attribution remain unverified. **CHANGE/EXPERIMENT:** complete six-record printable provenance and limitations without unrelated commercial CTA. **PASS/FAIL EVIDENCE:** offline browser PASS; hosted, creator publication, merchant and paid conversion HOLD. **OWNERS:** Apollo staging QA; Grok/Praxxis TASK-008 verified publication; Claude approved checkout/attribution; founder and independent QD release.

Revenue KPI: verified net revenue per 1,000 qualified human sessions (7/30-day cohorts); NOT COMPUTABLE absent Grok published `asset_id`, qualified sessions, confirmed paid orders, refunds and fees. An affiliate outbound click or email signup is not paid conversion.

## Governance

Stack only on R459 PR #3027. Never modify homepage PR #49, Research Desk PR #158, Grok/Praxxis queue, production WordPress, checkout, tracking or marketing. No invented Atlas map pins, purchased services, posted content, signup forms or image reuse.
