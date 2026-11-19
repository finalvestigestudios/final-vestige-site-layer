# Mind R481 — Executed exact-source QA and release HOLD (18 November 2026 PT)

## Scope and exact tested code

GitHub branch: `mind-r481-thatcher-orientation-proof-conversion-20261118`.

Source files under `mind/r481/` only. Nine exact source files and optional Python film renderer were fetched back from **GitHub** by branch and checked; no claim of site preview or CMS write. The table records Git **blob** identifiers, not commit HEAD identifiers.

| Source file | Git blob SHA from exact readback |
| --- | --- |
| THE_FACE_THAT_LOOKED_NORMAL_UNTIL_IT_TURNED_AROUND.md | 0e0f5715e40f8233f83c8de72aac2277ffd71cfa |
| ZEN12_BUYER_GUIDE_A_TEXT.html | a3bf34da2c415fd66cc193e62406dd5a0bbe2602 |
| ZEN12_BUYER_GUIDE_B_STORYBOARD.html | 4a02e653524211e39d32be0165032a975be74573 |
| MIND_HUB_GUTENBERG_SOURCE_ONLY.html | 80c434be6f103a040b10c25407310a90d42f5260 |
| SOURCE_CLAIM_PERMISSION_AND_RELEASE_MATRIX.json | f35657a371575cf23e887692464a776c5f572539 |
| OFFER_FUNNEL_CREATOR_AB_AND_NET_REVENUE_DOCKET.md | 04665adb837eab29cef7bc8a5378262af72b3c9c |
| OPTIONAL_42S_CAPTIONS.vtt | 58cfbf2fe298c8b5d05ff933a74ea9dc50466209 |
| OPTIONAL_42S_POSTER.svg | e4ae522453b493c67077281fd328f7e5363c5349 |
| qa.test.cjs | 1aaebeb1cb17b930cd4d832ede4ad502db96bbce |
| build_optional_42s.py | d922151d02f29e3561ce2b97c320c08e4a0fa0ae |

### Actually executed tests

**54/54 deterministic V8 assertions PASS against exact fetched committed source contents**, with **6/6 deliberately unsafe synthetic changes detected**. Checks include:
- 2,361-word original scholarly investigation with original Thompson (1980), Wong et al. (2010) non-face contradiction, Lobmaier/Mast (2007) rotated-observer design, Psalta et al. (2013/14), limitations of abstract access, published Puységur and free Fieldbook context.
- A and B guides contain byte-identical buyer content after *only* B's optional film section and variant labels are removed.
- Both variants have an actual natively `disabled` purchasing button, a prospective commission disclosure adjacent to the disabled control, zero seller-domain `href` exits, no JS, forms, iframes or autoplay.
- Published editorial routes, noindex source-only state, responsive viewport metadata and reduced-motion media rules.
- 28 claim decisions, 29 commercial gates all marked `HARD_HOLD_UNCLEARED`; no affiliate activation.
- Six VTT cues ending at 42 seconds, independent SVG illustration and Python offline render recipe.
- Test cases detect: removal of native disabled; removal of disclosure; insertion of executable click-handler; new form; injected tracking script; direct merchant exit.

**NATIVE NODE SUITE:** `qa.test.cjs` is committed as a portable regression suite but **not executed in a native Node runtime on the committed repo**. The above V8 checks are a separate actually executed verification, not a claim that the native suite ran.

### Offline video verification (separate, non-repo binary)

A local Python/Pillow/ffmpeg build on 18 November produced `ZEN12_R481_ORIGINAL_42S_SILENT_PREVIEW.mp4`:
- H.264, 1280×720, 24/1 fps, exactly 42.000000 seconds, 1,008 frames, **331,752 bytes**, with no audio.
- Two consecutive runs of the **local** script produced the identical SHA-256 `f86482418497db8e142e5920ec63b438c8056f6d5d2e2eb04cb6251ab9b63fd3`.
- A review ZIP containing the local MP4, six still cards, captions, and local build script was produced for the founder. This **binary is not a GitHub PR file and is not hosted or embedded on the site**.
- A Python renderer and VTT/poster source are committed; GitHub script and local source are functionally equivalent but no claim that committed Python was itself downloaded and run byte-for-byte. Site playback/hosting, final timed narration, caption readability, accessibility and page weight gates remain untested.

### Exact limits and release gates

**UNTESTED:** real Chromium/Safari/Firefox mobile (360/390/768/1440/1920), WordPress sanitization and Gutenberg preview, keyboard/screen-reader WCAG 2.2 AA, Lighthouse/CWV/CLS/INP, actual final video with narration, captions synced to final ElevenLabs voice, site CSP, authoritative signed-in partner dashboard, confirmed Jetpack welcome delivery, merchant checkout/returns, pricing, production event attribution, 7/30-day qualified cohorts and visitor A/B. No user traffic or merchant purchase occurred.

**Merchant check:** targeted connected Gmail found only the 2026-08-24 Refersion application **PENDING** notice. The public Inspire3 affiliate network is not account authorization. No FV-specific earning URL, eligible SKU, channel/email terms, merchant sale or settlement verified.

**Historical editorial overlap:** existing older Mind R182 Thatcher draft mentioned in connected Praxxis/Grok TASK-008. Editorial lead must compare original R182 manuscript to R481 and consolidate non-face/rotating-observer counterevidence, avoiding duplicate live coverage. Neither is public merely because it exists in GitHub.

**Commercial KPI:** realized net revenue per 1,000 authenticated qualified-human sessions **NOT COMPUTABLE**, because neither a matching trustworthy session denominator nor merchant-confirmed revenue/refunds/fees is available. Clicks are not sales.

**Release governance:** no CMS/navigation/Jetpack changes, no merchant links or script activation, no emails/social posts, no paid services, no merge or deploy. Homepage PR #49, owner Issue #150, Mind PR #172 and Dispatch #174 untouched. Founder remains release/commerce approver; Claude website implementation; Praxxis/Grok social authentication; Site QA accessibility and security signoff.

**Revision protocol:** If any future commit changes these bytes, rerun tests and update exact blob/HEAD evidence. Only PR review, founder permission and actual test receipts can clear gates; an authored test file is not a PASS.
