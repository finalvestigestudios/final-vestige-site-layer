# Mind R445 — Executed source-check receipt, independent verification limits and HOLD
**17 November 2026 (PT) | New isolated branch: `mind-r445-choice-blindness-offer-evidence-20261117` | Not published, not deployed**

## Scope and original deliverables

1. Original, **2,908-word** independently sourced investigation `THE_CHOICE_YOU_DID_NOT_MAKE.md`: the 2005 face choice-blindness experiment, the 2010 jam-and-tea marketplace extension, the 2013 political-attitude methodology, explicit ethical and inferential limits, Puységur primary-source archive, and a free consent-based twelve-minute demonstration. Not a branded audio efficacy study.
2. Two **substantively identical** independent Zen12 buyer guides: `ZEN12_A_TEXT_ONLY.html` and `ZEN12_B_OPTIONAL_42S_CONCEPT.html`. Variant B adds only a disclosed optional 42-second original static poster/storyboard/transcript/VTT *concept*, not an encoded or playable movie. No autoplay or video fetch. Both guides explicitly withhold seller link; the offer control is a native HTML `disabled` button, followed by the stated reason and preceded by plain adjacent prospective FTC disclosure.
3. Responsive four-stream **`MIND_HUB_WORDPRESS_SOURCE_ONLY.html`** prototype with no JavaScript or email forms; this is **not a WordPress CMS draft** or live `/mind/`. Historic categories and live navigation untouched.
4. **34-row claim-source ledger**, **18 URLs** and **28 release gates all HOLD**; official seller features and policies separated from independent research, unsupported benefit claims and authorization gaps.
5. Creator-to-existing-live-route matrix; one high-intent adult audience; single proposed Zen12 pre-sell; the existing /focus/ Jetpack funnel and source-linked direct-reading path; no media IDs guessed. Revenue acceptance requires independent seller-confirmed paid settlement and qualified-human visits, with 7/30-day cohorts.
6. Reproducible `QA_GATE.cjs` source tests, using only Node built-ins; test code is committed but native Node has not been executed.

## Actually executed QA, run against remote committed blobs

The connector fetched the actual branch's 8 original committed file blobs by path, with the following exact Git blob SHAs. The committed test logic was run **inside isolated V8 using read-only adapters for `fs`, `path`, `assert` and `process.stdout`**, wired to these fetched bytes. The gate checks read-only HTML, text, JSON, VTT and source-guard rules; **this was NOT a native Node invocation**, although the script's own terminal string says “native Node run.”

| File | Verified Git blob SHA |
| --- | --- |
| `ZEN12_A_TEXT_ONLY.html` | `e4917f46abf9e62cefca89fbfc8e97b8fd13f0c9` |
| `ZEN12_B_OPTIONAL_42S_CONCEPT.html` | `544d42738dfa2bc0472376fc4ecca80ebe5168be` |
| `MIND_HUB_WORDPRESS_SOURCE_ONLY.html` | `0ccfa67f47d997286c0bd4b632913a1fafd0733d` |
| `R445_OPTIONAL_42S.vtt` | `c2c9c1949f6add65edb5190f82017ba3351572c6` |
| `CLAIM_SOURCE_PERMISSION_MATRIX.json` | `f5768eb7a4b3c979793f4be16f6509bda5f7c604` |
| `THE_CHOICE_YOU_DID_NOT_MAKE.md` | `7cbcc0e31671b25bf5769684ed7a1229a41ea0f4` |
| `OFFER_FUNNEL_CREATOR_AND_REVENUE_ACCEPTANCE.md` | `f4cf1df445bc05f525f200793bd42610f68deab4` |
| `QA_GATE.cjs` | `80879fbc4ef29ecb8e2693a1d1fca7ae5b644f6b` |

**Final executed result: 46/46 read-only assertions passed, including 12/12 deliberately unsafe synthetic modifications correctly rejected.** Validated: common buyer body A/B is byte-identical, native disabled button, clear disclosure adjacency and link withholding, published Focus and change-blindness links, original SVG and transcript with six VTT cues ending at 42 seconds, matrix exact counts, four hub streams, no scripts/forms/merchant hrefs, no external tracking, no third-party media or autoplay. This is static source verification, not behavior in a deployed browser.

### Caught and repaired by the checks

- The initial safety test considered the phrase “disabled-offer” as proof of a native `disabled` attribute. A deliberately unsafe synthetic mutation removed the real attribute without being rejected. The test was corrected to match `\sdisabled(?=\s|>|=)`.
- A source check searched for all mention of “autoplay,” including the explicit prose that says the film has none. It was tightened to match actual `<audio>`/`<video>` autoplay attributes.
- The numerical claim test originally put a word boundary before a dollar sign, which would miss `$27.00`. The word boundary was removed, and the unsafe price mutation was then rejected.
- The article's evidence bibliography properly links official pages as citations, not earning links. The test was narrowed to disallow a tracked merchant-referral parameter rather than erase legitimate source trails.

**No live safety bug or paid conversion is claimed.** These were deliberately unsafe in-memory test cases and verifier corrections; the actual committed HTML remained inactive.

## Unexecuted release tests / independent review blockers

- Native Node test process, GitHub-hosted CI, full website build and WordPress content sanitization: **NOT EXECUTED**.
- Actual 360/390/768/1440/1920 screenshot/browser layout, WCAG 2.2 AA full keyboard/screen reader/focus/reduced motion, CWV/Lighthouse, Content Security Policy and external-link origin testing: **NOT EXECUTED**.
- Optional film encoding, rights clearance, user-initiated playback, caption synchronization, compression and player keyboard controls: **NOT EXECUTED**.
- Jetpack signup provider-confirmed conversion and welcome-delivery proof, real social-platform link/mobile restrictions, consented first-party event attribution and verified Grok media IDs: **NOT EXECUTED**.
- Final Vestige-specific Inspire3 acceptance and product/channel rights, issued earning URL, actual referred checkout price/refund terms, merchant-paid sale/settled commission/refunds/fees: **NOT VERIFIED**.
- A genuinely payable, rights-cleared FV-owned Mind digital SKU and customer fulfillment: **NOT VERIFIED**. Existing Focus Fieldbook is free.
- The 61-post live inventory was read from Issue #171's prior verified audit; the full text of all 61 historical posts was **not** independently re-read in this run. Live Puységur/Focus/change-blindness pages and official FTC/merchant sources were directly checked.

## Authoritative URLs and compliance sources inspected 17 November 2026

2005 choice-blindness paper https://pubmed.ncbi.nlm.nih.gov/16210542/ ; 2010 supermarket extension https://pubmed.ncbi.nlm.nih.gov/20637455/ ; 2013 extension https://pubmed.ncbi.nlm.nih.gov/23593244/ ; historical archive https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; Focus https://finalvestige.com/focus/ ; change-blindness canonical https://finalvestige.com/2026/11/02/change-blindness/ ; Inspire3 https://inspire3.com/ ; Zen12 official exact https://zen12.com/about ; full-course promotional https://zen12.com/secret/ ; alternate offer https://zen12.com/hnp ; Hypnosis Live exact SKU https://hypnosislive.com/mental-skills/total-focus ; its FAQ https://hypnosislive.com/faq ; Focus Shot exact https://brainwaveshots.com/focus-shot ; public affiliate portal https://affiliates.inspire3.com/ ; FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Absolute release boundary

**HARD HOLD.** Source-controlled draft PR only. No WordPress CMS/navigation/settings or new draft post, homepage PR #49, Mind hub PR #172, homepage art Issue #150, newsletter Issue #174, Jetpack list/welcome, Grok queue or posts, affiliate link, analytics script, paid SaaS, public publication, email send, merge, deploy or spending is authorized. Founder approves commerce and release; Claude owns site engineering/measurement; Praxxis validates Grok assets without replacing its creator role; independent Site QA signs off accessibility and claims.

**Revenue conclusion:** No authenticated merchant-paid commission or paid owned-product order, no accepted qualified-human session denominator. Net realized revenue per 1,000 qualified human sessions = **NOT COMPUTABLE**.
