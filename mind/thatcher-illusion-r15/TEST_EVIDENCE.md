# Mind & Perception R15 — reproducible evidence / independent QA limits
**Date:** 2026-10-31, local Pacific time. **State:** UNPUBLISHED source draft, no CMS or earning links activated.

## Exact source-contract execution

Branch: `feature/mind-thatcher-zen12-evidence-20261031-r15`, base `main`. The committed `qa.cjs` source at GitHub blob `732b1fc12bb5293709296c90869f685bb8cc1bf2` was **read back from GitHub** after fixing an escaped-regex source typo. Its other five inputs were read back from the **same branch** with these immutable Git blob hashes:

| Substantive input | Git blob SHA |
| --- | --- |
| `wordpress-draft.html` | `2c7009f2098853c6656782c07ef442acd38a13be` |
| `zen12-evidence-guide.md` | `c3bd6ca4ffec27149b8558774fc5ec68619a470a` |
| `claim-source-matrix.json` | `fc07ea405a46d19f3baabbae0c59d4c031283e93` |
| `VIDEO_PILOT_AND_NAV.md` | `67a160da79b602ad5ab6d6f54825ace807edb230` |
| `zen12-warmup-wordpress-draft.html` | `1fe77a022af81a98ec4e6faa44d3c3fa13bf6f4b` |
| `qa.cjs` | `732b1fc12bb5293709296c90869f685bb8cc1bf2` |

Implementation: in fresh isolated JavaScript V8 evaluate the **actual committed** `qa.cjs` `module.exports.audit()` with an object mapping exact names to fetched file text, with no network or browser DOM. Final output **93 / 93 source-level checks passed**. The initial auditor examined just four inputs (**73/73**), then a fifth production-ready HTML draft was added; a first auditor edit introduced syntactically invalid escaping, caught before test execution and fixed in commit `c1b3d930fac6a6d020154eca49e740ad90fb7fb6`. We do **not** obscure the correction or report a false clean first attempt.

The source auditor actually verifies: one article/page H1, internal anchors resolve, duplicate IDs absent, original 1980+ supporting study and research links, sourced non-face counterpoint, nonvalidated original four-face diagram text alternative, guide and separate warm-up deep source/offer copy, the official product About and exact checkout, free Focus route and historical Puységur route, honest 2019 vs 2023 independent evidence boundaries, near-inactive-offer earning disclosure, no active product referral CTA/script/iframe/secondary Jetpack form/trackers, no invented fixed dollar prices, merchant authorization false, link and rights null, aggregate measurement off, optional film concept and no autoplay, CSS responsive/keyboard/reduced motion/forced colors. Six mathematical contrast ratios in the investigation were checked against 4.5:1 WCAG AA numerical color threshold (NOT complete WCAG or actual pixels).

**Adversarial test pass:** after the final 93/93 baseline, separately generated **17/17 harmful in-memory one-at-a-time mutations were detected** by the committed audit, including: script, form, active checkout, removed nearby disclosure, autoplay, broken Focus link, missing one five-scene transcript cue, invented fixed price, removed reduced-motion, changed footer no-guarantee disclaimer, tracking activation, false merchant acceptance, removed original article disclosure, injected script, altered primary DOI, broken seller exact checkout in guide, and nonexistent evidence source ID. Earlier first-four-input run detected **21/21** distinct regressions; current mandatory final result uses 17/17 after adding the warm-up HTML.

### How to reproduce from checkout

```bash
node mind/thatcher-illusion-r15/qa.cjs
```

This must be run independently by site QA on a real Node checkout; current run did **not** execute this command under Node. The exported `audit` is pure, so the V8 execution exercises the same contract functions as the CLI entry point. For mutation cases, modify an in-memory copy of individual file strings and invoke `audit(copy)`, then assert `some(check => !check.pass)`; no production file was changed by mutations.

### Additional read-only verification

- GitHub Issue #171 reviewed, along with final relevant founder direction, earlier PRs #172/#229/#270 and latest Dispatch #174 handoff. Authenticated WordPress read-only inventory confirmed 61 published investigations and inspected **published** Puységur (page 1377) and Focus Fieldbook (page 1579). Both pages and the existing Jetpack Focus funnel were **never changed**.
- Exact official product descriptions inspected `https://inspire3.com/`, `https://zen12.com/about`, `https://zen12.com/getstarted` on 2026-10-31, especially the seller's 12x12-minute format and 48 MP3 package; no sale, endorsement, price or guarantee numbers adopted in buyer copy. Distinguish sales claims from independent experiments.
- FTC source guidance: `https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking` and `https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance`.
- Visual-science sources: `https://doi.org/10.1068/p090483`, `https://doi.org/10.1068/p260225`, `https://doi.org/10.1068/p6659` (original 1980 phenomenon, 1997 inversion/negative-speeded experiment, 2010 non-face counterpoint).
- Auditory evidence independently reviewed: `https://pubmed.ncbi.nlm.nih.gov/30073406/` (2019 meta-analysis with 22 studies / g = .45; not Zen12) and `https://pubmed.ncbi.nlm.nih.gov/37205669/` (2023 EEG review 14 studies, 5 supportive/8 contradictory/1 mixed; not Zen12). All 23 source rows/59 claim decisions in JSON.

## Not run and still mandatory

No actual WordPress draft creation or Gutenberg sanitizer round trip, no production route, no genuine hosted video or first-party media URL, no actual Safari/Chrome/mobile/AT screen-reader/keyboard, 200–400% zoom, no generated screen captures / Lighthouse/Core Web Vitals, no hosted CI confirmation, no verified logged-out real Focus submit/consent path, no authenticated affiliate approval/link/terms or tracking. Prior film PR #229 manifests are **prior build assertions**, not evidence of independently running the video in this run. No partner promotions, no product price, no opt-in email marketing verification. No exact conversion lift, sales or commissions are claimed.

Release gate: independent QA #126 and qualified scientific/copy editor; visual feedback from homepage lead #150 while **not editing flagship PR #49**; informational research handoff to Dispatch #174 without changing any of the six emails or existing welcome message; owner written affiliate approval and exact eligible Zen12 link/rights; founder permission to publish, separately later approval to activate any earning link. This is a DRAFT/HOLD PR, not a deployment.
