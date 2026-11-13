# Dispatch R328 — original six-issue offline email review bundle (NOT ADOPTED)

Original master: [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Tracking: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). This is **NOT** an alternate campaign, sending tool or approved mail template: it mechanically compiles the existing, untouched issue manuscripts into six offline HTML and six plaintext review assets.

**Run locally on checked-out original master branch plus this R328 addition:** `node dispatch/r328/test_canonical_previews.mjs`. No network, subscriber data, merchant link, sends or CMS access. The pure builder exports `buildIssue`, which consumes original markdown plus the manifest and reproduces exactly the committed previews. This package has static source and viewport considerations only, not a live WordPress/JETPACK or inbox proof.

Review: `dispatch/r328/reviewer.html`. Six HTML files use inline email-safe table styles, accessible readable links to **existing** Final Vestige pages, review-only warning, proposed hidden preheader and explicit unverified footer tokens. Two commercial future CTA tokens are intentionally NONLINKED. Plaintext outputs preserve full original body, proposed subject and metadata, and the legal hold.

**Limitations:** The original master Markdown leaves sources mostly in first-party references; independent official merchant claim URLs and revision cautions are in `RESEARCH_AND_PERMISSION_QA.md`, not silently injected into original mail. Proposed preheaders may not be supported by WordPress delivery. No actual human accessibility screen-reader, email-provider compatibility or Jetpack footer evidence was obtained. Original copy has specific conversion weaknesses—Issue 01/02 duplicate destination and Issue 06 repeat signup; earlier optional alternatives are **not adopted**.

Gate truth: all six `HOLD_UNSENT`, #03/#05 `HOLD_MERCHANT`, zero send authority; physical address and unsubscribe cannot be faked, and the campaign's paid revenue KPI is N/A.
