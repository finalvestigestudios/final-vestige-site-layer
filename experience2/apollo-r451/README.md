# Apollo R451 — conversion-evidence and source-custody release guard

**DRAFT, NOT LIVE, HARD HOLD.** Isolated Apollo Issue [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) + conversion measurement [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) + charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Based on R450 exact head `935caabcb1c093dcf5c5c0ca8b7731c1a86808c1`. No edits to PR #49, PR #158, any homepage lead branch, Claude analytics, or Grok/Praxxis TASK-008.

## Why a guard, not another sales button

R450 already offers actual staging-only source evidence, original classroom prompts, a voluntary citation receipt and exactly one free investigation CTA. The product/merchant verification and published creator-asset evidence are still missing. The next useful change is to prevent mistaking an offline pass, a planned video, an email signup or a checkout click for a production acceptance or commercial conversion.

`qa/release_guard.py` reads **the existing actual** R448 claim manifest and R450 offline browser results. It pins the manifest SHA-256 and the exact four NASA source URLs/date semantics, rejects changed or omitted source limitations, rejects publication claims without platform/date/review proof and rejects paid offer readiness without authenticated seller/SKU/rights/fulfillment/refund/approval evidence. It cannot enable checkout or activate merchant attribution. All future structurally valid inputs still require independent source verification. Never infer sales from clicks; net revenue per 1,000 qualified humans remains uncomputable.

Run under the stacked branch's `experience2` tree:

```bash
python apollo-r451/qa/release_guard.py
python apollo-r451/qa/test_release_guard.py
```

These are **offline integrity/structure tests only**. R450's previous Chromium `page.set_content` tests do not constitute hosted WordPress staging, axe-core WCAG, navigated LCP/CLS, screen-reader or p75 field CWV results. True HTTPS WordPress staging must still pass the R450 approved-origin/axe-SHA gate under independent QD; this PR does not change that gate or publish any output. The companion local R451 reviewer-page/browser prototype is a separate unmerged artifact, not claimed as GitHub code in this PR.

NASA source meaning: [1966 training gallery](https://www.nasa.gov/gallery/apollo-1/), [1967 Apollo 204 Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (probable arc, no conclusive single ignition source), [2017 memorial release](https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/), [2018 retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) (later tests, not original spark), [NASA media/rights guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/). No archival media copied and no promotional rights implied.

**Release gate:** R417 reconciliation, live Atlas ambiguous review labels, photo rights, independent QD, authentic staging and axe/LCP/CLS, screen-reader, green exact-head CI, verified payable original product and actual merchant/human cohorts, founder approval. No deployment, WordPress changes, affiliate activation, media posting, emails or spend.
