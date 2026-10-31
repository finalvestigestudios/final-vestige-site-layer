# R19 — Audit evidence and release blockers (31 October 2026 PDT)

## What was actually read
- Authenticated WordPress.com **READ ONLY**: finalvestige.com has 61 published posts, 79 published pages. Enumerated all 61 published investigation **titles** to check editorial duplication. Puységur published page ID 1377 and existing Focus Fieldbook published page ID 1579 were inspected for source framing, headings and existing Jetpack form; no writes.
- Issue #171 body and recent comments, existing art #150 and Dispatch #174 directives read first. Baseline main at 77a87635eb613ce6de268aee11350fa8242efa0f. PR #49, hub #172, all live routes protected.
- Original Faraday historical text: https://en.wikisource.org/wiki/Experimental_Researches_in_Chemistry_and_Physics/Table-turning ; 1976 pendulum: https://doi.org/10.1080/00221309.1976.9710871 ; 2011 history: https://doi.org/10.1080/00029157.2011.10401754 ; 2022 failed pendulum replication: https://doi.org/10.1080/00029157.2021.2010641 ; Ouija eye tracking (2018 online): https://link.springer.com/article/10.1007/s11097-018-9585-8 ; hypnosis brain meta-analysis: https://pubmed.ncbi.nlm.nih.gov/28238944/ .
- Official merchant seller pages inspected Oct 31: https://inspire3.com/ , **exact** Total Focus https://hypnosislive.com/mental-skills/total-focus , Zen12 https://zen12.com/about and checkout https://zen12.com/getstarted . No approved affiliate creative/swipe library was authenticated or accessed. Listing snapshot does **not** establish purchasing terms/rights for our account. Price/payout never asserted.
- FTC: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance ; NCCIH https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety ; EEG review https://pubmed.ncbi.nlm.nih.gov/37205669/ .

## Source readback audit actually executed, not an assertion of hosted CI
All **10 pre-evidence source files** fetched back using authenticated GitHub `fetch_file` on exact isolated branch at commit `770a41658c6783a66ae55c12c33a439e0e7ae10a`. Executed committed exported `audit(files,matrix)` and `mutations(files,matrix)` in a fresh isolated V8 JS evaluation against fetched **exact text**:
- **122/122 PASS** source contracts, including **8/8 computed WCAG text contrast ratios at least 4.5:1**, disabled controls, one H1 per HTML draft, no merchant product links, no script/iframe/pixel/form/email tracking, no autoplay, identical written A/B source with only review-only B media slot, title/source consistency, no false user experience and all evidence-matrix provenance.
- **22/22 deliberate adverse mutations caught**: live merchant link, removed disclosure, script and pixel, email form, autoplay, unhidden video, dropped captions, broken poster, fake onclick checkout, duplicate ID, duplicated Jetpack class, invented price, changed B copy, removed Focus, forged partner approval, claimed product use, enabled tracking, fabricated earning URL, lost matrix claims, corrupted citation and VTT removal.
- Before final correction, honest iterative runs gave **118/122** (four over-strict wording matchers) and **122/122 with 21/22 mutations** (test did not detect a broken image poster because the other poster reference remained). QA source contract fixed; rerun **122/122 and 22/22**. No claim that product efficacy was 'tested' by these checks.

### Exact audited GitHub blob SHAs
- INVESTIGATION.html: `7d107a5893195458e4ef0385c4785deba2270c10`
- TOTAL_FOCUS_BUYER_GUIDE.md: `7385d5cbd03afdda101ef01441f844a2e6fd739a`
- PILOT_A.html: `60ea86c5f4112f8a135fdc16107359ee70aac8fd`
- PILOT_B_STAGING.html: `ed3427e0a1b15ae5fd57e427947e903000f248c6`
- ZEN12_R19_POSTER.svg: `a411f718b286e00d750f19caf0732cf248e1d1e9`
- ZEN12_R19_CAPTIONS_DRAFT.vtt: `224db9642b17da9902c0e36ffd30f6971beaaff4`
- EXPERIMENT_AND_RELEASE.md: `d00ab0f5d6dd1eb74b291ab1ce33de6f4811cf1b`
- README.md: `abe2d5bef72525d1be80fe0877b654ef3bdbfb14`
- EVIDENCE_MATRIX.json: `334a1398063bbd91246576b9a0c0f571a2f620af`
- qa.cjs: `ea54944ef8f602c34121b0dbce8b5d94975cda1e`

## Reproduce with Node (not executed here)
`node mind/ideomotor-r19/qa.cjs --mutation`

Runtime's container Node exists, but no GitHub DNS, authenticated checkout or local repository working copy was available; therefore **full Node checkout execution was NOT run**. V8 source audit was executed directly on the GitHub readbacks. Exact tree comparison via native GitHub compare: 10 pre-evidence files **added**, no existing file changed/deleted, zero behind the main base. PR #302 draft. Hosted GitHub combined statuses: **0**; associated PR workflow runs returned **0**, neither a green pass nor evidence of successful CI.

## Content and QA caveats
- WordPress Gutenberg staging, live browser layout, keyboard/screen-reader/mobile, Lighthouse/CWV and media decoding/performance **NOT RUN**.
- B film source intentionally `REVIEW_ONLY_UNHOSTED_40_SECOND_FILM.mp4`, hidden and inoperable; actual original MP4 from separate PR #229 **not copied, hosted or verified here**. Poster design and VTT transcript are original **concepts**, not a finished sound- and visual-synchronized film.
- No affiliate URL active; price/discount/commission/guarantee not invented; account-specific acceptance, approved creative/swipe library, social/TikTok/email terms and actual SKU eligibility missing. Partner and conversion claims HOLD. No real analytics or randomized traffic experiment conducted.

## Hand-off / hard stop
Site QA #126: independently review links/science/disclosure, WordPress staging, Gutenberg sanitization, real native captions, screen readers, 360/390/768/1440/1920 layout, mobile/CWV and tracking OFF. Art #150: **visual consultation only**, no homepage #49 changes. Dispatch #174: source-only historical/offer notes; no changes to existing unsent newsletter drafts or Focus welcome. Founder: specific content publication approval and separate verified merchant activation approval required.

**Release: HOLD.** Zero CMS/navigation/settings, subscriber/email, merchant outbound, merge or deploy performed.